import sys

import pandas as pd
from pandas import DataFrame
from sklearn.pipeline import Pipeline

from src.exception import MyException
from src.logger import logging

class TargetValueMapping:
    def __init__(self):
        self.yes:int=0
        self.no:int=1
    
    def _asdict(self):
        return self.__dict__
    # it is {'yes':0, 'no':1}
    
    def reverse_mapping(self):
        mapping_response=self._asdict()
        return dict(zip(mapping_response.values(),mapping_response.keys()))

class MyModel:
    def __init__(self,preprocessing_obj:Pipeline,trained_model_object:object):
        self.preprocessing_object:str=preprocessing_obj
        self.trained_model_object=trained_model_object

    def predict(self,dataframe:pd.DataFrame)->DataFrame:
        try:
            logging.info("Starting prediction process")

            transformed_feature=self.preprocessing_object.transform(dataframe)

            logging.info("Using the trained model to get predictions")
            predictions=self.trained_model_object.predict(transformed_feature)

            return predictions
        
        except Exception as e:
            logging.error("Error occured in predict method",exc_info=True)
            raise MyException(e,sys) from e
    
    def __repr__(self):
        return f"{type(self.trained_model_object).__name__}()"

    def __str__(self):
        return f"{type(self.trained_model_object).__name__}()"