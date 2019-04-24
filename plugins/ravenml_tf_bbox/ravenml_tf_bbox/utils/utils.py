import os
import shutil
import tarfile
import yaml
import click
import urllib.request
from colorama import init, Fore
from pathlib import Path
from ravenml.utils.local_cache import LocalCache, global_cache
from ravenml.utils.question import user_confirms, user_input, user_selects

init()

bbox_cache = LocalCache(global_cache.path / Path('tf-bbox'))

def prepare_for_training(data_path, base_dir, arch_path, model_type, metadata: dict):

    hp_metadata = {}

    # check if base_dir exists already and prompt before overwriting
    if os.path.exists(base_dir):
        if user_confirms('Artifact storage location contains old data. Overwrite?'):
            shutil.rmtree(base_dir)
        else:
            return False
    os.makedirs(base_dir)
    click.echo('Created artifact folder.')
    
    # create a data folder within our base_directory
    os.makedirs(os.path.join(base_dir, 'data'))
    click.echo('Created data folder.')

    # copy object-detection.pbtxt from utilities and move into data folder
    pbtxt_file = os.path.join(data_path, 'label_map.pbtxt')
    shutil.copy(pbtxt_file, os.path.join(base_dir, 'data'))
    click.echo('Placed label_map.pbtxt file inside data folder.')

    # create models, model, eval, and train folders
    models_folder = os.path.join(base_dir, 'models')
    os.makedirs(models_folder)
    model_folder = os.path.join(models_folder, 'model')
    os.makedirs(model_folder)
    eval_folder = os.path.join(model_folder, 'eval')
    train_folder = os.path.join(model_folder, 'train')
    # os.makedirs(eval_folder)
    os.makedirs(train_folder)
    click.echo('Created models, model, train, eval folders')
    
    ## prompt for optimizers
    defaults = {}
    defaults_path = os.path.dirname(__file__) / Path('model_defaults') / Path(f'{model_type}_defaults.yml')
    with open(defaults_path, 'r') as stream:
        try:
            defaults = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    optimizer_name = user_selects('Choose optimizer', defaults.keys())
    hp_metadata['optimizer'] = optimizer_name
    
    ### create pipeline file based on a template and our desired path ###
    
    # grab default config for the chosen optimizer
    default_config = defaults[optimizer_name]
    
    # load pipeline file
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_name = f'{model_type}_{optimizer_name.lower()}.config'
    pipeline_path = os.path.join(cur_dir, 'pipeline_templates', pipeline_name)

    with open(pipeline_path) as template:
        pipeline_contents = template.read()
    if base_dir.endswith('/') or base_dir.endswith(r"\\"):
        pipeline_contents = pipeline_contents.replace('<replace_path>', base_dir)
    else:
        if os.name == 'nt':
            pipeline_contents = pipeline_contents.replace('<replace_path>', base_dir + r"\\")
        else:
            pipeline_contents = pipeline_contents.replace('<replace_path>', base_dir + '/')
            
    # prompt user for new configuration
    user_config = _configuration_prompt(default_config)
    # add to hyperparameter metadata dict
    for field, value in user_config.items():
        hp_metadata[field] = value
    # replace at all instances in config file
    for key, value in user_config.items():
        formatted = '<replace_' + key + '>'
        pipeline_contents = pipeline_contents.replace(formatted, str(value))

    # output new configuation
    pipeline_path = os.path.join(model_folder, 'pipeline.config')
    with open(pipeline_path, 'w') as file:
        file.write(pipeline_contents)
    click.echo('Created pipeline.config file inside models/model/.')
    
    # TODO: change to move all sharded chunks
    train_record = os.path.join(data_path, 'dev/standard/tf/train.record-00000-of-00001')
    test_record = os.path.join(data_path, 'dev/standard/tf/test.record-00000-of-00001')

    shutil.copy(train_record, os.path.join(base_dir, 'data'))
    shutil.copy(test_record, os.path.join(base_dir, 'data'))
    click.echo("Copied records to data directory.")

    # copy model checkpoints to our train folder
    checkpoint_folder = os.path.join(arch_path)
    checkpoint0_folder = os.path.join(cur_dir, 'checkpoint_0')
    # file1 = os.path.join(checkpoint_folder, 'checkpoint')

    file1 = os.path.join(checkpoint_folder, 'model.ckpt.data-00000-of-00001')
    file2 = os.path.join(checkpoint_folder, 'model.ckpt.index')
    file3 = os.path.join(checkpoint_folder, 'model.ckpt.meta')
    file4 = os.path.join(checkpoint0_folder, 'model.ckpt-0.data-00000-of-00001')
    file5 = os.path.join(checkpoint0_folder, 'model.ckpt-0.index')
    file6 = os.path.join(checkpoint0_folder, 'model.ckpt-0.meta')
    checkpoint_file = os.path.join(checkpoint0_folder, 'checkpoint')
    shutil.copy2(file1, train_folder)
    shutil.copy2(file2, train_folder)
    shutil.copy2(file3, train_folder)
    shutil.copy2(file4, train_folder)
    shutil.copy2(file5, train_folder)
    shutil.copy2(file6, train_folder)
    with open(checkpoint_file) as cf:
        checkpoint_contents = cf.read()
    checkpoint_contents = checkpoint_contents.replace('<replace>', train_folder)
    with open(os.path.join(train_folder, 'checkpoint'), 'w') as new_cf:
        new_cf.write(checkpoint_contents)
    click.echo('Added model checkpoints to models/model/train folder.')
    
    metadata['hyperparemeters'] = hp_metadata
    
    return True


def download_model_arch(model_name):

    url = 'http://download.tensorflow.org/models/object_detection/%s.tar.gz' %(model_name)
    
    # make paths within bbox cache 
    bbox_cache.ensure_subpath_exists('bbox_model_archs')
    archs_path = bbox_cache.path / Path('bbox_model_archs')
    untarred_path = archs_path / Path(model_name)
    
    # check if download is required
    if not bbox_cache.subpath_exists(untarred_path):
        click.echo("Model checkpoint not found in cache. Downloading...")
        # download tar file
        tar_name = url.split('/')[-1]
        tar_path = archs_path / Path(tar_name)
        urllib.request.urlretrieve(url, tar_path)
        
        click.echo("Untarring model checkpoint...")
        if (tar_name.endswith("tar.gz")):
            tar = tarfile.open(tar_path, "r:gz")
            tar.extractall(path=archs_path)
            tar.close()

        # get rid of tar file
        os.remove(tar_path)
    else:
        click.echo('Model checkpoint found in cache.')
    return untarred_path
    
def _configuration_prompt(current_config: dict):
    _print_config(current_config)
    if user_confirms('Edit default configuration?'):
        for field in current_config:
            if user_confirms(f'Edit {field}? (default: {current_config[field]})'):
                current_config[field] = user_input(f'{field}:', default=str(current_config[field]))
    return current_config

def _print_config(config: dict):
    click.echo('Current configuration:')
    for field, value in config.items():
        click.echo(Fore.GREEN + f'{field}: ' + Fore.WHITE + f'{value}')
