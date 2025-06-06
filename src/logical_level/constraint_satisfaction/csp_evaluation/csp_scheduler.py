from abc import ABC, abstractmethod
from itertools import cycle, islice
from typing import List, Set, Tuple

from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.model_parser import ModelParser
from logical_level.constraint_satisfaction.csp_evaluation.csp_evaluator import CSPEvaluator
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.logical_scenario import LogicalScenario
from utils.general_utils import set_seed
from utils.scenario import Scenario


class CSPScheduler(ABC):
    @abstractmethod
    def run(self, core_id : int):
        pass
    
    
class MSRScheduler(CSPScheduler):
    def __init__(self, evaluator: CSPEvaluator, functional_scenarios: List[FunctionalScenario],
                 random_seed : int, warmups : int, average_time_per_scene : int, init_method : str) -> None:
        self.evaluator = evaluator
        self.scenarios : List[Tuple[LogicalScenario, FunctionalScenario]] = [(LogicalScenarioBuilder.build_from_functional(scenario, init_method),
                                                                             scenario) for scenario in functional_scenarios]
        self.warmups = warmups
        self.max_eval_time = average_time_per_scene * len(self.scenarios)
        set_seed(random_seed)
        
    def run(self, core_id : int):
        for i, (logical_scenario, functional_scenario) in enumerate(islice(cycle(self.scenarios), self.warmups)):
            self.evaluator.evaluate(logical_scenario, functional_scenario, core_id, False, 0, self.max_eval_time)
            print(f'warmup {i + 1}/{self.warmups} completed with {self.evaluator.name}.')
        
        coverage = {logical_scenario : False for logical_scenario, _ in self.scenarios}
        eval_time = 0
        for logical_scenario, functional_scenario in cycle(self.scenarios):
            remaining = list(coverage.values()).count(False)
            if remaining == 0 or eval_time >= self.max_eval_time:
                break
            
            if coverage[logical_scenario]:
                continue
            
            eval_data = self.evaluator.evaluate(logical_scenario,
                                                functional_scenario,
                                                core_id,
                                                True,
                                                eval_time,
                                                self.max_eval_time)
            eval_time += eval_data.evaluation_time
            if eval_data.is_valid:
                coverage[logical_scenario] = True
                print(f"Covered FECs: {len(self.scenarios) - remaining + 1}/{len(self.scenarios)} with {self.evaluator.name}.")
                continue
        
class OneStepScheduler(CSPScheduler):
    def __init__(self, evaluator: CSPEvaluator, logical_scenario: LogicalScenario,
                 random_seed : int, warmups : int, average_time_per_scene : int) -> None:
        self.evaluator = evaluator
        self.logical_scenario = logical_scenario
        self.actor_number = (self.logical_scenario.vessel_number, self.logical_scenario.obstacle_number)
        self.total_fecs = ModelParser.TOTAL_FECS[self.actor_number]
        self.max_eval_time = average_time_per_scene * self.total_fecs
        self.warmups = warmups
        set_seed(random_seed)
    
    def run(self, core_id : int):
        for i in range(self.warmups):
            self.evaluator.evaluate(self.logical_scenario, None, core_id, False, 0, self.max_eval_time)
            print(f'warmup {i + 1}/{self.warmups} completed with {self.evaluator.name}.')
            
        covered_hashes : Set[int] = set()
        
        eval_time = 0
        while(eval_time < self.max_eval_time and len(covered_hashes) < self.total_fecs):
            eval_data = self.evaluator.evaluate(self.logical_scenario,
                                                None,
                                                core_id,
                                                True,
                                                eval_time,
                                                self.max_eval_time)
            if eval_data.is_valid:
                scenario = ConcreteSceneAbstractor.get_abstractions_from_eval(eval_data)
                if scenario.functional_scenario.is_relevant_by_fec:
                    if scenario.functional_scenario.fec_shape_hash() not in covered_hashes:
                        print(f"Covered FECs: {len(covered_hashes) + 1}/{self.total_fecs} with {self.evaluator.name}.")
                    covered_hashes.add(scenario.functional_scenario.fec_shape_hash())
            eval_time += eval_data.evaluation_time
            
class CSPSchedulerFactory:
    @staticmethod
    def factory(evaluator: CSPEvaluator, scenarios: List[Scenario],
                random_seed : int, warmups : int, average_time_per_scene : int, init_method : str) -> CSPScheduler:
        if len(scenarios) == 0:
            raise ValueError("No scenarios provided for CSPScheduler.")
        
        if len(scenarios) == 1 and isinstance(scenarios[0], LogicalScenario):
            return OneStepScheduler(evaluator, scenarios[0], random_seed, warmups, average_time_per_scene)
        elif isinstance(scenarios[0], FunctionalScenario):
            return MSRScheduler(evaluator, scenarios, random_seed, warmups, average_time_per_scene, init_method)
        else:
            raise ValueError(f"Unsupported scenario type: {type(scenarios[0])}. Expected LogicalScenario or FunctionalScenario.")