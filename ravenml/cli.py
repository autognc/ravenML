"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Main CLI entry point for ravenml.
"""

import click
from colorama import init, Fore
from ravenml.train.commands import train
from ravenml.data.commands import data
from ravenml.config.commands import config
from ravenml.utils.config import get_config, update_config
from ravenml.utils.local_cache import RMLCache

init()
cache = RMLCache()

### OPTIONS ###
clean_all_opt = click.option(
    '-a', '--all', is_flag=True,
    help='Clear all cache contents, including saved ravenML configuration.'
)


### COMMANDS ###
@click.group(help='Welcome to ravenML!')
def cli():
    """ Top level command group for ravenml.
    """
    pass
    
@cli.command(help='Cleans locally saved ravenML cache files.')
@clean_all_opt
def clean(all: bool):
    """ Cleans locally saved ravenml cache files.

    Args:
        all (bool): T/F whether to clean all files from cache, including
            configuration YAML, default false
    """
    if all:
        if not cache.clean():
            click.echo(Fore.RED + 'No cache to clean.')
    else:
        try:
            config = get_config()
            cache.clean()
            update_config(config)
        except ValueError:
            click.echo(Fore.RED + 'Bad configuration file. Deleting alongside cache.') 
            cache.clean()
        except FileNotFoundError:
            if not cache.clean():
                click.echo(Fore.RED + 'No cache to clean.')

cli.add_command(train)
cli.add_command(data)
cli.add_command(config)
