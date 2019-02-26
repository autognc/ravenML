import click
import raven.train.options

@click.group(help='Training plugin commands.')
@click.pass_context
@raven.train.options.kfold_opt
def plugin(ctx, kfold):
    pass
    
@plugin.command()
@click.pass_context
def print(ctx):
    click.echo('Test plugin print')
