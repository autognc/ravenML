"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   04/11/19

Tests the ravenml local_cache module.

NOTE: If this test fails, it may cause cascades of failures in other tests.
"""

import pytest
import os
import re
from pathlib import Path
from click.testing import CliRunner
from ravenml.cli import cli
from ravenml.utils.local_cache import global_cache

### SETUP ###
runner = CliRunner()
test_dir = os.path.dirname(__file__)
test_data_dir = test_dir / Path('data')
ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')

def setup_module():
    """ Sets up the module for testing.
    """
    # alter global and dataset cache objects used throughout ravenml for local caching
    global_cache.path = test_dir / Path('.testing')
    # global_cache.ensure_exists()
    
    # copy config file from test data into temporary testing cache
    # copyfile(test_data_dir / Path('config.yml'), global_cache.path / Path('config.yml'))

def teardown_module():
    """ Tears down the module after testing.
    """
    global_cache.clean()
    

# NOTE: there are no automated tests for prompt behavior of commands, as prompt-toolkit
# does not deal nicley with stdin not being an actual terminal (as pytest does it)

### TESTS ###
def test_no_leaky_cache_creation():
    """Assues that simply running `ravenml` on the command line does not 
    create the local cache. Can indicate that somewhere a piece of code is 
    ensuring the existence of the local cache on import, which we DO NOT want.
    """
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert not os.path.exists(global_cache.path)
