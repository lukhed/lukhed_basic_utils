import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


from aceCommon.timeCommon import create_time_stamp

def test_create_time_stamp():
    print(create_time_stamp())

if __name__ == '__main__':
    test_create_time_stamp()