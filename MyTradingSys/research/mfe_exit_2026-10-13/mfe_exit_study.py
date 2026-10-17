"""MFE-based exit study (card: reverse-engineer exits from the peak-profit point), 2026-10-13.

Two separate questions, reported separately:
  1. ENTRY QUALITY: gross (pre-fee) return of the fires at a fixed time exit, MFE and MAE.
  2. EXIT CAPTURE: how much of the MFE a causal exit rule keeps, fee-net.

Look-ahead rules in this file:
  - the MFE bar is hindsight; it is used ONLY in the descriptive table (describe_mfe).
  - every exit rule reads indicators of bars <= the decision bar (closed bar), exits at the NEXT 1m open.
  - rules are chosen on TRAIN; VALIDATE is the second look; HOLDOUT is read only for a variant that
    beats the time exit on VALIDATE (one variant per setup).
Costs: 0.10% round-trip taker (operator-set, 2 x 0.05%) + funding actually paid at the 8h marks held.
OI change is NOT_IN_DATA (no open-interest series on disk) and is not used.
"""
import csv
import glob
import json
import os
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

D = "F:/MTS/data/bigtrade"
FUND = "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_fund/fundingRate"
FEE_RT = 0.0010
DEV_ONLY = os.environ.get("MFE_DEV_ONLY") == "1"   # rerun 2026-10-17 on relabelled fires: only split == TRAIN rows are loaded
RUN_ID = "MFEX-RERUN-DEV-2026-10-17" if DEV_ONLY else "MFEX-2026-10-13"
K = 32                      # max hold in signal-TF bars (fixed, declared before any result)
STOP_ATR = 2.0              # wide protective stop, same in every arm
SETUPS = [                  # top 3 by tradable entries (counted 2026-10-13)
    ("turn_of_candle_1m", "fires_turn_of_candle_turn_of_candle_1m.csv", 1),
    ("sr_flip_15m", "fires_cryptocred_sr_flip_15m.csv", 15),
    ("rsi_events_5m", "fires_rsi_rsi_events_5m.csv", 5),
]
SETTINGS = {"rsi": (7, 14, 28), "stoch": (7, 14, 28), "bb": (10, 20, 40),
            "cvd": (3, 8, 24), "vol": (10, 20, 40)}


# ---------------------------------------------------------------- data
def load_1m():
    d = np.load(D + "/cache/perp/klines_1m.npz")
    return {k: d[k] for k in d.files}


def aggregate(k1, m):
    n = len(k1["t"]) // m * m
    r = lambda a: a[:n].reshape(-1, m)
    return {"t": k1["t"][:n:m], "o": r(k1["o"])[:, 0], "h": r(k1["h"]).max(1), "l": r(k1["l"]).min(1),
            "c": r(k1["c"])[:, -1], "v": r(k1["v"]).sum(1), "tbv": r(k1["tbv"]).sum(1)}


def load_funding():
    rows = []
    for f in sorted(glob.glob(FUND + "/*.csv")):
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                rows.append((int(r["calc_time"]), float(r["last_funding_rate"])))
    rows.sort()
    t = np.array([r[0] for r in rows], dtype=np.int64)
    c = np.concatenate([[0.0], np.cumsum([r[1] for r in rows])])
    return t, c


def funding_cum(ft, fc, t_ms):
    """sum of funding rates with calc_time <= t_ms (rate of events in (a, b] = cum(b) - cum(a))."""
    return fc[np.searchsorted(ft, t_ms, side="right")]


# ---------------------------------------------------------------- indicators (causal)
def rsi(c, n):
    out = np.full(len(c), np.nan)
    d = np.diff(c)
    g = np.where(d > 0, d, 0.0)
    ls = np.where(d < 0, -d, 0.0)
    if len(c) <= n:
        return out
    ag, al = g[:n].mean(), ls[:n].mean()
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + ls[i]) / n
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def stochrsi(c, n):
    r = rsi(c, n)
    out = np.full(len(c), np.nan)
    if len(c) < 2 * n:
        return out
    w = swv(r, n)
    lo, hi = w.min(1), w.max(1)
    rng = hi - lo
    with np.errstate(invalid="ignore", divide="ignore"):
        s = np.where(rng > 0, (r[n - 1:] - lo) / rng, 0.5)
    out[n - 1:] = s
    return out


