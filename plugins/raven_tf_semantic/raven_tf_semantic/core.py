import click
from raven.train.options import kfold_opt, pass_train
from raven.train.interfaces import TrainInput, TrainOutput

@click.group(help='TensorFlow Semantic Segmentation.')
@click.pass_context
def tf_semantic(ctx):
    pass
    
@tf_semantic.command()
@kfold_opt
@pass_train
@click.pass_context
def train(ctx, train: TrainInput, kfold):
    # If the context has a TrainInput already, it is passed as "train"
    # If it does not, the constructor is called AUTOMATICALLY
    # by Click because the @pass_train decorator is set to ensure
    # object creation, after which the created object is passed as "train"
    # after training, create an instance of TrainOutput and return it
    print(kfold)
    print(train.dataset)
    print(train.artifact_path)
    result = TrainOutput()
    return result
