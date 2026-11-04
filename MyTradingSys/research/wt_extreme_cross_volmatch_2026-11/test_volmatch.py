"""Tests for wt_extreme_cross_volmatch_2026-11/study.py (synthetic data only; no files read)."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location("wt_volmatch_study", HERE / "study.py")
st = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(st)


def test_baseline_matches_atr_decile():
    """Event bars all sit in the top ATR decile: their baseline is the mean MFE of that decile only, not of all bars."""
    rng = np.random.default_rng(1)
    atr = rng.uniform(0.01, 1.0, 5000)
    mfe = atr * 2.0                              # MFE grows with volatility, as on real bars
    edges = st.decile_edges(atr)
    dec = st.decile_of(atr, edges)
    assert set(np.unique(dec)) == set(range(10))
    base = st.decile_baseline(mfe, dec)
    ev_atr = np.array([0.99, 0.995, 0.999])      # all in decile 9
    ev_dec = st.decile_of(ev_atr, edges)
    assert list(ev_dec) == [9, 9, 9]
    want = mfe[dec == 9].mean()
    assert base[9] == pytest.approx(want)
    assert base[ev_dec].mean() == pytest.approx(want)
    assert base[9] > mfe.mean() * 1.5            # the unmatched mean would understate it


def test_atr_pct_wilder():
    """Wilder ATR(14) on constant 1.0 true range is 1.0 from bar 13 on; as % of a close of 100 that is 1.0 %."""
    n = 40
    c = np.full(n, 100.0)
    h, l = c + 0.5, c - 0.5
    a = st.atr_pct(h, l, c, 14)
    assert np.isnan(a[12])
    assert a[13] == pytest.approx(1.0)
    assert a[-1] == pytest.approx(1.0)


def test_loader_refuses_after_dev_end():
    with pytest.raises(ValueError):
        st.load_sym_1m("ETHUSDT", st.DEV_END_MS + 60000, root=HERE)


def test_cluster_key_separates_symbols():
    assert st.cluster_key("BTCUSDT", 19000) != st.cluster_key("ETHUSDT", 19000)
