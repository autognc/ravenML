
"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)  
Date Created:   4/11/2019

Standard options which should be used by ravenml plugins.

NOTE: there is currently nothing in this value except old functionality
that is no longer in use.
"""

import click

### HELPERS/CALLBACKS ###

# NOTE: the no_user callback and option are currently unused, however I am leaving it in the codebase
# so its functionality can be brought back if needed in the future. Its purpose is to
# ensure that ALL options to a command are set if the --no-user option is passed.
# def no_user_callback(ctx, param: click.core.Option, value: bool):
#     """Callback used by the no-user option. Evaluates all loaded parameters
#     and if any are still None, throws an error.

#     Args:
#         param (click.core.Option): option callback has been called by
#         value (bool): value of no-user option, default false
#     """
#     # set in context
#     if ctx.obj is None:
#         ctx.obj = {}
#     ctx.obj['NO_USER'] = value
#     # if we are in no_user mode, check all required arguments are there
#     if value:
#         for arg, value in ctx.params.items():
#             if value is None:
#                 # ctx.exit('You must supply the --%s argument when using --no-user!'%arg)
#                 raise click.exceptions.BadParameter('You must provide this argument when using --no-user!',
#                                                     ctx=ctx, param=arg, param_hint=str(arg))
# # NOTE: Any option intended to be used alongside the no_user_opt on a command
# # must have their is_eager flag set to TRUE for no_user_opt to work properly
# """Flag to determine if the command should run in user mode.
# """
# no_user_opt = click.option(
#     '--no-user', is_flag=True, callback=no_user_callback, expose_value=False,
#     help='Disable Inquirer prompts and use flags instead.'
# )

### OPTIONS ###

# NOTE: The pattern below is currently unused as we no longer make use of large
# numbers of options on a single command. I'm leaving it in the codebase in case its functionality
# is needed in the future. The option_decorator is a decorator that can be used on a click command
# using the same @option_decorator syntax as other decorators. It then applies all options
# defined in the "opts" list to that command in the order they are given in the list.
# This is just synactic sugar but makes the commands look much nicer.
# opts = [
#     verbose_opt,
#     comet_opt,
#     author_opt,
#     comments_opt,
#     model_name_opt,
#     optimizer_opt,
#     use_default_config_opt,
#     hyperparameters_opt
# ]

# ## Importable Option Decorator ##
# def option_decorator(func):
#     chain = opts[-1](func)
#     # must loop backwards so order of arguments in click
#     # command def is same as order in opts list
#     for i in range(len(opts) - 2, -1, -1):
#         chain = opts[i](chain)
#     return chain


### PASS DECORATORS ###
