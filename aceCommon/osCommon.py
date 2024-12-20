from pathlib import Path

def create_file_path_string(list_of_dir=None, base_path_list=None, **kwargs):
    """
    Creates a file path string by combining your current base directory with a list of subdirectories.

    Args:
        list_of_dir (list, optional): 
            List of directory names to append to your path. Defaults to None and will return your working directory 
            in this case.

        base_path_list (list, optional): 
            List of directory names to set your own base directory path. Defaults to None and your working 
            directory will be used as base in this case.

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