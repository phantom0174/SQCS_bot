import os
from typing import List
from pymongo import MongoClient
import pymongo

# Mongodb database
account = os.environ.get("MONGODB_ACCOUNT")
password = os.environ.get("MONGODB_PASSWORD")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"

mongo_client = MongoClient(link)


class Mongo:
    def __init__(self, database: str):
        self.client = mongo_client[database]

    def get_cur(self, collection: str):
        return self.client[collection]

    def get_curs(self, collections: List[str]):
        cursors: List[pymongo.cursor.CursorType] = [self.client[collection] for collection in collections]
        return tuple(cursors)

    def get_all_curs(self):
        cursors: List[pymongo.cursor.CursorType] = \
            [self.client[collection] for collection in self.client.list_collection_names()]
        return tuple(cursors)
