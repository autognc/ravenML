import click
from raven.train.options import kfold_opt, pass_train
from raven.train.interfaces import TrainInput, TrainOutput

@click.group(help='TensorFlow Semantic Segmentation.')
@click.pass_context
@kfold_opt
def tf_semantic(ctx, kfold):
    pass
    
@tf_semantic.command()
@pass_train
@click.pass_context
def train(ctx, train: TrainInput):
    # If the context has a TrainInput already, it is passed as "train"
    # If it does not, the constructor is called AUTOMATICALLY
    # by Click because the @pass_train decorator is set to ensure
    # object creation
    # after training, create an instance of TrainOutput and return it
    result = TrainOutput()
    return result
