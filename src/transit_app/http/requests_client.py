from __future__ import annotations
from typing import Any
import requests

class RequestsHttpClient:
    """
    Local/dev HTTP client based on 'requests'.
    Implements the HttpClient Protocol by matching its method signature.
    """

    def get_json(
            self,
            url: str,
            *,
            params: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            timeout_s: float = 10.0,
    ) -> dict[str, Any]:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout_s)
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed for {url}") from e
        
        # Raise for non-2xx response (includes 4xx/5xx)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            body = resp.text[:500] # cap for readable errors
            raise RuntimeError(f"HTTP {resp.status_code} for {url}. Body: {body}") from e
        
        try:
            data: dict[str, Any] = resp.json()
        except ValueError as e:
            body = resp.text[:500]
            raise RuntimeError(f"Expected JSON response from {url}. Body: {body}") from e
        
        return data
