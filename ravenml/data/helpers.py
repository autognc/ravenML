import os
import shutil
import pandas as pd
import json
import sys
from random import shuffle
from queue import Queue
from threading import Thread
from pathlib import Path
from colorama import Fore
from ravenml.utils.question import cli_spinner, user_selects, user_confirms, user_input
from ravenml.utils.config import get_config

def default_filter(tags_df, filter_metadata):
    """Method leads user through interactive filtering through image_ids based on 
        image tags

    Args:
        tags_df (DataFrame): a pandas DataFrame storing image IDs and
            associated tags; its structure is:
                index (rows) = image ID (str)
                column headers = the tags themselves
                columns = True/False values for whether the image has the tag
                    in that column header
        filter_metadata (dict): dict which will hold the sets that is created
            through the filtering process
    """
    sets = {}
    # outer loop to determine how many sets the user will create
    try:
        while True:
            subset = tags_df
            this_group_filters = []
            len_subsets = [len(subset)]
            # inner loop to handle filtering for ONE set
            while True:

                # if filters have been applied, display them to the user
                # to help guide their next choice
                if len(this_group_filters) > 0:
                    filters_applied = [
                        "   > " + (" " + f["type"] + " ").join(f["tags"]) +
                        " ({} -> {})".format(len_subsets[i],
                                            len_subsets[i + 1])
                        for i, f in enumerate(this_group_filters)
                    ]
                    print(Fore.MAGENTA + "ℹ Filters already applied:\n{}".
                        format("\n".join(filters_applied)))

                selected_tags = user_selects(
                    message=
                    "Please select a set of tags with which to apply a filter:",
                    choices=list(tags_df),
                    selection_type="checkbox")
                filter_type = user_selects(
                    message=
                    "Which filter would you like to apply to the above set?",
                    choices=["AND (intersection)", "OR (union)"],
                    selection_type="list")

                if filter_type == "AND (intersection)":
                    subset = and_filter(subset, selected_tags)
                    this_group_filters.append({
                        "type": "AND",
                        "tags": selected_tags
                    })
                elif filter_type == "OR (union)":
                    subset = or_filter(subset, selected_tags)
                    this_group_filters.append({
                        "type": "OR",
                        "tags": selected_tags
                    })
                print(
                    Fore.GREEN +
                    "ℹ There are {} images that meet the filter criteria selected."
                    .format(len(subset)))
                len_subsets.append(len(subset))

                if not user_confirms(
                        message=
                        "Would you like to continue filtering this set?",
                        default=False):
                    set_name = user_input(
                        message="What would you like to name this set?")
                        # validator=FilenameValidator)
                    sets[set_name] = subset
                    filter_metadata["groups"].append({
                        "name":
                        set_name,
                        "filters":
                        this_group_filters
                    })
                    break
                
            if not user_confirms(
                    message=
                    "Would you like to create more sets via filtering?",
                    default=False):
                break

        sets_to_join = []
        for set_name, set_data in sets.items():
            how_many = user_input(
                message=
                'How many images of set "{}" would you like to use? (?/{})'
                .format(set_name, len(set_data)),
                # validator=IntegerValidator,
                default=str(len(set_data)))
            n = int(how_many)
            sets_to_join.append(
                set_data.sample(n, replace=False, random_state=42))

            # find the right group within the metadata dict and add the number
            # included to it
            for group in filter_metadata["groups"]:
                if group["name"] == set_name:
                    group["number_included"] = n

        return join_sets(sets_to_join).index.tolist()

    except Exception as e:
        print(e)
        sys.exit(1)

def and_filter(tags_df, filter_tags):
    """Filters out a set of images based upon the intersection of its tag values
    
    NOTE: With an AND (intersection) filter, an image must possess all tags in
    the `filter_tags` list in order to pass the filter.

    Args:
        tags_df (DataFrame): a pandas DataFrame storing image IDs and
            associated tags; its structure is:
                index (rows) = image ID (str)
                column headers = the tags themselves
                columns = True/False values for whether the image has the tag
                    in that column header
        filter_tags (list): a list of str values for the tags that should be
            used to apply the filter
    
    Returns:
        DataFrame: a subset of the input DataFrame with those images that
            passed the AND filter remaining
    """
    subset = tags_df
    for tag in filter_tags:
        subset = subset[subset[tag]]
    return subset

