[![Build Status](https://travis-ci.com/autognc/ravenML.svg?branch=master)](https://travis-ci.com/autognc/ravenML)

# raven
Training CLI Tool

## Installation with Conda
Create the conda environment from the `environment.yml` file using:
```bash
conda env create -f environment.yml
```

Activate the conda environment with:
```bash
conda activate raven # may require source activate raven on some systems
```

Install raven from the root of this repository using:
```bash
pip install --editable .
```

Install default plugins by navigating to the `plugins/` directory and using:
```bash
./install_all.sh
```

## Commitizen
We will use commitizen for all commit messages. The repository is set up to use
commitizen via the `.czrc` file. If you have commitizen already installed globally,
you can use it to commit for this repository.  

If you do not have commitizen installed, follow the instructions on their 
[GitHub](https://github.com/commitizen/cz-cli).  

If you do not have npm installed, you will need to do that before installing commitizen.
npm is distributed with Node.js. Install Node.js [here](https://nodejs.org/en/download/).
