"""Fail-first tests for p1_split.py. Expected values are hand-built from synthetic data."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "phase_tag"))
import p1_split as p  # noqa: E402
import phase_tag  # noqa: E402


def _daily(n=900, bump=None):
    dates = pd.date_range("2021-01-04", periods=n, freq="D")
    close = np.array([100.0 + 30 * np.sin(i / 40.0) + i * 0.1 for i in range(n)])
    if bump is not None:
        close[bump] += 500.0
    return pd.DataFrame({"date": dates, "close": close})


def test_join_uses_tag_of_day_t_built_without_bar_t():
    base = _daily()
    t = 600
    a = phase_tag.compute_tags(base)
    b = phase_tag.compute_tags(_daily(bump=t))  # change bar t's close only
    for c in p.TAGS:
        assert (a[c].iloc[t] == b[c].iloc[t]) or (pd.isna(a[c].iloc[t]) and pd.isna(b[c].iloc[t]))
    # the join hands the event on day t exactly row t's tag
    tags = a.copy()
    tags["date"] = base["date"]
    day = base["date"].iloc[t]
    ev = pd.DataFrame({"date": [day], "r": [1.0]})
    ev_dev = ev.copy()
    # force into DEV window via shifted calendar for this check
    shift = pd.Timestamp("2022-03-01") - day
    tags["date"] = tags["date"] + shift
    ev_dev["date"] = ev_dev["date"] + shift
    out = p.join_events(ev_dev, tags, "cowen_side")
    assert len(out) == 1 and out["label"].iloc[0] == tags["cowen_side"].iloc[t]
    # and bar t DOES change the tag of day t+1 (so the test could fail if lagged wrongly)
    assert any(a[c].iloc[t + 1] != b[c].iloc[t + 1] for c in p.TAGS)


def test_holdout_and_pre_dev_dropped():
    tags = pd.DataFrame({"date": pd.to_datetime(["2021-12-31", "2022-01-05", "2025-07-02"]), "cowen_side": ["above"] * 3})
    ev = pd.DataFrame({"date": ["2021-12-31", "2022-01-05", "2025-07-02"], "r": [1, 2, 3]})
    assert list(p.join_events(ev, tags, "cowen_side")["r"]) == [2]


def _planted(inject, seed=3):
    rng = np.random.default_rng(seed)
    n = 1200
    dates = pd.date_range("2022-01-01", periods=n, freq="D")[:n]
    dates = dates[dates <= p.DEV_END]
    n = len(dates)
    lab = np.array(["a", "b", "c"])[(np.arange(n) // 60) % 3]
    y = rng.normal(0, 1.0, n)
    if inject:
        idx = np.flatnonzero(lab == "b")
        pick = rng.choice(idx, size=int(0.2 * len(idx)), replace=False)
        y[pick] += 3.0
    return pd.DataFrame({"date": dates, "r": y, "label": lab, "week_parity": (dates.isocalendar().week.values % 2).astype(str)})


def test_planted_edge_detected_only_in_planted_cell():
    m = _planted(True)
    tab, nt = p.analyse(m, n_shifts=300, rng=np.random.default_rng(0))
    flagged = list(tab[tab.flagged]["cell"])
    assert flagged == ["b"]


def test_no_injection_flags_nothing():
    m = _planted(False)
    tab, nt = p.analyse(m, n_shifts=300, rng=np.random.default_rng(0))
    assert not tab.flagged.any()


def test_small_cell_not_decided():
    m = _planted(True).iloc[:100]
    tab, _ = p.analyse(m, n_shifts=100, rng=np.random.default_rng(0))
    assert set(tab.verdict) <= {"N_TOO_SMALL", "REPORT_ONLY"}
