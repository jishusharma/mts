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
