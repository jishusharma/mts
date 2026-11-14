"""Wiring tests for reclaim_close_stop_10sym_2026-11-15: cost comes from research_kit, ten symbols, stats net/cluster arithmetic, and the OOS window
filter on reclaim-bar CLOSES (synthetic random-walk 4h klines patched in for the cache)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("rc10_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)
rk = study.rk


def test_constants():
    assert len(study.SYMS) == 10 and study.COST == rk.TAKER_RT_PCT / 100.0
    assert study.OOS_START == 1704067200000 and study.SPLIT_MS > study.OOS_START and study.OOS_END > study.SPLIT_MS


def test_stats_net_and_days():
    sub = [dict(gross=0.01, net=0.01 - study.COST, day=d, exit="stop", hold=2) for d in (1, 1, 2, 3)]
    r = study.stats(sub)
    assert r["n"] == 4 and r["days"] == 3
    assert abs(r["gross"] - 1.0) < 1e-9 and abs(r["net"] - (1.0 - rk.TAKER_RT_PCT)) < 1e-9


def _walk(n, t0, step):
    rng = np.random.default_rng(7)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    rows = []
    for i in range(n):
        o = c[i - 1] if i else c[0]
        rows.append([t0 + i * step, o, max(o, c[i]) * 1.01, min(o, c[i]) * 0.99, c[i], 1.0])
    return rows


def test_window_filter_and_net(monkeypatch):
    t0 = study.OOS_START - 200 * 4 * 3600000
    rows = _walk(2500, t0, 4 * 3600000)
    monkeypatch.setattr(study, "load", lambda sym, iv: rows)
    ev = study.sym_events("BTC", "4h", lambda t: "range")
    assert len(ev) > 5
    for e in ev:
        assert study.OOS_START <= e["t_close"] < study.OOS_END
        assert abs(e["net"] - (e["gross"] - study.COST)) < 1e-12
        assert e["win"] == ("w1" if e["t_close"] < study.SPLIT_MS else "w2")
