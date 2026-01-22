-- Reference tables derived from static GTFS

DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS routes;

CREATE TABLE stops (
  stop_id TEXT PRIMARY KEY,
  stop_name TEXT NOT NULL,
  stop_lat REAL,
  stop_lon REAL,
  location_type INTEGER,
  parent_station TEXT
);

CREATE TABLE routes (
  route_id TEXT PRIMARY KEY,
  route_short_name TEXT,
  route_long_name TEXT,
  route_type INTEGER
);

CREATE INDEX idx_stops_name ON stops(stop_name);
