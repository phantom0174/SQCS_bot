import os
import shutil
import logging
from local_module import (
    Uplink, BucketNotEmptyError, BucketNotFoundError, ListObjectsOptions
)


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

# Download options
DOWNLOAD_BASE_PATH = './bot/buffer/storj_download'


async def list_file(bucket_name: str, options: dict = None):
    # default options
    options = options or {
        "prefix": '',
        "recursive": True,
        "system": False
    }

    objects_list = project.list_objects(
        bucket_name,
        ListObjectsOptions(**options)
    )

    return [obj.key for obj in objects_list]


async def delete_file(bucket_name: str, storj_path: str) -> bool:
    try:
        project.delete_object(bucket_name, storj_path)
        return True
    except BaseException:
        logging.warning(f'Error while deleting files: {bucket_name}, {storj_path}')
        return False


async def delete_folder(bucket_name: str, storj_path: str):
    search_options = {
        "prefix": storj_path,
        "recursive": True,
        "system": False
    }
    for file in list_file(bucket_name, search_options):
        if '.' in file.split('/')[-1]:
            await delete_file(bucket_name, file)


async def create_bucket(bucket_name: str) -> bool:
    try:
        project.create_bucket(bucket_name)
        return True
    except BaseException:
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


async def upload_file(bucket_name: str, local_path: str, storj_path: str):
    with open(local_path, 'r+b') as file_handle:
        # get upload handle to specified bucket and upload file path
        upload = project.upload_object(bucket_name, storj_path)
        # upload file on storj
        upload.write_file(file_handle)
        # commit the upload
        upload.commit()


async def download_file(bucket_name: str, local_path: str, storj_path: str):
    with open(local_path, 'w+b') as file_handle:
        download = project.download_object(bucket_name, storj_path)
        # download data from storj to file
        download.read_file(file_handle)
        # close the download stream
        download.close()


async def download_folder(bucket_name: str, storj_path: str):
    download_path = (
        f'{DOWNLOAD_BASE_PATH}/{"_".join(storj_path[:-1].split("/"))}'
    )
    try:
        shutil.rmtree(DOWNLOAD_BASE_PATH)
    except BaseException:
        pass

    os.makedirs(download_path)

    async def traverse_folder(bucket_name: str, storj_path: str):
        search_options = {
            "prefix": storj_path,
            "recursive": False,
            "system": False
        }
        for child in list_file(bucket_name, search_options):
            if child.endswith('/'):
                # [:-1]: 'a/b/c/' -> 'a/b/c'
                child_local_path = f'{download_path}/{child[:-1]}'
                if not os.path.exists(child_local_path):
                    os.makedirs(child_local_path)

                await traverse_folder(
                    bucket_name=bucket_name,
                    storj_path=child
                )
            elif '.' in child.split('/')[-1]:
                child_local_path = f'{download_path}/{child}'
                await download_file(
                    bucket_name=bucket_name,
                    local_path=child_local_path,
                    storj_path=child
                )

    await traverse_folder(
        bucket_name=bucket_name,
        storj_path=storj_path
    )
