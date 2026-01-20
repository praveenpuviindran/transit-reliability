from __future__ import annotations
from urllib.parse import urljoin

def predictions(base_url: str) -> str:
    """
    Build the MBTA predictions endpoint URL.
    """
    return urljoin(base_url.rstrip("/") + "/", "predictions")
