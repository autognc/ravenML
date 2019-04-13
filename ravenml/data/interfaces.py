"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/19/2019

Classes necessary for interfacing with the data command group.
"""

import os
import glob
from pathlib import Path

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
        path (Path): filepath to dataset
    """
    def __init__(self, name: str, metadata: dict, path: Path):
        self._name = name
        self._metadata = metadata
        self._path = path
        
    def get_num_folds(self):
        """Gets the number of folds this dataset supports for 
        k-fold cross validation.

        Returns:
            int: number of folds
        """
        path = self.path / Path('dev')
        return len(glob.glob(str(path) + FOLD_DIR_PREFIX + '*'))
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n: str):
        self._name = n
        
    @property
    def metadata(self):
        return self._metadata
    
    @metadata.setter
    def metadata(self, metadata: dict):
        self._metadata = metadata
        
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path: Path):
        self._path = path
