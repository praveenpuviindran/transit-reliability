from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class EstimateRequest(BaseModel):
    origin_stop_id: str
    destination_stop_id: str
    route_id: str


class EtaResponse(BaseModel):
    depart_time: datetime
    p50_arrival: datetime
    p80_arrival: datetime
    p90_arrival: datetime
    headway_seconds: int | None
    explanation: str


class ReliabilityResponse(BaseModel):
    score: int
    reasons: List[str]


class JourneyEstimateResponse(BaseModel):
    route_id: str
    trip_id: str
    generated_at: datetime
    eta: EtaResponse
    summary: str
    reliability: ReliabilityResponse
