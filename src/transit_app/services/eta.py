from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass(frozen=True)
class EtaEstimate:
    """
    ETA estimate with uncertainty bands.
    Times are timezone-aware datetimes.
    """
    depart_time: datetime
    p50_arrival: datetime
    p80_arrival: datetime
    p90_arrival: datetime
    headway_seconds: Optional[int]
    explanation: str

class EtaEstimator:
    """
    Computes ETA percentiles using a imple headway-based 
    uncertainty heuristic.
    Design intent:
    - Pure logic (no HTTP)
    - Upgradeable later to quantile models/historical calibration.
    """

    def estimate(
            self,
            *,
            now: datetime,
            origin_departure: datetime,
            destination_arrival: datetime,
            second_origin_departure: datetime | None = None,
            alert_multiplier: float = 1.0,
    ) -> EtaEstimate:
        """
        Parameters:
        - now: current time (timezone aware)
        - origin_departure: departure time for the chosen trip
        - destination_arrival: arrival time at destination
        for the same trip
        - second_origin_departure: departure time of the next
        vehicle after this one (same stop/route/direction)
        - alert_multiplier: >=1 widens uncertainty when alerts
        exist

        Returns:
        - EtaEstimate with P50, P80, and P90 arrival times
        """
        if origin_departure.tzinfo is None or destination_arrival.tzinfo is None or now.tzinfo is None:
            raise ValueError("now, origin_departure, and destination_arrival must be timezone-aware datetimes")
        if destination_arrival < origin_departure:
            raise ValueError("destination_arrival cannot be earlier than origin_departure")
        
        # Compute headway (seconds between next 2 departures)

        headway_seconds: int | None = None
        if second_origin_departure is not None:
            if second_origin_departure.tzinfo is None:
                raise ValueError("second_origin_departure must be timezone-aware if provided")
            delta = (second_origin_departure - origin_departure).total_seconds()
            if delta > 0:
                headway_seconds = int(delta)

        # P50 = prediction arrival for this trip
        p50 = destination_arrival

        # Uncertainty heuristic:
        # - if headway is large, uncertainty is larger (miss risk/variability proxy)
        # - if headway is unknown, use a conservative default
        base_headway = headway_seconds if headway_seconds is not None else 10 * 60 # 10 minutes default

        # Additive buffers (seconds)
        p80_buffer = int(0.35 * base_headway * alert_multiplier)
        p90_buffer = int(0.60 * base_headway * alert_multiplier)

        p80 = p50 + timedelta(seconds=p80_buffer)
        p90 = p50 + timedelta(seconds=p90_buffer)

        # Explanation (simple version 1.0)
        if headway_seconds is None:
            explanation = "Uncertainty is wider because headway could not be estimated; using a conservative default."
        elif headway_seconds >= 12 * 60:
            explanation = "Uncertainty is wider because headway is large right now (service is less frequent)."
        elif headway_seconds >= 6 * 60:
            explanation = "Uncertainty is tighter because headway is small right now (service is frequent)."
        else:
            explanation = "Uncertainty is moderate based on current headway."

        if alert_multiplier > 1.0:
            explanation += "Active alerts widen the uncertainty bands."

        return EtaEstimate(
            depart_time=origin_departure,
            p50_arrival=p50,
            p80_arrival=p80,
            p90_arrival=p90,
            headway_seconds=headway_seconds,
            explanation=explanation,
        )
