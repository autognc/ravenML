"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Main CLI entry point for raven.
"""

import click
from raven.utils.local_cache import global_cache
from raven.train.commands import train
from raven.data.commands import data

@click.group()
def cli():
    """ Top level command group for raven.
    """
    pass
    
@cli.command()
def clean():
    """ Cleans locally saved raven cache files.
    """
    global_cache.clean() 

cli.add_command(train)
cli.add_command(data)
