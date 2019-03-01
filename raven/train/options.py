'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/25/2019

Standard options which should be used by raven training plugins.
'''

import click

'''
Flag to determine if K-Fold Cross Validation will be used in training.
'''
kfold_opt = click.option(
    '-k', '--kfold', is_flag=True, help='Perform kfold cross validation training.'
)
