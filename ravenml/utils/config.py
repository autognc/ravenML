"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   04/05/2019

Utility module for managing ravenml's configuration.
"""

import yaml
from copy import deepcopy
from pathlib import Path
from ravenml.utils.local_cache import global_cache

# required configuration fields
CONFIG_FIELDS = sorted(['dataset_bucket_name', 'artifact_bucket_name'])

def get_config():
    """Retrieves the current configuration.

    Raises:
        ValueError: If a required field is missing or an invalid field is found.
        FileNotFoundError: If a configuration file is not found.
    """
    config = {}
    if global_cache.subpath_exists('config.yml'):
        with open(global_cache.path / Path('config.yml'), 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        required_fields = deepcopy(CONFIG_FIELDS)
        for key, value in config.items():
            if key in required_fields:    
                required_fields.remove(key)
            else:
                raise ValueError('Invalid field in configuration - ' + key)
        if len(required_fields) != 0:
            raise ValueError('Missing required configuration fields - ' + str(required_fields))
    else:
        raise FileNotFoundError('Configuration file does not exist.')
    return config

def update_config(config: dict):
    """Updates the configuration file.

    Args:
        config (dict): new configuration as a dict
    """
    # ensure our output location actually exists
    global_cache.ensure_exists()
    with open(global_cache.path / Path('config.yml'), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
