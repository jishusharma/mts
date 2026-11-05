"""Fail-first tests for the c1v2_counts.py count runner (card wavetrend-c1-v2, step 3).

Two defects in the first runner, both caught here on synthetic data (no klines, no outcome):
1. run() assigned `c1_v2 = c1_v2.events(...)` inside the function, so the module name was a
   local -> UnboundLocalError before any count was made.
2. select_cells.select only knows event "C1"; rows labelled "C1_v2" could never be chosen,
   so every run froze "no cell" whatever the counts were.
"""
import numpy as np

import c1v2_counts as cc
import count_events as ce
import select_cells as sc


def _fake_pipeline(monkeypatch):
    n = 60
    H = np.zeros(n); L = np.zeros(n)
    H[10], H[30] = 10.0, 12.0                         # higher high, confirmed at 12 and 32
    wt1 = np.zeros(n)
    wt1[10], wt1[30] = 70.0, 60.0                     # confirmed WT peaks, lower second peak
    B = {"H": H, "L": L}
    monkeypatch.setattr(cc, "manifest_check", lambda d: ["fake.csv"])
    monkeypatch.setattr(ce, "load_dev", lambda files: B)
    monkeypatch.setattr(ce, "resample", lambda A, m: A)
    monkeypatch.setattr(ce, "wt_series", lambda B_: (wt1, wt1))
    monkeypatch.setattr(ce, "context", lambda *a: {"vol": np.ones(n), "part": np.ones(n)})
    monkeypatch.setattr(ce, "TFS", {"1h": 60})
    monkeypatch.setattr(ce, "HTF", {"1h": None})


def test_run_counts_c1v2_events(monkeypatch):
    _fake_pipeline(monkeypatch)
    res = cc.run()
    c1_v1, c1_v2e, _, _, m, n = res["1h"]
    assert c1_v2e == [(32, 1)]                        # later confirmation of the second pair (30+2)


def test_select_v2_picks_c1v2_rows():
    rows = [{"tf": "1h", "event": "C1_v2", "var": "ALL", "bin": "all", "events": 400, "event_days": 300,
             "side_up": 200, "side_lo": 200, "mde_d": 0.2},
            {"tf": "1h", "event": "C1_v2", "var": "vol", "bin": "hi", "events": 200, "event_days": sc.FLOOR,
             "side_up": 100, "side_lo": 100, "mde_d": 0.3},
            {"tf": "1h", "event": "C1_v2", "var": "part", "bin": "lo", "events": 100, "event_days": sc.FLOOR - 1,
             "side_up": 50, "side_lo": 50, "mde_d": 0.31}]
    chosen = cc.select_v2(rows)
    assert [(r["tf"], r["event"], r["var"], r["bin"]) for r in chosen] == [("1h", "C1_v2", "vol", "hi")]
