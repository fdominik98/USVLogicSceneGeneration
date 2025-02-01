# Dynamically add the directory of the current Scenic file to sys.path
import sys
import os

current_file = os.path.abspath(__file__)  # Get the full path of this file
current_dir = os.path.dirname(current_file)  # Extract its directory

if current_dir not in sys.path:  # Avoid duplicates
    sys.path.append(current_dir)

from scenic_base import *

ts_infos = create_scenario(ts_num=4)

ts1, prop1 = ts_infos[0]
require prop1.check_constraints()
ts2, prop2 = ts_infos[1]
require prop2.check_constraints()
ts3, prop3 = ts_infos[2]
require prop3.check_constraints()
ts4, prop4 = ts_infos[3]
require prop4.check_constraints()


prop_ts_1 = new NoCollideOutVisProps with val1 ts1, with val2 ts2
require prop_ts_1.check_constraints()
prop_ts_2 = new NoCollideOutVisProps with val1 ts1, with val2 ts3
require prop_ts_2.check_constraints()
prop_ts_3 = new NoCollideOutVisProps with val1 ts2, with val2 ts3
require prop_ts_3.check_constraints()

prop_ts_4 = new NoCollideOutVisProps with val1 ts4, with val2 ts1
require prop_ts_4.check_constraints()
prop_ts_5 = new NoCollideOutVisProps with val1 ts4, with val2 ts2
require prop_ts_5.check_constraints()
prop_ts_6 = new NoCollideOutVisProps with val1 ts4, with val2 ts3
require prop_ts_6.check_constraints()



