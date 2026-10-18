import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backfill_naked_pocs as B  # noqa: E402

DAY = 86_400_000
D1 = 1_790_899_200_000  # 2026-10-02 00:00Z


def bar(t, h, l, c, v):
    return (t, h, l, c, v)


def quiet_plus_wide(t0):
    bars = [bar(t0 + i * 60_000, 100.10, 100.00, 100.05, 100.0) for i in range(40)]
    bars.append(bar(t0 + 40 * 60_000, 200.0, 100.0, 150.0, 100.0))
    return bars


def test_poc_is_where_volume_traded_not_the_wide_bar():
    assert abs(B.day_poc(quiet_plus_wide(D1)) - 100.0) < 5.0


def test_zero_range_bar_is_finite():
    p = B.day_poc([bar(D1, 100.0, 100.0, 100.0, 5.0), bar(D1 + 60_000, 110.0, 100.0, 105.0, 1.0)])
    assert 99.0 <= p <= 101.0


def test_backfill_adds_missing_days_keeps_existing_and_marks_visited():
    d2 = "2026-10-02"
    d3 = "2026-10-03"
    days = {d2: quiet_plus_wide(D1), d3: [bar(D1 + DAY, 101.0, 99.0, 100.0, 10.0)]}
    entries = [{"date": "2026-08-03", "poc": 63155.87, "visited": False}]
    out, added, visited = B.backfill(entries, days, "2026-10-04")
    assert added == [d2, d3]
    assert [e["date"] for e in out] == ["2026-08-03", d2, d3]
    # d2's POC (~100) is traded through by d3's bar (99..101): visited; d3's own POC is only touched on its own day: naked
    by = {e["date"]: e for e in out}
    assert by[d2]["visited"] is True
    assert by[d3]["visited"] is False
    # the stale 63,155 sits outside every bar: stays naked, never touched
    assert by["2026-08-03"]["visited"] is False and by["2026-08-03"]["poc"] == 63155.87


def test_existing_day_is_not_overwritten_and_today_is_skipped():
    days = {"2026-10-02": quiet_plus_wide(D1)}
    entries = [{"date": "2026-10-02", "poc": 12345.0, "visited": False}]
    out, added, _ = B.backfill(entries, days, "2026-10-02")
    assert added == [] and out[0]["poc"] == 12345.0
