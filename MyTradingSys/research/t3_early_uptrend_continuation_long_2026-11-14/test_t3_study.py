"""Unit tests for t3_study.py. SYNTHETIC bars only: nothing here reads F:\\MTS\\data_cache or anything under scripts/sched.

Mutation check (each test must fail on a deliberately broken version at least once). Done 2026-11-14: t3_study.py copied to a scratch
folder, ONE edit applied, this file run there (FAILED = the test caught the break; all six mutants were caught, 5 passed + 1 failed or
4 passed + 2 failed in each run):
  lookahead  STUDY_BUG=1 (centred volume median + same-day phase key)           -> test_no_lookahead_signal_and_phase FAILED
  stop_tie   hit_s = (lj <= st) & (hj < tgt[alive])  (target wins a tie)         -> test_stop_wins_tie_and_gap_fill FAILED
  fund       _rows(): fund = s.cf[xi] - s.cf[e]  (funding window one day short)  -> test_fee_and_funding_hand_number FAILED
  cost       COST12 = 2 * fees.BINANCE_TAKER  (slippage dropped)                 -> test_cost_is_imported_12bp + hand number FAILED
  planted    trade-row net_R computed from -ret (sign broken)                    -> test_planted_edge_found_and_null_reads_zero FAILED
  greedy     if i > nxt  (signal on the exit bar blocked)                        -> test_onset_and_no_overlap FAILED
The exact edits are in test_notes below.
Round 2 (2026-11-14, audit M2): 27 one-line mutants, ALL caught: entry at signal-bar open, RIDE signal exit at close, time exits 59/61 and
30 -> 29/31, weekly VWAP off by a day, HM "|" for "&", VWAP leg / DI+>DI- leg / 250-bar warm-up removed, basket label shift, DEV end widened,
BH without monotone step, ex_best dropping the worst, volume median incl. current bar, bootstrap p with "<" for "<=", DELIST off / forced
exit at open / ended flag always or never true, plus the six above.
"""
import os
import sys
import datetime as dt
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import t3_study as S  # noqa: E402

S.BRAIN_CSV = os.path.join(HERE, "__no_such_brain__.csv")      # tests never read the real brain table
DAY = S.DAY
test_notes = {
    "lookahead": "STUDY_BUG=1",
    "stop_tie": "simulate(): hit_s = (lj <= st) & (hj < tgt[alive])",
    "fund": "_rows(): fund = s.cf[xi] - s.cf[e]",
    "cost": "COST12 = 2 * fees.BINANCE_TAKER",
    "planted": "_rows(): net_R=(-ret - COST12 - fund) / risk",
    "greedy": "greedy(): if i > nxt",
}


def ts_from(y, m, d, n):
    t0 = int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)
    return t0 + DAY * np.arange(n)


def synth_btc():
    """Steady exponential rise 2019-01-01..2021-12-31: UP all along after the SMA200 exists; UP_E after 2020-05-11 (<540 days)."""
    n = 1095
    ts = ts_from(2019, 1, 1, n)
    c = 4000 * np.exp(0.0012 * np.arange(n))
    return {"ts": ts, "c": c}


def make_seg(ts, o, h, l, c, v, fund=None, name="X"):
    s = S.Seg()
    s.sym = s.name = name
    s.ts, s.o, s.h, s.l, s.c, s.v = ts, o, h, l, c, v
    s.tbv = v * 0.5
    s.fund = fund
    return s


def flat_bars(n=500, start=(2019, 10, 1)):
    ts = ts_from(*start, n)
    o = np.full(n, 100.0)
    h = np.full(n, 102.0)
    l = np.full(n, 98.0)
    c = np.full(n, 100.0)
    v = np.full(n, 1000.0)
    return ts, o, h, l, c, v


def rw_seg(rng, n, drift_after=None, start=(2019, 10, 1), name="X"):
    """Random-walk coin. drift_after: bool signal-bar array; +2% extra return on the 10 bars after every True (planted edge)."""
    ts = ts_from(*start, n)
    r = rng.normal(0.0, 0.03, n)
    if drift_after is not None:
        for i in np.flatnonzero(drift_after):
            r[i + 1:i + 11] += 0.02
    c = 100 * np.exp(np.cumsum(r))
    o = np.empty(n)
    o[0] = 100.0
    o[1:] = c[:-1]
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.01, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.01, n))
    return make_seg(ts, o, h, l, c, rng.uniform(500, 1500, n), name=name)


