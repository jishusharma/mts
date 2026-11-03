"""RSI deep-buy Stage 3: causal confirmations at an RSI low vs the raw touch (OPUS_FRAMING s3/s4, card rsi-deep-confirmations).

Unit = Stage-0 episode (econ_floor.find_events: RSI <= L after >= L+3; h=3). Signal bar s = episode start. A confirmation is
the FIRST bar c in [s, e] where its rule is true, e = min(s+W, bar before the episode re-arms at RSI >= L+3, data end).
Entry = open of bar c+1 (next open), exit = open N bars later, fee 0.10% round trip (econ_floor.FEE <- backtest/fees.py).
Per confirmation and horizon N (bars of the TF): P(new lower low within N bars after c) where "new lower low" = a bar low in
c+1..c+N below the lowest low of the episode so far (s..c), and fee-net EV per event (day-clustered 95% CI), EV per calendar day, and
two comparisons with the raw touch (entry open[s+1]): vs_raw = mean net per event minus the UNCONDITIONAL raw-touch mean over all episodes
(independent-groups day-clustered CI, conservative; this is the tradeable comparison) and delta = paired difference on the SAME episodes
(conditional on the confirmation appearing later, so biased towards the confirmation: a diagnostic of what waiting saves, not an edge).
Every rule reads bars <= c only; higher-TF RSI = last COMPLETED bar before the bar's own HTF group (shifted one, OPUS_FRAMING s2.2).

Run: python confirmations.py --pass dev   (writes confirmations_dev.csv incl. the frozen best pair; refuses bars >= 2024-07-01)
     python confirmations.py --pass val   (reads 2024-07..2025-06 ONCE with the frozen pair from the dev csv; refuses >= 2025-07)
     python confirmations.py --pass report (writes CONFIRMATIONS.md)

Labels. SOURCED: RSI14 Wilder (FORMULAS s1), fee 0.10% round trip (backtest/fees.py), ATR = plain SMA of true range (FORMULAS s12),
z-score vs prior L bars with population sd (FORMULAS s28.1), Bollinger n=20 mult=2 population sd (FORMULAS s22), DEV/VALIDATION/HOLDOUT
cut dates (backtest/splits.py), taker-buy column of the Binance kline. OURS: h=3, W=16 bars, hook b=3 (5 sensitivity), climax z>=2 over
100 bars with close in the upper third of the bar, fast fall <= -3 ATR over 14 bars, volume spike z>=2, taker-buy share >= 0.55,
HTF state cuts 30/40, location windows 24h/7d, N in 4 and 16, min 30 days, best-pair rule (top two distinct families by mean net EV at N=16).
"""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import econ_floor as ef  # noqa: E402
import prob_tables as pt  # noqa: E402

FEE = ef.FEE
CUTOFF_MS = ef.CUTOFF_MS
HOLDOUT_MS = pt.HOLDOUT_MS
HYST = ef.HYST
W = 16                  # OURS: confirmation window, bars of the TF
HORIZONS = (4, 16)      # OURS: N, bars of the TF
MIN_DAYS = 30           # OPUS_FRAMING s4.5
CELLS = ((60, "abs20"), (60, "abs30"), (60, "rel_p2_90d"), (15, "abs30"), (15, "abs20"), (1, "abs10"))
# Stage-0 survivors (ECON_FLOOR.md H1): 1m abs30/abs20/rel and 15m rel are dead; 60m abs10 has 2 episodes; the rest are kept.
HTF_UP = {1: (15, 60), 15: (60, 240), 60: (240, 1440)}   # next two TFs up (OURS)
Z = 1.96
DAY_MS = 86_400_000


def load_klines_ext(paths, cutoff_ms=CUTOFF_MS):
    """1m kline CSVs with volume and taker_buy_volume. Raises ValueError if any bar opens at or after cutoff_ms."""
    import pandas as pd
    cols = ["open_time", "open", "high", "low", "close", "volume", "taker_buy_volume"]
    df = pd.concat([pd.read_csv(p, usecols=cols) for p in paths], ignore_index=True)
    t = df["open_time"].to_numpy(dtype="int64")
    if len(t) and t.max() > 10 ** 14:
        t = t // 1000
    if len(t) and t.max() >= cutoff_ms:
        raise ValueError("bar with open >= cutoff refused (this pass may not read it)")
    order = np.argsort(t, kind="stable")
    t = t[order]
    keep = np.r_[True, np.diff(t) > 0]
    out = {"open_time": t[keep]}
    for k in cols[1:]:
        out[k] = df[k].to_numpy(dtype="float64")[order][keep]
    return out


