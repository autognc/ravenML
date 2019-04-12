"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Main CLI entry point for ravenml.
"""

import click
from ravenml.utils.local_cache import global_cache
from ravenml.train.commands import train
from ravenml.data.commands import data
from ravenml.config.commands import config
from ravenml.utils.config import get_config, update_config

## OPTIONS
clean_all_opt = click.option(
    '-a', '--all', is_flag=True,
    help='Clear all cache contents, including saved ravenML configuration.'
)

@click.group()
def cli():
    """ Top level command group for ravenml.
    """
    pass
    
@cli.command()
@clean_all_opt
def clean(all):
    """ Cleans locally saved ravenml cache files.
    """
    if all:
        global_cache.clean() 
    else:
        try:
            config = get_config()
            global_cache.clean()
            update_config(config)
        except (ValueError, FileNotFoundError):
            global_cache.clean()

cli.add_command(train)
cli.add_command(data)
cli.add_command(config)