# ----------------------------------------------------------------------------- look-ahead
def test_no_lookahead_signal_and_phase():
    rng = np.random.default_rng(7)
    n = 420
    seg = rw_seg(rng, n)
    seg.v = rng.uniform(500, 1500, n)
    seg.v[rng.integers(40, n - 40, 25)] *= 6        # volume spikes so VOLX fires sometimes
    cut = 300
    base = S.coin_features(seg, bug=S.BUG)
    mut = make_seg(seg.ts.copy(), seg.o.copy(), seg.h.copy(), seg.l.copy(), seg.c.copy(), seg.v.copy())
    for a in ("o", "h", "l", "c", "v"):
        arr = getattr(mut, a)
        arr[cut + 1:] = arr[cut + 1:] * rng.uniform(0.2, 5.0, n - cut - 1)           # wreck every bar AFTER the signal bar
    mut.tbv = mut.v * 0.5
    alt = S.coin_features(mut, bug=S.BUG)
    for cell in ("A", "B"):
        assert np.array_equal(base[cell][:cut + 1], alt[cell][:cut + 1]), f"cell {cell} state at/before bar {cut} changed by later bars"
    # make sure the test has teeth: some state is actually true in the checked range
    assert base["A"][:cut + 1].sum() + base["B"][:cut + 1].sum() > 0
    # phase label: the label keyed to entry day D must not depend on any BTC close of day >= D
    btc = synth_btc()
    D = int(btc["ts"][700] // DAY)
    t1 = S.phase_labels(btc["ts"], btc["c"], bug=S.BUG)
    c2 = btc["c"].copy()
    c2[700:] = c2[700:] * np.linspace(0.05, 0.02, len(c2) - 700)         # crash from day D on (flips UP to DOWN)
    t2 = S.phase_labels(btc["ts"], c2, bug=S.BUG)
    l1 = S.phase_for_days(t1, np.array([D]))[0]
    l2 = S.phase_for_days(t2, np.array([D]))[0]
    assert l1 == 0 and l1 == l2, (l1, l2)


# ----------------------------------------------------------------------------- stop wins ties
def test_stop_wins_tie_and_gap_fill():
    ts, o, h, l, c, v = flat_bars(60)
    atr = S.atr_sma(h, l, c, 14)                      # = 4 -> S = max(2.5*4, 2%) = 10, stop 90, target 130
    e = 30
    h[e] = 140.0                                      # target 130 inside the entry bar ...
    l[e] = 85.0                                       # ... and so is the stop 90: stop must win
    sim = S.simulate(o, h, l, c, atr, "CAP3R")
    s = e - 1
    assert sim["reason"][s] == 1 and sim["px"][s] == pytest.approx(90.0) and sim["xi"][s] == e
    assert sim["S"][s] == pytest.approx(10.0)
    # gap through the stop: the next open is below the stop -> fill at the open (worse), not at the stop
    ts, o, h, l, c, v = flat_bars(60)
    o[e + 1], l[e + 1] = 85.0, 84.0                   # entry 100 -> stop 90; bar e+1 opens at 85
    sim = S.simulate(o, h, l, c, S.atr_sma(h, l, c, 14), "RIDE")
    assert sim["reason"][e - 1] == 1 and sim["px"][e - 1] == pytest.approx(85.0) and sim["xi"][e - 1] == e + 1
    # target alone (no stop) fills at the target, +3R
    ts, o, h, l, c, v = flat_bars(60)
    h[e] = 135.0
    sim = S.simulate(o, h, l, c, S.atr_sma(h, l, c, 14), "CAP3R")
    assert sim["reason"][e - 1] == 2 and sim["px"][e - 1] == pytest.approx(130.0)
    assert sim["ret"][e - 1] / sim["risk"][e - 1] == pytest.approx(3.0)


# ----------------------------------------------------------------------------- fee / funding hand number
def test_cost_is_imported_12bp():
    assert S.COST12 == pytest.approx(0.0012)          # hand number: 2 x 5 bp taker + 2 bp slippage
    assert S.COST6 == pytest.approx(0.0006)


def test_fee_and_funding_hand_number():
    ts, o, h, l, c, v = flat_bars(500)
    sidx = 260                                        # signal bar 2020-06-17 (>= 250th bar, entry day in UP_E)
    e = sidx + 1
    h[e + 1] = 131.0                                  # CAP3R target 130 hit on the bar after entry
    prints_ts = ts[0] + 8 * 3600000 * np.arange(3 * 520)
    fund = (prints_ts, np.full(len(prints_ts), 0.0001))
    seg = make_seg(ts, o, h, l, c, v, fund=fund)
    sig = np.zeros(500, bool)
    sig[sidx] = True
    w = S.build_world([seg], synth_btc(), bug=False, sig_override={"A": [sig], "B": [np.zeros(500, bool)]})
    df = S.trade_frame(w, "A", "CAP3R", [0])
    assert len(df) == 1
    t = df.iloc[0]
    # entry 100, S = 10 (ATR 4), exit 130 on bar e+1 -> gross 0.30, risk 0.10 -> gross R 3
    # funding: entry-open .. end of bar e+1 = 2 days = prints 08,16 (day e), 00,08,16 (day e+1), 00 (day e+2) = 6 x 1 bp = 0.0006
    assert t.gross_R == pytest.approx(3.0)
    assert t.funding == pytest.approx(0.0006)
    assert t.net_R == pytest.approx((0.30 - 0.0012 - 0.0006) / 0.10)      # = 2.982
    assert t.net_R6 == pytest.approx((0.30 - 0.0006 - 0.0006) / 0.10)
    assert not t.fund_flat
    # no funding file at all -> flat 3 bp/day for the 2 days, flagged
    seg2 = make_seg(ts, o, h, l, c, v, fund=None)
    w2 = S.build_world([seg2], synth_btc(), bug=False, sig_override={"A": [sig], "B": [np.zeros(500, bool)]})
    t2 = S.trade_frame(w2, "A", "CAP3R", [0]).iloc[0]
    assert t2.funding == pytest.approx(0.0006) and bool(t2.fund_flat)


# ----------------------------------------------------------------------------- onset + no overlap
def test_onset_and_no_overlap():
    st = np.array([0, 1, 1, 0, 1, 1, 1], bool)
    assert S.onset(st).tolist() == [False, True, False, False, True, False, False]
    # signals at bars 5, 8, 12 with exits at bars 8, 11, 20: bar 8 is allowed (>= exit bar 8), bar 12 is blocked by the trade 8..11? no: 12 >= 11
    assert S.greedy([5, 7, 8, 12], [8, 9, 11, 20]).tolist() == [5, 8, 12]
    assert S.greedy([5, 7, 9], [8, 9, 11]).tolist() == [5, 9]


# ----------------------------------------------------------------------------- planted edge vs null world
def _world(drift, seed):
    rng = np.random.default_rng(seed)
    n = 520
    segs, sigsA, sigsB = [], [], []
    for k in range(8):
        sig = (rng.uniform(size=n) < 0.04)
        sig[:260] = False
        sig[-70:] = False
        seg = rw_seg(rng, n, drift_after=sig if drift else None, name=f"C{k}")
        segs.append(seg)
        sigsA.append(sig)
        sigsB.append(np.zeros(n, bool))
    return S.build_world(segs, synth_btc(), bug=False, sig_override={"A": sigsA, "B": sigsB})


def test_planted_edge_found_and_null_reads_zero():
    wd = _world(True, 11)
    wn = _world(False, 11)
    rd = S.analyse_window(wd, "dev", draws=200)["cells"]["A"]["RIDE"]
    rn = S.analyse_window(wn, "dev", draws=200)["cells"]["A"]["RIDE"]
    assert rd["n"] >= 30 and rn["n"] >= 30
    assert rd["mean_net_R12"] > 1.0 and rd["ci_lo"] > 0           # planted +2%/day x 10 days is found
    assert rd["excess_ci_lo"] > 0                                 # and it beats random same-phase entries
    assert rn["ci_lo"] < 0 < rn["ci_hi"] or abs(rn["mean_net_R12"]) < 0.25   # no-drift world reads zero
    assert rn["excess_ci_lo"] < 0 < rn["excess_ci_hi"]
    assert rd["excess"] > rn["excess"] + 0.5


# ============================================================================= round 2 (audit fixes M1, M2): timing, cell B, stats vectors, DELIST
def _ref_rsi(c, n):
    """Plain-loop Wilder RSI with SMA seed (independent of study.rsi_wilder)."""
    out = [None] * len(c)
    gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, len(c))]
    losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, len(c))]
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n
    for i in range(n, len(c)):
        if i > n:
            ag = (ag * (n - 1) + gains[i - 1]) / n
            al = (al * (n - 1) + losses[i - 1]) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def _ref_cell_b(ts, h, l, c, v):
    r = _ref_rsi(list(c), 9)
    first = 9
    e3 = [None] * len(c)
    e3[first + 2] = sum(r[first:first + 3]) / 3
    for i in range(first + 3, len(c)):
        e3[i] = e3[i - 1] + (r[i] - e3[i - 1]) * 0.5
    w21 = [None] * len(c)
    for i in range(first + 20, len(c)):
        win = r[i - 20:i + 1]
        w21[i] = sum(x * (k + 1) for k, x in enumerate(win)) / 231.0
    out, pv, vv, wk_prev = [], 0.0, 0.0, None
    for i in range(len(c)):
        d = dt.datetime.fromtimestamp(ts[i] / 1000, dt.timezone.utc)
        wk = d.isocalendar()[:2]                                    # ISO weeks start on Monday
        if wk != wk_prev:
            pv = vv = 0.0
            wk_prev = wk
        pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        vv += v[i]
        vwap = pv / vv
        ok = w21[i] is not None and w21[i] < r[i] and w21[i] < e3[i] and c[i] > vwap
        out.append(bool(ok))
    return out


