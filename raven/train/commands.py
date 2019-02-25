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
def train():
    pass

@train.command(short_help='List available training plugins.')
def list():
    for entry in iter_entry_points(group='raven.plugins.train', name=None):
        print(entry.name)

@train.command()
def test():
    click.echo('Test subcommand with PyInquirer')

    questions = [
        {
            'type': 'input',
            'name': 'first_name',
            'message': 'What\'s your first name?',
        }
    ]

    ans = prompt(questions)
    click.echo(ans)
