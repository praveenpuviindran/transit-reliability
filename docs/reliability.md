Current uncertainty approach is headway-based heuristic
P50 = predicted arrival time for chosen trip
P80/P90 = P50 plus headway-proportional buffers
Missing headway uses 10-minute default
Alerts can widen via multiplier (placeholder)

# Deployment Notes

## Local development
The application is developed and tested locally using:
- FastAPI for the backend API
- A static HTML/JavaScript frontend served via `python -m http.server`
- Live reload using `uvicorn --reload`

The backend and frontend run on separate ports:
- API: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

CORS is enabled in the API to allow local browser-based access.

## Reference data storage (AWS S3)

Reference transit data (stops and routes) is built locally from GTFS and uploaded to AWS S3 as static artifacts.

These files are treated as read-only reference data and are not generated at runtime.

### Files stored in S3
- `reference/stops_min.json`
- `reference/routes_min.json`

### Bucket
Reference artifacts are stored in a dedicated S3 bucket:
