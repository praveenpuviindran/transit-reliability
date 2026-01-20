from transit_app.providers.mbta.mapper import predictions_from_mbta

def test_predictions_from_mbta_parses_minimal_payload():
    payload = {
        "data": [
            {
                "attributes": {
                    "direction_id": 1,
                    "arrival_time": "2026-01-20T12:00:00-05:00",
                    "departure_time": None,
                },
                "relationships": {
                    "stop": {"data": {"id": "place-alfcl"}},
                    "route": {"data": {"id": "Red"}},
                    "trip": {"data": {"id": "trip-123"}},
                },
            }
        ]
    }

    preds = predictions_from_mbta(payload)
    assert len(preds) == 1
    p = preds[0]
    assert p.stop_id == "place-alfcl"
    assert p.route_id == "Red"
    assert p.trip_id == "trip-123"
    assert p.direction_id == 1
    assert p.arrival_time is not None