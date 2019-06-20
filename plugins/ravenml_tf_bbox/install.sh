#!/usr/bin/env bash

##
# Author(s):        Carson Schubert (carson.schubert14@gmail.com)
# Date Created:     03/07/2019
#
# Install/uninstall script for raven TensorFlow Bounding Box plugin.
##


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
    
    # install protoc on system if necessary
    if [ ! $(which protoc) ]; then
        if [ $(uname) == 'Linux' ]; then
            PROTOC_ZIP=protoc-3.7.1-linux-x86_64.zip
            curl -OL https://github.com/google/protobuf/releases/download/v3.7.1/$PROTOC_ZIP
            if [ `whoami` != 'root' ]
                then
                    sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
                    sudo unzip -o $PROTOC_ZIP -d /usr/local include/*

                else
                    unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
                    unzip -o $PROTOC_ZIP -d /usr/local include/*
            fi
            
            rm -f $PROTOC_ZIP 
        elif [ $(uname) == 'Darwin' ]; then
            PROTOC_ZIP=protoc-3.7.1-osx-x86_64.zip
            curl -OL https://github.com/google/protobuf/releases/download/v3.7.1/$PROTOC_ZIP
            sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
            sudo unzip -o $PROTOC_ZIP -d /usr/local include/*
            rm -f $PROTOC_ZIP
        else
            echo 'Your system is not supported! Only Linux and macOS (Darwin) are supported.'
            exit 1
        fi
    fi

    # pycocotools requires two libraries be installed PRIOR to running its setup.py
    pip install numpy cython
    pip-compile --output-file $requirements_prefix.txt $requirements_prefix.in
    pip install -r $requirements_prefix.txt
    pip install -e .
else
    # NOTE: this does NOT clean up after the plugin (i.e, leaves plugin dependenices installed)
    # To clean up, use the install_all.sh script at the root of the plugins/ directory
    echo "Uninstalling..."
    pip uninstall ravenml-tf-bbox -y
fi


