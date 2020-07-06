<!-- [![Build Status](https://travis-ci.com/autognc/ravenML.svg?branch=master)](https://travis-ci.com/autognc/ravenML) -->

# ravenML
CLI tool for machine learning model training.

## Installation 

### PyPI
Install from pip via:
```bash
pip install ravenml
```

### Conda Installation (development)
Create the conda environment from the `environment.yml` file using:
```bash
conda env create -f environment.yml
```

Activate the conda environment with:
```bash
conda activate ravenml      # may require source activate ravenml depending on system setup
```

Install ravenML from the root of this repository using:
```bash
pip install --editable .
```

## Configuration
ravenML must be configured with the name of the S3 buckets you wish to pull [Jigsaw](https://github.com/autognc/jigsaw)-created
datasets from and upload trained models to.

After installation, set this configuration by running:
```bash
ravenml config update
```

You can check your configuration anytime by running `ravenml config show`, and update it anytime with `ravenml config update`.

### Training Plugins
ravenML provides core functionality while unique model training pipelines are implemented
via plugins dynamically loaded at runtime. A default set of plugins is located at
[ravenML-plugins](https://github.com/autognc/ravenML-plugins). See the README there
for more information about how plugins work and how to make your own.

To install all default plugins for use with ravenML you just need to clone the repository
and run a script.

Clone the respository with:
```bash
git clone https://github.com/autognc/ravenML-plugins
```

Install default plugins by navigating to the downloaded `ravenML` directory and using:
```bash
./install_all.sh
```

To test your installation run `ravenml train list` and verify that the training plugin names appear on your console.

## Contributing

### Commitizen
We will use commitizen for all commit messages. The repository is set up to use
commitizen via the `.czrc` file. If you have commitizen already installed globally,
you can use it to commit for this repository.  

If you do not have commitizen installed, follow the instructions on their 
[GitHub](https://github.com/commitizen/cz-cli).  

If you do not have npm installed, you will need to do that before installing commitizen.
npm is distributed with Node.js. Install Node.js [here](https://nodejs.org/en/download/).
