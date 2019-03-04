'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   02/25/2019

Standard options which should be used by raven training plugins.
'''

import click
from raven.train.interfaces import TrainInput

### HELPERS ###


### TRAIN CONTROL OPTIONS ###
kfold_opt = click.option(
    '-k', '--kfold', is_flag=True, help='Perform kfold cross validation training.'
)


### PASS DECORATORS ###
pass_train = click.make_pass_decorator(TrainInput, ensure=True)
