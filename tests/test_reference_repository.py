from __future__ import annotations

from transit_app.repositories.reference import ReferenceRepository
from transit_app.storage.base import BlobStorage


class FakeStorage(BlobStorage):
    def __init__(self, mapping: dict[str, bytes]) -> None:
        self._m = mapping

    def read_bytes(self, key: str) -> bytes:
        return self._m[key]


def test_reference_repository_reads_stops():
    storage = FakeStorage(
        {
            "stops_min.json": b'[{"stop_id":"place-davis","stop_name":"Davis"}]',
            "routes_min.json": b"[]",
        }
    )
    repo = ReferenceRepository(storage)
    stops = repo.list_stops()
    assert stops[0].stop_id == "place-davis"
    assert stops[0].stop_name == "Davis"


def test_reference_repository_reads_routes():
    storage = FakeStorage(
        {
            "stops_min.json": b"[]",
            "routes_min.json": b'[{"route_id":"Red","route_short_name":null,"route_long_name":"Red Line"}]',
        }
    )
    repo = ReferenceRepository(storage)
    routes = repo.list_routes()
    assert routes[0].route_id == "Red"
    assert routes[0].route_long_name == "Red Line"