def or_filter(tags_df, filter_tags):
    """Filters out a set of images based upon the union of its tag values
    
    NOTE: With an OR (union) filter, an image must possess at least one tag in
    the `filter_tags` list in order to pass the filter.

    Args:
        tags_df (DataFrame): a pandas DataFrame storing image IDs and
            associated tags; its structure is:
                index (rows) = image ID (str)
                column headers = the tags themselves
                columns = True/False values for whether the image has the tag
                    in that column header
        filter_tags (list): a list of str values for the tags that should be
            used to apply the filter
    
    Returns:
        DataFrame: a subset of the input DataFrame with those images that
            passed the OR filter remaining
    """
    result = pd.DataFrame()
    for tag in filter_tags:
        subset = tags_df[tags_df[tag]]
        result = pd.concat((result, subset), sort=False)
    result = result.reset_index().drop_duplicates(
        subset='index', keep='first').set_index('index')
    return result

def join_sets(sets):
    """Returns the union of a set of datasets
    
    NOTE: this function removes duplicates, so it is possible to end up with a
    smaller number of items than are given as inputs.

    Args:
        sets (list): a list of datasets that should be merged into one (the
            union of all datasets); each element of the list is a DataFrame
            in the format:
                index (rows) = image ID (str)
                column headers = the tags themselves
                columns = True/False values for whether the image has the tag
                    in that column header
    
    Returns:
        DataFrame: a DataFrame that represents the union of all of the input
            DataFrames with duplicates removed; it stores image IDs and 
            associated tags in the format:
                index (rows) = image ID (str)
                column headers = the tags themselves
                columns = True/False values for whether the image has the tag
                    in that column header
    """
    result = pd.DataFrame()
    for group in sets:
        result = pd.concat((result, group), sort=False)
    result = result.reset_index().drop_duplicates(
        subset='index', keep='first').set_index('index')
    return result

def copy_associated_files(images: list, destination_dir: Path, associated_files: list, num_threads=20):
    """Copies files associated with provided image list into a destination 
        directory locally
    
    Args:
        images (list): list of tuples with paths to a local directory paired 
            with an image id located in that directory
        destination_dir (Path): directory where data will be copied to
        associated_files (list): expected to be tuples of prefix-suffix pairs
            (prefix (str), suffix (str)),
            any number of list entries is allowed, but all associated files must
            be present, including metadata files
        num_threads (int, optional): Defaults to 20. Number of threads
            performing concurrent copies.
    """

    # function used to copy
    def copy_object(queue):
        while True:
            filepath = queue.get()
            if filepath is None:
                break
            shutil.copy(filepath, destination_dir.absolute())
            queue.task_done()

    # create a queue for objects that need to be copied
    # and spawn threads to copy them concurrently
    copy_queue = Queue(maxsize=0)
    workers = []
    for worker in range(num_threads):
        worker = Thread(target=copy_object, args=(copy_queue, ))
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)

    # gets all associated prefix-suffix pairs from 
    # associated_files list 
    file_types = set(associated_files)

    # iterates through each image path, and copies each associated file
    for image in images:
        for file_type in file_types:
            filepath = image[0] / str(file_type[0] + image[1] + file_type[1])
            if os.path.isfile(filepath):
                copy_queue.put(filepath.absolute())

    # joins all threads
    copy_queue.join()
    for _ in range(num_threads):
        copy_queue.put(None)
    for worker in workers:
        worker.join()

def split_data(obj_list, test_percent=.2):
    """Splits obj_list into test/dev sets
    
    Args:
        obj_list (list): list of objects to divide into test/dev
        test_percent (int): percentage of objects in the test set
    
    Returns:
        tuple of two lists. The first list is test, second dev
    """
    if len(obj_list) == 0:
        raise Exception("Empty object list passed.")
    if len(obj_list) == 1:
        raise Exception(
            "Object list of length 1 passed. Can't build test and dev set with this."
        )

    shuffle(obj_list)
    index_to_split_on = max(1, int(len(obj_list) * test_percent))

    test = obj_list[:index_to_split_on]
    dev = obj_list[index_to_split_on:]

    return (test, dev)

def read_json_metadata(dir_entry, image_id):
    """Reads a json metadata file and creates a dataframe
        with the tags found in the metadata
    
    Args:
        dir_entry (Path): path to metadata file
        image_id (String): image_id of metadata file
    
    Returns:
        dataframe with image_id key and True/False values
        for each tag.
    """
    with open(dir_entry.path, "r") as read_file:
        data = json.load(read_file)
    tag_list = data.get("tags", ['untagged'])
    if len(tag_list) == 0:
        tag_list = ['untagged']
    
    return pd.DataFrame(dict(zip(tag_list, [True] * len(tag_list))), index=[(Path(os.path.dirname(dir_entry)), image_id)])
