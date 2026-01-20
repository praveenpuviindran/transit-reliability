# transit-reliability

## Architecture (early)

This project separates:
- **Adapters**: web endpoints, HTTP clients, external API calls
- **Core logic**: ETA + reliability estimation services
- **Domain models**: Stop/Route/Trip/Prediction objects

Slice 1 builds the config + HTTP boundaries first so core logic stays testable and deployable.