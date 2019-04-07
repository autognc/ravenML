import pytest
import boto3
import os
from pathlib import Path
from moto import mock_s3
from shutil import copyfile
from click.testing import CliRunner
from raven.data.commands import list, inspect
from raven.utils.config import get_config
from raven.utils.local_cache import global_cache
from raven.utils.dataset import dataset_cache

### SETUP ###
mock = mock_s3()
runner = CliRunner()
test_dir = os.path.dirname(__file__)
test_data_dir = test_dir / Path('data')

def setup_module():
    """ setup any state specific to the execution of the given module."""
    mock.start()
    
    # alter global and dataset cache objects used throughout raven for local caching
    global_cache.path = test_dir / Path('.testing')
    global_cache.ensure_exists()
    dataset_cache.path = global_cache.path / Path('datasets')
    
    # copy config file from test data into temporary testing cache
    copyfile(test_data_dir / Path('config.yml'), global_cache.path / Path('config.yml'))

    config = get_config()
    
    S3 = boto3.resource('s3')
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    S3.create_bucket(Bucket=config['dataset_bucket_name'])
    bucket = S3.Bucket(config['dataset_bucket_name'])
    bucket.put_object(Key='test_dataset_1/metadata.json', Body=open(test_data_dir / Path('test_metadata_1.json'), 'rb'))
    bucket.put_object(Key='test_dataset_2/metadata.json', Body=open(test_data_dir / Path('test_metadata_2.json'), 'rb'))
    

def teardown_module():
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    global_cache.clean()
    mock.stop()    
    

### TESTS ###
def test_list_no_flags():
    result = runner.invoke(list)
    assert result.exit_code == 0
    assert result.output == 'test_dataset_1\ntest_dataset_2\n'

def test_list_detailed_flag():
    result = runner.invoke(list, ['-d'])
    assert result.exit_code == 0
    with open(test_data_dir / Path('detailed_list_output.txt'), 'r') as myfile:
        data = myfile.read()
    assert result.output == data
    
def test_inspect():
    result = runner.invoke(inspect, ['test_dataset_1'])
    assert result.exit_code == 0
    with open(test_data_dir / Path('inspection_output.txt'), 'r') as myfile:
        data = myfile.read()
    assert result.output == data
