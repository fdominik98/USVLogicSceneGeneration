from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pygad_ga_algorithm import PyGadGAAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.scipy_de_algorithm import SciPyDEAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from logical_level.constraint_satisfaction.rejection_sampling.rejection_sampling_pipeline import RejectionSamplingPipeline
from logical_level.constraint_satisfaction.solver_base import SolverBase


class SolverFactory:
    @staticmethod
    def factory(measurement_name, functional_scenarios, test_config : EvaluationData, number_of_runs, warmups, verbose) -> SolverBase:
        if test_config.algorithm_desc == PyGadGAAlgorithm.algorithm_desc:
            return PyGadGAAlgorithm(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)      
        elif test_config.algorithm_desc == PyMooNSGA2Algorithm.algorithm_desc:
            return PyMooNSGA2Algorithm(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)     
        elif test_config.algorithm_desc == PyMooNSGA3Algorithm.algorithm_desc:
            return PyMooNSGA3Algorithm(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)    
        elif test_config.algorithm_desc == SciPyDEAlgorithm.algorithm_desc:
            return SciPyDEAlgorithm(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)
        elif test_config.algorithm_desc == PySwarmPSOAlgorithm.algorithm_desc:
            return PySwarmPSOAlgorithm(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)
        elif test_config.algorithm_desc == RejectionSamplingPipeline.algorithm_desc:
            return RejectionSamplingPipeline(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)         
        else:
            raise Exception('Unknown algorithm desc')