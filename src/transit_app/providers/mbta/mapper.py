from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from transit_app.domain.models import Prediction

def _parse_time(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    # MBTA uses ISO 8601 timestamps, often with timezone offset
    try:
        # Python 3.10 supports fromisoformat with offsets like "+00:00"
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    
def predictions_from_mbta(payload: dict[str, Any]) -> list[Prediction]:
    data = payload.get("data", [])
    out: list[Prediction] = []

    for item in data:
        attrs = item.get("attributes", {}) or {}
        rel = item.get("relationships", {}) or {}

        stop_id = (
            rel.get("stop", {})
            .get("data", {})
            .get("id")
        )
        if not isinstance(stop_id, str) or not stop_id:
            # If we can't identify the stop, skip the record
            continue
        route_id = (
            rel.get("route", {})
            .get("data", {})
            .get("id")
        )

        trip_id = (
            rel.get("trip", {})
            .get("data", {})
            .get("id")
        )

        direction_id = attrs.get("direction_id")
        if not isinstance(direction_id, int):
            direction_id = None
        
        arrival_time = _parse_time(attrs.get("arrival_time"))
        departure_time = _parse_time(attrs.get("departure_time"))

        out.append(
            Prediction(
                stop_id=stop_id,
                route_id=route_id if isinstance(route_id, str) else None,
                trip_id=trip_id if isinstance(trip_id, str) else None,
                direction_id=direction_id,
                arrival_time=arrival_time,
                departure_time=departure_time,
            )
        )
    return out