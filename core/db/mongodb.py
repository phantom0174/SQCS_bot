import os
from typing import List, Tuple
from mongodb import MongoClient

# Mongodb database
account = os.environ.get("MONGODB_ACCOUNT")
password = os.environ.get("MONGODB_PASSWORD")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"


class Mongo:
    @staticmethod
    async def get_cursors(database: str, collections: List[str]) -> Tuple:
        if database not in MongoClient(link).database_names():
            raise BaseException(
                f'ARGUMENT ERROR: database not in {MongoClient(link).database_names()}',
                database
            )
        
        # Notice: not tested and not compiled
        client = MongoClient(link)[database]

        for collection in collections:
            if collection not in client.collection_names():
                raise BaseException(
                    f'ARGUMENT ERROR: collection not in {client.collection_names()}',
                    collection
                )

        cursors = list()
        for collection in collections:
            cursor = client[collection]
            cursors.append(cursor)
        
        return tuple(cursors)
