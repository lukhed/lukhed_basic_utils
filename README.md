# aceCommon

A collection of basic utility functions for Python projects.

## Installation and Usage

```bash
pip install lukhed_basic_utils
```

```python
from lukhed_basic_utils import osCommon as osC

example_path = osC.create_file_path_string(list_of_dir=['subdir', 'file.txt'])
print(example_path)
```

```bash
/home/user/current_working_dir/subdir/file.txt
```

## osCommon Methods
```python
from lukhed_basic_utils import osCommon as osC
```

## fileCommon Methods
```python
from lukhed_basic_utils import fileCommon as fC
```

## githubCommon Usage
```python
from lukhed_basic_utils.githubCommon import GithubHelper
gC = GithubHelper(project='lukhed', repo_name='exampleRepo')
example_dict = gC.retrieve_file_content('awesomeJson.json')
```