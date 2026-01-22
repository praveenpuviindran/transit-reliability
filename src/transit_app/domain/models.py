from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Prediction:
    """
    A normalized real-time prediction for a vehicle arriving/departing a stop.
    We keep this minimal for Slice 1. Will expand later.
    """
    stop_id: str
    route_id: Optional[str]
    trip_id: Optional[str]
    direction_id: Optional[int]
    arrival_time: Optional[datetime]
    departure_time: Optional[datetime]
