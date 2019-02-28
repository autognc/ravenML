##
# Author(s):        Carson Schubert (carson.schubert14@gmail.com)
# Date Created:     02/25/2019
#
# Install/uninstall script for raven plugins.
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
install=1
while getopts "u" opt; do
    case "$opt" in
        u)
            install=0
            ;;
     esac
done

if [ $install -eq 1 ]; then
    for d in */ ; do
        echo "Installing plugin $d..."
        cd $d
        pip install -e .
        cd -
    done
else
    for f in *; do
        if [ -d ${f} ]; then
            echo "Uninstalling plugin $f..."
            pip uninstall $f -y
        fi
    done
fi
