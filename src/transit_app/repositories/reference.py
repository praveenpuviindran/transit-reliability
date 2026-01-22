from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from transit_app.storage.base import BlobStorage


@dataclass(frozen=True)
class StopRef:
    stop_id: str
    stop_name: str


@dataclass(frozen=True)
class RouteRef:
    route_id: str
    route_short_name: str | None
    route_long_name: str | None


class ReferenceRepository:
    """
    Read-only repository for transit reference data (stops, routes).

    Backed by JSON artifacts produced from GTFS.
    Storage backend is injected (local now, S3 later).
    """

    def __init__(self, storage: BlobStorage) -> None:
        self._storage = storage

    def list_stops(self) -> list[StopRef]:
        raw = self._load_json("stops_min.json")
        return [StopRef(stop_id=x["stop_id"], stop_name=x["stop_name"]) for x in raw]

    def list_routes(self) -> list[RouteRef]:
        raw = self._load_json("routes_min.json")
        return [
            RouteRef(
                route_id=x["route_id"],
                route_short_name=x.get("route_short_name"),
                route_long_name=x.get("route_long_name"),
            )
            for x in raw
        ]

    def _load_json(self, filename: str) -> list[dict[str, Any]]:
        data = self._storage.read_bytes(filename)
        return json.loads(data.decode("utf-8"))
