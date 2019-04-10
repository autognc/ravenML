from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click
from ravenml.train.options import kfold_opt, pass_train
from ravenml.train.interfaces import TrainInput, TrainOutput

from absl import flags
import tensorflow as tf
from object_detection import model_hparams
from object_detection import model_lib
from utils.utils import prepare_for_training
import os

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

    data_path = train.dataset.get_dataset_path()

    base_dir = train.artifact_path
    base_dir = '/Users/nihaldhamani/Desktop/test'
    prepare_for_training(data_path, base_dir)

    model_dir = os.path.join(base_dir, 'models/model')
    pipeline_config_path = os.path.join(base_dir, 'models/model/pipeline.config')

    config = tf.estimator.RunConfig(model_dir=model_dir)
    train_and_eval_dict = model_lib.create_estimator_and_inputs(
        run_config=config,
        hparams=model_hparams.create_hparams(None),
        pipeline_config_path=pipeline_config_path,
        train_steps=20)
    
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
        eval_on_train_data=False)

    tf.estimator.train_and_evaluate(estimator, train_spec, eval_specs[0])

    result = TrainOutput()

    return result

