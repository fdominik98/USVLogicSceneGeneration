from logical_level.constraint_satisfaction.aggregates import ActorAggregate, AggregateAll, AggregateAllSwarm, CategoryAggregate
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm
from logical_level.constraint_satisfaction.rejection_sampling.rejection_sampling_pipeline import RejectionSamplingPipeline
from logical_level.mapping.instance_initializer import RandomInstanceInitializer

class MainMeasurementConfig():   
   #NUMBER_OF_RUNS = {(2, 0) : 7 * 5, (2, 1) : 7 * 5, (3, 0) : 28 * 5, (3, 1) : 28 * 5, (4, 0) : 84 * 5, (5, 0) : 210 * 5, (6, 0) : 462 * 5}
   NUMBER_OF_RUNS = {(2, 0) : 1000, (2, 1) : 1000, (3, 0) : 1000, (3, 1) : 1000, (4, 0) : 1000, (5, 0) : 1000, (6, 0) : 1000}
   WARMUPS = 2
   RANDOM_SEED = 1234
   TIMEOUT = 600
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = False
   BASE_NAME = 'test'
   
class DummyMeasurementConfig():   
   NUMBER_OF_RUNS = {(2, 0) : 7 * 5, (2, 1) : 7 * 5, (3, 0) : 28 * 1, (3, 1) : 28 * 1, (4, 0) : 84 * 1, (5, 0) : 210 * 1, (6, 0) : 462 * 1}
   WARMUPS = 0
   RANDOM_SEED = 1234
   TIMEOUT = 30
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = True
   BASE_NAME = 'dummy_test'
   
class MiniUSVMeasurementConfig():   
   NUMBER_OF_RUNS = {(2, 0) : 7 * 5, (2, 1) : 7 * 5, (3, 0) : 28 * 1, (3, 1) : 28 * 1, (4, 0) : 84 * 1, (5, 0) : 210 * 1, (6, 0) : 462 * 1}
   WARMUPS = 0
   RANDOM_SEED = 1234
   TIMEOUT = 30
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = True
   BASE_NAME = 'mini_usv_test'
   
# MEAS_GlobalConfig = DummyMeasurementConfig()
# MEAS_GlobalConfig = MiniUSVMeasurementConfig()
MEAS_GlobalConfig = MainMeasurementConfig()

nsga2_vessel_sb_msr_config = EvaluationData(population_size=8, mutate_eta=20, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1, timeout=MEAS_GlobalConfig.TIMEOUT,
                            init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=ActorAggregate.name,
                            config_group='SB-MSR', algorithm_desc=PyMooNSGA2Algorithm.algorithm_desc)

nsga2_vessel_sb_o_config = EvaluationData(population_size=8, mutate_eta=20, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1, timeout=MEAS_GlobalConfig.TIMEOUT,
                            init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=ActorAggregate.name,
                            config_group='SB-O', algorithm_desc=PyMooNSGA2Algorithm.algorithm_desc)

scenic_rs_msr_config = EvaluationData(population_size=1, timeout=MEAS_GlobalConfig.TIMEOUT, init_method=MEAS_GlobalConfig.INIT_METHOD,
                               random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAll.name,
                            config_group='RS-MSR', algorithm_desc=RejectionSamplingPipeline.algorithm_desc)

scenic_rs_o_config = EvaluationData(population_size=1, timeout=MEAS_GlobalConfig.TIMEOUT, init_method=MEAS_GlobalConfig.INIT_METHOD,
                               random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAll.name,
                            config_group='RS-O', algorithm_desc=RejectionSamplingPipeline.algorithm_desc)


nsga3_vessel_sb_msr_config = EvaluationData(population_size=6, mutate_eta=1, mutate_prob=0.5,
                            crossover_eta=1, crossover_prob=0.8, timeout=MEAS_GlobalConfig.TIMEOUT,
                            init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=ActorAggregate.name,
                            config_group='SB-MSR', algorithm_desc=PyMooNSGA3Algorithm.algorithm_desc)

nsga3_vessel_sb_o_config = EvaluationData(population_size=6, mutate_eta=1, mutate_prob=0.5,
                            crossover_eta=1, crossover_prob=0.8, timeout=MEAS_GlobalConfig.TIMEOUT,
                            init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=ActorAggregate.name,
                            config_group='SB-O', algorithm_desc=PyMooNSGA2Algorithm.algorithm_desc)

# ga_config = EvaluationData(population_size=4, num_parents_mating = 4,
#                         mutate_eta=20, mutate_prob=0.2, crossover_eta=10,
#                         crossover_prob=0.2, timeout=MEAS_GlobalConfig.TIMEOUT, init_method=MEAS_GlobalConfig.INIT_METHOD,
#                         random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAll.name)

# nsga2_all_config = EvaluationData(population_size=50, mutate_eta=10, mutate_prob=1.0,
#                             crossover_eta=20, crossover_prob=0.8, timeout=MEAS_GlobalConfig.TIMEOUT,
#                             init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAll.name)
# nsga2_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
#                             crossover_eta=15, crossover_prob=1.0, timeout=MEAS_GlobalConfig.TIMEOUT,
#                             init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=CategoryAggregate.name)


# nsga3_all_config = EvaluationData(population_size=20, mutate_eta=1, mutate_prob=0.8,
#                             crossover_eta=1, crossover_prob=1.0, timeout=MEAS_GlobalConfig.TIMEOUT,
#                             init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAll.name)
# nsga3_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
#                             crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
#                             init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=CategoryAggregate.name)


# pso_config = EvaluationData(population_size=30, c_1=2.5, c_2=1.0, w=0.4, timeout=MEAS_GlobalConfig.TIMEOUT,
#                           init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAllSwarm.name)

# de_config = EvaluationData(population_size=15, mutate_prob=0.5, crossover_prob=0.5,
#                           timeout=MEAS_GlobalConfig.TIMEOUT, init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=AggregateAll.name)