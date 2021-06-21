import os
import aioboto3
import boto3
import json
import subprocess
import asyncio
from pathlib import Path
from ravenml.utils.config import get_config
from ravenml.utils.local_cache import RMLCache

### DOWNLOAD FUNCTIONS ###
def list_top_level_bucket_prefixes(bucket_name: str):
    """Lists all top level prefixes in an S3 bucket.
    
    A top level prefix means it is the first in the chain. This will not list
    any subprefixes. 
    Ex: Bucket contains an element a/b/c/d.json, this function will only list a.
    
    Args:
        bucket_name (str): name of S3 bucket
        
    Returns:
        list: prefix strings
    """
    S3 = boto3.resource('s3')
    config = get_config()
    bucket_contents = S3.meta.client.list_objects(Bucket=bucket_name, Delimiter='/')
    contents = []
    if bucket_contents.get('CommonPrefixes') is not None:
        for obj in bucket_contents.get('CommonPrefixes'):
            contents.append(obj.get('Prefix')[:-1])
    return contents
    
def download_prefix(bucket_name: str, prefix: str, cache: RMLCache, custom_path: str = None):
    """Downloads all files with the specified prefix into the provided local cache.

    Args:
        bucket_name (str): name of bucket
        prefix (str): prefix to filter on
        cache (RMLCache): cache to download files to
        custom_path (str, optional): custom subpath in cache
            to download files to
    
    Returns:
        bool: T if successful, F if no objects found
    """
    try:
        s3_uri = 's3://' + bucket_name + '/' + prefix 
        if custom_path:
            local_path = cache.path / custom_path / prefix
        else:
            local_path = cache.path / prefix

        subprocess.call(["aws", "s3", "sync", s3_uri, str(local_path), '--quiet'])
        return True
    except:
        return False

def download_imageset_file(prefix: str, local_path: str):
    """Downloads file into the provided location. Meant for plugins to
        download imageset-wide required files, not images or related information

    Args:
        prefix (str): path to s3 file
        local_path (str): local path for where files are
            downloaded to

    Returns:
        bool: T if successful, F if no objects found
    """
    bucketConfig = get_config()
    image_bucket_name = bucketConfig.get('image_bucket_name')
    try:
        s3_uri = 's3://' + image_bucket_name + '/' + prefix 

        subprocess.call(["aws", "s3", "cp", s3_uri, str(local_path), '--quiet'])
        return True
    except:
        return False

async def conditional_download(bucket_name, prefix, local_path, cond_func = lambda x: True):
    """Downloads all files with the specified prefix into the provided local cache based on a condition.

    Args:
        bucket_name (str): name of bucket
        prefix (str): prefix to filter on
        local_path (str): where to download to
        cond_func (function, optional): boolean function specifying which
            files to download

    Returns:
        bool: T if successful, F if no objects found
    """
    try:
        async with aioboto3.resource("s3") as s3:
            bucket = await s3.Bucket(bucket_name)
            async for s3_object in bucket.objects.filter(Prefix=prefix+"/"):
                if cond_func(s3_object.key.split('/')[-1]) and not os.path.exists(local_path / s3_object.key):
                    await bucket.download_file(s3_object.key, local_path / s3_object.key)
    except:
        return False
    return True

def download_file_list(bucket_name, file_list):
    """Downloads all files with the specified prefix into the provided local cache based on a condition.

    Args:
        bucket_name (str): name of bucket
        file_list (str): list of files in format [(s3_prefix, local_path)] for 
            what to download

    Returns:
        bool: T if successful, F if no objects found
    """
    async def download_helper(bucket_name, file_list):
        async with aioboto3.resource("s3") as s3:
            bucket = await s3.Bucket(bucket_name)
            for f in file_list:
                if not os.path.exists(f[1]):
                    try:
                        await bucket.download_file(f[0], f[1])
                    except Exception as e:
                        if e.response['Error']['Code'] != '404':
                            return False
        return True

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_helper(bucket_name, file_list))

### UPLOAD FUNCTIONS ###
def upload_file_to_s3(prefix: str, file_path: Path, alternate_name=None):
    """Uploads file at given file path to model bucket on S3.

    Args:
        prefix (str): prefix for filename on S3
        file_path (Path): path to file
        alternate_name (str, optional): name to override local file name
    """
    S3 = boto3.resource('s3')
    config = get_config()
    model_bucket = S3.Bucket(config['model_bucket_name'])
    upload_path = prefix + '/' + file_path.name if alternate_name is None \
                    else prefix + '/' + alternate_name
    model_bucket.upload_file(str(file_path), upload_path)
        
def upload_dict_to_s3_as_json(s3_path: str, obj: dict):
    """Uploads given dictionary to model bucket on S3.

    Args:
        s3_path (str): full s3 path to save dictionary to, (no .json)
        obj (dict): dictionary to save
    """
    S3 = boto3.resource('s3')
    config = get_config()
    model_bucket = S3.Bucket(config['model_bucket_name'])   
    model_bucket.put_object(Body=json.dumps(obj, indent=2), Key=s3_path+'.json')

def upload_directory(bucket_name, prefix, local_path):
    """Recursively uploads a directory to S3
    
    Args:
        bucket_name (str): the name of the S3 bucket to upload to
        prefix (str): the name of the prefix to be uploaded to
        local_path (str): local path to directory being uploaded
    """
    
    s3_uri = 's3://' + bucket_name + '/' + prefix 
    subprocess.call(["aws", "s3", "sync", local_path, s3_uri, '--quiet'])
