# transit-reliability

## Architecture (Slice 2)

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

## Architecture (early)

This project separates:
- **Adapters**: web endpoints, HTTP clients, external API calls
- **Core logic**: ETA + reliability estimation services
- **Domain models**: Stop/Route/Trip/Prediction objects

Slice 1 builds the config + HTTP boundaries first so core logic stays testable and deployable.