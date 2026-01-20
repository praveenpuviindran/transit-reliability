from __future__ import annotations
from typing import Any, Protocol

class HttpClient(Protocol):
    """
    A tiny contract for "something that can fetch JSON".

    Why this exists:
    - lets us swap implementations later (requests locally, Worker fetch in prod)
    - makes unit testing easy (we can inject a fake client)
    """

    def get_json(
            self,
            url: str,
            *,
            params: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            timeout_s: float = 10.0,
    ) -> dict[str, Any]:
        ...
