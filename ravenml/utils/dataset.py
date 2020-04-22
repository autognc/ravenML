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
from ravenml.utils.local_cache import LocalCache, global_cache
from ravenml.utils.config import get_config
from ravenml.utils.aws import list_bucket_prefixes, download_prefix
from ravenml.data.interfaces import Dataset

# LocalCache within local cache for datasets
dataset_cache = LocalCache(path=global_cache.path / Path('datasets'))
# name of config field
BUCKET_FIELD = 'dataset_bucket_name'

### PUBLIC METHODS ###
def get_dataset_names() -> list:
    """Retrieves the names of all available datasets.

    Returns:
        list: dataset names
    """
    config = get_config()
    return list_bucket_prefixes(config[BUCKET_FIELD])

def get_dataset_metadata(name: str, no_check=False) -> dict:
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

def get_dataset(name: str) -> Dataset:
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
    config = get_config()
    if not download_prefix(config[BUCKET_FIELD], name, dataset_cache):
        raise ValueError(name)
