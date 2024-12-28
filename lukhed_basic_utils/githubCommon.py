from lukhed_basic_utils import osCommon as osC
from lukhed_basic_utils import fileCommon as fC
from lukhed_basic_utils import commonCommon as cC
from github import Github
from github.Repository import Repository
from github.GithubException import UnknownObjectException
import json
from typing import Optional

"""
https://github.com/grindSunday/
https://pygithub.readthedocs.io/en/latest/examples.html

Example Project: grindsunday
Example Repo: grindsports

"""

class GithubHelper:
    def __init__(self, project='your_project_name', repo_name=None):
        """
        :param project:         str(), a github account setup, currently only supporting grindsunday.
                                https://github.com/grindSunday

        :param repo_name:       str(), a repository available within the project. For example, in grindsunday:
                                https://github.com/grindSunday?tab=repositories
        """
        
        # Check setup upon instantiation
        cC.check_create_lukhed_config_path()
        self._resource_dir = cC.get_lukhed_config_path()
        self._github_config_file = osC.append_to_dir(self._resource_dir, 'githubConfig.json')
        self._github_config = []
        self.project = None
        self.repo = None                                        # type: Optional[Repository]
        self._gh_object = None                                  # type: Optional[Github]
        self._check_setup(project)

        if repo_name is not None:
            self._set_repo(repo_name)

    
    ###################
    # Setup/COnfig
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
        projects = [x['project'] for x in self._github_config]
        
        if project in projects:
            # Get the index of the item
            index = projects.index(project)
            token = self._github_config[index]['token']
            if self._authenticate(token):
                print(f"INFO: {project} project was activated")
                self.active_project = project
                return True
            else:
                print("ERROR: Error while trying to authenticate.")
                return False
        else:
            i = input((f'ERROR: There is no project "{project}" not found in the list. Would you like to go thru setup '
                   'to add a new Github scope for this project name? (y/n): '))
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
               "The github information you provide in this setup will be stored locally only. "
               "After setup, you can see the config file in your directory at /lukhedConfig/githubConfig.json."
               "\nPress any key to continue"))
        
        token = input("\n3. Login to your Github account and go to https://github.com/settings/tokens. Generate a new "
                      "token and ensure to give it scopes that allow reading and writing to repos. "
                      "Copy the token, paste it below, then press enter:\n")
        token = token.replace(" ", "")
        project = input(("\n4. Provide a project name (this is needed for using the class) and press enter. "
                         "Note: projects are case sensitive: "))
        account_to_add = {"project": project, "token": token}
        self._github_config.append(account_to_add)
        self._update_github_config_file()
        self._activate_project(project)

    def _update_github_config_file(self):
        fC.dump_json_to_file(self._github_config_file, self._github_config)

        
    ###################
    # Repo Helpers
    # These functions work with the active Repo
    ###################
    def _parse_repo_dir_list_input(self, repo_dir_list):
        if repo_dir_list is None:
            repo_dir_list = ""
        elif type(repo_dir_list) is str:
            repo_dir_list = repo_dir_list
        else:
            repo_dir_list = ""
            for d in repo_dir_list:
                repo_dir_list = repo_dir_list + "/" + d

        return repo_dir_list
    
    def _set_repo(self, repo_name):
        user = self._gh_object.get_user().login
        self.repo = self._gh_object.get_repo(user + "/" + repo_name)
        print(f"INFO: {repo_name} repo was activated")
        return True
    
    def _get_repo_contents(self, repo_path):
        contents = self.repo.get_contents(repo_path)
        return contents
    
    def get_list_of_repo_names(self, print_names=False):
        repos = []
        for repo in self._gh_object.get_user().get_repos():
            repos.append(repo.name)
            if print_names:
                print(repo.name)
    
    def change_repo(self, repo_name):
        self._set_repo(repo_name)
     
    def change_project(self, project, repo_name=None):
        activated = self._activate_project(project)

        if activated and repo_name is not None:
            self._set_repo(repo_name)

    def get_files_in_repo_path(self, path_as_list_or_str=None):
        """
        Gets a list of file paths in a repo given the parameters.

        :param repo_dir_list:   None, str(), or list()

                                None -> Output will be all files and all directories in the top level of the repo

                                str() -> String represents a top level folder in the repo. Output will be all files and
                                all directories within that top level folder

                                list() -> List path to the desired directory. Output will be all files and all directories
                                within the final directory in the path derived from the list. For example:
                                in repo=grind sports ["teamConversion", "nfl"] will retrieve all files within the nfl
                                directory which is in the top level directory of teamConversion.
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        contents = self._get_repo_contents(repo_path)

        return [x.path for x in contents]

    def retrieve_file_content(self, path_as_list_or_str, decode=True):
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

    def create_file(self, content, path_as_list_or_str=None, commit_message="no message"):
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        status = self.repo.create_file(path=repo_path, message=commit_message, content=content)
        return status

    def delete_file(self, path_as_list_or_str=None, commit_message="Delete file"):
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        try:
            # Get the file from the repository
            file = self.repo.get_contents(repo_path)

            # Delete the file
            status = self.repo.delete_file(path=repo_path, message=commit_message, sha=file.sha)
            return status
        except Exception as e:
            return str(e)

    def update_file(self, new_content, path_as_list_or_str, message="Updated content"):
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        new_content = self._parse_new_file_content(repo_path, new_content)
        existing_contents = self.retrieve_file_content(path_as_list_or_str, decode=False)

        status = self.repo.update_file(existing_contents.path, message=message, content=new_content, sha=existing_contents.sha)
        return status

    def create_update_file(self, path_as_list_or_str, content):
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        new_content = self._parse_new_file_content(repo_path, content)

        if self.file_exists(path_as_list_or_str):
            status = self.update_file(path_as_list_or_str, new_content)

        else:
            status = self.create_file(path_as_list_or_str, new_content)

        return status

    def file_exists(self, repo_dir_list=None):
        self._parse_repo_dir_list_input(repo_dir_list)
        res = self.retrieve_file_content(repo_dir_list, decode=False)
        if res is None:
            return False
        else:
            return True

    def _authenticate(self, token):
        self._gh_object = Github(token)
        return True

    def _parse_new_file_content(self, repo_path, content):
        if (".json" in repo_path and type(content) is dict) or type(content) is list:
            content = json.dumps(content)

        return content

    @staticmethod
    def _build_repo_path(list_path_from_root):
        return "/".join(list_path_from_root)

    


def retrieve_decoded_content_from_file(project, repo, file_name, github_object=None):
    g = _parse_github_object(github_object)
    repo_name = project + "/" + repo
    g_repo = g.get_repo(repo_name)

    return g_repo.get_contents(file_name).decoded_content


def retrieve_json_content_from_file(project, repo, file_name, github_object=None):
    g = _parse_github_object(github_object)
    c = retrieve_decoded_content_from_file(project, repo, file_name, github_object=g)

    return json.loads(c)


def return_github_instance():
    return _create_github_instances()


def update_file_in_repository(project, repo, file_name, new_content, github_object=None):
    g = _parse_github_object(github_object)
    repo = g.get_repo(project + "/" + repo)
    contents = repo.get_contents(file_name)
    if type(new_content) == dict or type(new_content) is list:
        repo.update_file(contents.path, "", json.dumps(new_content), contents.sha)
    else:
        repo.update_file(contents.path, "", str(new_content), contents.sha)


def create_new_file_in_repository(project, repo, file_name, file_content, github_object=None):
    """
    Creates new file. Cannot overwrite

    :param project:         str(), github root, for example, grindsunday

    :param repo:            str(), repo name, see repo names for grindsunday here:
                            https://github.com/grindSunday?tab=repositories

    :param file_name:       str(), location from repo. For example "test.txt" or "test/test.txt"

    :param file_content:    str() or dict(), file can write text files or json files.

    :param github_object:   pass the object if you already created one
    """

    g = _parse_github_object(github_object)
    repo = g.get_repo(project + "/" + repo)

    if ".json" in file_name and type(file_content) is dict or type(file_content) is list:
        file_content = json.dumps(file_content)

    status = repo.create_file(path=file_name, message="no message", content=file_content)
    return status


def get_file_paths_in_repository(project, repo, repo_dir_list=None, github_object=None):
    """
    Gets a list of file paths in a repo given the parameters. The output can then be used to retrieve file content
    of the desired files in the repo.

    :param project:         str(), gitHub root, for example, grindsunday

    :param repo:            str(), repo name, see repo names for grindsunday here:
                            https://github.com/grindSunday?tab=repositories
                            for example, grindSports

    :param repo_dir_list:   None, str(), or list()

                            None -> Output will be all files and all directories in the top level of the repo

                            str() -> String represents the top level folder in the repo. Output will be all files and
                            all directories within that top level folder

                            list() -> List path to the desired directory. Output will be all files and all directories
                            within the final directory in the path derived from the list. For example:
                            in repo=grind sports ["teamConversion", "nfl"] will retrieve all files within the nfl
                            directory which is in the top level directory of teamConversion.

    :param github_object:   pass the object if you already created one
    """
    g = _parse_github_object(github_object)
    repo = g.get_repo(project + "/" + repo)


    if repo_dir_list is None:
        contents = repo.get_contents("")
    elif type(repo_dir_list) is str:
        contents = repo.get_contents(repo_dir_list)
    else:
        content_path = ""
        for d in repo_dir_list:
            content_path = content_path + "/" + d

        contents = repo.get_contents(content_path)

    return [x.path for x in contents]


def _create_github_instances():
    t = retrieve_token()
    g = Github(t)
    return g


def _parse_github_object(github_object_parameter):
    if github_object_parameter is None:
        return _create_github_instances()
    else:
        return github_object_parameter


def retrieve_token():
    t = fC.read_single_line_from_file(osC.create_file_path_string(["resources", "aceCommon", "githubToken.txt"]))

    return t



if __name__ == '__main__':
    stop = 1

