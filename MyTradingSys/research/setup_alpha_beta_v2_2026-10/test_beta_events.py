"""Planted single sweep on synthetic 15m bars: exactly one event, and nothing after the sweep bar is used.
The same checks fail on the v1 beta_sweep.py logic (per-bar counting + next-bar look-ahead)."""
import os, sys, importlib.util
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_v2 as s2

DAY = 86400000
T0 = 20000 * DAY  # a UTC midnight


def planted(tail_noise=False, n_after=40):
    """Day 0: range 90..100 (PDH 100, PDL 90). Day 1: sits at 95, ONE bar wicks to 100.5 and closes 99.5 at 10:00,
    then bars keep poking above 100 and closing back inside (v1 counts each) unless tail_noise changes the tail."""
    rows = []
    for k in range(96):  # day 0
        hi = 100.0 if k == 40 else 95.5
        lo = 90.0 if k == 60 else 94.5
        rows.append((T0 + k * 900000, 95.0, hi, lo, 95.0, 100.0, 50.0))
    for k in range(96):  # day 1
        t = T0 + DAY + k * 900000
        o, h, l, c = 95.0, 95.5, 94.5, 95.0
        if k == 40:  # 10:00 UTC, the sweep
            o, h, l, c = 99.0, 100.5, 98.9, 99.5
        if k > 40 and k < 40 + n_after:
            o, h, l, c = 99.4, 100.4, 99.0, 99.6  # repeated pokes above PDH, back inside
        if tail_noise and k > 41:
            o, h, l, c = 1.0, 1e6, 1e-3, 5e5
        rows.append((t, o, h, l, c, 100.0, 40.0))
    return pd.DataFrame(rows, columns=["t", "open", "high", "low", "close", "volume", "tb"])


def v1_detector(b15):
    spec = importlib.util.spec_from_file_location("v1", os.path.join(HERE, "..", "setup_alpha_beta_2026-10-10", "beta_sweep.py"))
    v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
    bars = [{"t": int(r.t) // 1000, "o": r.open, "h": r.high, "l": r.low, "c": r.close, "v": r.volume, "tb": r.tb}
            for r in b15.itertuples()]
    cvd = 0.0
    for b in bars:
        cvd += b["tb"] * 2 - b["v"]; b["cvd"] = cvd
    lv = v1.mark_levels(bars)
    return [{"t": bars[e["i"]]["t"] * 1000, "i": e["i"], "side": e["side"]} for e in v1.find_sweeps(bars, lv)]


def v2_detector(b15):
    return s2.find_events(b15)


def check_single_event(detect):
    b = planted()
    evs = detect(b)
    assert len(evs) == 1, "expected exactly one sweep event, got %d" % len(evs)
    i = evs[0]["i"]
    assert evs[0]["side"] == "short"
    # no look-ahead: bars after the entry bar (i+1) are replaced by garbage, the event must not change
    b2 = b.copy()
    after = i + 2
    b2.loc[after:, ["open", "high", "low", "close"]] = [1.0, 1e6, 1e-3, 5e5]
    ev2 = detect(b2)
    first = [e for e in ev2 if e["i"] <= i + 1]
    assert [(e["i"], e["side"]) for e in first] == [(evs[0]["i"], evs[0]["side"])], "event depends on later bars"
    # and the detector run on bars truncated at the entry bar gives the same event
    ev3 = detect(b.iloc[:after].reset_index(drop=True))
    assert [(e["i"], e["side"]) for e in ev3] == [(evs[0]["i"], evs[0]["side"])], "event needs bars after entry bar"


def test_v2_single_event_no_lookahead():
    check_single_event(v2_detector)


def test_v1_logic_fails_the_same_check():
    with pytest.raises((AssertionError, IndexError)):
        check_single_event(v1_detector)


def test_dedupe_overlapping_files():
    df = pd.DataFrame({"open_time": [3, 1, 2, 2, 3], "open": [1] * 5, "high": [1] * 5, "low": [1] * 5,
                       "close": [1] * 5, "volume": [1] * 5, "tb": [1] * 5})
    assert list(s2.dedupe(df)["open_time"]) == [1, 2, 3]


def test_holdout_sealed():
    assert s2.SEAL_MS == int(pd.Timestamp("2025-07-01", tz="UTC").timestamp() * 1000)
    assert s2.month_of("x/BTCUSDT-1m-2025-07.csv") >= s2.SEAL_MONTH
    assert s2.month_of("x/BTCUSDT-1m-2025-09-03.csv") >= s2.SEAL_MONTH
    assert s2.month_of("x/BTCUSDT-1m-2025-06.csv") < s2.SEAL_MONTH
