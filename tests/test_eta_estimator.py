from datetime import datetime,  timezone,  timedelta
import pytest
from transit_app.services.eta import EtaEstimator

def _dt(minutes: int) -> datetime:
    return datetime(2026, 1, 20, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)

def test_eta_estimator_uses_headway_to_widen_bands():
    est = EtaEstimator()

    now = _dt(0)
    origin_dep = _dt(5)
    dest_arr = _dt(25)

    # headway = 12 minutes
    second_dep = _dt(17)

    out = est.estimate(
        now=now,
        origin_departure=origin_dep,
        destination_arrival=dest_arr,
        second_origin_departure=second_dep,
    )

    assert out.p50_arrival == dest_arr
    assert out.p80_arrival > out.p50_arrival
    assert out.p90_arrival > out.p80_arrival
    assert out.headway_seconds == 12 * 60

def test_eta_estimator_defaults_when_headway_missing():
    est = EtaEstimator()

    out = est.estimate(
        now=_dt(0),
        origin_departure=_dt(5),
        destination_arrival=_dt(25),
        second_origin_departure=None,
    )

    assert out.headway_seconds is None
    assert "conservative default" in out.explanation.lower()

def test_eta_estimator_requires_tz_aware_datetimes():
    est = EtaEstimator()
    naive = datetime(2026, 1, 20, 12, 0)

    with pytest.raises(ValueError):
        est.estimate(
            now=naive,
            origin_departure=naive,
            destination_arrival=naive,
        )
