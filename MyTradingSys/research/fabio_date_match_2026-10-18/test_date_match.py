import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import date_match as dm  # noqa: E402

DAY = dt.date(2025, 10, 15)
BASE = int(dt.datetime(2025, 10, 15, tzinfo=dt.timezone.utc).timestamp()) * 1000


def bars(fn, start_min=13 * 60, end_min=17 * 60):
    out = []
    for m in range(start_min, end_min):
        c = fn(m - start_min)
        out.append((BASE + m * 60000, c, c + 1, c - 1, c, 10.0))
    return out


def path(base):
    # entry at minute 45; +87 within 10 min; later +190 within 60 min; no dip below -20
    def f(i):
        if i < 45:
            return base
        if i < 55:
            return base + (i - 45) * 8.7
        if i < 100:
            return base + 87
        if i < 105:
            return base + 87 + (i - 100) * 20.6
        return base + 190
    return bars(f)


def test_pattern_scores_top_at_any_basis():
    for base in (24914.0, 1000.0):
        s, ms, _ = dm.best_match(path(base))
        assert s >= 0.99
        assert BASE + 13 * 3600000 <= ms <= BASE + (13 * 60 + 45) * 60000  # flat prefix ties: any entry up to the true one


def test_flat_scores_zero():
    s, _, _ = dm.best_match(bars(lambda i: 24914.0))
    assert s == 0


def test_stop_breach_scores_low():
    def f(i):
        if i < 45:
            return 24914.0
        if i < 50:
            return 24914.0 - 40
        return 24914.0 + (i - 50) * 5
    s, _, _ = dm.best_match(bars(f))
    assert s < 0.99


def test_verdict():
    assert dm.verdict([]) == "NOT_IN_DATA"
    assert dm.verdict([(1.0, "a"), (0.5, "b")]) == "MATCH"
    assert dm.verdict([(1.0, "a"), (0.95, "b")]) == "AMBIGUOUS"
