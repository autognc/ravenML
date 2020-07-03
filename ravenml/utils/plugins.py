"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   05/03/2019

Provides useful helper functions for training plugins.
"""

import click

def raise_parameter_error(option, hint: str):
    raise click.exceptions.BadParameter(option, param=option, param_hint=hint)

### DYNAMIC IMPORT FUNCTION ###
# NOTE: this function should be used in all plugins, but the function is NOT
# importable because of the use of globals(). You must copy the code.
# function is derived from https://stackoverflow.com/a/46878490

# def _dynamic_import(modulename, shortname = None, asfunction = False):
#     """ Function to dynamically import python modules into the global scope.

#     Args:
#         modulename (str): name of the module to import (ex: os, ex: os.path)
#         shortname (str, optional): desired shortname binding of the module (ex: import tensorflow as tf)
#         asfunction (bool, optional): whether the shortname is a module function or not (ex: from time import time)
        
#     Examples:
#         Whole module import: i.e, replace "import tensorflow"
#         >>> _dynamic_import('tensorflow')
        
#         Named module import: i.e, replace "import tensorflow as tf"
#         >>> _dynamic_import('tensorflow', 'tf')
        
#         Submodule import: i.e, replace "from object_detction import model_lib"
#         >>> _dynamic_import('object_detection.model_lib', 'model_lib')
        
#         Function import: i.e, replace "from ravenml.utils.config import get_config"
#         >>> _dynamic_import('ravenml.utils.config', 'get_config', asfunction=True)
        
#     """
#     if shortname is None: 
#         shortname = modulename
#     if asfunction is False:
#         globals()[shortname] = importlib.import_module(modulename)
#     else:        
#         globals()[shortname] = getattr(importlib.import_module(modulename), shortname)

