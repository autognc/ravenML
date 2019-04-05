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

    def __init__(self, path=RAVEN_LOCAL_STORAGE_PATH):
        self._path = path
        self.ensure_exists()

    def exists(self):
        """Checks if local storage cache exists on the machine.
        """
        return os.path.exists(self.path)
        
    def ensure_exists(self):
        """Ensures that the local storage cache exists on the machine.
        """
        if not self.exists():
            self._create()

    def subpath_exists(self, subpath: str):
        """Checks if a subpath within the local storage_cache exists.
        """
        return os.path.exists(self.path / Path(subpath))

    def ensure_subpath_exists(self, subpath: str):
        """Ensures the subpath exists in the local storage cache.
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
    
global_cache = LocalCache()
    
# #### YUP

# def exists():
#     """Checks if local storage cache exists on the machine.
#     """
#     return os.path.exists(RAVEN_LOCAL_STORAGE_PATH)
    
# def ensure_exists():
#     """Ensures that the local storage cache exists on the machine.
#     """
#     if not exists():
#         _create()

# def subpath_exists(subpath: str):
#     """Checks if a subpath within the local storage_cache exists.
#     """
#     return os.path.exists(RAVEN_LOCAL_STORAGE_PATH / Path(subpath))

# def ensure_subpath_exists(subpath: str):
#     """Ensures the subpath exists in the local storage cache.
#     """
#     if not subpath_exists(subpath):
#         _make_subpath(subpath)
    
# def clean():
#     """Cleans local storage cache.
#     """
#     try:
#         shutil.rmtree(RAVEN_LOCAL_STORAGE_PATH)
#     except FileNotFoundError:
#         click.echo('Nothing to clean.')

# def _create():
#     """Makes the local storage cache for raven.
    
#     Not for external use (use ensure_exists() instead)
#     """
#     os.mkdir(RAVEN_LOCAL_STORAGE_PATH)

# def _make_subpath(subpath):
#     """Creates a subpath within the local storage cache.

#     Not for external use (use ensure_subpath_exists() instead)
#     """

#     os.makedirs(RAVEN_LOCAL_STORAGE_PATH / Path(subpath), exist_ok=True)
