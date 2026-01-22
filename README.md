# transit-reliability

## Slice 6: Web UI + Presentation Layer

- Added a static web UI for selecting origin, destination, and route.
- Connected the UI to the local FastAPI backend via a POST /estimate endpoint.
- Introduced a presenter layer to convert structured journey estimates into a human-readable summary.
- Preserved raw JSON output for debugging while presenting clean text to end users.
- Configured CORS for local frontend–backend development.

## Slice 5: Local API (FastAPI)

A local FastAPI service exposes the core journey estimation as an HTTP endpoint.
Run: uvicorn apps.api_local.main:app --reload 

## Slice 4: Reliability score and explanation

The journey estimate now includes a reliability score (0-100) plus short reasons.
Current scoring is a simple, explainable heuristic based on:
- Headway (service frequency proxy)
- Whether conservative defaults were used due to missing live signals

This layer is designed to be replaced later with calibrated statistical models or historical reliability estimates.

## Slice 3: End-to-end journey estimate (live MBTA)

This slice connects real-time MBTA predictions to the ETA uncertainty model

What it does:
- fetches live predictions at an origin stop and destination stop for a route
- selects the earliest origin departure whose trip_id is present at the destination
- computes ETA percentiles (P50/P80/P90) using the headway-based uncertainty heuristic
- returns a single structured JourneyEstimate result (trip_id, departure, arrival bands, explanation)
Run: python apps/api_local/run_journey.py

## Slice 2: Architecture

At this stage, the system now includes:
- a provider layer that fetches live MBTA predictions and normalizes them into domain models
- a pure ETA estimation service that computes P50/P80/P90 arrival times
- a headway-based uncertainty heuristic that widens or narrows ETA bands based on service frequency
- explicit handling of incomplete real-time data (missing arrival/departure times)
- unit-tested, deterministic logic for both API mapping and ETA estimation

Key design decision:
- external API JSON is isolated at the boundary and never flows into core logic
- ETA estimation is pure logic with no HTTP or environment dependencies
- uncertainty modeling is intentionally simple but architected to be replaceable with statistical models later

This slice of the project establishes the core computation layer that future routing, reliability scoring, and deployment layers will build on. 

## Slice 1: Foundation

This project separates:
- **Adapters**: web endpoints, HTTP clients, external API calls
- **Core logic**: ETA + reliability estimation services
- **Domain models**: Stop/Route/Trip/Prediction objects

Slice 1 builds the config + HTTP boundaries first so core logic stays testable and deployable.