import sys
from typing import Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score,classification_report

from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import load_numpy_array_data,load_object,save_object
from src.entity.config_entity import ModelTrainerConfig
from src.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,ClassifactionMetricArtifact
from src.entity.estimator import MyModel

class ModelTrainer:
    def __init__(self,data_transformation_artifact:DataTransformationArtifact,
                 model_trainer_config:ModelTrainerConfig):
        
        self.data_transformation_artifact=data_transformation_artifact
        self.model_trainer_config=model_trainer_config
    
    def get_model_object_and_report(self,train:np.array,test:np.array)->Tuple[object,object]:
        try:
            logging.info("Training RandomForestClassifier with specified parameters")

            x_train,y_train,x_test,y_test=train[:,:-1],train[:,-1],test[:,:-1],test[:,-1]
            logging.info('train-test split done')

            model=RandomForestClassifier(
                n_estimators=self.model_trainer_config.n_estimators,
                min_samples_split=self.model_trainer_config.min_samples_split,
                min_samples_leaf=self.model_trainer_config.min_samples_leaf,
                max_depth=self.model_trainer_config.max_depth,
                criterion=self.model_trainer_config.criterion,
                random_state=self.model_trainer_config.random_state
            )

            logging.info("Model trainer going on.........................................................")
            model.fit(x_train,y_train)
            logging.info("Model training done")

            y_pred=model.predict(x_test)
            accuracy=accuracy_score(y_test,y_pred)
            f1=f1_score(y_test,y_pred)
            precision=precision_score(y_test,y_pred)
            recall=recall_score(y_test,y_pred)
            classification_class_wise_report=classification_report(y_test,y_pred)

            metric_artifact=ClassifactionMetricArtifact(
                f1_score=f1_score,
                precision_score=precision_score,
                recall_score=recall_score,
                classification_report=classification_class_wise_report
            )
            return model,metric_artifact
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of MOdelTrainer class")

        try:
            print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            print("Starting model training component")

            train_arr=load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_file_path)
            test_arr=load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_file_path)
            logging.info("train-test data loaded")

            trained_model,metric_artifact=self.get_model_object_and_report(train=train_arr,test=test_arr)
            logging.info("Model object and evaluation metric artifact")

            preprocessing_obj=load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            logging.info("Preprocessing obj loaded")

            if accuracy_score(test_arr[:,-1],trained_model.predict(test_arr[:,:-1]))<self.model_trainer_config.expected_accuracy:
                logging.info("No model found with score above base score")
                raise Exception("No model found with score above base score")
            
            logging.info("Saving new model as performance is better than previous one")
            my_model=MyModel(preprocessing_obj=preprocessing_obj,trained_model_object=trained_model)
            save_object(self.model_trainer_config.trained_model_file_path,my_model)
            logging.info("Saved final model object that includes both pre-processing and trained model")

            model_trainer_artifact=ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                metric_artifact=metric_artifact
            )
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        
        except Exception as e:
            raise MyException(e,sys) from e
