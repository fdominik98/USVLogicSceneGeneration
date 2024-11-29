from dataclasses import dataclass
from src.model.vessel import VesselDesc

@dataclass(frozen=True)
class VesselVariable():
    desc : VesselDesc
    
    def __post_init__(self):
        self.id = self.desc.id
        self.is_os = self.desc.is_os()
        self.name = 'OS' if self.is_os() else f'TS_{self.id}'
        self.max_speed = self.desc.max_speed
        self.min_speed = self.desc.min_speed
        self.max_length = self.desc.max_length
        self.min_length = self.desc.min_length
                
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    

 