from dataclasses import dataclass


VESSEL_AGENT_MAP = {
    0 : ('MiniUSV3', False),
    1 : ('MiniUSV2', True),
    2 : ('MiniUSV1', True),
    3 : ('MiniUSV4', True),
}


@dataclass(frozen=True)
class MQttConnectionInfo():
    user : str = ''
    password : str = ''
    broker: str = 'localhost'
    port: int = 1882 # '1883'
    tls_connection: bool = False
    allow_certificates = False