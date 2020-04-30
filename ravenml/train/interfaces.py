"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/03/2019

Contains the classes for interfacing with training command group.
"""
import os
from pathlib import Path
from ravenml.utils.question import cli_spinner, user_input, user_selects, user_confirms
from ravenml.utils.dataset import get_dataset_names, get_dataset
from ravenml.data.interfaces import Dataset



class TrainInput(object):
    """Represents a training input. Contains all plugin-independent information
    necessary for training. Plugins can define their own behavior for getting
    additional information.

    Kwargs:
        dataset_name (str, optional): name of dataset stored on S3 to use.
            Defaults to None, in which case user is prompted.
        artifact_path (str, optional): local filepath to save artifacts. 
            Defaults to None to direct S3 upload.

    Attributes:
        dataset (Dataset): Dataset in use
        artifact_path (Path): path to save artifacts. None if uploading to s3
    """
    
    ## NOTE: ##
    # Constructor uses only kwargs to make it compatible for use with
    # a Click pass decorator with ensure=True, which requires a default 
    # constructor with no positional arguments. 
    # The pass decorator with ensure=True is what allows 
    # creation of a TrainInput directly in the ravenml train command
    # ONLY when arguments are passed, which allows --help and other plugin
    # subcommands to be unaffected by TrainInput construction when a training
    # is not actually being started.
    def __init__(self, dataset_name=None, artifact_path=None):
        # prompt for dataset if not provided
        if dataset_name is None:
            dataset_options = cli_spinner('Finding datasets on S3...', get_dataset_names)
            dataset_name = user_selects('Choose dataset:', dataset_options)
        # download dataset and populate field
        self._dataset = cli_spinner(f'Downloading {dataset_name} from S3...', 
            get_dataset, dataset_name)
        self._artifact_path = artifact_path

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
    def artifact_path(self, new_path: str):
        self._artifact_path = new_path

class TrainOutput(object):
    """Training Output class

    Args:
        metadata (dict): metadata associated with training
        artifact_path (Path): path to root of training artifacts
        model_path (Path): path to final exported model
        extra_files (list): list of Path objects to extra files associated with the training
        local_mode (bool): whether this training was run in local mode or not

    Attributes:
        metadata (dict): metadata associated with training
        artifact_path (Path): path to root of training artifacts
        model_path (Path): path to final exported model
        extra_files (list): list of Path objects to extra files associated with the training
        local_mode (bool): whether this training was run in local mode or not
    """
    def __init__(self, metadata: dict, artifact_path: Path, model_path: Path, extra_files: list, local_mode: bool):
        self._metadata = metadata
        self._artifact_path = artifact_path
        self._model_path = model_path
        self._extra_files = extra_files
        self._local_mode = local_mode
        
    @property
    def metadata(self):
        return self._metadata
    
    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata
    
    @property
    def artifact_path(self):
        return self._artifact_path
        
    @artifact_path.setter
    def artifact_path(self, new_path):
        self._artifact_path = new_path
        
    @property
    def model_path(self):
        return self._model_path
    
    @model_path.setter
    def model_path(self, new_path):
        self._model_path = new_path

    @property
    def extra_files(self):
        return self._extra_files
    
    @extra_files.setter
    def extra_files(self, new_files):
        self._extra_files = new_files
    
    @property
    def local_mode(self):
        return self._local_mode
    

    
# dictionary of required information for training input
# and associated prompt logic
# input_dict = {
#     'dataset': self._prompt_dataset(),
# }

# # iterate over required kwargs and prompt if any are not found
# for field in input_dict.keys():
#     if field not in kwargs.keys():
#         input_dict[field]()
