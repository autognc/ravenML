"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   02/25/2019

Standard options which should be used by ravenml training plugins.
"""

import click
from ravenml.train.interfaces import TrainInput

### HELPERS/CALLBACKS ###

### OPTIONS ###

### PASS DECORATORS ###
"""Click pass decorator for use in training plugin commands that expect
to receive a TrainInput object. Triggers the creation of a TrainInput at ctx.obj
if one does not already exist there when the command executes. This behavior is used
to allow --help and other non-training plugin subcommands to run without triggering
TrainInput construction. See the TrainInput __init__ for more details.
"""
pass_train = click.make_pass_decorator(TrainInput, ensure=True)
