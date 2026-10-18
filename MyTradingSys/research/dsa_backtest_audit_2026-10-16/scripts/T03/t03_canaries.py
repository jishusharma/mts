"""T03 planted-edge canaries. Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T03/t03_canaries.py [--mutations]

Seeded synthetic 1m markets (30 days, built in %TEMP%/dsa_audit/T03) with known answers are pushed through every
simulator entry point. Expected numbers come from the small formulas in this file (price ratios, the (t_in, t_out]
funding convention of FORMULAS.md section 13, stop-first on a same-bar double hit), never from the code under test.
No real data is read. Seed is printed. Writes scripts/T03/out/canary_results.json and canary_table.md.
"""
import argparse
import datetime as dt
import importlib.util
import json
import sys
import tempfile
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "MyTradingSys").is_dir())
sys.path.insert(0, str(ROOT))
RES = ROOT / "MyTradingSys" / "research"
OUT = HERE / "out"
TMP = Path(tempfile.gettempdir()) / "dsa_audit" / "T03"
SEED = 20261018
MS = 60_000
TS0 = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
NDAYS = 30
N = NDAYS * 1440
HOLD = 60
PER8 = 480                      # bars per 8h settlement period; TS0 is a settlement instant
TOL = 1e-8                      # percentage points


# ------------------------------------------------------------------ module loading (optionally mutated)
def load_src(name, path, mutate=()):
    src = Path(path).read_text(encoding="utf-8")
    for a, b in mutate:
        assert a in src, f"mutation anchor missing: {a}"
        src = src.replace(a, b)
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(src, str(path), "exec"), mod.__dict__)
    return mod


# ------------------------------------------------------------------ markets
class Mk:
    """Continuous 1m bars. O/C set per bar; H/L default to max/min of O,C (no wicks) unless overridden."""

    def __init__(self, price=100.0):
        self.O = np.full(N, price)
        self.C = np.full(N, price)
        self.Hh = np.full(N, np.nan)
        self.Ll = np.full(N, np.nan)

    def bar(self, i, o, c, hi=None, lo=None):
        self.O[i], self.C[i] = o, c
        if hi is not None:
            self.Hh[i] = hi
        if lo is not None:
            self.Ll[i] = lo

    def flat(self, a, b, px):                      # bars a..b-1 flat at px
        self.O[a:b] = px
        self.C[a:b] = px

    def done(self):
        self.H = np.where(np.isnan(self.Hh), np.maximum(self.O, self.C), self.Hh)
        self.L = np.where(np.isnan(self.Ll), np.minimum(self.O, self.C), self.Ll)
        return self


def events_clean():
    """Entry bar e = 480*m + 200 (hold of 60 bars never crosses a 00/08/16 UTC settlement), sides alternate."""
    return [(480 * m + 200, 1 if m % 2 == 0 else -1) for m in range(2, 85)]


def events_funding(kind):
    if kind == "interior":                         # settlement 30 bars into the hold
        return [(480 * m - 30, 1 if m % 2 == 0 else -1) for m in range(2, 85)]
    if kind == "entry_on":                         # entry bar opens exactly at the settlement instant
        return [(480 * m, 1 if m % 2 == 0 else -1) for m in range(2, 85)]
    if kind == "exit_on":                          # exit instant (open of bar e+HOLD) is exactly the settlement
        return [(480 * m - HOLD, 1 if m % 2 == 0 else -1) for m in range(2, 85)]
    raise ValueError(kind)


