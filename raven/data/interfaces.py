'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/19/2019

Classes necessary for interfacing with the data command group.
'''

from pathlib import Path

class Dataset(object):
    '''Represents a training dataset.

    Args:
        path (Path): path to dataset relative to local cache

    Attributes:
        dataset: name of the dataset to be used
        artifact_path: path to save artifacts. None if uploading to s3

    '''
    def __init__(self, name: str, metadata: dict):
        self._name = name
        self._metadata = metadata
    
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
        
