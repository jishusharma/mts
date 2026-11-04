"""RSI deep-buy Step H: layer confluence at the RSI low (SPEC.md s2 Step H, SHOT_REVIEW C5; card rsi-deep-confluence).

Vote table, scores, schemes and the keep rule are pre-registered in CONFLUENCE.md (written before any outcome).
Event = Step F event (RSI14 of the event TF closes <= level L after being 3+ above; fill = next open). For every event one causal
vote per voter on the event TF (same) and on the next two TFs up (higher, LAST COMPLETED bar at the signal-bar close only).
NA (warm-up) is never turned into 0. Scoring reuses the Step F machinery (context_tables.py): F0 level-only walk-forward vs a
score cell shrunk to F0, log-loss delta, t over days, Holm over the whole grid, DEV decides, VALIDATION read once.

Run: python confluence.py --pass dev | val | report
Labels. SOURCED: Bollinger n=20 mult=2 population sd (FORMULAS s22), RSI14 Wilder, fee 0.10% (backtest/fees.py), Kurisko bands/levels
(layers/kurisko params), DEV/VAL/HOLDOUT dates. OURS: every vote band/cut (RSI 30/50, taker z 1 and 200 bars, Kurisko 3-bar memory,
divergence pivot 3 / span 100 / memory 20), score buckets, TF ladder.
"""
import argparse
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
import econ_floor as ef  # noqa: E402
import prob_tables as pt  # noqa: E402
import context_tables as ct  # noqa: E402

NA = float("nan")
NOT_IN_DATA = "NOT_IN_DATA"
LADDER = (1, 5, 15, 60, 240, 1440)
TFS = (1, 5, 15, 60)
LEVELS = ct.LEVELS
DAY_MS = 86_400_000
FEE = ef.FEE
PIV_K, PIV_SPAN, DIV_MEM = 3, 100, 20
TAK_WIN, TAK_Z = 200, 1.0
KUR_MEM = 3
SAME_VOTERS = ("V_BB", "V_KUR", "V_TAK", "V_SWP")
HIGH_VOTERS = ("V_RSI", "V_BB", "V_KUR", "V_TAK", "V_SWP", "V_DIV")
ALL_VOTERS = ("V_RSI", "V_BB", "V_KUR", "V_TAK", "V_SWP", "V_DIV")
SCHEMES = (("C_same", "C_high", "C_all") + tuple(f"ADD1_{v}" for v in ALL_VOTERS) + tuple(f"DROP1_{v}" for v in ALL_VOTERS))
FIELDS = ["kind", "tf_min", "outcome", "scheme", "level", "state", "n_events", "n_days", "p_price", "p_rsi", "mean_net_bps",
          "ev_day_bps", "events_per_day", "ll_f0", "ll_ctx", "delta_ll", "t_day", "p_one", "p_holm", "share_ctx", "verdict", "m"]

# layers listed in CONFLUENCE.md without bar-by-bar causal history here
LAYER_STATUS = {
    "wavetrend": NOT_IN_DATA, "trendline": NOT_IN_DATA, "pitchfork": NOT_IN_DATA, "turn_of_candle": NOT_IN_DATA,
    "cryptocred": NOT_IN_DATA, "krown": NOT_IN_DATA, "tom_fabio_orderflow": NOT_IN_DATA, "funding": NOT_IN_DATA,
    "open_interest": NOT_IN_DATA, "oscillator_agreement_count": NOT_IN_DATA,
}


def layer_status(name):
    """NOT_IN_DATA for a layer with no usable causal history; 'voter' for the six implemented voters. Never 0."""
    if name in LAYER_STATUS:
        return LAYER_STATUS[name]
    if name in ALL_VOTERS:
        return "voter"
    raise KeyError(name)


# ---------------------------------------------------------------- scores
def score_votes(votes):
    """Sum of +1/0/-1 votes. Any NA vote (not reporting) makes the score NA (NaN): no zero-filling."""
    v = np.asarray(votes, dtype="float64")
    if len(v) == 0 or np.isnan(v).any():
        return NA
    return float(v.sum())


