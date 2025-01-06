from src.cloud_storage.aws_storage import SimpleStorageService
from src.exception import MyException
from src.entity.estimator import MyModel
import sys
from pandas import DataFrame

class ProjEstimator:
    '''
    This class is used to save and retrieve our model 
    from s3 bucket and do prediction
    '''

    def __init__(self,bucket_name,model_path):
        '''
        model_path is location of model in bucket
        '''
        self.bucket_name=bucket_name
        self.s3=SimpleStorageService()
        self.model_path=model_path
        self.loaded_model:MyModel=None
    
    def is_model_present(self,model_path):
        try:
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name,s3_key=model_path)
        
        except MyException as e:
            print(e)
            return False
    
    def load_model(self)->MyModel:
        '''
        load the model from model_path
        '''

        return self.s3_load_model(self.model_path,bucket_name=self.bucket_name)
    
    def save_model(self,from_file,remove:bool=False)->None:
        '''
        save the model to model_path
        :param from_file: your local system model path
        :param_remove: by default it is false that mean you will have your model locallly available in your system folder
        '''

        try:
            self.s3.upload_file(from_file,
                                to_filename=self.model_path,
                                bucket_name=self.bucket_name,
                                remove=remove)
        
        except Exception as e:
            raise MyException(e,sys) from e

    def predict(self,fataframe:DataFrame):
        try:
            if self.loaded_model is None:
                self.loaded_model=self.load_model()

        except Exception as e:
            raise MyException(e,sys) from e