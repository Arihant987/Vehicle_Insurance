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