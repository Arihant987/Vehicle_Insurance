import os 
import sys 

from pandas import DataFrame
from sklearn.model_selection import train_test_split

from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact
from src.exception import MyException
from src.logger import logging
from src.data_access.proj_data import ProjData

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig=DataIngestionConfig())->None:
        '''
        Constructor to initialize the DataIngestion class
        '''
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise MyException(e,sys)
        
    def export_data_into_feature_store(self)->DataFrame:
        '''
        Method to export data 
        from MongoDB to csv file into feature store
        '''
        try:
            logging.info("Exporting data from MongoDb")

            my_data=ProjData()
            dataframe=my_data.export_collection_as_dataframe(collection_name=self.data_ingestion_config.collection_name)
            logging.info(f"Shape of data frame is: {dataframe.shape}")

            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info(f"Saving exported data into feature store at {feature_store_file_path} file path")
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            
            return dataframe
        except Exception as e:
            raise MyException(e,sys)
        
    def split_data_as_train_test(self,dataframe:DataFrame)->None:
        '''
        Method to split the data into train and test
        '''
        logging.info("Started splitting the data into train and test")
        try:
            train_set,test_set=train_test_split(dataframe,test_size=self.data_ingestion_config.train_test_split_ratio,random_state=42)
            logging.info("Splitting the data into train and test is done")

            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)

            logging.info("Exporting train and test file path")
            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path,index=False,header=True)

            logging.info(f"Exported train and test file path.")

        except Exception as e:
            raise MyException(e,sys)
        
    def initiate_data_ingestion(self)->DataIngestionArtifact:
        '''
        output: train and test set are returned as artifacts of data ingestion components
        '''
        logging.info("Entered initiate_data_ingestion method of Data_ingestion class")

        try:
            dataframe=self.export_data_into_feature_store()
            logging.info("Got the data from mongodb")

            self.split_data_as_train_test(dataframe)
            logging.info("Performed train test split on dataset")

            data_ingestion_artifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,test_file_path=self.data_ingestion_config.testing_file_path)
            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        
        except Exception as e:
            raise MyException(e,sys) from e