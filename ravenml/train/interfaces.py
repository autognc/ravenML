"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/03/2019

Contains the classes for interfacing with training command group.
"""

from ravenml.utils.question import cli_spinner, user_input, user_selects, user_confirms
from ravenml.utils.dataset import get_dataset_names, get_dataset
from ravenml.data.interfaces import Dataset

class TrainInput(object):
    """Represents a training input. Contains all plugin-independent information
    necessary for training. Plugins can define their own behavior for getting
    additional information.

    Args:
        inquire: ask user for inputs or not
        **kwargs: should be provided if inquire is set to False
            to populate TrainInput fields

    Attributes:
        dataset (Dataset): Dataset in use
        artifact_path (Path): path to save artifacts. None if uploading to s3
    """
    def __init__(self, inquire=True, **kwargs):
        if inquire:
            self._artifact_path = user_input('Enter filepath for artifacts:') if \
                                    user_confirms('Run in local mode?') else None
            dataset_options = cli_spinner('Finding datasets on S3', get_dataset_names)
            dataset = user_selects('Choose dataset:', dataset_options)
            self._dataset = cli_spinner(f'Downloading {dataset} from S3...', get_dataset, dataset)
        else:
            self._dataset = kwargs.get('dataset')
            self._artifact_path = kwargs.get('artifact_path')
    
    def local_mode(self):
        return self.artifact_path is not None

    @property
    def dataset(self):
        return self._dataset
        
    @dataset.setter
    def dataset(self, new_dataset: Dataset):
        self._dataset = new_dataset
        
    @property
    def artifact_path(self):
        return self._artifact_path
        
    @artifact_path.setter
    def artifact_path(self, new_path):
        self._artifact_path = new_path

class TrainOutput(object):
    """Training Output class

    Args:

    Attributes:
    
    """
    def __init__(self):
        pass
        