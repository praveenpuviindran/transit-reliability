from __future__ import annotations

import csv
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
GTFS_DIR = REPO_ROOT / "data" / "gtfs_raw"
OUT_DIR = REPO_ROOT / "data" / "reference"
DB_PATH = OUT_DIR / "reference.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


@dataclass(frozen=True)
class StopRow:
    stop_id: str
    stop_name: str
    stop_lat: float | None
    stop_lon: float | None
    location_type: int | None
    parent_station: str | None


@dataclass(frozen=True)
class RouteRow:
    route_id: str
    route_short_name: str | None
    route_long_name: str | None
    route_type: int | None


def _to_float(x: str) -> float | None:
    x = (x or "").strip()
    return float(x) if x else None


def _to_int(x: str) -> int | None:
    x = (x or "").strip()
    return int(x) if x else None


def read_stops(stops_txt: Path) -> list[StopRow]:
    rows: list[StopRow] = []
    with stops_txt.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                StopRow(
                    stop_id=r["stop_id"].strip(),
                    stop_name=r["stop_name"].strip(),
                    stop_lat=_to_float(r.get("stop_lat", "")),
                    stop_lon=_to_float(r.get("stop_lon", "")),
                    location_type=_to_int(r.get("location_type", "")),
                    parent_station=(r.get("parent_station", "") or "").strip() or None,
                )
            )
    return rows


def read_routes(routes_txt: Path) -> list[RouteRow]:
    rows: list[RouteRow] = []
    with routes_txt.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                RouteRow(
                    route_id=r["route_id"].strip(),
                    route_short_name=(r.get("route_short_name", "") or "").strip() or None,
                    route_long_name=(r.get("route_long_name", "") or "").strip() or None,
                    route_type=_to_int(r.get("route_type", "")),
                )
            )
    return rows


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def upsert_stops(conn: sqlite3.Connection, stops: Iterable[StopRow]) -> None:
    conn.executemany(
        """
        INSERT INTO stops(stop_id, stop_name, stop_lat, stop_lon, location_type, parent_station)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(stop_id) DO UPDATE SET
          stop_name=excluded.stop_name,
          stop_lat=excluded.stop_lat,
          stop_lon=excluded.stop_lon,
          location_type=excluded.location_type,
          parent_station=excluded.parent_station
        """,
        [
            (s.stop_id, s.stop_name, s.stop_lat, s.stop_lon, s.location_type, s.parent_station)
            for s in stops
        ],
    )
    conn.commit()


def upsert_routes(conn: sqlite3.Connection, routes: Iterable[RouteRow]) -> None:
    conn.executemany(
        """
        INSERT INTO routes(route_id, route_short_name, route_long_name, route_type)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(route_id) DO UPDATE SET
          route_short_name=excluded.route_short_name,
          route_long_name=excluded.route_long_name,
          route_type=excluded.route_type
        """,
        [(r.route_id, r.route_short_name, r.route_long_name, r.route_type) for r in routes],
    )
    conn.commit()


def write_minified_json(stops: list[StopRow], routes: list[RouteRow]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Keep it small: only what UI needs
    stops_min = [
        {"stop_id": s.stop_id, "stop_name": s.stop_name}
        for s in stops
        # Keep parent stations (location_type=1) and regular stops if parent missing
        if (s.location_type in (None, 0, 1))
    ]

    routes_min = [
        {"route_id": r.route_id, "route_short_name": r.route_short_name, "route_long_name": r.route_long_name}
        for r in routes
    ]

    (OUT_DIR / "stops_min.json").write_text(json.dumps(stops_min, indent=2), encoding="utf-8")
    (OUT_DIR / "routes_min.json").write_text(json.dumps(routes_min, indent=2), encoding="utf-8")


def main() -> None:
    stops_txt = GTFS_DIR / "stops.txt"
    routes_txt = GTFS_DIR / "routes.txt"

    if not stops_txt.exists() or not routes_txt.exists():
        raise FileNotFoundError(
            "Missing GTFS files. Put MBTA GTFS files into data/gtfs_raw/ (must include stops.txt and routes.txt)."
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    stops = read_stops(stops_txt)
    routes = read_routes(routes_txt)

    conn = sqlite3.connect(DB_PATH)
    try:
        init_db(conn)
        upsert_stops(conn, stops)
        upsert_routes(conn, routes)
    finally:
        conn.close()

    write_minified_json(stops, routes)

    print("Built reference data:")
    print("-", DB_PATH)
    print("-", OUT_DIR / "stops_min.json")
    print("-", OUT_DIR / "routes_min.json")


if __name__ == "__main__":
    main()
