"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   04/05/2019

Command group for setting raven configuration.
"""

import click
import yaml
from pathlib import Path
from colorama import init, Fore
from raven.utils.question import user_input, user_confirms
from raven.utils.config import CONFIG_FIELDS
from raven.utils.local_cache import global_cache
from raven.utils.config import get_config, update_config

init()
    
### OPTIONS ###


### COMMANDS ###
@click.group()
@click.pass_context
def config(ctx):
    """
    Configuration commands.
    """
    ctx.obj = False     # flag to indicate if entering update from show

@config.command()
@click.pass_context
def show(ctx):
    """Show current config.
    """
    try:
        # try and load the configuration
        config = get_config()
        for key, value in config.items():
            print(Fore.GREEN + key + ': ' + Fore.WHITE + value)
    except FileNotFoundError:
        # thrown when no configuration file is found
        click.echo(Fore.RED + 'No configuration found.')
        if user_confirms('Would you like to make a new configuration?', default=True):
            ctx.obj = True
            ctx.invoke(update)
    except ValueError:
        # thrown when current configuration file is invalid
        click.echo(Fore.RED + 'Current configuration file is invalid.')
        if user_confirms('Would you like to fix it?', default=True):
            ctx.obj = True
            ctx.invoke(update)

@config.command()
@click.pass_context
def update(ctx):
    """Update current config.
    """
    config = {}
    try: 
        # try and load the configuration
        config = get_config()
    except FileNotFoundError:
        # thrown when no configuration file is found
        # checks to see if flag is set to indicate we arrived here from show
        if not ctx.obj:
            click.echo(Fore.RED + 'No configuration found to update. A new one will be created.')
    except ValueError:
        # thrown current configuration file is invalid
        # checks to see if flag is set to indicate we arrived here from show
        if not ctx.obj:
            click.echo(Fore.RED + 'Current configuration is invalid. A new one will be created.')

    # flag to indicate if config was successfully loaded or not
    loaded = len(config) > 0
    
    # update configuration fields
    for field in CONFIG_FIELDS:
        if loaded:
            if user_confirms('Edit ' + field + '?'):
                config[field] = user_input(field + ':', default=config[field]) 
        else:
            config[field] = user_input(field + ':')

    # save updates
    update_config(config)
