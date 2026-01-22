from __future__ import annotations

from datetime import timezone
from typing import Any


class JourneyPresenter:
    @staticmethod
    def to_summary(estimate: Any) -> str:
        eta = estimate.eta
        reliability = estimate.reliability

        depart = eta.depart_time.astimezone(timezone.utc).strftime("%H:%M")
        p50 = eta.p50_arrival.astimezone(timezone.utc).strftime("%H:%M")
        p90 = eta.p90_arrival.astimezone(timezone.utc).strftime("%H:%M")

        reliability_note = (
            reliability.reasons[0]
            if getattr(reliability, "reasons", None)
            else "Reliability information unavailable."
        )

        return (
            f"Take the {estimate.route_id} Line. "
            f"Depart around {depart}. "
            f"Expected arrival between {p50} and {p90}. "
            f"{reliability_note}"
        )
