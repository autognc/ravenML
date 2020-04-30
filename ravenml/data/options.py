import click

### HELPERS/CALLBACKS ###


### OPTIONS ###
"""Flag to determine if K-Fold Cross Validation will be used in training.
"""
dataset_name_opt = click.option(
    '--dataset-name', type=str,
    help='Name of dataset being created'
)

kfolds_opt = click.option(
    '--kfolds', '-k', type=int,
    help='Number of folds in dataset.'
)

upload_opt = click.option(
    '--upload', type=str,
    help='Enter the bucket you would like to upload too.'
)

delete_local_opt = click.option(
    '--delete-local', '-d', 'delete_local', is_flag=True,
    help='Delete local datasets.'
)

filter_opt = click.option(
    '-f', '--filter', is_flag=True, 
    help='Enable interactive image filtering option'
)

### PASS DECORATORS ###

