"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/18/2019

Handles local file caching for ravenml.
"""

import os
import shutil
from pathlib import Path

# local cache root path for ravenml application
RAVENML_LOCAL_STORAGE_PATH = Path(os.path.expanduser('~/.ravenML'))

class RMLCache(object):
    """Represents a local storage cache. Provides functions for
    ensuring the cache exists and making subpaths within it.

    Args:
        path (Path): Absolute path in filesystem to serve as root of the local cache.
    
    Attributes:
        path (Path): Absolute path in filesystem to root of the local cache.
    """

    # local cache root path for ravenml application
    RAVENML_LOCAL_STORAGE_PATH = Path(os.path.expanduser('~/.ravenML'))
    
    def __init__(self, path:str='.'):
        self.path = RAVENML_LOCAL_STORAGE_PATH / Path(path)
        # self.ensure_exists()

    def ensure_exists(self):
        """Ensures that the local storage cache exists on the machine.
        """
        os.makedirs(self.path, exist_ok=True)

    def subpath_exists(self, subpath: str) -> bool:
        """Checks if a subpath within the local storage cache exists.
        
        Args:
            subpath (str): desired subpath (i.e 'datasets/my_dataset')
        
        Returns:
            bool: true if subpath exists, false if not
        """
        return os.path.exists(self.path / Path(subpath))

    def ensure_subpath_exists(self, subpath: str):
        """Ensures the subpath exists in the local storage cache.
        
        Args:
            subpath (str): desired subpath (i.e 'datasets/my_dataset')
        """
        os.makedirs(self.path / Path(subpath), exist_ok=True)
    
    def ensure_clean_subpath(self, subpath:str):
        if self.subpath_exists(subpath):
            shutil.rmtree(self.path / Path(subpath))

    def clean(self) -> bool:
        """Cleans local storage cache.
        
        Returns:
            bool: True if successfully removed cache, false if no cache found for removal
        """
        try:
            shutil.rmtree(self.path)
            return True
        except FileNotFoundError:
            return False
    