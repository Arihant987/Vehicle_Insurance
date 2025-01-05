import sys
from src.exception import MyException
from src.logger import logging

from src.components.data_ingestion import DataIngestion

from src.entity.config_entity import (DataIngestionConfig)

from src.entity.artifact_entity import (DataIngestionArtifact)

class TrainPipeline:
    def __init__(self):
        self.data_ingestion_config=DataIngestionConfig()


    def start_data_ingestion(self)->DataIngestionArtifact:
        '''
        This method of TrainPipeline class is responsible for starting data ingestion component
        '''
        try:
            logging.info("Entered start data ingestion method inside Training Pipeline")
            logging.info("Getting data from MongoDB")
            data_ingestion=DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info("Got the train and test set from db")
            logging.info("Exited data ingestion pipeline")
            return data_ingestion_artifact
        except Exception as e:
            raise MyException(e,sys) from e
        
    def run_pipeline(self,)->None:
        '''
        This method is responsible for running complete pipeline
        '''
        try:
            data_ingestion_artifact=self.start_data_ingestion()
        

        except Exception as e:
            raise MyException(e,sys)
        

from src.pipeline.training_pipeline import TrainPipeline

pipeline=TrainPipeline()
pipeline.run_pipeline()