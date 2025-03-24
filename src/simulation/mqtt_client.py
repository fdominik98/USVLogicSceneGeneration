from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
import json
import ssl
import traceback
from typing import Any, Dict, List
import uuid
import paho.mqtt.client as mqtt

from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.concrete_scene import ConcreteScene
from simulation.sim_utils import waypoint_from_state

@dataclass(frozen=True)
class MqttClient(ABC):
    """Mqtt connection information"""
    client: mqtt.Client = field(init=False)
    user: str = field(default='', init=False)
    password: str = field(default='', init=False)
    broker: str = field(default='host.docker.internal', init=False)
    port: int = field(default=1883, init=False)
    tls_connection: bool = field(default=False, init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'client', mqtt.Client(client_id=self.name))
        self.client.user_data_set("waraps")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
    
    
    def connect(self):
        """Connect to the broker using the mqtt client"""
        if self.tls_connection:
            self.client.username_pw_set(self.user, self.password)
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as exc:
            print(f"{self.name} failed to connect to broker {self.broker}:{self.port}")
            print(exc)
            exit()
            
    def on_connect(self, client, userdata, flags, rc):
        """Callback triggered when the client connects to the broker"""
        try:
            if rc == 0:
                print(f"{self.name} connected to MQTT Broker: {self.broker}:{self.port}")
                for listen_topic in self.listen_topics:
                    self.client.subscribe(listen_topic)
                    print(f"Subscribing to {listen_topic}")
            else:
                print(f"Error to connect : {rc}")
        except Exception:
            print(traceback.format_exc())

    def on_disconnect(self, client, userdata, rc):
        """Is triggered when the client gets disconnected from the broker"""
        print(f"{self.name} got disconnected from the broker {userdata} with code {rc}")
        if rc == 5:
            print("No (or Wrong) Credentials.")
            
            
    def on_message(self, client, userdata, msg : mqtt.MQTTMessage):
        """Is triggered when a message is published on topics agent subscribes to"""
        try:
            msg_str = msg.payload.decode("utf-8")
            print(f'Received from {self.receiver_name}: {json.loads(msg_str)}')
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
        
        
@dataclass(frozen=True)
class MqttAgentClient(MqttClient):
    vessel : ConcreteVessel
        
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
            
            
    def publish_command(self, waypoints : List[dict]):
        command = {
            "com-uuid": str(uuid.uuid4()),
            "command": "start-task",
            "execution-unit": f"{self.vessel.name}",
            "sender": self.name,
            "task": {
                "name": "move-path",
                "params": {
                "speed": "standard",
                "waypoints": waypoints,
                
                }
            },
            "task-uuid": str(uuid.uuid4()),
            "time_added": 0
        }
        str_command = json.dumps(command)
        self.client.publish(self.base_topic, str_command)   
        

@dataclass(frozen=True)
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
            vessel_dict[vessel.name]["coordinates"] = [{"lat" : waypoint["latitude"], "long" : waypoint["longitude"]}]
            vessel_dict[vessel.name]["image"] = "boat"
            vessel_dict[vessel.name]["imageObj"] = {"name": "boat", "type": "boat", "icon": "/icons/simulated_boat.svg", "parent": False, "mapObject": False,
                                    "modules": {"gazebo": {"active": False, "camera": False}, "team_leader": {"active": False}, "object_detection": {"active": False}}}
            vessel_dict[vessel.name]["children"] = []
            vessel_dict[vessel.name]["resource_pools"] = []
            vessel_dict[vessel.name]["name"] = vessel.name
            
        command = {
            "com-uuid": str(uuid.uuid4()),
            "command": "start-task",
            "execution-unit": self.receiver_name,
            "sender": self.name,
            "task": {
                "name": "generate-scenario",
                "params": {
                "scenario": vessel_dict,
                "scenarioName": scenario_name
                }
            },
            "task-uuid": str(uuid.uuid4())
        }
        str_command = json.dumps(command)
        self.client.publish(self.base_topic, str_command)   
        