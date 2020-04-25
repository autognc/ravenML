import sys
import os
import boto3
import json
from pathlib import Path
from ravenml.utils.config import get_config
from ravenml.utils.local_cache import LocalCache

### DOWNLOAD FUNCTIONS ###
def list_bucket_prefixes(bucket_name: str):
    S3 = boto3.resource('s3')
    config = get_config()
    bucket_contents = S3.meta.client.list_objects(Bucket=bucket_name, Delimiter='/')
    contents = []
    if bucket_contents.get('CommonPrefixes') is not None:
        for obj in bucket_contents.get('CommonPrefixes'):
            contents.append(obj.get('Prefix')[:-1])
    return contents
    
def download_prefix(bucket_name: str, prefix: str, cache: LocalCache):
    """Downloads all files with the specified prefix into the provided local cache.

    Args:
        bucket_name (str): name of bucket
        prefix (str): prefix to filter on
        cache (LocalCache): cache to download files to
    
    Returns:
        bool: T if successful, F if no objects found
    """
    S3 = boto3.resource('s3')
    bucket = S3.Bucket(bucket_name)
    # filter bucket contents by prefix (add / to avoid accidental matching of invalid substrings
    # of valid dataset names)
    i = 0
    for obj in bucket.objects.filter(Prefix = prefix + '/'):
        # check to be sure object is not a folder by peeking at its last character
        i+=1
        if obj.key[-1] != '/':
            if not cache.subpath_exists(obj.key):
                subpath = os.path.dirname(obj.key)
                cache.ensure_subpath_exists(subpath)
                storage_path = cache.path / Path(obj.key)
                bucket.download_file(obj.key, str(storage_path))
    # T if objects were found and downloaded, F if not
    return i != 0

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
    


# class Save(object):
#     def __init__(self, upload_to_s3=True, 
#                     bucket_name='Trained Model Artifacts', 
#                     model_directory="~/trained_models"):
#         self._upload_to_s3 = True
#         self._bucket_name = bucket_name
#         self._model_dir = model_directory
    
#     @property
#     def upload_to_s3(self):
#         return self._upload_to_s3
    
#     @upload_to_s3.setter
#     def upload_to_s3(self, val):
#         self._upload_to_s3 = val

#     @property
#     def bucket_name(self):
#         return self._bucket_name
    
#     @bucket_name.setter
#     def bucket_name(self, bucket_name):
#         self._bucket_name = bucket_name
    
#     @property
#     def model_dir(self):
#         return self._model_dir
    
#     @model_dir.setter
#     def model_dir(self, path):
#         self._model_dir = path

#     def hook(self, t):
#         """ Simple callback function to update the progress bar on each of the files being uploaded to s3

#         Args:
#             t: a tqdm object that updates the progress bar
        
#         Returns:
#             None
#         """ 
#         def inner(bytes_amount):
#             t.update(bytes_amount)
#         return inner

#     def save_to_s3(self):
#         """ This function uploads trained model artifacts to an s3 bucket

#         This function upload model artifcats (the checkpoint files and .pb) to the specified directory. There is also a progress bar updating the user on the status of each file.

#         Args:
        
#         Returns:
#             None
#         """
#         if self.upload_to_s3:
#             try:
#                 s3 = boto3.resource('s3')
#                 s3_bucket = s3.Bucket(self.bucket_name)
#                 for file in Path(self.model_dir).iterdir():
#                     file_path = str(file)
#                     file_name = str(file.parts[-1])
#                     file_size = file.stat().st_size

#                     with tqdm(total=file_size, desc=file_name, miniters=1) as t:                   
#                         s3_bucket.upload_file(file_path, file_name, 
#                                               Callback=self.hook(t))
            
#             except Exception as e:
#                 print("Uh oh error occurred")
#                 print(e)
    