import boto3
import os
from src.constants import aws_secret_access_key_env_key,aws_access_key_id_env_key,region_name


class S3Client:

    s3_client=None
    s3_resource=None

    def __init__(self,region_name=region_name):
        '''
        Gets aws credentials from env_variables and then made
        a connection with S3 bucket 
        '''

        if S3Client.s3_resource==None or S3Client.s3_client==None:

            access_key_id=aws_access_key_id_env_key
            # print(access_key_id)
            secret_access_key=aws_secret_access_key_env_key
            # print(secret_access_key)

            if access_key_id is None:
                raise Exception(f"Environment variable:{aws_access_key_id_env_key} is not set")
            
            if secret_access_key is None:
                raise Exception(f"Environment variable: {aws_secret_access_key_env_key} is not set")
            
            # in bracket 's3' is the service you want to interact with
            S3Client.s3_resource=boto3.resource('s3',
                                                aws_access_key_id=access_key_id,
                                                aws_secret_access_key=secret_access_key,
                                                region_name=region_name
                                                )
            
            self.s3_resource=S3Client.s3_resource
            self.s3_client=S3Client.s3_client
            # it is none only

