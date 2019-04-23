
"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   4/11/2019

Standard options which should be used by ravenml plugins.
"""

import click

### HELPERS/CALLBACKS ###
def no_user_callback(ctx, param: click.core.Option, value: bool):
    """Callback used by the no-user option. Evaluates all loaded parameters
    and if any are still None, throws an error.

    Args:
        param (click.core.Option): option callback has been called by
        value (bool): value of no-user option, default false
    """
    # set in context
    ctx.obj = {}
    ctx.obj['NO_USER'] = value
    # if we are in no_user mode, check all required arguments are there
    if value:
        for arg, value in ctx.params.items():
            if value is None:
                # ctx.exit('You must supply the --%s argument when using --no-user!'%arg)
                raise click.exceptions.BadParameter('bad bad', ctx=ctx, param=arg, param_hint=str(arg))

# NOTE: Any option intended to be used alongside the no_user_opt on a command
# must have their is_eager flag set to TRUE for no_user_opt to work properly

### OPTIONS ###
"""Flag to determine if the command should run in user mode.
"""
no_user_opt = click.option(
    '--no-user', is_flag=True, callback=no_user_callback, expose_value=False,
    help='Disable Inquirer prompts and use flags instead.'
)


### PASS DECORATORS ###
