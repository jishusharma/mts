"""Tests for atlas.py (card wavetrend-dev-atlas). Run: python -m pytest <this file>. Expected values by hand."""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atlas  # noqa: E402
import count_events as ce  # noqa: E402


def test_frozen_cells_load_and_unknown_cell_raises():
    cells = atlas.load_cells()
    assert sorted(cells) == [f"W{i:02d}" for i in range(1, 10)]
    with pytest.raises(KeyError):
        atlas.require_cell(cells, "W10", "5m", "A1_L53", "trend", "trend_with")
    with pytest.raises(ValueError):                       # same id, changed bin = changing a cell after seeing results
        atlas.require_cell(cells, "W01", "5m", "A1_L53", "trend", "trend_against")


def test_cells_not_in_prereg_text_raise(tmp_path):
    bad = tmp_path / "CELLS.csv"
    bad.write_text("cell,tf,event,context_var,bin,events,event_days,side_up,side_lo,mde_d_holm12\n"
                   "W99,5m,A1_L53,trend,trend_with,1,1,1,0,0.1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        atlas.load_cells(bad)


def test_direction_convention():
    assert atlas.direction("A1_L53", 1) == -1 and atlas.direction("A2_L53", -1) == 1
    assert atlas.direction("B1", 1) == 1 and atlas.direction("B2", -1) == -1 and atlas.direction("C1", 1) == -1


def test_forward_outcomes_hand_values():
    O = np.array([10., 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23.])
    C = O + 0.5
    B = {"O": O, "H": C + 1, "L": O - 1, "C": C, "V": np.ones(len(O))}
    F = atlas.forward(B)
    assert F[4][0] == pytest.approx(C[4] / O[1] - 1)       # open(t+1) -> close(t+4)
    assert F["up"][0] == pytest.approx(B["H"][1:13].max() / O[1] - 1)
    assert F["dn"][0] == pytest.approx(B["L"][1:13].min() / O[1] - 1)
    assert np.isnan(F[12][5])                              # nothing after the series end


def test_cluster_se_and_wilson_and_holm():
    m, se, nd = atlas.cluster_mean_se([1., 3., 5., 7.], [0, 0, 1, 1])
    assert m == 4 and nd == 2 and se == pytest.approx(np.sqrt(2 * 4 ** 2) / 4)   # day sums of deviations: -4, +4
    lo, hi = atlas.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-3) and hi == pytest.approx(0.7634, abs=1e-3)
    rej, adj = atlas.holm([0.001, 0.04, 0.03], 0.05)       # thresholds 0.05/3, 0.05/2, 0.05
    assert rej == [True, False, False] and adj[0] == pytest.approx(0.003)


def test_bin_mask_matches_bin_of():
    n = 400
    rng = np.random.default_rng(3)
    ctx = {"vol": rng.random(n), "trend": rng.integers(-1, 2, n), "part": rng.random(n), "hour3": np.zeros(n, int),
           "htf": rng.normal(0, 60, n)}
    ctx["trend"][::17] = 9
    ctx["htf"][::23] = np.nan
    edges = {"vol": (0.3, 0.6), "part": (0.3, 0.6)}
    for side in (1, -1):
        for var, bn in (("trend", "trend_with"), ("trend", "trend_mixed"), ("htf", "htf_mid"), ("htf", "htf_with")):
            mk = atlas.bin_mask(ctx, var, bn, side)
            ref = np.array([ce.bin_of(ctx, edges, t, side)[var] == bn for t in range(n)])
            assert (mk == ref).all()
    with pytest.raises(ValueError):
        atlas.bin_mask(ctx, "vol", "vol_lo", 1)


def test_control_arm_present_and_random_clock_unbiased_on_noise():
    """On a driftless random walk a WT event cell has no effect vs its random clock, and every arm exists."""
    rng = np.random.default_rng(11)
    n = 6000
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.003, n)))
    B = {"O": np.r_[c[0], c[:-1]], "H": c * 1.001, "L": c * 0.999, "C": c, "V": np.ones(n)}
    wt = ce.wt_series(B)
    res = {"5m": {"ctx": ce.context(B, wt[0], 5, None, None), "edges": None, "evs": {}}}
    res["5m"]["edges"] = {"vol": ce.tercile_edges(res["5m"]["ctx"]["vol"]), "part": ce.tercile_edges(res["5m"]["ctx"]["part"])}
    res["5m"]["evs"]["A1_L53"] = ce.ev_A(wt[0], 53, 3)[0]
    tfo = atlas.Tf("5m", res, {"5m": B}, {"5m": wt})
    out = atlas.event_arms(tfo, "A1_L53", res["5m"]["evs"]["A1_L53"], np.random.default_rng(1), ("trend", "trend_with"))
    assert {"conj", "random_clock", "context_alone"} <= set(out)
    d = atlas.diff_test(out["conj"], out["random_clock"])
    assert abs(d["z"]) < 3.5
