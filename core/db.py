import os
import logging
import requests
from typing import Union
from pymongo import MongoClient
from local_module.uplink_python.uplink_python.uplink import Uplink
from local_module.uplink_python.uplink_python.errors import BucketNotEmptyError, BucketNotFoundError
from local_module.uplink_python.uplink_python.module_classes import ListObjectsOptions

# Mongodb database
account = os.environ.get("MONGODB_ACCOUNT")
password = os.environ.get("MONGODB_PASSWORD")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"

# set client
self_client = MongoClient(link)["sqcs-bot"]
fluctlight_client = MongoClient(link)["LightCube"]


# JsonApi semi-database


class JsonApi:
    def __init__(self):
        self.link_header = 'https://api.jsonstorage.net/v1/json/'

        # json link switcher
        self.json_links = str(os.environ.get("JSON_API_ADAPTER_LINK"))
        self.link_dict = requests.get(self.link_header + self.json_links).json()['links']

    def get(self, name) -> Union[dict, None]:
        if name not in self.link_dict.keys():
            return None

        response = requests.get(self.link_header + self.link_dict[name])
        return response.json()

    def put(self, name, alter_json) -> None:
        if name not in self.link_dict.keys():
            return None

        requests.put(self.link_header + self.link_dict[name], json=alter_json)


# static json db
rsp = JsonApi().get('HumanityExtension')


# humanity extension parser
async def huma_get(directory: str, ending: str = '') -> Union[str, list]:
    dir_split = directory.split('/')

    data = rsp
    for dirs in dir_split:
        if isinstance(data, dict):
            data = data.get(dirs)
        elif isinstance(data, list):
            data = data[int(dirs)]

    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return '\n'.join(data) + ending


# Storj database
STORJ_API_KEY = os.environ.get('STORJ_API_KEY')
STORJ_SATELLITE = os.environ.get('STORJ_SATELLITE')
STORJ_ENCRYPTION_PASSPHRASE = os.environ.get('STORJ_ENCRYPTION_PASSPHRASE')

uplink = Uplink()

access = uplink.request_access_with_passphrase(
    satellite=STORJ_SATELLITE,
    api_key=STORJ_API_KEY,
    passphrase=STORJ_ENCRYPTION_PASSPHRASE
)

project = access.open_project()


async def list_file(bucket: str):
    objects_list = project.list_objects(
        bucket,
        ListObjectsOptions(
            recursive=True,
            system=True
        )
    )
    # print all objects path
    for obj in objects_list:
        print(obj.key, " | ", obj.is_prefix)  # as python class object
        print(obj.get_dict())  # as python dictionary


async def create_bucket(bucket_name: str) -> bool:
    try:
        project.create_bucket(bucket_name)
        return True
    except:
        logging.warning(f'Error while creating bucket: {bucket_name}')
        return False


async def delete_bucket(bucket_name: str) -> bool:
    try:
        project.delete_bucket(bucket_name)
        return True
    # if delete bucket fails due to "not empty", delete all the objects and try again
    except BucketNotEmptyError as exception:
        logging.warning(f'Error while deleting bucket: {exception.message}')
        logging.warning("Deleting object's inside bucket and try to delete bucket again...")

        # list objects in given bucket recursively using ListObjectsOptions
        objects_list = project.list_objects(bucket_name, ListObjectsOptions(recursive=True))
        # iterate through all objects path
        for obj in objects_list:
            # delete selected object
            project.delete_object(bucket_name, obj.key)
        return False
    except BucketNotFoundError as exception:
        logging.warning(f'Desired bucket delete error: {exception.message}')
        return False


async def upload_file(bucket: str, local_file_path: str, target_file_path: str):
    with open(local_file_path, 'r+b') as file_handle:
        # get upload handle to specified bucket and upload file path
        upload = project.upload_object(bucket, target_file_path)
        # upload file on storj
        upload.write_file(file_handle)
        # commit the upload
        upload.commit()


async def download_file(bucket: str, local_file_path: str, target_file_path: str):
    with open(local_file_path, 'w+b') as file_handle:
        download = project.download_object(bucket, target_file_path)
        # download data from storj to file
        download.read_file(file_handle)
        # close the download stream
        download.close()
