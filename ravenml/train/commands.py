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
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from ravenml.train.interfaces import TrainInput, TrainOutput
from ravenml.train.options import pass_train
from ravenml.utils.question import cli_spinner
from ravenml.utils.aws import upload_file_to_s3, upload_dict_to_s3_as_json

EC2_INSTANCE_ID_URL = 'http://169.254.169.254/latest/meta-data/instance-id'

### OPTIONS ###
config_opt = click.option(
    '-c', '--config', type=str, help='Path to config file. Defaults to ~/ravenML_configs/config.yaml'
)

### COMMANDS ###
@with_plugins(iter_entry_points('ravenml.plugins.train'))
@click.group(help='Training commands.')
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
        try:
            with open(Path(config), 'r') as stream:
                train_config = yaml.safe_load(stream)
        except Exception as e:
            hint = 'config, no such file exists'
            raise click.exceptions.BadParameter(config, ctx=ctx, param=config, param_hint=hint)
        # trigger TrainInput creation, note this may prompt the user depending on the config file used
        ctx.obj = TrainInput(train_config, ctx.invoked_subcommand)

@train.resultcallback()
@pass_train
@click.pass_context
def process_result(ctx: click.Context, ti: TrainInput, result: TrainOutput, config: str):
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
        # upload if not in local mode, determined by user defined artifact_path field in config
        if not ti.config.get('artifact_path'):
            uuid = cli_spinner('Uploading artifacts...', _upload_result, result, ti.metadata)
            click.echo(f'Artifact UUID: {uuid}')
        else:
            print(ti.metadata)
            click.echo(f'LOCAL MODE: Not uploading model to S3. Model is located at: {ti.artifact_path}')
            
        # kill if on ec2 unless user has explicitly said not to
        # NOTE: users may run in local mode on EC2. Do not fall into the trap of trying
        # to use the artifact_path field in the config to determine if running on EC2 or not.
        if not ti.config.get('ec2_no_kill'):
            click.echo('Checking for EC2 instance...')
            try:
                with urlopen(EC2_INSTANCE_ID_URL, timeout=5) as url:
                    ec2_instance_id = url.read().decode('utf-8')
                click.echo(f'EC2 Runtime detected.')
                client = boto3.client('ec2')
                client.terminate_instances(InstanceIds=[ec2_instance_id], DryRun=False)
            except URLError:
                click.echo('No EC2 runtime detected.')
        else:
            click.echo('Not checking for EC2 since no-kill was set.')
    return result


### HELPERS ###
def _upload_result(result: TrainOutput, metadata: dict):
    """ Wraps upload procedure into single function for use with cli_spinner.

    Generates a UUID for the model and uploads all artifacts.

    Args:
        result (TrainOutput): TrainOutput object, to be uploaded
        metadata (dict): metadata associated with this run, to be uploaded
    
    Returns:
        str: uuid assigned to result on upload
    """
    shortuuid.set_alphabet('23456789abcdefghijkmnopqrstuvwxyz')
    uuid = shortuuid.uuid()
    model_name = f'{metadata["architecture"]}_{uuid}.pb'
    upload_file_to_s3('models', result.model_path, alternate_name=model_name)
    upload_dict_to_s3_as_json(f'models/metadata_{uuid}', metadata)
    if result.extra_files != []:
        for fp in result.extra_files:
            upload_file_to_s3(f'extras/{uuid}', fp)
    return uuid
