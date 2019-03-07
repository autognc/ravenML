'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/23/2019

Main CLI entry point for raven.
'''

import click
from raven.train.commands import train

@click.group()
def cli():
    '''
    Top level command group for raven.
    '''
    pass

cli.add_command(train)
