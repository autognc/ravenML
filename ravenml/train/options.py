"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/25/2019

Standard options which should be used by ravenml training plugins.
"""

import click
from ravenml.train.interfaces import TrainInput

### HELPERS/CALLBACKS ###


### OPTIONS ###
"""Flag to determine if K-Fold Cross Validation will be used in training.
"""
kfold_opt = click.option(
    '-k', '--kfold', is_flag=True, help='Perform kfold cross validation training.'
)

commet_opt = click.option(
    '-c', '--comet', type=str,
    help='Create comet experiment with specified name on this training run.'
)

model_name_opt = click.option(
    '-m', '--model-name', type=str,
    help='Name of model to be used for training.'
)

overwrite_local_opt = click.option(
    '-o', '--overwrite-local', is_flag=True,
    help='Overwrite files that may be in path specified.'
)

optimizer_opt = click.option(
    '--optimizer', type=str,
    help='Optimizer for training.'
)

use_default_config_opt = click.option(
    '--use-default-config', is_flag=True,
    help='Use default configuration for training'
)

hyperparameters_opt = click.option(
    '--hyperparameters', type=str,
    help='List of specified configurations for training'
)

### PASS DECORATORS ###
"""Click pass decorator for use in training plugin commands that expect
to receive a TrainInput object. Ensures the creation of such an object
if it is not found in the Context. This behavior enables creation
of a TrainInput directly in the ravenml train command ONLY when arguments
are passed, which allows --help and other plugin subcommands to remain unaffected
by TrainInput construction when a training is not actually being started.
"""
pass_train = click.make_pass_decorator(TrainInput, ensure=True)
