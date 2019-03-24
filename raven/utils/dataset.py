'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/13/2019

Utility module for managing Jigsaw created datasets.
'''

import os
import json
from pathlib import Path
import boto3
import raven.utils.local_cache as local_cache
from raven.data.interfaces import Dataset

S3 = boto3.resource('s3')
DATASET_BUCKET = S3.Bucket('skr-datasets-test')

# path within local cache for datasets
DATASET_PATH = local_cache.RAVEN_LOCAL_STORAGE_PATH / Path('datasets')

### PUBLIC METHODS ###
def get_dataset_names():
    '''Retrieves the names of all available datasets.

    Returns:
        list: dataset names
    '''
    bucket_contents = S3.meta.client.list_objects(Bucket='skr-datasets-test', Delimiter='/')
    dataset_names = []
    for obj in bucket_contents.get('CommonPrefixes'):
        dataset_names.append(obj.get('Prefix')[:-1])
    return dataset_names

def get_dataset_metadata(name: str, no_check=False):
    '''Retrieves dataset metadata. Downloads from S3 if necessary.

    Args:
        name: string name of dataset
        no_check: whether to verify metadata existence

    Returns:
        dict: dataset metadata
    '''
    if not no_check:
        _ensure_metadata(name)
    return json.load(open(DATASET_PATH / Path(name) / 'metadata.json'))

def get_dataset(name: str):
    '''Retrives a dataset. Downloads from S3 if necessary.

    Args:
        name (str): string name of dataset
    
    Returns:
        Dataset: dataset itself
    '''
    _ensure_dataset(name)
    return Dataset(name, get_dataset_metadata(name, no_check=True))
 

### PRIVATE HELPERS ###
def _to_dataset_dir(path: str):
    '''Convert a path to be within the datasets directory
    in the local storage cache.
    
    Args:
        path (str): path to convert
    
    Returns:
        Path: converted path
    '''
    return Path('datasets') / Path(path)

def _ensure_metadata(name: str):
    '''Ensure dataset metadata exists.

    Args:
        name (str): name of dataset
    '''
    metadata_path = DATASET_PATH / Path(name) / 'metadata.json'
    if not local_cache.subpath_exists(metadata_path):
        local_cache.ensure_exists()
        local_cache.ensure_subpath_exists(_to_dataset_dir(name))
        metadata_key = f'{name}/metadata.json'
        DATASET_BUCKET.download_file(metadata_key, str(metadata_path))

def _ensure_dataset(name: str):
    '''Ensures dataset exists.

    Args:
        name (str): name of dataset
    '''
    local_cache.ensure_exists()
    local_cache.ensure_subpath_exists(_to_dataset_dir(name))
    for obj in DATASET_BUCKET.objects.filter(Prefix = name):
        local_key = _to_dataset_dir(name)
        if not local_cache.subpath_exists(local_key):
            subpath = os.path.dirname(local_key)
            local_cache.ensure_subpath_exists(subpath)
            storage_path = DATASET_PATH / Path(obj.key)
            DATASET_BUCKET.download_file(obj.key, str(storage_path))