def test_entry_at_next_open_and_exit_fill_prices():
    ts, o, h, l, c, v = flat_bars(80)
    atr = S.atr_sma(h, l, c, 14)                       # 4 -> S = max(10, 2% of entry) = 10 for entry 100
    sg = 30
    o[sg], c[sg] = 99.0, 101.0                         # signal bar: open != close
    o[sg + 1] = 100.0                                  # entry bar open 100 (signal-bar open 99 / close 101 must not be used)
    sim = S.simulate(o, h, l, c, atr, "RIDE")
    assert sim["entry"][sg] == 100.0
    o[sg + 1] = 100.5
    sim = S.simulate(o, h, l, c, atr, "RIDE")
    assert sim["entry"][sg] == 100.5 and sim["S"][sg] == pytest.approx(max(2.5 * atr[sg], 0.02 * 100.5))
    # entry price flows through the trade row
    seg = make_seg(*flat_bars(500))
    seg.o[261] = 100.7                                 # entry open of a signal on bar 260
    sig = np.zeros(500, bool)
    sig[260] = True
    w = S.build_world([seg], synth_btc(), bug=False, sig_override={"A": [sig], "B": [np.zeros(500, bool)]})
    t = S.trade_frame(w, "A", "RIDE", [0]).iloc[0]
    assert t.entry_px == pytest.approx(100.7) and t.signal_date < t.entry_date


