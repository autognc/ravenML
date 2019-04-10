import sys
import os
import subprocess

from . import object_detection

cwd = os.path.dirname(os.path.abspath(__file__))
if cwd not in sys.path:
    sys.path.append(cwd)
if os.path.join(cwd, 'slim') not in sys.path:
    sys.path.append(os.path.join(cwd, 'slim'))