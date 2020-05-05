"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/03/2019

Contains the classes for interfacing with training command group.
"""
import os
import sys
import click
import shutil
from datetime import datetime
from pathlib import Path
from colorama import init, Fore
from ravenml.utils.local_cache import RMLCache
from ravenml.utils.question import cli_spinner, user_input, user_selects, user_confirms
from ravenml.utils.dataset import get_dataset_names, get_dataset
from ravenml.data.interfaces import Dataset
from schema import Schema, Optional, And, Use

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
        plugin_cache (RMLCache): RMLCache for this plugin. Created at 
            ~/.ravenML/<plugin command>.
        config (dict)
    """
    
   
    def __init__(self):
        """ Default constructor for use with @pass_train pass decorator
        Automatically called when a command decorated with @pass_train is
        triggered and not TrainInput exists in ctx.obj. This means the user
        did not provide a config in the --config option.
        """
        raise click.exceptions.UsageError(('You must provide the --config option'
            'on `ravenml train` when using this plugin command.'))

    def __init__(self, config: dict, cache_name:str):
        ## Set up Local Cache ##
        self.plugin_cache = RMLCache(cache_name)
        
        ## Set up Artifact Path
        ap = config.get('artifact_path')
        if ap is None:
            self.plugin_cache.ensure_clean_subpath('temp')
            self.plugin_cache.ensure_subpath_exists('temp')
            self.artifact_path = Path(self.plugin_cache.path / 'temp')
        else:
            ap = Path(artifact_path)
            # check if local path contains data
            if os.path.exists() and os.path.isdir(ap) and len(os.listdir(ap)) > 0:
                if config.get('overwrite_local') or user_confirms('Local artifact storage location contains old data. Overwrite?'):
                    shutil.rmtree(ap)
                else:
                    click.echo(Fore.RED + 'Training cancelled.')
                    click.get_current_context().exit() 
            # create directory, need exist_ok since we only delete
            # if directory contains files
            os.makedirs(ap, exist_ok=True)
            self.artifact_path = ap
        
        ## Set up Dataset ##
        # prompt for dataset if not provided
        dataset_name = config.get('dataset')
        if dataset_name is None:
            dataset_options = cli_spinner('No dataset provided. Finding datasets on S3...', get_dataset_names)
            dataset_name = user_selects('Choose dataset:', dataset_options)
        # download dataset and populate field
        try:
            self.dataset = cli_spinner(f'Downloading {dataset_name} from S3...', 
                get_dataset, dataset_name)
        except ValueError as e:
            hint = 'dataset name, no such dataset exists on S3'
            raise click.exceptions.BadParameter(dataset_name, param=dataset_name, param_hint=hint)
    
        ## Set up Basic Metadata ##
        # TODO: add environment description, git hash, etc
        self.metadata = config.get('metadata', {})
        # handle user defined metadata fields
        if not self.metadata.get('created_by'):
            self.metadata['created_by'] = user_input('Please enter your first and last name:')
        if not self.metadata.get('comments'):
            self.metadata['comments'] = user_input('Please enter descriptive comments about this training:')
        
        # handle automatic metadata fields
        self.metadata['date_started_at'] = datetime.utcnow().isoformat() + "Z"
        self.metadata['dataset_used'] = self.dataset.metadata
            
    
    ## NOTE: ##
    # Constructor uses only kwargs to make it compatible for use with
    # a Click pass decorator with ensure=True, which requires a default 
    # constructor with no positional arguments. 
    # The pass decorator with ensure=True is what allows 
    # creation of a TrainInput directly in the ravenml train command
    # ONLY when arguments are passed, which allows --help and other plugin
    # subcommands to be unaffected by TrainInput construction when a training
    # is not actually being started.
    # def __init__(self, dataset_name=None, artifact_path=None, overwrite=False, cache_name=None):
    #     ## Set up Local Cache ##
    #     # cache name is None when __init__ called by pass decorator, so get plugin name via context
    #     if cache_name is None:
    #         self.plugin_cache = RMLCache(click.get_current_context().command_path.split(' ')[2]) 
    #     else:
    #         self.plugin_cache = RMLCache(cache_name)
        
    #     ## Set up Artifact Path ##
    #     # path is None for s3 upload (no local flag passed)
    #     if artifact_path is None:
    #         # clear temp dir in case already exists
    #         self.plugin_cache.ensure_clean_subpath('temp')
    #         # create temp dir in local cache for artifacts
    #         self.plugin_cache.ensure_subpath_exists('temp')
    #         self.artifact_path = Path(self.plugin_cache.path / 'temp')
    #     else:
    #         # convert to Path object
    #         ap = Path(artifact_path)
    #         # check if local path contains data
    #         if os.path.exists(ap) and os.path.isdir(ap) and len(os.listdir(ap)) > 0:
    #             if overwrite or user_confirms('Artifact storage location contains old data. Overwrite?'):
    #                 shutil.rmtree(ap)
    #             else:
    #                 click.echo(Fore.RED + 'Training cancelled.')
    #                 click.get_current_context().exit() 
    #         # create directory, need exist_ok since we only delete
    #         # if the directory contains files
    #         os.makedirs(ap, exist_ok=True)
    #         self.artifact_path = ap
            
    #     ## Set up Dataset ##
    #     # prompt for dataset if not provided
    #     if dataset_name is None:
    #         dataset_options = cli_spinner('Finding datasets on S3...', get_dataset_names)
    #         dataset_name = user_selects('Choose dataset:', dataset_options)
    #     # download dataset and populate field
    #     self.dataset = cli_spinner(f'Downloading {dataset_name} from S3...', 
    #         get_dataset, dataset_name)

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
    def __init__(self, metadata: dict, artifact_path: Path, model_path: Path, extra_files: list):
        self.metadata = metadata
        self.artifact_path = artifact_path
        self.model_path = model_path
        self.extra_files = extra_files
    
# dictionary of required information for training input
# and associated prompt logic
# input_dict = {
#     'dataset': self._prompt_dataset(),
# }

# # iterate over required kwargs and prompt if any are not found
# for field in input_dict.keys():
#     if field not in kwargs.keys():
#         input_dict[field]()