def test_ride_signal_exit_next_open_and_time_exits():
    ts, o, h, l, c, v = flat_bars(160)
    atr = S.atr_sma(h, l, c, 14)
    sg = 30
    e = sg + 1
    j = e + 12                                         # close below the prior-10-day low (98) without touching the stop (90)
    l[j], c[j] = 94.0, 95.0
    o[j + 1] = 96.0                                    # fill must be the NEXT open, not the signal close 95
    sim = S.simulate(o, h, l, c, atr, "RIDE")
    assert sim["reason"][sg] == 3 and sim["xi"][sg] == j and sim["px"][sg] == pytest.approx(96.0)
    # a close AT the prior 10-day low is NOT a signal exit (strictly below needed)
    ts, o, h, l, c, v = flat_bars(160)
    l[j], c[j] = 94.0, 98.0
    sim = S.simulate(o, h, l, c, atr, "RIDE")
    assert sim["reason"][sg] == 4
    # time exits: RIDE closes day 60 (entry day = day 1 -> bar e+59), CAP3R day 30 (bar e+29), at that bar's close
    ts, o, h, l, c, v = flat_bars(160)
    c[e + 59], c[e + 29] = 101.0, 100.5
    sim = S.simulate(o, h, l, c, atr, "RIDE")
    assert sim["reason"][sg] == 4 and sim["xi"][sg] == e + 59 and sim["px"][sg] == pytest.approx(101.0)
    simc = S.simulate(o, h, l, c, atr, "CAP3R")
    assert simc["reason"][sg] == 4 and simc["xi"][sg] == e + 29 and simc["px"][sg] == pytest.approx(100.5)
    # with one bar fewer than the time exit needs, the trade stays unresolved
    m = e + 59
    sim = S.simulate(o[:m], h[:m], l[:m], c[:m], atr[:m], "RIDE")
    assert sim["xi"][sg] == -1
    m = e + 29
    simc = S.simulate(o[:m], h[:m], l[:m], c[:m], atr[:m], "CAP3R")
    assert simc["xi"][sg] == -1


