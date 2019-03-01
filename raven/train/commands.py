'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Command group for training in raven.
'''

from pkg_resources import iter_entry_points

import click
from click_plugins import with_plugins

from PyInquirer import prompt

@with_plugins(iter_entry_points('raven.plugins.train'))
@click.group()
@click.pass_context
def train(ctx):
    '''
    Train command group. Just needs to exist, everything flows from this.
    '''
    pass

@train.command(help='List available training plugins.')
def list():
    '''
    Lists mounted training plugins by name.
    '''
    for entry in iter_entry_points(group='raven.plugins.train', name=None):
        print(entry.name)
