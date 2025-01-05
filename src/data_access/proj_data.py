import sys
import pandas as pd
import numpy as np
from typing import Optional

from src.configuration.mongo_db_connection import MongoDBclient
from src.exception import MyException
from src.constants import database_name,collection_name

class ProjData:
    '''
    A class to export MongoDB records as a pandas DataFrame
    '''

    def __init__(self)->None:
        '''
        Constructor to create a connection to MongoDB database
        '''
        try:
            # Connection is set
            self.mongo_client=MongoDBclient(database_name=database_name)
        except Exception as e:
            raise MyException(e,sys)
        
    def export_collection_as_dataframe(self,collection_name:str,database_name:Optional[str]=None)->pd.DataFrame:
        '''
        Method to export MongoDB records as a pandas DataFrame
        '''
        try:
            if database_name is None:
                collection=self.mongo_client.database[collection_name]
            else:
                collection=self.mongo_client.client[database_name][collection_name]
            
            print("Fetching data from MongoDB")
            df=pd.DataFrame(list(collection.find()))
            print(f"Data fetched successfully with len: {len(df)}")

            if "id" in df.columns.to_list():
                df=df.drop(columns=["id"],axis=1)

            # No need as no value is null
            df.replace({"na":np.nan},inplace=True)
            return df
        
        except Exception as e:
            raise MyException(e,sys)
        
# just for testing
# testing=ProjData()
# testing.export_collection_as_dataframe(collection_name=collection_name) # type: ignore