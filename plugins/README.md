# Raven Training Plugins
Default training plugins for Raven, and examples for making your own plugins.

## Structure
All plugins are independent and separate Python packages.
```
package_name/                   # name of the package, with underscores
    package_name/               # ''
        __init__.py             
        core.py                 # core of plugin - contains command group 
                                    entire plugin flows from
    install.sh                  # install script for the plugin
    requirements.in             # user created requirements file for CPU install
    requirements-gui.in         # user created requirements file for GPU install
    requirements.txt            # pip-compile created requirements file for CPU install
    requirements-gui.txt        # pip-compile created requirements file for GPU install
    setup.py                    # python package setuptools
```
Additional files, directories, and modules can be created as needed. Just be sure to include
an `__init__.py` in every directory you create, and think in modules.

### Requirements Structure
In order to support both GPU and CPU installs, each plugin will depend on
requirements files rather than packages in `install_requires` in `setup.py`. 
We use [pip-compile](https://github.com/jazzband/pip-tools) to maintain all requirements with
uninstall functionality. Developers should create **two files**:
1. requirements.in
2. requirements-gui.in

These files are manually maintained and include all python packages which the plugin
depends on (such as tensorflow, pytorch, etc). Crucially, they do **not** contain 
these packages' dependencies. `pip-compile` is then used on the `.in` files to create
two files:
1. requirements.txt
2. requirements-gui.txt

Which are created by the command:
```
pip-compile --out-file <prefix>.txt <prefix>.in
```

### install.sh
An `install.sh` script should be written to handle the pip-compile logic and ensure that any
external dependenices (such as NVIDIA Drivers or additional packages) are met. This script
should **only** handle the uninstall logic for the package itself, not its dependenices. Because many
plugins will have similar dependencies, which themselves share dependencies, we cannot safely remove
individual plugin dependenices without uninstall all plugins. What this means for plugins in this directory:
- Plugins can be installed individually using their respective `install.sh` script.
- Plugins can also be installed en masse using `install_all.sh` at the root of this directory.
- Plugins can **exclusively** be uninstalled en masse using `install_all.sh` at the root of this directory.

All `install.sh` scripts should support two flags:
- **-u**: uninstall. Passed to uninstall the plugin itself.
- **-g**: GPU install. Can be paired with `-u` for uninstalling a GPU install.

## Making a Plugin

**test** * is my `test` 
