"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/10/2019

Command group for dataset exploration in ravenml.
"""

import pydoc
import click
from colorama import init, Fore
from halo import Halo
from ravenml.utils.dataset import get_dataset_names, get_dataset_metadata
from ravenml.utils.question import cli_spinner

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
    """Dataset exploration commands.
    
    Args:
        ctx (Context): click context object
    """
    pass

@data.resultcallback()
@click.pass_context
def process_result(ctx, result):
    pass

@data.command()
@detailed_opt
def list(detailed: bool):
    """List available datasets.
    
    Args:
        detailed: T/F show detailed view
    """
    dataset_names = cli_spinner("Finding datasets on S3...", get_dataset_names)

    if detailed:
        detailed_info = cli_spinner("Downloading dataset metadata from S3...", _get_detailed_dataset_info, dataset_names)
        pydoc.pager(detailed_info)      
        return
        
    for name in dataset_names:
        click.echo(name)

@data.command()
@click.argument('dataset_name')
def inspect(dataset_name: str):
    """See detailed information about a dataset.

    Args:
        dataset_name: string name of the dataset to inspect
    """
    metadata = cli_spinner("Downloading dataset metadata from S3...", get_dataset_metadata, dataset_name)
    click.echo(_stringify_metadata(metadata, colored=True))


### HELPERS ###
def _stringify_metadata(metadata, colored=False):
    """Turn metadata into a nicely formatted string for displaying.

    Args:
        metadata: dictionary of metadata
        colored: whether to colorize string, default False

    Returns:
        str: formatted metadata string
    """
    result = ''
    for key, val in metadata.items():
        if key not in EXCLUDED_METADATA:
            if colored:
                result += Fore.GREEN + str(key).upper() + ' ' + Fore.WHITE + str(val) + '\n'
            else:
                result += str(key).upper() + ' ' + str(val) + '\n'
    return result

def _get_detailed_dataset_info(datasets):
    """Stringifies and concatenates metadata for a list of datasets.

    Args:
        datasets: list of dataset names

    Returns:
        str: concatenated and delimited metadata string for each dataset.
    """
    result = ''
    for dataset in datasets:
        metadata = get_dataset_metadata(dataset)
        result += _stringify_metadata(metadata)
        result += '----------' '\n'
    return result
