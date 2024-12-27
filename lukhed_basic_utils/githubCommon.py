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

class GitCommon:
    def __init__(self, project='grindsunday', repo_name='grindsports'):
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
        self._github_config = None
        self._check_setup()
        
        self.project= project.lower()

        # Authenticate with GitHub
        self._gh_object = None                      # type: Optional[Github]
        self._authenticate()

        # set the repository
        self.repo_name = repo_name.lower()
        self.repo = None                            # type: Optional[Repository]
        self._set_repo()

    def _check_setup(self):
        need_setup = True
        if osC.check_if_file_exists(self._github_config_file):
            # Check for an active github configuration
            self._github_config = fC.load_json_from_file(self._github_config_file)
            if not self._github_config:
                need_setup = True
            else:
                need_setup = False
        else:
            github_config = []
            fC.dump_json_to_file(self._github_config_file, github_config)
            need_setup = True

        if need_setup:
            self._prompt_for_setup()

        
    def _prompt_for_setup(self):
        i = input("*** You do not have a valid config file to utilize github. Do you want to go thru easy setup? (y/n):")
        if i == 'y':
            self._guided_setup()
        elif i == 'n':
            print("OK, to use github functions, see https://github.com/lukhed/lukhed_basic_utils for more information.")
            quit()
        else:
            print("Did not get an expected result of 'y' or 'n'. Please reinstantiate and try again. Exiting script.")
            quit()

    def _guided_setup(self):
        print("\nStarting setup. Your github information will only be stored locally. You can see the config file created " \
              "as a result of this setup in /lukhedConfig/githubConfig.json")
        quit()
    def change_project(self, project, repo_name):
        self.project = project.lower()
        self._authenticate()

        self.repo_name = repo_name.lower()
        self._set_repo()

    def change_repo(self, repo_name):
        self.repo_name = repo_name.lower()
        self._set_repo()

    def get_file_paths_in_path(self, repo_dir_list=None):
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
        contents = self._get_repo_contents(repo_dir_list)

        return [x.path for x in contents]

    def retrieve_file_content(self, repo_dir_list, decode=True):
        fp = self._build_repo_path(repo_dir_list)

        try:
            contents = self._get_repo_contents(fp)
        except UnknownObjectException as e:
            # file not found exception
            return None

        if decode:
            decoded = contents.decoded_content

            if '.json' in fp:
                return json.loads(decoded)
            else:
                return decoded

        else:
            return contents

    def create_file(self, repo_dir_list, content):
        repo_path = self._build_repo_path(repo_dir_list)
        status = self.repo.create_file(path=repo_path, message="no message", content=content)
        return status

    def delete_file(self, repo_dir_list, commit_message="Delete file"):
        repo_path = self._build_repo_path(repo_dir_list)
        try:
            # Get the file from the repository
            file = self.repo.get_contents(repo_path)

            # Delete the file
            status = self.repo.delete_file(path=repo_path, message=commit_message, sha=file.sha)
            return status
        except Exception as e:
            return str(e)

    def update_file(self, repo_dir_list, new_content):
        existing_contents = self.retrieve_file_content(repo_dir_list, decode=False)
        status = self.repo.update_file(existing_contents.path, "", new_content, existing_contents.sha)
        return status

    def create_update_file(self, repo_dir_list, content):
        new_content = self._parse_new_file_content(repo_dir_list, content)

        if self.file_exists(repo_dir_list):
            status = self.update_file(repo_dir_list, new_content)

        else:
            status = self.create_file(repo_dir_list, new_content)

        return status

    def file_exists(self, repo_dir_list):
        res = self.retrieve_file_content(repo_dir_list, decode=False)
        if res is None:
            return False
        else:
            return True

    def _authenticate(self):
        token_path = osC.append_to_dir(self._resource_dir, "githubProjects.json")
        projects = fC.load_json_from_file(token_path)
        t = projects[self.project]
        self._gh_object = Github(t)

    def _set_repo(self):
        self.repo = self._gh_object.get_repo(self.project + "/" + self.repo_name)

    def _parse_new_file_content(self, repo_dir_list, content):
        repo_path = self._build_repo_path(repo_dir_list)
        if (".json" in repo_path and type(content) is dict) or type(content) is list:
            content = json.dumps(content)

        return content

    @staticmethod
    def _build_repo_path(list_path_from_root):
        return "/".join(list_path_from_root)

    def _get_repo_contents(self, repo_dir_list):
        if repo_dir_list is None:
            contents = self.repo.get_contents("")
        elif type(repo_dir_list) is str:
            contents = self.repo.get_contents(repo_dir_list)
        else:
            content_path = ""
            for d in repo_dir_list:
                content_path = content_path + "/" + d

            contents = self.repo.get_contents(content_path)

        return contents


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


def test_functions():
    G = GitCommon()
    stop = 1
    # test = G.get_file_paths_in_repository('machineLearning')
    grind_sports_readme = G.create_update_file(['poop.json'], [1, 2, 3 ,4])
    # G.change_repo('machineLearning')
    # machine_learning_readme = G.retrieve_file_content(['README.md'])
    # j = G.retrieve_json_from_file('stocks', ['td_token_path.json'])
    stop = 1
    t = get_file_paths_in_repository("grindsunday", "grindSports", repo_dir_list="teamConversion")
    n = create_new_file_in_repository("grindsunday", "grindsports", "schedules/test_schedule.json", {"test": "json"})
    c = retrieve_decoded_content_from_file("grindsunday", "grindsports", "schedules/README.txt")
    update_file_in_repository("grindSunday", "stocks", "td_token_path.json", {"creation_timestamp": None, "token": {}})
    c = retrieve_json_content_from_file("grindSunday", "stocks", "td_token_path.json")


if __name__ == '__main__':
    # print(get_file_paths_in_repository("grindsunday", "grindSports", repo_dir_list="teamConversion"))
    test_functions()

