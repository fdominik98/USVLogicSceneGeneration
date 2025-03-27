import re
import subprocess
from typing import Dict, List
from concrete_level.models.actor_state import ActorState
from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from simulation.mqtt_client import MqttAgentClient, MqttScenarioClient
from simulation.sim_utils import coord_to_lat_long, waypoint_from_state
import os
import docker
import yaml
import time
from utils.file_system_utils import SIMULATION_FOLDER

class WARAPSParser():
    def __init__(self, trajectory_manager : TrajectoryManager):
        self.trajectory_manager = trajectory_manager
        
        # Load the docker-compose file
        compose_file = f"{SIMULATION_FOLDER}/docker-compose-simulation.yml"
        with open(compose_file, "r") as file:
            self.compose_config : dict = yaml.safe_load(file)

        # Start Docker client
        self.docker_client = docker.from_env()
        
        
        # self.scenario_client = MqttScenarioClient()
        # self.scenario_client.connect()
        # self.scenario_client.publish_command(trajectory_manager.concrete_scene, trajectory_manager.functional_scenario.name)
        self.agent_clients : List[MqttAgentClient] = []
        self.waypoint_map : Dict[ConcreteVessel, List[dict]] = {}
        for i, (vessel, state) in enumerate(self.trajectory_manager.concrete_scene.items()):
            self.start_container(vessel, state, 14552 + i)
            # TODO: configuring container environments for agents
            self.agent_clients.append(MqttAgentClient(vessel))
            waypoints = [waypoint_from_state(state) for state in self.trajectory_manager.trajectories[vessel]]
            self.waypoint_map[vessel] = waypoints
    
    @staticmethod
    def replace_variables(template: str, values: dict) -> str:
        """
        Replaces placeholders in the template string with corresponding values from the dictionary.
        
        :param template: The input string containing placeholders in the form ${VAR}
        :param values: A dictionary containing variable names as keys and replacement values as values.
        :return: The formatted string with placeholders replaced.
        """
        return re.sub(r"\${(.*?)}", lambda m: values.get(m.group(1), m.group(0)), template)
            
    def start_container(self, vessel : ConcreteVessel, init_state : ActorState, port : int):
        project_name = f'{self.trajectory_manager.functional_scenario.name}_{vessel.name}'.lower()
            
        vessel_pos = coord_to_lat_long(init_state.p)
        custom_env = {
            "NAME" : vessel.name,
            "DOMAIN" : "surface",
            "REAL_SIM" : "simulation",
            "AGENT_DESCRIPTION" : "surface vessel",
            "AGENT_MODEL" : "vessel.mini_usv",
            
            "VIDEO_SRC0" : "/dev/video0",
            "VIDEO_SERVER" : "ome.waraps.org",
            
            "BROKER" : "host.docker.internal",
            "PORT" : "1883",
            "TLS_CERTIFICE" : "0",
            "MQTT_USER" : "",
            "MQTT_PASSWORD" : "",
            
            "FCS_SERIAL" : "/dev/serial0",            
            "BAUD_RATE" : "57600",
            "CONNECTION_STRING" : "tcp:mavproxy:14551",
            
            "SIM_PORT": "5760",
            
            "SPEEDUP": "1",
            "VEHICLE" : "Rover",
            "MODEL": "motorboat",
            "VEHICLE_PARAMS": "Rover",
            "INSTANCE" : "1",
            
            "HOME_POS": f"{vessel_pos[0]},{vessel_pos[1]},0,{init_state.heading_deg}",
            
            "MAVPROXY": f"tcpin:mavproxy:14551",
            "LOCAL_BRIDGE": f"udp:172.17.0.1:14550",
            
            "GCS_1": f"host.docker.internal:{str(port)}",
            "GCS_2": f"host.docker.internal:{str(port)}",
        }
        
        modified_compose : dict = {'services' : dict()}
        services : Dict[str, dict] = self.compose_config.get("services", {})
        service_name_map = {service : f"{vessel.name}_{service}" for service in services.keys()}
        for service_name, service_config in services.items():
            # Modify service name (to avoid conflicts in `docker-compose ps`)
            service_name = service_name_map[service_name]
            new_service_config = service_config.copy()
            new_service_config['environment'] = custom_env
            new_service_config['command'] = self.replace_variables(service_config['command'], custom_env)
            if 'depends_on' in service_config:
                new_service_config['depends_on'] = [service_name_map[service] for service in service_config['depends_on']]
            
            modified_compose["services"][service_name] = new_service_config

        compose_filename = f"{SIMULATION_FOLDER}/docker-compose-{project_name}.yml"
        # Save as a new compose file
        with open(compose_filename, "w") as file:
            yaml.dump(modified_compose, file, default_flow_style=False)

        # Run the container in parallel
        process = subprocess.Popen(["docker-compose", "-f", compose_filename,
                                    "--project-name", project_name,
                                    "up", "-d"])
        process.wait()
        # Delete the modified compose file
        os.remove(compose_filename)
        
            