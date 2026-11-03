"""RSI deep-buy Phase 1F: context-conditioned tables, walk-forward (SPEC.md s2 Step F, OPUS_FRAMING s2.2 / s4.3; card rsi-deep-context-tables).

Event: RSI(tf) closes at or below level L after being >= 3 above (hysteresis 3, no window), fill = next bar open; known at the
signal bar close. Two outcomes per event:
  price: open[i+1+H]/open[i+1]-1 > fee, H = 60 minutes (H = 60/tf bars)
  rsi  : RSI rises 5 points off its running minimum before that minimum is 3 below the entry RSI, within 60 bars (else excluded)
Predictors, all walk-forward (an event's probability uses only events whose outcome was resolved at or before its signal bar):
  F0   unconditional cell (tf, level): (k+1)/(n+2) on the resolved past events.
  F1   macro phase, 3 schemes x 3 states (trend, vol, range), from COMPLETED daily bars, labels NA before 2023-01-01 (2022 = warm-up).
  F2   trailing context per window L in 4h,6h,12h,1d,3d,1w: floor-gap state, touch-count state, bounce-record state (relative coordinates).
  Each context cell is shrunk to its parent F0 value by empirical Bayes, p = (k + m*p0)/(n + m); a cell with < 30 distinct past days
  returns the parent value. m = beta-binomial method-of-moments strength estimated once on DEV cells (OURS).
Comparison: per (tf, outcome, scheme) mean log-loss improvement of context over F0 over the scored events, t over distinct days, one-sided
normal p, Holm over the whole grid. DEV decides candidates; VALIDATION is read once and keeps a candidate only if it also beats F0 there.

Run: python context_tables.py --pass dev      (writes context_tables_dev.csv; refuses any bar open >= 2024-07-01)
     python context_tables.py --pass val      (needs the frozen dev csv; scores events 2024-07..2025-06 once; refuses >= 2025-07 HOLDOUT)
     python context_tables.py --pass report   (writes CONTEXT_REPORT.md from the two csv files)

Labels. SOURCED: RSI14 Wilder (econ_floor), fee 0.10% round trip (backtest/fees.py), DEV/VALIDATION/HOLDOUT dates (SPEC s5), >= 30
independent days per cell and empirical-Bayes shrinkage to the parent (SPEC Step F guards 2-3), Holm, walk-forward (guards 4-5).
OURS: hysteresis 3, levels 10..40 step 5, H = 60 min, race b=5 d=3 N=60 bars, L grid, floor-gap cut points (0, 3 RSI points), touch buckets
0/1/2+, bounce-record buckets none/<50%/>=50%, macro definitions below (the operator's words have no formula), Laplace parent prior,
m clamp [2, 5000], tf grid 1m/5m/15m/1h.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import econ_floor as ef  # noqa: E402
import prob_tables as pt  # noqa: E402

CUTOFF_MS = ef.CUTOFF_MS
HOLDOUT_MS = pt.HOLDOUT_MS
LABEL_START_MS = int(np.datetime64("2023-01-01T00:00", "ms").astype("int64"))
FEE = ef.FEE
DAY_MS = 86_400_000
TFS = (1, 5, 15, 60)
LEVELS = (10, 15, 20, 25, 30, 35, 40)
HYST = 3.0
H_MIN = 60
RACE_B, RACE_D, RACE_N = 5.0, 3.0, 60
LOOKBACKS = (240, 360, 720, 1440, 4320, 10080)          # minutes: 4h 6h 12h 1d 3d 1w
MIN_DAYS = 30
M_CLAMP = (2.0, 5000.0)
OUTCOMES = ("price", "rsi")
MACRO = ("trend", "vol", "range")
SCHEMES = tuple(f"M_{s}" for s in MACRO) + tuple(f"{f}_{L}" for f in ("floor", "touch", "bounce") for L in LOOKBACKS)
FIELDS = ["kind", "tf_min", "outcome", "scheme", "level", "state", "n_events", "n_days", "k", "p_raw", "p_parent", "p_final",
          "used_ctx", "ll_f0", "ll_ctx", "delta_ll", "t_day", "p_one", "p_holm", "share_ctx", "verdict", "m"]


# ---------------------------------------------------------------- estimators
def shrink(k, n, p0, m):
    """Empirical-Bayes shrinkage of a cell proportion toward its parent: (k + m p0)/(n + m); empty cell = parent."""
    return (k + m * p0) / (n + m) if (n + m) > 0 else p0


def ctx_pred(k, n, days, p0, m):
    """Context cell prediction: parent value when the cell has fewer than MIN_DAYS independent days, else the shrunk value."""
    return p0 if days < MIN_DAYS else shrink(k, n, p0, m)


def eb_strength(ks, ns, p0s):
    """Beta-binomial method-of-moments prior strength m = a + b: Var(phat) = p0 q0 [rho + (1-rho)/n], rho = 1/(m+1).
    Weighted by n; clamped to M_CLAMP."""
    ks, ns, p0s = (np.asarray(x, dtype="float64") for x in (ks, ns, p0s))
    ok = ns > 0
    ks, ns, p0s = ks[ok], ns[ok], p0s[ok]
    if len(ns) < 2:
        return M_CLAMP[1]
    v = float(np.sum(ns * (ks / ns - p0s) ** 2) / ns.sum())
    pq = float(np.sum(ns * p0s * (1 - p0s)) / ns.sum())
    nbar = float(ns.mean())
    if pq <= 0 or nbar <= 1:
        return M_CLAMP[1]
    rho = (v / pq - 1.0 / nbar) / (1.0 - 1.0 / nbar)
    if rho <= 1.0 / (M_CLAMP[1] + 1):
        return M_CLAMP[1]
    return float(min(max(1.0 / min(rho, 1.0) - 1.0, M_CLAMP[0]), M_CLAMP[1]))


def holm(ps):
    ps = np.asarray(ps, dtype="float64")
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0.0
    for rank, j in enumerate(order):
        run = max(run, (len(ps) - rank) * ps[j])
        adj[j] = min(1.0, run)
    return adj.tolist()


def walk_counts(e, res, y, day):
    """For events sorted by signal bar e: (k, n, distinct days) over earlier events with res <= e. Outcome y in {0,1}."""
    e, res, y, day = (np.asarray(x) for x in (e, res, y, day))
    if len(e) == 0:
        z = np.zeros(0, dtype="int64")
        return z, z, z
    order = np.argsort(res, kind="stable")
    sres = res[order]
    cnt = np.searchsorted(sres, e, side="right")
    cumk = np.r_[0, np.cumsum(y[order])]
    dd = day[order]
    _, first = np.unique(dd, return_index=True)
    flag = np.zeros(len(dd), dtype="int64")
    flag[first] = 1
    cumd = np.r_[0, np.cumsum(flag)]
    return cumk[cnt].astype("int64"), cnt.astype("int64"), cumd[cnt].astype("int64")


# ---------------------------------------------------------------- macro phase (daily, completed bars only)
def _rank_prior(x, min_prior):
    """Percentile rank of x[u] among x[:u] (strictly earlier values); -1 where fewer than min_prior finite priors."""
    out = np.full(len(x), -1.0)
    seen = []
    import bisect
    for u, v in enumerate(x):
        if len(seen) >= min_prior and np.isfinite(v):
            out[u] = bisect.bisect_left(seen, v) / len(seen)
        if np.isfinite(v):
            bisect.insort(seen, v)
    return out


def macro_labels(dopen, close, high, low):
    """Per daily bar u, labels from days <= u-1 only. -1 = NA. States 0..2. Days opening before 2023-01-01 are always NA.
    trend: 0 down (ret30<0 and close<MA200), 2 up (ret30>0 and close>MA200), 1 mixed.
    vol  : tercile of the 30d realised vol of daily log returns against its own expanding history.
    range: tercile of the 30d range width (high-low)/close against its own expanding history (low = consolidation)."""
    dopen, close, high, low = (np.asarray(x, dtype="float64") for x in (dopen, close, high, low))
    n = len(close)
    trend = np.full(n, -1, dtype="int64")
    vol = np.full(n, -1, dtype="int64")
    rng = np.full(n, -1, dtype="int64")
    lr = np.r_[np.nan, np.diff(np.log(close))]
    rv = np.full(n, np.nan)
    wd = np.full(n, np.nan)
    for j in range(30, n):                 # features known AFTER day j closes
        rv[j] = np.std(lr[j - 29:j + 1], ddof=1)
        wd[j] = (high[j - 29:j + 1].max() - low[j - 29:j + 1].min()) / close[j]
    rv_rank = _rank_prior(rv, 60)
    wd_rank = _rank_prior(wd, 300)
    for u in range(1, n):
        if dopen[u] < LABEL_START_MS:
            continue
        j = u - 1                          # last completed day
        if j >= 200:
            ret30 = close[j] / close[j - 30] - 1.0
            ma = close[j - 199:j + 1].mean()
            trend[u] = 0 if (ret30 < 0 and close[j] < ma) else (2 if (ret30 > 0 and close[j] > ma) else 1)
        if rv_rank[j] >= 0:
            vol[u] = min(int(rv_rank[j] * 3), 2)
        if wd_rank[j] >= 0:
            rng[u] = min(int(wd_rank[j] * 3), 2)
    return {"trend": trend, "vol": vol, "range": rng}


# ---------------------------------------------------------------- trailing context (F2)
def lbars_for(tf, minutes):
    return max(1, minutes // tf)


def trailing_features(rsi, ev, res, y, tf, lbars):
    """Per event (signal bar index ev, outcome resolved at bar res with value y), from data strictly before the event:
    floor_state: RSI at the event minus the lowest RSI over the previous lbars bars: 0 below the floor (new low), 1 within 3 points, 2 above, -1 NA
    touch_state: earlier events of this level inside the window: 0, 1, 2+
    bounce_state: of those earlier events whose outcome was resolved by the event bar: 0 none, 1 share < 0.5, 2 share >= 0.5
    returns (floor_state, touch_state, bounce_state, floor value)."""
    import pandas as pd
    rsi = np.asarray(rsi, dtype="float64")
    ev, res, y = np.asarray(ev, dtype="int64"), np.asarray(res, dtype="int64"), np.asarray(y, dtype="float64")
    fl = pd.Series(rsi).rolling(lbars, min_periods=max(1, (lbars * 3) // 4)).min().shift(1).to_numpy()
    floor = fl[ev]
    gap = rsi[ev] - floor
    fs = np.where(np.isnan(gap), -1, np.where(gap < 0, 0, np.where(gap <= 3.0, 1, 2))).astype("int64")
    lo = np.searchsorted(ev, ev - lbars, side="right")        # first earlier event with ev_k > ev_j - lbars
    tcount = np.arange(len(ev)) - lo
    ts = np.minimum(tcount, 2).astype("int64")
    bs = np.zeros(len(ev), dtype="int64")
    for j in range(len(ev)):
        if tcount[j] <= 0:
            continue
        sl = slice(lo[j], j)
        done = res[sl] <= ev[j]
        yy = y[sl][done & ~np.isnan(y[sl])]
        if len(yy):
            bs[j] = 2 if yy.mean() >= 0.5 else 1
    return fs, ts, bs, floor


# ---------------------------------------------------------------- events and outcomes
def level_events(rsi, level):
    wid = np.zeros(len(rsi), dtype="int64")
    idx, _ = pt.visit_events(rsi, wid, float(level), HYST)
    return idx


def rsi_race_free(rsi, ev, b=RACE_B, d=RACE_D, n_max=RACE_N):
    """(outcome 1/0/nan, resolve bar). 1 = RSI rose b off its running minimum first, 0 = running minimum fell d below the entry RSI first."""
    out = np.full(len(ev), np.nan)
    res = np.full(len(ev), -1, dtype="int64")
    n = len(rsi)
    for q, i in enumerate(ev):
        e0 = rsi[i]
        m = e0
        for j in range(i + 1, min(n, i + 1 + n_max)):
            if np.isnan(rsi[j]):
                break
            if rsi[j] >= m + b:
                out[q], res[q] = 1.0, j
                break
            m = min(m, rsi[j])
            if m <= e0 - d:
                out[q], res[q] = 0.0, j
                break
    return out, res


def price_outcome(open_, ev, h):
    n = len(open_)
    ok = ev + 1 + h < n
    y = np.full(len(ev), np.nan)
    res = np.where(ok, ev + 1 + h, -1)
    e = ev[ok]
    y[ok] = (open_[e + 1 + h] / open_[e + 1] - 1.0 > FEE).astype("float64")
    return y, res


def daily_bars(d1):
    d = ef.resample(d1, 1440)
    return d["open_time"], d["close"], d["high"], d["low"]


def build_events(d1, tf):
    """All per-event arrays for one RSI timeframe: dict level -> dict of arrays."""
    d = ef.resample(d1, tf)
    rsi = ef.rsi_series(d["close"])
    t = d["open_time"]
    dopen, dclose, dhigh, dlow = daily_bars(d1)
    lab = macro_labels(dopen, dclose, dhigh, dlow)
    dayidx = {int(v): i for i, v in enumerate(dopen // DAY_MS)}
    h = max(1, H_MIN // tf)
    out = {}
    for L in LEVELS:
        ev = level_events(rsi, L)
        if len(ev) == 0:
            continue
        yp, rp = price_outcome(d["open"], ev, h)
        yr, rr = rsi_race_free(rsi, ev)
        evday = t[ev] // DAY_MS
        rec = {"ev": ev, "t": t[ev], "day": evday, "y": {"price": yp, "rsi": yr}, "res": {"price": rp, "rsi": rr}, "state": {}}
        for s in MACRO:
            st = np.array([lab[s][dayidx[int(dd)]] if int(dd) in dayidx else -1 for dd in evday], dtype="int64")
            rec["state"][f"M_{s}"] = st
        # trailing features use the price outcome as the bounce record (resolved at its exit bar)
        okp = ~np.isnan(yp)
        for Lm in LOOKBACKS:
            fs, ts, bs, _ = trailing_features(rsi, ev, np.where(okp, rp, 10 ** 12), yp, tf, lbars_for(tf, Lm))
            rec["state"][f"floor_{Lm}"], rec["state"][f"touch_{Lm}"], rec["state"][f"bounce_{Lm}"] = fs, ts, bs
        out[L] = rec
    return out


# ---------------------------------------------------------------- scoring
def _ll(p, y):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def score_tf(events, m_by, start_ms, end_ms):
    """Walk-forward predictions for one tf. Returns (records, cells): records[(outcome, scheme)] = list of (day, ll_f0, ll_ctx, used);
    cells[(outcome, scheme, level, state)] = (k, n, days) FINAL counts over all valid events; f0cells[(outcome, level)] likewise."""
    recs = {(o, s): [] for o in OUTCOMES for s in SCHEMES}
    cells, f0cells = {}, {}
    for L, r in events.items():
        for o in OUTCOMES:
            y, res = r["y"][o], r["res"][o]
            v = ~np.isnan(y)
            if v.sum() == 0:
                continue
            e, rs, yy, dd, tt = r["ev"][v], res[v], y[v], r["day"][v], r["t"][v]
            k0, n0, d0 = walk_counts(e, rs, yy, dd)
            p0 = (k0 + 1.0) / (n0 + 2.0)
            f0cells[(o, L)] = (int(yy.sum()), len(yy), len(np.unique(dd)))
            sc = (tt >= start_ms) & (tt < end_ms)
            m = m_by.get(o, M_CLAMP[1])
            for s in SCHEMES:
                st = r["state"][s][v]
                pc = p0.copy()
                used = np.zeros(len(e), dtype=bool)
                for sv in np.unique(st[st >= 0]):
                    mk = st == sv
                    kk, nn, dy = walk_counts(e[mk], rs[mk], yy[mk], dd[mk])
                    pcs = np.array([ctx_pred(a, b, c, q, m) for a, b, c, q in zip(kk, nn, dy, p0[mk])])
                    pc[mk] = pcs
                    used[mk] = dy >= MIN_DAYS
                    cells[(o, s, L, int(sv))] = (int(yy[mk].sum()), int(mk.sum()), len(np.unique(dd[mk])))
                pick = sc & (st >= 0)
                if pick.any():
                    recs[(o, s)].extend(zip(dd[pick].tolist(), _ll(p0[pick], yy[pick]).tolist(),
                                            _ll(pc[pick], yy[pick]).tolist(), used[pick].tolist()))
    return recs, cells, f0cells


def estimate_m(cells, f0cells):
    """Per outcome: pooled beta-binomial strength over final DEV cells with >= MIN_DAYS days."""
    m_by = {}
    for o in OUTCOMES:
        ks, ns, ps = [], [], []
        for (oo, s, L, sv), (k, n, dy) in cells.items():
            if oo != o or dy < MIN_DAYS or (o, L) not in f0cells:
                continue
            k0, n0, _ = f0cells[(o, L)]
            ks.append(k); ns.append(n); ps.append((k0 + 1.0) / (n0 + 2.0))
        m_by[o] = eb_strength(ks, ns, ps) if ks else M_CLAMP[1]
    return m_by


def summarise(recs):
    """(delta mean, t over days, one-sided p, n events, n days, share using context) per key."""
    out = {}
    for key, lst in recs.items():
        if not lst:
            continue
        a = np.array([(x[0], x[1] - x[2], x[3]) for x in lst], dtype="float64")
        days, inv = np.unique(a[:, 0], return_inverse=True)
        dsum = np.bincount(inv, weights=a[:, 1])
        nd = len(days)
        mean_ev = float(a[:, 1].mean())
        if nd > 1 and dsum.std(ddof=1) > 0:
            t = float(dsum.mean() / (dsum.std(ddof=1) / math.sqrt(nd)))
        else:
            t = 0.0
        p = 0.5 * math.erfc(t / math.sqrt(2))          # one-sided: context better than F0
        out[key] = (mean_ev, t, p, len(lst), nd, float(a[:, 2].mean()), float(np.mean([x[1] for x in lst])),
                    float(np.mean([x[2] for x in lst])))
    return out


# ---------------------------------------------------------------- driver
def _fmt(v):
    return f"{v:.6g}" if isinstance(v, (float, np.floating)) else v


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: _fmt(r.get(k, "")) for k in FIELDS})


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def run(d1, start_ms, end_ms, m_fixed=None, dev_candidates=None):
    rows = []
    allsum = {}
    cellrows = []
    mrows = []
    for tf in TFS:
        ev = build_events(d1, tf)
        recs0, cells0, f0 = score_tf(ev, {}, start_ms, end_ms) if m_fixed is None else (None, None, None)
        m_by = estimate_m(cells0, f0) if m_fixed is None else m_fixed[tf]
        recs, cells, f0cells = score_tf(ev, m_by, start_ms, end_ms)
        for o in OUTCOMES:
            mrows.append({"kind": "m", "tf_min": tf, "outcome": o, "m": m_by[o]})
        for key, val in summarise(recs).items():
            allsum[(tf,) + key] = val
        for (o, s, L, sv), (k, n, dy) in cells.items():
            k0, n0, d0 = f0cells[(o, L)]
            p0 = (k0 + 1.0) / (n0 + 2.0)
            used = dy >= MIN_DAYS
            cellrows.append({"kind": "cell", "tf_min": tf, "outcome": o, "scheme": s, "level": L, "state": sv, "n_events": n,
                             "n_days": dy, "k": k, "p_raw": k / n if n else "", "p_parent": p0,
                             "p_final": ctx_pred(k, n, dy, p0, m_by[o]), "used_ctx": int(used)})
        print(f"tf={tf}m done: events {sum(len(r['ev']) for r in ev.values())}, cells {len(cells)}", flush=True)
    keys = sorted(allsum)
    padj = holm([allsum[k][2] for k in keys])
    for k, pa in zip(keys, padj):
        tf, o, s = k
        mean_ev, t, p, n, nd, share, llf, llc = allsum[k]
        cand = (mean_ev > 0 and pa < 0.05)
        verdict = ("candidate" if cand else "drop")
        if dev_candidates is not None:
            verdict = "keep" if (dev_candidates.get(k, False) and mean_ev > 0) else "drop"
        rows.append({"kind": "summary", "tf_min": tf, "outcome": o, "scheme": s, "n_events": n, "n_days": nd, "ll_f0": llf,
                     "ll_ctx": llc, "delta_ll": mean_ev, "t_day": t, "p_one": p, "p_holm": pa, "share_ctx": share,
                     "verdict": verdict})
    return mrows + rows + cellrows


def write_report(out):
    dev, val = read_csv(out / "context_tables_dev.csv"), read_csv(out / "context_tables_val.csv")
    ds = {(int(r["tf_min"]), r["outcome"], r["scheme"]): r for r in dev if r["kind"] == "summary"}
    vs = {(int(r["tf_min"]), r["outcome"], r["scheme"]): r for r in val if r["kind"] == "summary"}

    def f(r, k):
        return float(r[k])

    L = ["# RSI deep-buy Phase 1F: context-conditioned tables (card rsi-deep-context-tables, SPEC s2 Step F)\n"]
    L.append("Data: BTCUSDT 1m. DEV = bar open < 2024-07-01 (`context_tables_dev.csv`, written and frozen first, sha256 "
             f"`{pt.sha256(out / 'context_tables_dev.csv')[:16]}`). VALIDATION = events 2024-07-01..2025-06-30, read once "
             "(`context_tables_val.csv`); its parameters (m, candidate list) come from the frozen DEV file. HOLDOUT (2025-07 onward) is "
             "refused by the loader and was never read. Generated by `context_tables.py`; test: `test_context_tables.py`. "
             "Descriptive probabilities, not a trading rule; no fee-net edge is claimed.\n")
    L.append("## What was built\n")
    L.append("Event = RSI(tf) closes at or below level L (10..40 step 5) after being 3+ above; fill = next bar open. Two outcomes: "
             "`price` = open 60 minutes after the fill exceeds the fill by more than the 0.10% round-trip fee; `rsi` = RSI rises 5 points "
             "off its running minimum before that minimum is 3 below the entry RSI, within 60 bars (unresolved events excluded). "
             "F0 (unconditional baseline, the table of `PROB_REPORT.md` made walk-forward) = (k+1)/(n+2) on the earlier events of the same "
             "(tf, level) whose outcome was already resolved. A context cell (scheme, state, tf, level) is shrunk to that F0 value, "
             "p = (k + m p0)/(n + m), and returns the F0 value while it has fewer than 30 distinct past days. "
             "Every prediction uses only events resolved at or before its signal bar (walk-forward, so VALIDATION is a forward test of the whole pipeline).\n")
    L.append("Context schemes (21): macro `M_trend` (30d return sign and close vs 200d mean: down / mixed / up), `M_vol` (tercile of 30d realised "
             "vol against its own expanding history), `M_range` (tercile of the 30d range width against its own history; low = consolidation); "
             "all from the last COMPLETED daily bar, NA before 2023-01-01 (2022 is warm-up). Trailing context per lookback 4h, 6h, 12h, 1d, 3d, 1w: "
             "`floor_L` (event RSI minus the lowest RSI of the previous L: below the floor = new regime / within 3 points / more than 3 above), "
             "`touch_L` (earlier events of that level inside L: 0 / 1 / 2+), `bounce_L` (of those, the share whose price bounce beat the fee and was "
             "already resolved: none / under 50% / 50% or more).\n")
    L.append("## Prior strength m (empirical Bayes, beta-binomial method of moments on the final DEV cells; clamp 2..5000)\n")
    L.append("| RSI TF | outcome | m |\n|---|---|---|")
    for r in dev:
        if r["kind"] == "m":
            L.append(f"| {r['tf_min']}m | {r['outcome']} | {float(r['m']):.1f} |")
    L.append("\nm at the upper clamp (5000) means the context cells are not more spread out around their parent than chance allows: "
             "shrinkage then returns almost exactly the parent.\n")
    cand = [k for k, r in ds.items() if r["verdict"] == "candidate"]
    keep = [k for k, r in vs.items() if r["verdict"] == "keep"]
    L.append(f"## Result\n\n**{len(keep)} of {len(ds)} pre-registered context tests are kept** (DEV: delta log-loss > 0 and Holm p < 0.05 over all {len(ds)}; "
             f"then VALIDATION delta log-loss > 0). DEV candidates: {len(cand)}. Everything else: F0 is the answer.\n")
    kt = [f(vs[k], "t_day") for k in keep]
    L.append(f"Read this honestly: `keep` only means the VALIDATION delta is above 0, as the card's rule asks. The kept contexts' VALIDATION t over days "
             f"is {', '.join(f'{x:.2f}' for x in kt) if kt else 'n/a'} (none reaches 2) and the gains are a few 1e-4 nats of log-loss per event, "
             "so no context is a material improvement over F0; F0 stays the working table and a kept context is a candidate for the next "
             "card's fee-net EV check, not a rule.\n")
    L.append("delta = mean log-loss of F0 minus mean log-loss of the context prediction per scored event (positive = context better). "
             "t = over distinct days (events of a day cluster); p one-sided normal; p_holm over the full grid. share_ctx = scored events that had "
             ">= 30 context days (the rest fell back to the parent).\n")
    L.append("### DEV candidates and their VALIDATION result\n")
    L.append("| RSI TF | outcome | scheme | DEV events | DEV days | DEV delta | DEV t | DEV p_holm | VAL events | VAL days | VAL delta | VAL t | verdict |\n"
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sorted(cand, key=lambda k: -f(ds[k], "delta_ll")):
        a, b = ds[k], vs.get(k)
        bv = (f"{b['n_events']} | {b['n_days']} | {f(b, 'delta_ll'):+.5f} | {f(b, 't_day'):.2f} | {b['verdict']}" if b
              else "n/a | n/a | n/a | n/a | n/a")
        L.append(f"| {k[0]}m | {k[1]} | {k[2]} | {a['n_events']} | {a['n_days']} | {f(a, 'delta_ll'):+.5f} | {f(a, 't_day'):.2f} | "
                 f"{f(a, 'p_holm'):.4f} | {bv} |")
    L.append("\n### Largest VALIDATION deltas (top 12, any scheme; DEV verdict shown)\n")
    L.append("| RSI TF | outcome | scheme | VAL events | VAL days | VAL delta | VAL t | DEV delta | DEV verdict |\n|---|---|---|---|---|---|---|---|---|")
    for k in sorted(vs, key=lambda k: -f(vs[k], "delta_ll"))[:12]:
        b, a = vs[k], ds.get(k)
        dd = f"{f(a, 'delta_ll'):+.5f}" if a else "n/a"
        L.append(f"| {k[0]}m | {k[1]} | {k[2]} | {b['n_events']} | {b['n_days']} | {f(b, 'delta_ll'):+.5f} | {f(b, 't_day'):.2f} | "
                 f"{dd} | {a['verdict'] if a else 'n/a'} |")
    n_pos = sum(1 for r in vs.values() if f(r, "delta_ll") > 0)
    L.append(f"\nVALIDATION: {n_pos} of {len(vs)} tests have delta > 0 (about half is chance); "
             f"DEV: {sum(1 for r in ds.values() if f(r, 'delta_ll') > 0)} of {len(ds)}.\n")
    cells_dev = [r for r in dev if r["kind"] == "cell"]
    used = sum(1 for r in cells_dev if r["used_ctx"] == "1")
    L.append(f"## Cells\n\nDEV context cells with at least one event: {len(cells_dev)}; with >= {MIN_DAYS} independent days (own estimate used): {used}; "
             f"the other {len(cells_dev) - used} return their parent (F0) value. Per-cell rows (raw, parent, final shrunk probability, n, days) "
             "are in the two CSV files (`kind=cell`).\n")
    L.append("## Parameters (SOURCED vs OURS)\n")
    L.append("SOURCED: RSI14 Wilder on close, UTC (econ_floor.py, FORMULAS.md s1); fee 0.10% round trip (backtest/fees.py); DEV/VALIDATION/HOLDOUT dates "
             "(SPEC s5); >= 30 independent days per cell, empirical-Bayes shrinkage to the parent, Holm over the grid, walk-forward estimation, "
             "VALIDATION read once (SPEC Step F guards).\n\n"
             "OURS (all in the trial ledger layer_lab/TRIALS.md, none tuned on VALIDATION): hysteresis 3; levels 10..40 step 5; price horizon 60 minutes; "
             "RSI race b=5, d=3, N=60 bars; macro definitions and cut points (terciles of own history, 200d mean, 30d windows); lookbacks 4h..1w; "
             "floor-gap cut points 0 and 3 RSI points; touch and bounce-record buckets; Laplace parent (k+1)/(n+2); m by method of moments "
             "(clamp 2..5000, estimated on DEV only); TFs 1m/5m/15m/1h.\n")
    L.append("## Caveats\n")
    L.append("- Look-ahead: every feature uses data strictly before the event bar (trailing floor shifted one bar, macro labels from the last completed day, "
             "bounce record only from outcomes resolved at or before the signal bar); tests plant a future bar and require unchanged output.\n"
             "- The bounce-record feature uses the price outcome for both outcome tables.\n"
             "- NOT built here: the memory-length comparison of SPEC Step F (expanding vs 1y/90d/30d P_touch calibration) and the fee-net EV comparison; "
             "this card compares log-loss only.\n"
             "- Macro labels need about 330 days of history for the range scheme; 2022 is warm-up, so all scored events are 2023-01 or later.\n"
             "- Holm counts the 168 summary tests; per-cell rows are not tests. About 5% of unadjusted tests are positive by chance.\n")
    Path(out / "CONTEXT_REPORT.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("wrote CONTEXT_REPORT.md", len(keep), "kept of", len(ds))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="which", choices=("dev", "val", "report"), required=True)
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.which == "report":
        write_report(out)
        return
    if a.which == "dev":
        d1 = ef.load_klines(pt.month_files(a.klines, "2024-06"))
        pt.assert_dev(d1)
        rows = run(d1, 0, CUTOFF_MS)
        dest = out / "context_tables_dev.csv"
    else:
        devp = out / "context_tables_dev.csv"
        if not devp.exists():
            raise SystemExit("context_tables_dev.csv must be written before the VALIDATION read")
        drows = read_csv(devp)
        m_fixed = {tf: {} for tf in TFS}
        for r in drows:
            if r["kind"] == "m":
                m_fixed[int(r["tf_min"])][r["outcome"]] = float(r["m"])
        cand = {(int(r["tf_min"]), r["outcome"], r["scheme"]): r["verdict"] == "candidate" for r in drows if r["kind"] == "summary"}
        d1 = ef.load_klines(pt.month_files(a.klines, "2025-06"), cutoff_ms=HOLDOUT_MS)
        pt.assert_val(d1)
        print("dev csv sha256", pt.sha256(devp))
        rows = run(d1, CUTOFF_MS, HOLDOUT_MS, m_fixed=m_fixed, dev_candidates=cand)
        dest = out / "context_tables_val.csv"
    write_csv(rows, dest)
    print("rows", len(rows), "->", dest)


if __name__ == "__main__":
    main()
