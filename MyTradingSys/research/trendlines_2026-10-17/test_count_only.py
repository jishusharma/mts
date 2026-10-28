"""Tests for count_only.py (card trendline-count-only). Expected numbers are hand-computed, not from the code.
Run: python -m pytest MyTradingSys/research/trendlines_2026-10-17/test_count_only.py
"""
import csv
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import count_only as co  # noqa: E402


def _kline(t, p=100.0):
    return f"{t},{p},{p + 1},{p - 1},{p},1.0,{t + 59999},1.0,1,0.5,0.5,0\n"


def _write(d, name, rows):
    (Path(d) / name).write_text("open_time,open,high,low,close,volume,close_time,quote_volume,count,tbv,tbqv,ignore\n" + "".join(rows), newline="\n")


def test_loader_refuses_bar_at_or_after_2024_07_01():
    # a 2024-06 file carrying the first VALIDATION minute must raise
    with tempfile.TemporaryDirectory() as d:
        _write(d, "BTCUSDT-1m-2024-06.csv", [_kline(co.CUTOFF_MS - 60000), _kline(co.CUTOFF_MS)])
        with pytest.raises(ValueError, match="sealed"):
            co.load_dev_1m(klines=d)


def test_loader_ignores_files_outside_dev_months_and_keeps_last_dev_bar():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "BTCUSDT-1m-2024-06.csv", [_kline(co.CUTOFF_MS - 60000)])
        _write(d, "BTCUSDT-1m-2024-07.csv", [_kline(co.CUTOFF_MS)])   # not read: month outside DEV
        bars = co.load_dev_1m(klines=d)
        assert len(bars) == 1 and bars[0]["t"] == co.CUTOFF_MS - 60000


def test_outcome_column_is_refused():
    for bad in ("fwd_return", "mfe", "MAE_atr", "fee_bp", "price_change", "outcome_hit"):
        with pytest.raises(ValueError):
            co.assert_no_outcome_columns(["cell", bad])
    co.assert_no_outcome_columns(["cell", "events", "event_days", "mde_sd_holm_m"])


def test_written_outputs_have_no_outcome_column():
    for name in ("CELLS.csv", "effective_n_by_day.csv"):
        p = HERE / "counts" / name
        if p.exists():
            co.assert_no_outcome_columns(next(csv.reader(open(p, encoding="utf-8"))))


def test_mde_hand_values():
    # m=1: z(0.975)=1.95996 -> (1.95996+0.84)/sqrt(100) = 0.27999
    assert co.mde_sd(100, 1) == pytest.approx(0.27999, abs=1e-4)
    # wavetrend floor: Holm 12, z=2.87 -> 153 days gives 0.30 SD (3.71/12.369)
    assert co.mde_sd(153, 12) == pytest.approx(0.3, abs=2e-3)
    assert co.mde_sd(0, 5) == float("inf")


def test_holm_family_smallest_consistent_m():
    # m=1 would carry 2 cells (> m); m=2: MDE(120,2) = (2.2414+0.84)/sqrt(120) = 0.2813 <= 0.30 -> carry both, family 2
    m, ok = co.holm_family({"a": 120, "b": 120, "c": 10})
    assert m == 2 and ok == ["a", "b"]
    # 100 days: m=1 passes both (0.28) but 2 > 1; m=2 gives 0.308 > 0.30, nothing carried
    m, ok = co.holm_family({"a": 100, "b": 100})
    assert m == 2 and ok == []
    assert co.holm_family({"a": 5, "b": 6})[1] == []


def test_terciles():
    assert co.terciles([1, 2, 3, 4, 5, 6]) == (3, 5)
    assert [co.tercile_of(x, (3, 5)) for x in (1, 3, 4, 5, 6)] == ["T1", "T1", "T2", "T2", "T3"]


# ---- v2 (card trendline-count-only-v2): first_touch vs all_touches, retest/reclaim, causal terciles, digests, base m
class FakeDet:
    """Minimal detector stand-in: lines dict + append-only events + rejects (hand-built, no price series)."""
    def __init__(self, lines, events):
        self.lines, self.events, self.rejects = lines, events, []


def _ln(lid, side="support", slope=0.1, avail=5, elig=("A",), broken=None):
    return {"id": lid, "side": side, "slope_atr": slope, "available_at": avail, "eligible": set(elig), "broken_at": broken}


def _ev(line, state, bar, known=None, **kw):
    e = {"line": line, "state": state, "bar": bar, "known_at": bar if known is None else known}
    e.update(kw)
    return e


def _bars(n=60):
    return [{"t": 1_700_000_000_000 + i * 3_600_000} for i in range(n)]


