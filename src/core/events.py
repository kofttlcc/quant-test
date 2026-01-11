from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, Optional
import time

class EventType(Enum):
    """Standard Event Types for the Hybrid Core."""
    MARKET_DATA = auto()
    SIGNAL = auto()
    ORDER = auto()
    FILL = auto()
    ERROR = auto()
    SYSTEM = auto()

@dataclass
class Event:
    """Base Event Class."""
    type: EventType
    payload: Any
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