def bbpos(c, n):
    out = np.full(len(c), np.nan)
    w = swv(c, n)
    ma, sd = w.mean(1), w.std(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        out[n - 1:] = np.where(sd > 0, (c[n - 1:] - ma) / (2 * sd), 0.0)
    return out


def cvdslope(v, tbv, m):
    d = 2 * tbv - v
    cs, cv = np.concatenate([[0.0], np.cumsum(d)]), np.concatenate([[0.0], np.cumsum(v)])
    out = np.full(len(v), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        num = cs[m:] - cs[:-m]
        den = cv[m:] - cv[:-m]
        out[m - 1:] = np.where(den > 0, num / den, 0.0)
    return out


def volratio(v, m_tf, days):
    """volume / mean of the same slot-of-day over the previous `days` days (excludes today)."""
    spd = 1440 // m_tf
    nd = len(v) // spd
    a = v[:nd * spd].reshape(nd, spd)
    cs = np.vstack([np.zeros((1, spd)), np.cumsum(a, 0)])
    out = np.full((nd, spd), np.nan)
    for i in range(days, nd):
        out[i] = a[i] / np.maximum((cs[i] - cs[i - days]) / days, 1e-12)
    res = np.full(len(v), np.nan)
    res[:nd * spd] = out.ravel()
    return res


def build_features(b, m):
    f = {}
    for n in SETTINGS["rsi"]:
        f[f"rsi{n}"] = rsi(b["c"], n)
    for n in SETTINGS["stoch"]:
        f[f"stoch{n}"] = stochrsi(b["c"], n)
    for n in SETTINGS["bb"]:
        f[f"bb{n}"] = bbpos(b["c"], n)
    for n in SETTINGS["cvd"]:
        f[f"cvd{n}"] = cvdslope(b["v"], b["tbv"], n)
    for n in SETTINGS["vol"]:
        f[f"vol{n}"] = volratio(b["v"], m, n)
    return f


# ---------------------------------------------------------------- rules
VARIANTS = (
    [("E1_momflip", f"rsi{a}/rsi{b}", (f"rsi{a}", f"rsi{b}")) for a, b in ((7, 14), (7, 28), (14, 28))]
    + [("E2_stoch_exh", f"stoch{n}", (f"stoch{n}",)) for n in SETTINGS["stoch"]]
    + [("E3_bb_reject", f"bb{n}", (f"bb{n}",)) for n in SETTINGS["bb"]]
    + [("E4_cvdflip", f"cvd{a}/cvd{b}", (f"cvd{a}", f"cvd{b}")) for a, b in ((3, 24), (3, 8), (8, 24))]
    + [("E5_volclimax", f"vol{n}", (f"vol{n}", "_candle")) for n in SETTINGS["vol"]]
)


def rule_signal(kind, feats, s, c, o):
    """bool array (per TF bar): rule says EXIT a trade of side s (+1 long, -1 short) at this bar's close.
    Uses bars <= i only (shift by one for the 'previous' reading)."""
    prev = lambda x: np.concatenate([[np.nan], x[:-1]])
    with np.errstate(invalid="ignore"):
        if kind == "E1_momflip":
            x, y = s * (feats[0] - 50), s * (feats[1] - 50)
            return (prev(x) >= 0) & (x < 0) & (y > 0)
        if kind == "E2_stoch_exh":
            u = feats[0] if s > 0 else 1 - feats[0]
            return (prev(u) > 0.8) & (u <= 0.8)
        if kind == "E3_bb_reject":
            u = s * feats[0]
            return (prev(u) > 1) & (u <= 1)
        if kind == "E4_cvdflip":
            return (s * feats[0] < 0) & (s * feats[1] > 0)
        if kind == "E5_volclimax":
            return (feats[0] > 2.0) & (s * (c - o) < 0)
    raise ValueError(kind)


# ---------------------------------------------------------------- trades
def read_fires(fname):
    out = []
    with open(os.path.join(D, "fires", fname), newline="") as fh:
        for r in csv.DictReader(fh):
            if r["tradable"] == "1" and r["side"] in ("long", "short") and r["split"] in (("TRAIN",) if DEV_ONLY else ("TRAIN", "VALIDATE", "HOLDOUT")):
                out.append((int(r["t_fire_ms"]), 1 if r["side"] == "long" else -1, float(r["atr"]), r["split"]))
    out.sort()
    return out


def thin(fires, m):
    """greedy non-overlap: next entry no earlier than K bars after the previous kept entry."""
    kept, last = [], -1
    gap = K * m * 60000
    for f in fires:
        if f[0] >= last + gap:
            kept.append(f)
            last = f[0]
    return kept


def trade_matrix(k1, fires, m, ft, fc):
    """For each kept trade and each exit offset k=0..K-1 (exit at the next 1m open after TF bar k closes,
    or the protective stop if hit first): gross and net return, plus MFE/MAE. Returns dict of arrays."""
    t1 = k1["t"]
    n_pos = len(t1)
    rows = []
    for (tf_, s, atr, split) in fires:
        i0 = int(np.searchsorted(t1, tf_))
        if i0 >= n_pos or t1[i0] != tf_ or i0 % m != 0 or i0 + (K + 1) * m >= n_pos:
            continue
        rows.append((i0, s, atr, split, tf_))
    n = len(rows)
    G = np.full((n, K), np.nan)
    EXT = np.zeros((n, K), dtype=np.int64)          # exit 1m index per offset
    mfe = np.zeros(n)
    mae = np.zeros(n)
    mfe_k = np.zeros(n, dtype=np.int64)
    s_arr = np.zeros(n, dtype=np.int64)
    j0 = np.zeros(n, dtype=np.int64)
    split = np.empty(n, dtype=object)
    tent = np.zeros(n, dtype=np.int64)
    ks = np.arange(K)
    for r, (i0, s, atr, sp, tf_) in enumerate(rows):
        e = k1["o"][i0]
        lo = k1["l"][i0:i0 + K * m]
        hi = k1["h"][i0:i0 + K * m]
        ex_i = i0 + (ks + 1) * m                      # next 1m open after TF bar k closes
        px = k1["o"][ex_i]
        if s > 0:
            stop = e - STOP_ATR * atr
            hit = np.nonzero(lo <= stop)[0]
            fav, adv = hi.max() / e - 1, 1 - lo.min() / e
            mk = int(np.argmax(hi)) // m
        else:
            stop = e + STOP_ATR * atr
            hit = np.nonzero(hi >= stop)[0]
            fav, adv = 1 - lo.min() / e, hi.max() / e - 1
            mk = int(np.argmin(lo)) // m
        g = s * (px / e - 1)
        if len(hit):
            h0 = int(hit[0])                          # 1m offset of the stop bar
            sg = s * (stop / e - 1)
            stopped = ex_i - i0 > h0                  # exit open is after the stop bar
            g = np.where(stopped, sg, g)
            ex_i = np.where(stopped, i0 + h0 + 1, ex_i)
        G[r], EXT[r] = g, ex_i
        mfe[r], mae[r], mfe_k[r], s_arr[r], j0[r], split[r], tent[r] = fav, adv, mk, s, i0 // m, sp, tf_
    # funding paid by the side (long pays positive rate)
    te = t1[EXT]
    fcost = (funding_cum(ft, fc, te) - funding_cum(ft, fc, tent)[:, None]) * s_arr[:, None]
    NET = G - FEE_RT - fcost
    return {"n": n, "gross": G, "net": NET, "ext": EXT, "mfe": mfe, "mae": mae, "mfe_k": mfe_k, "s": s_arr,
            "j0": j0, "split": split.astype(str), "i0": np.array([r[0] for r in rows]), "t": tent}


def livelike(k1, tm, m, ft, fc, stop=0.01, target=0.02, bars=8):
    """live_like_1pct_2pct_8bars bracket (EXIT_POLICIES_REPORT definition), stop-first on shared bars."""
    t1 = k1["t"]
    out = np.zeros(tm["n"])
    for r in range(tm["n"]):
        i0, s = int(tm["i0"][r]), int(tm["s"][r])
        e = k1["o"][i0]
        w = bars * m
        lo, hi = k1["l"][i0:i0 + w], k1["h"][i0:i0 + w]
        if s > 0:
            sh = np.nonzero(lo <= e * (1 - stop))[0]
            th = np.nonzero(hi >= e * (1 + target))[0]
        else:
            sh = np.nonzero(hi >= e * (1 + stop))[0]
            th = np.nonzero(lo <= e * (1 - target))[0]
        sh = sh[0] if len(sh) else 10 ** 9
        th = th[0] if len(th) else 10 ** 9
        if sh <= th and sh < 10 ** 9:
            g, ex = -stop, i0 + sh + 1
        elif th < 10 ** 9:
            g, ex = target, i0 + th + 1
        else:
            g, ex = s * (k1["c"][i0 + w - 1] / e - 1), i0 + w
        fcost = (funding_cum(ft, fc, t1[ex]) - funding_cum(ft, fc, t1[i0])) * s
        out[r] = g - FEE_RT - fcost
    return out


def rule_offsets(tm, sig_long, sig_short):
    """first exit offset (0..K-1) at which the rule fires, else K-1 (time exit). Also a fired flag."""
    n = tm["n"]
    off = np.full(n, K - 1, dtype=np.int64)
    fired = np.zeros(n, dtype=bool)
    for r in range(n):
        j = int(tm["j0"][r])
        sg = (sig_long if tm["s"][r] > 0 else sig_short)[j:j + K]
        nz = np.nonzero(sg)[0]
        if len(nz):
            off[r], fired[r] = int(nz[0]), True
    return off, fired


# ---------------------------------------------------------------- stats
def tstat(x):
    x = x[np.isfinite(x)]
    if len(x) < 3 or x.std(ddof=1) == 0:
        return 0.0
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x))))


