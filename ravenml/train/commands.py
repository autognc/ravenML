"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in ravenml.
"""

import click
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from ravenml.train.interfaces import TrainInput, TrainOutput
from ravenml.utils.dataset import get_dataset
from ravenml.utils.question import cli_spinner
from ravenml.options import no_user_opt

### OPTIONS ###
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
@click.group(help='Training commands.')
@click.pass_context
@no_user_opt
@dataset_opt
@local_opt
def train(ctx: click.Context, local: str, dataset: str):
    """ Training command group.
    
    Args:
        ctx (Context): click context object
        local (str): local filepath. defaults to 'None' and only used if in no-user mode
        dataset (str): dataset name. None if not in no-user mode
    """
    if ctx.obj['NO_USER']:
        # if no_user is true, make a TrainInput from the other flags
        try:
            dataset_obj = cli_spinner('Retrieving dataset from s3...', get_dataset, dataset)
            if local == 'None': 
                local = None
            ti = TrainInput(inquire=False, dataset= dataset_obj, artifact_path=local)
            # assign to context for use in plugin
            ctx.obj = ti
        except ValueError as e:
            raise click.exceptions.BadParameter(dataset, ctx=ctx, param=dataset, param_hint='dataset name')

@train.resultcallback()
@click.pass_context
def process_result(ctx: click.Context, result: TrainOutput, local: str, dataset: str):
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
    print(result)
    if ctx.invoked_subcommand != 'list':
        click.echo('Upload model artifacts here.')
    return result

@train.command()
def list():
    """List available training plugins by name.
    """
    for entry in iter_entry_points(group='ravenml.plugins.train', name=None):
        click.echo(entry.name)