def bucket_same(s):
    """S <= -1 -> 0; 0 -> 1; 1 -> 2; >= 2 -> 3; NA -> -1."""
    s = np.asarray(s, dtype="float64")
    return np.where(np.isnan(s), -1, np.where(s <= -1, 0, np.where(s == 0, 1, np.where(s == 1, 2, 3)))).astype("int64")


def bucket_total(s):
    """H or T <= -1 -> 0; 0 -> 1; 1..2 -> 2; >= 3 -> 3; NA -> -1."""
    s = np.asarray(s, dtype="float64")
    return np.where(np.isnan(s), -1, np.where(s <= -1, 0, np.where(s == 0, 1, np.where(s <= 2, 2, 3)))).astype("int64")


def bucket_sign(s):
    """<0 -> 0; 0 -> 1; >0 -> 2; NA -> -1."""
    s = np.asarray(s, dtype="float64")
    return np.where(np.isnan(s), -1, np.where(s < 0, 0, np.where(s == 0, 1, 2))).astype("int64")


# ---------------------------------------------------------------- single-voter rules (pure, causal, bar t uses bars <= t)
def vote_rsi(r):
    r = np.asarray(r, dtype="float64")
    return np.where(np.isnan(r), np.nan, np.where(r <= 30.0, 1.0, np.where(r >= 50.0, -1.0, 0.0)))


def vote_bb(close, n=20, mult=2.0):
    import pandas as pd
    c = pd.Series(np.asarray(close, dtype="float64"))
    mid = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    up, lo = (mid + mult * sd).to_numpy(), (mid - mult * sd).to_numpy()
    cc = c.to_numpy()
    out = np.where(cc < lo, 1.0, np.where(cc > up, -1.0, 0.0))
    return np.where(np.isnan(up), np.nan, out)


def vote_taker(share, win=TAK_WIN, z=TAK_Z):
    """z of the bar's taker-buy share vs the previous `win` bars (mean, population sd of those bars)."""
    import pandas as pd
    s = pd.Series(np.asarray(share, dtype="float64"))
    mu = s.rolling(win).mean().shift(1)
    sd = s.rolling(win).std(ddof=0).shift(1)
    zz = ((s - mu) / sd.where(sd > 0)).to_numpy()
    return np.where(np.isnan(zz), np.nan, np.where(zz >= z, 1.0, np.where(zz <= -z, -1.0, 0.0)))


def vote_sweep(high, low, close, pdl, pdh):
    high, low, close, pdl, pdh = (np.asarray(x, dtype="float64") for x in (high, low, close, pdl, pdh))
    up = (low < pdl) & (close > pdl)
    dn = (high > pdh) & (close < pdh)
    out = np.where(up & ~dn, 1.0, np.where(dn & ~up, -1.0, 0.0))
    return np.where(np.isnan(pdl) | np.isnan(pdh), np.nan, out)


