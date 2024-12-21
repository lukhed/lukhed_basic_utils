from pathlib import Path
import os

def create_file_path_string(list_of_dir=None, base_path_list=None, **kwargs):
    """
    Constructs a file path string by combining a base directory with a list of subdirectories.

    Args:
        list_of_dir (list, optional): 
            A list of subdirectory names to append to the base path. If None, defaults to an empty list,
            which will return the base directory as-is.
        base_path_list (list, optional): 
            A list of directory names defining the base path. If None, the current working directory
            is used as the base path.
        **kwargs: 
            Additional options for defining the base path:
                - parent (int): Number of parent directories to go up from the current working directory.
                - ace_parent (int): Number of parent directories to go up from the location of this script.

    Returns:
        str: The constructed file path as a string.

    Examples:
        Using the current working directory as the base path:
        ```python
        create_file_path_string(list_of_dir=["subdir", "file.txt"])
        # Output: "<current_working_directory>/subdir/file.txt"

        Specifying a custom base path:
        ```python
        create_file_path_string(
            list_of_dir=["documents"],
            base_path_list=["C:", "Users", "username"]
        )
        # Output: "C:/Users/username/documents"

        Using a parent directory as the base:
        ```python
        create_file_path_string(list_of_dir=["config"], parent=1)
        # Output: "<parent_directory>/config"
        ```
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

def append_to_dir(dir_path_to_add_to, to_append):
    """
    Appends a subdirectory or subdirectories to a given directory path.

    Args:
        dir_path_to_add_to (str): The base directory path to which subdirectories will be added.
        to_append (str or list): A single directory (str) or multiple directories (list) to append.

    Returns:
        str: The full path with the appended subdirectories.

    Example:
        ```python
        dir_path_to_add_to = "C:/users/test"
        to_append = ["documents", "pictures"]
        result = append_to_dir(dir_path_to_add_to, to_append)
        print(result)  # Output: "C:/users/test/documents/pictures"
        ```
    """
    if type(to_append) == list:
        for dir_name in to_append:
            dir_path_to_add_to = os.path.join(dir_path_to_add_to, dir_name)
        return dir_path_to_add_to
    else:
        return os.path.join(dir_path_to_add_to, to_append)