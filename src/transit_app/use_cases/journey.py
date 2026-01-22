from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from transit_app.services.eta import EtaEstimate

@dataclass(frozen=True)
class JourneyEstimate:
    """
    End-to-end journey estimate from origin to 
    destination using a single real-time stop.
    """

    origin_stop_id: str
    destination_stop_id: str
    route_id: str
    trip_id: str
    eta: EtaEstimate
    generated_at: datetime

from typing import Optional
from transit_app.domain.models import Prediction
from transit_app.providers.mbta.client import MbtaV3Client
from transit_app.providers.mbta.mapper import predictions_from_mbta
from transit_app.services.eta import EtaEstimator

class JourneyEstimator:
    """
    Orchestrates real-time MBTA predictions to produce
    a full journey ETA estimate.
    """

    def __init__(
        self,
        *,
        mbta_client: MbtaV3Client,
        eta_estimator: EtaEstimator,
    ) -> None:
        self._mbta = mbta_client
        self._eta = eta_estimator

    def estimate(
        self,
        *,
        origin_stop_id: str,
        destination_stop_id: str,
        route_id: str,
        now: datetime,
    ) -> JourneyEstimate:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        # 1) Fetch origin predictions
        origin_raw = self._mbta.get_predictions(
            stop_id=origin_stop_id,
            route_id=route_id,
            limit=5,
            sort="departure_time",
        )
        origin_preds = predictions_from_mbta(origin_raw)

        if not origin_preds:
            raise RuntimeError("No upcoming departures found at origin stop")

        # 2) Choose the next trip with a valid departure time
        origin_preds = [
            p for p in origin_preds
            if p.departure_time is not None
        ]

        if not origin_preds:
            raise RuntimeError("No departures with valid times at origin stop")

        origin_preds.sort(key=lambda p: p.departure_time)
        chosen = origin_preds[0]

        # 3) Find headway (second departure on same route/direction)
        second_dep: Optional[datetime] = None
        if len(origin_preds) > 1:
            second_dep = origin_preds[1].departure_time

        # 4) Fetch destination predictions for the same trip
        dest_raw = self._mbta.get_predictions(
            stop_id=destination_stop_id,
            route_id=route_id,
            limit=10,
        )
        dest_preds = predictions_from_mbta(dest_raw)

        dest_match = None
        for p in dest_preds:
            if p.trip_id == chosen.trip_id and p.arrival_time is not None:
                dest_match = p
                break

        if dest_match is None:
            raise RuntimeError(
                f"No destination prediction found for trip {chosen.trip_id}"
            )

        # 5) Estimate ETA
        eta = self._eta.estimate(
            now=now,
            origin_departure=chosen.departure_time,
            destination_arrival=dest_match.arrival_time,
            second_origin_departure=second_dep,
        )

        return JourneyEstimate(
            origin_stop_id=origin_stop_id,
            destination_stop_id=destination_stop_id,
            route_id=route_id,
            trip_id=chosen.trip_id,
            eta=eta,
            generated_at=now,
        )
