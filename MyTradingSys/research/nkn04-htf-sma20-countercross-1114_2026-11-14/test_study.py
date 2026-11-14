"""Fast synthetic tests for study.py (no cache access, no network). Run: python -m pytest test_study.py -q"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study as st  # noqa: E402

ROOT = HERE.parents[2]


def synth(days=260, seed=1, start_day=18000):
    rng = np.random.default_rng(seed)
    n = days * 96
    t = start_day * st.DAY + st.M15 * np.arange(n, dtype=np.int64)
    r = rng.normal(0, 0.003, n) + 0.0002 * np.sin(np.arange(n) / 3000.0)
    c = 100 * np.exp(np.cumsum(r))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.001, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.001, n)))
    return st.fill_grid(t, o, h, l, c, np.ones(n))


def labels_for(a):
    days = np.unique(a["t"] // st.DAY)
    rng = np.random.default_rng(5)
    codes = rng.integers(0, 3, len(days)).astype(np.int8)
    return (days, codes, np.zeros(len(days)), "x")


STATE_KEYS = ["L", "atrd", "phase", "label", "wsma", "sma15", "hm", "atr15", "pb4", "rsi4", "hmax8", "lmin8", "mv", "x_dn", "x_up", "app_s", "app_l",
              "at_s", "at_l", "away_s", "away_l", "wc", "fp_s", "fp_l"]


def same(x, y):
    if x.dtype.kind == "f":
        return np.allclose(x, y, equal_nan=True, rtol=0, atol=1e-9)
    return (x == y).all()


def test_lookahead_poke_every_state():
    a = synth()
    lab = labels_for(a)
    full = st.bar_state(a, lab)
    n = full["n"]
    rng = np.random.default_rng(9)
    for T in (int(n * 0.55) + 7, int(n * 0.8) + 33, int(n * 0.8) + 58):  # includes bars in the middle of a 4h bar, an hour and a day
        b = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in a.items()}
        for k in ("o", "h", "l", "c"):
            b[k][T + 1:] = b[k][T + 1:] * (1 + rng.normal(0, 0.2, n - T - 1))  # poke every future bar
        poked = st.bar_state(b, lab)
        for k in STATE_KEYS:
            assert same(full[k][:T + 1], poked[k][:T + 1]), f"look-ahead in {k} at T={T}"
    # truncation: drop all bars after T, state up to T unchanged
    T = int(n * 0.7) + 21
    cut = {k: (v[:T + 1].copy() if isinstance(v, np.ndarray) else v) for k, v in a.items() if k != "prov"}
    cut["prov"] = a["prov"]
    tr = st.bar_state(cut, lab)
    for k in STATE_KEYS:
        assert same(full[k][:T + 1], tr[k][:T + 1]), f"truncation changes {k}"


def test_lookahead_has_teeth():
    """the poke test must detect a deliberate leak: a phase built from the SAME day's close differs from the lagged one."""
    a = synth()
    td, _, hd, ld, cd = st.resample(a["t"], a["o"], a["h"], a["l"], a["c"], 96)
    ph = st.coin_day_phase(hd, ld, cd)
    lagged = st.bar_state(a, labels_for(a))["phase"]
    day = a["t"] // st.DAY
    same_day = np.full(len(day), 0, np.int8)
    pos = np.searchsorted(td // st.DAY, day)
    ok = (pos < len(td)) & ((td // st.DAY)[np.minimum(pos, len(td) - 1)] == day)
    same_day[ok] = ph[pos[ok]]
    assert (same_day != lagged).any()


def test_adx_matches_layer_module():
    spec = importlib.util.spec_from_file_location("adx_layer", ROOT / "MyTradingSys" / "backtest" / "layers" / "adx" / "adx.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = np.random.default_rng(3)
    c = 100 + np.cumsum(rng.normal(0, 1, 300))
    h, l = c + rng.random(300), c - rng.random(300)
    dp, dm, ax = m.adx_di(list(h), list(l), list(c), 14)
    p2, m2, a2 = st.adx_di(h, l, c, 14)
    for x, y in ((dp, p2), (dm, m2), (ax, a2)):
        xx = np.array([np.nan if v is None else v for v in x])
        assert np.allclose(xx, y, equal_nan=True, atol=1e-9)


def test_fee_on_both_legs_hand_number():
    # entry 100, halves exit at 102 and 100, dist 1.2, 12 bp round trip = 6 bp on entry notional + 6 bp on exit notional
    # fee = (0.0006*100 + 0.0006*(0.5*102+0.5*100)) / 1.2 = (0.06 + 0.0606)/1.2 = 0.1005
    assert st.fee_r(100.0, 102.0, 100.0, 1.2, 12.0) == pytest.approx(0.1005, abs=1e-9)
    # maker 6 bp = 3 bp each leg
    assert st.fee_r(100.0, 102.0, 100.0, 1.2, 6.0) == pytest.approx(0.05025, abs=1e-9)
    res = dict(xa=102.0, xb=100.0)
    g, net = st.trade_net(100.0, res, 1, 1.2, 12.0)
    assert g == pytest.approx(0.5 * 2.0 / 1.2)
    assert net == pytest.approx(g - 0.1005)


def test_split_by_signal_bar():
    # signal on 2023-12-31 23:45 (DEV) whose entry bar and exit are in 2024 stays DEV; the first bar of 2024 is VAL
    last_dev = st.SPLIT - st.M15
    assert st.split_of([last_dev, st.SPLIT, st.SPLIT + st.DAY]).tolist() == [0, 1, 1]


def flat(n, price=100.0):
    z = np.full(n, price)
    return z.copy(), z.copy(), z.copy(), z.copy()


def test_stop_gap_fill_long_and_short():
    o, h, l, c = flat(10)
    # long, entry bar 1 at 100, dist 2 -> stop 98; bar 3 gaps open 95 through the stop
    o[3], h[3], l[3], c[3] = 95, 96, 94, 95
    r = st.simulate(o, h, l, c, 0, 1, 50.0, 100.0, 2.0)
    assert r["reason"] == "stop" and r["xb"] == 95 and r["xi"] == 3
    # short mirror: stop 102, bar 3 gaps up to open 105
    o, h, l, c = flat(10)
    o[3], h[3], l[3], c[3] = 105, 106, 104, 105
    r = st.simulate(o, h, l, c, 0, -1, 150.0, 100.0, 2.0)
    assert r["reason"] == "stop" and r["xb"] == 105


def test_target_gap_fills_at_open_and_stop_first_same_bar():
    o, h, l, c = flat(10)
    # long dist 2 -> target 104; bar 2 gaps open 106 above the target: half fills at 106 (open), not 104
    o[2], h[2], l[2], c[2] = 106, 107, 106, 107
    # runner then exits when the next bar breaks the highest prior low (bar 3 low 100 < trail 106)
    o[3], h[3], l[3], c[3] = 107, 107, 100, 101
    r = st.simulate(o, h, l, c, 0, 1, 50.0, 100.0, 2.0)
    assert r["xa"] == 106 and r["tgt_hit"]
    assert r["xb"] == 106 and r["reason"] == "runner"  # trail 106, bar opens 107, low 100 -> fill at min(trail, open) = 106
    # stop and target inside one bar: stop wins
    o, h, l, c = flat(10)
    o[2], h[2], l[2], c[2] = 100, 105, 97, 100
    r = st.simulate(o, h, l, c, 0, 1, 50.0, 100.0, 2.0)
    assert r["reason"] == "stop" and r["xb"] == 98 and not r["tgt_hit"]


def test_half_at_2r_runner_trail_hand_case_and_two_closes():
    o, h, l, c = flat(14)
    # long e=100 dist 2 stop 98 target 104. bar1 quiet. bar2 high 104.5 -> half at 104 (open 100, no gap), trail low=99.5
    o[2], h[2], l[2], c[2] = 100, 104.5, 99.5, 104
    # bar3: low 101 (> trail 99.5, ratchet trail to 101), bar4: low 103, bar5 breaks: low 102.5 <= trail 103 -> fill min(103, open 104)=103
    o[3], h[3], l[3], c[3] = 104, 106, 101, 105
    o[4], h[4], l[4], c[4] = 105, 107, 103, 106
    o[5], h[5], l[5], c[5] = 104, 105, 102.5, 103
    r = st.simulate(o, h, l, c, 0, 1, 50.0, 100.0, 2.0)
    assert (r["xa"], r["xb"], r["xi"], r["reason"]) == (104, 103, 5, "runner")
    g, _ = st.trade_net(100.0, r, 1, 2.0, 12.0)
    assert g == pytest.approx(((104 - 100) + (103 - 100)) / 2 / 2.0)  # 1.75 R
    # two consecutive closes through L (long: below L=99) from the entry bar on exit at the second close
    o, h, l, c = flat(10)
    for k in (3, 4):
        o[k], h[k], l[k], c[k] = 99.5, 99.9, 98.5, 98.9
    r = st.simulate(o, h, l, c, 0, 1, 99.0, 100.0, 5.0)
    assert r["reason"] == "close_through" and r["xi"] == 4 and r["xb"] == 98.9
    # a single close through L does not exit
    o, h, l, c = flat(10)
    o[3], h[3], l[3], c[3] = 99.5, 99.9, 98.5, 98.9
    r = st.simulate(o, h, l, c, 0, 1, 99.0, 100.0, 5.0)
    assert r["reason"] == "time"


def test_planted_edge_short_through_simulator():
    # falling market after the trigger: short must have positive net R, the long the mirror negative
    n = 40
    o = 100 - 0.5 * np.arange(n)
    c = o - 0.4
    h, l = o + 0.1, c - 0.1
    r = st.simulate(o, h, l, c, 2, -1, 1e9, o[3], 1.2)
    g, net = st.trade_net(o[3], r, -1, 1.2, 12.0)
    assert g > 1 and net > 0
    g2, net2 = st.trade_net(o[3], st.simulate(o, h, l, c, 2, 1, 0.0, o[3], 1.2), 1, 1.2, 12.0)
    assert net2 < 0


def test_stop_dist_floor_and_structure():
    assert st.stop_dist(-1, 100.0, 100.5, 0.2) == pytest.approx(1.2)      # 1.2% floor wins
    assert st.stop_dist(-1, 100.0, 105.0, 0.2) == pytest.approx(5.0)      # structure wins
    assert st.stop_dist(1, 100.0, 99.0, 3.0) == pytest.approx(3.0)        # ATR wins


def cols(**kw):
    n = len(kw["side"])
    base = dict(coin=np.array(["X"] * n), i=np.arange(n), t=np.full(n, st.SPLIT + 1), at=np.ones(n, bool), v1=np.ones(n, bool), v2=np.ones(n, bool),
                fp=np.zeros(n, bool), wc=np.zeros(n, bool))
    base.update({k: np.array(v) for k, v in kw.items()})
    return base


def test_control_phase_trade_never_in_primary_cell():
    L, D, R, U = st.LAB_MARKDOWN, st.DOWN, st.RANGE, st.UP
    C = cols(side=[-1, -1, -1, 1, 1, -1, 1, -1], phase=[D, D, U, U, D, R, R, D], label=[L, st.LAB_OTHER, st.LAB_MARKUP, st.LAB_MARKUP, L, L, st.LAB_NONE, st.LAB_NONE])
    prim = np.zeros(8, bool)
    for cid in st.PRIMARY:
        prim |= st.cell_mask(C, st.CELLS[cid - 1])
    # only row 0 (short, DOWN x MARKDOWN) and row 3 (long, UP x MARKUP) are primary
    assert prim.tolist() == [True, False, False, True, False, False, False, False]
    # every control cell is disjoint from the primary cell it mirrors
    for cell in st.CELLS:
        m = st.cell_mask(C, cell)
        if cell["role"] in ("CONTROL C1", "CONTROL C2", "CONTROL C3", "CONTROL C4", "CONTROL C5", "CONTROL C6"):
            assert not (m & prim).any()
    # away-level and at-level never overlap
    C2 = cols(side=[-1, -1], phase=[D, D], label=[L, L], at=[True, False])
    at_m = st.cell_mask(C2, st.CELLS[0])
    aw_m = st.cell_mask(C2, st.CELLS[6])
    assert at_m.tolist() == [True, False] and aw_m.tolist() == [False, True]
    assert st.cell_mask(C2, st.CELLS[0]).sum() == 1
    assert len(st.CELLS) == 22 and len(st.PRIMARY) == 6 and st.PRIMARY == [1, 2, 3, 4, 5, 6]


def test_layer_variants_nested():
    C = cols(side=[-1, -1, -1], phase=[st.DOWN] * 3, label=[st.LAB_MARKDOWN] * 3, v1=[False, True, True], v2=[False, False, True])
    v = [st.cell_mask(C, st.CELLS[k]).tolist() for k in (0, 1, 2)]
    assert v == [[True, True, True], [False, True, True], [False, False, True]]


def test_bh_and_dedupe_and_bootstrap():
    q = st.bh_q([0.01, 0.04, 0.03, 0.5])
    assert q == pytest.approx([0.04, 0.0533333, 0.0533333, 0.5], abs=1e-6)
    keep = st.dedupe(np.array(["A", "A", "A", "B"]), np.array([10, 12, 30, 12]), np.array([20, 25, 31, 15]))
    assert keep.tolist() == [True, False, True, True]
    rng = np.random.default_rng(1)
    x = np.full(50, 0.3)
    assert st.boot_ci_low(x, rng) == pytest.approx(0.3)
    lo, p = st.day_cluster(x, np.arange(50) // 5, rng)
    assert lo == pytest.approx(0.3) and p < 0.01
    assert st.ex_best5(np.array([1.0, 1, 1, 1, 1, 1, 100, 100, 100, 100, 100.0])) == pytest.approx(1.0)


def test_4h_index_uses_only_closed_bars():
    a = synth(days=60)
    S = st.bar_state(a, labels_for(a))
    t4, _, _, _, c4 = st.resample(a["t"], a["o"], a["h"], a["l"], a["c"], 16)
    pb = st.bollinger_pb(c4, 20)
    for i in (2000, 2001, 2003, 2010, 2015, 3000):
        j = np.searchsorted(t4 + st.H4, a["t"][i], side="right") - 1
        assert t4[j] + st.H4 <= a["t"][i] < t4[j] + 2 * st.H4  # last closed 4h bar, never the one containing bar i
        assert S["pb4"][i] == pytest.approx(pb[j], nan_ok=True)


def test_loader_asserts(tmp_path):
    t = np.array([0, 900000, 1800000], dtype=np.int64)
    with pytest.raises(AssertionError):
        st.fill_grid(np.array([0, 900000, 900000]), *(np.ones(3),) * 5)
    with pytest.raises(AssertionError):
        st.fill_grid(np.array([0, 900001]), *(np.ones(2),) * 5)
    g = st.fill_grid(np.array([0, 900000, 3600000], dtype=np.int64), *(np.arange(3.0) + 1,) * 5)
    assert len(g["t"]) == 5 and g["filled"].tolist() == [False, False, True, True, False] and g["prov"]["gaps"] == 1
    np.savez(tmp_path / "XUSDT_15m.npz", ts=t, o=np.ones(3), h=np.ones(3), l=np.ones(3), c=np.ones(3), v=np.ones(3))
    assert st.load_coin("X", tmp_path / "XUSDT_15m.npz")["prov"]["key"] == "ts"
    np.savez(tmp_path / "YUSDT_15m.npz", o=np.ones(3), h=np.ones(3), l=np.ones(3), c=np.ones(3), v=np.ones(3))
    with pytest.raises(AssertionError):
        st.load_coin("Y", tmp_path / "YUSDT_15m.npz")


def test_candidate_trigger_hand_case():
    """a short trigger requires: close crosses below SMA20 of 15m, prior 2h move up, approach from below L, HM not bullish; at-level flag from the ATR band."""
    a = synth(days=120, seed=4)
    lab = labels_for(a)
    S = st.bar_state(a, lab)
    cs = st.candidates(S, "X")
    assert len(cs) > 0
    for sym, i, side, t, ph, lb, at, v1, v2, fp, wc in cs[:200]:
        assert t == S["t"][i] and ph in (1, 2, 3)
        if side < 0:
            assert S["c"][i] < S["sma15"][i] and S["mv"][i] > 0 and S["c"][i - 8] < S["L"][i] and S["hm"][i] != 1
        else:
            assert S["c"][i] > S["sma15"][i] and S["mv"][i] < 0 and S["c"][i - 8] > S["L"][i] and S["hm"][i] != -1
