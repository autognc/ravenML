'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/10/2019

Command group for dataset exploration in raven.
'''

import click
import pydoc
from colorama import init, Fore
from halo import Halo
from raven.utils.dataset import get_dataset_names, get_dataset_metadata

init()

EXCLUDED_METADATA = ['filters', 'transforms', 'image_ids']

### OPTIONS ###
detailed_opt = click.option(
    '-d', '--detailed', 'detailed', is_flag=True,
    help='Get detailed information about datasets.'
)


### COMMANDS ###
@click.group()
@click.pass_context
def data(ctx):
    ''' Dataset exploration commands.
    '''
    pass

@data.resultcallback()
@click.pass_context
def process_result(ctx, result):
    pass

@data.command()
@detailed_opt
def list(detailed):
    ''' List available datasets.
    '''
    spinner = Halo(text="Finding datasets on S3...", text_color="magenta")
    spinner.start()
    dataset_names = get_dataset_names()
    spinner.succeed(text=spinner.text + "Complete.")
    
    if not detailed:
        for d in dataset_names:
            click.echo(d)
        return
    else:
        spinner = Halo(text="Downloading dataset metadata from S3...", text_color="magenta")
        spinner.start()
        detailed_info = _get_detailed_dataset_info(dataset_names)
        spinner.succeed(text=spinner.text + "Complete.")
        pydoc.pager(detailed_info)        
        
@data.command()
@click.argument('dataset_name')
def inspect(dataset_name):
    ''' See detailed information about a dataset.
    
    Args:
        dataset_name: string name of the dataset to inspect
    '''
    spinner = Halo(text="Downloading dataset metadata from S3...", text_color="magenta")
    spinner.start()
    metadata = get_dataset_metadata(dataset_name)
    spinner.succeed(text=spinner.text + 'Complete.')
    click.echo(_stringify_metadata(metadata, colored=True))


### HELPERS ###
def _stringify_metadata(metadata, colored=False):
    ''' Turn metadata into a nicely formatted string for displaying.

    Args:
        metadata: dictionary of metadata
        colored: whether to colorize string, default False
    
    Returns:
        str: formatted metadata string
    '''
    result = ''
    for key, val in metadata.items():
        if key not in EXCLUDED_METADATA:
            if colored:
                result += Fore.GREEN + str(key).upper() + ' ' + Fore.WHITE + str(val) + '\n'
            else:
                result += str(key).upper() + ' ' + str(val) + '\n'
    return result

def _get_detailed_dataset_info(datasets):
    ''' Stringifies and concatenates metadata for a list of datasets.

    Args:
        datasets: list of dataset names
    
    Returns:
        str: concatenated and delimited metadata string for each dataset.
    '''
    result = ''
    for d in datasets:
        metadata = get_dataset_metadata(d)
        result += _stringify_metadata(metadata)
        result += '----------' '\n'
    return result
