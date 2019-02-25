import click

@click.group()
def semantic():
    click.echo("Semantic")
    
@semantic.command()
def print():
    click.echo("print semantic")
