"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   04/05/2019

Utility module for managing ravenml's configuration.
"""

import yaml
from copy import deepcopy
from pathlib import Path
from ravenml.utils.local_cache import RMLCache
from click.exceptions import BadParameter

config_cache = RMLCache()

# required configuration fields
CONFIG_FIELDS = sorted(['image_bucket_name', 'dataset_bucket_name', 'model_bucket_name'])

def get_config() -> dict:
    """Retrieves the current configuration.
    
    Returns:
        dict: current configuration

    Raises:
        ValueError: If a required field is missing or an invalid field is found.
        FileNotFoundError: If a configuration file is not found.
    """
    config = {}
    if config_cache.subpath_exists('config.yml'):
        with open(config_cache.path / Path('config.yml'), 'r') as stream:
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
    config_cache.ensure_exists()
    with open(config_cache.path / Path('config.yml'), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
    
def load_yaml_config(path: Path):
    """Loads a YAML config file. 
    
    Used in the `train` and `data` command groups when creating datasets or running trainings.

    Args:
        path (pathlib.Path): path to YAML config file
    
    Returns:
        dict: loaded config
    
    Raises:
        click.exceptions.BadParameter: any error failing load of config file raises this
            with an appropriate error message for the particular error
    """
    try:
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError as e:
        hint = 'config, no such file exists'
        raise BadParameter(config, ctx=ctx, param=config, param_hint=hint)
    except yaml.parser.ParserError as e:
        hint = 'config file, formatting of file is invalid'
        raise BadParameter(config, ctx=ctx, param=config, param_hint=hint)
    except Exception as e:
        hint = 'unknown, unknown error occurred with config file.'
        print('-- ERROR BELOW --')
        print(e)
        raise BadParameter(config, ctx=ctx, param=config, param_hint=hint)
