"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   04/06/19

Tests the ravenml config command group.
"""

import pytest
import os
import re
from pathlib import Path
from shutil import copyfile
from click.testing import CliRunner
from ravenml.config.commands import config, show, update
from ravenml.cli import clean
from ravenml.utils.local_cache import RMLCache
from ravenml.utils.dataset import dataset_cache
from ravenml.utils.config import get_config, update_config, config_cache

### SETUP ###
runner = CliRunner()
test_dir = os.path.dirname(__file__)
test_data_dir = test_dir / Path('data')
ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
test_cache = RMLCache()

def setup_module():
    """ Sets up the module for testing.
    """
    # alter global and dataset cache objects used throughout ravenml for local caching
    test_cache.path = test_dir / Path('.testing')
    test_cache.ensure_exists()
    config_cache.path = test_cache.path 
    
    # copy config file from test data into temporary testing cache
    copyfile(test_data_dir / Path('config.yml'), test_cache.path / Path('config.yml'))

def teardown_module():
    """ Tears down the module after testing.
    """
    test_cache.clean()
    

# NOTE: there are no automated tests for prompt behavior of commands, as prompt-toolkit
# does not deal nicley with stdin not being an actual terminal (as pytest does it)

### TESTS ###
def test_show():
    """ Tests the show subcommand.
    """
    result = runner.invoke(show)
    assert result.exit_code == 0
    with open(test_data_dir / Path('config_output.txt'), 'r') as myfile:
        data = myfile.read()
    sub = ansi_escape.sub('', result.output)
    assert sub == data

def test_update():
    """Tests the update subcommand in no user mode.
    """
    result = runner.invoke(update, ['--no-user', '-d', 'test_data_buck', '-m', 'test_art_buck', '-i', 'test_img_buck'])
    assert result.exit_code == 0
    with open(test_data_dir / Path('config_update_contents.txt'), 'r') as myfile:
        data = myfile.read()
    with open(test_cache.path / Path('config.yml'), 'r') as myfile:
        config_contents = myfile.read()
    assert config_contents == data
    
def test_update_no_config():
    """Basically the same as test_update, except we clean the existing configuration
    file away before calling it. Ensures the command properly deals with this scanario.
    """
    conf = get_config()
    test_cache.clean()
    result = runner.invoke(config, ['update', '--no-user', '-d', 'test_data_buck', '-m', 'test_art_buck', '-i', 'test_img_buck'])
    assert result.exit_code == 0
    with open(test_data_dir / Path('config_update_contents.txt'), 'r') as myfile:
        data = myfile.read()
    with open(test_cache.path / Path('config.yml'), 'r') as myfile:
        config_contents = myfile.read()
    assert config_contents == data
    update_config(conf)
