"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/25/2019

Standard options which should be used by ravenml training plugins.
"""

import click
from ravenml.train.interfaces import TrainInput

### HELPERS ###


### TRAIN CONTROL OPTIONS ###
"""
Flag to determine if K-Fold Cross Validation will be used in training.
"""
kfold_opt = click.option(
    '-k', '--kfold', is_flag=True, help='Perform kfold cross validation training.'
)


### PASS DECORATORS ###
pass_train = click.make_pass_decorator(TrainInput, ensure=True)
