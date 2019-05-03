"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in ravenml.
"""

import click
import json
import shortuuid
from pathlib import Path
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from ravenml.train.interfaces import TrainInput, TrainOutput
from ravenml.utils.dataset import get_dataset_names, get_dataset
from ravenml.utils.question import cli_spinner
from ravenml.utils.save import upload_file_to_s3, upload_dict_to_s3_as_json
from ravenml.options import no_user_opt
    
### OPTIONS ###
# dataset_opt = click.option(
#     '-d', '--dataset', 'dataset', type=click.Choice(get_dataset_names()), is_eager=True,
#     help='Dataset to use for training.'
# )

dataset_opt = click.option(
    '-d', '--dataset', 'dataset', type=str, is_eager=True,
    help='Dataset to use for training.'
)

local_opt = click.option(
    '-l', '--local', 'local', type=str, is_eager=True, default='None',
    help='Keep all model artifacts local.'
)


### COMMANDS ###
@with_plugins(iter_entry_points('ravenml.plugins.train'))
@click.group()
@click.pass_context
@no_user_opt
@dataset_opt
@local_opt
def train(ctx, local, dataset):
    """ Training commands.
    """
    if ctx.obj['NO_USER']:
        # if no_user is true, make a TrainInput from the other flags
        if local == 'None': 
            local = None
        ti = TrainInput(inquire=False, 
                        dataset=cli_spinner('Retrieving dataset from s3...', get_dataset, dataset),
                        artifact_path=local)
        # assign to context for use in plugin
        ctx.obj = ti

@train.resultcallback()
@click.pass_context
def process_result(ctx, result: TrainOutput, local, dataset):
    # need to consider issues with this being called on every call to train
    if ctx.invoked_subcommand != 'list' and result is not None:
        print(json.dumps(result.metadata, indent=2))
        click.echo(result.artifact_path)
        click.echo(result.model_path)
        cli_spinner('Uploading artifacts...', _upload_result, result)
    return result

@train.command()
def list():
    """List available training plugins by name.
    """
    for entry in iter_entry_points(group='ravenml.plugins.train', name=None):
        click.echo(entry.name)

def _upload_result(result: TrainOutput):
    """ Wraps upload procure into single function for use with cli_spinner.

    Generates a UUID for the model and uploads all artifacts.

    Args:
        result (TrainOutput): TrainOutput object to be uploaded
    """
    shortuuid.set_alphabet('23456789abcdefghijkmnopqrstuvwxyz')
    uuid = shortuuid.uuid()
    model_name = f'{result.metadata['architecture']}_{uuid}.pb'
    upload_file_to_s3('models', result.model_path, alternate_name=model_name)
    upload_dict_to_s3_as_json(f'models/metadata_{uuid}', result.metadata)
    if result.extra_files != []:
        for fp in result.extra_files:
            upload_file_to_s3(f'extras/{uuid}', fp)

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
