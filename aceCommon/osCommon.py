import os
from pathlib import Path

def create_file_path_string(list_of_dir=None, base_path_list=None, **kwargs):
    """
    Creates a file path string by combining a base directory (as a list) with a list of subdirectories.

    Args:
        list_of_dir (list of str): List of directory names to append to the base path.
        base_path_list (list of str): List of directory names representing the base path.
        **kwargs:
            parent (int): Number of parent directories to go up from the current file.
            ace_parent (int): Number of parent directories to go up from the aceCommon package location.

    Returns:
        str: The constructed file path string.
    """
    # Default list of directories
    if list_of_dir is None:
        list_of_dir = ['']

    # Determine the base path
    if base_path_list:
        # Convert the list_for_base_path into an absolute path
        dir_name = Path(*base_path_list)
    elif 'parent' in kwargs:
        parent_level = kwargs['parent']
        dir_name = Path.cwd().parents[parent_level]
    elif 'ace_parent' in kwargs:
        # Get the aceCommon package location
        dir_name = Path(__file__).parents[kwargs['ace_parent']]
    else:
        # Default to current working directory
        dir_name = Path.cwd()

    # Construct the full path
    for item in list_of_dir:
        dir_name = dir_name / item

    return str(dir_name)