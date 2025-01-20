from typing import Union

from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from concrete_level.models.trajectories import Trajectories
from concrete_level.trajectory_generation.trajectory_builder import TrajectoryBuilder


class TrajectoryManager():
    def __init__(self, trajectories : Union[Trajectories, ConcreteScene]) -> None:
        
        if isinstance(trajectories, ConcreteScene):
            self.trajectories = TrajectoryBuilder.default_trajectory_from_scene(trajectories)
        elif isinstance(trajectories, Trajectories):
            self.trajectories : Trajectories = trajectories            
        else:
            raise ValueError('The passed parameter has incorrect type.')
            
        self.scenario = ConcreteSceneAbstractor.get_abstractions_from_concrete(self.trajectories.get_scene(0))
        self.logical_scenario = self.scenario.logical_scenario
        self.functional_scenario = self.scenario.functional_scenario
        self.concrete_scene = self.scenario.concrete_scene
        
    def get_scenario(self, t : int) -> MultiLevelScenario:
        return MultiLevelScenario(self.trajectories.get_scene(t), self.logical_scenario, self.functional_scenario)
    
    @property
    def timespan(self):
        return self.trajectories.timespan