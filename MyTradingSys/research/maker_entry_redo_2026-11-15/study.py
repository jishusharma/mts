"""maker_entry_redo_2026-11-15: do resting LIMIT (maker) entries beat the taker entry fee-net on two already-studied 10-symbol rules?
Arm BB = bb_range_retest_10sym_2026-11-15 (level +- k ATR retest, 15m, range-gated, session-range tagged, 0.5x-distance stop bracket).
Arm WT = wt_c30_retest_10sym_2026-11-15 (WaveTrend dot, dot-bar-midpoint retest entry, gate "with", 12-bar close exit).
Signals, levels, brackets and horizons come UNCHANGED from the parent modules (imported by path). Only the entry changes: the limit is placed at the
parent's retest level when the parent's entry trigger would start, fills only when a 1m bar trades THROUGH it by one tick, at the limit price, and
the exit is walked on 1m bars. Costs: research_kit.TAKER_RT_PCT (taker baseline) and research_kit.MAKER_IN_RT_PCT (maker entry, taker exit);
nothing is redefined here. See PRE_REG.md. Passes: --pass count (signals, fills and days only, no returns), --pass run."""
import argparse
import calendar
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "dev"))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
import data_cache  # noqa: E402


def _load(name, rel):
    sp = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


bb10 = _load("bb10_parent", "MyTradingSys/research/bb_range_retest_10sym_2026-11-15/study.py")
wt10 = _load("wt10_parent", "MyTradingSys/research/wt_c30_retest_10sym_2026-11-15/study.py")
lvl, prev, base = bb10.lvl, bb10.prev, wt10.base

CACHE = data_cache.cache_dir() / "maker-redo-1115"
bb10.CACHE = CACHE / "bb"
wt10.CACHE = CACHE / "wt"
M1_DIR = data_cache.cache_dir() / "binance_1m"
SYMS = bb10.SYMS
DAY, M1 = 86400000, 60000
OOS_START = calendar.timegm((2024, 1, 1, 0, 0, 0)) * 1000
SPLIT_MS = calendar.timegm((2025, 7, 1, 0, 0, 0)) * 1000
OOS_END = calendar.timegm((2026, 11, 12, 0, 0, 0)) * 1000    # exclusive: the 1m archive ends 2026-11-13 23:59, exits need room
TAKER_PCT, MAKER_PCT = rk.TAKER_RT_PCT, rk.MAKER_IN_RT_PCT
MIN_N, MIN_DAYS = 30, 20
BB_SESS, BB_K = lvl.CONFIRM_SESSIONS, lvl.K_GRID            # 3 x 3 = 9 cells
WT_TFS, WT_CONFS, WT_SIDES = base.TFS, base.CONFIRM_CONFS, base.SIDES   # 3 x 2 x 2 = 12 cells
M_FAMILY = len(BB_SESS) * len(BB_K) + len(WT_TFS) * len(WT_CONFS) * len(WT_SIDES)    # 21


class M1Data:
    """1m archive of one symbol: arrays t,o,h,l,c (UTC ms) and the tick (smallest nonzero price step seen in the last 300k rows)."""

    def __init__(self, sym):
        z = np.load(M1_DIR / ("%sUSDT_1m.npz" % sym))
        self.t = z["t_ms"].astype(np.int64)
        self.o, self.h, self.l, self.c = z["o"], z["h"], z["l"], z["c"]
        self.tick = infer_tick(self.c[-300000:])

    def lo(self, t):
        return int(np.searchsorted(self.t, t, side="left"))


def infer_tick(prices):
    d = np.abs(np.diff(np.round(np.asarray(prices, dtype=float), 8)))
    d = d[d > 1e-9]
    return float(np.min(d)) if len(d) else 0.0


def limit_fill(m, t0, t1, level, side):
    """First 1m bar with start in [t0, t1) that trades through the limit by one tick (long: low <= level - tick; short: high >= level + tick).
    Touching the level exactly is NOT a fill. Fill price = the limit (never better). Returns the 1m index or None. Reads only bars >= t0."""
    a, b = m.lo(t0), m.lo(t1)
    if b <= a:
        return None
    if side > 0:
        hit = np.nonzero(m.l[a:b] <= level - m.tick)[0]
    else:
        hit = np.nonzero(m.h[a:b] >= level + m.tick)[0]
    return a + int(hit[0]) if len(hit) else None


