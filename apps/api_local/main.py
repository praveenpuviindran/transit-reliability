from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from transit_app.presenters.journey_presenter import JourneyPresenter

from transit_app.config.settings import Settings
from transit_app.http.api_models import (
    EstimateRequest,
    JourneyEstimateResponse,
    EtaResponse,
    ReliabilityResponse,
)
from transit_app.http.requests_client import RequestsHttpClient
from transit_app.providers.mbta.client import MbtaV3Client
from transit_app.services.eta import EtaEstimator
from transit_app.services.reliability import ReliabilityScorer
from transit_app.use_cases.journey import JourneyEstimator

app = FastAPI(title="Transit Reliability API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/estimate", response_model=JourneyEstimateResponse)
def estimate(req: EstimateRequest) -> JourneyEstimateResponse:
    now = datetime.now(tz=ZoneInfo("America/New_York"))

    settings = Settings.from_env()
    http = RequestsHttpClient()
    mbta = MbtaV3Client(http=http, settings=settings)

    journey = JourneyEstimator(
        mbta_client=mbta,
        eta_estimator=EtaEstimator(),
        reliability_scorer=ReliabilityScorer(),
    )

    try:
        result = journey.estimate(
            origin_stop_id=req.origin_stop_id,
            destination_stop_id=req.destination_stop_id,
            route_id=req.route_id,
            now=now,
        )
        summary = JourneyPresenter.to_summary(result)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JourneyEstimateResponse(
        route_id=result.route_id,
        trip_id=result.trip_id,
        generated_at=result.generated_at,
        eta=EtaResponse(
            depart_time=result.eta.depart_time,
            p50_arrival=result.eta.p50_arrival,
            p80_arrival=result.eta.p80_arrival,
            p90_arrival=result.eta.p90_arrival,
            headway_seconds=result.eta.headway_seconds,
            explanation=result.eta.explanation,
        ),
        reliability=ReliabilityResponse(
            score=result.reliability.score,
            reasons=result.reliability.reasons,
        ),
        summary=summary,
    )
