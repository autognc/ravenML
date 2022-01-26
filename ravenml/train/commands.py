"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in ravenml.
"""

import click
import json
import shortuuid
import boto3
import yaml
import os
import inspect
import ravenml.utils.git as git
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path
from ravenml.train.interfaces import TrainInput, TrainOutput
from ravenml.utils.question import cli_spinner
from ravenml.utils.aws import upload_file_to_s3, upload_dict_to_s3_as_json
from ravenml.utils.plugins import LazyPluginGroup
from ravenml.utils.config import load_yaml_config

EC2_INSTANCE_ID_URL = 'http://169.254.169.254/latest/meta-data/instance-id'

### OPTIONS ###
config_opt = click.option(
    '-c', '--config', type=str, help='Path to config file. Defaults to ~/ravenML_configs/config.yaml'
)

### COMMANDS ###
@click.group(cls=LazyPluginGroup, entry_point_name='ravenml.plugins.train', help='Training commands.')
@click.pass_context
@config_opt
def train(ctx: click.Context, config: str):
    """ Training command group.
    
    Args:
        ctx (Context): click context object
        config (str): Path to config yaml file for this training run. Required
            when a user is calling a plugin command decorated with @pass_train
    """
    # check if config flag was passed, if not simply carry on to child command
    if config:
        # attempt to load config
        # NOTE: this function will raise a click error if there is an issue loading config
        train_config = load_yaml_config(Path(config))
        # trigger TrainInput creation, note this may prompt the user depending on the config file used
        ctx.obj = TrainInput(train_config, ctx.invoked_subcommand)

@train.resultcallback()
@click.pass_context
def process_result(ctx: click.Context, result: TrainOutput, config: str):
    """Processes the result of a training by analyzing the given TrainOutput object.
    This callback is called after ANY command originating from the train command 
    group, hence the check to see if a result was actually returned - plugins
    simply do not return a TrainOutput from non-training commands.

    Args:
        ctx (Context): click context object
        ti (TrainInput): TrainInput object stored at ctx.obj, created at start of training.
            This object contains the metadata from the run and the path to the
            training artifacts (at ti.artifact_path) which is printed to the user
            after a local training.
        result (TrainOutput): training output object returned by training plugin
        config (str): config option from train command. Click requires that command
            callbacks accept the options from the original command.
    """
    if result is not None:
        # only plugin training commands that return a TrainOutput will activate this block
        # thus ctx.obj will always be a TrainInput object
        # NOTE: you cannot use the @pass_train decorator on process_result, otherwise on
        # non-training plugin commands, the TrainInput __init__ will be called by Click
        # when process_result runs and no TrainInput is at ctx.obj
        ti = ctx.obj    
        
        # store git info for plugin
        # NOTE: this will fail for plugins not installed via source
        plugin_repo_root = git.is_repo(result.plugin_dir)
        git_info = {}
        if plugin_repo_root:
            git_info["plugin_git_sha"] = git.git_sha(plugin_repo_root)
            # note running the patch commands in repo root will include patches for all plugins
            git_info["plugin_tracked_git_patch"] = git.git_patch_tracked(plugin_repo_root)
            git_info["plugin_untracked_git_patch"] = git.git_patch_untracked(plugin_repo_root)
        else:
            git_info = git.retrieve_from_pkg(result.plugin_dir)
        ti.metadata.update(git_info)

        # upload if not in local mode, determined by user defined artifact_path field in config
        if not ti.config.get('artifact_path'):
            uuid = cli_spinner('Uploading artifacts...', _upload_result, result, ti.metadata, ti.plugin_metadata)
            click.echo(f'Artifact UUID: {uuid}')
        else:
            with open(ti.artifact_path / 'metadata.json', 'w') as f:
                json.dump(ti.metadata, f, indent=2)
            click.echo(f'LOCAL MODE: Not uploading model to S3. Model is located at: {ti.artifact_path}')
            
        # stop, terminate, or do nothing to ec2 based on policy
        ec2_policy = ti.config.get('ec2_policy')
        # check if the policy is to stop or terminate
        if ec2_policy == None or ec2_policy == 'stop' or ec2_policy == 'terminate':
            policy_str = ec2_policy if ec2_policy else 'default'
            click.echo(f'Checking for EC2 instance and applying policy "{policy_str}"...')
            try:
                # grab ec2 id
                with urlopen(EC2_INSTANCE_ID_URL, timeout=5) as url:
                    ec2_instance_id = url.read().decode('utf-8')
                click.echo(f'EC2 Runtime detected.')
                client = boto3.client('ec2')
                # default is stop
                if ec2_policy == None or ec2_policy == 'stop':
                    click.echo("Stopping...")
                    client.stop_instances(InstanceIds=[ec2_instance_id], DryRun=False)
                else:
                    click.echo("Terminating...")
                    client.terminate_instances(InstanceIds=[ec2_instance_id], DryRun=False)
            except URLError:
                click.echo('No EC2 runtime detected. Doing nothing.')
        else:
            click.echo('Not checking for EC2 runtime since policy is to keep running.')
    return result


### HELPERS ###
def _upload_result(result: TrainOutput, metadata: dict, plugin_metadata: dict):
    """ Wraps upload procedure into single function for use with cli_spinner.

    Generates a UUID for the model and uploads all artifacts.

    Args:
        result (TrainOutput): TrainOutput object, to be uploaded
        metadata (dict): metadata associated with this run, to be uploaded
        plugin_metadata (dict): plugin metadata, used to access architecture of run
            for naming uploading model
    
    Returns:
        str: uuid assigned to result on upload
    """
    shortuuid.set_alphabet('23456789abcdefghijkmnopqrstuvwxyz')
    uuid = shortuuid.uuid()
    file_extension = os.path.splitext(result.model_path)[1]
    model_name = f'{plugin_metadata["architecture"]}_{uuid}{file_extension}'
    upload_file_to_s3('models', result.model_path, alternate_name=model_name)
    upload_dict_to_s3_as_json(f'models/metadata_{uuid}', metadata)
    if result.extra_files != []:
        for fp in result.extra_files:
            upload_file_to_s3(f'extras/{uuid}', fp)
    return uuid
