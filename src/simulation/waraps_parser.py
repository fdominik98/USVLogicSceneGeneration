import subprocess
from typing import Dict, List
from concrete_level.models.actor_state import ActorState
from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from simulation.mqtt_client import MqttAgentClient, MqttScenarioClient
from simulation.sim_utils import coord_to_lat_long, waypoint_from_state, to_true_north
import os
import docker
import yaml
import time
from utils.asv_utils import TEN_MINUTE_IN_SEC
from utils.file_system_utils import SIMULATION_FOLDER

class WARAPSParser():
    def __init__(self, trajectory_manager : TrajectoryManager):
        self.trajectory_manager = trajectory_manager
        
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
            data = self.trajectory_manager.trajectories[0:TEN_MINUTE_IN_SEC][vessel]
            waypoints = [waypoint_from_state(state) for state in data]
            self.waypoint_map[vessel] = waypoints
    
    def start_container(self, vessel : ConcreteVessel, init_state : ActorState, port : int):
        project_name = f'{self.trajectory_manager.functional_scenario.name}_{vessel.name}'.lower()
        
        process = subprocess.Popen(['docker-compose', '-p', project_name, 'down'])
        process.wait()
        
        params_file = f'{SIMULATION_FOLDER}/params-{project_name}.params'
        params = {
                    # Waypoint navigation parameters
                    'WP_PIVOT_ANGLE': 0.0,  # Angle threshold in degrees for initiating a pivot turn at a waypoint
                    'WP_RADIUS': vessel.length / 2,  # Acceptance radius in meters around a waypoint, set to half the vessel's length
                    'WP_SPEED': vessel.max_speed,  # Target speed in meters per second between waypoints, set to the vessel's maximum speed

                    # Gripper control parameters
                    'GRIP_ENABLE': 1,  # Enables the use of a gripper; 1 for enabled, 0 for disabled
                    'GRIP_GRAB': 1100,  # PWM value in microseconds to command the gripper to grab a payload
                    'GRIP_NEUTRAL': 1500,  # PWM value in microseconds for the gripper's neutral position (neither grabbing nor releasing)
                    'GRIP_REGRAB': 0,  # Time in seconds to re-grip payload after releasing; 0 disables this feature
                    'GRIP_RELEASE': 1900,  # PWM value in microseconds to command the gripper to release a payload
                    'GRIP_TYPE': 1,  # Type of gripper; 1 for servo gripper, 2 for EMP gripper

                    # Radio control options
                    'RC7_OPTION': 19,  # Assigns RC channel 7 to control the gripper; 19 corresponds to the 'Gripper' function

                    # Servo output functions
                    'SERVO9_FUNCTION': 28,  # Assigns servo output 9 to function as a gripper
                    'SERVO1_FUNCTION': 73,  # Assigns servo output 1 to control the left throttle (for skid-steering vehicles)
                    'SERVO3_FUNCTION': 74,  # Assigns servo output 3 to control the right throttle (for skid-steering vehicles)

                    # Obstacle avoidance parameters
                    'OA_MARGIN_MAX': vessel.radius,  # Maximum distance in meters to maintain from obstacles; 0 disables margin
                    'OA_BR_LOOKAHEAD': None,  # Lookahead distance in meters for the BendyRuler algorithm; specific value to be determined
                    'OA_BR_TYPE': None,  # Type of BendyRuler algorithm to use; specific value to be determined
                    'RNGFND_TURN_ANGL': None,  # Angle in degrees to turn when an obstacle is detected by the rangefinder; specific value to be determined
                    'RNGFND_TURN_TIME': None,  # Time in seconds to execute the turn when an obstacle is detected; specific value to be determined
                    'RNGFND_TRIGGER_CM': None,  # Distance in centimeters at which the rangefinder triggers an obstacle avoidance maneuver; specific value to be determined
                    
                    # FROM ROVER DEFAULT PARAMS
                    # Airspeed sensor configuration
                    'ARSPD_PIN': 1,  # Analog pin assigned for airspeed sensor input
                    'ARSPD_BUS': 2,  # I2C bus number for airspeed sensor communication

                    # Speed and steering control gains
                    'ATC_SPEED_P': 0.1,  # Proportional gain for speed control loop
                    'ATC_STR_RAT_FF': 0.75,  # Feedforward term for steering rate control

                    # Battery monitoring setup
                    'BATT_MONITOR': 4,  # Type of battery monitoring (e.g., analog voltage and current sensing)

                    # Cruise control settings
                    'CRUISE_SPEED': init_state.speed,  # Target speed in meters per second for autonomous modes
                    'CRUISE_THROTTLE': 30,  # Initial throttle percentage to achieve cruise speed

                    # Accelerometer calibration offsets and scaling factors for the second accelerometer
                    'INS_ACC2OFFS_X': 0.001,  # Offset correction for X-axis
                    'INS_ACC2OFFS_Y': 0.001,  # Offset correction for Y-axis
                    'INS_ACC2OFFS_Z': 0.001,  # Offset correction for Z-axis
                    'INS_ACC2SCAL_X': 1.001,  # Scaling factor for X-axis
                    'INS_ACC2SCAL_Y': 1.001,  # Scaling factor for Y-axis
                    'INS_ACC2SCAL_Z': 1.001,  # Scaling factor for Z-axis

                    # Accelerometer calibration offsets and scaling factors for the primary accelerometer
                    'INS_ACCOFFS_X': 0.001,  # Offset correction for X-axis
                    'INS_ACCOFFS_Y': 0.001,  # Offset correction for Y-axis
                    'INS_ACCOFFS_Z': 0.001,  # Offset correction for Z-axis
                    'INS_ACCSCAL_X': 1.001,  # Scaling factor for X-axis
                    'INS_ACCSCAL_Y': 1.001,  # Scaling factor for Y-axis
                    'INS_ACCSCAL_Z': 1.001,  # Scaling factor for Z-axis

                    # Flight mode assignments
                    'MODE3': 11,  # Flight mode assigned to position 3 (e.g., Auto mode)
                    'MODE4': 10,  # Flight mode assigned to position 4 (e.g., Steering mode)
                    'MODE5': 2,   # Flight mode assigned to position 5 (e.g., Acro mode)

                    # Radio control input ranges
                    'RC1_MAX': 2000,  # Maximum pulse width for RC channel 1 (steering)
                    'RC1_MIN': 1000,  # Minimum pulse width for RC channel 1
                    'RC3_MAX': 2000,  # Maximum pulse width for RC channel 3 (throttle)
                    'RC3_MIN': 1000,  # Minimum pulse width for RC channel 3

                    # Relay pin assignments
                    'RELAY1_PIN': 1,  # GPIO pin assigned to relay 1
                    'RELAY2_PIN': 2,  # GPIO pin assigned to relay 2

                    # Servo output ranges
                    'SERVO1_MIN': 1000,  # Minimum pulse width for servo output 1
                    'SERVO1_MAX': 2000,  # Maximum pulse width for servo output 1
                    'SERVO3_MIN': 1000,  # Minimum pulse width for servo output 3
                    'SERVO3_MAX': 2000,  # Maximum pulse width for servo output 3

                    # Simulation settings
                    'SIM_PIN_MASK': 127,  # Bitmask for enabling/disabling simulated pins

                    # Logging configuration
                    'INS_LOG_BAT_MASK': 127,  # Bitmask for enabling IMU logging during flight

                    # FROM ROVER-SKID DEFAULT PARAMS
                    # Skid-steering specific parameters
                    'SERVO1_FUNCTION': 73,  # Function assigned to servo output 1 (Throttle Left)
                    'SERVO3_FUNCTION': 74,  # Function assigned to servo output 3 (Throttle Right)
        }
        
        
        with open(params_file, 'w') as file:
            for key, value in params.items():
                if value is not None:
                    file.write(f'{key}\t{value}\n')
                
           
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
            'MODEL': 'rover-skid',
            'VEHICLE_PARAMS': 'Rover',
            'INSTANCE' : '0',
            
            'HOME_POS': f'{vessel_pos[0]},{vessel_pos[1]},0,{to_true_north(init_state.heading_deg)}',
            
            'MAVPROXY': f'tcpin:{mavproxy}:14551',
            'LOCAL_BRIDGE': f'udp:localhost:14550',
            
            'GCS_1': f'udp:host.docker.internal:{str(port)}',
        }
        env_list = [f'{name}={value}' for name, value in env.items()]
        
        docker_compose = {
            'services' : {                
                simulator : {
                    'image' : 'registry.waraps.org/ardupilot-sitl:latest',
                    'restart' : 'unless-stopped',
                    'environment' : env_list,
                    'volumes' : [f'{params_file}:/params/my{env["VEHICLE_PARAMS"]}.params'],
                    #'command' : f'/ardupilot/Tools/autotest/sim_vehicle.py --vehicle {env['VEHICLE']} --frame {env['MODEL']} -I{env['INSTANCE']} --custom-location="{env['HOME_POS']}" --add-param-file=/params/my{env['VEHICLE_PARAMS']}.params -w --no-rebuild --no-mavproxy --speedup {env['SPEEDUP']}'
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
                    'image' : 'registry.waraps.org/waraps-arduagent:test',
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
        # os.remove(compose_filename)
        # os.remove(params_file)
        
        