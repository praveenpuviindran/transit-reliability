from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    """
    Application configuration.

    Why this exists:
    - Single source of truth for runtime configuration
    - Keeps env var parsing out of business logic
    - Frozen dataclass -> immutable config (safer)
    """

    mbta_base_url: str = "https://api-v3.mbta.com"
    mbta_api_key: str | None = None
    timeout_s: float = 10.0

    @staticmethod
    def from_env() -> "Settings":
        """
        Build Settings from environment variables.

        Supported env vars:
        - MBTA_BASE_URL (optional)
        - MBTA_API_KEY (optional)
        - HTTP_TIMEOUT_S (optional)
        """
        base_url = os.getenv("MBTA_BASE_URL", "https://api-v3.mbta.com").strip()
        api_key = os.getenv("MBTA_API_KEY")
        api_key = api_key.strip() if api_key else None

        timeout_raw = os.getenv("HTTP_TIMEOUT_S", "10").strip()
        try:
            timeout_s = float(timeout_raw)
        except ValueError as e:
            raise ValueError(f"HTTP_TIMEOUT_S must be a number, got: {timeout_raw!r}") from e
        
        return Settings(mbta_base_url=base_url, mbta_api_key=api_key, timeout_s=timeout_s)
    

    
        