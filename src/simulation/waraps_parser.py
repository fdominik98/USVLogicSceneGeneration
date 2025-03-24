from typing import Dict, List
import docker
from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from simulation.mqtt_client import MqttAgentClient, MqttScenarioClient
from simulation.sim_utils import waypoint_from_state


class WARAPSParser():
    def __init__(self, trajectory_manager : TrajectoryManager):
        self.scenario_client = MqttScenarioClient()
        self.scenario_client.connect()
        self.scenario_client.publish_command(trajectory_manager.concrete_scene, trajectory_manager.functional_scenario.name)
        self.agent_clients : List[MqttAgentClient] = []
        self.waypoint_map : Dict[ConcreteVessel, List[dict]] = {}
        for vessel in trajectory_manager.concrete_scene.vessels:
            # TODO: configuring container environments for agents
            self.agent_clients.append(MqttAgentClient(vessel))
            waypoints = [waypoint_from_state(state) for state in trajectory_manager.trajectories[vessel]]
            self.waypoint_map[vessel] = waypoints
            
            
            
            

            