import pytest
import os
import re
from pathlib import Path
from shutil import copyfile
from click.testing import CliRunner
from raven.config.commands import show, update
from raven.utils.local_cache import global_cache
from raven.utils.dataset import dataset_cache

### SETUP ###
runner = CliRunner()
test_dir = os.path.dirname(__file__)
test_data_dir = test_dir / Path('data')
ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')

def setup_module():
    """ setup any state specific to the execution of the given module."""
    # alter global and dataset cache objects used throughout raven for local caching
    global_cache.path = test_dir / Path('.testing')
    global_cache.ensure_exists()
    dataset_cache.path = global_cache.path / Path('datasets')
    
    # copy config file from test data into temporary testing cache
    copyfile(test_data_dir / Path('config.yml'), global_cache.path / Path('config.yml'))

def teardown_module():
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    global_cache.clean()
    

### TESTS ###
def test_show():
    result = runner.invoke(show)
    assert result.exit_code == 0
    with open(test_data_dir / Path('config_output.txt'), 'r') as myfile:
        data = myfile.read()
    sub = ansi_escape.sub('', result.output)
    assert sub == data

# def test_update():
#     result = runner.invoke(update, input='\r\r')
#     assert result.exit_code == 0
