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


@dataclass(frozen=True)
class MQttConnectionInfo():
    user : str = ''
    password : str = ''
    broker: str = 'localhost'
    port: int = 1882
    tls_connection: bool = False
    allow_certificates = False

class MqttClient(ABC):
   
    def __init__(self, is_simulation):
        self.running_tasks : Set[str] = set()
        
        if is_simulation:
            self.connection_info = MQttConnectionInfo()
        else:
            self.connection_info = MQttConnectionInfo(user='mqtt', password='Check', broker='broker.waraps.org', port=8883, tls_connection=True,
                                                      allow_certificates=False)
        
        
        self.client = mqtt.Client(client_id=self.name)
        self.client.user_data_set('waraps')
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
    
    
    def connect(self):
        '''Connect to the broker using the mqtt client'''
        if self.connection_info.tls_connection:
            self.client.username_pw_set(self.connection_info.user, self.connection_info.password)
            self.client.tls_set(cert_reqs=(ssl.CERT_NONE if self.connection_info.allow_certificates else ssl.CERT_REQUIRED),)
            self.client.tls_insecure_set(True)
        try:
            res = None
            while res is None or res is not mqtt.MQTTErrorCode.MQTT_ERR_SUCCESS:
                res : mqtt.MQTTErrorCode = self.client.connect(self.connection_info.broker, self.connection_info.port, 60)
                print(f'{self.name} connection result: {res}')
            self.client.loop_start()
        except Exception as exc:
            print(f'{self.name} failed to connect to broker {self.connection_info.broker}:{self.connection_info.port}')
            print(exc)
            print(f'Continue without {self.receiver_name}.')
            
    def on_connect(self, client, userdata, flags, rc):
        '''Callback triggered when the client connects to the broker'''
        try:
            if rc == 0:
                print(f'{self.name} connected to MQTT Broker: {self.connection_info.broker}:{self.connection_info.port}')
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
    
    vessel_id_name_map = {
        0 : 'MiniUSV1',
        1 : 'MiniUSV2',
        2 : 'MiniUSV3',
        3 : 'MiniUSV4',
    }
    
    def __init__(self, is_simulation : bool, vessel : ConcreteVessel, initial_state : ActorState, vessel_pos : np.ndarray):
        self.is_simulation = is_simulation
        self.simulation_str = 'simulation' if is_simulation else 'real'
        self.vessel = vessel
        self.initial_state = initial_state
        self.vessel_pos = vessel_pos
        self.vessel_name = self.vessel.name if is_simulation else self.vessel_id_name_map[vessel.id]
        super().__init__(is_simulation)
        
    @property
    def listen_topics(self) -> List[str]:
        return [f'waraps/unit/surface/{self.simulation_str}/{self.vessel_name}/exec/response',
                f'waraps/unit/surface/{self.simulation_str}/{self.vessel_name}/exec/feedback']
    
    @property
    def base_topic(self) -> str:
        return f'waraps/unit/surface/{self.simulation_str}/{self.vessel_name}/exec/command'
    
    @property
    def receiver_name(self) -> str:
        return self.vessel_name
            
            
    def publish_follow_path(self, waypoints : List[dict], speed):
        command = {
            'com-uuid': str(uuid.uuid4()),
            'command': 'start-task',
            'execution-unit': f'{self.vessel_name}',
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
            'execution-unit': f'{self.vessel_name}',
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
        #         'execution-unit': f'{self.vessel_name}',
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
        

        