"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/13/2019

Utility module for managing Jigsaw created datasets.
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import boto3
from ravenml.utils.local_cache import LocalCache, global_cache
from ravenml.data.interfaces import Dataset
from ravenml.utils.config import get_config

# LocalCache within local cache for datasets
dataset_cache = LocalCache(path=global_cache.path / Path('datasets'))

### PUBLIC METHODS ###
def get_dataset_names():
    """Retrieves the names of all available datasets.

    Returns:
        list: dataset names
    """
    S3 = boto3.resource('s3')
    config = get_config()
    bucket_contents = S3.meta.client.list_objects(Bucket=config['dataset_bucket_name'], Delimiter='/')
    dataset_names = []
    if bucket_contents.get('CommonPrefixes') is not None:
        for obj in bucket_contents.get('CommonPrefixes'):
            dataset_names.append(obj.get('Prefix')[:-1])
    return dataset_names

def get_dataset_metadata(name: str, no_check=False):
    """Retrieves dataset metadata. Downloads from S3 if necessary.

    Args:
        name: string name of dataset
        no_check: whether to verify metadata existence

    Returns:
        dict: dataset metadata
        
    Raises:
        ValueError: if given dataset name is invalid
    """
    if not no_check:
        try:
            _ensure_metadata(name)
        except ClientError as e:
            raise ValueError(name) from e
    return json.load(open(dataset_cache.path / Path(name) / 'metadata.json'))

def get_dataset(name: str):
    """Retrives a dataset. Downloads from S3 if necessary.

    Args:
        name (str): string name of dataset
    
    Returns:
        Dataset: dataset itself
        
    Raises:
        ValueError: if dataset name is invalid (re raised)
    """
    try:
        _ensure_dataset(name)
        return Dataset(name, get_dataset_metadata(name, no_check=True), dataset_cache.path / Path(name))
    except ValueError:
        raise
 

### PRIVATE HELPERS ###
def _ensure_metadata(name: str):
    """Ensure dataset metadata exists.

    Args:
        name (str): name of dataset
    """
    S3 = boto3.resource('s3')
    config = get_config()
    DATASET_BUCKET = S3.Bucket(config['dataset_bucket_name'])
    metadata_path = Path(name) / 'metadata.json'
    if not dataset_cache.subpath_exists(metadata_path):
        dataset_cache.ensure_subpath_exists(name)
        metadata_key = f'{name}/metadata.json'
        metadata_absolute_path = dataset_cache.path / metadata_path
        DATASET_BUCKET.download_file(metadata_key, str(metadata_absolute_path))

def _ensure_dataset(name: str):
    """Ensures dataset exists.

    Args:
        name (str): name of dataset
        
    Raises:
        ValueError: if dataset name is invalid (no matching objects in S3 bucket)
    """
    S3 = boto3.resource('s3')
    config = get_config()
    DATASET_BUCKET = S3.Bucket(config['dataset_bucket_name'])
    # filter bucket contents by prefix (add / to avoid accidental matching of invalid substrings
    # of valid dataset names)
    i = 0
    for obj in DATASET_BUCKET.objects.filter(Prefix = name + '/'):
        # check to be sure object is not a folder by peeking at its last character
        i+=1
        if obj.key[-1] != '/':
            if not dataset_cache.subpath_exists(obj.key):
                subpath = os.path.dirname(obj.key)
                dataset_cache.ensure_subpath_exists(subpath)
                storage_path = dataset_cache.path / Path(obj.key)
                DATASET_BUCKET.download_file(obj.key, str(storage_path))
    if i == 0:
        raise ValueError(name)
