"""Synthetic-bar tests for T9 (core + stats). No data cache. Run: python -m pytest test_t9_core.py"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t9_core as core  # noqa: E402
import t9_stats as st  # noqa: E402

DAY = 86400000


def epoch_day(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


MON0 = epoch_day(2021, 1, 4)           # a Monday
assert (MON0 + 3) % 7 == 0
NW = 75


class AllState:
    def __init__(self, v="BULL"):
        self.v = v

    def get(self, k, default=None):
        return self.v


def uptrend(n=7 * NW, g=0.004):
    return 100.0 * (1 + g) ** np.arange(n)


def build(closes, over=None, r=0.003, start=MON0, ended=False):
    over = over or {}
    rows = []
    for i, c in enumerate(closes):
        o = closes[i - 1] if i else c
        row = (o, max(o, c) * (1 + r), min(o, c) * (1 - r), c)
        row = over.get(i, row)
        rows.append(((start + i) * DAY,) + tuple(row))
    a = np.array(rows, float)
    pull = a[-1, 0] + (400 * DAY if ended else DAY)
    return core.Coin("SYN", a, pull_ms=int(pull))


def dip(closes, w, frac=0.4):
    """Sunday-only spike: low of the Sunday bar of week w goes to frac x close (open and close unchanged)."""
    i = 7 * w + 6
    c = closes[i]
    o = closes[i - 1]
    return {i: (o, max(o, c) * 1.003, frac * c, c)}


def planted(weeks=(60, 70)):
    closes = uptrend()
    over = {}
    for w in weeks:
        over.update(dip(closes, w))
    return closes, over


# ------------------------------------------------------------------ formulas
def test_ema_worked_example_formulas_md():
    e = core.ema([50, 55, 45, 60], 3)
    assert np.isnan(e[0]) and np.isnan(e[1])
    assert e[2] == 50.0 and abs(e[3] - 55.0) < 1e-12


def test_atr_wilder_seed_and_recursion():
    h = np.array([11.0] * 20)
    l = np.array([9.0] * 20)
    c = np.array([10.0] * 20)
    a = core.wilder_atr(h, l, c, 14)
    assert np.isnan(a[12]) and abs(a[13] - 2.0) < 1e-12 and abs(a[19] - 2.0) < 1e-12
    h2 = h.copy()
    h2[14] = 13.0                      # TR 4 at index 14
    a2 = core.wilder_atr(h2, l, c, 14)
    assert abs(a2[14] - (2.0 * 13 + 4.0) / 14) < 1e-12


def test_fee_constants_from_fees_py_and_hand_number():
    from fees import BINANCE_TAKER, SLIPPAGE_RT_S13
    assert core.FEE_RT == 2 * BINANCE_TAKER + SLIPPAGE_RT_S13
    assert abs(core.FEE_RT - 0.0012) < 1e-12            # 12 bp, hand number


# ------------------------------------------------------------------ weekly resample
def test_weekly_bars_whole_iso_weeks_close_is_sunday():
    closes = uptrend(7 * 3 + 3)
    c = build(closes)
    assert c.nw == 3 and len(c.wc) == 3
    assert c.wc[0] == closes[6] and c.wc[2] == closes[20]


def test_sunday_spike_changes_signal_on_monday_never_on_sunday():
    closes, over = planted((60,))
    base = build(closes)                                   # no spike
    spike = build(closes, over)
    w, d0 = 60, 7 * 61
    assert not any(s["w"] == w for s in core.signals(base, AllState()))
    assert any(s["w"] == w and s["d0"] == d0 for s in core.signals(spike, AllState()))
    # data through Saturday of week w: the week is incomplete, no signal for it, whatever the Sunday does
    sat = build(closes[:7 * w + 6], {k: v for k, v in over.items() if k < 7 * w + 6})
    assert sat.nw == w and not any(s["w"] == w for s in core.signals(sat, AllState()))
    # data through Sunday only (no Monday bar): entry bar absent, so no tradable signal yet
    sun = build(closes[:7 * w + 7], over)
    assert sun.nw == w + 1 and not any(s["w"] == w for s in core.signals(sun, AllState()))
    # Monday bar present: the signal exists, built only from bars through Sunday
    mon = build(closes[:d0 + 1], over)
    assert any(s["w"] == w and s["d0"] == d0 for s in core.signals(mon, AllState()))


def test_signal_ignores_bars_after_signal_week_look_ahead():
    closes, over = planted((60, 70))
    full = build(closes, over)
    sigs = core.signals(full, AllState())
    assert len(sigs) == 2
    rs = np.random.RandomState(3)
    for s in sigs:
        d0 = s["d0"]
        trunc = build(closes[:d0 + 1], {k: v for k, v in over.items() if k <= d0})
        t = [x for x in core.signals(trunc, AllState()) if x["d0"] == d0]
        assert len(t) == 1
        for key in ("entry", "stop", "risk", "w"):
            assert abs(t[0][key] - s[key]) < 1e-12
        # scramble every bar after the entry-day bar: the signal is unchanged
        c2 = closes.copy()
        c2[d0 + 1:] *= rs.uniform(0.3, 3.0, len(c2) - d0 - 1)
        o2 = {k: v for k, v in over.items() if k <= d0}
        alt = build(c2, o2)
        a = [x for x in core.signals(alt, AllState()) if x["d0"] == d0]
        assert len(a) == 1 and abs(a[0]["stop"] - s["stop"]) < 1e-12


def test_entry_is_next_monday_open_not_signal_close():
    closes, over = planted((60,))
    c = build(closes, over)
    s = core.signals(c, AllState())[0]
    assert s["entry"] == c.o[s["d0"]] and s["d0"] % 7 == 0 and s["d0"] == 7 * (s["w"] + 1)
    assert s["signal_ms"] == c.ms[s["d0"] - 1]


# ------------------------------------------------------------------ rules: gate, cooldown, DD20, stop floor
def test_btc_gate_blocks_bear():
    closes, over = planted((60,))
    c = build(closes, over)
    assert core.signals(c, AllState("BEAR")) == []
    assert len(core.signals(c, AllState("BASE"))) == 1


def test_smooth_cycle_needs_ten_consecutive_days():
    d = ["d%02d" % i for i in range(30)]
    raw = ["BULL"] * 5 + ["BEAR"] * 9 + ["BULL"] * 3 + ["BEAR"] * 10 + ["BULL"] * 3
    out = core.smooth_cycle(d, raw)
    assert out["d13"] == "BULL"                     # 9 BEAR days: prior state holds
    assert out["d17"] == "BULL"                     # interrupted run restarts
    assert out["d25"] == "BULL"                     # 9th BEAR day of the second run
    assert out["d26"] == "BEAR"                     # 10th consecutive day switches
    assert out["d27"] == "BEAR" and out["d29"] == "BEAR"   # 3 BULL days do not switch back


def test_cooldown_56_days_per_coin():
    closes, over = planted((60, 65, 70))               # entries 35 and 70 days apart... 60->65 = 35 d, 60->70 = 70 d
    c = build(closes, over)
    ws = [s["w"] for s in core.signals(c, AllState())]
    assert ws == [60, 70]


def test_dd20_exclusion_skips_signal():
    closes, over = planted((60,))
    c = build(closes, over)
    assert len(core.signals(c, AllState())) == 1
    c.dd20[60] = True
    assert core.signals(c, AllState()) == []
    cl = uptrend()
    cl[7 * 40 + 6:] *= 0.7                              # 30% drop at week 40's close
    k = build(cl)
    assert k.dd20[40] and not k.dd20[30]


def test_stop_floor_is_one_and_half_percent():
    closes = uptrend()
    over = dip(closes, 60, frac=0.9999)                  # week low barely under... low > EMA21 so no touch: force through ema
    c = build(closes, over)
    c.touch[60] = True                                   # force a signal with a low very close to the entry
    s = core.signals(c, AllState())[0]
    assert abs(s["risk"] - 0.015) < 1e-9 or s["risk"] > 0.015
    assert s["stop"] <= s["entry"] * (1 - 0.015) + 1e-12


# ------------------------------------------------------------------ simulator
def _cap_coin(over=None):
    closes = uptrend()
    return closes, build(closes, over or {})


def test_cap_exit_at_84_days_open():
    closes, c = _cap_coin()
    d0 = 7 * 60
    t = core.simulate(c, d0, 0.5)
    assert t["exit_reason"] == "CAP" and t["exit_i"] == d0 + 84 and t["exit_px"] == c.o[d0 + 84]
    assert abs(t["days"] - 84) < 1e-9


def test_trend_exit_next_monday_open_after_weekly_close_below_ema55():
    closes = uptrend()
    i = 7 * 61 + 6
    px = closes[i]
    over = {i: (closes[i - 1], closes[i - 1] * 1.001, 0.5 * px * 0.99, 0.5 * px)}
    c = build(closes, over)
    assert c.wc[61] < c.e55[61]
    t = core.simulate(c, 7 * 60, 0.95)
    assert t["exit_reason"] == "TREND" and t["exit_i"] == 7 * 62 and t["exit_px"] == c.o[7 * 62]


def test_stop_wins_ties_with_trend_exit_same_bar():
    closes = uptrend()
    d0 = 7 * 60
    entry = closes[d0 - 1]
    risk = 0.05
    stop = entry * (1 - risk)
    i = 7 * 60 + 6
    over = {i: (closes[i - 1], closes[i - 1], stop, 0.2 * entry)}     # low == stop exactly, close far below EMA55
    c = build(closes, over)
    assert c.wc[60] < c.e55[60]
    t = core.simulate(c, d0, risk)
    assert t["exit_reason"] == "STOP" and t["exit_i"] == i
    assert abs(t["exit_px"] - c.o[d0] * (1 - risk)) < 1e-9


def test_stop_gap_fills_at_open():
    closes = uptrend()
    d0 = 7 * 60
    j = d0 + 2
    entry = closes[d0 - 1]
    over = {j: (0.5 * entry, 0.5 * entry, 0.4 * entry, 0.45 * entry)}
    c = build(closes, over)
    t = core.simulate(c, d0, 0.1)
    assert t["exit_reason"] == "STOP-GAP" and t["exit_px"] == 0.5 * entry and t["exit_i"] == j


def test_fee_arithmetic_on_a_known_stop_trade():
    closes = uptrend()
    d0 = 7 * 60
    entry = closes[d0 - 1]
    risk = 0.10
    stop = entry * (1 - risk)
    j = d0 + 3
    over = {j: (closes[j - 1], closes[j - 1], stop * 0.99, stop * 0.995)}
    c = build(closes, over)
    t = core.simulate(c, d0, risk)
    gross = (entry * (1 - risk)) / entry - 1.0
    assert t["exit_reason"] == "STOP"
    assert abs(t["gross"] - gross) < 1e-12 and abs(gross + 0.10) < 1e-12
    assert abs(t["fee"] - 0.0012) < 1e-15
    assert abs(t["net"] - (-0.10 - 0.0012)) < 1e-12           # no funding cache: zero, flagged not covered
    assert not t["funding_covered"] and t["funding"] == 0.0
    assert abs(t["net_R"] - (-0.1012 / 0.10)) < 1e-9 and abs(t["fee_R"] - 0.012) < 1e-12
    assert abs(t["gross_R"] + 1.0) < 1e-9


def test_funding_real_window_and_not_in_data():
    closes, c = _cap_coin()
    d0 = 7 * 60
    t0 = int(c.ms[d0])
    ts = np.arange(t0 - 10 * 8 * 3600 * 1000, t0 + 90 * DAY, 8 * 3600 * 1000)
    f = core.Funding(ts, np.full(len(ts), 0.0001))
    t = core.simulate(c, d0, 0.5, f)
    assert t["funding_covered"] and abs(t["funding"] - 252 * 0.0001) < 1e-12     # print at entry excluded, at exit included
    assert abs(t["net"] - (t["gross"] - 0.0012 - 252 * 0.0001)) < 1e-12
    short = core.Funding(ts[ts < t0 + 40 * DAY], np.full(int((ts < t0 + 40 * DAY).sum()), 0.0001))
    u = core.simulate(c, d0, 0.5, short)
    assert not u["funding_covered"] and u["funding"] == 0.0 and u["net_flat"] < u["net"]


def test_unresolved_trade_excluded_on_live_coin_flagged_ended_on_dead_coin():
    closes = uptrend(7 * 63)
    live = build(closes)
    assert core.simulate(live, 7 * 60, 0.5) is None
    dead = build(closes, ended=True)
    t = core.simulate(dead, 7 * 60, 0.5)
    assert t["exit_reason"] == "ENDED" and t["ended"] and t["exit_px"] == dead.c[-1]


def test_planted_edge_trades_are_net_positive():
    closes, over = planted((60, 70))
    c = build(closes, over)
    trades = [core.trade_from_signal(c, s) for s in core.signals(c, AllState())]
    trades = [t for t in trades if t]
    assert trades and all(t["gross"] > 0 and t["net_R"] > 0 for t in trades)


# ------------------------------------------------------------------ stats
def mk(R, week, coin="A", split="VAL", year="2024", n=0):
    ms = (epoch_day(2024, 1, 1) + 7 * week) * DAY
    return dict(coin=coin, split=split, entry_year=year, net_R=R, gross_R=R + 0.01, fee_R=0.01, net=R * 0.1, gross=R * 0.1 + 0.001,
                iso_week="W%03d" % week, entry_ts=ms, days=20.0, ended=False, funding_covered=True, net_flat_R=R,
                exit_reason="TREND", btc_state="BULL")


def test_planted_edge_detected_by_block_bootstrap():
    rs = np.random.RandomState(1)
    rows = [mk(1.0 + rs.normal(0, 1.0), w) for w in range(60) for _ in range(2)]
    b = st.block_bootstrap(rows)
    assert b["ci_low"] > 0 and b["mean"] > 0.5 and b["weeks"] == 60 and b["W"] == 60


def test_no_edge_reads_about_zero():
    rs = np.random.RandomState(2)
    rows = [mk(rs.normal(0, 1.0), w) for w in range(120) for _ in range(3)]
    b = st.block_bootstrap(rows)
    assert abs(b["mean"]) < 0.15 and b["ci_low"] < 0 < b["ci_high"]


def test_bootstrap_counts_empty_calendar_weeks():
    rows = [mk(1.0, 0), mk(1.0, 9)]
    assert st.block_bootstrap(rows)["W"] == 10


def test_bootstrap_deterministic_seed_1114():
    rows = [mk(float(w % 3) - 0.5, w) for w in range(40)]
    assert st.block_bootstrap(rows) == st.block_bootstrap(rows)
    assert st.SEED == 1114 and st.NBOOT == 2000 and st.NDRAW == 1000 and st.BLOCK == 4


def test_placebo_real_above_candidates_vs_equal():
    rs = np.random.RandomState(4)
    real = [1.5] * 40
    cands = [rs.normal(0.0, 0.5, 8) for _ in real]
    p = st.placebo_draw(real, cands)
    assert p["real_mean"] >= p["p975"] and p["excess"] > 1.0 and p["n"] == 40
    same = [rs.normal(0.0, 1.0, 8) for _ in range(40)]
    q = st.placebo_draw([float(np.mean(c)) for c in same], same)
    assert q["real_mean"] < q["p975"]
    assert st.placebo_draw([1.0], [[]])["n"] == 0 and st.placebo_draw([1.0], [[]])["skipped"] == 1


def test_ex_best_weeks_and_top_coin_and_loyo_and_in_position():
    rows = [mk(0.1, w, coin="A") for w in range(10)] + [mk(50.0, 20, coin="B"), mk(40.0, 21, coin="C")]
    e = st.ex_best_weeks(rows, 2)
    assert e["n"] == 10 and abs(e["mean"] - 0.1) < 1e-12
    t = st.top_coin_removal(rows, 3)
    assert [x["removed"][-1] for x in t] == ["B", "C", "A"] and abs(t[1]["mean"] - 0.1) < 1e-12 and t[2]["n"] == 0
    r2 = [dict(mk(1.0, w), entry_year="2024") for w in range(5)] + [dict(mk(-2.0, w + 5), entry_year="2025") for w in range(5)]
    L = st.leave_one_year_out(r2)
    assert not L["all_positive"] and L["by_year"]["2025"]["mean"] == 1.0 and L["by_year"]["2024"]["mean"] == -2.0
    assert abs(st.in_position_daily([dict(net=0.2, days=10.0), dict(net=0.1, days=20.0)]) - 0.01) < 1e-12
    assert len(st.capped([mk(9.0, 0)])) == 1 and st.capped([mk(9.0, 0)])[0]["net_R"] == 3.0


def test_verdict_underpowered_is_never_fail():
    rows = [mk(1.0, w) for w in range(5)]
    S = st.run_stats(rows, {}, {"VAL": 0.0, "DEV": 0.0})
    assert S["verdict"] == "UNDERPOWERED" and S["kill_fired"] == [] and not S["bars"]["1"]


def test_verdict_pass_and_fail_paths():
    rs = np.random.RandomState(7)
    val, dev = [], []
    for y, base in (("2024", 0), ("2025", 60), ("2026", 120)):
        for w in range(25):
            for _ in range(2):
                val.append(dict(mk(1.0 + rs.normal(0, 0.5), base + w, coin="C%d" % rs.randint(0, 12), year=y), split="VAL"))
    for w in range(40):
        dev.append(dict(mk(0.8, w, split="DEV", year="2021"), split="DEV"))
    rows = val + dev
    pin = {"VAL": {"win": [(r["net_R"], rs.normal(0.0, 0.3, 6)) for r in val], "glob": []}}
    S = st.run_stats(rows, pin, {"VAL": 0.0001, "DEV": 0.0001})
    S2 = dict(S)
    assert S["bars"]["1"] and S["bars"]["2"] and S["bars"]["3"] and S["bars"]["4"] and S["bars"]["5"]
    # in-position daily: net 0.1*R per 20 days -> 0.005 per day, above 0.0001
    assert S["bars"]["6"] and S["bars"]["7"] and S["bars"]["8"] and S["verdict"] == "PASS"
    bad = st.run_stats(rows, pin, {"VAL": 0.5, "DEV": 0.5})
    assert bad["verdict"].startswith("FAIL") and "KILL" in bad["verdict"] and not bad["bars"]["6"]
    assert S2["holm_p_family_worst"] >= S2["holm_p_study"]
