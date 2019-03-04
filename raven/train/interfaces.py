'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/03/2019

Contains the classes for interfacing with training plugins.
'''

from PyInquirer import prompt

# placeholder: this will be replaced with calls to AWS to retrieve datasets
def get_datasets():
    return ['a', 'b', 'c']

class TrainInput(object):
    '''Represents a training input. Contains all plugin-independent information
    necessary for training. Plugins can define their own behavior for getting
    additional information.

    Args:
        inquire: ask user for inputs or not

    Attributes:
        dataset: name of the dataset to be used
        local: run in local mode or not
    
    '''
    def __init__(self, inquire=True):
        if inquire:
            questions = [
                {
                    'type': 'confirm',
                    'message': 'Run in local mode?',
                    'name': 'local',
                    'default': False,
                },
                {
                    'type': 'input',
                    'name': 'artifact_path',
                    'message': 'Enter filepath for artifacts:',
                    'when': lambda answers: answers['local']
                }
            ]
            # add dataset choices
            questions.append({
                    'type': 'list',
                    'name': 'dataset',
                    'message': 'Choose dataset',
                    'choices': get_datasets()
            })
            answers = prompt(questions)
            self._dataset = answers['dataset']
            # path will be None when not in local mode
            self._artifact_path = answers['artifact_path'] if answers['local'] else None
        else:
            self._dataset = 'test'
            self._artifact_path = None
    
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
        