"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/10/2019

Command group for dataset exploration in ravenml.
"""

import click
import pydoc
from colorama import Fore
from ravenml.utils.imageset import get_imageset_names, get_imageset_metadata
from ravenml.utils.dataset import get_dataset_names, get_dataset_metadata
from ravenml.utils.plugins import LazyPluginGroup
from ravenml.utils.question import cli_spinner

# metedata fields to exclude when printing metadata to the user 
# these are specific to datasets at the moment
EXCLUDED_METADATA = ['filters', 'transforms', 'image_ids']

### OPTIONS ###
explore_details_opt = click.option(
    '-e', '--explore_details', 'explore_details', is_flag=True,
    help='Explore detailed metadata about all imagesets/datasets currently on S3 via a pager view.'
)

print_details_opt = click.option(
    '-p', '--print-details', 'print_details', is_flag=True,
    help='Print detailed metadata about all imagesets/datasets currently on S3 to the console.'
)

filter_details_opt = click.option(
    '-f', '--filter-details', 'filter_str', type=str,
    help=('Keyword/phrase filter for displaying detailed imageset/dataset metadata. '
            'Case sensitive and case insensitive filtering is performed.')
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
# dataset given by a plugin when create is called, see train.commands.process_result for example
@data.resultcallback()
@click.pass_context
def process_result(ctx: click.Context, result):
    pass


## Dataset Creation Commands ##
# TODO: determine interfaces for this command
@data.group(cls=LazyPluginGroup, entry_point_name='ravenml.plugins.data', help='Create a new dataset.')
def create():
    click.echo("Eventually this will create datasets for you.")


## Imageset Commands ##
@data.command(help="List available image sets.")
@filter_details_opt
@explore_details_opt
@print_details_opt
def list_imagesets(print_details: bool, explore_details: bool, filter_str: str):
    """List available image sets on S3.
    
    Args:
        print_details (bool): T/F print detailed view to console
        explore_details (bool): T/F bring up detailed view in pager
        filter_str (str): string to detailed view on. None if not provided by user.
    """
    imageset_names = cli_spinner("Finding image sets on S3...", get_imageset_names)
    
    if explore_details or print_details:
        detailed_info = cli_spinner("Downloading imageset metadata from S3...", _get_detailed_imageset_info, imageset_names, filter_str=filter_str)
        if explore_details:
            pydoc.pager(detailed_info)      
        else:
            click.echo(detailed_info)
        return
        
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
        # can check if the metadata returned is for an individual image if it has pose info
        if 'pose' in metadata.keys():
            click.echo(Fore.RED + ('Set-wide metadata not found. '
                                    'Falling back to sample image metadata.'))
        click.echo(_stringify_metadata(metadata, colored=True))
    # get_imageset_metadata will raise a value error if imageset name not found
    except ValueError as e:
        raise click.exceptions.BadParameter(imageset_name, param=imageset_name, param_hint='imageset name')
    # get imageset_metadata will raise a KeyError if the imageset does not contain any metadata files.
    except KeyError as e:
        raise click.exceptions.ClickException(f'Given imageset "{imageset_name}" does not contain any metadata files.')


## Dataset commands ##
@data.command(help='List available datasets.')
@filter_details_opt
@explore_details_opt
@print_details_opt
def list_datasets(print_details: bool, explore_details: bool, filter_str: str):
    """List available datasets.
    
    Args:
        print_details (bool): T/F print detailed view to console
        explore_details (bool): T/F bring up detailed view in pager
        filter_str (str): string to detailed view on. None if not provided by user.
    """
    dataset_names = cli_spinner("Finding datasets on S3...", get_dataset_names)

    if explore_details or print_details:
        detailed_info = cli_spinner("Downloading dataset metadata from S3...", _get_detailed_dataset_info, dataset_names, filter_str=filter_str)
        if explore_details:
            pydoc.pager(detailed_info)      
        else:
            click.echo(detailed_info)
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
    # get_dataset_metadata will raise a value error if the given dataset name does not exist on S3
    # OR if that dataset does not contain a metadata file. Currently these two situations are indistinguishible
    # TODO: separate errors for bad dataset name and dataset lacking metadata. This will need to be done in the 
    # get_dataset_metadata function
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

def _get_detailed_dataset_info(datasets: list, filter_str:str=None) -> str:
    """Stringifies and concatenates metadata for a list of datasets.

    Args:
        datasets (list): list of dataset names
        filter_str (str, optional): string to filter metadata on

    Returns:
        str: concatenated and delimited metadata string for each dataset.
    """
    result = ''
    for dataset in datasets:
        try:
            metadata = get_dataset_metadata(dataset)
            str_metadata = _stringify_metadata(metadata)
            if filter_str:
                if filter_str in str_metadata:
                    result += str_metadata
                    result += '----------' '\n'
            else:
                result += str_metadata
                result += '----------' '\n'
        # we know we are only calling get_dataset_metadata on datsets that actually exist in S3,
        # so any ValueError indicates that dataset is missing metadata
        except ValueError as e:
            click.echo(f'Unable to find metadata in dataset "{dataset}", it will be skipped')
    return result

def _get_detailed_imageset_info(imagesets: list, filter_str:str=None) -> str:
    """Stringifies and concatenates metadata for a list of imagesets.

    Args:
        imagesets (list): list of imageset names
        filter_str (str, optional): string to filter metadata on

    Returns:
        str: concatenated and delimited metadata string for each imageset.
    """
    result = ''
    for imageset in imagesets:
        try:
            metadata = get_imageset_metadata(imageset)
            str_metadata = _stringify_metadata(metadata)
            if filter_str:
                # case sensitive and case insensitive checks
                if filter_str in str_metadata or filter_str.upper() in str_metadata or filter_str.lower() in str_metadata:
                    result += f'--IMAGESET NAME: {imageset.upper()}' + '\n'
                    result += str_metadata
                    result += '----------' + '\n'
            else:
                result += f'--IMAGESET NAME: {imageset.upper()}' + '\n'
                result += str_metadata
                result += '----------' + '\n'
        # we know we are only calling get_imageset_metadata on imagesets that actually exist in S3,
        # so we only need to check for KeyErrors (for imagesets that do not contain metadata files)
        except KeyError as e:
            click.echo(f'Unable to find metadata in imageset "{imageset}", it will be skipped')
    return result