def test_weekly_vwap_monday_reset_hand_numbers():
    ts = ts_from(2021, 1, 3, 9)                        # Sun 3 Jan .. Mon 11 Jan 2021 (Mondays: 4 Jan, 11 Jan)
    tp = np.array([10, 20, 30, 10, 10, 10, 10, 10, 40], float)
    v = np.array([1, 1, 3, 4, 1, 1, 1, 1, 2], float)
    got = S.weekly_vwap(ts, tp, tp, tp, v)
    exp = [10, 20, 27.5, 18.75, 160 / 9, 17.0, 180 / 11, 190 / 12, 40]
    assert got.tolist() == pytest.approx(exp)


def test_cell_b_hand_vectors_and_reference():
    # RSI9 hand number: closes alternate 10,11,... -> 9 changes (5 up, 4 down), first RSI at index 9
    c = np.array([10, 11, 10, 11, 10, 11, 10, 11, 10, 11], float)
    r = S.rsi_wilder(c, 9)
    assert np.isnan(r[:9]).all() and r[9] == pytest.approx(100 - 100 / (1 + (5 / 9) / (4 / 9)))   # = 55.5556
    # EMA3 of [1,2,3,4,5]: seed SMA(1,2,3)=2 at idx2, then alpha .5: 3, 4
    assert S.ema_sma_seed(np.array([1, 2, 3, 4, 5.0]), 3)[2:].tolist() == pytest.approx([2.0, 3.0, 4.0])
    # WMA3 of [1,2,3,4]: (1*1+2*2+3*3)/6 = 14/6, (2+6+12)/6 = 20/6
    assert S.wma(np.array([1, 2, 3, 4.0]), 3)[2:].tolist() == pytest.approx([14 / 6, 20 / 6])
    # the whole cell-B state against a plain-loop reference, on a random walk long enough to exercise every leg
    rng = np.random.default_rng(5)
    n = 400
    seg = rw_seg(rng, n, start=(2020, 1, 1))
    seg.v = rng.uniform(500, 1500, n)
    seg.tbv = seg.v * 0.5
    got = S.coin_features(seg, bug=False)["B"]
    ref = np.array(_ref_cell_b(seg.ts, seg.h, seg.l, seg.c, seg.v))
    assert np.array_equal(got, ref)
    # teeth: each leg removes some bars, and the OR-combination differs from the AND
    rsi = S.rsi_wilder(seg.c, 9)
    e3, w21 = S.ema_sma_seed(rsi, 3), S.wma(rsi, 21)
    vw = S.weekly_vwap(seg.ts, seg.h, seg.l, seg.c, seg.v)
    hm = (w21 < rsi) & (w21 < e3)
    assert ref.sum() > 5 and (hm & ~(seg.c > vw)).sum() > 5 and ((seg.c > vw) & ~hm & ~np.isnan(w21)).sum() > 5
    assert ((w21 < rsi) & ~(w21 < e3)).sum() + ((w21 < e3) & ~(w21 < rsi)).sum() > 5


