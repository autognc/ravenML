import os, inspect, shutil, time, json, subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
from ravenml.data.interfaces import CreateInput
from ravenml.utils.question import cli_spinner, cli_spinner_wrapper, DecoratorSuperClass
from ravenml.utils.config import get_config
from ravenml.data.helpers import default_filter, copy_associated_files, split_data, read_json_metadata

class DatasetWriter(DecoratorSuperClass):
    """Interface for creating datasets, methods are in order of what is expected to be 
        called by the plugins

    Methods:
        __init__ (CreateInput): takes in CreateInput object and initializes variables
            to be used by the rest of the methods and the plugins
        load_image_ids (): gets all image_ids/tags from the supplied imagesets based on
            finding metadata files
        interactive_filter (): takes the current image_ids and allows the user to create
            sets through interactive filtering using the image_ids
        construct_all (): plugin specific method to generate objects which will be used
            in writing the dataset
        write_dataset (): main driver for writing the dataset locally
        write_metadata (): writes dataset metadata file(s)
        write_additional_files (): writes any plugin_specific files not covered in
            write_dataset, write_metadata
    """

    def __init__(self, create: CreateInput, **kwargs):
        """Initialization for interface, tags_df, image_ids, and
            filter_metadata are initialized with dummy values and
            are meant to be filled in by method calls.

        Args:
            create (CreateInput): what is passed to the plugin,
                containing configuration information
        
        Initializations:
            num_folds (int): number of folds in dataset
            test_percent (float): percentage of dataset to be used in test set
            dataset_path (Path): path to where dataset should be written
            dataset_name (String): name of dataset
            created_by (String): name of person creating dataset
            comments (String): comments on dataset
            plugin_name (String): name of the plugin being used
            imageset_paths (list): list of paths to all imagesets being used
            tags_df (pandas dataframe): after load_image_ids() is run, holds 
                tags associated with each image_id
            image_ids (list): list of tuples containing a path to an imageset
                and an image_id in that imageset
            filter_metadata (dict): holds the groups of different subsets of
                image_ids
        """

        metadata = create.metadata
        self.num_folds = create.kfolds
        self.test_percent = create.test_percent
        self.dataset_path = create.dataset_path
        self.dataset_name = metadata['dataset_name']
        self.created_by = metadata['created_by']
        self.comments = metadata['comments']
        self.plugin_name = create.plugin_metadata['architecture']
        self.imageset_paths = create.imageset_paths
        self.tags_df = pd.DataFrame()
        self.image_ids = None
        self.filter_metadata = {"groups": []}
        self.obj_dict = {}
    
    def load_image_ids(self):
        """Method goes through imagesets and is expected to populate the 'tags_df'
            dataframe with image_ids and tags related to each image_id, as well
            as 'image_ids' with a list of image_ids.

        Args:
        """
        raise NotImplementedError

    def interactive_filter(self):
        """Method assumes that 'image_ids' and 'tags_df' have already been found and allows
            user to filter through them for subsets they choose to use based on tags

        Args:
        """
        raise NotImplementedError

    def construct_all(self):
        """Method should create objects from the image_ids given with whatever
            information is needed for the write_dataset method to use. Is required 
            to set 'obj_dict' to be a dictionary with image_id keys and the constructed
            objects as values.

        Args:
        """
        raise NotImplementedError

    @cli_spinner_wrapper("Writing out dataset locally...")
    def write_dataset(self):
        """Main driver, writes dataset based on objects passed from construct_all

        Args:
        """
        raise NotImplementedError

    @cli_spinner_wrapper("Writing out metadata locally...")
    def write_metadata(self):
        """Writes out a metadata file

        Args:
        """
        raise NotImplementedError
    
    @cli_spinner_wrapper("Writing out additional files...")
    def write_additional_files(self):
        """Writes out additional files

        Args:
        """
        raise NotImplementedError

