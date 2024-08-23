
from genetic_algorithms.evaluation_data import EvaluationData
from model.usv_config import *
from aggregates import Aggregate
from genetic_algorithms.genetic_algorithm_base import GeneticAlgorithmBase
from aggregates import VesselAggregate
from model.usv_config import *
from deap import base, creator, tools, algorithms

class DeapAlgorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name : str, config_name: str, verbose : bool, random_init : bool = False) -> None:
        super().__init__(measurement_name, 'deap_algorithm', config_name, verbose, random_init)
    
    def get_aggregate(self, env) -> Aggregate:
        return VesselAggregate(env, minimize=True)   
    
    
    def init_problem(self, initial_population : list[list[float]], eval_data : EvaluationData) -> None:
        # Attribute generator with different boundaries
        def generate_individual(actors):
            return [np.random.uniform(low, high) for low, high in self.boundaries] * actors

        # Define the multi-objective fitness
        creator.create("FitnessMulti", base.Fitness, weights=self.aggregate.weights)  # Maximize all objectives
        creator.create("Individual", list, fitness=creator.FitnessMulti)

        # Initialize the toolbox
        toolbox = base.Toolbox()

        toolbox.register("individual", tools.initIterate, creator.Individual, lambda : generate_individual(self.env_config.actor_num))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", self.aggregate.evaluate)
        toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=-10, up=10, eta=eval_data.crossover_eta)
        # indpb: number of variables to mutate per indivudal
        toolbox.register("mutate", tools.mutPolynomialBounded, low=[b[0] for b in self.boundaries]* self.env_config.actor_num,
                        up=[b[1] for b in self.boundaries] * self.env_config.actor_num, eta=eval_data.mutate_eta, indpb=1/self.env_config.all_variable_num)
        toolbox.register("select", tools.selNSGA2)
        
        stats = None
        if self.verbose:
            # Statistics to keep track of the progress
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("min", np.min, axis=0)

        def get_population(num):
            # Create the initial population
            return [creator.Individual(ind) for ind in self.env.get_population(num)]
            #population = toolbox.population(n=num)

        halloffame = tools.ParetoFront()  # Keep track of the best individuals
        population = get_population(eval_data.population_size)
        
        return toolbox, population, halloffame, stats

    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        toolbox, population, halloffame, stats = some_input
        
        # Run the genetic algorithm
        algorithms.eaMuPlusLambda(population, toolbox, mu=eval_data.population_size, lambda_=eval_data.population_size, cxpb=eval_data.crossover_prob,
                                  mutpb=eval_data.mutate_prob, ngen=eval_data.number_of_generations,
                                stats=stats, halloffame=halloffame, verbose=self.verbose)
        return halloffame
        
    
    def convert_results(self, some_results, eval_data : EvaluationData) -> tuple[list[float], list[float]]:
        halloffame = some_results
        best_ind = tools.selBest(halloffame, 1)[0]
        return list(best_ind), list(best_ind.fitness.values)


    

