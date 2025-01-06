import os
from datetime import date

database_name="Vehicle-proj_data"
collection_name="proj_data"
mongodb_url_key="mongodb_url" # will get from .env file

pipeline_name:str="vehicle-pipeline"
artifact_dir:str="artifact"

target_column='Response'
current_year=date.today().year
preprocessing_object_file_name="preprocessing.pkl"

file_name:str="data.csv"
train_file_name:str="train.csv"
test_file_name:str="test.csv"
schema_file_path=os.path.join("config","schema.yaml")

data_ingestion_collection_name:str="proj_data"
data_ingestion_dir_name:str="data_ingestion"
data_ingestion_feature_store_dir:str="feature_store"
data_ingestion_ingested_dir:str="ingested"
data_ingestion_train_test_split_ratio:float=0.25

data_validation_dir_name:str="data_validation"
data_validation_report_file_name:str="report.yaml"

data_transformation_dir_name:str="data_transformation"
data_transformation_transformed_data_dir:str="transformed"
data_transformation_transformed_obj_dir:str="transformed_object"

model_trainer_dir_name:str='model_trainer'
model_trainer_trained_model_dir:str="trained_model"
model_file_name="model.pkl"
model_trainer_expected_score:float=0.6
model_trainer_model_config_file_path:str=os.path.join('config','model.yaml')
model_trainer_n_estimators=200
model_trainer_min_samples_split:int=7
model_trainer_min_samples_leaf:int=6
min_samples_split_max_depth:int=10
min_samples_split_criterion:str="entropy"
min_samples_split_random_state=101