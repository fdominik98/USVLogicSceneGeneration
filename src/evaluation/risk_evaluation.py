import numpy as np
from utils.asv_utils import N_MILE_TO_M_CONVERSION
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from logical_level.models.actor_variable import VesselVariable

class RiskVector():
    def __init__(self, scenario: MultiLevelScenario) -> None:
        self.proximity_vectors = [ProximityRiskIndex(scenario, a1, a2) for a1, a2 in scenario.os_non_os_pairs]
        self.nav_risk_vector = NavigationRiskIndex(scenario, scenario.concrete_scene.os)
            
        self.max_proximity_index = min(self.proximity_vectors, key=lambda obj: obj.tcpa)
        #self.safe_navigation_area_index = self.nav_risk_vector.find_safe_navigation_area_index()
        self.danger_sector = self.nav_risk_vector.find_danger_sector()
        
        self.dcpa = self.max_proximity_index.dcpa
        self.tcpa = self.max_proximity_index.tcpa
        self.proximity_index = self.max_proximity_index.proximity_index
        
        #self.distance = (pow(np.e, np.linalg.norm(self.risk_vector) / np.sqrt(3)) - 1) / (np.e - 1)
        

class ProximityRiskIndex():
    def __init__(self, scenario : MultiLevelScenario, actor1 : ConcreteVessel, actor2 : ConcreteVessel) -> None:
        props = scenario.get_geo_props(actor1, actor2)
        self.dist = props.o_distance
        self.tcpa = props.tcpa
        self.dcpa = props.dcpa
        
        dr = 1 * N_MILE_TO_M_CONVERSION
        ts = 10 * 60
        
        if self.tcpa < 0 or self.tcpa > ts:
            self.dcpa_norm = 0
            self.tcpa_norm = 0
        else:       
            if self.dcpa < props.safety_dist:
                self.dcpa_norm = 1
            else:
                #self.dcpa_norm = (pow(np.e, (dr - self.dcpa) / (dr - relation.safety_dist)) - 1) / (np.e - 1)
                self.dcpa_norm = (pow(np.e, (dr - self.dcpa) / (dr - props.safety_dist)) - 1) / (np.e - 1)
            #self.tcpa_norm = (pow(np.e, (ts - self.tcpa) / ts) - 1) / (np.e - 1)
            self.tcpa_norm = (pow(np.e, (ts - self.tcpa) / ts) - 1) / (np.e - 1)
        if self.dcpa_norm * self.tcpa_norm > 0:
            self.proximity_index = np.sqrt(self.dcpa_norm * self.tcpa_norm)
        else:
            self.proximity_index = 0
        
class NavigationRiskIndex():
    def __init__(self, scenario: MultiLevelScenario, actor : ConcreteVessel) -> None:
        self.scenario = scenario
        self.scene = scenario.concrete_scene
        self.initial_state = self.scene[actor]
        self.actor = actor
        self.variable : VesselVariable = scenario.to_variable(self.actor)
    
    def find_danger_sector(self) -> float:
        for i in range(91):
            new_state = self.initial_state.modify_copy(heading=self.initial_state.heading + np.radians(i))
            new_scene = SceneBuilder(self.scene.as_dict()).set_state(self.actor, new_state).build()
            scenario = MultiLevelScenario(new_scene, self.scenario.logical_scenario, self.scenario.functional_scenario)
            if not scenario.may_collide_anyone(self.actor):
                break
        for j in range(91):
            new_state = self.initial_state.modify_copy(heading=self.initial_state.heading - np.radians(i))
            new_scene = SceneBuilder(self.scene.as_dict()).set_state(self.actor, new_state).build()
            scenario = MultiLevelScenario(new_scene, self.scenario.logical_scenario, self.scenario.functional_scenario)
            if not scenario.may_collide_anyone(self.actor):
                break
        return pow((i + j) / 180, 0.33)
            
    def find_safe_navigation_area_index(self) -> float:
        collides = 0
        no_collides = 0
        partitions = 50
        
        speeds = [i * (self.variable.max_speed / partitions)  for i in range(1, partitions + 1)]  
        for speed in speeds:
            for i in range(0, 180):
                for direction in [-1, 1]:  # -1 for counterclockwise, 1 for clockwise
                    new_state = self.initial_state.modify_copy(heading=self.initial_state.heading + direction * np.radians(i), speed=speed)
                    new_scene = SceneBuilder(self.scene.as_dict()).set_state(self.actor, new_state)
                    scenario = MultiLevelScenario(new_scene, self.scenario.logical_scenario, self.scenario.functional_scenario)
                    if scenario.may_collide_anyone(self.actor):
                        collides += 1
                    else:
                        no_collides += 1
        return (pow(np.e, collides / (collides + no_collides)) - 1) / (np.e - 1)
    