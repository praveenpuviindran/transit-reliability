from transit_app.services.reliability import ReliabilityScorer


def test_reliability_high_when_headway_small():
    scorer = ReliabilityScorer()
    report = scorer.score(
        headway_seconds=3 * 60,
        used_default_headway=False,
        had_destination_match=True,
    )
    assert report.score >= 80
    assert any("frequent" in r.lower() for r in report.reasons)


def test_reliability_lower_when_headway_large():
    scorer = ReliabilityScorer()
    report = scorer.score(
        headway_seconds=15 * 60,
        used_default_headway=False,
        had_destination_match=True,
    )
    assert report.score <= 60
    assert any("infrequent" in r.lower() for r in report.reasons)


def test_reliability_penalized_when_default_used():
    scorer = ReliabilityScorer()
    report = scorer.score(
        headway_seconds=None,
        used_default_headway=True,
        had_destination_match=True,
    )
    assert report.score < 80
    assert any("conservative default" in r.lower() for r in report.reasons)
