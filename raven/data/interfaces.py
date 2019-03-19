'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/19/2019

Classes necessary for interfacing with the data command group.
'''

from pathlib import Path

class Dataset(object):
    '''Represents a training dataset.

    Args:
        

    Attributes:
        dataset: name of the dataset to be used
        artifact_path: path to save artifacts. None if uploading to s3
    
    '''
    def __init__(self, path: Path, metadata: dict):
        self._metadata = metadata
        self._path = path
        
