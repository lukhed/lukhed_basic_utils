from lukhed_basic_utils import osCommon as osC
from lukhed_basic_utils import fileCommon as fC
from github import Github
from github.Repository import Repository
from github.GithubException import UnknownObjectException
import json
from typing import Optional

class GithubHelper:
    def __init__(self, project='your_project_name', repo_name=None, set_config_directory=None):
        """
        A helper class for interacting with GitHub repositories, handling authentication, 
        and various file operations within a repository.

        Upon instantiation, the class checks for an existing GitHub configuration file
        (`githubConfig.json`) in the lukhed config directory. If a valid configuration
        does not exist, it guides you through creating one, storing the credentials locally.
        Once configurted, the class can then authenticate with GitHub using a personal access token
        associated with a specific project.

        Parameters:
            project (str, optional): Name of the project to activate. Defaults to
                'your_project_name'. Project names are not case sensitive.
            repo_name (str, optional): Name of the repository to activate immediately
                after instantiation. Defaults to None.
            set_config_directory (str, optional): Full path to the directory that contains your GithubHelper config 
                file (token file). Default is None and this class will create a directory in your working directory 
                called 'lukhedConfig' to store the GithubHelper config file.

        Attributes:
            _resource_dir (str): Path to the lukhed config directory.
            _github_config_file (str): Full path to the `githubConfig.json` file containing
                user tokens for various projects.
            _github_config (list): Loaded GitHub configuration data (list of dictionaries),
                each containing a "project" and "token" key.
            user (str | None): Authenticated GitHub username, set upon successful authentication.
            project (str | None): Currently active project name (lowercase).
            repo (github.Repository.Repository | None): GitHub repository object for the
                active repository, if any.
            _gh_object (github.Github | None): The authenticated GitHub instance used to
                make API calls.
    """
        
        # Check setup upon instantiation
        if set_config_directory is None:
            osC.check_create_dir_structure(['lukhedConfig'])
            self._resource_dir = osC.create_file_path_string(['lukhedConfig'])
        else:
            self._resource_dir = set_config_directory
            if not osC.check_if_dir_exists(self._resource_dir):
                print(f"ERROR: The config directory '{set_config_directory}' does not exist. Exiting...")
                quit()

        self._github_config_file = osC.append_to_dir(self._resource_dir, 'githubConfig.json')
        self._github_config = []
        self.user = None
        self.project = None
        self.repo = None                                        # type: Optional[Repository]
        self._gh_object = None                                  # type: Optional[Github]
        self._check_setup(project)

        if repo_name is not None:
            self._set_repo(repo_name)

    
    ###################
    # Setup/Config
    ###################
    def _check_setup(self, project):
        need_setup = True
        if osC.check_if_file_exists(self._github_config_file):
            # Check for an active github configuration
            self._github_config = fC.load_json_from_file(self._github_config_file)
            if not self._github_config:
                need_setup = True
            else:
                # check if project exists
                self._activate_project(project)
                need_setup = False
        else:
            # write default config to file
            fC.dump_json_to_file(self._github_config_file, self._github_config)
            need_setup = True

        if need_setup:
            self._prompt_for_setup()

    def _activate_project(self, project):
        try:
            projects = [x['project'].lower() for x in self._github_config]
        except Exception as e:
            input((f"ERROR: Error while trying to parse the config file. It may be corrupt."
                   "You can delete the config directory and go through setup again. Press any button to quit."))
            quit()
        
        try:
            project = project.lower()
        except Exception as e:
            input((f"ERROR: Error while trying to parse project name '{project}'. Try another project name. "
                   "Press any button to quit."))
            quit()
            
        if project in projects:
            # Get the index of the item
            index = projects.index(project)
            token = self._github_config[index]['token']
            if self._authenticate(token):
                print(f"INFO: {project} project was activated")
                self.active_project = project
                self.user = self._gh_object.get_user().login
                return True
            else:
                print("ERROR: Error while trying to authenticate.")
                return False
        else:
            
            i = input((f'ERROR: There is no project "{project}" in the config file. Would you like to go thru setup '
                   'to add a new Github key for this project name? (y/n): '))
            if i == 'y':
                self._guided_setup()
            else:
                print("Ok, exiting...")
                quit()
    
    def _prompt_for_setup(self):
        i = input("1. You do not have a valid config file to utilize github. Do you want to go thru easy setup? (y/n):")
        if i == 'y':
            self._guided_setup()
        elif i == 'n':
            print("OK, to use github functions, see https://github.com/lukhed/lukhed_basic_utils for more information.")
            quit()
        else:
            print("Did not get an expected result of 'y' or 'n'. Please reinstantiate and try again. Exiting script.")
            quit()

    def _guided_setup(self):
        input(("\n2. Starting setup\n"
               "The github key you provide in this setup will be stored locally only. "
               "After setup, you can see the config file in your directory at /lukhedConfig/githubConfig.json."
               "\nPress any key to continue"))
        
        token = input("\n3. Login to your Github account and go to https://github.com/settings/tokens. Generate a new "
                      "token and ensure to give it scopes that allow reading and writing to repos. "
                      "Copy the token, paste it below, then press enter:\n")
        token = token.replace(" ", "")
        project = input(("\n4. Provide a project name (this is needed for using the class) and press enter. "
                         "Note: projects are not case sensitive: "))
        account_to_add = {"project": project.lower(), "token": token}
        self._github_config.append(account_to_add)
        self._update_github_config_file()
        self._activate_project(project)

    def _update_github_config_file(self):
        fC.dump_json_to_file(self._github_config_file, self._github_config)

    def _authenticate(self, token):
        self._gh_object = Github(token)
        return True


    ###################
    # Repo Helpers
    ###################
    def _activate_repo(self, repo_name):
        self.repo = self._gh_object.get_repo(self.user + "/" + repo_name)
        print(f"INFO: {repo_name} repo was activated")
        
    def _parse_repo_dir_list_input(self, repo_dir_list):
        if repo_dir_list is None:
            repo_path = ""
        elif type(repo_dir_list) is str:
            repo_path = repo_dir_list
        else:
            repo_path = "/".join(repo_dir_list)

        return repo_path
    
    def _parse_content_for_upload(self, content):
        if type(content) is dict or type(content) is list:
            content = json.dumps(content)
        else:
            content = str(content)
            
        return content
    
    def _set_repo(self, repo_name):
        try:
            self._activate_repo(repo_name)
            return True
        except Exception as e:
            print((f"ERROR: Error trying to set repo to {repo_name}. Maybe the repo does not exist in your account. "
                   f"See the full error below:\n{e}"))
            create_repo = input(f"Do you want to create a private repo named {repo_name}? (y/n) ")
            if create_repo == 'y':
                if self.create_repo(repo_name, private=True):
                    self._activate_repo(repo_name)
            
    def _get_repo_contents(self, repo_path):
        contents = self.repo.get_contents(repo_path)
        return contents
    
    def create_repo(self, repo_name, description="Repo created by lukhed-basic-utils", private=True):
        """
        Creates a new repository on GitHub.

        Parameters:
            repo_name (str): The name of the repository to create.
            description (str, optional): A brief description of the repository.
            private (bool, optional): Determines whether the repository should be private. 
                                      Defaults to True (private repository).

        Returns:
            bool: True if the repository was created successfully, False otherwise.

        Example:
            >>> success = obj.create_repo("my-new-repo", description="A test repo", private=True)
        """
        try:
            repo = self._gh_object.get_user().create_repo(
                name=repo_name,
                description=description,
                private=private
            )
            print(f"Repository '{repo.name}' created successfully at {repo.html_url}")
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    
    def get_list_of_repo_names(self, print_names=False):
        """
        Returns a list of repo names available in the active project. Optionally prints the list to console.

        Parameters:
            print_names (bool, optional): If True, prints the list of available repos to the console. Defaults to False.
        
        Returns:
            list: A list of repo names associated with the active account.
        """
        repos = []
        for repo in self._gh_object.get_user().get_repos():
            repos.append(repo.name)
            if print_names:
                print(repo.name)
    
    def change_repo(self, repo_name):
        """
        Changes the active repository.

        Parameters:
            repo_name (str): Name of the repository to switch to.
        """ 
        self._set_repo(repo_name)
     
    def change_project(self, project, repo_name=None):
        """
        Changes the active project. Optionally switches the repository if repo_name is provided.

        Parameters:
            project (str): Name of the project to activate.
            repo_name (str, optional): Name of the repository to switch to. Defaults to None.
        """
        activated = self._activate_project(project)

        if activated and repo_name is not None:
            self._set_repo(repo_name)

    def get_files_in_repo_path(self, path_as_list_or_str=None):
        """
        Retrieves a list of file paths in the specified repository path.

        Parameters:
            path_as_list_or_str (list | str, optional): Path to a directory in the repository.
            Can be provided as a list of directory segments or a single string. Defaults to None.

        Returns:
            list: A list of file paths (str) found at the specified location in the repository.
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        contents = self._get_repo_contents(repo_path)

        return [x.path for x in contents]

    def retrieve_file_content(self, path_as_list_or_str, decode=True):
        """
        Retrieves the content of a file in the repository. Optionally decodes the content
        and returns either raw text/binary or JSON (if the file is .json).

        Parameters:
            path_as_list_or_str (list | str): Path to the file in the repository, either
            as a list of directory segments or a single string.

            decode (bool, optional): If True, decodes the file content. If the file is JSON,
                returns a Python dictionary; otherwise returns the raw decoded data. If False,
                returns a ContentFile object. Defaults to True.

        Returns:
            dict | str | None: Decoded JSON object if .json file and decode=True, string content
            for other file types if decode=True, ContentFile object if decode=False, or None
            if the file is not found.

        Example:
            >>> # Retrieve and decode content of a JSON file
            >>> json_data = self.retrieve_file_content(["data", "example.json"], decode=True)
            >>> print(json_data)
            {"key": "value", "numbers": [1, 2, 3]}
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)

        try:
            contents = self._get_repo_contents(repo_path)
        except UnknownObjectException as e:
            # file not found exception
            return None

        if decode:
            decoded = contents.decoded_content
            if '.json' in repo_path:
                return json.loads(decoded)
            else:
                return decoded

        else:
            return contents

    def create_file(self, content, path_as_list_or_str, commit_message="no message"):
        """
        Creates a new file in the repository with the specified content.

        Parameters:
            content (str | dict): The content to upload. If dict, it will be converted to JSON.
            path_as_list_or_str (list | str): Path to the file in the repository,
            either as a list of directory segments or a single string.
            commit_message (str, optional): Commit message for the new file. Defaults to "no message".

        Returns:
            dict: A status dictionary returned by the GitHub API after file creation.

        Example:
            >>> # Create a file with some text content
            >>> status = self.create_file("Hello, world!", ["docs", "hello.txt"], "Add hello.txt")
            >>> print(status["commit"].sha)
            6f0e918c...
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        content = self._parse_content_for_upload(content)
        status = self.repo.create_file(path=repo_path, message=commit_message, content=content)
        return status

    def delete_file(self, path_as_list_or_str, commit_message="Delete file"):
        """
        Deletes a file from the repository.

        Parameters:
            path_as_list_or_str (list | str): Path to the file in the repository,
            either as a list of directory segments or a single string.
            commit_message (str, optional): Commit message for the deletion. Defaults to "Delete file".

        Returns:
            dict | str: A status dictionary returned by the GitHub API after file deletion,
            or an error message if deletion fails.
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        try:
            # Get the file from the repository
            file = self.repo.get_contents(repo_path)

            # Delete the file
            status = self.repo.delete_file(path=repo_path, message=commit_message, sha=file.sha)
            return status
        except Exception as e:
            return e

    def update_file(self, new_content, path_as_list_or_str, message="Updated content"):
        """
        Updates the content of an existing file in the repository.

        Parameters:
            new_content (str | dict | list): The new content to upload. If dict or list, it will be converted to json.
            path_as_list_or_str (list | str): Path to the existing file in the repository,
            either as a list of directory segments or a single string.
            message (str, optional): Commit message for the update. Defaults to "Updated content".

        Returns:
            dict: A status dictionary returned by the GitHub API after file update.

        Example:
            >>> # Update an existing text file
            >>> update_status = self.update_file("New content goes here",
            ...                                  ["docs", "hello.txt"],
            ...                                  "Update hello.txt")
            >>> print(update_status["commit"].sha)
            83b2fa1c...
        """
        new_content = self._parse_content_for_upload(new_content)
        existing_contents = self.retrieve_file_content(path_as_list_or_str, decode=False)

        status = self.repo.update_file(existing_contents.path, message=message, content=new_content, 
                                       sha=existing_contents.sha)
        return status

    def create_update_file(self, path_as_list_or_str, content):
        """
        Creates a new file or updates an existing file with the given content.

        Parameters:
            path_as_list_or_str (list | str): Path to the file in the repository, either as a list
            of directory segments or a single string.
            content (str | dict): The content to upload. If dict, it may be converted to JSON
            depending on file type.

        Returns:
            dict: A status dictionary returned by the GitHub API after file creation or update.

        Example:
            >>> # Create or update a file named "config.json"
            >>> status = self.create_update_file(["configs", "config.json"], {"env": "dev", "debug": True})
            >>> print(status["commit"].message)
            Updated content
        """
        if self.file_exists(path_as_list_or_str):
            status = self.update_file(path_as_list_or_str, content)
        else:
            status = self.create_file(path_as_list_or_str, content)

        return status

    def file_exists(self, repo_dir_list):
        """
        Checks if a file exists in the repository.

        Parameters:
            repo_dir_list (list | str): Path to the file in the repository,
                either as a list of directory segments or a single string.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        self._parse_repo_dir_list_input(repo_dir_list)
        res = self.retrieve_file_content(repo_dir_list, decode=False)
        if res is None:
            return False
        else:
            return True

        