def resample_ext(d, minutes):
    """UTC-aligned complete groups only: OHLC from econ_floor.resample, volume and taker_buy_volume summed."""
    if minutes == 1:
        return d
    r = ef.resample(d, minutes)
    g = d["open_time"] // (minutes * 60_000)
    ug, start, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == minutes
    for k in ("volume", "taker_buy_volume"):
        if k in d:
            r[k] = np.add.reduceat(d[k], start)[ok]
    return r


def atr_sma(high, low, close, n=14):
    """FORMULAS s12: ATR[i] = mean(TR[i-n+1..i]), TR[i] = max(h-l, |h-c[i-1]|, |l-c[i-1]|); NaN for i < n."""
    pc = np.r_[np.nan, close[:-1]]
    tr = np.maximum.reduce([high - low, np.abs(high - pc), np.abs(low - pc)])
    tr[0] = np.nan
    import pandas as pd
    return pd.Series(tr).rolling(n).mean().to_numpy()      # tr[0] is NaN, so the first value is at i = n


def zscore_prior(x, L):
    """FORMULAS s28.1: z_i = (x_i - mean(x[i-L..i-1])) / pstdev(x[i-L..i-1]); NaN when i < L or the sd is 0."""
    import pandas as pd
    s = pd.Series(x)
    mu = s.rolling(L).mean().shift(1).to_numpy()
    sd = s.rolling(L).std(ddof=0).shift(1).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (np.asarray(x, dtype="float64") - mu) / sd
    z[~(sd > 1e-9)] = np.nan
    return z


def bollinger_lower(close, n=20, mult=2.0):
    import pandas as pd
    s = pd.Series(close)
    return (s.rolling(n).mean() - mult * s.rolling(n).std(ddof=0)).to_numpy()


def episode_end(rsi, s, level, wcap=W):
    """Last bar (inclusive) at which a confirmation for the episode starting at s may fire."""
    e = min(s + wcap, len(rsi) - 1)
    for i in range(s + 1, e + 1):
        if rsi[i] >= level + HYST:
            return i - 1
    return e


def first_true(cond, s, e):
    seg = cond[s:e + 1]
    if not seg.any():
        return -1
    return s + int(np.argmax(seg))


def hook_bar(rsi, s, e, b):
    """C1: first bar where RSI is >= b points above its running minimum since s."""
    m = np.inf
    for i in range(s, e + 1):
        m = min(m, rsi[i])
        if rsi[i] - m >= b:
            return i
    return -1


def shift_bar(high, low, close, s, e):
    """C3: first close above the high of the lowest-low bar of the episode so far (bars s..i-1)."""
    k = s
    for i in range(s + 1, e + 1):
        if low[i - 1] < low[k]:
            k = i - 1
        if close[i] > high[k]:
            return i
    return -1


def cond_climax(high, low, close, zlen=100, zmin=2.0, loc=2 / 3):
    rng = high - low
    z = zscore_prior(rng, zlen)
    with np.errstate(divide="ignore", invalid="ignore"):
        where = (close - low) / rng
    return (z >= zmin) & (where >= loc)


def _ret_atr(high, low, close, n=14):
    a = atr_sma(high, low, close, n)
    r = np.full(len(close), np.nan)
    r[n:] = close[n:] - close[:-n]
    with np.errstate(divide="ignore", invalid="ignore"):
        return r / a


def cond_fast_fall(high, low, close, k=-3.0):
    return _ret_atr(high, low, close) <= k


def cond_grind(high, low, close, k=-3.0):
    return _ret_atr(high, low, close) > k


def cond_vol_spike(vol, zmin=2.0):
    return zscore_prior(vol, 100) >= zmin


def cond_taker_buy(vol, taker, share=0.55):
    with np.errstate(divide="ignore", invalid="ignore"):
        return (taker / vol) >= share


