"""
Author(s):      Gavin Martin, Carson Schubert (carson.schubert14@gmail.com)
Data Created:   03/18/2019

Wrapper functions for prompting user input via questionary. Stolen from jigsaw.
"""

import sys
from halo import Halo
from questionary import prompt

def in_test_mode():
    """ Determines if we are running in an automated test or not.

    This attribute is set via conftest.py in the ravenml/tests directory
    """
    return hasattr(sys, "_called_from_test")

class Spinner:
    """Wrapper class to prevent bugs with Halo in pytest (see Issue #97)
    """

    def __init__(self, text, text_color):
        self.text = text
        if in_test_mode():
            return
        self._spinner = Halo(text=text, text_color=text_color)

    def start(self):
        if in_test_mode():
            return
        self._spinner.start()

    def succeed(self, text):
        if in_test_mode():
            return
        self._spinner.succeed(text=text)

def user_input(message, default="", validator=None):
    """Prompts the user for input
    
    Args:
        message (str): the message to give to the user before they provide
            input
        default (str, optional): Defaults to "". The default input response
        validator (Validator, optional): Defaults to None. A PyInquirer
            validator used to validate input before proceeding
    
    Returns:
        str: the user's response
    """
    if validator is not None:
        question = [
            {
                "type": "input",
                "name": 'value',
                "message": message,
                "default": default,
                "validate": validator,
            },
        ]
    else:
        question = [
            {
                "type": "input",
                "name": 'value',
                "message": message,
                "default": default
            },
        ]
    answer = prompt(question)
    return answer["value"]

def user_selects(message, choices, selection_type="list", sort_choices=True):
    """Prompts the user to select a choice(s) given a message
    
    Args:
        message (str): the message to give to the user before they choose
        choices (list): a list of the options to provide
        selection_type (str, optional): Defaults to "list". Should be "list"
            or "checkbox" for radio-button-style or checkbox-style selections
        sort_choices (bool, optional): Defaults to True. Whether to
            alphabetically sort the choices in the list provided to the user
    
    Returns:
        str or list: the str for the choice selected if "list" is the 
                        selection_type
                     the list of the choices selected if "checkbox" is the 
                        selection_type
    """
    question = [
        {
            "type": selection_type,
            "name": 'value',
            "message": message,
            "choices": sorted(choices) if sort_choices else choices
        },
    ]
    answer = prompt(question)
    return answer['value']
    
def user_confirms(message, default=False):
    """Prompts the user to confirm an action by typing y/n
    
    Args:
        message (str): the message to give to the user before they choose
        default (bool, optional): Defaults to False.
    
    Returns:
        bool: the user's response in bool format
    """
    question = [
        {
            "type": "confirm",
            "name": "value",
            "message": message,
            "default": default
        },
    ]
    answer = prompt(question)
    return answer["value"]
    
def cli_spinner(text, func, *args):
    """ Halo spinner wrapper
    """
    # spinner = Halo(text=text, text_color="magenta")
    spinner = Spinner(text=text, text_color="magenta")
    spinner.start()
    result = func(*args)
    spinner.succeed(text=spinner.text + 'Complete.')
    return result
    
