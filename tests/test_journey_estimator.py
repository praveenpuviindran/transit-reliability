from datetime import datetime, timedelta, timezone
import pytest
from transit_app.domain.models import Prediction
from transit_app.services.eta import EtaEstimator
from transit_app.use_cases.journey import JourneyEstimator

class FakeMbtaClient:
    def get_predictions(self, *, stop_id, route_id, limit=10, sort=None):
        if stop_id == "origin":
            return {
                "data": [
                    {
                        "attributes": {
                            "departure_time": "2026-01-20T12:05:00+00:00"
                        },
                        "relationships": {
                            "stop": {"data": {"id": "origin"}},
                            "route": {"data": {"id": route_id}},
                            "trip": {"data": {"id": "trip-1"}},
                        },
                    },
                    {
                        "attributes": {
                            "departure_time": "2026-01-20T12:17:00+00:00"
                        },
                        "relationships": {
                            "stop": {"data": {"id": "origin"}},
                            "route": {"data": {"id": route_id}},
                            "trip": {"data": {"id": "trip-2"}},
                        },
                    },
                ]
            }
        if stop_id == "destination":
            return {
                 "data": [
                    {
                        "attributes": {
                            "arrival_time": "2026-01-20T12:25:00+00:00"
                        },
                        "relationships": {
                            "stop": {"data": {"id": "destination"}},
                            "route": {"data": {"id": route_id}},
                            "trip": {"data": {"id": "trip-1"}},
                        },
                    }
                ]
            }

        return {"data": []}
    
def test_journey_estimator_end_to_end():
    estimator = JourneyEstimator(
        mbta_client=FakeMbtaClient(),
        eta_estimator=EtaEstimator(),
    )

    now = datetime(2026, 1, 20, 12, 0, tzinfo=timezone.utc)

    result = estimator.estimate(
        origin_stop_id="origin",
        destination_stop_id="destination",
        route_id="Red",
        now=now,
    )

    assert result.trip_id == "trip-1"
    assert result.eta.p50_arrival > now
    assert result.eta.p90_arrival >= result.eta.p80_arrival >= result.eta.p50_arrival