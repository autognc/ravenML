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
from ravenml.utils.local_cache import RMLCache

### SETUP ###
runner = CliRunner()
test_dir = Path(os.path.dirname(__file__))
test_data_dir = test_dir / Path('data')
ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
test_cache = RMLCache()

def setup_module():
    """ Sets up the module for testing.
    """
    test_cache.path = test_dir / '.testing'

def teardown_module():
    """ Tears down the module after testing.
    """
    test_cache.clean()


### TESTS ###
def test_no_leaky_cache_creation():
    """Assues that simply running `ravenml` on the command line does not 
    create the local cache. Can indicate that somewhere a piece of code is 
    ensuring the existence of the local cache on import, which we DO NOT want.
    """
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert not os.path.exists(test_cache.path)
