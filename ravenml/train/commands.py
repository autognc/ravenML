"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in ravenml.
"""

import click
import json
import shortuuid
import os
import boto3
import yaml
import sys
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from ravenml.train.interfaces import TrainInput, TrainOutput
from ravenml.train.options import pass_train
from ravenml.utils.dataset import get_dataset
from ravenml.utils.question import cli_spinner
from ravenml.utils.aws import upload_file_to_s3, upload_dict_to_s3_as_json
from ravenml.options import no_user_opt

EC2_INSTANCE_ID_URL = 'http://169.254.169.254/latest/meta-data/instance-id'

### OPTIONS ###
dataset_opt = click.option(
    '-d', '--dataset', 'dataset', type=str,
    help='Name of dataset on S3 for training.'
)

local_opt = click.option(
    '-l', '--local', 'local', type=str,
    help='Do not upload to S3 and instead save artifacts to the provided filepath.'
)

overwrite_local_opt = click.option(
    '-o', '--overwrite', is_flag=True,
    help='Overwrite existing files at artifact path in --local without prompting.'
)

ec2_kill_opt = click.option(
    '--no-kill', 'no_kill', is_flag=True,
    help='Do not kill EC2 instance ravenML is running on after training. Ignored if not on EC2.'
)

config_opt = click.option(
    '-c', '--config', type=str, help='Path to config file. Defaults to ~/ravenML_configs/config.yaml'
)

### COMMANDS ###
@with_plugins(iter_entry_points('ravenml.plugins.train'))
@click.group(help='Training commands.')
@click.pass_context
# @ec2_kill_opt
# @dataset_opt
# @overwrite_local_opt
# @local_opt
@config_opt
# def train(ctx: click.Context, local: str, overwrite: bool, dataset: str, no_kill: bool):
def train(ctx: click.Context, config: str):
    """ Training command group.
    
    Args:
        ctx (Context): click context object
        local (str): local filepath. defaults to 'None' and only used if in no-user mode
        dataset (str): dataset name. None if not in no-user mode
        no_kill (bool): whether to kill EC2 instance after training
    """
    ## NOTE: ##
    # All plugins require a TrainInput object to begin training. ravenML 
    # guarantees this in two ways for two different cases:
    #   1.  User did NOT provide any arguments to this command and thus 
    #       must be prompted for dataset name. TrainInput object is created 
    #       automatically by pass_train decorator in plugin since it does not need to
    #       receive any information from this command. Therefore, NO action is taken
    #       so that this command does not do anything for calls to other plugin 
    #       subcommands such as help.
    #   2.  User DID provide arguments to this command and thus is kicking off
    #       a training, therefore NOT calling any other plugin subcommand. This means
    #       it is ok (and necessary) to create a TrainInput in this command, as we know
    #       for sure which plugin subcommand is coming next.o
    if config:
        try:
            with open(Path(config), 'r') as stream:
                config = yaml.safe_load(stream)
        except Exception as e:
            hint = 'config, no such file exists'
            raise click.exceptions.BadParameter(config, ctx=ctx, param=config, param_hint=hint)

        ctx.obj = TrainInput(config, ctx.invoked_subcommand)

    # if dataset or local:
    #     try:
    #         ti = TrainInput(dataset_name=dataset, artifact_path=local, 
    #             overwrite=overwrite, cache_name=ctx.invoked_subcommand)
    #         # assign to context for use in plugin
    #         ctx.obj = ti
    #     except ValueError as e:
    #         hint = 'dataset name, no such dataset exists on S3:'
    #         raise click.exceptions.BadParameter(dataset, ctx=ctx, param=dataset, param_hint=hint)

@train.resultcallback()
@pass_train
@click.pass_context
# def process_result(ctx: click.Context, result: TrainOutput, local: str, overwrite: bool, dataset: str,  no_kill: bool):
def process_result(ctx: click.Context, ti: TrainInput, result: TrainOutput, config: str):
    """Processes the result of a training by analyzing the given TrainOutput object.
    This callback is called after ANY command originating from the train command 
    group, hence the check for commands other than training plugins.

    Args:
        ctx (Context): click context object
        result (TrainOutput): training output object returned by training plugin
        local (str): copy of local option provided to original command (see train)
        dataset (str): copy of dataset option provided to original comamand (see train)
    """
    # need to consider issues with this being called on every call to train
    if result is not None:
        # upload if not in local mode, determined by presence of artifact_path field in config
        if not ti.config.get('artifact_path'):
            uuid = cli_spinner('Uploading artifacts...', _upload_result, result)
            click.echo(f'Artifact UUID: {uuid}')
        else:
            click.echo(f'LOCAL MODE: Not uploading model to S3. Model is located at: {result.artifact_path}')
            
        # kill if on ec2
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
def _upload_result(result: TrainOutput):
    """ Wraps upload procedure into single function for use with cli_spinner.

    Generates a UUID for the model and uploads all artifacts.

    Args:
        result (TrainOutput): TrainOutput object to be uploaded
    
    Returns:
        str: uuid assigned to result on upload
    """
    shortuuid.set_alphabet('23456789abcdefghijkmnopqrstuvwxyz')
    uuid = shortuuid.uuid()
    model_name = f'{result.metadata["architecture"]}_{uuid}.pb'
    upload_file_to_s3('models', result.model_path, alternate_name=model_name)
    upload_dict_to_s3_as_json(f'models/metadata_{uuid}', result.metadata)
    if result.extra_files != []:
        for fp in result.extra_files:
            upload_file_to_s3(f'extras/{uuid}', fp)
    return uuid

# @train.command()
# def testup():
#     metadata = {
#         "created_by": "carosn",
#         "comments": "no",
#         "date_started_at": "2019-05-03T01:33:50.694751Z",
#         "dataset_used": {
#             "name": "carsonTest",
#             "date_created": "2019-03-18T22:38:59.794095Z",
#             "created_by": "Carson Schubert",
#             "comments": "initial test",
#             "training_type": "Bounding Box",
#             "image_ids": [
#             "pic_204",
#             "pic_701",
#             "pic_268",
#             "pic_594",
#             "pic_634",
#             "pic_674",
#             "pic_310",
#             "pic_236",
#             "pic_270"
#             ],
#             "filters": {
#             "groups": []
#             },
#             "transforms": []
#         },
#         "architecture": "ssd_mobilenet_v1_coco",
#         "hyperparemeters": {
#             "optimizer": "RMSProp",
#             "num_classes": 2,
#             "use_dropout": True,
#             "dropout_keep_probability": 0.8,
#             "initial_learning_rate": 0.004
#         },
#         "date_completed_at": "2019-05-03T01:35:01.441570Z"
#     }
#     base = Path('/home/carson/.ravenML/tf-bbox/temp')
#     model = base / Path('models') / Path('model') / Path('export') \
#                     / Path ('exported_model') / '1556847298' / 'saved_model.pb'        
#     result = TrainOutput(metadata, base, model, [])
#     cli_spinner('Uploading artifacts...', _upload_result, result)
