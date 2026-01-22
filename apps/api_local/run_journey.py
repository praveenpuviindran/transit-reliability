from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from transit_app.config.settings import Settings
from transit_app.http.requests_client import RequestsHttpClient
from transit_app.providers.mbta.client import MbtaV3Client
from transit_app.services.eta import EtaEstimator
from transit_app.use_cases.journey import JourneyEstimator


def main() -> None:
    # Use your assumed timezone (America/New_York)
    now = datetime.now(tz=ZoneInfo("America/New_York"))

    settings = Settings.from_env()
    http = RequestsHttpClient()
    mbta = MbtaV3Client(http=http, settings=settings)

    journey = JourneyEstimator(mbta_client=mbta, eta_estimator=EtaEstimator())

    # Start with a known simple case: Red Line, Davis -> Kendall/MIT
    origin_stop_id = "place-davis"
    destination_stop_id = "place-harsq"
    route_id = "Red"

    result = journey.estimate(
        origin_stop_id=origin_stop_id,
        destination_stop_id=destination_stop_id,
        route_id=route_id,
        now=now,
    )

    print("Journey estimate")
    print("--------------")
    print("Route:", result.route_id)
    print("Trip:", result.trip_id)
    print("Generated at:", result.generated_at.isoformat())
    print("Depart:", result.eta.depart_time.isoformat())
    print("Arrive P50:", result.eta.p50_arrival.isoformat())
    print("Arrive P80:", result.eta.p80_arrival.isoformat())
    print("Arrive P90:", result.eta.p90_arrival.isoformat())
    print("Headway (s):", result.eta.headway_seconds)
    print("Explanation:", result.eta.explanation)


if __name__ == "__main__":
    main()
