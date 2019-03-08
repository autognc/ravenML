# Raven Training Plugins
Default training plugins for Raven, and examples for making your own plugins.

## Structure
All plugins are independent and separate Python packages with the following structure:
```
raven_package_name/                   # name of the package, with underscores
    raven_package_name/               # ''
        __init__.py             
        core.py                 # core of plugin - contains command group 
                                    entire plugin flows from
    install.sh                  # install script for the plugin
    requirements.in             # user created requirements file for CPU install
    requirements-gui.in         # user created requirements file for GPU install
    requirements.txt            # pip-compile created requirements file for CPU install
    requirements-gpu.txt        # pip-compile created requirements file for GPU install
    setup.py                    # python package setuptools
```
Additional files, directories, and modules can be created as needed. Just be sure to include
an `__init__.py` in every directory you create, and think in modules.

## Requirements Scheme
In order to support both GPU and CPU installs, each plugin will depend on
requirements files rather than packages in `install_requires` in `setup.py`. 
We use [pip-compile](https://github.com/jazzband/pip-tools) to maintain all requirements with
uninstall functionality. Developers should create **two files**:
1. requirements.in
2. requirements-gpu.in

These files are manually maintained and include all python packages which the plugin
depends on (such as tensorflow, pytorch, etc). Crucially, they do **not** contain 
these packages' dependencies. `pip-compile` is then used on the `.in` files to create
two files:
1. requirements.txt
2. requirements-gpu.txt

Which are created by the command:
```
pip-compile --out-file <prefix>.txt <prefix>.in
```

### install.sh
An `install.sh` script should be written to handle all install logic (including updating pip-compile created requirements files) and ensure 
external dependenices (such as NVIDIA Drivers or additional packages) are met on install. When uninstalling, this script
should **only** handle the uninstall logic for the package itself, not its dependenices. The reason for the difference in 
behavior between install and uninstall is simple: Because many
plugins will have similar dependencies, which themselves share dependencies, we cannot safely remove
all of an individual plugin's dependenices without uninstalling all plugins. What this means for plugins in this directory:
- Plugins can be installed individually using their respective `install.sh` script.
- Plugins can also be installed en masse using `install_all.sh` at the root of this directory.
- Plugins can **exclusively** be uninstalled en masse using `install_all.sh` at the root of this directory.
If you uninstall a plugin individually using its `install.sh` script, you will **only** be uninstalling the plugin itself;
none of its dependencies will be cleaned up. This should be avoided to prevent creating a bloated environment.

All `install.sh` scripts should support two flags:
- `-u`: uninstall. Passed to uninstall the plugin itself.
- `-g`: GPU install. Can be paired with `-u` for uninstalling a GPU install.

### install_all.sh
Installs all plugins in this directory using their `install.sh` scripts. Mostly a convenience item when installing.
When uninstalling, this script should be used **exclusively** in place of any individual plugin's `install.sh` script.
It supports the same two flags as any `install.sh`:
- `-u`: uninstall. Passed to uninstall all plugins, including all plugin dependencies.
- `-g` GPU install. Can be paired with `-g` for uninstalling a GPU install.

`install_all.sh` contains logic to ensure that if any plugins share dependencies with Raven core these dependencies
remain met at the compeition of the pluigin uninstall. This is accomplished by verifying the environment against its
`environment.yml` file once `install.sh -u` script is run for each plugin.

## Making a Plugin

Follow these steps to create a plugin.

### 1. Create file structure.
Every Raven training plugin will begin with the following file structure:
```
raven_<plugin_name>/                   # name of the package, with underscores
    raven_<plugin_name>/               # ''
        __init__.py             
        core.py                 # core of plugin - contains command group 
                                    entire plugin flows from
    install.sh                  # install script for the plugin
    requirements.in             # user created requirements file for CPU install
    requirements-gpu.in         # user created requirements file for GPU install
    setup.py                    # python package setuptools
```

We will go through each of these files individually.

#### Inner `raven_<plugin_name>/` directory
Contains the source code for the plugin itself. Inside are two files:
1. `__init__.py`: empty file which marks this at a python module.
2. `core.py`: core of the plugin where the top level command group is located. Go from the skeleton below:
```python
import click
from raven.train.options import kfold_opt, pass_train
from raven.train.interfaces import TrainInput, TrainOutput

@click.group(help='Top level command group description')
@click.pass_context
@kfold_opt
def <plugin_name>(ctx, kfold):
    pass
    
@<plugin_name>.command()
@pass_train
@click.pass_context
def train(ctx, train: TrainInput):
    # If the context (ctx) has a TrainInput already, it is passed as "train"
    # If it does not, the constructor is called AUTOMATICALLY
    # by Click because the @pass_train decorator is set to ensure
    # object creation, after which the created object is passed as "train"
    # after training, create an instance of TrainOutput and return it
    result = TrainOutput()
    return result               # return result back up the command chain
```
`TrainInput` and `TrainOutput` are described in detail in the [Interfaces](#standard-interfaces) section.

#### `setup.py`
Contains setuptools code for turning this plugin into a python package. Go from the skeleton below:
```python
from setuptools import setup

setup(
    name='raven_<plugin_name>',
    version='0.1',
    description='Training plugin for raven',
    packages=['raven_<plugin_name>'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [raven.plugins.train]
        <plugin_name>=raven_<plugin_name>.core:<plugin_name>
    '''
)
```

#### `requirements.in` and `requirements-gpu.in`
Contain all plugin Python dependencies. These should be manually created and updated.
It is expected that these will largely overlap - however, keeping them separate is the
cleanest way of doing things. Write these files exactly as you would a normal `requirements.txt`.
There is no skeleton for these files. See [requirements](https://pip.pypa.io/en/stable/user_guide/#requirements-files) 
information here.

#### `install.sh`
See [install.sh](#installsh) section for description. Go from the skeleton below:
```shell
#!/usr/bin/env bash

set -o errexit      # exit immediately if a pipeline returns non-zero status
set -o pipefail     # Return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, 
                    # or zero if all commands in the pipeline exit successfully.
set -o nounset      # Treat unset variables and parameters other than the special parameters 
                    # ‘@’ or ‘*’ as an error when performing parameter expansion.

# parse flags
install=1
requirements_prefix="requirements"
while getopts "ugd" opt; do
    case "$opt" in
        u)
            install=0
            ;;
        g)
            requirements_prefix="requirements-gpu"
            echo "-- GPU mode!"
            ;;
     esac
done

if [ $install -eq 1 ]; then
    echo "Installing..."
    pip-compile --output-file $requirements_prefix.txt $requirements_prefix.in
    pip install -r $requirements_prefix.txt
else
    # NOTE: this does NOT clean up after the plugin (i.e, leaves plugin dependenices installed)
    # To clean up, use the install_all.sh script at the root of the plugins/ directory
    echo "Uninstalling..."
    pip uninstall <plugin_name> -y
fi

```

### 2. Write plugin specific code.
Create additional files, directories, and modules as needed. Just be sure to include
an `__init__.py` in every directory you create, and think in modules.  

Consider creating a separate directory for each sub command group, structured as:
```
<command_group_name>/
    __init__.py
    commands.py
```

Go from the skeleton below for `commands.py`:
```python
import click

### OPTIONS ###
# put all local command options here


### COMMANDS ###
@click.group()
@click.pass_context
def <command_group_name>(ctx):
    pass

@<command_group_name>.command()
def <command_name>():
    click.echo('Sub command group command here!')
```

Within this directory you can create an `interfaces.py` file for any interfaces you want to expose
from the command and an `options.py` file for any command options you want to expose.

To import this sub command group in `<plugin_name>/<plugin_name>/core.py` you would put the following lines:
```python
from <plugin_name>.<command_group_name>.commands import <command_group_name>

<plugin_name>.add_command(<command_group_name>)
```

### 3. Install plugin
**NOTE** You must be inside the Raven anaconda environment when performing this operation.

Install the plugin using `install.sh`, using the `-g` flag if appropriate. At this point, if you run
`pip list` you should see your plugin listed, with the underscores in its named replaced by dashes.

At this point, your plugin should automatically load inside of Raven. Run `raven train list` to see 
all installed plugins and verify that yours appears.

### 4. (Optional) Test uninstalling plugin
It is a good idea to test that your plugin can be properly uninstalled as well. Recall that to uninstall a plugin
added to the Raven `plugins/` directory, you **must** use the `install_all.sh` script with the `-u` flag. 

Note that if plugins are created outside of the `plugins/`, directory they cannot be uninstalled using the 
`install_all.sh` script. There is no easy solution for this. It is up to the user to either leave plugin 
dependencies installed in the environment, write additional scripts to ensure plugin depenency removal does 
not impact other plugins, or some other manual solution.

## Standard Interfaces
Two classes define the **standard interface** between Raven core and training plugins:
- `TrainInput`
- `TrainOutput`

Import them with the following code (also seen in the [example](#inner-raven_plugin_name-directory) for `core.py`):
```python
from raven.train.interfaces import TrainInput, TrainOutput
```

### TrainInput
Class whose objects contain all necessary information for a training plugin to actually train. 

### TrainOutput
Class whose objects contain all necessary information for Raven core to process and save or upload training artifacts.