class DefaultDatasetWriter(DatasetWriter):
    """Default Interface for creating datasets, methods are in order of what is expected to be 
        called by the plugins. Plugin is expected to override 'construct_all', 'export_data',
        and 'write_additional_files', if the plugin expects to call 'write_dataset'. 

    Methods (not in DatasetWriter):
        write_out_train_split (objects, path, split_type): method that is overridden by the plugin, is called
            on by 'write_out_complete_set' in this implementation to write the contents of the objects
            created by 'construct_all'
        write_out_test_set (path (Path), data (list)): helper method for this implementation of
            'write_dataset', writes out test set   
        write_out_complete_set (path (Path), data (list)): helper method for this implementation of
            'write_dataset', creates test and train groups and corresponding paths for plugin to write to        
    """

    def __init__(self, create: CreateInput):
        """Method calls DatasetWriter's initialization to get all variables it needs

        Args:
            create (CreateInput): what is passed to the plugin,
                containing configuration information
        """
        super().__init__(create)

    def write_out_train_split(self, objects, path, split_type, *args, **kwargs):
        """Method should be overridden by plugin if default 'write_dataset' implementation is to be called.
            Method writes data in plugin-specific way, given objects and the path to write to. The train
            split includes training data and validation/development data depending on the split type.

        Args:
            objects (object): objects made by 'construct_all' that are used to write data
            path (Path): filepath to where data should be written
            split_type (String): type of split that is being written, currently the only two possibilities
                being called by 'write_complete_set' are 'train' and 'test'.
        """
        raise NotImplementedError
    
    def load_image_ids(self, metadata_format: tuple):
        """Method iterates through imagesets chosen by the user searching for image_ids based on the premise
            that each image_id corresponds to a metadata file. Once a metadata file is found (based on the
            metadata prefix-suffix tuple provided) image_id is extracted from the file
            name and the file is parsed to get tag information. Currently only json metadata files are
            supported in this default implementation.

            If overridden, method is expected to set 'self.tags_df' if wanting to support 'interactive_filter'.
            'self.tags_df' should be set to a pandas dataframe created from a dict with tuple pairs: 
            (imageset_path (Path), image_id (String)) as keys and an array of True/False values for whether 
            the image_id has each corresponding tag. 'self.image_ids' is also expected to be set to a list of 
            image_ids if any other methods need to be used.
        
        Args:
            metadata_format (tuple): prefix-suffix pair of what metadata files look like
        Variables Needed:
            imageset_paths (list): filepaths to all imagesets being looked at (provided by 'create' input)
        """
        # Gets metadata prefix and suffix
        metadata_prefix = metadata_format[0]
        metadata_suffix = metadata_format[1]
        if metadata_suffix != '.json':
            raise Exception("Currently non-json metadata files are not supported for the default loading of image ids")
        
        # Goes through each file in each imageset to search for metadata files
        # metadata files are parsed for tags and filename is parsed for image_id 
        for data_dir in self.imageset_paths:
            for dir_entry in os.scandir(data_dir):
                if not (dir_entry.name.startswith(metadata_prefix) and dir_entry.name.endswith(metadata_suffix)):
                    continue
                image_id = dir_entry.name.replace(metadata_prefix, '').replace(metadata_suffix, '')
                temp = read_json_metadata(dir_entry, image_id)
                self.tags_df = pd.concat((self.tags_df, temp), sort=False)
            self.tags_df = self.tags_df.fillna(False)

        self.image_ids = self.tags_df.index.tolist()

    def interactive_filter(self):
        """Method is expected to only be called after 'load_image_ids' is called, as it relies on 
            'self.tags_df' to be prepopulated. Method prompts user through interactive filtering 
            of image_ids based on their tags.

            If overridden, method is expected to set 'self.image_ids' to whatever image_ids are still
            to be used after filtering. 'self.filter_metadata' also needs to be set to a dict containing
            set-names as keys and lists of image_ids as values.

        Variables Needed:
            tags_df (dataframe): needs to be set for the 'default_filter' function to be able to filter by tags
                (provided by 'load_image_ids')
        """
        self.image_ids = default_filter(self.tags_df, self.filter_metadata)
    
    def write_metadata(self):
        """Method writes out metadata in JSON format in file 'metadata.json',
            in root directory of dataset.

            If overridden, there are no expectations.

        Variables Needed:
            dataset_name (str): the name of the dataset (provided by 'create' input)
            created_by (str): name of who made the dataset (provided by 'create' input)
            comments (str): comments or notes supplied by the user regarding the
                dataset produced by this tool ((provided by 'create' input))
            training_type (str): the training type selected by the user (provided by 'create' input)
            image_ids (list): a list of image IDs that ended up in the final
                dataset (either dev or test) (provided by 'create' input)
            filters (dict): a dictionary representing filter metadata (provided by 'interactive_filter')
            dataset_path (Path): where metadata will be written (provided by 'create' input)
        """
        dataset_path = self.dataset_path / self.dataset_name
        metadata_filepath = dataset_path / 'metadata.json'
        ravenml_patch_filepath = dataset_path / 'ravenml.diff'
        plugin_patch_filepath = dataset_path / 'plugin.diff'

        metadata = {}
        metadata["name"] = self.dataset_name
        metadata["date_created"] = datetime.utcnow().isoformat() + "Z"
        metadata["created_by"] = self.created_by
        metadata["comments"] = self.comments
        metadata["training_type"] = self.plugin_name
        metadata["image_ids"] = [(image_id[0].name, image_id[1]) for image_id in self.image_ids]
        metadata["filters"] = self.filter_metadata
        metadata["ravenml_git_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')

        # Writes patchfile for raven core
        with open(ravenml_patch_filepath, 'w') as f:
            subprocess.call(["git", "diff", "--no-prefix", "-u", "."], stdout=f)

        # Finds file which called 'write_metadata' method, which should be the plugin and changes to that directory
        plugin_file = inspect.getmodule(inspect.stack()[3][0]).__file__
        os.chdir(os.path.dirname(plugin_file))
        metadata["plugin_git_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')

        # Writes patchfile for plugin code
        # Only writes patchfile for diff in plugin folder
        with open(plugin_patch_filepath, 'w') as f:
            subprocess.call(["git", "diff", "--no-prefix", "-u", ".."], stdout=f)

        with open(metadata_filepath, 'w') as outfile:
            json.dump(metadata, outfile)

    def write_dataset(self, associated_files):
        """Method is parent function for writing out complete dataset. Method first
            creates 'test' and 'dev' subsets. The 'test' subset gets all related files
            to it copied into a test folder. The 'dev' subset calls 'write_out_complete_set'
            in the 'splits/complete' directory. Note that prior to this method, obj_dict
            should be set to a list of objects that are meant to be written.

            If overridden, there are no expectations, but note that the variables 'kfolds'
            and 'test_percent' are provided for use.
        
        Args:
            associated_files (list): decides what files are to be copied for the test set

        Variables Needed:
            obj_dict (dict): dict of objects to be written in dataset
            dataset_path (Path): where dataset will be written (provided by 'create' input)
            dataset_name (str): the name of the dataset (provided by 'create' input)
        """
        dataset_path = self.dataset_path / self.dataset_name
        print(dataset_path)

        test_subset, dev_subset = split_data(list(self.obj_dict.items()), test_percent=self.test_percent)
        
        # Test subset
        test_path = dataset_path / 'test'
        self.write_out_test_set(test_path, test_subset, associated_files)

        dev_path = dataset_path / 'splits'

        # standard_path = dev_path / 'standard'
        # write_out_fold(standard_path, fold, is_standard=True)

        complete_path = dev_path / 'complete'
        self.write_out_complete_set(complete_path, [data[1] for data in dev_subset])

    def write_out_test_set(self, path, data, associated_files):
        """Method is helper function for writing out dataset. Writes
            out test set by copying over associated files to the
            specified test path. Assumes objlist has 'image_filepath'
            and 'image_id' as keys.

            If overridden, there are no expectations.

        Args:
            path (Path): Path to where data should be written
            data (list): data that should be written
            associated_files (list): decides what files are to be copied for the test set
        """
        os.mkdir(path)
        test_image_ids = [id[0] for id in data]
        copy_associated_files(test_image_ids, path, associated_files)

    def write_out_complete_set(self, path, data):
        """Method is helper function for writing out dataset. Creates a 
            'train' subdirectory and calls for 'write_out_train_split' to write
            test_data and train_data. test_data is not the test set, but a validation
            set to be used during training.

            If overridden, there are no expectations.

        Args:
            path (Path): Path to where data should be written
            data (list): data that should be written
        """
        data_path = path / 'train'
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        test_data, train_data = split_data(data, test_percent=self.test_percent)

        self.write_out_train_split(train_data, data_path, split_type='train')
        self.write_out_train_split(test_data, data_path, split_type='test')
