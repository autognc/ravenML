'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   03/10/2019

Command group for dataset exploration in raven.
'''

import click

# placerholder: will eventually hit AWS to find available datasets
def get_datasets():
    return ['a', 'b', 'c']
    
    
### OPTIONS ###


### COMMANDS ###
@click.group()
@click.pass_context
def data(ctx):
    '''
    Dataset exploration commands.
    '''
    pass

@data.resultcallback()
@click.pass_context
def process_result(ctx, result):
    pass

@data.command()
def list():
    '''
    List available datasets.
    '''
    click.echo('List stuff here')
