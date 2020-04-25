"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/10/2019

Command group for dataset exploration in ravenml.
"""

import pydoc
import click
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from colorama import init, Fore
from ravenml.utils.imageset import get_imageset_names, get_imageset_metadata
from ravenml.utils.dataset import get_dataset_names, get_dataset_metadata
from ravenml.utils.question import cli_spinner

init()

EXCLUDED_METADATA = ['filters', 'transforms', 'image_ids']

### OPTIONS ###
detailed_opt = click.option(
    '-d', '--detailed', 'detailed', is_flag=True,
    help='Show detailed metadata about datasets.'
)


### COMMANDS ###
@click.group(help='Data exploration and dataset creation commands.')
@click.pass_context
def data(ctx):
    """Data exploration and dataset creation command group.
    
    Args:
        ctx (Context): click context object
    """
    pass

# TODO: eventually this will handle uploading/deleting the created
# dataset given by a plugin, see train.commands.process_result for example
@data.resultcallback()
@click.pass_context
def process_result(ctx: click.Context, result):
    pass

# TODO: determine interfaces for this command
@with_plugins(iter_entry_points('ravenml.plugins.data'))
@data.group(help='Create a new dataset.')
def create():
    click.echo("Eventually this will create datasets for you.")

## Imageset Commands ##
@data.command(help="List available image sets.")
def list_imagesets():
    """List available image sets on S3.
    """
    imageset_names = cli_spinner("Finding image sets on S3...", get_imageset_names)
    for name in imageset_names:
        click.echo(name)

@data.command(help='See detailed metadata about an image set.')
@click.argument('imageset_name')
def inspect_imageset(imageset_name: str):
    """See detailed metadata about a dataset.

    Args:
        dataset_name (str): string name of the dataset to inspect
    """
    try:
        metadata = cli_spinner("Downloading imageset metadata from S3...", get_imageset_metadata, imageset_name)
        if 'pose' in metadata.keys():
            click.echo(Fore.RED + ('Set-wide metadata not found. '
                                    'Falling back to sample image metadata.'))
        click.echo(_stringify_metadata(metadata, colored=True))
    # get_imageset_metadata will raise a value error imageset name not found
    except ValueError as e:
        raise click.exceptions.BadParameter(imageset_name, param=imageset_name, param_hint='imageset name')

## Dataset commands ##
@data.command(help='List available datasets.')
@detailed_opt
def list_datasets(detailed: bool):
    """List available datasets.
    
    Args:
        detailed (bool): T/F show detailed view
    """
    dataset_names = cli_spinner("Finding datasets on S3...", get_dataset_names)

    if detailed:
        detailed_info = cli_spinner("Downloading dataset metadata from S3...", _get_detailed_dataset_info, dataset_names)
        pydoc.pager(detailed_info)      
        return
        
    for name in dataset_names:
        click.echo(name)

@data.command(help='See detailed metadata about a dataset.')
@click.argument('dataset_name')
def inspect_dataset(dataset_name: str):
    """See detailed metadata about a dataset.

    Args:
        dataset_name (str): string name of the dataset to inspect
    """
    try:
        metadata = cli_spinner("Downloading dataset metadata from S3...", get_dataset_metadata, dataset_name)
        click.echo(_stringify_metadata(metadata, colored=True))
    # get_dataset_metadata will raise a value error if the given dataset name
    # cannot be found
    except ValueError as e:
        raise click.exceptions.BadParameter(dataset_name, param=dataset_name, param_hint='dataset name')
        

### HELPERS ###
def _stringify_metadata(metadata: dict, colored=False) -> str:
    """Turn metadata into a nicely formatted string for displaying.

    Args:
        metadata (dict): dictionary of metadata
        colored (bool, optional): whether to colorize string, default False

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

def _get_detailed_dataset_info(datasets: list) -> str:
    """Stringifies and concatenates metadata for a list of datasets.

    Args:
        datasets (list): list of dataset names

    Returns:
        str: concatenated and delimited metadata string for each dataset.
    """
    result = ''
    for dataset in datasets:
        metadata = get_dataset_metadata(dataset)
        result += _stringify_metadata(metadata)
        result += '----------' '\n'
    return result
