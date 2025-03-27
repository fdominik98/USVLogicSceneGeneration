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
from utils.asv_utils import absolute_to_true_north
from utils.file_system_utils import SIMULATION_FOLDER

class WARAPSParser():
    def __init__(self, trajectory_manager : TrajectoryManager):
        self.trajectory_manager = trajectory_manager
        
        # Load the docker-compose file
        compose_file = f'{SIMULATION_FOLDER}/docker-compose-simulation.yml'
        with open(compose_file, 'r') as file:
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
    
    def start_container(self, vessel : ConcreteVessel, init_state : ActorState, port : int):
        project_name = f'{self.trajectory_manager.functional_scenario.name}_{vessel.name}'.lower()
        
        process = subprocess.Popen(['docker-compose', '-p', project_name, 'down'])
        process.wait()
        
           
        mavproxy = f'{vessel.name}_mavproxy'
        arduagent = f'{vessel.name}_arduagent'
        simulator = f'{vessel.name}_simulator'
            
        vessel_pos = coord_to_lat_long(init_state.p)
        env = {
            'NAME' : vessel.name,
            'DOMAIN' : 'surface',
            'REAL_SIM' : 'simulation',
            'AGENT_DESCRIPTION' : 'surface vessel',
            'AGENT_MODEL' : 'vessel.mini_usv',
            
            'VIDEO_SRC0' : '/dev/video0',
            'VIDEO_SERVER' : 'ome.waraps.org',
            
            'BROKER' : 'host.docker.internal',
            'PORT' : '1883',
            'TLS_CERTIFICE' : '0',
            'MQTT_USER' : '',
            'MQTT_PASSWORD' : '',
            
            'FCS_SERIAL' : '/dev/serial0',            
            'BAUD_RATE' : '57600',
            'CONNECTION_STRING' : f'tcp:{mavproxy}:14551',
            
            'SIM_PORT': '5760',
            
            'SPEEDUP': '1',
            'VEHICLE' : 'Rover',
            'MODEL': 'motorboat',
            'VEHICLE_PARAMS': 'Rover',
            'INSTANCE' : '0',
            
            'HOME_POS': f'{vessel_pos[0]},{vessel_pos[1]},0,{absolute_to_true_north(init_state.heading_deg)}',
            
            'MAVPROXY': f'tcpin:{mavproxy}:14551',
            'LOCAL_BRIDGE': f'udp:localhost:14550',
            
            'GCS_1': f'udp:localhost:{str(port)}',
        }
        env_list = [f'{name}={value}' for name, value in env.items()]
        
        docker_compose = {
            'services' : {                
                simulator : {
                    'image' : 'registry.waraps.org/ardupilot-sitl:latest',
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    #'command' : f'/ardupilot/Tools/autotest/sim_vehicle.py --vehicle {env['VEHICLE']} --frame {env['MODEL']} -I{env['INSTANCE']} --custom-location="{env['HOME_POS']}" --add-param-file=/params/my{env['VEHICLE_PARAMS']}.params -w --no-rebuild --no-mavproxy --speedup {env['SPEEDUP']}'
                },
                
                mavproxy : {
                    'image' : 'registry.waraps.org/waraps-mavproxy:latest',
                    'depends_on' : [simulator],
                    'tty' : True,
                    'stdin_open' : True,
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    'command' :f'mavproxy.py --master=tcp:{simulator}:{env['SIM_PORT']} --out={env['MAVPROXY']} --out={env['LOCAL_BRIDGE']} --out={env['GCS_1']}'
                },
                
                arduagent : {
                    'image' : 'registry.waraps.org/waraps-arduagent:latest',
                    'depends_on' : [mavproxy, simulator],
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    'command' : 'python -B -u /app/main.py'
                }
            }
        }

        compose_filename = f'{SIMULATION_FOLDER}/docker-compose-{project_name}.yml'
        # Save as a new compose file
        with open(compose_filename, 'w') as file:
            yaml.dump(docker_compose, file, default_flow_style=False)

        # Run the container in parallel
        process = subprocess.Popen(['docker-compose', '-f', compose_filename,
                                    '--project-name', project_name,
                                    'up', '-d'])
        process.wait()
        # Delete the modified compose file
        os.remove(compose_filename)
        
            