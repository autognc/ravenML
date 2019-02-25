import click

@click.group()
def plugin():
    click.echo("Core click")
    
@plugin.command()
def print():
    click.echo("print core")
