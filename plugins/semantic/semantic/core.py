import click
import raven.train.options

@click.group(help='Semantic training commands.')
@click.pass_context
@raven.train.options.kfold_opt
def semantic(ctx, kfold):
    pass
    
@semantic.command()
@click.pass_context
def print(ctx):
    click.echo('Test semantic print')
