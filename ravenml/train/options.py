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


### PASS DECORATORS ###
"""Click pass decorator for use in training plugin commands that expect
to receive a TrainInput object. Ensures the creation of such an object
if it is not found in the Context. This behavior enables creation
of a TrainInput directly in the ravenml train command ONLY when arguments
are passed, which allows --help and other plugin subcommands to remain unaffected
by TrainInput construction when a training is not actually being started.
"""
pass_train = click.make_pass_decorator(TrainInput, ensure=True)
