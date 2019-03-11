'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Main CLI entry point for raven.
'''

import click
from raven.train.commands import train
from raven.data.commands import data

@click.group()
def cli():
    '''
    Top level command group for raven.
    '''
    pass

cli.add_command(train)
cli.add_command(data)
