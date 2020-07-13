import os, shutil, time, json
import contextlib2
from pathlib import Path
from object_detection.dataset_tools import tf_record_creation_util
from random import shuffle
from datetime import datetime
from ravenml.data.interfaces import CreateInput
from ravenml.utils.question import cli_spinner, cli_spinner_wrapper

class DatasetWriter(object):

    def __init__(self, create: CreateInput, **kwargs):
        self.associated_files = kwargs['associated_files']
        self.related_data_prefixes = kwargs['related_data_prefixes']
        
        metadata = create.metadata
        self.num_folds = metadata['kfolds'] if metadata.get('kfolds') else 5 # Never actually used
        self.test_percent = metadata['test_percent'] if metadata.get('test_percent') else .2
        self.label_to_int_dict = {}
        self.dataset_path = create.dataset_path
        self.dataset_name = metadata['dataset_name']
        self.cache = create.plugin_cache
    
    def construct_all(self, *args, **kwargs):
        raise NotImplementedError

    def export_as_TFExample(self, *args, **kwargs):
        raise NotImplementedError
    
    def write_additional_files(self, *args, **kwargs):
        raise NotImplementedError

    @cli_spinner_wrapper("Writing out dataset locally...")
    def write_dataset(self, obj_list: list):
        """Main driver for this file
        
        Args:
            obj_list (list): objects that will be transformed into usable dataset
            test_percent (float): percent of data that'll be test data
            num_folds (int): number of folds to write
            out_dir (Path): directory to write this dataset to
            custom_dataset_name (str): name of the dataset's containing folder
        """

        dataset_path = self.dataset_path / self.dataset_name
        print(dataset_path)
        self.delete_dir(dataset_path) # Only deletes the contents already inside the directory

        test_subset, dev_subset = self.split_data(obj_list)

        # Test subset.
        self.write_related_data(test_subset, dataset_path / 'test')

        dev_path = dataset_path / 'splits'

        # standard_path = dev_path / 'standard'
        # write_out_fold(standard_path, fold, is_standard=True)

        complete_path = dev_path / 'complete'
        self.write_out_complete_set(complete_path, dev_subset)

    def delete_dir(self, path):
        """Deletes all files and folders in specified directory
        
        Args:
            path (Path object): target directory
        """
        if os.path.isdir(path):
            print('\n', "Deleting contents of", path,
                "you've got five seconds to cancel this.")
            time.sleep(5)

            for the_file in os.listdir(path):
                file_path = os.path.join(path, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
                    raise Exception(
                        "Directory deletion failed. Maybe you have a file explorer/terminal open in this dir?"
                    )

            print('\n', "Done deleting contents of", path)

    def split_data(self, obj_list):
        """Splits obj_list into test/dev sets
        
        Args:
            obj_list (list): list of objects to divide into test/dev
            test_percent (int): percentage of objects in the test set
        
        Returns:
            tuple of two lists. The first list is test, second dev
        """
        if len(obj_list) == 0:
            raise Exception("Empty object list passed.")
        if len(obj_list) == 1:
            raise Exception(
                "Object list of length 1 passed. Can't build test and dev set with this."
            )

        shuffle(obj_list)
        index_to_split_on = max(1, int(len(obj_list) * self.test_percent))

        test = obj_list[:index_to_split_on]
        dev = obj_list[index_to_split_on:]

        return (test, dev)

    def write_related_data(self, objects, path):
        if not os.path.exists(path):
            os.makedirs(path)

        for obj in objects:
            self.copy_associated_files(path, obj)

    def copy_associated_files(self, destination, obj):
            data_dir = self.cache.path / 'data'

            for suffix in self.associated_files.values():
                for prefix in self.related_data_prefixes.values():
                    filepath = data_dir / f'{prefix}{obj.get("image_id")}{suffix}'
                    if os.path.exists(filepath):
                        shutil.copy(
                            str(filepath.absolute()), str(destination.absolute()))

    def write_out_complete_set(self, path, data):
        """Writes out the special complete set into 'dev'. No validation data.
        
        Args:
            path (Path): directory to write complete set out to
            data (list): objects to write to the complete set
        """
        record_path = path / 'train'
        if not os.path.exists(record_path):
            os.makedirs(record_path)

        test_record_data, train_record_data = self.split_data(data)

        self.write_out_tf_examples(train_record_data, record_path / 'train.record')
        self.write_out_tf_examples(test_record_data, record_path / 'test.record')

    def write_out_tf_examples(self, objects, path):
        """Writes out list of objects out as a single tf_example
        
        Args:
            objects (list): list of objects to put into the tf_example 
            path (Path): directory to write this tf_example to, encompassing the name
        """
        num_shards = (len(objects) // 1000) + 1
        
        with open(str(path) + '.numexamples', 'w') as output:
            output.write(str(len(objects)))

        with contextlib2.ExitStack() as tf_record_close_stack:
            output_tfrecords = tf_record_creation_util.open_sharded_output_tfrecords(
                tf_record_close_stack, path, num_shards)

            for index, object_item in enumerate(objects):
                tf_example = self.export_as_TFExample(object_item)
                output_shard_index = index % num_shards
                output_tfrecords[output_shard_index].write(
                    tf_example.SerializeToString())
