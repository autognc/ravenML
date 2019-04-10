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

@click.group()
def cli():
    """ Top level command group for ravenml.
    """
    pass
    
@cli.command()
def clean():
    """ Cleans locally saved ravenml cache files.
    """
    global_cache.clean() 

cli.add_command(train)
cli.add_command(data)
cli.add_command(config)
