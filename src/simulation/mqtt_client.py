from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
import json
import ssl
import traceback
from typing import Any, Dict, List, Set
import uuid
import numpy as np
import paho.mqtt.client as mqtt

from concrete_level.models.actor_state import ActorState
from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.concrete_scene import ConcreteScene
from simulation.sim_utils import waypoint_from_state

class MqttClient(ABC):
    '''Mqtt connection information'''
    user : str = ''
    password : str = ''
    broker: str = 'localhost'
    port: int = 1882
    tls_connection: bool = False
    running_tasks : Set[str] = set()
    
    def __init__(self):
        self.client = mqtt.Client(client_id=self.name)
        self.client.user_data_set('waraps')
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
    
    
    def connect(self):
        '''Connect to the broker using the mqtt client'''
        if self.tls_connection:
            self.client.username_pw_set(self.user, self.password)
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)
        try:
            res = None
            while res is None or res is not mqtt.MQTTErrorCode.MQTT_ERR_SUCCESS:
                res : mqtt.MQTTErrorCode = self.client.connect(self.broker, self.port, 60)
                print(f'{self.name} connection result: {res}')
            self.client.loop_start()
        except Exception as exc:
            print(f'{self.name} failed to connect to broker {self.broker}:{self.port}')
            print(exc)
            exit()
            
    def on_connect(self, client, userdata, flags, rc):
        '''Callback triggered when the client connects to the broker'''
        try:
            if rc == 0:
                print(f'{self.name} connected to MQTT Broker: {self.broker}:{self.port}')
                for listen_topic in self.listen_topics:
                    self.client.subscribe(listen_topic)
                    print(f'Subscribing to {listen_topic}')
            else:
                print(f'Error to connect : {rc}')
        except Exception:
            print(traceback.format_exc())

    def on_disconnect(self, client, userdata, rc):
        '''Is triggered when the client gets disconnected from the broker'''
        print(f'{self.name} got disconnected from the broker {userdata} with code {rc}')
        if rc == 5:
            print('No (or Wrong) Credentials.')
            
            
    def on_message(self, client, userdata, msg : mqtt.MQTTMessage):
        '''Is triggered when a message is published on topics agent subscribes to'''
        try:
            msg_str = msg.payload.decode('utf-8')
            msg_dict = json.loads(msg_str)
            print(f'Received from {self.receiver_name}: {msg_dict}')
            if 'status' in msg_dict:
                if msg_dict['status'] == 'running' or msg_dict['status'] == 'started' or msg_dict['status'] == 'planning':
                    self.running_tasks.add(msg_dict['task-uuid'])
                if msg_dict['status'] == 'failed' or msg_dict['status'] == 'finished' or msg_dict['status'] == 'aborted':
                    self.running_tasks.discard(msg_dict['task-uuid'])
            elif 'response' in msg_dict:
                if msg_dict['response'] == 'running':
                    self.running_tasks.add(msg_dict['task-uuid'])
                if msg_dict['response'] == 'failed' or msg_dict['response'] == 'finished':
                    self.running_tasks.discard(msg_dict['task-uuid'])
        except Exception:
            print(traceback.format_exc())

    @property
    def name(self) -> str:
        return f'{self.receiver_name}_client'
    
    @property
    @abstractmethod
    def receiver_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def listen_topics(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def base_topic(self) -> str:
        pass
    
    def disconnect(self):
        self.client.disconnect()     
        
        
class MqttAgentClient(MqttClient):
    def __init__(self, vessel : ConcreteVessel, initial_state : ActorState, vessel_pos : np.ndarray):
        self.vessel = vessel
        self.initial_state = initial_state
        self.vessel_pos = vessel_pos
        super().__init__()
        
    @property
    def listen_topics(self) -> List[str]:
        return [f'waraps/unit/surface/simulation/{self.vessel.name}/exec/response',
                f'waraps/unit/surface/simulation/{self.vessel.name}/exec/feedback']
    
    @property
    def base_topic(self) -> str:
        return f'waraps/unit/surface/simulation/{self.vessel.name}/exec/command'
    
    @property
    def receiver_name(self) -> str:
        return self.vessel.name
            
            
    def publish_follow_path(self, waypoints : List[dict], speed):
        command = {
            'com-uuid': str(uuid.uuid4()),
            'command': 'start-task',
            'execution-unit': f'{self.vessel.name}',
            'sender': self.name,
            'task': {
                'name': 'move-path',
                'params': {
                'speed': str(speed),
                'waypoints': waypoints,
                'loop' : False,
                }
            },
            'task-uuid': str(uuid.uuid4()),
            'time_added': 0
        }
        str_command = json.dumps(command)
        self.client.publish(self.base_topic, str_command)   
        
    def publish_abort_all(self):
        for task in self.running_tasks:
            command = {
                'com-uuid': str(uuid.uuid4()),
                'command': 'signal-task',
                'sender': self.name,
                'signal': '$abort',
                'task-uuid': task
            }
            str_command = json.dumps(command)
            self.client.publish(self.base_topic, str_command)
            
    def publish_go_to(self, waypoint : np.ndarray, speed, look_at : np.ndarray = None):
        command = {
            'com-uuid': str(uuid.uuid4()),
            'command': 'start-task',
            'execution-unit': f'{self.vessel.name}',
            'sender': self.name,
            'task': {
                'name': 'move-to',
                'params': {
                'speed': str(speed),
                'waypoint': {
                    'altitude': 0,
                    'latitude': waypoint[0],
                    'longitude': waypoint[1],
                    'rostype': 'GeoPoint'
                }
                }
            },
            'task-uuid': str(uuid.uuid4()),
            'time_added': 0
        }
        str_command = json.dumps(command)
        self.client.publish(self.base_topic, str_command)
        
        # if look_at is not None:
        #     command = {
        #         'com-uuid': str(uuid.uuid4()),
        #         'command': 'start-task',
        #         'execution-unit': f'{self.vessel.name}',
        #         'sender': self.name,
        #         'task': {
        #             'name': 'look-at-position',
        #             'params': {
        #             'geopoint': {
        #                 'latitude': look_at[0],
        #                 'longitude': look_at[1],
        #                 'altitude': 0
        #             }
        #             },
        #             'task-uuid': str(uuid.uuid4())
        #         }
        #     }
        #     str_command = json.dumps(command)
        #     self.client.publish(self.base_topic, str_command)
        

class MqttScenarioClient(MqttClient):
    
    @property
    def receiver_name(self) -> str:
        return 'genesis_backend'
    
    @property
    def listen_topics(self) -> List[str]:
        return [f'waraps/service/virtual/real/realgenesis1/exec/response',
                f'waraps/service/virtual/real/realgenesis1/exec/feedback']
    
    @property
    def base_topic(self) -> str:
        return f'waraps/service/virtual/real/realgenesis1/exec/command'
    
    def publish_command(self, scene : ConcreteScene, scenario_name : str):
        vessel_dict : Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(dict))
        for vessel in scene.vessels:
            waypoint = waypoint_from_state(scene[vessel])
            vessel_dict[vessel.name]['coordinates'] = [{'lat' : waypoint['latitude'], 'lng' : waypoint['longitude']}]
            vessel_dict[vessel.name]['image'] = 'boat'
            vessel_dict[vessel.name]['imageObj'] = {'name': 'boat', 'type': 'boat', 'icon': '/icons/simulated_boat.svg', 'parent': False, 'mapObject': False,
                                    'modules': {'gazebo': {'active': False, 'camera': False}, 'team_leader': {'active': False}, 'object_detection': {'active': False}}}
            vessel_dict[vessel.name]['children'] = []
            vessel_dict[vessel.name]['resource_pools'] = []
            vessel_dict[vessel.name]['name'] = vessel.name
            
        command = {
            'com-uuid': str(uuid.uuid4()),
            'command': 'start-task',
            'execution-unit': self.receiver_name,
            'sender': self.name,
            'task': {
                'name': 'generate-scenario',
                'params': {
                'scenario': vessel_dict,
                'scenarioName': scenario_name
                }
            },
            'task-uuid': str(uuid.uuid4())
        }
        str_command = json.dumps(command)
        self.client.publish(self.base_topic, str_command)   
        