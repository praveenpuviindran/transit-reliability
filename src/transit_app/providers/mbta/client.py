from __future__ import annotations
from typing import Any
from transit_app.config.settings import Settings
from transit_app.http.base import HttpClient
from transit_app.providers.mbta.endpoints import predictions as predictions_url

class MbtaV3Client:
    """
    Thin client for MBTA v3 API.
    Responsibility: perform HTTP requests and return raw JSON dicts.
    """
    def __init__(self, http: HttpClient, settings: Settings) -> None:
        self._http = http
        self._settings = settings

    def get_predictions(
            self,
            *,
            stop_id: str,
            route_id: str | None = None,
            direction_id: int | None = None,
            limit: int = 10,
            sort: str = "departure_time",
    ) -> dict[str, Any]:
        url = predictions_url(self._settings.mbta_base_url)

        params: dict[str, Any] = {
            "filter[stop]": stop_id,
            "page[limit]": limit,
            "sort": sort,
        }
        if route_id is not None:
            params["filter[route]"] = route_id
        if direction_id is not None:
            params["filter[direction_id]"] = direction_id

        headers: dict[str, str] = {}
        if self._settings.mbta_api_key:
            headers["x-api-key"] = self._settings.mbta_api_key

        return self._http.get_json(
            url,
            params=params,
            headers=headers if headers else None,
            timeout_s=self._settings.timeout_s,
        )
    