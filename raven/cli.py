'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   02/23/2019

Cli 
'''
import click
from .train import train

@click.group()
def cli():
    pass

cli.add_command(train)

# @with_plugins(iter_entry_points('raven.plugins'))
# @click.group()
# def cli():
#     pass