def market(kind):
    """Returns (Mk, events). Event = (entry bar index e, side +1/-1). Entry price = O[e]."""
    ev = events_clean()
    if kind == "zero":
        rng = np.random.default_rng(SEED)
        C = 100.0 * np.exp(np.cumsum(rng.normal(0.0, 2e-4, N)))
        m = Mk()
        m.C = C
        m.O = np.concatenate(([100.0], C[:-1]))
        w = rng.uniform(0.0, 1e-4, (2, N))
        m.Hh = np.maximum(m.O, m.C) * (1 + w[0])
        m.Ll = np.minimum(m.O, m.C) * (1 - w[1])
        return m.done(), ev
    m = Mk()
    d = 0.003
    for e, s in ev:
        if kind == "planted":                      # linear ramp over the hold, +0.30 % in the trade's favour
            for k in range(HOLD):
                m.bar(e + k, 100.0 * (1 + s * d * k / HOLD), 100.0 * (1 + s * d * (k + 1) / HOLD))
            m.bar(e + HOLD, 100.0 * (1 + s * d), 100.0)
        elif kind == "inside_signal_bar":          # the whole move happens inside the signal bar e-1
            m.bar(e - 1, 100.0, 100.0 * (1 + s * d))
            m.flat(e, e + HOLD, 100.0 * (1 + s * d))
            m.bar(e + HOLD, 100.0 * (1 + s * d), 100.0)
        elif kind == "after_exit":                 # flat hold, the move starts in the bar right after the exit
            m.bar(e + HOLD, 100.0, 100.0 * (1 + s * d))
            m.bar(e + HOLD + 1, 100.0 * (1 + s * d), 100.0)
        elif kind == "gap_stop":                   # entry bar flat, then the market opens 2 % through the stop and stays there
            g = 100.0 * (1 - s * 0.02)
            m.flat(e + 1, e + HOLD, g)
            m.bar(e + HOLD, g, 100.0)
        elif kind == "same_bar":                   # one bar touches both stop (0.5 %) and target (1 % / 2R)
            hi, lo = (101.1, 99.4) if s > 0 else (100.6, 98.9)
            m.bar(e + 1, 100.0, 100.0, hi, lo)
        elif kind == "timeout_gap":                # flat hold; the bar after the last bar of the hold opens 1 % lower (long) / higher (short)
            m.bar(e + HOLD, 100.0 * (1 - s * 0.01), 100.0)
        elif kind == "flat":
            pass
        else:
            raise ValueError(kind)
    return m.done(), ev


def market_funding(kind):
    return Mk().done(), events_funding(kind)


def expected_fixed(mk, ev):
    """Own formula: long/short return in % from the entry-bar open to the close of the last bar of the hold."""
    return np.array([s * (mk.C[e + HOLD - 1] / mk.O[e] - 1.0) * 100.0 for e, s in ev])


def settle_count(e, hold=HOLD):
    """Settlements s with t_in < s <= t_out, t_in = open of bar e, t_out = open of bar e+hold (FORMULAS.md 13)."""
    return sum(1 for b in range(e + 1, e + hold + 1) if b % PER8 == 0)


# ------------------------------------------------------------------ harness adapters
def bars_list(mk):
    return [dict(t=TS0 + i * MS, o=float(mk.O[i]), h=float(mk.H[i]), l=float(mk.L[i]), c=float(mk.C[i])) for i in range(N)]


def bt_run(B, bars, mk, e, s, stop, targets, funding=None, mark=None, hold=HOLD):
    side = "long" if s > 0 else "short"
    entry = float(mk.O[e])
    r = B.simulate_trade(side, entry, TS0 + (e - 1) * MS, stop, targets, bars[e:e + hold + 4], mark_bars=mark, funding=funding,
                         max_bars=hold)
    risk = abs(entry - stop)
    return r, risk, entry


def gross_bt(B, mk, ev, bars, stop_pct=0.05):
    out = []
    for e, s in ev:
        stop = float(mk.O[e]) * (1 - s * stop_pct)
        r, risk, entry = bt_run(B, bars, mk, e, s, stop, [])
        out.append(np.nan if r["net_r"] is None else r["gross_r"] * risk / entry * 100.0)
    return np.array(out)


def bars1m(T, mk):
    z = np.zeros(N)
    return T.Bars1m(TS0, mk.O.tolist(), mk.H.tolist(), mk.L.tolist(), mk.C.tolist(), z.tolist(), z.tolist())