def bracket_1m(m, f, px, sgn, target, stop_frac, t_end, close_end):
    """Bracket entered at px on 1m bar f: target = `target` (market on touch, taker as the shared cost model assumes), stop = px -+ stop_frac x
    |target - px| (market stop, a gap fills at the 1m open), time exit = `close_end` (the parent's 15m bar close) at t_end. The fill minute itself
    can stop the trade out (stop first), never reach the target (the fill price is only known to be touched inside it). Stop first when one 1m bar
    touches both. Returns (gross % of px, exit kind) or None when the target is on the wrong side."""
    if (target - px) * sgn <= 0:
        return None
    stop = px - sgn * stop_frac * abs(target - px)
    k_end = m.lo(t_end)
    for k in range(f, k_end):
        o, h, l = m.o[k], m.h[k], m.l[k]
        if sgn > 0:
            if l <= stop:
                return (min(o, stop) - px) / px * 100.0, "stop"
            if k > f and h >= target:
                return (target - px) / px * 100.0, "target"
        else:
            if h >= stop:
                return (px - max(o, stop)) / px * 100.0, "stop"
            if k > f and l <= target:
                return (px - target) / px * 100.0, "target"
    return sgn * (close_end - px) / px * 100.0, "time"


def tf_index(bars, tf_ms, t):
    """Index of the tf bar containing time t (bars sorted by start), or None."""
    lo, hi = 0, len(bars)
    while lo < hi:
        mid = (lo + hi) // 2
        if bars[mid]["t"] <= t:
            lo = mid + 1
        else:
            hi = mid
    j = lo - 1
    return j if j >= 0 and t < bars[j]["t"] + tf_ms else None


