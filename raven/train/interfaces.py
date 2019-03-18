'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/03/2019

Contains the classes for interfacing with training plugins.
'''

from raven.utils.question import user_input, user_selects, user_confirms

# placeholder: this will be replaced with calls to AWS to retrieve datasets
def get_datasets():
    return ['a','b','c']
    
class TrainInput(object):
    '''Represents a training input. Contains all plugin-independent information
    necessary for training. Plugins can define their own behavior for getting
    additional information.

    Args:
        inquire: ask user for inputs or not
        **kwargs: should be provided if inquire is set to False
            to populate TrainInput fields

    Attributes:
        dataset: name of the dataset to be used
        artifact_path: path to save artifacts. None if uploading to s3
    
    '''
    def __init__(self, inquire=True, **kwargs):
        if inquire:
            # get dataset
            self._artifact_path = user_input('Enter filepath for artifacts:') if \
                                    user_confirms('Run in local mode?') else None
            self._dataset = user_selects('Choose dataset:', get_datasets())
        else:
            self._dataset = kwargs.get('dataset')
            self._artifact_path = kwargs.get('artifact_path')
    
    def local_mode(self):
        return self.artifact_path is not None

    @property
    def dataset(self):
        return self._dataset
        
    @dataset.setter
    def dataset(self, new_dataset):
        self._dataset = new_dataset
        
    @property
    def artifact_path(self):
        return self._artifact_path
        
    @artifact_path.setter
    def artifact_path(self, new_path):
        self._artifact_path = new_path

class TrainOutput(object):
    '''Training Output class

    Args:

    Attributes:
    
    '''
    def __init__(self):
        pass
        