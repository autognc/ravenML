import pytest
import os
import boto3
from ..utils.aws import Save

class TestSave(object):
    def tests_create_file(self, tmp_path):
        contents_of_file = "baby"
        filename_key = "hello.txt"
        d = tmp_path / "testing"
        d.mkdir()
        p = d / filename_key
        p.write_text(contents_of_file)

        s = Save(bucket_name='testing-upload-module', 
                model_directory=str(d))
        
        s.save_to_s3()

        # testing if the file got succesfully uploaded to s3
        file_found = False
        s3 = boto3.resource('s3')
        s3_bucket = s3.Bucket(s.bucket_name)

        for obj in s3_bucket.objects.all():
            if obj.key == filename_key:
                file_found = True
                break
        
        assert file_found

        








