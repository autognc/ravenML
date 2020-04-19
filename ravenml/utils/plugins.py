"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   05/03/2019

Provides useful helper functions for training plugins.
"""

import click
from datetime import datetime
from ravenml.data.interfaces import Dataset
from ravenml.utils.question import user_input

def fill_basic_metadata(metadata: dict, dataset: Dataset, name=None, comments=None):
    """Adds basic metadata to the provided dictionary with user input
    and dataset fields.
    
    Metadata added:
        created_by (prompted): name of user performing the training
        comments (prompted); user comments about the training
        date_started_at: timestamp in ISO time
        dataset_used: dataset used for this training

    Args:
        metadata (dict): metadata dictionary object
        dataset (Dataset): training dataset
    
    Example:
        >>> metadata = {}
        >>> fill_basic_metadata(metadata, dataset)
    """
    metadata['created_by'] = name if name else user_input('Please enter your first and last name:')
    metadata['comments'] = comments if comments else user_input('Please enter any comments about this training:')
    metadata['date_started_at'] = datetime.utcnow().isoformat() + "Z"
    metadata['dataset_used'] = dataset.metadata
    
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

