'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in raven.
'''

import click
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from raven.train.interfaces import TrainInput, TrainOutput

# placerholder: will eventually hit AWS to find available datasets
def get_datasets():
    return ['a', 'b', 'c']
    
    
### OPTIONS ###
def no_user_callback(ctx, param, value):
    # set in context
    ctx.obj = {}
    ctx.obj['NO_USER'] = value
    # if we are in no_user mode, check all required arguments are there
    if value:
        for arg, value in ctx.params.items():
            if value is None:
                ctx.exit('You must supply the --%s argument when using --no-user!'%arg)
    
no_user_opt = click.option(
    '--no-user', is_flag=True, callback=no_user_callback, expose_value=False,
    help='Disable Inquirer prompts and use flags instead.'
)

# these commands must be eager so their values are available in the no_user_opt callback
dataset_opt = click.option(
    '-d', '--dataset', 'dataset', type=click.Choice(get_datasets()), is_eager=True,
    help='Dataset to use for training.'
)

local_opt = click.option(
    '-l', '--local', 'local', type=str, is_eager=True, default='None',
    help='Keep all model artifacts local.'
)


### COMMANDS ###
@with_plugins(iter_entry_points('raven.plugins.train'))
@click.group()
@click.pass_context
@no_user_opt
@dataset_opt
@local_opt
def train(ctx, local, dataset):
    '''
    Training commands.
    '''
    if ctx.obj['NO_USER']:
        # if no_user is true, make a TrainInput from the other flags
        if local == 'None': 
            local = None
        ti = TrainInput(inquire=False, dataset=dataset, artifact_path=local)
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
    '''
    List available training plugins by name.
    '''
    for entry in iter_entry_points(group='raven.plugins.train', name=None):
        print(entry.name)
