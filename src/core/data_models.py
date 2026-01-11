from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class Bar:
    """
    Standard OHLCV Bar Data Model.
    Compatible with QuantConnect/Lean specifications.
    """
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    period: timedelta = timedelta(minutes=1)
    
    @property
    def end_time(self) -> datetime:
        return self.time + self.period

@dataclass
class Tick:
    """
    Tick Data Model for high-frequency compatible streams.
    """
    symbol: str
    time: datetime
    price: float
    volume: float = 0.0
    
@dataclass
class Quote:
    """
    L1 Quote Data (Bid/Ask).
    """
    symbol: str
    time: datetime
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float