def gross_tom(T, mk, ev, b):
    out = []
    for e, s in ev:
        entry = float(mk.O[e])
        r = T.sim_limit_trade(b, e, "long" if s > 0 else "short", entry, entry * (1 - s * 0.05), entry * (1 + s * 0.5), 5, HOLD - 1)
        out.append(r["gross_r"] * abs(entry - entry * (1 - s * 0.05)) / entry * 100.0 if r.get("filled") and "gross_r" in r else np.nan)
    return np.array(out)


def gross_t055(R, mk, ev):
    bars = [dict(t=TS0 + i * MS, c=float(mk.C[i])) for i in range(N)]
    evs = [dict(i=e - 1, side="long" if s > 0 else "short") for e, s in ev]
    tr = R.score_trades(evs, bars, HOLD, MS, [], lambda *a, **k: 0.0)
    return np.array([x["gross"] * 100.0 for x in tr])


def screen_cells(S, mk, ev, d=0):
    A = dict(O=mk.O, H=mk.H, L=mk.L)
    t = np.array([e - 1 - d for e, _ in ev], np.int64)
    side = np.array([s for _, s in ev], np.int64)
    led = dict(t=t, side=side, F=np.zeros(len(t), bool), day=t // 1440, D5=np.zeros(len(t)), leg=np.zeros(len(t)))
    return S.compute_cells(A, led, NDAYS)


def gross_screen(S, mk, ev):
    return screen_cells(S, mk, ev)["G"][(0, HOLD)]


def gross_chart(K, mk, ev):
    t = np.array([e - 2 for e, _ in ev], np.int64)
    side = np.array([s for _, s in ev], np.int64)
    return K.trade_gross(mk.O, t, side, HOLD, d=1)


def of_trade(OF, mk, ev, ext_fn=None):
    A1 = np.column_stack((mk.O, mk.H, mk.L, mk.C))
    res = []
    for e, s in ev:
        side = "long" if s > 0 else "short"
        ext = float(mk.O[e]) * (1 - s * 0.05) if ext_fn is None else ext_fn(e, s)
        res.append(OF.trade(A1, e, ext, side))
    return res


def gross_of(OF, mk, ev):
    return np.array([r[1] + OF.FEE_RT if r else np.nan for r in of_trade(OF, mk, ev)])


def lv_rows(mk, a, b):
    return np.column_stack((TS0 + np.arange(a, b) * MS, mk.O[a:b], mk.H[a:b], mk.L[a:b], mk.C[a:b], np.zeros(b - a)))


def lv_run(P, mk, e, s, stop, t1, hold=HOLD):
    rows = lv_rows(mk, e, e + hold)
    res = P.run(rows, (0, s, float(mk.O[e]), stop, t1, t1 + (t1 - mk.O[e])), "single", False)
    return res


def lv_exit(res, s):
    f = [x for x in res["fills"] if x[1] != "entry"]
    ent = [x for x in res["fills"] if x[1] == "entry"]
    if not f or not ent:
        return np.nan, "none"
    return s * (f[-1][3] / ent[0][3] - 1.0) * 100.0, f[-1][1]


def gross_lv(P, mk, ev):
    return np.array([lv_exit(lv_run(P, mk, e, s, float(mk.O[e]) * (1 - s * 0.05), float(mk.O[e]) * (1 + s * 0.5)), s)[0] for e, s in ev])


# ------------------------------------------------------------------ result collection
class Table:
    def __init__(self):
        self.rows = []

    def cmp(self, h, canary, exp, got, tol=TOL, note=""):
        exp, got = np.asarray(exp, float), np.asarray(got, float)
        if got.size == 0 or np.isnan(got).all():
            return self.block(h, canary, note or "harness returned no value")
        diff = np.nanmax(np.abs(exp - got))
        self.rows.append(dict(harness=h, canary=canary, n=int(got.size), expected=float(np.nanmean(exp)), got=float(np.nanmean(got)),
                              max_abs_diff=float(diff), status="PASS" if diff <= tol else "FAIL", note=note))

    def scalar(self, h, canary, exp, got, tol=TOL, note=""):
        self.cmp(h, canary, [exp], [got], tol, note)

    def block(self, h, canary, why):
        self.rows.append(dict(harness=h, canary=canary, n=0, expected=None, got=None, max_abs_diff=None, status="BLOCKED", note=why))


def run_all(mods, tag=""):
    B, T, R, S, K, OF, P = (mods[k] for k in ("bt", "tom", "t055", "screen", "chart", "of", "lv"))
    TC = mods["costs"]
    tb = Table()
    markets = {k: market(k) for k in ("zero", "planted", "inside_signal_bar", "after_exit")}
    cases = [("a_zero_drift", "zero"), ("b_planted_0.30", "planted"), ("c_move_inside_signal_bar", "inside_signal_bar"), ("d_move_after_exit", "after_exit")]
    mkr_bt = {k: bars_list(v[0]) for k, v in markets.items()}
    mkr_tom = {k: bars1m(T, v[0]) for k, v in markets.items()}
    for cname, k in cases:
        mk, ev = markets[k]
        exp = expected_fixed(mk, ev)
        tb.cmp("bt_engine.simulate_trade", cname, exp, gross_bt(B, mk, ev, mkr_bt[k]))
        tb.cmp("tom_bt.sim_limit_trade", cname, exp, gross_tom(T, mk, ev, mkr_tom[k]))
        tb.cmp("run_t055.score_trades", cname, exp, gross_t055(R, mk, ev))
        tb.cmp("screen.compute_cells", cname, exp, gross_screen(S, mk, ev))
        tb.cmp("chart_read_g5.trade_gross", cname, exp, gross_chart(K, mk, ev))
        tb.cmp("orderflow_views.trade (fw60)", cname, exp, gross_of(OF, mk, ev))
        tb.cmp("levels_sizing.run (day_end)", cname, exp, gross_lv(P, mk, ev))
        if cname.startswith("a_"):
            tb.scalar("zero-edge sanity", cname, 0.0, float(np.mean(exp)), tol=3 * float(np.std(exp) / np.sqrt(len(exp))) + 1e-12,
                      note=f"seed {SEED}; planted market has mean(exp)=0 within 3 SE of the walk")
    # net accounting on the planted market (own formulas)
    mk, ev = markets["planted"]
    bl = mkr_bt["planted"]
    nets = []
    for e, s in ev:
        r, risk, entry = bt_run(B, bl, mk, e, s, float(mk.O[e]) * (1 - s * 0.05), [])
        pout = float(mk.C[e + HOLD - 1])
        nets.append((r["pnl_pct_net"], 0.30 - 0.05 - 0.05 * pout / entry))
    tb.cmp("bt_engine.simulate_trade", "b_net_fees_taker_both_legs", [x[1] for x in nets], [x[0] for x in nets], note="expected = 0.30 - 0.05 - 0.05*pout/pin (pct)")
    res = []
    for e, s in ev:
        entry = float(mk.O[e])
        r = T.sim_limit_trade(mkr_tom["planted"], e, "long" if s > 0 else "short", entry, entry * (1 - s * 0.05), entry * (1 + s * 0.5), 5, HOLD - 1)
        pout = float(mk.C[e + HOLD - 1])
        res.append((r["net_r"] * abs(entry * 0.05) / entry * 100.0, 0.30 - 0.0 - 0.05 * pout / entry))
    tb.cmp("tom_bt.sim_limit_trade", "b_net_fees_maker_in_taker_out", [x[1] for x in res], [x[0] for x in res], note="Deribit maker 0 / taker 0.05")
    bars = [dict(t=TS0 + i * MS, c=float(mk.C[i])) for i in range(N)]
    tr = R.score_trades([dict(i=e - 1, side="long" if s > 0 else "short") for e, s in ev], bars, HOLD, MS, [], TC.net_return)
    tb.cmp("run_t055.score_trades", "b_net_cost_model", [0.003 - 0.0012 for _ in ev], [x["net"] for x in tr], tol=1e-12, note="net = gross - 0.0010 - 0.0002 (FORMULAS 13); fraction")

    # ---------------- (e) funding
    for kind in ("interior", "entry_on", "exit_on"):
        mk, ev = market_funding(kind)
        for rate in (1e-4, -1e-4):
            tag_ = f"e_funding_{kind}_rate{rate:+.4f}"
            expf = np.array([s * rate * 100.0 * settle_count(e) for e, s in ev])      # pct paid by the trader
            frec = [(TS0 + 480 * m * MS, rate) for m in range(0, 90)]
            bl = bars_list(mk)
            got = []
            for e, s in ev:
                r, *_ = bt_run(B, bl, mk, e, s, 100.0 * (1 - s * 0.05), [], funding=frec)
                got.append(r["funding_paid_pct"])
            tb.cmp("bt_engine.simulate_trade", tag_, expf, got)
            got_n = []
            for e, s in ev:
                r, *_ = bt_run(B, bl, mk, e, s, 100.0 * (1 - s * 0.05), [], funding=None)
                got_n.append(r["funding_paid_pct"])
            if kind == "interior":
                tb.cmp("bt_engine.simulate_trade (funding=None)", tag_, expf, got_n, note="L5: None means 0 with no error")
            got = [100.0 * TC.funding_paid("long" if s > 0 else "short", TS0 + e * MS, TS0 + (e + HOLD) * MS, frec) for e, s in ev]
            tb.cmp("trade_costs.funding_paid", tag_, expf, got, tol=1e-9)
            bars = [dict(t=TS0 + i * MS, c=float(mk.C[i])) for i in range(N)]
            tr = R.score_trades([dict(i=e - 1, side="long" if s > 0 else "short") for e, s in ev], bars, HOLD, MS, frec, TC.net_return)
            tb.cmp("run_t055.score_trades", tag_, expf, [100.0 * (x["net_nofund"] - x["net"]) for x in tr], tol=1e-9)
            cells = screen_cells(S, mk, ev)
            tb.cmp("screen.compute_cells FUND", tag_, expf, cells["FUND"][(0, HOLD)], note="flat 1 bp per crossing, blind to side and rate (L1)")
            t = np.array([e - 2 for e, _ in ev], np.int64)
            tb.cmp("chart_read_g5.funding_pct", tag_, expf, K.funding_pct(t + 2, t + 2 + HOLD), note="flat 1 bp per crossing, blind to side and rate (L1)")
    tb.block("tom_bt.sim_limit_trade", "e_funding", "no funding term in sim_limit_trade (fees only)")
    tb.block("orderflow_views.trade", "e_funding", "no funding term (FEE_RT only)")
    tb.block("levels_sizing.run", "e_funding", "no rate input; flat stress qty*op*1e-4/480 per bar, side-blind (cannot take a rate)")
    # bt_engine partial coverage: records stop before the hold
    mk, ev = market_funding("interior")
    bl = bars_list(mk)
    short = [(TS0 + 480 * m * MS, 1e-4) for m in range(0, 10)]
    raised = 0
    for e, s in ev:
        try:
            bt_run(B, bl, mk, e, s, 95.0 if s > 0 else 105.0, [], funding=short)
        except ValueError:
            raised += 1
    need = sum(1 for e, _ in ev if e + HOLD > 480 * 9)
    tb.scalar("bt_engine.simulate_trade", "e_funding_records_missing_for_hold", need, raised, note="expected fail-closed (B103 behaviour of trade_costs) on every event whose exit is past the last funding record; got = events that raised")
    raised = 0
    bars = [dict(t=TS0 + i * MS, c=100.0) for i in range(N)]
    for e, s in ev:
        try:
            R.score_trades([dict(i=e - 1, side="long" if s > 0 else "short")], bars, HOLD, MS, short, TC.net_return)
        except ValueError:
            raised += 1
    tb.scalar("run_t055.score_trades", "e_funding_records_missing_for_hold", need, raised, note="expected fail-closed on every event whose exit is past the last funding record")

    # ---------------- (f) gap through the stop
    mk, ev = market("gap_stop")
    exp = np.array([s * (mk.O[e + 1] / mk.O[e] - 1.0) * 100.0 for e, s in ev])          # fill at the gap open, -2.00 pct
    bl = bars_list(mk)
    got = []
    for e, s in ev:
        stop = 100.0 * (1 - s * 0.005)
        r, risk, entry = bt_run(B, bl, mk, e, s, stop, [(100.0 * (1 + s * 0.01), 1.0)])
        got.append(r["gross_r"] * risk / entry * 100.0)
    tb.cmp("bt_engine.simulate_trade", "f_gap_through_stop", exp, got)
    b = bars1m(T, mk)
    got = []
    for e, s in ev:
        entry = 100.0
        r = T.sim_limit_trade(b, e, "long" if s > 0 else "short", entry, entry * (1 - s * 0.005), entry * (1 + s * 0.01), 5, HOLD - 1)
        got.append(r["gross_r"] * abs(entry * 0.005) / entry * 100.0)
    tb.cmp("tom_bt.sim_limit_trade", "f_gap_through_stop", exp, got)
    res = of_trade(OF, mk, ev, lambda e, s: 100.0 * (1 - s * 0.005) / (1 - s * 0.001))
    tb.cmp("orderflow_views.trade (stop/2R leg)", "f_gap_through_stop", exp, [r[3] + OF.FEE_RT for r in res], note="N2 of 2026-10-15 audit: books the stop price, not the gap open")
    got = [lv_exit(lv_run(P, mk, e, s, 100.0 * (1 - s * 0.005), 100.0 * (1 + s * 0.02)), s)[0] for e, s in ev]
    tb.cmp("levels_sizing.run", "f_gap_through_stop", exp, got)
    for h in ("run_t055.score_trades", "screen.compute_cells", "chart_read_g5.trade_gross"):
        tb.block(h, "f_gap_through_stop", "fixed-hold harness: no stop concept")
    # L5 mark-bar variants (bt_engine only)
    exit_reason = []
    for e, s in ev:                                   # mark stays at 100 for the whole hold while the trade tape gaps 2 % through the stop
        mark = {TS0 + k * MS: dict(t=TS0 + k * MS, o=100.0, h=100.0, l=100.0, c=100.0) for k in range(e + 1, e + HOLD + 1)}
        r, *_ = bt_run(B, bl, mk, e, s, 100.0 * (1 - s * 0.005), [(100.0 * (1 + s * 0.01), 1.0)], mark=mark)
        exit_reason.append(r["exit_reason"] == "stop")
    tb.scalar("bt_engine.simulate_trade", "f2_trade_gaps_but_mark_does_not", 0.0, float(np.mean(exit_reason)),
              note="exchange stops trigger on MARK: no stop expected while mark stays above; got = share of events stopped (0 = consistent)")

    # ---------------- (g) same bar stop + target
    mk, ev = market("same_bar")
    exp = np.array([s * ((100.0 * (1 - s * 0.005)) / 100.0 - 1.0) * 100.0 for e, s in ev])      # stop first: -0.50 pct
    bl = bars_list(mk)
    got, amb = [], []
    for e, s in ev:
        stop, tgt = 100.0 * (1 - s * 0.005), 100.0 * (1 + s * 0.01)
        r, risk, entry = bt_run(B, bl, mk, e, s, stop, [(tgt, 1.0)])
        got.append(r["gross_r"] * risk / entry * 100.0)
        amb.append(r["ambiguous_bars"])
    tb.cmp("bt_engine.simulate_trade", "g_same_bar_stop_and_target", exp, got)
    tb.scalar("bt_engine.simulate_trade", "g_ambiguous_counter", len(ev), sum(amb))
    b = bars1m(T, mk)
    got = []
    for e, s in ev:
        entry = 100.0
        r = T.sim_limit_trade(b, e, "long" if s > 0 else "short", entry, entry * (1 - s * 0.005), entry * (1 + s * 0.01), 5, HOLD - 1)
        got.append(r["gross_r"] * abs(entry * 0.005) / entry * 100.0)
    tb.cmp("tom_bt.sim_limit_trade", "g_same_bar_stop_and_target", exp, got)
    res = of_trade(OF, mk, ev, lambda e, s: 100.0 * (1 - s * 0.005) / (1 - s * 0.001))
    tb.cmp("orderflow_views.trade (stop/2R leg)", "g_same_bar_stop_and_target", exp, [r[3] + OF.FEE_RT for r in res])
    got = []
    for e, s in ev:
        got.append(lv_exit(lv_run(P, mk, e, s, 100.0 * (1 - s * 0.005), 100.0 * (1 + s * 0.01)), s)[0])
    tb.cmp("levels_sizing.run", "g_same_bar_stop_and_target", exp, got)
    for h in ("run_t055.score_trades", "screen.compute_cells", "chart_read_g5.trade_gross"):
        tb.block(h, "g_same_bar_stop_and_target", "fixed-hold harness: no stop or target")

    # ---------------- (h) timeout: reason, bars held, fill price; and the L5 close-vs-next-open gap
    mk, ev = market("planted")
    bl = bars_list(mk)
    ok_reason, ok_bars, ok_t = [], [], []
    for e, s in ev:
        r, *_ = bt_run(B, bl, mk, e, s, float(mk.O[e]) * (1 - s * 0.05), [])
        ok_reason.append(r["exit_reason"] == "timeout")
        ok_bars.append(r["bars_held"] == HOLD)
        ok_t.append(r["exit_t"] == TS0 + (e + HOLD - 1) * MS)
    tb.scalar("bt_engine.simulate_trade", "h_timeout_reason_bars_exit_bar", 3.0, float(np.mean(ok_reason) + np.mean(ok_bars) + np.mean(ok_t)))
    mk, ev = market("timeout_gap")
    bl = bars_list(mk)
    eng = np.array([bt_run(B, bl, mk, e, s, float(mk.O[e]) * (1 - s * 0.05), [])[0]["gross_r"] * abs(float(mk.O[e]) * 0.05) / float(mk.O[e]) * 100.0 for e, s in ev])
    scr = gross_screen(S, mk, ev)
    nxt = np.array([s * (mk.O[e + HOLD] / mk.O[e] - 1.0) * 100.0 for e, s in ev])
    tb.cmp("bt_engine.simulate_trade", "h2_timeout_vs_next_open_gap", nxt, eng, note="L5: timeout fills at the last bar's close; a market exit sent at that close fills at the next open. got=close fill, exp=next-open fill (-1.00 pct apart)")
    tb.cmp("screen.compute_cells", "h2_timeout_vs_next_open_gap", nxt, scr, note="screen exits at the next open: consistent with the next-open reading")
    # tom_bt timeout: close of last bar; fill price uses slip=0
    b = bars1m(T, mk)
    got = []
    for e, s in ev:
        entry = 100.0
        r = T.sim_limit_trade(b, e, "long" if s > 0 else "short", entry, entry * (1 - s * 0.05), entry * (1 + s * 0.5), 5, HOLD - 1)
        got.append(r["gross_r"] * abs(entry * 0.05) / entry * 100.0)
    tb.cmp("tom_bt.sim_limit_trade", "h2_timeout_vs_next_open_gap", nxt, got, note="same close-fill convention as bt_engine")
    return tb


def load_modules(mut=None):
    mut = mut or {}
    mods = {}
    mods["bt"] = load_src("bt_engine_t03", ROOT / "MyTradingSys/backtest/bt/bt_engine.py", mut.get("bt", ()))
    import MyTradingSys.backtest.tom_bt as T
    import MyTradingSys.backtest.layers.positioning.trade_costs as TC
    import MyTradingSys.backtest.layers.run_t055 as R
    mods["tom"], mods["costs"], mods["t055"] = T, TC, R
    sys.path.insert(0, str(RES / "gross_effect_screen_2026-10-15"))
    import screen as S
    mods["screen"] = S
    mods["chart"] = load_src("chart_common_t03", RES / "chart_read_g5_2026-10-16/common.py", mut.get("chart", ()))
    mods["of"] = load_src("of_study_t03", RES / "orderflow_views_2026-10-14/study.py", mut.get("of", ()))
    mods["lv"] = load_src("lv_probe_t03", RES / "levels_sizing_2026-10-14/probe.py", mut.get("lv", ()))
    return mods


MUTATIONS = {
    "M1 bt_engine funding sign dropped": dict(bt=[("paid = sgn * rate * remaining", "paid = rate * remaining")]),
    "M2 bt_engine gap fills at the stop": dict(bt=[("stop_px = b[\"o\"] if gapped else stop", "stop_px = stop")]),
    "M3 bt_engine targets before stop on a double hit": dict(bt=[("if stop_hit and (stop_first or not hit_targets):", "if stop_hit and (not stop_first and not hit_targets):")]),
    "M4 chart_read exit one bar late": dict(chart=[("e, x = t + 1 + d, t + 1 + d + h", "e, x = t + 1 + d, t + 2 + d + h")]),
    "M5 chart_read enters on the signal bar open": dict(chart=[("e, x = t + 1 + d, t + 1 + d + h", "e, x = t + d, t + 1 + d + h")]),
}


def table_md(rows):
    L = ["| harness | canary | n | expected (mean, pct) | got (mean, pct) | max abs diff | status | note |", "|---|---|---|---|---|---|---|---|"]
    f = lambda v: "" if v is None else f"{v:.6f}"
    for r in rows:
        L.append(f"| {r['harness']} | {r['canary']} | {r['n']} | {f(r['expected'])} | {f(r['got'])} | {f(r['max_abs_diff'])} | {r['status']} | {r['note']} |")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutations", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    print("seed", SEED, "root", ROOT)
    tb = run_all(load_modules())
    (OUT / "canary_results.json").write_text(json.dumps(tb.rows, indent=1), encoding="utf-8", newline="\n")
    (OUT / "canary_table.md").write_text(table_md(tb.rows) + "\n", encoding="utf-8", newline="\n")
    for k in ("PASS", "FAIL", "BLOCKED"):
        print(k, sum(r["status"] == k for r in tb.rows))
    for r in tb.rows:
        if r["status"] == "FAIL":
            print("FAIL", r["harness"], r["canary"], r["expected"], r["got"])
    if a.mutations:
        base = {(r["harness"], r["canary"]): r["status"] for r in tb.rows}
        kills = []
        for name, mut in MUTATIONS.items():
            t2 = run_all(load_modules(mut))
            flipped = [(r["harness"], r["canary"]) for r in t2.rows if r["status"] == "FAIL" and base.get((r["harness"], r["canary"])) == "PASS"]
            kills.append(dict(mutation=name, newly_failing=len(flipped), examples=[f"{h} / {c}" for h, c in flipped[:4]]))
            print("MUTATION", name, "-> newly FAIL:", len(flipped), flipped[:3])
        (OUT / "mutation_kills.json").write_text(json.dumps(kills, indent=1), encoding="utf-8", newline="\n")
    np.savez_compressed(TMP / "zero_market.npz", O=market("zero")[0].O, C=market("zero")[0].C)


if __name__ == "__main__":
    main()
