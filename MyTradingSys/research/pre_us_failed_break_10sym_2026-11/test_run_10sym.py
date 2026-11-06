"""Tests for run_10sym.py: DEV-only loader, gap days are no-signal (never filled), one failed-break fixture day."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from MyTradingSys.backtest import splits  # noqa: E402

_sp = importlib.util.spec_from_file_location("run_10sym", HERE / "run_10sym.py")
r = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(r)

HEAD = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"


def _write(folder, sym, name, stamps):
    folder.mkdir(parents=True, exist_ok=True)
    rows = "".join(f"{int(pd.Timestamp(t).timestamp() * 1000)},1,2,0.5,1.5,1,0,0,0,0,0,0\n" for t in stamps)
    (folder / f"{sym}-1m-{name}.csv").write_text(HEAD + rows, newline="\n")


def test_loader_refuses_bar_at_or_after_dev_end(tmp_path):
    _write(tmp_path / "klines_xyz", "XYZUSDT", "2024-06", ["2024-06-30 23:59", "2024-07-01 00:00"])
    with pytest.raises(splits.SplitViolation):
        r.load_klines("XYZUSDT", root=tmp_path)


def test_loader_never_opens_later_month_files(tmp_path):
    _write(tmp_path / "klines_xyz", "XYZUSDT", "2024-06", ["2024-06-30 23:59"])
    _write(tmp_path / "klines_xyz", "XYZUSDT", "2024-07", ["2024-07-01 00:00"])
    _write(tmp_path / "klines_xyz", "XYZUSDT", "2026-09-26", ["2026-09-26 00:00"])
    assert r.load_klines("XYZUSDT", root=tmp_path).index.max() == pd.Timestamp("2024-06-30 23:59")


def test_gap_is_not_filled_and_day_is_no_signal(tmp_path):
    stamps = [t for t in pd.date_range("2022-01-01", "2022-01-07 23:59", freq="min")
              if not (t.day == 7 and 8 <= t.hour < 9)]                      # one hour missing on Jan 7
    _write(tmp_path / "klines_xyz", "XYZUSDT", "2022-01", stamps)
    df = r.load_klines("XYZUSDT", root=tmp_path)
    assert len(df) == len(stamps)                                             # nothing interpolated or zero-filled
    o, h, l, c = r.to_grid(df)
    assert np.isnan(h[6, 8 * 60:9 * 60]).all()
    ok = r.usable_days(o, h, l, c)
    assert not ok[6] and not ok[:5].any()


def _flat(price=100.0):
    a = np.full((r.NDAYS, 1440), price)
    return a.copy(), a.copy() + 0.1, a.copy() - 0.1, a.copy()


def test_failed_break_day_gives_one_short_that_hits_target():
    o, h, l, c = _flat()
    d = 20
    # hourly range 0.2 -> ATR14 = 0.2. Prior day high 101 is the level (>= open + 0.5 ATR).
    h[d - 1, 600] = 101.0
    h[d, 8 * 60] = 101.15                                                     # break above 101 + 0.1 ATR, excursion < 1.5 ATR
    c[d, 8 * 60] = 101.1
    c[d, 8 * 60 + 1] = 100.5                                                  # closes back below: signal bar t = 08:01
    o[d, 8 * 60 + 2] = 100.5                                                  # entry bar open
    l[d, 8 * 60 + 10] = 99.0                                                  # target trade-through (support >= 1 ATR below, or fallback)
    S = r.Sym("BTCUSDT", o, h, l, c)
    t = S.signal(d)
    assert t == 8 * 60 + 1
    ep = S.simulate(d, t)
    assert ep["outcome"] == "TARGET" and ep["tranches"] == 1 and ep["gross_bps"] > 0
    assert ep["net_bps"] == pytest.approx(ep["gross_bps"] - 2 * r.LEG_COST * 0.25 * 1e4)
    assert S.signal(d + 1) is None                                            # flat day: no break, no signal