def cond_location(low, close, bars):
    """(sweep, newlow): newlow = low below the lowest low of the prior `bars` bars; sweep = newlow and the close back above it."""
    import pandas as pd
    pm = pd.Series(low).rolling(bars).min().shift(1).to_numpy()
    newlow = low < pm
    return newlow & (close > pm), newlow


def htf_rsi_lastcompleted(t_ms, d1, htf_min):
    """RSI14 of the HTF bar BEFORE the HTF group that contains each time in t_ms (so the group in progress, and the bar
    itself, never enter). NaN where that HTF bar is missing or inside the RSI warm-up."""
    dh = resample_ext(d1, htf_min)
    r = ef.rsi_series(dh["close"])
    gh = dh["open_time"] // (htf_min * 60_000)
    g = np.asarray(t_ms) // (htf_min * 60_000) - 1
    pos = np.searchsorted(gh, g)
    pos_c = np.minimum(pos, len(gh) - 1)
    ok = (pos < len(gh)) & (gh[pos_c] == g)
    out = np.full(len(g), np.nan)
    out[ok] = r[pos_c[ok]]
    return out


def entry_exit(open_, c, N):
    """Entry = open of the bar after the confirmation bar, exit = open N bars later. None when the exit is beyond the data."""
    if c + 1 + N >= len(open_):
        return None
    e, x = float(open_[c + 1]), float(open_[c + 1 + N])
    return e, x, x / e - 1.0


def outcome_lower_low(low, s, c, N):
    return bool(low[c + 1:c + 1 + N].min() < low[s:c + 1].min())


def pair_bar(c1, c2):
    return -1 if c1 < 0 or c2 < 0 else max(c1, c2)


