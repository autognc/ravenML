"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/19/2019

Classes necessary for interfacing with the data command group.
"""

import os
import glob
from pathlib import Path
import ravenml.utils.local_cache as local_cache

### CONSTANTS ###
# these should be used in all possible situations to protect us
# in case they change in the future
STANDARD_DIR = 'standard'
FOLD_DIR_PREFIX = 'fold_'
TEST_DIR = 'test'

# TODO add necessary functionality to this class as needed

class Dataset(object):
    """Represents a training dataset.

    Args:
        name (str): name of dataset 
        metadata (dict): metadata of dataset

    Attributes:
        name (str): name of the dataset 
        metadata (dict): metadata of dataset
    """
    def __init__(self, name: str, metadata: dict):
        self._name = name
        self._metadata = metadata
        
    def get_num_folds(self):
        path = local_cache.ravenml_LOCAL_STORAGE_PATH / Path(self.name) / 'dev'
        return len(glob.glob(str(path) + FOLD_DIR_PREFIX + '*'))
    
    def get_dataset_path(self):
        path = local_cache.RAVENML_LOCAL_STORAGE_PATH / Path('datasets') / Path(self.name)
        return path
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n
        
    @property
    def metadata(self):
        return self._metadata
    
    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata
        