def test_cell_a_di_leg_and_volume_median_hand_cases():
    n = 90

    def trend(sign):
        ts = ts_from(2021, 1, 1, n)
        c = 200 + sign * 1.0 * np.arange(n)
        o = np.concatenate([[c[0]], c[:-1]])
        v = np.full(n, 1000.0)
        v[60] = 10000.0                                # 10x spike, prior-30 median 1000
        return make_seg(ts, o, c + 0.5, c - 0.5, c, v)
    up, dn = trend(+1), trend(-1)
    fu, fd = S.coin_features(up, bug=False), S.coin_features(dn, bug=False)
    assert fu["A"][60] and not fd["A"][60]             # DI+ > DI- needed: down trend with ADX 100 and a spike is NOT a signal
    dip, dim, adx = S.adx_di(dn.h, dn.l, dn.c, 14)
    assert adx[60] >= 20 and dim[60] > dip[60] and dn.v[60] >= 2 * 1000.0
    # median is of the PRIOR 30 days only; a spike of 1.999x the median gives no signal, 2.0x does
    up.v[60] = 1999.0
    assert not S.coin_features(up, bug=False)["A"][60]
    up.v[60] = 2000.0
    assert S.coin_features(up, bug=False)["A"][60]
    # the bar's own volume must not be in its median: prior 30 days median 1000 except 16 bars at 5000 (median 5000 with the own bar
    # of 5000 included would be the same), so use own volume 2500 vs 16 prior bars at 1000 and 14 at 5000 (prior median 1000 -> signal)
    up.v[30:60] = np.concatenate([np.full(16, 1000.0), np.full(14, 5000.0)])
    up.v[60] = 2500.0
    assert S.coin_features(up, bug=False)["A"][60]
    # with the own bar included the 31-value median would be... still 1000 here; flip: 15 prior bars at 1000, 15 at 5000 -> prior median 3000
    up.v[30:60] = np.concatenate([np.full(15, 1000.0), np.full(15, 5000.0)])
    assert not S.coin_features(up, bug=False)["A"][60]          # 2500 < 2 * 3000
    up.v[60] = 6000.0
    assert S.coin_features(up, bug=False)["A"][60]              # 6000 >= 2 * 3000


def test_warmup_250_bars():
    for sidx, expect in ((100, 0), (247, 0), (248, 0), (249, 1), (250, 1)):
        sig = np.zeros(500, bool)
        sig[sidx] = True
        w = S.build_world([make_seg(*flat_bars(500, start=(2020, 6, 1)))], synth_btc(), bug=False,
                          sig_override={"A": [sig], "B": [np.zeros(500, bool)]})
        assert len(S.trade_frame(w, "A", "RIDE", [0])) == expect, sidx


def test_basket_label_alignment_hand_number():
    n = 671
    ts = ts_from(2020, 3, 1, n)
    d = ts // DAY
    ret = 0.002 * ((d % 5) + 1)
    o = 100 * np.cumprod(np.concatenate([[1.0], 1 + ret[:-1]]))
    c = o * 1.001
    seg = make_seg(ts, o, o * 1.01, o * 0.99, c, np.full(n, 1000.0))
    w = S.build_world([seg], synth_btc(), bug=False, sig_override={"A": [np.zeros(n, bool)], "B": [np.zeros(n, bool)]})
    got = S.basket_daily(w, "dev")
    keys, lab = w.table
    exp = []
    for i in range(1, n - 1):                          # return of day[i] = open[i+1]/open[i]-1, eligible if bar i-1 >= 250th bar
        D = int(d[i])
        if i - 1 >= S.MIN_BARS - 1 and D <= S.DEV_END_DAY and S.phase_for_days((keys, lab), np.array([D]))[0] == 0:
            exp.append(o[i + 1] / o[i] - 1)
    assert got["days"] == len(exp) > 300
    assert got["mean_daily"] == pytest.approx(float(np.mean(exp)))
    assert S.phase_for_days((keys, lab), np.array([S.day_num(2021, 11, 2)]))[0] == 0     # last UP_E entry day 2021-11-02 (since 539) ...
    assert S.phase_for_days((keys, lab), np.array([S.day_num(2021, 11, 3)]))[0] == 1     # ... UP_L from 2021-11-03 (540 days)
    # the last UP_E day and the day after have different returns, so a one-day label shift moves the mean
    assert ret[int(S.day_num(2021, 11, 2) - d[0])] != ret[int(S.day_num(2021, 11, 3) - d[0])]