def build_ctx(d1, tf):
    d = resample_ext(d1, tf)
    n = len(d["open"])
    hi, lo, cl = d["high"], d["low"], d["close"]
    day_bars = 1440 // tf
    ctx = {"d": d, "n": n, "rsi": ef.rsi_series(cl), "day": d["open_time"] // DAY_MS}
    sweep24, new24 = cond_location(lo, cl, day_bars)
    _, new7 = cond_location(lo, cl, 7 * day_bars)
    conds = {"C5_climax": cond_climax(hi, lo, cl), "C5_fast": cond_fast_fall(hi, lo, cl), "C5_grind": cond_grind(hi, lo, cl),
             "C9_volspike": cond_vol_spike(d["volume"]), "C9_takerbuy": cond_taker_buy(d["volume"], d["taker_buy_volume"]),
             "C8_sweep24": sweep24, "C8_newlow24": new24, "C8_newlow7d": new7,
             "C8_belowBB": cl < bollinger_lower(cl)}
    for tag, hm in zip("ab", HTF_UP[tf]):
        r = htf_rsi_lastcompleted(d["open_time"], d1, hm)
        conds[f"C7{tag}_gt40"] = r > 40
        conds[f"C7{tag}_30_40"] = (r >= 30) & (r <= 40)
        conds[f"C7{tag}_lt30"] = r < 30
    ctx["conds"] = conds
    return ctx


def conf_bar(name, ctx, s, e):
    if name == "RAW":
        return s
    d, rsi = ctx["d"], ctx["rsi"]
    if name == "C1_hook3":
        return hook_bar(rsi, s, e, 3.0)
    if name == "C1_hook5":
        return hook_bar(rsi, s, e, 5.0)
    if name == "C3_shift":
        return shift_bar(d["high"], d["low"], d["close"], s, e)
    if name.startswith("PAIR:"):
        a, b = name[5:].split("+")
        return pair_bar(conf_bar(a, ctx, s, e), conf_bar(b, ctx, s, e))
    return first_true(ctx["conds"][name], s, e)


def single_names():
    return (["C1_hook3", "C1_hook5", "C3_shift", "C5_climax", "C5_fast", "C5_grind"]
            + [f"C7{t}_{b}" for t in "ab" for b in ("gt40", "30_40", "lt30")]
            + ["C9_volspike", "C9_takerbuy", "C8_sweep24", "C8_newlow24", "C8_newlow7d", "C8_belowBB"])


def level_array(rsi, level, tf):
    if level == "rel_p2_90d":
        return ef.relative_level(rsi, 90 * (1440 // tf), 1440 // tf)
    return float(level[3:])


def episodes(ctx, level, tf, start_ms):
    rsi = ctx["rsi"]
    ev, lv = ef.find_events(rsi, level_array(rsi, level, tf))
    t = ctx["d"]["open_time"]
    ev = [s for s in ev if s + 1 < ctx["n"] and t[s] >= start_ms]
    return [(s, float(lv[s])) for s in ev]


FIELDS = ["pass", "tf_min", "level", "conf", "N", "status", "n_episodes", "n_conf", "share_conf", "n_days", "p_lower",
          "p_lower_lo_d", "p_lower_hi_d", "p_lower_raw_same", "mean_net_pct", "net_lo_pct", "net_hi_pct", "mean_net_raw_same_pct",
          "delta_pct", "delta_lo_pct", "delta_hi_pct", "vs_raw_pct", "vs_raw_lo_pct", "vs_raw_hi_pct", "ev_per_cal_day_pct", "cal_days", "median_delay_bars"]


def cell_rows(ctx, tf, level, names, start_ms, which):
    d = ctx["d"]
    o, lo, t = d["open"], d["low"], d["open_time"]
    eps = episodes(ctx, level, tf, start_ms)
    rsi = ctx["rsi"]
    ends = [episode_end(rsi, s, L) for s, L in eps]
    lvl = level_array(rsi, level, tf)
    finite = np.isfinite(lvl) if level == "rel_p2_90d" else np.isfinite(rsi)
    eff_start = max(start_ms, int(t[int(np.argmax(finite))]))
    cal_days = max(1.0, (int(t[-1]) - eff_start) / DAY_MS)
    rows = []
    rawstat = {}                # N -> (mean, se) of the unconditional raw-touch net return over ALL episodes (names[0] must be RAW)
    for name in (names if names[0] == "RAW" else ["RAW"] + list(names)):
        cs = [conf_bar(name, ctx, s, e) for (s, _), e in zip(eps, ends)]
        for N in HORIZONS:
            g_c, g_r, ll_c, ll_r, days, delay = [], [], [], [], [], []
            for (s, _), c in zip(eps, cs):
                if c < 0:
                    continue
                xc, xr = entry_exit(o, c, N), entry_exit(o, s, N)
                if xc is None or xr is None:
                    continue
                g_c.append(xc[2]); g_r.append(xr[2])
                ll_c.append(outcome_lower_low(lo, s, c, N)); ll_r.append(outcome_lower_low(lo, s, s, N))
                days.append(int(ctx["day"][s])); delay.append(c - s)
            base = {"pass": which, "tf_min": tf, "level": level, "conf": name, "N": N, "n_episodes": len(eps), "cal_days": cal_days}
            n = len(g_c)
            if n == 0:
                rows.append({**base, "status": "no_events", "n_conf": 0, "n_days": 0})
                continue
            gc, gr = np.array(g_c) - FEE, np.array(g_r) - FEE
            dy = np.array(days)
            nd = int(len(np.unique(dy)))
            m, se = ef.cluster_mean_se(gc, dy)
            md, sed = ef.cluster_mean_se(gc - gr, dy)
            if name == "RAW":
                rawstat[N] = (m, se)
            rm, rse = rawstat.get(N, (m, se))
            vs, vse = m - rm, float(np.hypot(se, rse)) if name != "RAW" else 0.0   # independent-groups SE: conservative, the groups overlap
            p = float(np.mean(ll_c))
            lod, hid = pt.wilson(round(p * nd), nd)
            rows.append({**base, "status": "ok" if nd >= MIN_DAYS else "too_few_days", "n_conf": n,
                         "share_conf": n / len(eps), "n_days": nd, "p_lower": p, "p_lower_lo_d": lod, "p_lower_hi_d": hid,
                         "p_lower_raw_same": float(np.mean(ll_r)), "mean_net_pct": m * 100, "net_lo_pct": (m - Z * se) * 100,
                         "net_hi_pct": (m + Z * se) * 100, "mean_net_raw_same_pct": float(gr.mean() * 100),
                         "delta_pct": md * 100, "delta_lo_pct": (md - Z * sed) * 100, "delta_hi_pct": (md + Z * sed) * 100,
                         "vs_raw_pct": vs * 100, "vs_raw_lo_pct": (vs - Z * vse) * 100, "vs_raw_hi_pct": (vs + Z * vse) * 100,
                         "ev_per_cal_day_pct": float(gc.sum() * 100 / cal_days), "median_delay_bars": float(np.median(delay))})
    return [r for r in rows if r["conf"] in names]


def choose_pair(rows, tf, level):
    """Frozen on DEV: top two distinct families (C1/C3/C5/C7/C8/C9) by mean net EV at N=16 among status ok singles; None if < 2."""
    cand = [r for r in rows if r["tf_min"] == tf and r["level"] == level and r["N"] == 16 and r["status"] == "ok"
            and r["conf"] != "RAW" and not r["conf"].startswith("PAIR:")]
    cand.sort(key=lambda r: -r["mean_net_pct"])
    first = None
    for r in cand:
        if first is None:
            first = r
        elif r["conf"][:2] != first["conf"][:2]:
            return f"PAIR:{first['conf']}+{r['conf']}"
    return None


def month_files(klines, last_ym):
    return pt.month_files(klines, last_ym)


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k]:.6g}" if isinstance(r.get(k), (float, np.floating)) else r.get(k, "")) for k in FIELDS})


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def oi_rows(which):
    return [{"pass": which, "conf": "C_OI", "status": "NOT_IN_DATA"}]


def run(which, klines, out):
    out = Path(out)
    if which == "dev":
        d1 = load_klines_ext(month_files(klines, "2024-06"))
        start, dest, frozen = 0, out / "confirmations_dev.csv", {}
    else:
        dev = out / "confirmations_dev.csv"
        dest = out / "confirmations_val.csv"
        if not dev.exists():
            raise SystemExit("confirmations_dev.csv must be written (and frozen) before the VALIDATION read")
        if dest.exists():
            raise SystemExit("VALIDATION already read once (confirmations_val.csv exists); refusing a second read")
        frozen = {(int(r["tf_min"]), r["level"]): r["conf"] for r in read_csv(dev)
                  if r["conf"].startswith("PAIR:") and r["N"] == "16"}
        print("dev csv sha256", sha256(dev))
        d1 = load_klines_ext(month_files(klines, "2025-06"), cutoff_ms=HOLDOUT_MS)
        start = CUTOFF_MS
    rows = []
    for tf in sorted({c[0] for c in CELLS}):
        ctx = build_ctx(d1, tf)
        for ctf, level in CELLS:
            if ctf != tf:
                continue
            cr = cell_rows(ctx, tf, level, ["RAW"] + single_names(), start, which)
            pair = choose_pair(cr, tf, level) if which == "dev" else frozen.get((tf, level))
            if pair:
                cr += cell_rows(ctx, tf, level, [pair], start, which)
            rows += cr
            print(f"tf={tf}m {level} episodes={cr[0]['n_episodes']} pair={pair} rows={len(cr)}", flush=True)
    rows += oi_rows(which)
    write_csv(rows, dest)
    print("rows", len(rows), "->", dest)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="which", choices=("dev", "val", "report"), required=True)
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    if a.which == "report":
        write_report(Path(a.out))
        return
    run(a.which, a.klines, a.out)


