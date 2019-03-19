'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/13/2019

Utility module for interacting with Jigsaw created datasets.`
'''

import boto3
import os
import json
import raven.utils.file_handler as file_handler
from pathlib import Path

S3 = boto3.resource('s3')
DATASET_BUCKET = S3.Bucket('skr-datasets-test')

### PUBLIC METHODS ###

def get_dataset_names():
    '''Retrieves the name of all available datasets.
    
    Returns:
        list: dataset names
    '''
    bucket_contents = S3.meta.client.list_objects(Bucket='skr-datasets-test', Delimiter='/')
    dataset_names = []
    for obj in bucket_contents.get('CommonPrefixes'):
        dataset_names.append(obj.get('Prefix')[:-1])
    return dataset_names

def get_dataset_metadata(name):
    '''Retrieves dataset metadata if possible.

    Returns:
        dict: dataset metadata
    '''
    _ensure_metadata(name)
    return json.load(open(file_handler.RAVEN_LOCAL_STORAGE_PATH / Path(name) / 'metadata.json'))

def get_datasets():
    # TODO retrieve all datasets
    pass
    

### PRIVATE HELPERS ###
def _ensure_metadata(name):
    storage_path = file_handler.RAVEN_LOCAL_STORAGE_PATH / Path(name) / 'metadata.json'
    if not file_handler.subpath_exists(storage_path):
        file_handler.ensure_exists()
        file_handler.ensure_subpath_exists(name)
        metadata_key = f'{name}/metadata.json'
        DATASET_BUCKET.download_file(metadata_key, str(storage_path))
