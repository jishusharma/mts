"""Build the hourly rolling-DFA H series from DEV 1m BTCUSDT (2022-01-01..2025-06-30; later files never opened)."""
import importlib.util
import os

import numpy as np
import pandas as pd

import dfa

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
END_TS = int(pd.Timestamp("2025-07-01", tz="UTC").timestamp())


def load_tfb():
    p = os.path.join(REPO, "MyTradingSys", "research", "tf_break_event_study_2026-10-30", "study.py")
    spec = importlib.util.spec_from_file_location("tf_break_study", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def h_from_closes(bar_open, close, window=dfa.WINDOW):
    """H per 1h bar. bar_open: UTC epoch seconds of complete 1h bars (sorted). H[i] needs `window` returns whose bars
    are consecutive (no missing hour): else NaN. Return k = ln(close[k]/close[k-1]) uses bars k-1 and k, known at the
    close of bar k, so H[i] (returns i-window+1..i) is known at bar_open[i] + 3600."""
    bo = np.asarray(bar_open, np.int64)
    r = np.r_[np.nan, np.diff(np.log(np.asarray(close, float)))]
    n = len(r)
    h = np.full(n, np.nan)
    ok = np.r_[False, np.diff(bo) == 3600]          # return k is a true 1h return
    r0 = np.where(ok, r, 0.0)
    h_all = dfa.rolling_alpha(r0, window=window)
    cs = np.r_[0, np.cumsum(~ok)]                   # count of bad returns in each window
    for_ok = np.zeros(n, bool)
    idx = np.arange(window - 1, n)
    for_ok[idx] = (cs[idx + 1] - cs[idx + 1 - window]) == 0
    h[for_ok] = h_all[for_ok]
    return h


def build(df1m):
    tfb = load_tfb()
    df1m = df1m[df1m.t < END_TS]
    b = tfb.bars(df1m, 60)
    bo = b["t"].to_numpy(np.int64)
    h = h_from_closes(bo, b["c"].to_numpy(float))
    return pd.DataFrame({"bar_open": bo, "avail": bo + 3600, "h": h})