def _fl(r, k):
    return float(r[k]) if r.get(k) not in (None, "") else float("nan")


def _key(r):
    return (r["tf_min"], r["level"], r["conf"], r["N"])


def _has(r):
    return bool(r) and r.get("n_conf") not in (None, "", "0")


def _fmt(r):
    return (f"{int(r['n_conf'])} / {int(r['n_days'])}d | {_fl(r, 'p_lower'):.2f} | {_fl(r, 'mean_net_pct'):+.3f} "
            f"[{_fl(r, 'net_lo_pct'):+.2f}, {_fl(r, 'net_hi_pct'):+.2f}] | {_fl(r, 'vs_raw_pct'):+.3f} "
            f"[{_fl(r, 'vs_raw_lo_pct'):+.2f}, {_fl(r, 'vs_raw_hi_pct'):+.2f}] | {_fl(r, 'ev_per_cal_day_pct'):+.4f}")


def _table(L, head, cand, vmap, with_conf):
    cols = "| TF | level | " + ("conf | " if with_conf else "") + "N | split | n / days | P(lower) | net % [CI] | vs raw % [CI] | EV/day % |"
    L += ["", f"## {head}", "", cols, "|" + "---|" * (cols.count("|") - 1)]
    for r in cand:
        for nm, x in (("DEV", r), ("VAL", vmap.get(_key(r)))):
            if _has(x):
                flag = "" if x["status"] == "ok" else f" ({x['status']})"
                L.append(f"| {r['tf_min']}m | {r['level']} | " + (f"{r['conf']} | " if with_conf else "")
                         + f"{r['N']} | {nm}{flag} | {_fmt(x)} |")


