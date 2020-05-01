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
from ravenml.utils.local_cache import RMLCache
from ravenml.utils.config import get_config
from ravenml.utils.aws import list_bucket_prefixes

imageset_cache = RMLCache('imagesets')
# name of config field
BUCKET_FIELD = 'image_bucket_name'

### PUBLIC METHODS ###
def get_imageset_names() -> list:
    """Retrieves the names of all available imagesets.

    Returns:
        list: imageset names
    """
    config = get_config()
    return list_bucket_prefixes(config[BUCKET_FIELD])

def get_imageset_metadata(name: str, no_check=False) -> dict:
    """Retrieves imageset metadata. Downloads from S3 if necessary.

    Args:
        name: string name of imageset
        no_check: whether to verify metadata existence

    Returns:
        dict: imageset metadata
        
    Raises:
        ValueError: if given imageset name is invalid
    """
    if not no_check:
        try:
            _ensure_metadata(name)
        except ClientError as e:
            raise ValueError(name) from e
    return json.load(open(imageset_cache.path / Path(name) / 'metadata.json'))

# def get_dataset(name: str) -> Dataset:
#     """Retrives a dataset. Downloads from S3 if necessary.

#     Args:
#         name (str): string name of dataset
    
#     Returns:
#         Dataset: dataset itself
        
#     Raises:
#         ValueError: if dataset name is invalid (re raised)
#     """
#     try:
#         _ensure_dataset(name)
#         return Dataset(name, get_dataset_metadata(name, no_check=True), dataset_cache.path / Path(name))
#     except ValueError:
#         raise
 

### PRIVATE HELPERS ###
def _ensure_metadata(name: str):
    """Ensure imageset metadata exists.
    NOTE: This function works around the fact that we don't have
    imageset wide metadata files for all imagesets. In that case, it
    picks a random metadata file and reports the fields contained within.

    Args:
        name (str): name of imageset
    """
    S3 = boto3.resource('s3')
    config = get_config()
    image_bucket = S3.Bucket(config[BUCKET_FIELD])
    metadata_path = Path(name) / 'metadata.json'
    if not imageset_cache.subpath_exists(metadata_path):
        imageset_cache.ensure_subpath_exists(name)
        # attempt to download raw metadata.json
        metadata_key = f'{name}/metadata.json'
        metadata_absolute_path = imageset_cache.path / metadata_path
        try:
            # attempt to grab imageset-wide metadata
            image_bucket.download_file(metadata_key, str(metadata_absolute_path))
        except ClientError as e:
            # fallback to grabbing a single image metadata file (better than nothing)
            pre = f'{name}/meta_'
            metadata_key = image_bucket.objects.filter(Delimiter='/', Prefix=pre).limit(1)
            metadata_key = metadata_key[0].key
            image_bucket.download_file(metadata_key, str(metadata_absolute_path))

# def _ensure_dataset(name: str):
#     """Ensures dataset exists.

#     Args:
#         name (str): name of dataset
        
#     Raises:
#         ValueError: if dataset name is invalid (no matching objects in S3 bucket)
#     """
#     S3 = boto3.resource('s3')
#     config = get_config()
#     DATASET_BUCKET = S3.Bucket(config['dataset_bucket_name'])
#     # filter bucket contents by prefix (add / to avoid accidental matching of invalid substrings
#     # of valid dataset names)
#     i = 0
#     for obj in DATASET_BUCKET.objects.filter(Prefix = name + '/'):
#         # check to be sure object is not a folder by peeking at its last character
#         i+=1
#         if obj.key[-1] != '/':
#             if not dataset_cache.subpath_exists(obj.key):
#                 subpath = os.path.dirname(obj.key)
#                 dataset_cache.ensure_subpath_exists(subpath)
#                 storage_path = dataset_cache.path / Path(obj.key)
#                 DATASET_BUCKET.download_file(obj.key, str(storage_path))
#     if i == 0:
#         raise ValueError(name)
