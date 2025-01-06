import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.compose import ColumnTransformer

from src.constants import target_column,schema_file_path,current_year
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import save_numpy_array_data,read_yaml_file,save_object

class DataTransformation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact:DataValidationArtifact):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_transformation_config=data_transformation_config
            self.data_validation_artifact=data_validation_artifact
            self._schema_config=read_yaml_file(file_path=schema_file_path)
        
        except Exception as e:
            raise MyException(e,sys) from e
    
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e,sys) from e
        
    def get_data_transformer_object(self)->Pipeline:
        '''
        Creates and returns a data transformer object
        '''
        logging.info("Entered get_data_transformer_object method of DataTransformation class")

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

            logging.info("Final pipeline of scalers ready")
            logging.info("Exited get_data_transformers_object method of DataTransformation Class")

            return final_pipeline
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def map_gender_columns(self,df):
        '''
        Map gender column to 0 for female 
        and 1 for male
        '''
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender']=df['Gender'].map({'Female':0,'Male':1}).astype(int)
        return df
    
    def create_dummy_columns(self,df):
        '''
        Create dummy variables for categorical features
        '''
        logging.info("Create dummy variables for categorical features")
        df=pd.get_dummies(df,drop_first=True)
        return df
    
    def rename_columns(self,df):
       '''
       Rename specific columns and ensure integer types for dummy variables
       ''' 
       logging.info("Renaming specific columns and ensure integer types for dummmy columns")
       
       df=df.rename(columns={
           "Vehicle_Age_< 1 Year":"Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years":"Vehicle_Age_gt_2_Years"
        })
       for col in ["Vehicle_Age_lt_1_Year","Vehicle_Age_gt_2_Years","Vehicle_Damage_Yes"]:
            if col in df.columns:
               df[col]=df[col].astype('int')

       return df

    def _drop_id_column(self,df):
        '''
        drop the id column if it exists
        '''
        logging.info("Dropping the id column")
        drop_columns=self._schema_config['drop_columns']
        if drop_columns in df.columns:
            df=df.drop(drop_columns,axis=1)
        
        return df
    
    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info("Data Transformation Started")

            # Checking if data validation is correct or not 
            if not self.data_validation_artifact.validation_status:
                raise Exception(self.data_validation_artifact.message)
            
            train_df=self.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df=self.read_data(file_path=self.data_ingestion_artifact.test_file_path)
            
            logging.info("Train-Test data loaded")

            x_train_df=train_df.drop(columns=[target_column],axis=1)
            y_train_df=train_df[target_column]

            x_test_df=test_df.drop(columns=[target_column],axis=1)
            y_test_df=test_df[target_column]

            logging.info("x and y defined for both train and test.df")

            x_train_df=self.map_gender_columns(x_train_df)
            x_train_df=self._drop_id_column(x_train_df)
            x_train_df=self.create_dummy_columns(x_train_df)
            x_train_df=self.rename_columns(x_train_df)

            x_test_df=self.map_gender_columns(x_test_df)
            x_test_df=self._drop_id_column(x_test_df)
            x_test_df=self.create_dummy_columns(x_test_df)
            x_test_df=self.rename_columns(x_test_df)

            logging.info("Custom transformations applied to train and test data")

            logging.info("Starting data transformation")
            preprocessor=self.get_data_transformer_object()
            
            logging.info("Initializing transformation of training data")
            x_train_arr=preprocessor.fit_transform(x_train_df)
            logging.info("Initializing transformation of testing data")
            x_test_arr=preprocessor.transform(x_test_df)
            logging.info("Transformation done of training and testing data")

            logging.info("Applying Smoteenn for handling imbalanced dataset")
            smt=SMOTEENN(sampling_strategy='minority')
            x_train_final,y_train_final=smt.fit_resample(
                x_train_arr,y_train_df
            )
            logging.info("Smoteenn applied successfully")

            train_arr=np.c_[x_train_final,np.array(y_train_final)]
            test_arr=np.c_[x_test_arr,np.array(y_test_df)]
            logging.info("Feature target concatination done for train-test.df")

            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor)
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array=test_arr)
            logging.info("Saving transformation object and transformation files")

            logging.info("Data transformation completed successfully")

            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
        
        except Exception as e:
            raise MyException(e,sys) from e