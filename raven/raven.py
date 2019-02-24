from __future__ import print_function, unicode_literals
import click
from PyInquirer import prompt, print_json

@click.group()
def cli():
    pass

@cli.command()
def initdb():
    click.echo('Initialized the database')

    questions = [
        {
            'type': 'input',
            'name': 'first_name',
            'message': 'What\'s your first name?',
        }
    ]

    answers = prompt(questions)
    print(answers)  # use the answers as input for your app

@cli.command()
def dropdb():
    click.echo('Dropped the database')

if __name__ == '__main__':
    cli()