def test_first_touch_counts_once_per_eligible_line_all_touches_counts_every_touch():
    # line eligible A at bar 10; touched at 12, 15, 20 -> first_touch 1, all_touches 3 (arm A)
    ev = [_ev("L", "eligible", 10, arm="A"), _ev("L", "touched", 12), _ev("L", "touched", 15), _ev("L", "touched", 20)]
    lines, events, _, _ = co.count_detector(FakeDet({"L": _ln("L")}, ev), _bars())
    kinds = [e[1] for e in events if e[0] == "A"]
    assert kinds.count("first_touch") == 1 and kinds.count("all_touches") == 3
    assert [e[4] for e in events if e[1] == "first_touch"] == [12]


def test_touch_before_eligibility_is_not_counted():
    ev = [_ev("L", "touched", 8), _ev("L", "eligible", 10, arm="A"), _ev("L", "touched", 14)]
    _, events, _, _ = co.count_detector(FakeDet({"L": _ln("L")}, ev), _bars())
    assert [e[4] for e in events if e[1] == "first_touch"] == [14]
    assert sum(1 for e in events if e[1] == "all_touches") == 1


def test_retest_and_reclaim_cells_exist_only_after_an_eligible_break():
    ev = [_ev("L", "eligible", 10, arm="A"), _ev("L", "broken", 20), _ev("L", "retested", 22), _ev("L", "reclaimed", 23),
          _ev("M", "broken", 20), _ev("M", "eligible", 21, arm="A"), _ev("M", "retested", 22), _ev("M", "reclaimed", 23)]
    lines = {"L": _ln("L", broken=20), "M": _ln("M", broken=20, avail=6)}
    _, events, _, _ = co.count_detector(FakeDet(lines, ev), _bars())
    ret = [e for e in events if e[1] in ("break", "retested", "reclaimed")]
    # L: break, retest, reclaim counted once each; M was not eligible when it broke (eligible at 21 > break 20): nothing
    assert sorted(e[1] for e in ret) == ["break", "reclaimed", "retested"]
    assert {e[4] for e in ret if e[1] == "retested"} == {22} and {e[4] for e in ret if e[1] == "reclaimed"} == {23}


def test_causal_terciles_do_not_change_when_later_lines_are_appended():
    base = [_ln(f"s{i}", slope=0.1 * (i + 1), avail=10 + i) for i in range(12)]
    first = co.causal_terciles(base)
    extended = co.causal_terciles(base + [_ln(f"x{i}", slope=9.0 + i, avail=100 + i) for i in range(30)])
    assert all(first[ln["id"]] == extended[ln["id"]] for ln in base)
    # hand check: line s11 (slope 1.2, 11 earlier lines 0.1..1.1): edges s[11//3]=s[3]=0.4, s[7]=0.8 -> 1.2 > 0.8 = T3
    assert first["s11"] == "T3"
    # warm-up: the first line has no history -> T0, never a full-sample tercile
    assert first["s0"] == "T0"


def test_causal_terciles_same_bar_lines_use_only_strictly_earlier_history():
    ls = [_ln(f"a{i}", slope=0.1 * (i + 1), avail=10 + i) for i in range(10)] + [_ln("p", slope=5.0, avail=50), _ln("q", slope=0.01, avail=50)]
    t = co.causal_terciles(ls)
    assert t["p"] == "T3" and t["q"] == "T1"      # both judged on the same 10 earlier lines, not on each other


def test_holm_family_with_base_m_counts_prior_variants():
    # base 65: k=2 -> m=67, z(1-0.05/134)=3.3658?  MDE(300,67) ~0.2437 ok; MDE(150,67)=(3.37+0.84)/12.25=0.344 not carried
    m, ok = co.holm_family({"a": 300, "b": 290, "c": 150}, base_m=65)
    assert m == 67 and ok == ["a", "b"]


def test_loader_records_sha256_of_every_file_read():
    import hashlib
    with tempfile.TemporaryDirectory() as d:
        _write(d, "BTCUSDT-1m-2024-06.csv", [_kline(co.CUTOFF_MS - 60000)])
        _write(d, "BTCUSDT-1m-2024-07.csv", [_kline(co.CUTOFF_MS)])   # not read -> not digested
        rows = []
        co.load_dev_1m(klines=d, digests=rows)
        want = hashlib.sha256((Path(d) / "BTCUSDT-1m-2024-06.csv").read_bytes()).hexdigest()
        assert [(r["file"], r["sha256"]) for r in rows] == [("BTCUSDT-1m-2024-06.csv", want)]


def test_written_cells_csv_has_v2_columns_and_kline_digests_exist():
    header = next(csv.reader(open(HERE / "counts" / "CELLS.csv", encoding="utf-8")))
    for col in ("first_touch", "all_touches", "retested", "reclaimed"):
        assert col in header
    dg = list(csv.DictReader(open(HERE / "counts" / "KLINE_DIGESTS.csv", encoding="utf-8")))
    assert len(dg) == 30 and all(len(r["sha256"]) == 64 for r in dg)