# ------------------------------------------------------------------------------------------ arm BB
def bb_symbol(sym, regime_at, m):
    bars = bb10.load(sym, "15m")
    tags = lvl.session_range_tags(bars, bb10.TF_MS)
    evs = prev.find_events(bars, bb10.TF_MS)
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    out = []
    for e in evs:
        if not (OOS_START <= e["t_close"] < OOS_END):
            continue
        e["session"] = rk.session_tag(e["t_close"] / 1000)
        e["tag"] = tags[e["i"]]
        e["regime"] = regime_at(e["t_close"]) or "none"
        if not (e["tag"] and e["regime"] == "range" and e["session"] in BB_SESS):
            continue
        i, sgn = e["i"], e["side"]
        atr = lvl.atr14(ohlc, i)
        if atr != atr:
            continue
        r = None                                                   # re-entry bar: same rule as lvl.level_arm_fill step 1
        for b in range(i + 1, min(i + lvl.M_REENTER, len(ohlc) - 1) + 1):
            c = ohlc[b][3]
            if (sgn > 0 and c > e["level"]) or (sgn < 0 and c < e["level"]):
                r = b
                break
        if r is None:
            continue
        for k in BB_K:
            L = e["level"] + sgn * k * atr
            row = dict(sym=sym, arm="BB", session=e["session"], k=k, side=sgn, day=int(e["t_close"] // DAY), t=e["t_close"],
                       t0=None, m=None, tk=None)
            # taker baseline T0 = the parent exactly (15m touch fill, 15m bracket)
            fill = lvl.level_arm_fill(ohlc, i, sgn, e["level"], k, atr)
            if fill is not None:
                j, px = fill
                g = prev.bracket_trade(ohlc, j, px, sgn, e["target"])
                if g is not None:
                    row["t0"] = dict(gross=g, day=int(bars[j]["t"] // DAY), t=bars[j]["t"], stop_pct=prev.STOP_FRAC * abs(e["target"] - px) / px * 100.0)
            # maker model M and the 1m-resolution touch control TK
            t_start = bars[r]["t"] + bb10.TF_MS
            t_stop = t_start + lvl.N_TOUCH * bb10.TF_MS
            for key, thr in (("m", True), ("tk", False)):
                if thr:
                    f = limit_fill(m, t_start, t_stop, L, sgn)
                else:                                              # touch fill at the limit (the parent's rule at 1m): level reached, fill at L
                    a, b2 = m.lo(t_start), m.lo(t_stop)
                    hit = np.nonzero(m.l[a:b2] <= L)[0] if sgn > 0 else np.nonzero(m.h[a:b2] >= L)[0]
                    f = a + int(hit[0]) if len(hit) else None
                if f is None:
                    continue
                j = tf_index(bars, bb10.TF_MS, int(m.t[f]))
                if j is None or j + prev.K_BARS >= len(bars):
                    continue
                t_end = bars[j + prev.K_BARS]["t"] + bb10.TF_MS
                res = bracket_1m(m, f, L, sgn, e["target"], prev.STOP_FRAC, t_end, bars[j + prev.K_BARS]["c"])
                if res is None:
                    continue
                row[key] = dict(gross=res[0], exit=res[1], day=int(m.t[f] // DAY), t=int(m.t[f]),
                                stop_pct=prev.STOP_FRAC * abs(e["target"] - L) / L * 100.0)
            out.append(row)
    return out


# ------------------------------------------------------------------------------------------ arm WT
def wt_symbol(sym, per_sym, m):
    out = []
    for tf in WT_TFS:
        r = per_sym[tf]
        bars, tf_ms = r["bars"], base.TF_MS[tf]
        ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
        for sname, sgn in WT_SIDES.items():
            for conf in WT_CONFS:
                for e in r["ev"][(sname, conf)]:
                    if not (OOS_START <= e["t_close"] < OOS_END) or not base.event_in_gate(e["ctx"], sgn, "with"):
                        continue
                    i = e["i"]
                    L = base.level_of(bars[i])
                    row = dict(sym=sym, arm="WT", tf=tf, conf=conf, side=sname, sgn=sgn, day=int(e["t_close"] // DAY), t=e["t_close"], t0=None, m=None)
                    fill = rk.retest_entry(ohlc, i, L, sgn, base.RETEST_N)
                    if fill is not None:
                        j = fill[0]
                        if j + base.H < len(bars):
                            px = fill[1]
                            row["t0"] = dict(gross=sgn * (bars[j + base.H]["c"] - px) / px * 100.0, day=int(bars[j]["t"] // DAY), t=bars[j]["t"])
                    t_start = bars[i]["t"] + tf_ms
                    f = limit_fill(m, t_start, t_start + base.RETEST_N * tf_ms, L, sgn)
                    if f is not None:
                        j = tf_index(bars, tf_ms, int(m.t[f]))
                        if j is not None and j + base.H < len(bars):
                            row["m"] = dict(gross=sgn * (bars[j + base.H]["c"] - L) / L * 100.0, exit="time", day=int(m.t[f] // DAY), t=int(m.t[f]))
                    out.append(row)
    return out


# ------------------------------------------------------------------------------------------ statistics
def stats(trs, cost_pct):
    if not trs:
        return dict(n=0, days=0)
    g = np.array([x["gross"] for x in trs])
    day = [x["day"] for x in trs]
    net = g - cost_pct
    m_, se = rk.cluster_mean_se(net, day)
    t = rk.t_stat(m_, se) if se == se else float("nan")
    return dict(n=len(g), days=len(set(day)), gross=float(g.mean()), net=m_, se=se, t=t, p=rk.norm_p_two(t) if t == t else float("nan"),
                ci_lo=m_ - 1.96 * se, ci_hi=m_ + 1.96 * se, win=float((net > 0).mean()))


def cell(rows, pick):
    """One cell: rows (one per signal) -> taker T0 stats, maker M stats, fill rate, adverse selection, net per signal with misses = 0."""
    n_sig = len(rows)
    t0 = [x["t0"] for x in rows if x["t0"]]
    mk = [x["m"] for x in rows if x["m"]]
    out = dict(pick, signals=n_sig)
    s0, sm = stats(t0, TAKER_PCT), stats(mk, MAKER_PCT)
    for pre, s in (("t_", s0), ("m_", sm)):
        for k, v in s.items():
            out["%s%s" % (pre, k)] = v
    out["fill_rate"] = len(mk) / n_sig if n_sig else float("nan")
    out["t0_fill_rate"] = len(t0) / n_sig if n_sig else float("nan")
    both = [x for x in rows if x["m"] and x["t0"]]
    if both:                                   # adverse selection: parent gross over the rows the limit filled minus over all rows the parent filled
        out["adverse_gross"] = float(np.mean([x["t0"]["gross"] for x in both]) - np.mean([x["gross"] for x in t0]))
    if n_sig:
        out["m_net_per_signal"] = float(sum(x["gross"] - MAKER_PCT for x in mk) / n_sig)
        out["t_net_per_signal"] = float(sum(x["gross"] - TAKER_PCT for x in t0) / n_sig)
    if rows and rows[0]["arm"] == "BB":
        tk = [x["tk"] for x in rows if x["tk"]]
        st = stats(tk, TAKER_PCT)
        out["tk_n"], out["tk_net"] = st["n"], st.get("net", float("nan"))
        out["tk_gross"] = st.get("gross", float("nan"))
        out["stop_share_m"] = float(np.mean([x["exit"] == "stop" for x in mk])) if mk else float("nan")
        out["target_share_m"] = float(np.mean([x["exit"] == "target" for x in mk])) if mk else float("nan")
    return out


def subwin(rows, which):
    f = (lambda x: x["m"]["t"] < SPLIT_MS) if which == 1 else (lambda x: x["m"]["t"] >= SPLIT_MS)
    return stats([x["m"] for x in rows if x["m"] and f(x)], MAKER_PCT).get("net", float("nan"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="ps", choices=("count", "run"), required=True)
    ps = ap.parse_args().ps
    regime_at = bb10.regime_fn()
    wk, mo = base.rsi_series(wt10.load("BTC", "1w")), base.rsi_series(wt10.load("BTC", "1M"))
    allrows = []
    for s in SYMS:
        m = M1Data(s)
        print(s, "tick", m.tick, file=sys.stderr, flush=True)
        allrows += bb_symbol(s, regime_at, m)
        ctx = wt10.ctx_for(s, wk, mo)
        allrows += wt_symbol(s, wt10.sym_events(s, ctx, True), m)
    mix = rk.regime_mix_line([regime_at(t) for t in lvl.week_starts(OOS_START, OOS_END)])
    cells = []
    for sess in BB_SESS:
        for k in BB_K:
            sub = [x for x in allrows if x["arm"] == "BB" and x["session"] == sess and x["k"] == k]
            cells.append(dict(cell(sub, dict(arm="BB", cell="%s k=%s" % (sess, k))), w1_net=subwin(sub, 1), w2_net=subwin(sub, 2)))
    for tf in WT_TFS:
        for sname in WT_SIDES:
            for conf in WT_CONFS:
                sub = [x for x in allrows if x["arm"] == "WT" and x["tf"] == tf and x["side"] == sname and x["conf"] == conf]
                cells.append(dict(cell(sub, dict(arm="WT", cell="%s %s %s" % (tf, sname, conf))), w1_net=subwin(sub, 1), w2_net=subwin(sub, 2)))
    if ps == "run":
        ps_ = [c.get("m_p", float("nan")) for c in cells]
        adj = rk.holm([p if p == p else 1.0 for p in ps_], m=M_FAMILY)
        for c, q in zip(cells, adj):
            c["holm_p"] = float(q)
            c["edge"] = bool(c.get("m_n", 0) >= MIN_N and c.get("m_days", 0) >= MIN_DAYS and c.get("m_net", -1) > 0 and q < 0.05
                             and c["w1_net"] == c["w1_net"] and c["w2_net"] == c["w2_net"] and c["w1_net"] > 0 and c["w2_net"] > 0)
        (HERE / "survivors.json").write_text(json.dumps([c["cell"] for c in cells if c["edge"]]))
    name = "counts.csv" if ps == "count" else "cells.csv"
    cols = sorted({k for c in cells for k in c}, key=lambda k: (k not in ("arm", "cell", "signals"), k))
    if ps == "count":
        cols = ["arm", "cell", "signals", "m_n", "m_days", "t_n", "t_days", "fill_rate", "t0_fill_rate"]
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for c in cells:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in c.items()})
    (HERE / "regime_mix.txt").write_text(mix + "\n", encoding="utf-8", newline="\n")
    print(mix)
    for c in cells:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items() if k in ("cell", "signals", "m_n", "t_n", "fill_rate", "t_net", "m_net", "m_p", "holm_p", "adverse_gross", "edge")})


if __name__ == "__main__":
    main()
