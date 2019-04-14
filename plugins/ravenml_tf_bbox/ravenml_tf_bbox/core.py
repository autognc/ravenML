from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import click
import io
import sys
import importlib
from absl import flags
from pathlib import Path
from ravenml.train.options import kfold_opt, pass_train
from ravenml.train.interfaces import TrainInput, TrainOutput
from utils.utils import prepare_for_training, download_model_arch, bbox_cache

@click.group(help='TensorFlow Object Detection with bounding boxes.')
@click.pass_context
def tf_bbox(ctx):
    pass
    
@tf_bbox.command()
@kfold_opt
@pass_train
@click.pass_context
def train(ctx, train: TrainInput, kfold):
    # If the context has a TrainInput already, it is passed as "train"
    # If it does not, the constructor is called AUTOMATICALLY
    # by Click because the @pass_train decorator is set to ensure
    # object creation, after which the created object is passed as "train"
    # after training, create an instance of TrainOutput and return it
    _import_od()
    
    tf.logging.set_verbosity(tf.logging.INFO)
    
    data_path = train.dataset.get_dataset_path()

    if train.artifact_path is None:
        base_dir = str(bbox_cache.path / Path('temp'))
    else:
        base_dir = str(train.artifact_path)
    # base_dir = '/home/carson/Desktop/test'

    # make into list for diff files
    arch_model_name = 'ssd_mobilenet_v1_coco_2018_01_28'

    arch_path = download_model_arch(arch_model_name)

    prepare_for_training(data_path, base_dir, arch_path)

    model_dir = os.path.join(base_dir, 'models/model')
    pipeline_config_path = os.path.join(base_dir, 'models/model/pipeline.config')

    config = tf.estimator.RunConfig(model_dir=model_dir)
    train_and_eval_dict = model_lib.create_estimator_and_inputs(
        run_config=config,
        hparams=model_hparams.create_hparams(None),
        pipeline_config_path=pipeline_config_path,
        train_steps=100)
    
    estimator = train_and_eval_dict['estimator']
    train_input_fn = train_and_eval_dict['train_input_fn']
    eval_input_fns = train_and_eval_dict['eval_input_fns']
    eval_on_train_input_fn = train_and_eval_dict['eval_on_train_input_fn']
    predict_input_fn = train_and_eval_dict['predict_input_fn']
    train_steps = train_and_eval_dict['train_steps']

    train_spec, eval_specs = model_lib.create_train_and_eval_specs(
        train_input_fn,
        eval_input_fns,
        eval_on_train_input_fn,
        predict_input_fn,
        train_steps,
        final_exporter_name='exported_model',
        eval_on_train_data=False)

    tf.estimator.train_and_evaluate(estimator, train_spec, eval_specs[0])

    result = TrainOutput()

    return result

# stdout redirection found at https://codingdose.info/2018/03/22/supress-print-output-in-python/
def _import_od():
    """ Imports the necessary libraries for object detection training.
    Used to avoid importing them at the top of the file where they get imported
    on every ravenML command call, even those not to this plugin.
    
    Also suppresses warning outputs from the TF OD API.
    """
    # create a text trap and redirect stdout
    # to suppress printed warnings from object detection and tf
    text_trap = io.StringIO()
    sys.stdout = text_trap
    
    # Calls to _dynamic_import below map to the following standard imports:
    #
    # import tensorflow as tf
    # from object_detection import model_hparams
    # from object_detection import model_lib
    _dynamic_import('tensorflow', 'tf')
    _dynamic_import('object_detection.model_hparams', 'model_hparams')
    _dynamic_import('object_detection.model_lib', 'model_lib')
    
    # now restore stdout function
    sys.stdout = sys.__stdout__
    
# this function is derived from https://stackoverflow.com/a/46878490
def _dynamic_import(modulename, shortname = None, asfunction = False):
    """ Function to dynamically import python modules into the global scope.

    Args:
        modulename (str): name of the module to import (ex: os, ex: os.path)
        shortname (str, optional): desired shortname binding of the module (ex: import tensorflow as tf)
        asfunction (bool, optional): whether the shortname is a module function or not (ex: from time import time)
        
    Examples:
        Whole module import: i.e, replace "import tensorflow"
        >>> _dynamic_import('tensorflow')
        
        Named module import: i.e, replace "import tensorflow as tf"
        >>> _dynamic_import('tensorflow', 'tf')
        
        Submodule import: i.e, replace "from object_detction import model_lib"
        >>> _dynamic_import('object_detection.model_lib', 'model_lib')
        
        Function import: i.e, replace "from ravenml.utils.config import get_config"
        >>> _dynamic_import('ravenml.utils.config', 'get_config', asfunction=True)
        
    """
    if shortname is None: 
        shortname = modulename
    if asfunction is False:
        globals()[shortname] = importlib.import_module(modulename)
    else:        
        globals()[shortname] = getattr(importlib.import_module(modulename), shortname)
