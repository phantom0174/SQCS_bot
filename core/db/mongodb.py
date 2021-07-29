import os
import logging
from typing import List, Tuple, Union
from pymongo import MongoClient
import pymongo

# Mongodb database
account = os.environ.get("MONGODB_ACCOUNT")
password = os.environ.get("MONGODB_PASSWORD")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"


class Mongo:
    def __init__(self, database: str):
        self.client = MongoClient(link)[database]

    def get_cur(self, collection: str) -> pymongo.cursor.CursorType:
        return self.client[collection]

    def get_curs(self, collections: List[str]) -> Tuple[pymongo.cursor.CursorType]:
        cursors = [self.client[collection] for collection in collections]
        return tuple(cursors)

    def get_all_curs(self) -> Tuple[pymongo.cursor.CursorType]:
        cursors = [self.client[collection]
                   for collection in client.list_collection_names()]
        return tuple(cursors)
