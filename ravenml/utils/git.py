"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com), Abhi Dhir
Data Created:   11/09/2020

Utility functions for grabbing git information to place into metadata.
"""

import subprocess
import json
import re
from os import chdir, listdir
from pathlib import Path

# look for dist-info or egg-info styles
# raven_dist_info_re = re.compile("(ravenml)-?\d*\.?\d*(.dist-info|.egg-info)")

def is_repo(path: Path) -> bool:
    return '.git' in listdir(path)

def git_sha(path: Path) -> str:
    # store cwd and change to path
    cwd = Path.cwd()
    chdir(path)
    # execute command 
    rev_check = "git rev-parse HEAD"
    # TODO: try except error handling
    out = subprocess.check_output(rev_check.split()).strip().decode('utf-8')
    # restore cwd
    chdir(cwd)
    return out

def git_patch_tracked(path: Path) -> str:
    # store cwd and change to path
    cwd = Path.cwd()
    chdir(path)
    # execute command
    tracked_patch = "git --no-pager diff -u ."
    # TODO: try except error handling
    out = subprocess.check_output(tracked_patch.split()).decode('utf-8')
    # restore cwd
    chdir(cwd)
    return out
    
def git_patch_untracked(path: Path) -> str:
    """ Returns error message if one is received.
    """
    # store cwd and change to path
    cwd = Path.cwd()
    chdir(path)
    # execute command
    git_ls = "git ls-files --others --exclude-standard"
    xargs = "xargs -n 1 git --no-pager diff /dev/null"
    # getting untracked files is a piped operation and thus cannot be done
    # with a simple subprocess.check_output call
    untracked_files = subprocess.check_output(git_ls.split()).decode('utf-8')
    if len(untracked_files) == 0: return ''
    p = subprocess.Popen(xargs.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
    try:
        untracked_patch, err = p.communicate(input=untracked_files.encode(), timeout=5)
    except TimeoutExpired:
        p.kill()
        _, err = p.communicate()
    # restore cwd
    chdir(cwd)
    return untracked_patch.decode('utf-8') if len(err) == 0 else err.decode('utf-8')

# path should be to package root
def retrieve_from_pkg(path: Path):
    with open(path / 'git_info.json', 'w') as f:
        return json.load(f)
    
    # git_info["ravenml_git_sha"] = git.git_sha(rml_dir)
    # git_info["ravenml_tracked_git_patch"] = git.git_patch_tracked(rml_dir)
    # git_info["ravenml_untracked_git_patch"] = git.git_patch_untracked(rml_dir)
    
    # site_packages_dir = path.parent
    # matches = filter(raven_dist_info_re.match, os.listdir(site_packages_dir))
    # print(matches)
