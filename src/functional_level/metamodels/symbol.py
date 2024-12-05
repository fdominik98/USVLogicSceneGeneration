
from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol(ABC):
    pass

@dataclass(frozen=True)
class BinarySymbol(Symbol, ABC):
    pass

@dataclass(frozen=True)
class UnarySymbol(Symbol, ABC):
    pass

@dataclass(frozen=True)
class HeadOnSymbol(BinarySymbol):
    pass

@dataclass(frozen=True)
class CrossingFromPortSymbol(BinarySymbol):
    pass

@dataclass(frozen=True)
class OvertakingSymbol(BinarySymbol):
    pass

@dataclass(frozen=True)
class VesselSymbol(UnarySymbol, ABC):
    pass

@dataclass(frozen=True)
class OSSymbol(VesselSymbol):
    pass

@dataclass(frozen=True)
class TSSymbol(VesselSymbol):
    pass

@dataclass(frozen=True)
class ObstacleSymbol(UnarySymbol):
    pass