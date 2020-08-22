"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/03/2019

Contains the classes for interfacing with training command group.
"""
import os
import click
import shutil
from datetime import datetime
from pathlib import Path
from colorama import Fore
from ravenml.utils.local_cache import RMLCache
from ravenml.utils.question import cli_spinner, user_input, user_selects, user_confirms
from ravenml.utils.dataset import get_dataset_names, get_dataset
from ravenml.data.interfaces import Dataset

class TrainInput(object):
    """Represents a training input. Contains all plugin-independent information
    necessary for training. Plugins can define their own behavior for getting
    additional information.

    Args:
        config (dict): training config dict
        plugin_name (str): name of the plugin that will use this TrainInput.
            Train command (commands.py) sets gives the exact plugin command (i.e, tf-bbox, etc)

    Attributes:
        config (dict): full training config dict as loaded from config yaml file
        plugin_cache (RMLCache): RMLCache for this plugin. Created at 
            ~/.ravenML/<plugin_name>
        artifact_path (Path): path to save artifacts. Points to temp/ inside
            the root of plugin_cache if uploading to S3, otherwise points
            to user defined local path.
        dataset (Dataset): Dataset object for this training run.
        metadata (dict): dictionary of metadata about this training.
            Automatically populated with common data, plugins add more as needed.
        plugin_metadata (dict): dictionary within full metadata dict where plugins
            place their specific metadata. Plugins should never assign to this
            attribute as it will break the relationship between plugin_metadata and metadata.
        plugin_config (dict): plugin section of config dict. Plugins look here
            for plugin-specific configuration.
    """
    def __init__(self, config:dict=None, plugin_name:str=None):
        """ Keyword args must be used for this class to work with the @pass_train pass decorator.
        That decorator is defined in options.py. It is applied to commands to ensure that a 
        TrainInput object exists in the click Context at ctx.obj. Click pass decorators 
        do this by creating an object with no constructor arguments at ctx.obj if one does
        not already exist.

        Therefore, this constructor is ONLY called with no args when a command decorated with 
        @pass_train is triggered and no TrainInput exists yet at ctx.obj. This behavior is used
        to know when the user has called a plugin training command but did not provide a config 
        filepath via --config.
        
        The train command defined at commands.py will ONLY create a TrainInput at ctx.obj
        if --config was used. This prevents undesired creation of TrainInput objects during
        execution non-training plugin commands, as click always executes the code in the train
        command on its way down the chain to the plugin command itself.
        
        tl:dr: if this constructor is called without keyword args set, we know a user
        has called a plugin's train command without providing a config, so we fail.
        """
        if config is None or plugin_name is None:
            raise click.exceptions.UsageError(('You must provide the --config option '
                'on `ravenml train` when using this plugin command.'))

        ## Store config
        self.config = config
        
        ## Set up Local Cache
        # TODO: maybe create the subdir here?
        # currently the cache_name subdir is only created IF the plugin places files there
        self.plugin_cache = RMLCache(f'train_{plugin_name}')
        
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
        
        ## Set up fields for plugin use
        # NOTE: plugins should overwrite the architecture field to something
        # more specific/useful since it is used to name the final uploaded model
        self.metadata[plugin_name] = {'architecture': plugin_name}
        # plugins should only ACCESS the plugin_metadata attibute and add items. They should
        # NEVER assign to the attribute as it will break the reference to the overall metadata dict
        self.plugin_metadata = self.metadata[plugin_name]
        if not config.get('plugin'):
            raise click.exceptions.BadParameter(config, param=config, param_hint='config, no "plugin" field. Config was')
        else:
            self.plugin_config = config.get('plugin') 
            
class TrainOutput(object):
    """Represents a training output. Plugin training command functions return this object
    so it can be processed by the `process_result` callback registed on the train command.
    This callback handles killing EC2 instances and uploading the trained model to S3.
    
    Note this object does not contain the metadata associated with the training run,
    although that is technically an output. This is because metadata is created 
    and populated with common data in the TrainInput __init__ that runs prior to training.
    The TrainInput object for the training is still at ctx.obj when training completes
    and can be accessed by the process_result callback, therefore metadata is
    not passed back via TrainOutput. Instead plugins directly modify the metadata
    in the TrainInput object during training, and it is then accessed for upload at the end.

    Args:
        model_path (Path): path to final exported model
        extra_files (list): list of Path objects to extra files associated with the training
            These are uploaded under the "extras" prefix in the models S3 bucket.
            They are tied to the final model via a unique UUID attached to each model at upload,
            Ex: model is uploaded with UUID "12345" at "models/12345.pb".
            Extras are then at: "extras/12345.pb"
            See _upload_result in commands.py for more details

    Attributes:
        model_path (Path): path to final exported model
        extra_files (list): list of Path objects to extra files associated with the training
    """
    def __init__(self, model_path: Path, extra_files: list):
        self.model_path = model_path
        self.extra_files = extra_files
    