def test_bh_q_ex_best_week_boot_known_vectors():
    assert S.bh_q([0.01, 0.04]).tolist() == pytest.approx([0.02, 0.04])
    assert S.bh_q([0.04, 0.01]).tolist() == pytest.approx([0.04, 0.02])
    assert S.bh_q([0.03, 0.04]).tolist() == pytest.approx([0.04, 0.04])          # step-up monotone: min over larger ranks
    assert S.bh_q([0.01, 0.02, 0.03]).tolist() == pytest.approx([0.03, 0.03, 0.03])
    assert S.bh_q([0.9, 0.8]).tolist() == pytest.approx([0.9, 0.9])
    assert S.ex_best(list(range(1, 11)), 5) == pytest.approx(3.0)                # drops 6..10, keeps 1..5
    assert S.ex_best([-10, -5, 0, 1, 2, 3, 4, 5], 5) == pytest.approx(-5.0)       # drops the 5 BEST (1..5), keeps -10,-5,0
    assert S.ex_best([1, 2, 3, 4, 5], 5) is None
    wb = S.week_boot([1, 1, 3, 3], [10, 10, 11, 11])                             # two weeks: resampled means are 1, 2 or 3
    assert wb["mean"] == 2.0 and wb["weeks"] == 2 and wb["ci_lo"] == 1.0 and wb["ci_hi"] == 3.0
    assert wb["p"] == pytest.approx(1 / (S.BOOT_B + 1))
    ws = S.week_boot([1, 1, 3, 3], [10, 10, 11, 11], shift=1.5)                  # H0 mean <= 1.5: resampled mean 1 -> p about 0.25
    assert ws["mean"] == 0.5 and 0.2 < ws["p"] < 0.3
    w0 = S.week_boot([1, 1, 3, 3], [10, 10, 11, 11], shift=2.0)                  # resampled mean 2 sits exactly at H0: counts (<=), p about 0.75
    assert 0.70 < w0["p"] < 0.80


def test_delist_forced_exit_at_segment_end():
    ts, o, h, l, c, v = flat_bars(60)
    atr = S.atr_sma(h, l, c, 14)
    c[-1] = 93.0                                       # last close 93: stop 90 not touched, still open at the segment end
    l[-1] = 92.0
    sg = 50
    for kind in ("RIDE", "CAP3R"):
        keep = S.simulate(o, h, l, c, atr, kind)
        assert keep["xi"][sg] == -1                                             # at the GLOBAL end an unresolved trade is dropped
        sim = S.simulate(o, h, l, c, atr, kind, force_end=True)
        assert sim["xi"][sg] == 59 and sim["px"][sg] == pytest.approx(93.0) and S.REASON[int(sim["reason"][sg])] == "DELIST"
        assert sim["ret"][sg] == pytest.approx(-0.07)
    # a crash into the last bar below the stop is a normal STOP at the open, not DELIST
    ts, o, h, l, c, v = flat_bars(60)
    o[-1], l[-1], c[-1] = 70.0, 60.0, 65.0
    sim = S.simulate(o, h, l, c, S.atr_sma(h, l, c, 14), "RIDE", force_end=True)
    assert S.REASON[int(sim["reason"][57])] == "STOP" and sim["px"][57] == pytest.approx(70.0)
    # through build_world: an ended segment keeps the loss as a DELIST row, a non-ended one drops it
    n = 500
    sig = np.zeros(n, bool)
    sig[n - 5] = True
    res = {}
    for ended in (False, True):
        seg = make_seg(*flat_bars(n, start=(2020, 6, 1)))
        seg.c = seg.c.copy()
        seg.c[-1] = 93.0
        seg.ended = ended
        w = S.build_world([seg], synth_btc(), bug=False, sig_override={"A": [sig], "B": [np.zeros(n, bool)]})
        res[ended] = S.trade_frame(w, "A", "RIDE", [0])
        assert S.dropped_unresolved(w, "A", "RIDE", "dev") == (0 if ended else 1)
    assert len(res[False]) == 0 and len(res[True]) == 1
    t = res[True].iloc[0]
    assert t.exit_reason == "DELIST" and t.days_held == 4 and t.net_R < 0


