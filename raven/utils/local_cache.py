"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/18/2019

Handles local file caching for raven.
"""

import os
import shutil
import click
from pathlib import Path

RAVEN_LOCAL_STORAGE_PATH = Path(os.path.expanduser('~/.raven-ml'))

class LocalCache(object):
    """Represents a local storage cache. Provides functions for
    ensuring the cache exists and making subpaths within it.

    Args:
        path (Path): Absolute path in filesystem to serve as root of the local cache.
    
    Attributes:
        path (Path): Absolute path in filesystem to root of the local cache.
    """

    def __init__(self, path=RAVEN_LOCAL_STORAGE_PATH):
        self._path = path
        self.ensure_exists()

    def exists(self):
        """Checks if local storage cache exists on the machine.
        
        Returns:
            bool: true if local cache exists, false if not
        """
        return os.path.exists(self.path)
        
    def ensure_exists(self):
        """Ensures that the local storage cache exists on the machine.
        """
        if not self.exists():
            self._create()

    def subpath_exists(self, subpath: str):
        """Checks if a subpath within the local storage_cache exists.
        
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
        if not self.subpath_exists(subpath):
            self._make_subpath(subpath)
        
    def clean(self):
        """Cleans local storage cache.
        """
        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:
            click.echo('Nothing to clean.')
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        self._path = path

    def _create(self):
        """Makes the local storage cache for raven.
        
        Not for external use (use ensure_exists() instead)
        """
        os.makedirs(self.path)

    def _make_subpath(self, subpath):
        """Creates a subpath within the local storage cache.

        Not for external use (use ensure_subpath_exists() instead)
        """
        os.makedirs(self.path / Path(subpath))
    
# importable global cache, should be used wherever possible
#
# Example use for datasets:
#
# from pathlib import Path
# from raven.utils.local_cache import LocalCache, global_cache
#
# dataset_cache = LocalCache(path=global_path.path / Path('datasets'))
#
global_cache = LocalCache()
