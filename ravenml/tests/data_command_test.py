"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   04/06/19

Tests the ravenml data command group.
"""

import pytest
import boto3
import os
import click
from pathlib import Path
from moto import mock_s3
from shutil import copyfile
from click.testing import CliRunner
from ravenml.data.commands import list_datasets, inspect_dataset
from ravenml.utils.config import get_config
from ravenml.utils.local_cache import global_cache
from ravenml.utils.dataset import dataset_cache

### SETUP ###
mock = mock_s3()
runner = CliRunner()
test_dir = os.path.dirname(__file__)
test_data_dir = test_dir / Path('data')

def setup_module():
    """ Sets up the module for testing.
    """
    mock.start()
    
    # alter global and dataset cache objects used throughout ravenml for local caching
    global_cache.path = test_dir / Path('.testing')
    global_cache.ensure_exists()
    dataset_cache.path = global_cache.path / Path('datasets')
    
    # copy config file from test data into temporary testing_cache
    copyfile(test_data_dir / Path('config.yml'), global_cache.path / Path('config.yml'))

    config = get_config()
    S3 = boto3.resource('s3', region_name='us-east-1')
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    S3.create_bucket(Bucket=config['dataset_bucket_name'])
    bucket = S3.Bucket(config['dataset_bucket_name'])
    bucket.put_object(Key='test_dataset_1/metadata.json', Body=open(test_data_dir / Path('test_metadata_1.json'), 'rb'))
    bucket.put_object(Key='test_dataset_2/metadata.json', Body=open(test_data_dir / Path('test_metadata_2.json'), 'rb'))

def teardown_module():
    """ Tears down the module after testing.
    """
    global_cache.clean()
    mock.stop()    
    
    
# NOTE: there are no automated tests for prompt behavior of commands, as prompt-toolkit
# does not deal nicley with stdin not being an actual terminal (as pytest does it)

### TESTS ###
def test_list_no_flags():
    """Tests the list subcommmand with no flags.
    """
    result = runner.invoke(list_datasets)
    assert result.exit_code == 0
    assert result.output == 'test_dataset_1\ntest_dataset_2\n'

def test_list_detailed_flag():
    """Tests the list subcommmand with the -d (--detailed) flag
    """
    result = runner.invoke(list_datasets, ['-d'])
    assert result.exit_code == 0
    with open(test_data_dir / Path('detailed_list_output.txt'), 'r') as myfile:
        data = myfile.read()
    assert result.output == data
    
def test_inspect():
    """Tests the inspect subcommand.
    """
    result = runner.invoke(inspect_dataset, ['test_dataset_1'])
    assert result.exit_code == 0
    with open(test_data_dir / Path('inspection_output.txt'), 'r') as myfile:
        data = myfile.read()
    assert result.output == data
    
def test_inspect_invalid_dataset_name():
    """Tests the inspect subcommand with an invalid dataset name.
    """
    result = runner.invoke(inspect_dataset, ['bad_dataset_name'])
    assert result.exit_code == click.exceptions.BadParameter.exit_code
