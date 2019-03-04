import sys
import os
import boto3
from pathlib import Path
from tqdm import tqdm

class Save(object):
    def __init__(self, upload_to_s3=True, 
                    bucket_name='Trained Model Artifacts', 
                    model_directory="~/trained_models"):
        self._upload_to_s3 = True
        self._bucket_name = bucket_name
        self._model_dir = model_directory
    
    @property
    def upload_to_s3(self):
        return self._upload_to_s3
    
    @upload_to_s3.setter
    def upload_to_s3(self, val):
        self._upload_to_s3 = val

    @property
    def bucket_name(self):
        return self._bucket_name
    
    @bucket_name.setter
    def bucket_name(self, bucket_name):
        self._bucket_name = bucket_name
    
    @property
    def model_dir(self):
        return self._model_dir
    
    @model_dir.setter
    def model_dir(self, path):
        self._model_dir = path

    def hook(self, t):
        """ Simple callback function to update the progress bar on each of the files being uploaded to s3

        Args:
            t: a tqdm object that updates the progress bar
        
        Returns:
            None
        """ 
        def inner(bytes_amount):
            t.update(bytes_amount)
        return inner

    def save_to_s3(self):
        """ This function uploads trained model artifacts to an s3 bucket

        This function upload model artifcats (the checkpoint files and .pb) to the specified directory. There is also a progress bar updating the user on the status of each file.

        Args:
            None
        
        Returns:
            None
        """
        if self.upload_to_s3:
            try:
                s3 = boto3.resource('s3')
                s3_bucket = s3.Bucket(self.bucket_name)
                for file in Path(self.model_dir).iterdir():
                    file_path = str(file)
                    file_name = str(file.parts[-1])
                    file_size = file.stat().st_size

                    with tqdm(total=file_size, desc=file_name, miniters=1) as t:                   
                        s3_bucket.upload_file(file_path, file_name, 
                                              Callback=self.hook(t))
            
            except Exception as e:
                print("Uh oh error occurred")
                print(e)


# if __name__ == "__main__":
#     d = '/Users/pratyushsingh/Desktop/testing123'
#     s = Save(bucket_name='testing-upload-module', 
#                 model_directory=str(d))
#     s.save_to_s3()
    