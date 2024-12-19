import os
from pathlib import Path
from aceCommon import create_file_path_string

def test_create_file_path_string():
    print("Test 1: Base path provided as a list:")
    path1 = create_file_path_string(
        list_of_dir=['subdir', 'file.txt'],
        base_path_list=['C:', 'Users', 'dad', 'Documents']
    )
    expected_path1 = Path('C:', 'Users', 'dad', 'Documents', 'subdir', 'file.txt')
    print(path1)
    assert Path(path1) == expected_path1, "Base path list test failed"

    print("\nTest 2: Default to current working directory:")
    path2 = create_file_path_string(list_of_dir=['subdir', 'file.txt'])
    expected_path2 = Path.cwd() / 'subdir' / 'file.txt'
    print(path2)
    assert Path(path2) == expected_path2, "Default working directory test failed"

    print("\nTest 3: Custom base path using ace_parent:")
    path3 = create_file_path_string(list_of_dir=['config'], ace_parent=1)
    # Adjust this test based on your project structure
    print(path3)
    assert 'config' in path3, "Relative ace_parent test failed"

    print("\nTest 4: Current working directory fallback:")
    path4 = create_file_path_string(list_of_dir=['mydir'])
    expected_path4 = Path.cwd() / 'mydir'
    print(path4)
    assert Path(path4) == expected_path4, "Current working directory fallback test failed"

if __name__ == '__main__':
    test_create_file_path_string()
