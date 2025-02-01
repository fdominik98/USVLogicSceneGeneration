# Dynamically add the directory of the current Scenic file to sys.path
import sys
import os

current_file = os.path.abspath(__file__)  # Get the full path of this file
current_dir = os.path.dirname(current_file)  # Extract its directory

if current_dir not in sys.path:  # Avoid duplicates
    sys.path.append(current_dir)

from scenic_base import *

ts_infos = create_scenario(ts_num=1)

ts1, prop1 = ts_infos[0]
require prop1.check_constraints()




