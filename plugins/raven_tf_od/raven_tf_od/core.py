import click
import raven.train.options

@click.group(help='TensorFlow Object Detection.')
@click.pass_context
@raven.train.options.kfold_opt
def tf_od(ctx, kfold):
    pass
    
@tf_od.command()
@click.pass_context
def print(ctx):
    click.echo('Test TF OD print')