def two_sided_p(t):
    from math import erf, sqrt
    return float(1 - erf(abs(t) / sqrt(2)))


def summarize(mask, net_ret, gross_ret, mfe):
    x, g, f = net_ret[mask], gross_ret[mask], mfe[mask]
    if len(x) == 0:
        return {"n": 0}
    return {"n": int(len(x)), "net_bp": float(x.mean() * 1e4), "gross_bp": float(g.mean() * 1e4),
            "win": float((x > 0).mean()), "t_net": tstat(x),
            "mfe_capture": float(g.mean() / f.mean()) if f.mean() > 0 else float("nan")}


def placebo_p(R, off, mask, n_perm=2000, seed=20261013):
    """Same trades, rule exit offsets permuted across trades (no replacement). Tests whether the TIMING
    carries information beyond the holding-time distribution. One-sided: share of perms >= observed."""
    rng = np.random.default_rng(seed)
    idx = np.nonzero(mask)[0]
    Rm, om = R[idx], off[idx]
    obs = Rm[np.arange(len(idx)), om].mean()
    cnt = 0
    for _ in range(n_perm):
        p = rng.permutation(len(idx))
        cnt += Rm[np.arange(len(idx)), om[p]].mean() >= obs
    return (cnt + 1) / (n_perm + 1)


