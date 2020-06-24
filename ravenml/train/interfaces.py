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

    Args:
        config (dict): training config dict
        cache_name (str): name of subcache inside ravenML cache to use.
            Should be the name of the plugin command (i.e, tf-bbox, etc)

    Attributes:
        plugin_cache (RMLCache): RMLCache for this plugin. Created at 
            ~/.ravenML/<plugin command>.
        artifact_path (Path): path to save artifacts. Points to temp/ inside
            the root of plugin_cache if uploading to S3, otherwise points
            to user defined local path.
        dataset (Dataset): Dataset object for this training run.
        metadata (dict): dictionary of metadata about this training.
            Automatically populated with common data, plugins add more.
        config (dict): full training config dict 
        plugin_config (dict): plugin section of config dict for plugin to use
    """
    def __init__(self, config:dict=None, cache_name:str=None):
        """ Default args given for use with @pass_train pass decorator.
        Constructor is called with no args when a command decorated with @pass_train is
        triggered and no TrainInput exists in ctx.obj. This occurs when the user
        did not provide a config in the --config option.
        """
        if config is None or cache_name is None:
            raise click.exceptions.UsageError(('You must provide the --config option'
                'on `ravenml train` when using this plugin command.'))

        ## Set up Local Cache
        # TODO: maybe create the subdir here?
        self.plugin_cache = RMLCache(cache_name)
        
        ## Set up Artifact Path
        ap = config.get('artifact_path')
        if ap is None:
            self.plugin_cache.ensure_clean_subpath('temp')
            self.plugin_cache.ensure_subpath_exists('temp')
            self.artifact_path = Path(self.plugin_cache.path / 'temp')
        else:
            ap = Path(os.path.expanduser(ap))
            # check if local path contains data
            if os.path.exists(ap) and os.path.isdir(ap) and len(os.listdir(ap)) > 0:
                if config.get('overwrite_local') or user_confirms('Local artifact storage location contains old data. Overwrite?'):
                    shutil.rmtree(ap)
                else:
                    click.echo(Fore.RED + 'Training cancelled.')
                    click.get_current_context().exit() 
            # create directory, need exist_ok since we only delete
            # if directory contains files
            # TODO: protect against paths to actual files
            os.makedirs(ap, exist_ok=True)
            self.artifact_path = ap
        
        ## Set up Dataset
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
    
        ## Set up Basic Metadata
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
        # set up plugin metadata area
        self.metadata[cache_name] = {}
        
        # provide config to plugin
        self.config = config
        self.plugin_config = config.get('plugin')
        self.plugin_metadata_field = cache_name
            
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
    