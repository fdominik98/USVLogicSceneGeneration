import subprocess
from typing import Dict, List, Tuple
from haversine import Unit
import numpy as np
from concrete_level.models.actor_state import ActorState
from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from simulation.mqtt_client import MqttAgentClient, MqttScenarioClient
from simulation.sim_utils import coord_to_lat_long, true_north_heading, waypoint_from_state
import docker
import yaml
import time
from global_config import GlobalConfig
from utils.file_system_utils import SIMULATION_GEN_FOLDER
from utils.math_utils import compute_start_point

class WARAPSParser():
    def __init__(self, trajectory_manager : TrajectoryManager):
        self.trajectory_manager = trajectory_manager
        self.trajectory_manager.shift_states_to_zero()
        self.is_simulation = False
        
        # Start Docker client
        self.docker_client = docker.from_env()
        
        # self.scenario_client = MqttScenarioClient()
        # self.scenario_client.connect()
        # self.scenario_client.publish_command(trajectory_manager.concrete_scene, trajectory_manager.functional_scenario.name)
        self.agent_clients : List[MqttAgentClient] = []
        self.waypoint_map : Dict[ConcreteVessel, List[dict]] = {}
        for i, (vessel, state) in enumerate(self.trajectory_manager.concrete_scene.items()):
            if not isinstance(vessel, ConcreteVessel):
                raise ValueError(f"Vessel {vessel} is not a ConcreteVessel.")
            
            vessel_pos = compute_start_point(state.p, state.v, state.speed, vessel.max_acceleration)
            if self.is_simulation:
                self.start_container(vessel, state, vessel_pos, 14552 + i)
            # TODO: configuring container environments for agents
            self.agent_clients.append(MqttAgentClient(self.is_simulation, vessel, state, vessel_pos))
            data = self.trajectory_manager.trajectories[0:GlobalConfig.TEN_MINUTE_IN_SEC][vessel]
            waypoints = [waypoint_from_state(state) for state in data]
            self.waypoint_map[vessel] = waypoints
    
    def start_container(self, vessel : ConcreteVessel, init_state : ActorState, vessel_pos : np.ndarray, port : int):
        
        project_name = f'{self.trajectory_manager.functional_scenario.name}_{vessel.name}'.lower()
        
        process = subprocess.Popen(['docker-compose', '-p', project_name, 'down'])
        process.wait()
        
        params_file = f'{SIMULATION_GEN_FOLDER}/params-{project_name}.params'
        params = {
                    # Boat params
                    'FRAME_CLASS' : 2, # motorboat
                    'SIM_TIDE' : 0,
                    'SIM_WIND_SPD' : 0,
                    'SIM_WIND_T' : 0,
                    'SIM_WAVE_ENABLE' : 0,
                    
                    # Waypoint navigation parameters
                    'WP_PIVOT_ANGLE': 0.0,  # Angle threshold in degrees for initiating a pivot turn at a waypoint
                    'WP_RADIUS': vessel.length / 2,  # Acceptance radius in meters around a waypoint, set to half the vessel's length
                    'WP_SPEED': init_state.speed,  # Target speed in meters per second between waypoints, set to the vessel's maximum speed
                    'WPNAV_SPEED' : init_state.speed,  # Speed in meters per second for waypoint navigation, set to the vessel's maximum speed
                    'SPEED_MAX' : vessel.max_speed,
                    # Gripper control parameters
                    # 'GRIP_ENABLE': 1,  # Enables the use of a gripper; 1 for enabled, 0 for disabled
                    # 'GRIP_GRAB': 1100,  # PWM value in microseconds to command the gripper to grab a payload
                    # 'GRIP_NEUTRAL': 1500,  # PWM value in microseconds for the gripper's neutral position (neither grabbing nor releasing)
                    # 'GRIP_REGRAB': 0,  # Time in seconds to re-grip payload after releasing; 0 disables this feature
                    # 'GRIP_RELEASE': 1900,  # PWM value in microseconds to command the gripper to release a payload
                    # 'GRIP_TYPE': 1,  # Type of gripper; 1 for servo gripper, 2 for EMP gripper

                    # # Servo output functions
                    # 'SERVO9_FUNCTION': 28,  # Assigns servo output 9 to function as a gripper

                    # Obstacle avoidance parameters
                    'OA_MARGIN_MAX': vessel.radius,  # Maximum distance in meters to maintain from obstacles; 0 disables margin
                    'OA_BR_LOOKAHEAD': None,  # Lookahead distance in meters for the BendyRuler algorithm; specific value to be determined
                    'OA_BR_TYPE': None,  # Type of BendyRuler algorithm to use; specific value to be determined
                    'RNGFND_TURN_ANGL': None,  # Angle in degrees to turn when an obstacle is detected by the rangefinder; specific value to be determined
                    'RNGFND_TURN_TIME': None,  # Time in seconds to execute the turn when an obstacle is detected; specific value to be determined
                    'RNGFND_TRIGGER_CM': None,  # Distance in centimeters at which the rangefinder triggers an obstacle avoidance maneuver; specific value to be determined
                    
                    # Speed and steering control gains
                    'ATC_SPEED_P': 0.1,  # Proportional gain for speed control loop
                    'ATC_STR_RAT_FF': 0.75,  # Feedforward term for steering rate control
                    'ATC_ACCEL_MAX' : vessel.max_acceleration,
                    'WPNAV_ACCEL' : vessel.max_acceleration ,
                    
                    # Battery monitoring setup
                    'BATT_MONITOR': 4,  # Type of battery monitoring (e.g., analog voltage and current sensing)

                    # Cruise control settings
                    'CRUISE_SPEED': init_state.speed,  # Target speed in meters per second for autonomous modes
                    'CRUISE_THROTTLE' : 30, # Initial throttle percentage to achieve cruise speed
                    # 'CRUISE_THROTTLE': 30,  # Initial throttle percentage to achieve cruise speed

                    # 'SERVO1_FUNCTION': 73,  # Function assigned to servo output 1 (Throttle Left)
                    # 'SERVO3_FUNCTION': 74,  # Function assigned to servo output 3 (Throttle Right)
        }
        
        
        with open(params_file, 'w') as file:
            for key, value in params.items():
                if value is not None:
                    file.write(f'{key}\t{value}\n')
                
           
        mavproxy = f'{vessel.name}_mavproxy'
        arduagent = f'{vessel.name}_arduagent'
        simulator = f'{vessel.name}_simulator'
            
        # Shift the position to let the ship accelerate
        
        start_pos_lat_long = coord_to_lat_long(init_state.p)
        env = {
            'NAME' : vessel.name,
            'DOMAIN' : 'surface',
            'REAL_SIM' : 'simulation',
            'AGENT_DESCRIPTION' : 'surface vessel',
            'AGENT_MODEL' : 'vessel.mini_usv',
            
            'VIDEO_SRC0' : '/dev/video0',
            'VIDEO_SERVER' : 'ome.waraps.org',
            
            'BROKER' : 'host.docker.internal',
            #'PORT' : '1883',
            'PORT' : '1882',
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
            'VEHICLE_PARAMS': 'motorboat',
            'INSTANCE' : '0',
            
            'HOME_POS': f'{start_pos_lat_long[0]},{start_pos_lat_long[1]},0,{true_north_heading(vessel_pos, init_state.p, Unit.DEGREES)}',
            
            'MAVPROXY': f'tcpin:{mavproxy}:14551',
            'LOCAL_BRIDGE': f'udp:host.docker.internal:14550',
            
            'GCS_1': f'udp:host.docker.internal:{str(port)}',
        }
        env_list = [f'{name}={value}' for name, value in env.items()]
        
        docker_compose = {
            'services' : {                
                simulator : {
                    'image' : f'registry.waraps.org/ardupilot-sitl:latest',
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    'volumes' : [f'{params_file}:/params/my{env["VEHICLE_PARAMS"]}.params'],
                    #'command': f'/ardupilot/Tools/autotest/sim_vehicle.py --vehicle {env["VEHICLE"]} --frame {env["MODEL"]} -I{env["INSTANCE"]} --custom-location="{env["HOME_POS"]}" -w --no-rebuild --no-mavproxy --speedup {env["SPEEDUP"]}'
                },
                
                mavproxy : {
                    'image' : 'registry.waraps.org/waraps-mavproxy:latest',
                    'depends_on' : [simulator],
                    'tty' : True,
                    'stdin_open' : True,
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    # 'command' : f'mavproxy.py --master=tcp:{simulator}:{env["SIM_PORT"]} --out={env["MAVPROXY"]} --out={env["LOCAL_BRIDGE"]} --out={env["GCS_1"]}',  
                    'command' : f'mavproxy.py --master=tcp:{simulator}:{env["SIM_PORT"]} --out={env["MAVPROXY"]} --out={env["GCS_1"]}',                   
                },
                
                arduagent : {
                    'image' : f'registry.waraps.org/waraps-arduagent:latest',
                    'depends_on' : [mavproxy, simulator],
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    'command' : 'python -B -u /app/main.py'
                }
            }
        }

        compose_filename = f'{SIMULATION_GEN_FOLDER}/docker-compose-{project_name}.yml'
        # Save as a new compose file
        with open(compose_filename, 'w') as file:
            yaml.dump(docker_compose, file, default_flow_style=False)

        # Run the container in parallel
        process = subprocess.Popen(['docker-compose', '-f', compose_filename,
                                    '--project-name', project_name,
                                    'up', '-d'])
        process.wait()
        
        