def describe_mfe(feats, tm, b, split="TRAIN"):
    """HINDSIGHT table: signed readings at the MFE bar (and 1..3 bars before) minus the mean of the
    same trade's other bars. Not tradable; shows what state the peak looks like."""
    out = []
    sel = np.nonzero((tm["split"] == split) & (tm["mfe_k"] >= 4))[0]
    for name, arr in feats.items():
        diffs = {k: [] for k in (0, 1, 2, 3)}
        for r in sel:
            s, j0, km = int(tm["s"][r]), int(tm["j0"][r]), int(tm["mfe_k"][r])
            w = arr[j0:j0 + K]
            if name.startswith("rsi"):
                w = s * (w - 50)
            elif name.startswith("stoch"):
                w = s * (w - 0.5)
            elif name.startswith("bb") or name.startswith("cvd"):
                w = s * w
            else:
                w = np.log(np.maximum(w, 1e-6))
            keep = np.ones(K, bool)
            keep[max(0, km - 3):km + 1] = False
            base = w[keep]
            base = base[np.isfinite(base)]
            if len(base) < 5:
                continue
            for k in diffs:
                v = w[km - k]
                if np.isfinite(v):
                    diffs[k].append(v - base.mean())
        row = {"feature": name, "n": len(diffs[0])}
        for k in diffs:
            a = np.array(diffs[k])
            row[f"d_peak-{k}"] = float(a.mean()) if len(a) else float("nan")
            row[f"t_peak-{k}"] = tstat(a) if len(a) else float("nan")
        out.append(row)
    return out


