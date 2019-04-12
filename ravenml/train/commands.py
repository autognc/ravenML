"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in ravenml.
"""

import click
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from ravenml.train.interfaces import TrainInput, TrainOutput
from ravenml.utils.dataset import get_dataset_names, get_dataset
from ravenml.utils.question import cli_spinner
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
    """
    Training commands.
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
    if ctx.invoked_subcommand != 'list':
        click.echo('Upload model artifacts here.')
    return result

@train.command()
def list():
    """
    List available training plugins by name.
    """
    for entry in iter_entry_points(group='ravenml.plugins.train', name=None):
        click.echo(entry.name)
