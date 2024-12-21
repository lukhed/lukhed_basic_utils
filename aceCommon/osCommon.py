from pathlib import Path
import os
import platform
import shutil
import sys

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
    
def return_immediate_child_dirs_given_dir(full_dir_path):
    return [f.path for f in os.scandir(full_dir_path) if f.is_dir()]
    
def return_files_in_dir_as_strings(dir_path):
    # returns files in a directory in a list of strings
    file_list = list()

    for file in os.listdir(dir_path):
        file_list.append(os.fsdecode(file))

    file_list = [append_to_dir(dir_path, x) for x in file_list]

    if "linux" in platform.system().lower():
        file_list.sort()

    return file_list

def check_if_dir_exists(full_path):
    # Checks if dir exists
    if os.path.isdir(full_path):
        return True
    else:
        return False

def create_dir(full_path):
    # takes full path and creates the directory.
    os.mkdir(full_path)

def check_create_dir_structure(dirPathList, full_path=False, **kwargs):
    # takes in a dir path list (where the list starts from the first folder to check from root)
    # check if dirs in the list exist
    # if dir doesn't exist, create it.
    # return number of dirs created as int
    # kwargs: return_path = 1 (this returns the path that was checked or created)

    path_flag = 0
    if 'return_path' in kwargs:
        path_flag = 1

    if full_path:
        dirsCreated = 0
        tPath = dirPathList
        if not check_if_dir_exists(dirPathList):
            create_dir(dirPathList)
            dirsCreated = 1
    else:
        pathList = list()
        i = 0
        dirsCreated = 0
        while i < len(dirPathList):
            pathList.append(dirPathList[i])
            tPath = create_file_path_string(pathList)

            if os.path.isdir(tPath):
                pass
            else:
                os.mkdir(tPath)
                dirsCreated = dirsCreated + 1

            i = i + 1

    if path_flag == 1:
        return tPath
    else:
        return dirsCreated
    
def get_most_recently_modified_file_in_path_list(file_list):
    modified_list = list()
    for f in file_list:
        modified_list.append(os.path.getmtime(f))

    max_index = modified_list.index(max(modified_list))
    return file_list[max_index]

def check_if_file_exists(full_path):
    if os.path.isfile(full_path):
        return True
    else:
        return False

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def delete_directory_with_contents(filePath):
    if os.path.exists(filePath):
        shutil.rmtree(filePath)
        return 'success'
    return 'failed: file DNE'

def copy_directory_with_contents(source_full_path, destination_full_path):
    # copies an entire directory with all contents and returns the destination path
    return shutil.copytree(source_full_path, destination_full_path)

def block_print():
    # call to block prints
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    # call to restore prints
    sys.stdout = sys.__stdout__

def copy_file(source_file, dest_file):
    try:
        shutil.copyfile(source_file, dest_file)
        return 'success'
    except:
        return 'failed'

def create_root_path_starting_from_drive(root_drive_str):
    # takes a root drive and makes a path that you can start building on with other functions of this module
    # Example: root_drive = "C:"
    root_drive = os.path.join(root_drive_str, os.sep)
    return root_drive

def extract_file_name_given_full_path(full_path):
    return os.path.basename(full_path)

def get_last_folder_from_path(full_path):
    without_extra_slash = os.path.normpath(full_path)
    last_part = os.path.basename(without_extra_slash)
    return last_part

def get_parent_dir_given_full_dir(full_dir_path):
    return os.path.dirname(full_dir_path)

def get_working_dir():
    return os.getcwd()

def is_platform_windows():
    """
    return: bool()
    """

    if os.name == "nt":
        return True
    else:
        return False
