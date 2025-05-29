from logical_level.constraint_satisfaction.aggregates import ActorAggregate, AggregateAll, AggregateAllSwarm
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm
from logical_level.constraint_satisfaction.rejection_sampling.rejection_sampling_pipeline import RejectionSamplingPipeline
from logical_level.mapping.instance_initializer import RandomInstanceInitializer

TWO_VESSEL_CLASS_NUM = 7
THREE_VESSEL_CLASS_NUM = 28
FOUR_VESSEL_CLASS_NUM = 84
FIVE_VESSEL_CLASS_NUM = 210
SIX_VESSEL_CLASS_NUM = 462

class MeasurementConfig():   
   #NUMBER_OF_RUNS = {(2, 0) : 7 * 5, (2, 1) : 7 * 5, (3, 0) : 28 * 5, (3, 1) : 28 * 5, (4, 0) : 84 * 5, (5, 0) : 210 * 5, (6, 0) : 462 * 5}
   NUMBER_OF_RUNS = {(2, 0) : 1 * TWO_VESSEL_CLASS_NUM, 
                     (2, 1) : 1 * TWO_VESSEL_CLASS_NUM,
                     (3, 0) : 1 * THREE_VESSEL_CLASS_NUM, 
                     (3, 1) : 1 * THREE_VESSEL_CLASS_NUM,
                     (4, 0) : 1 * FOUR_VESSEL_CLASS_NUM,
                     (5, 0) : 1 * FIVE_VESSEL_CLASS_NUM,
                     (6, 0) : 1 * SIX_VESSEL_CLASS_NUM}
   WARMUPS = 2
   RANDOM_SEED = 1234
   TIMEOUT = 600
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = True
   BASE_NAME = 'test'
   
class MSRMeasurementConfig():   
   NUMBER_OF_RUNS = {(2, 0) : 1 * TWO_VESSEL_CLASS_NUM, 
                     (2, 1) : 1 * TWO_VESSEL_CLASS_NUM,
                     (3, 0) : 1 * THREE_VESSEL_CLASS_NUM, 
                     (3, 1) : 1 * THREE_VESSEL_CLASS_NUM,
                     (4, 0) : 1 * FOUR_VESSEL_CLASS_NUM,
                     (5, 0) : 1 * FIVE_VESSEL_CLASS_NUM,
                     (6, 0) : 1 * SIX_VESSEL_CLASS_NUM}
   WARMUPS = 2
   RANDOM_SEED = 1234
   TIMEOUT = 600
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = False
   BASE_NAME = 'MSR_test'
   
class DummyMeasurementConfig(MeasurementConfig):   
   #NUMBER_OF_RUNS = {(2, 0) : 7 * 5, (2, 1) : 7 * 5, (3, 0) : 28 * 1, (3, 1) : 28 * 1, (4, 0) : 84 * 1, (5, 0) : 210 * 1, (6, 0) : 462 * 1}
   NUMBER_OF_RUNS = {(2, 0) : 10, (2, 1) : 10, (3, 0) : 10, (3, 1) : 10, (4, 0) : 10, (5, 0) : 10, (6, 0) : 10}
   WARMUPS = 0
   RANDOM_SEED = 1234
   TIMEOUT = 10
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = True
   BASE_NAME = 'dummy_test'
   
class MiniUSVMeasurementConfig(MeasurementConfig):   
   NUMBER_OF_RUNS = {(1, 0) : 1, (2, 0) : 7 * 5, (2, 1) : 7 * 5, (3, 0) : 28 * 1, (3, 1) : 28 * 1, (4, 0) : 84 * 1, (5, 0) : 210 * 1, (6, 0) : 462 * 1}
   WARMUPS = 0
   RANDOM_SEED = 1234
   TIMEOUT = 30
   INIT_METHOD = RandomInstanceInitializer.name
   VERBOSE = True
   BASE_NAME = 'mini_usv_test'
   
def create_config(meas_config : MeasurementConfig, config_group : str) -> EvaluationData:
   config = EvaluationData(timeout=meas_config.TIMEOUT,
                            init_method=meas_config.INIT_METHOD, random_seed=meas_config.RANDOM_SEED,
                            aggregate_strat=ActorAggregate.name, config_group=config_group)
   if config_group == 'SB-MSR':
      config.population_size=8
      config.mutate_eta=20
      config.mutate_prob=0.8
      config.crossover_eta=15
      config.crossover_prob=1
      config.algorithm_desc=PyMooNSGA3Algorithm.algorithm_desc()                 
      config.aggregate_strat=ActorAggregate.name
   elif config_group == 'SB-O':
      config.population_size=8
      config.mutate_eta=20
      config.mutate_prob=0.8
      config.crossover_eta=15
      config.crossover_prob=1
      config.algorithm_desc=PyMooNSGA3Algorithm.algorithm_desc()                 
      config.aggregate_strat=ActorAggregate.name
   elif config_group == 'RS-MSR':
      config.population_size=1
      config.aggregate_strat=AggregateAll.name
      config.algorithm_desc=RejectionSamplingPipeline.algorithm_desc()
   elif config_group == 'RS-O':
      config.population_size=1
      config.aggregate_strat=AggregateAll.name
      config.algorithm_desc=RejectionSamplingPipeline.algorithm_desc()
   else:
      raise ValueError(f"Unknown config group: {config_group}")
   return config
                          


# nsga3_vessel_sb_msr_config = EvaluationData(population_size=6, mutate_eta=15, mutate_prob=0.8,
#                             crossover_eta=20, crossover_prob=1, timeout=MEAS_GlobalConfig.TIMEOUT,
#                             init_method=MEAS_GlobalConfig.INIT_METHOD, random_seed=MEAS_GlobalConfig.RANDOM_SEED, aggregate_strat=ActorAggregate.name,
#                             config_group='SB-MSR', algorithm_desc=PyMooNSGA3Algorithm.algorithm_desc)


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