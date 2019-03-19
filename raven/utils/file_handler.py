'''
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   03/18/2019

Handles local file caching for raven.
'''

import os
import shutil
import click
from pathlib import Path

RAVEN_LOCAL_STORAGE_PATH = Path(os.path.expanduser('~/.raven-ml'))

def create():
    os.mkdir(RAVEN_LOCAL_STORAGE_PATH)

def exists():
    return os.path.exists(RAVEN_LOCAL_STORAGE_PATH)

def ensure_exists():
    if not exists():
        create()

def subpath_exists(subpath):
    return os.path.exists(RAVEN_LOCAL_STORAGE_PATH / Path(subpath))

def ensure_subpath_exists(subpath):
    if not subpath_exists(subpath):
        make_subpath(subpath)

def make_subpath(subpath):
    os.mkdir(RAVEN_LOCAL_STORAGE_PATH / Path (subpath))
    
def clean():
    try:
        shutil.rmtree(RAVEN_LOCAL_STORAGE_PATH)
    except FileNotFoundError:
        click.echo('Nothing to clean.')