def write_report(out):
    out = Path(out)
    dev, val = read_csv(out / "confirmations_dev.csv"), read_csv(out / "confirmations_val.csv")
    vmap = {_key(r): r for r in val}
    L = ["# CONFIRMATIONS: Stage 3, causal confirmations at an RSI low vs the raw touch (RSI deep-buy)", "",
         "BTCUSDT, DEV `confirmations_dev.csv` (open < 2024-07-01, written and frozen first, sha256 "
         f"`{sha256(out / 'confirmations_dev.csv')[:16]}`), VALIDATION `confirmations_val.csv` read once (2024-07-01..2025-06-30, "
         "frozen pairs only). HOLDOUT (2025-07 onward) is refused by the loader and was never read. Generated by `confirmations.py`; "
         "the trial row in `layer_lab/TRIALS.md` was written before the outcomes.", "",
         "Method. Unit = Stage-0 episode (RSI <= level after >= level+3) on the six TF x level cells that H1 did not kill "
         "(ECON_FLOOR.md: 60m abs20/abs30/rel, 15m abs30/abs20, 1m abs10). A confirmation fires on the first bar c within 16 bars of the "
         "signal bar, before the episode re-arms, using bars <= c only (higher-TF RSI = last completed bar before the bar's own HTF group). "
         "Entry = open of c+1, exit = open N bars later (N = 4, 16 bars of the TF), fee 0.10% round trip (SOURCED backtest/fees.py). "
         "`P(lower)` = a bar low in c+1..c+N below the lowest low of the episode so far (s..c); for the raw touch the reference is the signal "
         "bar's low, so a confirmation lowers it partly by construction (its reference low is the lower episode low). `net` = mean net return "
         "per event, % of price, with a day-clustered 95% CI. `vs raw` = net minus the unconditional raw-touch net over all episodes "
         "(independent-groups day-clustered CI, conservative since the groups overlap): the tradeable comparison. `EV/day` = sum of net "
         "returns per calendar day of the sample, 1 unit per signal. Rows with fewer than 30 independent days are `too_few_days` (kept in "
         "the CSV, not ranked).", ""]
    ok_d = [r for r in dev if r["status"] == "ok" and r["conf"] != "RAW"]
    for nm, rows in (("DEV", dev), ("VALIDATION", val)):
        ok = [r for r in rows if r["status"] == "ok" and r["conf"] != "RAW"]
        n_all = sum(r["conf"] not in ("RAW", "C_OI") for r in rows)
        L.append(f"- {nm}: {n_all} confirmation rows (singles and the frozen pair, x cell x N), {len(ok)} with >= 30 days; "
                 f"net CI lower bound > 0: **{sum(_fl(r, 'net_lo_pct') > 0 for r in ok)}**; vs-raw CI lower bound > 0: "
                 f"**{sum(_fl(r, 'vs_raw_lo_pct') > 0 for r in ok)}**. Chance alone gives about 2.5% one-sided = {0.025 * len(ok):.1f} of {len(ok)}.")
    pos = [r for r in ok_d if _fl(r, "net_lo_pct") > 0 or _fl(r, "vs_raw_lo_pct") > 0]
    best = max(ok_d, key=lambda r: _fl(r, "mean_net_pct"))
    bv = vmap.get(_key(best))
    raw60 = next(r for r in dev if r["conf"] == "RAW" and r["tf_min"] == "60" and r["level"] == "abs20" and r["N"] == "16")
    L += ["", "## Verdict", ""]
    if not pos:
        L.append("**No confirmation shows a fee-net edge on DEV: no row has a day-clustered net CI above 0 and none beats the unconditional raw touch with its CI above 0.**")
    else:
        L.append(f"**{len(pos)} DEV rows have a net or vs-raw CI above 0 (listed below); read them against {0.025 * len(ok_d):.1f} expected by chance.**")
    L.append(f"The best DEV mean net is {best['conf']} on {best['tf_min']}m {best['level']} N={best['N']}: {_fl(best, 'mean_net_pct'):+.3f}% "
             f"[{_fl(best, 'net_lo_pct'):+.2f}, {_fl(best, 'net_hi_pct'):+.2f}] on {best['n_days']} days; VALIDATION same row: "
             + (f"{_fl(bv, 'mean_net_pct'):+.3f}% on {bv['n_days']} days ({bv['status']})." if _has(bv) else "no events.")
             + f" The ECON_FLOOR 60m abs20 lead: raw N=16 net {_fl(raw60, 'mean_net_pct'):+.3f}% [{_fl(raw60, 'net_lo_pct'):+.2f}, "
             f"{_fl(raw60, 'net_hi_pct'):+.2f}] on {raw60['n_days']} days, too wide to call, and no confirmation narrows it enough.")
    L += ["", "What the confirmations do: they cut the odds of a new lower low (tables below) and give up part of the bounce; per event the net "
          "stays inside the fee noise. The paired `delta` columns in the CSV (confirmed entry minus raw entry on the same episodes) are "
          "positive for many rows, but they are conditional on the confirmation appearing later, so they measure what waiting saves in episodes "
          "that kept falling, not an edge; use `vs raw`."]
    raws = [r for r in dev if r["conf"] == "RAW"]
    _table(L, "Raw touch per cell (baseline), DEV and VALIDATION", raws, vmap, False)
    _table(L, "Frozen best pair per cell (chosen on DEV at N=16: top two distinct families by mean net EV, then fixed)",
           [r for r in dev if r["conf"].startswith("PAIR:")], vmap, True)
    singles = [r for r in ok_d if not r["conf"].startswith("PAIR:")]
    _table(L, "Top 12 DEV singles by net EV per event (>= 30 days), VALIDATION row beside",
           sorted(singles, key=lambda r: -_fl(r, "mean_net_pct"))[:12], vmap, True)
    _table(L, "Lowest 10 P(new lower low) among DEV singles (>= 30 days): what the safety costs in net EV",
           sorted(singles, key=lambda r: _fl(r, "p_lower"))[:10], vmap, True)
    L += ["", "## Notes and decisions", "",
          "- Open interest: NOT_IN_DATA before 2025-09 (Binance metrics archive starts 2025-09-01, OPUS_FRAMING s3); no OI confirmation tested, row `C_OI` in both CSVs.",
          "- Grid: 21 singles + RAW + 1 frozen pair per cell, N in 4 and 16; every row is in the CSVs, nothing dropped; the multiple-comparison count is in the bullets above.",
          "- Not run (outside this card's list C1, C3, C5, C7, C9, C8): C4 divergence, C6 dwell, funding, candle patterns, VWAP distance.",
          "- DECISION (OURS): confirmation window 16 bars of the TF; a bar after the episode re-arms (RSI >= level+3) cannot confirm.",
          "- DECISION (OURS): fee charged once per trade (0.10% round trip); no slippage or funding; fill = next bar open exactly as in ECON_FLOOR.",
          "- Overlap: events inside one day or one crash are correlated; days are the unit of evidence, the CI is day-clustered and still optimistic across adjacent days.",
          "- Episodes whose exit falls beyond the sample end are dropped, not clipped. RSI warm-up (200 bars; the daily HTF RSI needs 200 days, so C7b on 60m is empty before mid-2022) is NaN, never a signal.",
          "- Disclosure: the first VALIDATION run left the `vs raw` columns of the frozen PAIR rows at 0 (a bug: the raw reference was not computed for the pair call). The VALIDATION data were NOT read again; those columns were recomputed arithmetically from the RAW and PAIR rows of the same csv (mean difference, hypot of the two SEs recovered from the CIs). The same arithmetic reproduces the corrected code on DEV to 5e-6 percentage points.",
          "- VALIDATION was read once with pairs frozen from the DEV csv; nothing was tuned on it. Guards in `test_confirmations.py`: HTF value unchanged when the current HTF bar changes, DEV loader refuses bars from 2024-07-01, entry = next open."]
    (out / "CONFIRMATIONS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("wrote", out / "CONFIRMATIONS.md")


if __name__ == "__main__":
    main()
