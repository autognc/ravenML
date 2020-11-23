"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com), Abhi Dhir
Data Created:   11/09/2020

Utility functions for grabbing git information to place into metadata.
"""

import subprocess
import json
from os import chdir, listdir
from pathlib import Path

def is_repo(path: Path) -> bool:
    """ Checks if the given path is in a github repository by detecting a .git directory.
    
    Starting at the given path, the tree is traversed recursively until the .git is found,
    or the root of the file tree is reached.

    Args:
        path (Path): path to a directory
    
    Returns:
        str: path to root of the repository, None otherwise
    """
    parent_path = path.parent
    while path != parent_path:
        if (path / '.git').exists():
            return path
        path = parent_path
        parent_path = path.parent
    return None

def git_sha(path: Path) -> str:
    """ Find SHA hash of the current HEAD in the repository. 

    This function catches all exceptions to make it safe to call at the end of
    dataset creation or model training.

    Args:
        path (Path): path to a directory inside a git repo
    
    Returns:
        str: SHA hash of current HEAD, or error message if unable to execute cmd
    """
    # store cwd and change to path
    cwd = Path.cwd()
    chdir(path)
    # execute command 
    rev_check = "git rev-parse HEAD"
    try:
        out = subprocess.check_output(rev_check.split()).strip().decode('utf-8')
    except Exception as e:
        out = str(e)
    # restore cwd
    chdir(cwd)
    return out

def git_patch_tracked(path: Path) -> str:
    """ Generate a patchfile of the diff for all tracked files in the repo

    This function catches all exceptions to make it safe to call at the end of
    dataset creation or model training
    
    Args:
        path (Path): path to a directory inside a git repo. Unless you have a reason
            not to, this should be the root of the repo for maximum coverage
    
    Returns:
        str: patchfile for tracked files, or error message if unable to excecute cmd
    """
    # store cwd and change to path
    cwd = Path.cwd()
    chdir(path)
    # execute command
    tracked_patch = "git --no-pager diff -u ."
    try:
        out = subprocess.check_output(tracked_patch.split()).decode('utf-8')
    except Exception as e:
        out = str(e)
    # restore cwd
    chdir(cwd)
    return out
    
def git_patch_untracked(path: Path) -> str:
    """ Generate a patchfile of the diff for all untracked files in the repo
    
    This function catches all exceptions to make it safe to call at the end of
    dataset creation or model training
    
    Args:
        path (Path): path to a directory inside a git repo. Unless you have a reason
            not to, this should be the root of the repo for maximum coverage
    
    Returns:
        str: patchfile for untracked files, or error message if unable to execute cmd
    """
    # store cwd and change to path
    cwd = Path.cwd()
    chdir(path)
    # execute command
    git_ls = "git ls-files --others --exclude-standard"
    xargs = "xargs -n 1 git --no-pager diff /dev/null"
    # getting untracked files is a piped operation and thus cannot be done
    # with a simple subprocess.check_output call
    try:
        untracked_files = subprocess.check_output(git_ls.split()).decode('utf-8')
        if len(untracked_files) == 0: 
            chdir(cwd)
            return ''
        p = subprocess.Popen(xargs.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        try:
            untracked_patch, err = p.communicate(input=untracked_files.encode(), timeout=5)
        except TimeoutExpired:
            p.kill()
            _, err = p.communicate()
    except Exception as e:
        # encode so return line works
        err = str(e).encode(encoding='UTF-8')
    # restore cwd
    chdir(cwd)
    return untracked_patch.decode('utf-8') if len(err) == 0 else err.decode('utf-8')

def retrieve_from_pkg(path: Path):
    """ Retrieves git information from the installed package location if possible.

    Git information will be stored in the package root in "git_info.json" in case of
    git clone install and PyPI install.

    Args:
        path (Path): path within the installed package location

    Returns:
        dict: dictionary of git information. Empty if none found.
    """
    parent_path = path.parent
    # recursively move up the file tree until the file is found or deemed not present
    while path != parent_path and path.name != 'site-packages':
        git_info_path = path / 'git_info.json'
        if git_info_path.exists():
            with open(git_info_path, 'r') as f:
                return json.load(f)
        path = parent_path
        parent_path = path.parent
    return {}
    