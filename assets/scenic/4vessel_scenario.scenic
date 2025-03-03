ts_infos = create_scenario(ts_num=3)

ts1, prop1 = ts_infos[0]
require prop1.check_constraints()
ts2, prop2 = ts_infos[1]
require prop2.check_constraints()
ts3, prop3 = ts_infos[2]
require prop3.check_constraints()

prop_ts_1 = new NoCollideOutVisProps with val1 ts1, with val2 ts2
require prop_ts_1.check_constraints()
prop_ts_2 = new NoCollideOutVisProps with val1 ts1, with val2 ts3
require prop_ts_2.check_constraints()
prop_ts_3 = new NoCollideOutVisProps with val1 ts2, with val2 ts3
require prop_ts_3.check_constraints()



