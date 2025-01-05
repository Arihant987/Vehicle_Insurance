import os 
import sys
import pymongo
import certifi
from dotenv import load_dotenv
load_dotenv()
# certifi is for ssl security socket layer

from src.exception import MyException
from src.logger import logging
from src.constants import database_name,mongodb_url_key

ca=certifi.where()

class MongoDBclient:
    '''
    MongoDB client class to connect to the MongoDB database

    Attributes:
    client: A shared MongoClient instance for the class
    database: Database 
    '''
    client=None # shared MongoClient instance across the application

    def __init__(self,database_name:str=database_name)->None:
        ''''
        Constructor to create a connection to MongoDB database 
        '''
        try:
            if MongoDBclient.client is None:
                mongodb_url=os.getenv("connection_url")
                if mongodb_url is None:
                    raise Exception(f"MongoDB URL key not set and not found in the environment variable {mongodb_url_key}")
                MongoDBclient.client=pymongo.MongoClient(mongodb_url, tlsCAFile=ca) # ca is certificate authority
            
            self.client=MongoDBclient.client
            self.database=self.client[database_name]
            self.database_name=database_name
            logging.info(f"Connected to the database {database_name} of MongoDB")

        except Exception as e:
            raise MyException(e,sys)
        
# For testing if it is working or not
# client=MongoDBclient(database_name=database_name)