# ---------------------------------------------------------------- driver
def main(out_dir):
    k1 = load_1m()
    ft, fc = load_funding()
    results = {"config": {"K": K, "stop_atr": STOP_ATR, "fee_rt": FEE_RT, "funding_to_ms": int(ft[-1])},
               "setups": {}}
    registry = []
    for name, fname, m in SETUPS:
        print("setup", name, flush=True)
        fires = thin(read_fires(fname), m)
        b = aggregate(k1, m)
        feats = build_features(b, m)
        tm = trade_matrix(k1, fires, m, ft, fc)
        ll = livelike(k1, tm, m, ft, fc)
        sp = tm["split"]
        tmask = {s: sp == s for s in ("TRAIN", "VALIDATE", "HOLDOUT")}
        time_idx = np.full(tm["n"], K - 1)
        rows = np.arange(tm["n"])
        time_net = tm["net"][rows, time_idx]
        time_gross = tm["gross"][rows, time_idx]
        res = {"fires_thinned": tm["n"], "split_n": {s: int(m_.sum()) for s, m_ in tmask.items()},
               "entry_quality": {}, "arms": {}, "mfe_table": None, "hold_min": K * m}
        for s in ("TRAIN", "VALIDATE"):
            mk = tmask[s]
            for side, sv in (("long", 1), ("short", -1), ("all", 0)):
                mm = mk & ((tm["s"] == sv) if sv else True)
                if mm.sum() == 0:
                    continue
                res["entry_quality"][f"{s}/{side}"] = {
                    "n": int(mm.sum()), "gross_time_exit_bp": float(time_gross[mm].mean() * 1e4),
                    "t_gross": tstat(time_gross[mm]), "mfe_bp_mean": float(tm["mfe"][mm].mean() * 1e4),
                    "mfe_bp_median": float(np.median(tm["mfe"][mm]) * 1e4),
                    "mae_bp_mean": float(tm["mae"][mm].mean() * 1e4),
                    "share_mfe_gt_fee": float((tm["mfe"][mm] > FEE_RT).mean())}
        arms = {"time_exit": (time_idx, None), "livelike_1pct_2pct_8bars": (None, ll)}
        sig = {}
        for kind, label, fkeys in VARIANTS:
            ins = [feats[k] if k in feats else None for k in fkeys]
            candle = fkeys[-1] == "_candle"
            ins = [x for x in ins if x is not None]
            sl = rule_signal(kind, ins, +1, b["c"], b["o"])
            ss = rule_signal(kind, ins, -1, b["c"], b["o"])
            off, fired = rule_offsets(tm, sl, ss)
            sig[f"{kind}:{label}"] = (off, fired)
            arms[f"{kind}:{label}"] = (off, None)
        for arm, (off, direct) in arms.items():
            net = direct if direct is not None else tm["net"][rows, off]
            gross = tm["gross"][rows, off] if off is not None else None
            res["arms"][arm] = {}
            for s in ("TRAIN", "VALIDATE"):
                mk = tmask[s]
                g = gross if gross is not None else net + FEE_RT
                d = summarize(mk, net, g, tm["mfe"])
                if arm != "time_exit" and d["n"]:
                    d["t_vs_time"] = tstat((net - time_net)[mk])
                    d["diff_vs_time_bp"] = float((net - time_net)[mk].mean() * 1e4)
                if off is not None and arm in sig and d["n"]:
                    d["fired_share"] = float(sig[arm][1][mk].mean())
                    d["mean_hold_bars"] = float((off[mk] + 1).mean())
                res["arms"][arm][s] = d
                registry.append((name, arm, K, s, d))
        # selection: TRAIN best variant (n >= 100), advance only if VALIDATE net beats time exit
        cand = [(a, res["arms"][a]["TRAIN"]["net_bp"]) for a in sig if res["arms"][a]["TRAIN"]["n"] >= 100]
        sel = max(cand, key=lambda x: x[1])[0] if cand else None
        res["selected_on_train"] = sel
        res["advance_to_holdout"] = False
        if sel:
            v = res["arms"][sel]["VALIDATE"]
            tv = res["arms"]["time_exit"]["VALIDATE"]
            res["advance_to_holdout"] = bool(v["n"] and v["net_bp"] > tv["net_bp"] and v.get("t_vs_time", 0) > 1.64)
            res["selected_validate"] = {"net_bp": v.get("net_bp"), "time_exit_net_bp": tv.get("net_bp"),
                                        "t_vs_time": v.get("t_vs_time")}
            off = sig[sel][0]
            res["placebo_p_train"] = placebo_p(tm["net"], off, tmask["TRAIN"])
            res["placebo_p_validate"] = placebo_p(tm["net"], off, tmask["VALIDATE"]) if tmask["VALIDATE"].any() else None
            if res["advance_to_holdout"]:
                mk = tmask["HOLDOUT"]
                net = tm["net"][rows, off]
                d = summarize(mk, net, tm["gross"][rows, off], tm["mfe"])
                d["t_vs_time"] = tstat((net - time_net)[mk])
                d["diff_vs_time_bp"] = float((net - time_net)[mk].mean() * 1e4)
                d["time_exit_net_bp"] = float(time_net[mk].mean() * 1e4)
                d["livelike_net_bp"] = float(ll[mk].mean() * 1e4)
                d["placebo_p"] = placebo_p(tm["net"], off, mk)
                res["holdout"] = d
        res["mfe_table"] = describe_mfe(feats, tm, b)
        results["setups"][name] = res
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", newline="\n") as fh:
        json.dump(results, fh, indent=1, default=float)
    n_var = len(VARIANTS)
    with open(os.path.join(out_dir, "TRIAL_REGISTRY.csv"), "w", newline="\n") as fh:
        w = csv.writer(fh)
        w.writerow(["run_id", "date", "family", "event", "tf", "h", "sign", "window", "n", "mean_net_bps",
                    "p_adj", "note"])
        for name, arm, h, s, d in registry:
            if not d.get("n"):
                continue
            t = d.get("t_vs_time", d.get("t_net", 0.0))
            p = min(1.0, two_sided_p(t) * (n_var * len(SETUPS) if arm not in ("time_exit",) else 1))
            w.writerow([RUN_ID, "2026-10-17" if DEV_ONLY else "2026-10-13", "MFEX", f"{name}:{arm}", name.split("_")[-1], h, 0, s,
                        d["n"], round(d["net_bp"], 1), round(p, 4), "design" if s == "TRAIN" else "check"])
    print("done", flush=True)
    return results


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