def prior_day_levels(t, d_open, d_high, d_low):
    """Previous completed UTC day (low, high) for each bar open time t (NaN when that day is missing)."""
    t, d_open = np.asarray(t, dtype="int64"), np.asarray(d_open, dtype="int64")
    want = (t // DAY_MS - 1) * DAY_MS
    pos = np.searchsorted(d_open, want)
    pos_c = np.minimum(pos, len(d_open) - 1)
    ok = (pos < len(d_open)) & (d_open[pos_c] == want)
    return (np.where(ok, np.asarray(d_low, dtype="float64")[pos_c], np.nan),
            np.where(ok, np.asarray(d_high, dtype="float64")[pos_c], np.nan))


def div_signals(close, rsi, k=PIV_K, span=PIV_SPAN):
    """Per-bar divergence stamps (+1 bullish, -1 bearish, 0 none). A close pivot at j needs bars j-k..j+k, so it is stamped at j+k
    (never at j). Adjacent pivots of the same kind at most `span` bars apart. Bullish = lower price low, higher RSI low; bearish = mirror."""
    close, rsi = np.asarray(close, dtype="float64"), np.asarray(rsi, dtype="float64")
    n = len(close)
    sig = np.zeros(n)
    for kind in (1, -1):
        piv = []
        for j in range(k, n - k):
            if np.isnan(rsi[j]):
                continue
            left, right = close[j - k:j], close[j + 1:j + 1 + k]
            if kind == 1:
                ok = close[j] < left.min() and close[j] <= right.min()
            else:
                ok = close[j] > left.max() and close[j] >= right.max()
            if ok:
                piv.append(j)
        for a, b in zip(piv[:-1], piv[1:]):
            if b - a > span:
                continue
            if kind == 1 and close[b] < close[a] and rsi[b] > rsi[a]:
                sig[b + k] = 1.0
            if kind == -1 and close[b] > close[a] and rsi[b] < rsi[a]:
                sig[b + k] = -1.0
    return sig


def vote_div(close, rsi, mem=DIV_MEM, k=PIV_K, span=PIV_SPAN):
    """Most recent stamp within the last `mem` bars decides (bar t uses stamps <= t)."""
    sig = div_signals(close, rsi, k, span)
    n = len(sig)
    idx = np.where(sig != 0, np.arange(n), -10 ** 9)
    last = np.maximum.accumulate(idx)
    recent = (np.arange(n) - last) <= mem - 1
    out = np.where(recent, sig[np.maximum(last, 0)], 0.0)
    return np.where(np.isnan(np.asarray(rsi, dtype="float64")), np.nan, out)


# ---------------------------------------------------------------- timeframe plumbing
def htf_completed_index(base_open, base_ms, htf_open, htf_ms):
    """Index of the last HTF bar COMPLETED at the signal-bar close time (base open + base_ms); -1 when none."""
    close_t = np.asarray(base_open, dtype="int64") + base_ms
    return np.searchsorted(np.asarray(htf_open, dtype="int64") + htf_ms, close_t, side="right") - 1


def load_klines(paths, cutoff_ms):
    """1m OHLC + volume + taker_buy_volume. Raises if any bar opens at or after cutoff_ms."""
    import pandas as pd
    df = pd.concat([pd.read_csv(p, usecols=["open_time", "open", "high", "low", "close", "volume", "taker_buy_volume"])
                    for p in paths], ignore_index=True)
    t = df["open_time"].to_numpy(dtype="int64")
    if len(t) and t.max() > 10 ** 14:
        t = t // 1000
    if len(t) and t.max() >= cutoff_ms:
        raise ValueError("bar with open >= cutoff refused")
    order = np.argsort(t, kind="stable")
    t = t[order]
    keep = np.r_[True, np.diff(t) > 0]
    out = {"open_time": t[keep]}
    for k in ("open", "high", "low", "close", "volume", "taker_buy_volume"):
        out[k] = df[k].to_numpy(dtype="float64")[order][keep]
    return out


def resample_ext(d1, minutes):
    """ef.resample plus summed volume and taker_buy_volume (same complete-group rule)."""
    out = dict(ef.resample({k: d1[k] for k in ("open_time", "open", "high", "low", "close")}, minutes))
    if minutes == 1:
        out["volume"], out["taker_buy_volume"] = d1["volume"], d1["taker_buy_volume"]
        return out
    g = d1["open_time"] // (minutes * 60_000)
    ug, start, cnt = np.unique(g, return_index=True, return_counts=True)
    start = start[cnt == minutes]
    for k in ("volume", "taker_buy_volume"):
        cs = np.r_[0.0, np.cumsum(d1[k])]
        out[k] = cs[start + minutes] - cs[start]
    return out


def tf_votes(d1, tf, dayl):
    """All voters on every bar of timeframe tf. Returns (bars dict, {voter: float array with NaN = not reporting})."""
    import pandas as pd
    from MyTradingSys.backtest.layers.kurisko import quad_rotation as kq
    d = resample_ext(d1, tf)
    tf_ms = tf * 60_000
    rsi = ef.rsi_series(d["close"])
    v = {"V_RSI": vote_rsi(rsi), "V_BB": vote_bb(d["close"])}
    bars = list(zip(d["open_time"].tolist(), d["high"].tolist(), d["low"].tolist(), d["close"].tolist()))
    lns = kq.lines(bars, tf_ms)
    flag = np.zeros(len(bars))
    for e in kq.detect(lns):
        if e.side == "long":
            flag[e.t] = 1.0
    mem = pd.Series(flag).rolling(KUR_MEM, min_periods=1).max().to_numpy()
    slow = np.asarray(lns[3], dtype="float64")
    v["V_KUR"] = np.where(np.isnan(slow), np.nan, mem)
    share = np.where(d["volume"] > 0, d["taker_buy_volume"] / np.where(d["volume"] > 0, d["volume"], 1.0), np.nan)
    v["V_TAK"] = vote_taker(share)
    pdl, pdh = prior_day_levels(d["open_time"], *dayl)
    v["V_SWP"] = vote_sweep(d["high"], d["low"], d["close"], pdl, pdh)
    v["V_DIV"] = vote_div(d["close"], rsi)
    return d, v


def event_votes(base_tf, ev, base, tfv):
    """For event signal-bar indices ev on base_tf: same dict {voter: votes} and high dict {voter: summed over the two HTFs}."""
    pos = LADDER.index(base_tf)
    htfs = LADDER[pos + 1:pos + 3]
    same = {k: tfv[base_tf][1][k][ev] for k in SAME_VOTERS}
    high = {k: np.zeros(len(ev)) for k in HIGH_VOTERS}
    for h in htfs:
        hd, hv = tfv[h]
        ix = htf_completed_index(base["open_time"][ev], base_tf * 60_000, hd["open_time"], h * 60_000)
        for k in HIGH_VOTERS:
            val = np.where(ix >= 0, hv[k][np.maximum(ix, 0)], np.nan)
            high[k] = high[k] + val
    return same, high


def scheme_states(same, high):
    """dict scheme -> int state array (-1 = not scored). Only full-coverage events are scored (every voter reporting)."""
    S = np.sum([same[k] for k in SAME_VOTERS], axis=0)
    H = np.sum([high[k] for k in HIGH_VOTERS], axis=0)
    tot = {k: high[k] + (same[k] if k in same else 0.0) for k in ALL_VOTERS}
    T = S + H
    full = ~(np.isnan(S) | np.isnan(H))
    out = {"C_same": bucket_same(S), "C_high": bucket_total(H), "C_all": bucket_total(T)}
    for k in ALL_VOTERS:
        out[f"ADD1_{k}"] = bucket_sign(tot[k])
        out[f"DROP1_{k}"] = bucket_total(T - tot[k])
    for s in out:
        out[s] = np.where(full, out[s], -1)
    return out


# ---------------------------------------------------------------- events
def build_events(d, rsi, tf):
    h = max(1, ct.H_MIN // tf)
    t = d["open_time"]
    out = {}
    for L in LEVELS:
        ev = ct.level_events(rsi, L)
        if len(ev) == 0:
            continue
        yp, rp = ct.price_outcome(d["open"], ev, h)
        yr, rr = ct.rsi_race_free(rsi, ev)
        ok = ev + 1 + h < len(d["open"])
        ret = np.full(len(ev), np.nan)
        ret[ok] = d["open"][ev[ok] + 1 + h] / d["open"][ev[ok] + 1] - 1.0 - FEE
        out[L] = {"ev": ev, "t": t[ev], "day": t[ev] // DAY_MS, "y": {"price": yp, "rsi": yr}, "res": {"price": rp, "rsi": rr},
                  "ret": ret, "state": {}}
    return out


@contextmanager
def schemes_active():
    old = ct.SCHEMES
    ct.SCHEMES = SCHEMES
    try:
        yield
    finally:
        ct.SCHEMES = old


def bucket_rows(tf, events, start_ms, end_ms):
    """Descriptive fee-net table by score bucket and level (plus 'ALL' = pooled levels); events inside [start, end), full coverage.
    state 'ALL' = level-only (every covered event of that level)."""
    ndays = (end_ms - start_ms) / DAY_MS
    rows = []
    for L in list(events) + ["ALL"]:
        for s in SCHEMES:
            for sv in (-2, 0, 1, 2, 3):
                ys, rs, rt, dd = [], [], [], []
                for L2, r2 in events.items():
                    if L != "ALL" and L2 != L:
                        continue
                    st = r2["state"][s]
                    base = (r2["t"] >= start_ms) & (r2["t"] < end_ms) & (st >= 0) & ~np.isnan(r2["ret"])
                    m = base if sv == -2 else base & (st == sv)
                    ys.append(r2["y"]["price"][m]); rs.append(r2["y"]["rsi"][m]); rt.append(r2["ret"][m]); dd.append(r2["day"][m])
                y, rr, ret, day = (np.concatenate(x) for x in (ys, rs, rt, dd))
                if len(ret) == 0:
                    continue
                rows.append({"kind": "bucket", "tf_min": tf, "scheme": s, "level": L, "state": "ALL" if sv == -2 else sv,
                             "n_events": len(ret), "n_days": len(np.unique(day)), "p_price": float(np.nanmean(y)),
                             "p_rsi": float(np.nanmean(rr)) if (~np.isnan(rr)).any() else "",
                             "mean_net_bps": float(ret.mean() * 1e4), "ev_day_bps": float(ret.sum() * 1e4 / ndays),
                             "events_per_day": len(ret) / ndays})
    return rows


def run(d1, start_ms, end_ms, m_fixed=None, dev_candidates=None):
    dayd = ef.resample({k: d1[k] for k in ("open_time", "open", "high", "low", "close")}, 1440)
    dayl = (dayd["open_time"], dayd["high"], dayd["low"])
    tfv = {}
    for tf in LADDER:
        tfv[tf] = tf_votes(d1, tf, dayl)
        print(f"votes tf={tf}m done", flush=True)
    rows, allsum, mrows = [], {}, []
    for tf in TFS:
        d, _ = tfv[tf]
        rsi = ef.rsi_series(d["close"])
        events = build_events(d, rsi, tf)
        for L, r in events.items():
            same, high = event_votes(tf, r["ev"], d, tfv)
            r["state"] = scheme_states(same, high)
        with schemes_active():
            if m_fixed is None:
                _, cells0, f0 = ct.score_tf(events, {}, start_ms, end_ms)
                m_by = ct.estimate_m(cells0, f0)
            else:
                m_by = m_fixed[tf]
            recs, cells, f0cells = ct.score_tf(events, m_by, start_ms, end_ms)
        for o in ct.OUTCOMES:
            mrows.append({"kind": "m", "tf_min": tf, "outcome": o, "m": m_by[o]})
        for key, val in ct.summarise(recs).items():
            allsum[(tf,) + key] = val
        rows += bucket_rows(tf, events, start_ms, end_ms)
        print(f"tf={tf}m scored, events {sum(len(r['ev']) for r in events.values())}", flush=True)
    keys = sorted(allsum)
    padj = ct.holm([allsum[k][2] for k in keys])
    summ = []
    for k, pa in zip(keys, padj):
        tf, o, s = k
        mean_ev, t, p, n, nd, share, llf, llc = allsum[k]
        verdict = "candidate" if (mean_ev > 0 and pa < 0.05) else "drop"
        if dev_candidates is not None:
            verdict = "keep" if (dev_candidates.get(k, False) and mean_ev > 0) else "drop"
        summ.append({"kind": "summary", "tf_min": tf, "outcome": o, "scheme": s, "n_events": n, "n_days": nd, "ll_f0": llf,
                     "ll_ctx": llc, "delta_ll": mean_ev, "t_day": t, "p_one": p, "p_holm": pa, "share_ctx": share,
                     "verdict": verdict})
    return mrows + summ + rows


# ---------------------------------------------------------------- driver
def write_csv(rows, path):
    import csv
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ct._fmt(r.get(k, "")) for k in FIELDS})


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
        d1 = load_klines(pt.month_files(a.klines, "2024-06"), ef.CUTOFF_MS)
        pt.assert_dev(d1)
        rows = run(d1, 0, ef.CUTOFF_MS)
        dest = out / "confluence_dev.csv"
    else:
        devp = out / "confluence_dev.csv"
        if not devp.exists():
            raise SystemExit("confluence_dev.csv must be written before the VALIDATION read")
        drows = ct.read_csv(devp)
        m_fixed = {tf: {} for tf in TFS}
        for r in drows:
            if r["kind"] == "m":
                m_fixed[int(r["tf_min"])][r["outcome"]] = float(r["m"])
        cand = {(int(r["tf_min"]), r["outcome"], r["scheme"]): r["verdict"] == "candidate" for r in drows if r["kind"] == "summary"}
        d1 = load_klines(pt.month_files(a.klines, "2025-06"), ct.HOLDOUT_MS)
        pt.assert_val(d1)
        print("dev csv sha256", pt.sha256(devp))
        rows = run(d1, ef.CUTOFF_MS, ct.HOLDOUT_MS, m_fixed=m_fixed, dev_candidates=cand)
        dest = out / "confluence_val.csv"
    write_csv(rows, dest)
    print("rows", len(rows), "->", dest)


