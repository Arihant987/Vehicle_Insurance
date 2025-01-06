import os
from src.constants import *
from dataclasses import dataclass
from datetime import datetime

TIMESTAMP: str=datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

@dataclass
class TrainingPipelineConfig:
    pipeline_name:str=pipeline_name
    artifact_dir:str=os.path.join(artifact_dir,TIMESTAMP)
    timestamp:str=TIMESTAMP

training_pipeline_config:TrainingPipelineConfig=TrainingPipelineConfig()

@dataclass
class DataIngestionConfig:
    data_ingestion_dir:str=os.path.join(training_pipeline_config.artifact_dir,data_ingestion_dir_name)
    feature_store_file_path:str=os.path.join(data_ingestion_dir,data_ingestion_feature_store_dir,file_name)
    training_file_path:str=os.path.join(data_ingestion_dir,data_ingestion_ingested_dir,train_file_name)
    testing_file_path:str=os.path.join(data_ingestion_dir,data_ingestion_ingested_dir,test_file_name)
    train_test_split_ratio:float=data_ingestion_train_test_split_ratio
    collection_name:str=data_ingestion_collection_name

@dataclass
class DataValidationConfig:
    data_validation_dir:str=os.path.join(training_pipeline_config.artifact_dir,data_validation_dir_name)
    validation_report_file_path:str=os.path.join(data_validation_dir,data_validation_report_file_name)

@dataclass
class DataTransformationConfig:
    data_transformation_dir:str=os.path.join(training_pipeline_config.artifact_dir,data_transformation_dir_name)
    transformed_train_file_path:str=os.path.join(data_transformation_dir,data_transformation_transformed_data_dir,train_file_name.replace("csv","npy"))
    transformed_test_file_path:str=os.path.join(data_transformation_dir,data_transformation_transformed_data_dir,test_file_name.replace("csv","npy"))
    transformed_object_file_path:str=os.path.join(data_transformation_dir,data_transformation_transformed_obj_dir,preprocessing_object_file_name)

@dataclass
class ModelTrainerConfig:
    model_trainer_dir:str=os.path.join(training_pipeline_config.artifact_dir,model_trainer_dir_name)
    trained_model_file_path:str=os.path.join(model_trainer_dir,model_trainer_trained_model_dir,model_file_name)
    expected_accuracy:float=model_trainer_expected_score
    model_config_file_path:str=model_trainer_model_config_file_path
    n_estimators=model_trainer_n_estimators
    min_samples_split=model_trainer_min_samples_split
    min_samples_leaf=model_trainer_min_samples_leaf
    max_depth=min_samples_split_max_depth
    criterion=min_samples_split_criterion
    random_state=min_samples_split_random_state

@dataclass
class ModelEvaluationConfig:
    changed_threshold_score:float=model_evaluation_changed_threshold_score
    bucket_name:str=model_bucket_name
    s3_model_key_path:str=model_file_name