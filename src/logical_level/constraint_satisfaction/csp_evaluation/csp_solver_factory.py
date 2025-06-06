from logical_level.constraint_satisfaction.csp_evaluation.csp_solver import CSPSolver
from logical_level.constraint_satisfaction.evolutionary_computation.pygad_ga_algorithm import PyGadGAAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.scipy_de_algorithm import SciPyDEAlgorithm
from logical_level.constraint_satisfaction.rejection_sampling.rejection_sampling_pipeline import BaseRejectionSampling, TwoStepCDRejectionSampling, TwoStepRejectionSampling


class CPSSolverFactory:
    @staticmethod
    def factory(algorithm_desc : str, verbose) -> CSPSolver:
        if algorithm_desc == PyGadGAAlgorithm.algorithm_desc():
            return PyGadGAAlgorithm(verbose)      
        elif algorithm_desc == PyMooNSGA2Algorithm.algorithm_desc():
            return PyMooNSGA2Algorithm(verbose)     
        elif algorithm_desc == PyMooNSGA3Algorithm.algorithm_desc():
            return PyMooNSGA3Algorithm(verbose)    
        elif algorithm_desc == SciPyDEAlgorithm.algorithm_desc():
            return SciPyDEAlgorithm(verbose)
        elif algorithm_desc == PySwarmPSOAlgorithm.algorithm_desc:
            return PySwarmPSOAlgorithm(verbose)
        elif algorithm_desc == BaseRejectionSampling.algorithm_desc():
            return BaseRejectionSampling(verbose)   
        elif algorithm_desc == TwoStepRejectionSampling.algorithm_desc():
            return TwoStepRejectionSampling(verbose)
        elif algorithm_desc == TwoStepCDRejectionSampling.algorithm_desc():
            return TwoStepCDRejectionSampling(verbose)      
        else:
            raise Exception('Unknown algorithm desc')