ts_infos = create_scenario(ts_num=2)

ts1, prop1 = ts_infos[0]
require prop1.check_constraints()
ts2, prop2 = ts_infos[1]
require prop2.check_constraints()

prop_ts_1 = new NoCollideOutVisProps with val1 ts1, with val2 ts2
require prop_ts_1.check_constraints()



