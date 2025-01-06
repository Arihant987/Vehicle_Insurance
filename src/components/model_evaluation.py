from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import ModelEvaluationArtifact,ModelTrainerArtifact,DataIngestionArtifact
from sklearn.metrics import f1_score

from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from src.exception import MyException
from src.constants import target_column,schema_file_path
from src.logger import logging
from src.utils.main_utils import load_object,read_yaml_file
import sys
import pandas as pd
from typing import Optional
from src.entity.s3_estimator import ProjEstimator
from dataclasses import dataclass

@dataclass
class EvaluateModelResponse:
    trained_model_f1_score:float
    # by best model it means model uploaded on aws (s3 bucket)
    best_model_f1_score:float
    is_model_accepted:bool
    difference:float

class ModelEvaluation:

    def __init__(self,model_eval_config:ModelEvaluationConfig,data_ingestion_artifact:DataIngestionArtifact,
                 model_trainer_artifact:ModelTrainerArtifact):
        try:
            self.model_eval_config=model_eval_config
            self.data_ingestion_artifact=data_ingestion_artifact
            self.model_trainer_artifact=model_trainer_artifact
            self._schema_config=read_yaml_file(file_path=schema_file_path)
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def get_best_model(self)->Optional[ProjEstimator]:
        '''
        to get model from s3 bucket
        '''
        try:
            bucket_name=self.model_eval_config.bucket_name
            model_path=self.model_eval_config.s3_model_key_path
            proj_estimator=ProjEstimator(bucket_name=bucket_name,
                                         model_path=model_path)
            
            if proj_estimator.is_model_present(model_path=model_path):
                return proj_estimator
            return None
        
        except Exception as e:
            raise MyException(e,sys) from e
        

    def map_gender_column(self, df):
        """
        Map Gender column to 0 for Female and 1 for Male.
        """
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender']=df['Gender'].map({'Female': 0, 'Male': 1}).astype(int)
        return df

    def create_dummy_columns(self, df):
        """
        Create dummy variables for categorical features.
        """
        logging.info("Creating dummy variables for categorical features")
        df = pd.get_dummies(df, drop_first=True)
        return df

    def rename_columns(self, df):
        """
        Rename specific columns and ensure integer types for dummy columns.
        """
        logging.info("Renaming specific columns and casting to int")
        df = df.rename(columns={
            "Vehicle_Age_< 1 Year": "Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years": "Vehicle_Age_gt_2_Years"
        })
        for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
            if col in df.columns:
                df[col] = df[col].astype('int')
        return df
    
    def drop_id_column(self, df):
        """
        Drop the 'id' column if it exists.
        """
        logging.info("Dropping 'id' column")
        drop_columns=self._schema_config['drop_columns']
        if drop_columns in df.columns:
            df = df.drop(drop_columns, axis=1)
        return df
    
    def get_data_transformer_object(self)->Pipeline:
        '''
        Creates and returns a data transformer object
        '''
        logging.info("Entered get_data_transformer_object method")

        try:
            ss=StandardScaler()
            mm=MinMaxScaler()
            logging.info("Initialized StandardScaler and MinMaxScaler")

            ss_features=self._schema_config['ss_features']
            mm_features=self._schema_config['mm_features']
            logging.info("Columns loaded from schema")

            preprocessor=ColumnTransformer(
                transformers=[
                    ("StandardScaler",ss,ss_features),
                    ("MinMaxScaler",mm,mm_features)
                ],
                remainder='passthrough' # skips the columns as it is
            )

            final_pipeline=Pipeline(steps=[("Preprocessor",preprocessor)])

            logging.info("Final pipeline ready")
            logging.info("Exited get_data_transformers_object method")

            return final_pipeline
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def evaluate_model(self)->EvaluateModelResponse:
        '''
        This function is used to evaluate trained model with production model and then chooose best model
        '''
        try:
            test_df=pd.read_csv(self.data_ingestion_artifact.test_file_path)
            x,y=test_df.drop(target_column,axis=1),test_df[target_column]

            logging.info("Test data loaded and now transforming it for prediction .........")

            x=self.map_gender_column(x)
            x=self.drop_id_column(x)
            x=self.create_dummy_columns(x)
            x=self.rename_columns(x)

            preprocessor=self.get_data_transformer_object()
            train_df = pd.read_csv(self.data_ingestion_artifact.trained_file_path)
            x_train = train_df.drop(target_column, axis=1)
            x_train = self.map_gender_column(x_train)
            x_train = self.drop_id_column(x_train)
            x_train = self.create_dummy_columns(x_train)
            x_train = self.rename_columns(x_train)
            preprocessor.fit(x_train)
            
            x_test=preprocessor.transform(x)

            trained_model=load_object(file_path=self.model_trainer_artifact.trained_model_file_path)
            logging.info("Trained model loaded.")
            trained_model_f1_score=self.model_trainer_artifact.metric_artifact.f1_score
            logging.info(f"f1 score for this model is {trained_model_f1_score}")

            best_model_f1_score=None
            best_model=self.get_best_model()

            if best_model is not None:
                logging.info(f"Computing f1 score for production model.......")
                y_hat_best_model=best_model.predict(x_test)
                best_model_f1_score=f1_score(y,y_hat_best_model)
                logging.info(f"f1 score for production model: {best_model_f1_score}, f1 score for new trained model: {trained_model_f1_score}")

            tmp_best_model_score=0 if best_model_f1_score is None else best_model_f1_score
            result=EvaluateModelResponse(trained_model_f1_score=trained_model_f1_score,
                                         best_model_f1_score=best_model_f1_score,
                                         is_model_accepted=trained_model_f1_score>tmp_best_model_score,
                                         difference=trained_model_f1_score-tmp_best_model_score)
            
            logging.info(f"Result: {result}")
            return result
        
        except Exception as e:
            raise MyException(e,sys)
        
    def initiate_model_evaluation(self)->ModelEvaluationArtifact:
        try:
            print("------------------------------------------------------------------------------------------")
            logging.info("Initialized Model Evaluation Component")
            evaluate_model_response=self.evaluate_model()
            s3_model_path=self.model_eval_config.s3_model_key_path

            model_evaluation_artifact=ModelEvaluationArtifact(is_model_aacepted=evaluate_model_response.is_model_accepted,
                                                              s3_model_path=s3_model_path,
                                                              trained_model_path=self.model_trainer_artifact.trained_model_file_path,
                                                              changed_accuracy=evaluate_model_response.difference
                                                              )  
            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact
        except Exception as e:
            raise MyException(e,sys) from e