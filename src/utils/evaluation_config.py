
# NUMBER_OF_RUNS = {2 : 150, 3 : 6 * 17, 4 : 21 * 5, 5 : 50 * 2, 6 : 99 * 1}
# NUMBER_OF_RUNS = {2 : 150, 3 : 6 * 34, 4 : 21 * 10, 5 : 50 * 4, 6 : 99 * 3}
# NUMBER_OF_RUNS = {2 : 150, 3 : 6 * 50, 4 : 21 * 15, 5 : 50 * 6, 6 : 99 * 4}
from logical_level.constraint_satisfaction.aggregates import ActorAggregate, AggregateAll, AggregateAllSwarm, CategoryAggregate
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.mapping.instance_initializer import RandomInstanceInitializer


NUMBER_OF_RUNS = {2 : 100, 3 : 1000, 4 : 1000, 5 : 1000, 6 : 1000}
WARMUPS = 2
RANDOM_SEED = 1234
TIMEOUT = 20
INIT_METHOD = RandomInstanceInitializer.name
VERBOSE = True

START_FROM = [0,0,0]


ga_config = EvaluationData(population_size=4, num_parents_mating = 4,
                        mutate_eta=20, mutate_prob=0.2, crossover_eta=10,
                        crossover_prob=0.2, timeout=TIMEOUT, init_method=INIT_METHOD,
                        random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)


nsga2_vessel_config = EvaluationData(population_size=10, mutate_eta=15, mutate_prob=0.8,
                            crossover_eta=20, crossover_prob=1, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=ActorAggregate.name,
                            config_group='SBO')
nsga2_all_config = EvaluationData(population_size=50, mutate_eta=10, mutate_prob=1.0,
                            crossover_eta=20, crossover_prob=0.8, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)
nsga2_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=CategoryAggregate.name)


nsga3_vessel_config = EvaluationData(population_size=6, mutate_eta=15, mutate_prob=1.0,
                            crossover_eta=10, crossover_prob=0.8, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=ActorAggregate.name)
nsga3_all_config = EvaluationData(population_size=20, mutate_eta=1, mutate_prob=0.8,
                            crossover_eta=1, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)
nsga3_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=CategoryAggregate.name)


pso_config = EvaluationData(population_size=30, c_1=2.5, c_2=1.0, w=0.4, timeout=TIMEOUT,
                          init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAllSwarm.name)

de_config = EvaluationData(population_size=15, mutate_prob=0.5, crossover_prob=0.5,
                          timeout=TIMEOUT, init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)

scenic_config = EvaluationData(population_size=1, timeout=TIMEOUT, init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name,
                            config_group='RS')