def _write_csv(root, name, ts, o, h, l, c, v):
    import pandas as pd
    os.makedirs(os.path.join(root, "spot_1d"), exist_ok=True)
    pd.DataFrame(dict(ts=ts, o=o, h=h, l=l, c=c, v=v, tbv=v * 0.5)).to_csv(os.path.join(root, "spot_1d", f"{name}USDT.csv"), index=False)


def test_dev_truncated_vs_untruncated_and_ended_flags(tmp_path):
    root = str(tmp_path)
    rng = np.random.default_rng(3)
    nb = 1900                                          # BTC 2019-01-01 .. 2024-03-14
    bts = ts_from(2019, 1, 1, nb)
    bc = 4000 * np.exp(0.0012 * np.arange(nb))
    _write_csv(root, "BTC", bts, bc, bc * 1.01, bc * 0.99, bc, np.full(nb, 1e4))
    n = 1700                                           # NEAR 2019-10-01 .. 2024-06-26: past DEV_END + 62 d (2024-03-03)
    cts = ts_from(2019, 10, 1, n)
    r = rng.normal(0.004, 0.04, n)
    cc = 100 * np.exp(np.cumsum(r))
    co = np.concatenate([[100.0], cc[:-1]])
    ch, cl = np.maximum(co, cc) * 1.005, np.minimum(co, cc) * 0.995
    cv = rng.uniform(500, 1500, n)
    cv[rng.integers(260, n, 140)] *= 5
    _write_csv(root, "NEAR", cts, co, ch, cl, cc, cv)
    # FIL: a calendar gap after bar 399, so segment #1 ends for real; segment #2 runs to the end of its (early-ending) file
    gts = np.concatenate([ts_from(2019, 10, 1, 400), ts_from(2021, 1, 1, 1500)])
    gc = 50 * np.exp(np.cumsum(rng.normal(0.003, 0.04, 1900)))
    _write_csv(root, "FIL", gts, np.concatenate([[50.0], gc[:-1]]), gc * 1.01, gc * 0.99, gc, np.full(1900, 1000.0))
    wd, kept_d, _ = S.load_world("dev", root)
    wv, kept_v, _ = S.load_world("val", root)
    flags_d = {s.name: s.ended for s in wd.segs}
    flags_v = {s.name: s.ended for s in wv.segs}
    assert flags_d == {"NEAR": False, "FIL#1": True, "FIL#2": False}, flags_d      # DEV cut is not a delisting
    assert flags_v == {"NEAR": True, "FIL#1": True, "FIL#2": True}, flags_v        # real early ends are
    assert wd.segs[0].n < wv.segs[0].n                  # DEV world really is truncated
    total = 0
    for cell in S.CELLS:
        for kind in S.KINDS:
            a = S.trade_frame(wd, cell, kind, [0, 1, 2, 3])
            b = S.trade_frame(wv, cell, kind, [0, 1, 2, 3])
            a, b = a[S.window_mask(a, "dev")].reset_index(drop=True), b[S.window_mask(b, "dev")].reset_index(drop=True)
            assert a.drop(columns=["si"]).equals(b.drop(columns=["si"])), (cell, kind)
            total += len(a)
    pa, pb = S.pool_for(wd, "RIDE", "dev"), S.pool_for(wv, "RIDE", "dev")
    assert len(pa["r"]) == len(pb["r"]) and np.allclose(pa["r"], pb["r"])
    assert total > 20                                   # the comparison has teeth: DEV trades exist
    assert S.basket_daily(wd, "dev") == S.basket_daily(wv, "dev")


def test_window_constants_pinned():
    assert S.DEV_END_DAY == S.day_num(2023, 12, 31) and S.VAL_START_DAY == S.day_num(2024, 1, 1)
    assert S.MIN_BARS == 250 and S.HOLD == {"RIDE": 60, "CAP3R": 30} and S.EARLY_DAYS == 540
