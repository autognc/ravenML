"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/13/2019

Utility module for managing Jigsaw created datasets.
"""

import json
import boto3
from pathlib import Path
from botocore.exceptions import ClientError
from ravenml.utils.local_cache import RMLCache
from ravenml.utils.config import get_config
from ravenml.utils.aws import list_top_level_bucket_prefixes

imageset_cache = RMLCache('imagesets')
# name of config field
BUCKET_FIELD = 'image_bucket_name'

### PUBLIC METHODS ###
def get_imageset_names() -> list:
    """Retrieves the names of all available imagesets in bucket pointed to by global config.

    Returns:
        list: imageset names
    """
    config = get_config()
    return list_top_level_bucket_prefixes(config[BUCKET_FIELD])

def get_imageset_metadata(name: str, no_check=False) -> dict:
    """Retrieves imageset metadata. Downloads from S3 if necessary.

    Args:
        name (str): string name of imageset
        no_check (bool, optional): whether to verify metadata existence

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
        except StopIteration as e:
            raise KeyError(name) from e
    return json.load(open(imageset_cache.path / Path(name) / 'metadata.json'))

# NOTE: this function is left here as a template for the eventual "get_imageset" function
# not implemented yet because we may find a better way to get image sets than actually downloading them locally
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
        
    Raises:
        ClientError: If the given imageset name does not exist in the S3 bucket.
        StopIteration: If the given imageset does not have any metadata files named according to the standard scheme.
    """
    S3 = boto3.resource('s3')
    config = get_config()
    image_bucket = S3.Bucket(config[BUCKET_FIELD])
    cache_metadata_path = Path(name) / 'metadata.json'      # relative path inside the cache where metadata will go
    if not imageset_cache.subpath_exists(cache_metadata_path):
        imageset_cache.ensure_subpath_exists(name)
        # attempt to download set-wide metadata.json
        imageset_bucket_metadata_key = f'{name}/metadata.json'
        metadata_download_absolute_path = imageset_cache.path / cache_metadata_path
        try:
            # attempt to grab imageset-wide metadata
            image_bucket.download_file(imageset_bucket_metadata_key, str(metadata_download_absolute_path))
        except ClientError as e:
            # fallback to grabbing a single image metadata file (better than nothing)
            prefix = f'{name}/meta_'
            # get all items in bucket with this prefix, but limit results to 1
            image_metadata_key_collection = image_bucket.objects.filter(Delimiter='/', Prefix=prefix).limit(1)
            # filter() returns a collection iterable, which we must convert to an iterator (generator) and call next on
            try:
                image_metadata_key = next(iter(image_metadata_key_collection)).key
                image_bucket.download_file(image_metadata_key, str(metadata_download_absolute_path))
            # explicitly reraise these errors for verbosity
            except ClientError as e:
                raise
            except StopIteration as e:
                raise

# NOTE: this function is left here as a template for the eventual "ensure_imageset" function
# not implemented yet because we may find a better way to get image sets than actually downloading them locally
# def _ensure_dataset(name: str):
#     """Ensures dataset exists.

#     Args:
#         name (str): name of dataset
        
#     Raises:
#         ValueError: if dataset name is invalid (no matching objects in S3 bucket)
#     """
    # config = get_config()
    # if not download_prefix(config[BUCKET_FIELD], name, dataset_cache):
    #     raise ValueError(name)
