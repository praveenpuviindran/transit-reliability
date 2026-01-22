from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ReliabilityReport:
    """
    Reliability summary for a journey estimate.
    score: 0 (worst) to 100 (best)
    reasons: short human-readable reasons that justify the score
    """
    score: int
    reasons: list[str]

class ReliabilityScorer:
    """
    Computes a simple reliability score based on headway and data completeness.

    This is deliberately heuristic and explainable.
    Later we can replace with statistical calibration / historical models.
    """

    def score(
        self,
        *,
        headway_seconds: Optional[int],
        used_default_headway: bool,
        had_destination_match: bool,
    ) -> ReliabilityReport:
        reasons: list[str] = []

        # start optimistic, subtract penalties
        score = 100

        # 1) Headway-based penalty (service frequency proxy)
        if headway_seconds is None:
            score -= 25
            reasons.append("Headway could not be estimated from live data.")
        else:
            # Convert headway into a penalty bucket
            if headway_seconds >= 15 * 60:
                score -= 45
                reasons.append("service is infrequent right now (large headway).")
            elif headway_seconds >= 10 * 60:
                score -= 30
                reasons.append("Service headway is moderately large right now.")
            elif headway_seconds >= 6 * 60:
                score -= 15
                reasons.append("Service headway is moderate right now.")
            else:
                reasons.append("Service is frequent right now (small headway).")
        # 2) Default headway usage penalty (means we widened uncertainty conservatively)
        if used_default_headway:
            score -= 10
            reasons.append("Uncertainty bands used a conservative default headway.")
        # 3) Destination match coverage (if false, the estimate wouldn't exist - we keep this for extensibility; currently journey estimation requires a match.)
        if not had_destination_match:
            score -= 40
            reasons.append("Destination prediction coverage was missing for upcoming trips.")
        # Clamp and finalize
        score = max(0, min(100, score))

        # If no reasons somehow, provide a generic line
        if not reasons:
            reasons.append("Reliability could not be assessed with available signals.")
        
        return ReliabilityReport(score=score, reasons=reasons)
