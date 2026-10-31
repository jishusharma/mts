"""Tests for run_v3_l3.py, derived from FABIO_V3_SPEC.md 7.2 / 8 and PRE_REG_FABIO_V3.md (counts and rules by hand)."""
import datetime as dt

from MyTradingSys.backtest.layers.fabio import run_v3_l3 as r


def test_grid_cell_counts_match_spec_7_2():
    cells = r.grid()
    by = {m: sum(1 for k, (mm, _) in cells.items() if mm == m) for m in "ABCD"}
    assert by == {"A": 48, "B": 24, "C": 16, "D": 24}          # 3*2*2*2*2, 3*2*2*2, 2*2*2*2, 3*2*2*2
    assert len(cells) == 112


def test_every_cell_sets_the_engine_required_keys():
    for k, (m, c) in r.grid().items():
        for key in ("N", "p", "z_hi", "m_c", "f", "g", "entry_mode", "mgmt"):
            assert key in c, (k, key)
        assert c["mgmt"] == "event"                            # main grid runs mgmt event (spec 7.2)


def test_registered_trial_count_is_139():
    # 6 (stage 1) + 112 (A,B,C,D) + 20 (variants) + 1 (B trail) = 139
    assert 6 + 112 + 20 + 1 == r.N_DECLARED


def test_variants_dist_needs_be_k_and_only_b_has_trail():
    cfg = r.grid()["B|N60|z2|f0.003|rest"][1]
    v = r.variants("B", cfg)
    assert v["dist_k1.0"]["be_k"] == 1.0 and v["dist_k2.0"]["mgmt"] == "dist"
    assert v["trail"]["target_mode"] == "trail"
    assert "trail" not in r.variants("A", r.grid()["A|N60|p0.05|f0.003|rest|goff"][1])


def test_split_never_touches_the_holdout():
    assert r.OOS_RANGE[1] < dt.date(2026, 6, 26) and r.IS_RANGE[1] < r.OOS_RANGE[0]


def test_summ_hand_numbers():
    s = r.summ([1.0, -1.0, 0.0, 2.0])            # mean 0.5, trade days 3, wins 2/3, pstdev sqrt(1.25): squares .25+2.25+.25+2.25=5, /4
    assert s["mean"] == 0.5 and s["trade_days"] == 3 and s["win"] == 2 / 3
    assert abs(s["sd"] - 1.25 ** 0.5) < 1e-12


def test_week_boot_constant_series_has_degenerate_ci():
    d = [dt.date(2026, 1, 5) + dt.timedelta(days=i) for i in range(14)]
    lo, hi = r.week_boot(d, [0.3] * 14, n_boot=50)
    assert abs(lo - 0.3) < 1e-12 and abs(hi - 0.3) < 1e-12


def test_run_day_counts_no_setup_as_zero_r():
    # 5 flat bars: no model can fire -> (0.0, 'none'); engine runs must not crash on a short window
    bars = [{"t": 60000 * i, "o": 100.0, "h": 100.0, "l": 100.0, "c": 100.0, "buy_vol": 1.0, "sell_vol": 1.0, "delta": 0.0,
             "b99_buy_vol": 0.0, "b99_sell_vol": 0.0, "b999_buy_vol": 0.0, "b999_sell_vol": 0.0, "thr_days": 30,
             "fp": "100:1.0:1.0", "cvd": 0.0, "cvd_day": 0.0} for i in range(5)]
    cfg = r.grid()["C|m5|f0.003|rest|goff"][1]
    out = r._run_day((bars, [], [("k", "C", cfg, 2.0)]))
    assert out["k"][0] == 0.0


class _NeverPool:
    """Pool whose futures never complete: the B099 stall."""
    def submit(self, fn, arg):
        from concurrent.futures import Future
        return Future()


class _DeadPool:
    """Pool whose worker died: the B099 broken pool."""
    def submit(self, fn, arg):
        from concurrent.futures import Future
        from concurrent.futures.process import BrokenProcessPool
        f = Future()
        f.set_exception(BrokenProcessPool("worker died"))
        return f


def _one_window():
    return [{"date": dt.date(2026, 1, 5), "bars": [], "prior": []}]


def test_b099_stalled_phase_fails_closed(monkeypatch):
    import pytest
    monkeypatch.setattr(r, "TASK_TIMEOUT", 0.05)
    with pytest.raises(r.RunFailed, match="oos_grid.*2026-01-05"):
        r.run_cells(_NeverPool(), _one_window(), {"k": ("C", {})}, 2.0, "oos_grid")


def test_b099_dead_worker_fails_closed():
    import pytest
    with pytest.raises(r.RunFailed, match="BrokenProcessPool"):
        r.run_cells(_DeadPool(), _one_window(), {"k": ("C", {})}, 2.0, "oos_grid")


def test_model_b_in_trade_fill_is_managed_not_scored_zero(monkeypatch):
    # Hand numbers (spec 4 model B / 5.2): balance H 100 L 98; probe bar 1 (c 100.5, absorbed), reclaim bar 2 (c 99.9) -> short.
    # rest limit 99.9 fills bar 3 (h 100.0); Xp 100.5 -> D = |100.5-99.9| + 0.1 = 0.7 (<= Dmax 1% * 99.9); target E_s = 98.0 hit bar 4 (l 97.8).
    # gross R = (99.9 - 98.0) / 0.7 = 2.7142857; maker entry + maker target -> fee 0; slip 0 -> net R 19/7 (old code scored 0.0).
    from MyTradingSys.backtest.layers.fabio.v3 import engine, models
    rows = [(99, 99.5, 98.8, 99.0), (99.0, 100.5, 99.0, 100.5), (100.5, 100.5, 99.5, 99.9), (99.9, 100.0, 99.5, 99.4),
            (99.4, 99.6, 97.8, 98.2)]
    bars = [{"t": k * 60000, "o": o, "h": h, "l": lo, "c": c, "buy_vol": 0.0, "sell_vol": 0.0, "delta": 0.0,
             "b99_buy_vol": 0.0, "b99_sell_vol": 0.0, "b999_buy_vol": 0.0, "b999_sell_vol": 0.0, "thr_days": 30, "fp": ""}
            for k, (o, h, lo, c) in enumerate(rows)]
    monkeypatch.setattr(models, "balance", lambda b, i, N, k, bs: {"H": 100.0, "L": 98.0, "R": 2.0, "poc": 99.0})
    cfg = dict(N=1, p=0.10, f=0.003, entry_mode="rest", mgmt="dist", be_k=1.0, slip_bps=0.0)
    absb = [0, 1, 0, 0, 0]
    st = engine._scan("B", bars, 0, 4, cfg, {"k_bal": 0.8, "bin_size": 50.0, "tier": "99", "gate": None, "absb": absb, "ctrl": None})
    assert st["state"] == "IN_TRADE"
    ctx = {"s8_kw": {}, "ctrl": None, "absb": absb}
    t = engine._manage("B", st, bars, 0, 4, cfg, ctx)
    assert t is not None and t["reason"] == "target"
    assert abs(t["net_r"] - 19 / 7) < 1e-9
