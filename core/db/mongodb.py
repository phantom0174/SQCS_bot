import os
import logging
from typing import List, Tuple, Union
from pymongo import MongoClient

# Mongodb database
account = os.environ.get("MONGODB_ACCOUNT")
password = os.environ.get("MONGODB_PASSWORD")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"


async def db_exists(database: str):
    if database not in MongoClient(link).list_database_names():
        logging.warning(f"{database} didn't exists!")
        return False
    return True


async def collection_exists(client, collection: str):
    if collection not in client.list_collection_names():
        logging.warning(f"{collection} didn't exists under client {client}!")
        return False
    return True


async def get_cursors(database: str, collections: List[str]) -> Union[Tuple, None]:
    if not (await db_exists(database)):
        return None

    # Notice: not tested and not compiled
    client = MongoClient(link)[database]

    for collection in collections:
        if not (await collection_exists(client, collection)):
            return None

    cursors = [client[collection] for collection in collections]
    return tuple(cursors)


async def get_all_cursors(database: str):
    if not (await db_exists(database)):
        return None

    client = MongoClient(link)[database]

    cursors = [client[collection] for collection in client.list_collection_names()]
    return tuple(cursors)

