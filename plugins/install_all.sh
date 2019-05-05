#!/usr/bin/env bash

##
# Author(s):        Carson Schubert (carson.schubert14@gmail.com)
# Date Created:     02/25/2019
#
# Install/uninstall script for raven plugins.
# NOTE: This script MUST be run from the plugins directory.
##


set -o errexit      # exit immediately if a pipeline returns non-zero status
set -o pipefail     # Return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, 
                    # or zero if all commands in the pipeline exit successfully.
set -o nounset      # Treat unset variables and parameters other than the special parameters 
                    # ‘@’ or ‘*’ as an error when performing parameter expansion.

# echo "Checking for active raven conda environment..."

# grab available conda envs
# ENVS=$(conda env list | awk '{print $1}' )
# # attempt to source environment
# if [[ $ENVS = *"raven"* ]]; then
#    source activate raven
#    echo "Successfully activated raven environment."
# else 
#    echo "Error: please install the raven conda environment on your system."
#    exit
# fi;

# determine if we are installing or uninstalling
install_flag=d
gpu_flag=d
ec2_flag=d
requirements_prefix="requirements"
while getopts "ugc" opt; do
    case "$opt" in
        c)
            ec2_flag=c
            ;;
        u)
            install_flag=u
            ;;
        g)
            gpu_flag=g
            requirements_prefix="requirements-gpu"
     esac
done

for f in * ; do
    if [ -d ${f} ]; then
        echo "Going on plugin $f..."
        cd $f
        ./install.sh -$install_flag -$gpu_flag
        if [ "$install_flag" = "u" ]; then
            echo "Cleaning up plugin dependencies..."
            pip uninstall -r $requirements_prefix.txt -y
        fi
        cd - > /dev/null
    fi
done



if [ "$ec2_flag" = "d" ]; then
    # ensure raven core environment dependencies are still met
    echo "Checking raven core dependencies..."
    cd ..
    conda env update -f environment.yml
fi
