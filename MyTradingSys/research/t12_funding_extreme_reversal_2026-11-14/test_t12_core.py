"""Synthetic-bar tests for T12 (core + stats). No data cache. Run: python -m pytest test_t12_core.py"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t12_core as core  # noqa: E402
import t12_stats as st  # noqa: E402

DAY = 86400000
H8 = 8 * 3600 * 1000


def eday(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


START = eday(2022, 3, 7)        # a Monday
assert (START + 3) % 7 == 0


def bars(closes, start=START, r=0.005, over=None, skip=()):
    """Daily rows [ts, o, h, l, c]: open = previous close, range +-r around the body; over = {i: (o,h,l,c)}."""
    over = over or {}
    out = []
    for i, c in enumerate(closes):
        if i in skip:
            continue
        o = closes[i - 1] if i else c
        row = over.get(i, (o, max(o, c) * (1 + r), min(o, c) * (1 - r), c))
        out.append(((start + i) * DAY,) + tuple(row))
    return np.array(out, float)


def mkcoin(closes, name="SYN", ended=False, **kw):
    rows = bars(closes, **kw)
    end = int(rows[-1, 0]) + (0 if not ended else 0)
    c = core.Coin(name, rows, data_end_ms=end + (400 * DAY if ended else 0))
    return c


def mkfund(daily, start=START, n_days=None, per_day=3, drop_days=()):
    """daily: array of per-print rate by day (len = days); 3 prints/day at 00:00, 08:00, 16:00 UTC."""
    ts, rate = [], []
    for k, v in enumerate(daily):
        if k in drop_days:
            continue
        for q in range(per_day):
            ts.append((start + k) * DAY + q * H8 + (37 if q == 1 else 0))   # sub-second jitter: rounded away
            rate.append(v)
    return core.Funding(ts, rate)


def walk(n, seed=3, sd=0.01, p0=100.0):
    rs = np.random.RandomState(seed)
    return p0 * np.exp(np.cumsum(rs.normal(0, sd, n)))


def base_funding(n, seed=5, mu=0.00003, sd=0.00001):
    rs = np.random.RandomState(seed)
    return rs.normal(mu, sd, n)


# ---------------------------------------------------------------- fee arithmetic
def test_fee_is_12bp_from_fees_py():
    import fees
    assert abs(core.FEE_RT - 0.0012) < 1e-12                   # hand number
    assert core.FEE_RT == 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13


def _flat_plan(side, over=None, n=300, fund_rate=0.0):
    closes = [100.0] * n
    c = mkcoin(closes, over=over, r=0.0)
    f = mkfund(np.full(n + 30, fund_rate))
    i = 280
    p, why = core.plan_trade(c, f, i, side, stop_pct=0.10)
    assert why is None, why
    return c, f, p


def test_fee_arithmetic_flat_trade():
    c, f, p = _flat_plan(+1)
    r = core.simulate_plan(c, f, p)
    assert abs(r["gross"]) < 1e-12 and r["reason"] == "TIME" and r["days"] == 10
    assert abs(r["netp"] - (-0.0012)) < 1e-12
    assert abs(r["fee_R"] - 0.0012 / 0.10) < 1e-12              # fee in R = 12bp / stop%
    assert abs(r["netp_R"] - (-0.012)) < 1e-12


# ---------------------------------------------------------------- funding sign and carry
def test_funding_sign_long_pays_short_receives():
    c, f, pl = _flat_plan(+1, fund_rate=0.0002)
    _, _, ps = _flat_plan(-1, fund_rate=0.0002)
    rl, rs_ = core.simulate_plan(c, f, pl), core.simulate_plan(c, f, ps)
    assert rl["fund"] > 0 and rs_["fund"] < 0
    assert abs(rl["fund"] + rs_["fund"]) < 1e-15
    assert abs(rl["fund"] - 30 * 0.0002) < 1e-12                # 10 days x 3 prints, hand number
    assert abs(rl["nett"] - (rl["netp"] - 0.006)) < 1e-12


def test_no_funding_means_no_trade_and_no_imputation():
    n = 300
    c = mkcoin([100.0] * n, r=0.0)
    f = mkfund(np.full(n, 0.0001), drop_days={285})            # a missing day inside the hold window
    p, why = core.plan_trade(c, f, 280, +1, stop_pct=0.1)
    assert p is None and why == "no_funding"
    p, why = core.plan_trade(c, None, 280, +1, stop_pct=0.1)
    assert p is None and why == "no_funding"


# ---------------------------------------------------------------- stop wins ties and gaps
def test_stop_wins_tie_long():
    over = {282: (100.0, 130.0, 85.0, 120.0)}                   # touches the 10% stop (90) AND closes far above entry
    c, f, p = _flat_plan(+1, over=over)
    r = core.simulate_plan(c, f, p)
    assert r["reason"] == "STOP" and abs(r["exit_px"] - 90.0) < 1e-9
    assert abs(r["gross_R"] - (-1.0)) < 1e-9


def test_stop_wins_tie_short():
    over = {282: (100.0, 115.0, 70.0, 80.0)}
    c, f, p = _flat_plan(-1, over=over)
    r = core.simulate_plan(c, f, p)
    assert r["reason"] == "STOP" and abs(r["exit_px"] - 110.0) < 1e-9
    assert abs(r["gross_R"] - (-1.0)) < 1e-9


def test_stop_gap_fills_at_open():
    over = {283: (80.0, 92.0, 78.0, 88.0)}                      # opens below the 90 stop: fills at the open
    c, f, p = _flat_plan(+1, over=over)
    r = core.simulate_plan(c, f, p)
    assert r["reason"] == "STOP-GAP" and abs(r["exit_px"] - 80.0) < 1e-9 and abs(r["gross_R"] - (-2.0)) < 1e-9


def test_stop_checked_on_entry_bar():
    over = {281: (100.0, 101.0, 89.0, 100.0)}                   # entry-day low pierces the stop
    c, f, p = _flat_plan(+1, over=over)
    r = core.simulate_plan(c, f, p)
    assert r["reason"] == "STOP" and r["exit_i"] == p["j"]


def test_stop_on_exit_day_beats_close():
    n = 300
    j = 281
    over = {j + 9: (100.0, 101.0, 89.0, 100.5)}                 # exit-day low pierces the stop, close is fine
    c, f, p = _flat_plan(+1, over=over)
    r = core.simulate_plan(c, f, p)
    assert r["reason"] == "STOP" and r["exit_i"] == j + 9


# ---------------------------------------------------------------- entry timing and look-ahead
def test_entry_is_next_bar_open():
    closes = list(walk(320))
    c = mkcoin(closes)
    f = mkfund(base_funding(350))
    p, _ = core.plan_trade(c, f, 290, +1)
    assert p["entry"] == c.o[291] and p["entry_ms"] == c.ms[291] and p["j"] == 291


def _planted(n=400, i_sig=330, side=+1):
    """Walk with a funding extreme spell and a reversal bar at i_sig (long cell: negative funding)."""
    closes = list(walk(n, seed=11))
    mu = -0.00012 if side > 0 else 0.00012
    daily = base_funding(n + 30)
    daily[i_sig - 2:i_sig + 1] = mu
    over = {}
    prev_h = closes[i_sig - 1] * 1.005
    if side > 0:
        over[i_sig] = (closes[i_sig - 1] * 0.99, closes[i_sig - 1] * 1.05, closes[i_sig - 1] * 0.985, prev_h * 1.02)
    else:
        pl = closes[i_sig - 1] * 0.995
        over[i_sig] = (closes[i_sig - 1] * 1.01, closes[i_sig - 1] * 1.012, closes[i_sig - 1] * 0.94, pl * 0.98)
    closes[i_sig] = over[i_sig][3]
    return closes, daily, over


class _Ph:
    def __init__(self, lab):
        self.lab = lab

    def label(self, day):
        return self.lab


def test_signal_fires_on_planted_extreme_and_reversal_both_cells():
    for cell, side, lab in (("A", +1, "MARKDOWN"), ("B", -1, "DISTRIBUTION")):
        closes, daily, over = _planted(side=side)
        c = mkcoin(closes, over=over)
        f = mkfund(daily)
        sigs = core.signals(c, f, _Ph(lab), cell)
        assert [s["i"] for s in sigs] == [330], (cell, [s["i"] for s in sigs])


def test_phase_gate_blocks_wrong_label():
    closes, daily, over = _planted(side=+1)
    c = mkcoin(closes, over=over)
    f = mkfund(daily)
    assert core.signals(c, f, _Ph("MARKUP"), "A") == []
    assert core.signals(c, f, _Ph("MARKDOWN"), "B") == []


def test_signal_uses_only_bars_through_signal_bar():
    closes, daily, over = _planted(side=+1)
    c = mkcoin(closes, over=over)
    f = mkfund(daily)
    full = [s["i"] for s in core.signals(c, f, _Ph("MARKDOWN"), "A")]
    assert 330 in full
    trunc_rows = bars(closes, over=over)[:331]                  # bars through the signal bar only
    ct = core.Coin("SYN", trunc_rows, data_end_ms=int(trunc_rows[-1, 0]))
    ft = mkfund(daily[:331])                                   # funding through the signal day only
    part = [s["i"] for s in core.signals(ct, ft, _Ph("MARKDOWN"), "A")]
    assert [i for i in full if i <= 330] == part
    # scramble everything after the signal bar: the signal at 330 is unchanged
    rs = np.random.RandomState(9)
    c2 = list(closes)
    for k in range(331, len(c2)):
        c2[k] = c2[k] * float(np.exp(rs.normal(0, 0.3)))
    d2 = daily.copy()
    d2[331:] = rs.normal(0, 0.01, len(d2) - 331)
    cc = mkcoin(c2, over=over)
    ff = mkfund(d2)
    assert 330 in [s["i"] for s in core.signals(cc, ff, _Ph("MARKDOWN"), "A")]


def test_percentile_window_ends_day_before_signal():
    n = 400
    daily = base_funding(n)
    f = mkfund(daily)
    day = START + 330
    w = f.window(day)
    k = day - f.d0
    assert len(w) == core.PWIN
    assert np.allclose(w, f.f3[k - 180:k], equal_nan=True)     # day itself excluded
    daily2 = daily.copy()
    daily2[328:331] = -0.001                                   # an extreme exactly at the signal days
    f2 = mkfund(daily2)
    assert core.extreme_flag(f2, day, +1) and not core.extreme_flag(f, day, +1)
    # the spike contaminates windows of LATER days only; the window of `day` is unchanged
    assert np.allclose(f2.window(day)[:-2], f.window(day)[:-2], equal_nan=True)


def test_floor_blocks_small_negative_funding():
    n = 400
    daily = np.full(n, 0.00002)
    daily[328:331] = -0.00005                                   # lowest of the window but above -0.01%
    f = mkfund(daily)
    assert not core.extreme_flag(f, START + 330, +1)
    daily[328:331] = -0.00015
    assert core.extreme_flag(mkfund(daily), START + 330, +1)


def test_f3_is_mean_of_8h_prints_over_3_days():
    f = mkfund([0.0001, 0.0002, 0.0006] + [0.0] * 5)
    assert abs(f.f3_at(START + 2) - 0.0003) < 1e-12            # (1+2+6)/3 e-4
    assert np.isnan(f.f3_at(START + 1))


def test_cooldown_blocks_second_signal_within_10_days():
    n = 420
    closes = list(walk(n, seed=21))
    daily = base_funding(n + 30)
    over = {}
    for s in (330, 335, 345):
        daily[s - 2:s + 1] = -0.00012
        pc = closes[s - 1]
        over[s] = (pc * 0.99, pc * 1.06, pc * 0.985, pc * 1.04)
        closes[s] = over[s][3]
        closes[s + 1:] = [x for x in closes[s + 1:]]
    c = mkcoin(closes, over=over)
    f = mkfund(daily)
    # make closes[s] follow the over rows (mkcoin uses over); previous high requirement satisfied by pc*1.06 > prev high
    got = [s["i"] for s in core.signals(c, f, _Ph("MARKDOWN"), "A")]
    assert got[0] == 330 and 335 not in got and 345 in got


# ---------------------------------------------------------------- segments, ended, alive
def test_hole_splits_segments_and_blocks_spanning_trade():
    n = 340
    closes = list(walk(n, seed=2))
    c = mkcoin(closes, skip={300, 301, 302})
    assert c.seg_start[-1] > 0
    f = mkfund(base_funding(n + 30))
    i_before = int(np.where(c.ms == (START + 299) * DAY)[0][0])
    p, why = core.plan_trade(c, f, i_before, +1)
    assert p is None and why in ("no_entry_bar", "window_past_segment")
    p, why = core.plan_trade(c, f, i_before - 20, +1)          # window ends before the hole: allowed
    assert why is None


def test_alive_needs_260_bars_after_a_hole():
    n = 340
    c = mkcoin(list(walk(n, seed=4)), skip={150})
    f = mkfund(np.full(n + 30, -0.0004))
    flags = core.day_flags(c, f, _Ph("MARKDOWN"), "A")
    assert all(r["i"] - c.seg_start[r["i"]] >= 259 for r in flags)


def test_ended_coin_exits_at_last_bar_active_coin_is_skipped():
    n = 290
    closes = [100.0] * n
    f = mkfund(np.full(n + 30, 0.0))
    ce = mkcoin(closes, ended=True, r=0.0)
    p, why = core.plan_trade(ce, f, 285, +1, stop_pct=0.1)
    assert why is None and p["ended"] and p["x"] == n - 1
    ca = mkcoin(closes, ended=False, r=0.0)
    p, why = core.plan_trade(ca, f, 285, +1, stop_pct=0.1)
    assert p is None and why == "window_past_segment"


def test_alive_counts():
    cs = [mkcoin(list(walk(300, seed=s)), name="C%d" % s) for s in range(5)]
    cnt = core.alive_counts(cs)
    assert max(cnt.values()) == 5 and min(cnt.values()) >= 1
    assert min(cnt) == START + 259                              # first alive day = 260th bar


def test_alive_below_30_excludes_signal():
    closes, daily, over = _planted(side=+1)
    c = mkcoin(closes, over=over)
    f = mkfund(daily)
    assert core.signals(c, f, _Ph("MARKDOWN"), "A", alive=core.alive_counts([c])) == []
    big = {d: 40 for d in range(START, START + 500)}
    assert len(core.signals(c, f, _Ph("MARKDOWN"), "A", alive=big)) == 1


# ---------------------------------------------------------------- weeks (ISO) and cycle smoothing
def test_sunday_belongs_to_previous_monday_week_not_next():
    mon = START
    assert core.iso_week_idx(mon) == core.iso_week_idx(mon + 6)
    assert core.iso_week_idx(mon + 7) == core.iso_week_idx(mon) + 1
    for d in range(mon, mon + 21):
        a = dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).isocalendar()
        b = dt.datetime.fromtimestamp(core.iso_week_idx(d) * 7 * 86400 - 3 * 86400, dt.timezone.utc).isocalendar()
        assert (a[0], a[1]) == (b[0], b[1])


def test_cycle_smoothing_needs_10_consecutive_days():
    raw = ["BEAR"] * 20 + ["BULL"] * 9 + ["BEAR"] * 5 + ["BULL"] * 10 + ["BASE"] * 3
    sm = core.smooth_cycle(raw)
    assert sm[20 + 8] == "BEAR" and sm[-1 - 3 - 0] == "BULL"
    assert sm[20 + 9 + 5 + 8] == "BEAR" and sm[20 + 9 + 5 + 9] == "BULL"
    assert sm[-1] == "BULL"                                     # 3 days of BASE is not enough


def test_reversal_bar_definitions():
    n = 300
    closes = list(walk(n, seed=8))
    f = mkfund(np.full(n + 30, -0.0004))
    i = 290
    pc = closes[i - 1]
    prev_h = float(bars(closes)[i - 1, 2])
    over = {i: (pc, prev_h * 1.1, pc * 0.99, prev_h * 1.01)}   # green, closes above prior high
    c = mkcoin(closes[:i] + [over[i][3]] + closes[i + 1:], over=over)
    rr = {r["i"]: r["rev"] for r in core.day_flags(c, f, _Ph("MARKDOWN"), "A")}
    assert rr[i] is True
    over = {i: (pc, prev_h * 1.1, pc * 0.99, prev_h * 0.999)}  # green but not above prior high
    c = mkcoin(closes[:i] + [over[i][3]] + closes[i + 1:], over=over)
    rr = {r["i"]: r["rev"] for r in core.day_flags(c, f, _Ph("MARKDOWN"), "A")}
    assert rr[i] is False


# ---------------------------------------------------------------- statistics: planted edge, no edge, null placebo
def _rows(n_weeks, mean_r, sd=1.0, per_week=2, seed=1):
    rs = np.random.RandomState(seed)
    out = []
    for w in range(n_weeks):
        for k in range(per_week):
            v = mean_r + rs.normal(0, sd)
            out.append(dict(coin="C%d" % (k % 5), week=3000 + w, year=2024 + (w // 52), cycle="BEAR", netp_R=v,
                            nett_R=v, netp=v / 10, nett=v / 10, days=10, split="VAL"))
    return out


def test_planted_edge_detected():
    rows = _rows(150, 0.5)
    b = st.block_bootstrap(rows)
    assert b["mean"] > 0.3 and b["ci_low"] > 0 and b["p_le0"] < 0.05


def test_no_edge_reads_about_zero():
    rows = _rows(150, 0.0, seed=7)
    b = st.block_bootstrap(rows)
    assert abs(b["mean"]) < 0.2 and b["ci_low"] < 0 < b["ci_high"]


def test_bootstrap_is_seeded_and_week_clustered():
    rows = _rows(60, 0.2)
    assert st.block_bootstrap(rows) == st.block_bootstrap(rows)
    # one huge week must widen the CI relative to the same total spread over many weeks
    one = _rows(60, 0.0, per_week=1)
    for r in one[:1]:
        r["netp_R"] = 40.0
    assert st.block_bootstrap(one)["ci_high"] > 0.2


def test_placebo_detects_planted_and_null_is_not_flagged():
    rs = np.random.RandomState(3)
    pairs = [(1.0 + rs.normal(0, 0.1), rs.normal(0, 1.0, 40)) for _ in range(120)]
    pl = st.placebo(pairs)
    assert pl["excess"] > 0.5 and pl["real_mean"] >= pl["p975"]
    hits = 0
    for sd in range(20):
        rs = np.random.RandomState(100 + sd)
        pairs = [(rs.normal(0, 1.0), rs.normal(0, 1.0, 40)) for _ in range(120)]
        p = st.placebo(pairs, seed=1114 + sd)
        hits += int(p["real_mean"] >= p["p975"])
    assert hits <= 3                                           # ~5% false positive rate, loose bound


def test_placebo_skips_trades_without_candidates():
    pl = st.placebo([(1.0, np.array([])), (2.0, np.array([0.0, 0.0]))])
    assert pl["n"] == 1 and pl["skipped"] == 1 and pl["real_mean"] == 2.0


def test_ex_best_weeks_and_top_coin_removal_and_loyo():
    rows = _rows(40, 0.0, per_week=5)
    rows[0]["netp_R"] = 50.0
    assert st.mean([r["netp_R"] for r in rows]) > 0.2
    assert abs(st.ex_best_weeks(rows, k=1)["mean"]) < 0.2
    tr = st.top_coin_removal(rows, k=3)
    assert len(tr) == 3 and tr[0]["removed"][0] == rows[0]["coin"]
    assert set(st.leave_one_year_out(rows)) == {2024}


def test_holm():
    a = st.holm({"A": 0.01, "B": 0.03})
    assert abs(a["A"] - 0.02) < 1e-12 and abs(a["B"] - 0.03) < 1e-12


def test_underpowered_is_never_fail():
    rows = _rows(5, -3.0)                                       # clearly negative but tiny
    b = st.block_bootstrap(rows)
    v, bars = st.verdict("A", rows, rows, b, b, dict(n=0), dict(ok=False), dict(mean=-1), [], {}, False)
    assert v == "UNDERPOWERED" and bars == {1: False}


def test_verdict_pass_carry_only_and_fail():
    val = _rows(120, 0.6, per_week=5, seed=4)
    dev = _rows(60, 0.3, seed=5)
    bp = st.block_bootstrap(val)
    pl = dict(n=100, real_mean=bp["mean"], p975=bp["mean"] - 0.1, excess=0.3)
    ex5 = st.ex_best_weeks(val, 5)
    top3 = st.top_coin_removal(val, 3)
    loyo = st.leave_one_year_out(val)
    v, bars = st.verdict("A", val, dev, bp, bp, pl, dict(ok=True), ex5, top3, loyo, False)
    assert v == "PASS" and all(bars[k] for k in range(1, 9))
    v, _ = st.verdict("A", val, dev, bp, bp, pl, dict(ok=True), ex5, top3, loyo, True)
    assert v == "SIGN-FLIP"
    neg = _rows(120, -0.0, per_week=5, seed=6)
    for r in neg:
        r["netp_R"] -= 0.4
    bn = st.block_bootstrap(neg)
    bt = dict(mean=0.4, ci_low=0.1, ci_high=0.7, p_le0=0.01)
    v, _ = st.verdict("A", neg, dev, bn, bt, pl, dict(ok=True), ex5, top3, loyo, False)
    assert v == "CARRY-ONLY"
    v, _ = st.verdict("A", neg, dev, bn, bn, pl, dict(ok=True), ex5, top3, loyo, False)
    assert v == "FAIL"


def test_sign_flip_helper():
    rows = _rows(40, 0.0, per_week=2)
    for r in rows:
        r["cycle"] = "BULL"
        r["netp_R"] = 0.5
    rows[0]["cycle"] = "BEAR"
    rows[0]["netp_R"] = -0.1
    flip, mo, ma = st.sign_flip(rows, "A")
    assert flip and mo > 0 and ma < 0
    assert not st.sign_flip(rows, "B")[0]