def write_report(out):
    """Append the Result section to CONFLUENCE.md (the pre-registered part above '## Result' is kept byte for byte)."""
    dev, val = ct.read_csv(out / "confluence_dev.csv"), ct.read_csv(out / "confluence_val.csv")
    ds = {(int(r["tf_min"]), r["outcome"], r["scheme"]): r for r in dev if r["kind"] == "summary"}
    vs = {(int(r["tf_min"]), r["outcome"], r["scheme"]): r for r in val if r["kind"] == "summary"}
    db = {(int(r["tf_min"]), r["scheme"], r["level"], r["state"]): r for r in dev if r["kind"] == "bucket"}
    vb = {(int(r["tf_min"]), r["scheme"], r["level"], r["state"]): r for r in val if r["kind"] == "bucket"}

    def f(r, k):
        return float(r[k])

    L = ["", "## Result", ""]
    L.append(f"Data: BTCUSDT 1m. DEV = bar open < 2024-07-01 (`confluence_dev.csv`, written and frozen first, sha256 "
             f"`{pt.sha256(out / 'confluence_dev.csv')[:16]}`). VALIDATION = events 2024-07-01..2025-06-30, read once (`confluence_val.csv`); "
             "its parameters (m, candidate list) come from the frozen DEV file. HOLDOUT (2025-07 onward) is refused by the loader and "
             "was never read. Generated by `confluence.py`; test: `test_confluence.py`. Descriptive, not a trading rule; the net-EV columns "
             "are an in-sample bucket description, not a fee-net edge claim.\n")
    cand = [k for k, r in ds.items() if r["verdict"] == "candidate"]
    keep = [k for k in cand if vs.get(k) and vs[k]["verdict"] == "keep"]
    L.append(f"**{len(keep)} of {len(ds)} pre-registered confluence tests are kept** (DEV: delta log-loss > 0 and Holm p < 0.05 over all "
             f"{len(ds)}; then VALIDATION delta log-loss > 0). DEV candidates: {len(cand)}. Everything else: level-only F0 is the answer.\n")
    L.append("delta = mean log-loss of level-only F0 minus mean log-loss of the score-conditioned prediction per scored event (positive = "
             "score better). t over distinct days; p_holm over the full grid.\n")
    L.append("### DEV candidates and their VALIDATION result\n")
    L.append("| RSI TF | outcome | scheme | DEV events | DEV days | DEV delta | DEV t | DEV p_holm | VAL delta | VAL t | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sorted(cand):
        d, v = ds[k], vs.get(k)
        tail = f"{f(v, 'delta_ll'):+.5f} | {f(v, 't_day'):.2f} | {v['verdict']} |" if v else "n/a | n/a | n/a |"
        L.append(f"| {k[0]}m | {k[1]} | {k[2]} | {d['n_events']} | {d['n_days']} | {f(d, 'delta_ll'):+.5f} | {f(d, 't_day'):.2f} | "
                 f"{f(d, 'p_holm'):.4f} | " + tail)
    if not cand:
        L.append("| none | | | | | | | | | | |")
    L.append("\n### Same-TF score vs higher-TF score vs total (price outcome; positive delta = better than level-only)\n")
    L.append("| RSI TF | scheme | DEV delta | DEV t | VAL delta | VAL t |")
    L.append("|---|---|---|---|---|---|")
    for tf in TFS:
        for sc in ("C_same", "C_high", "C_all"):
            d, v = ds.get((tf, "price", sc)), vs.get((tf, "price", sc))
            if d and v:
                L.append(f"| {tf}m | {sc} | {f(d, 'delta_ll'):+.5f} | {f(d, 't_day'):.2f} | {f(v, 'delta_ll'):+.5f} | {f(v, 't_day'):.2f} |")
    L.append("\n### Add-one and drop-one by layer (price outcome, delta log-loss vs level-only)\n")
    L.append("ADD1 = the layer alone (its votes summed over the 3 TFs, 3 states); DROP1 = total score without the layer. A layer moves the "
             "odds most when its ADD1 delta is highest and its DROP1 delta falls furthest below C_all.\n")
    L.append("| layer | " + " | ".join(f"DEV {tf}m | VAL {tf}m" for tf in TFS) + " | mean DEV |")
    L.append("|---|" + "---|" * (2 * len(TFS) + 1))
    best = []
    for v_ in ALL_VOTERS:
        cells, devs = [], []
        for tf in TFS:
            d, v = ds.get((tf, "price", f"ADD1_{v_}")), vs.get((tf, "price", f"ADD1_{v_}"))
            cells += [f"{f(d, 'delta_ll'):+.5f}" if d else "n/a", f"{f(v, 'delta_ll'):+.5f}" if v else "n/a"]
            if d:
                devs.append(f(d, "delta_ll"))
        m = float(np.mean(devs)) if devs else float("nan")
        best.append((m, v_))
        L.append(f"| ADD1 {v_} | " + " | ".join(cells) + f" | {m:+.5f} |")
    L.append("")
    L.append("| layer | " + " | ".join(f"DEV {tf}m DROP1 minus C_all" for tf in TFS) + " |")
    L.append("|---|" + "---|" * len(TFS))
    for v_ in ALL_VOTERS:
        cells = []
        for tf in TFS:
            d, a = ds.get((tf, "price", f"DROP1_{v_}")), ds.get((tf, "price", "C_all"))
            cells.append(f"{f(d, 'delta_ll') - f(a, 'delta_ll'):+.5f}" if d and a else "n/a")
        L.append(f"| DROP1 {v_} | " + " | ".join(cells) + " |")
    best.sort(reverse=True)
    L.append(f"\nLayer with the highest mean DEV ADD1 delta (price outcome): **{best[0][1]}** ({best[0][0]:+.5f}); "
             f"lowest: {best[-1][1]} ({best[-1][0]:+.5f}).\n")
    for title, bk in (("DEV", db), ("VALIDATION", vb)):
        L.append(f"### Score buckets, all levels pooled, fee-net description ({title}; ALL = every covered event = level-only)\n")
        L.append("net = open 60 min after the fill / fill open - 1 - 0.10% fee. ev/day = sum of net over events / calendar days of the "
                 "period (overlapping events of one RSI episode are all counted, so this describes the bucket, not a portfolio).\n")
        L.append("| RSI TF | scheme | bucket | events | days | P(price>fee) | P(RSI bounce) | mean net bp | ev/day bp |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for tf in TFS:
            for sc in ("C_same", "C_high", "C_all"):
                for sv in ("ALL", "0", "1", "2", "3"):
                    r = bk.get((tf, sc, "ALL", sv))
                    if r:
                        pr = f"{f(r, 'p_rsi'):.3f}" if r["p_rsi"] != "" else "n/a"
                        L.append(f"| {tf}m | {sc} | {sv} | {r['n_events']} | {r['n_days']} | {f(r, 'p_price'):.3f} | {pr} | "
                                 f"{f(r, 'mean_net_bps'):+.2f} | {f(r, 'ev_day_bps'):+.1f} |")
        L.append("")
    L.append("## Layers: causal history\n")
    L.append("| layer | causal history |")
    L.append("|---|---|")
    for v_ in ("V_RSI (higher-TF RSI band)", "V_BB Bollinger", "V_KUR Kurisko quad stochastic", "V_TAK taker-buy share",
               "V_SWP prior-day sweep", "V_DIV higher-TF divergence"):
        L.append(f"| {v_} | yes |")
    for k_ in sorted(LAYER_STATUS):
        L.append(f"| {k_} | {LAYER_STATUS[k_]} |")
    L.append("\nMirror for highs (short bias, question 5): not run (exploratory per SPEC Step G mirror rule; does not block). "
             "Standalone layers are mostly no-edge (LAYERS.md), so these votes are features of the state, not signals.\n")
    p = out / "CONFLUENCE.md"
    head = p.read_text().split("\n## Result")[0].rstrip("\n")
    head = head.replace('Results are appended under "Result" after the DEV run.', 'Results are under "Result" at the end.')
    with open(p, "w", newline="\n") as fh:
        fh.write(head + "\n" + "\n".join(L) + "\n")


if __name__ == "__main__":
    main()
