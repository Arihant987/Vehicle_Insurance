import boto3
from src.configuration.aws_connection import S3Client
from io import StringIO
from typing import Union,List
import os,sys
from src.logger import logging
# import Bucket type
from mypy_boto3_s3.service_resouce import Bucket

from src.exception import MyException
from botocore.exceptions import ClientError
from pandas import DataFrame,read_csv
import pickle


class SimpleStorageService:
    '''
    class for interacting with AWS s3 storage, providing methods for file management,
    data uploads, and data retrieval in S3 buckets.
    '''

    def __init__(self):

        s3_client=S3Client()
        self.s3_resource=s3_client.s3_resource
        self.s3_client=s3_client.s3_client

    def s3_key_path_available(self,bucket_name,s3_key)->bool:
        '''
        check if specified s3_key(s3 key path){file_path} 
        is available in specified bucket
        '''
        try:
            # get_bucket is defined later
            bucket=self.get_bucket(bucket_name)
            file_objects=[file_object for file_object in bucket.objects.filter(Prefix=s3_key)]
            return len(file_objects)>0
        
        except Exception as e:
            raise MyException(e,sys) from e
    
    @staticmethod
    def read_object(object_name:str,decode:bool=True,make_readable:bool=False)->Union[StringIO,str]:
        '''
        reads the specified s3 object with optional decoding and formatting

        Args:

        object_name(str): s3 obj name
        decode: whether to decode the object content as a string
        make_readable: whether to convert content to StringIO for df usage

        Returns:

        Union(StringI0,str): content of object as a StringI0 or decoded string
        '''
        try:
            func=(
                lambda: object_name.get()["Body"].read().decode()
                if decode else object_name.get()["Body"].read()
            )
            conv_func=lambda: StringIO(func()) if make_readable else func()

            return conv_func()
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def get_bucket(self,bucket_name:str)->Bucket:
        logging.info("Entered the get_bucket method of SSS class")
        try:
            bucket=self.s3_resource.Bucket(bucket_name)
            logging.info("Exited the get_bucket method of SSS class")
            return bucket
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def get_file_object(self,filename:str,bucket_name:str)->Union[List[object],object]:
        '''
        retrieves the file object(s) from bucket name 
        
        Args:
        filename(str): the name of file to retrieve

        Returns:
        return (s3 file obj,list of file obj)
        '''

        logging.info("Entered the get_file_object method of SSS class")

        try:
            bucket=self.get_bucket(bucket_name)
            file_objects=[file_object for file_object in bucket.objects.filter(Prefix=filename)]
            func= lambda x:x[0] if len(x)==1 else x
            file_objs=func(file_objects)
            logging.info("Exited the get_file_object method of SSS class")
            return file_objs
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def load_model(self,model_name:str,bucket_name:str,model_dir:str=None)->object:
        '''
        Load a serialized model

        args: model_dir(str): Directory path with in the bucket
        '''
        try:
            model_file=model_dir+"/"+model_name if model_dir else model_name
            file_object=self.get_file_object(model_file,bucket_name)
            model_obj=self.read_object(file_object,decode=False)
            model=pickle.loads(model_obj)
            logging.info("Production model loaded from S3 bucket")
            
            return model
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def create_folder(self,folder_name:str,bucket_name:str)->None:
        '''
        Creates a folder in specified S3 bucket
        '''
        logging.info("Entered the create folder method of SSS class")
        try:
            self.s3_resource.Object(bucket_name,folder_name).load()

        except ClientError as e:
            if e.response["Error"]["Code"]=='404':
                folder_obj=folder_name+"/"
                self.s3_client.put_object(Bucket=bucket_name,key=folder_obj)
        
        logging.info("Entered the create folder method of SSS class")

    def upload_file(self,from_filename:str,to_filename:str,bucket_name:str,remove:bool=True):
        '''
        upload a file to s3 bucket and
        option to delte the file
        '''
        logging.info("Entered the upload_file_path of SSS class")
        try:
            logging.info(f"Uploading {from_filename} to {to_filename} in {bucket_name}")
            self.s3_resource.meta.client.upload_file(from_filename,bucket_name,to_filename)
            logging.info(f"Uploaded {from_filename} to {to_filename} in {bucket_name}")

            if remove:
                os.remove(from_filename)
                logging.info(f"Removed local file {from_filename} after upload")
            logging.info("Exited the upload_file_path of SSS class") 
        
        except Exception as e:
            raise MyException(e,sys) from e
        
    def upload_df_as_csv(self,data_frame:DataFrame,local_filename:str,bucket_filename:str,bucket_name:str)->None:
        '''
        bucket_filename: target filename in the bucket
        '''
        logging.info("Entered the upload_df_as_csv method of SSS class")

        try:
            data_frame.to_csv(local_filename,index=None,header=True)
            self.upload_file(local_filename,bucket_filename,bucket_name)
            logging.info("Exited the upload_df_as_csv method of SSS class")

        except Exception as e:
            raise MyException(e,sys) from e
            
    def get_df_from_object(self,obj: object)-> DataFrame:
        '''
        Converts an s3 object to df
        args: object is s3 object
        '''
        logging.info("Entered the get_df_from_object method of SSS class")
        try:
            content=self.read_object(obj,make_readable=True)
            df=read_csv(content,na_values='na')
            logging.info("Entered the get_df_from_object method of SSS class")
            return df
        
        except Exception as e:
            raise MyException(e, sys) from e
    
    def read_csv(self,filename:str,bucket_name:str)->DataFrame:
        logging.info("Entered the read_csv method of SSS class")
        try:
            csv_obj=self.get_file_object(filename,bucket_name)
            df=self.get_df_from_object(csv_obj)
            logging.info("Exited the read_csv method of SSS class")
            return df
        except Exception as e:
            raise MyException(e, sys) from e