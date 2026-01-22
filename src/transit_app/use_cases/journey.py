from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from transit_app.services.eta import EtaEstimate
from transit_app.services.reliability import ReliabilityReport, ReliabilityScorer

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
    reliability: ReliabilityReport
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

    def __init__(self, *, mbta_client: MbtaV3Client, eta_estimator: EtaEstimator, reliability_scorer: ReliabilityScorer) -> None:
        self._mbta = mbta_client
        self._eta = eta_estimator
        self._rel = reliability_scorer

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

        # Fetch destination predictions once and index by trip_id
        dest_raw = self._mbta.get_predictions(
            stop_id=destination_stop_id,
         route_id=route_id,
            limit=25,
        )
        dest_preds = predictions_from_mbta(dest_raw)

        # Build a map: trip_id -> best available destination time (prefer arrival_time)
        dest_time_by_trip: dict[str, datetime] = {}
        for p in dest_preds:
            if not p.trip_id:
                continue
            t = p.arrival_time or p.departure_time
            if t is None:
                continue
            # If multiple records exist for same trip, keep the earliest time
            if p.trip_id not in dest_time_by_trip or t < dest_time_by_trip[p.trip_id]:
                dest_time_by_trip[p.trip_id] = t

        # Now choose the first origin departure whose trip appears at destination
        chosen: Prediction | None = None
        second_dep: Optional[datetime] = None
        dest_time: Optional[datetime] = None

        for i, cand in enumerate(origin_preds):
            if not cand.trip_id or cand.departure_time is None:
                continue
            if cand.trip_id in dest_time_by_trip:
                chosen = cand
                dest_time = dest_time_by_trip[cand.trip_id]
                # headway = next departure after chosen (if any)
                if i + 1 < len(origin_preds):
                    second_dep = origin_preds[i + 1].departure_time
                break

        if chosen is None or dest_time is None:
            raise RuntimeError(
                "No matching destination prediction found for upcoming origin departures. "
                "Try a closer destination stop or increase prediction limits."
            )

        # Estimate ETA using chosen origin departure and matched destination time
        eta = self._eta.estimate(
            now=now,
            origin_departure=chosen.departure_time,
            destination_arrival=dest_time,
            second_origin_departure=second_dep,
        )
        used_default_headway = eta.headway_seconds is None
        had_destination_match = True

        reliability = self._rel.score(
            headway_seconds=eta.headway_seconds,
            used_default_headway=used_default_headway,
            had_destination_match=had_destination_match,
        )
        return JourneyEstimate(
            origin_stop_id=origin_stop_id,
            destination_stop_id=destination_stop_id,
            route_id=route_id,
            trip_id=chosen.trip_id,
            eta=eta,
            reliability=reliability,
            generated_at=now,
        )