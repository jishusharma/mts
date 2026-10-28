"""Stage 0 economic-floor kill test for the RSI deep-buy study (OPUS_FRAMING.md s1 H1 + s5, SHOT_REVIEW.md C12).

BTCUSDT 1m klines, DEV only (loader refuses any bar with open >= 2024-07-01). RSI14 Wilder on 1m/15m/1h (resampled
from 1m, UTC-aligned, complete bars only). Episode start: RSI closes <= L after being >= L+h (h=3). Levels: absolute
30/20/10 and relative = trailing-90d 2nd percentile (computed from bars strictly before each daily block).
Fill = next bar open; exit = open `h` bars later; horizons {1,4,16} bars; gross return vs fee 0.10% round trip.
Baseline = mean forward return of ALL bars in the same (UTC hour, trailing-vol tercile) cell; vol cuts are
trailing-90d and causal. CI = day-clustered (plus a 7-day-block CI, reported only).
Output: ECON_FLOOR.csv (aggregates only, no prices) and ECON_FLOOR.md.

Run: python econ_floor.py [--klines F:/MTS/data/tom_raw/klines]
Labels: RSI14, fee 0.10% = SOURCED (backtest/fees.py); h=3, levels, horizons, 90d/2nd pct, vol window 60, cell definition,
200-bar search/episode caps = OURS.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MTS = HERE.parents[1]
sys.path.insert(0, str(MTS / "backtest"))
sys.path.insert(0, str(MTS / "backtest" / "layers" / "rsi"))
import fees  # noqa: E402
from rsi_core import rsi_core  # noqa: E402

FEE = 2 * fees.BINANCE_TAKER            # 0.10% round trip, SOURCED backtest/fees.py (taker both sides)
CUTOFF_MS = int(np.datetime64("2024-07-01T00:00", "ms").astype("int64"))   # DEV ends before this
HYST = 3.0                              # OURS, fixed (OPUS_FRAMING s1)
ABS_LEVELS = (30.0, 20.0, 10.0)         # OURS
HORIZONS = (1, 4, 16)                   # OURS
TFS = (1, 15, 60)                       # minutes
VOL_BARS = 60                           # OURS, trailing vol window (bars)
EPISODE_CAP = 200                       # OURS, bars: episode window for trough/lag
TARGET_CAP = 5000                       # OURS, bars searched for the RSI 40/50/60 target
WARMUP = 200                            # RSI seed memory (OPUS_FRAMING s2.1)
Z95 = 1.96
Z_POWER = 1.96 + 0.84                   # MDE at 80% power
DAY_MS = 86_400_000


def load_klines(paths, cutoff_ms=CUTOFF_MS):
    """Read 1m kline CSVs. Raises ValueError if any bar opens at or after the DEV cutoff."""
    import pandas as pd
    frames = [pd.read_csv(p, usecols=["open_time", "open", "high", "low", "close"]) for p in paths]
    df = pd.concat(frames, ignore_index=True)
    t = df["open_time"].to_numpy(dtype="int64")
    if len(t) and t.max() > 10**14:
        t = t // 1000                   # microsecond archives
    if len(t) and t.max() >= cutoff_ms:
        raise ValueError("bar with open >= DEV cutoff 2024-07-01 refused (VALIDATION/HOLDOUT not readable here)")
    order = np.argsort(t, kind="stable")
    t = t[order]
    keep = np.r_[True, np.diff(t) > 0]
    out = {"open_time": t[keep]}
    for k in ("open", "high", "low", "close"):
        out[k] = df[k].to_numpy(dtype="float64")[order][keep]
    return out


def _win(arr, a, b):
    """arr[a:b] with explicit bounds (the caller states how far the window reaches; see each use)."""
    return arr[a:b]


def resample(d, minutes):
    """UTC-aligned OHLC aggregation of 1m bars; only complete groups are kept."""
    if minutes == 1:
        return d
    g = d["open_time"] // (minutes * 60_000)
    ug, start, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == minutes
    start = start[ok]
    last_idx = start + (minutes - 1)    # last 1m bar inside each complete group (the group's close)
    return {"open_time": ug[ok] * minutes * 60_000,
            "open": d["open"][start],
            "high": np.array([_win(d["high"], s, s + minutes).max() for s in start]),
            "low": np.array([_win(d["low"], s, s + minutes).min() for s in start]),
            "close": d["close"][last_idx]}


def rsi_series(close):
    r = np.array([np.nan if v is None else v for v in rsi_core(list(map(float, close)), 14)], dtype="float64")
    r[:WARMUP] = np.nan
    return r


def block_percentiles(x, qs, window, step):
    """out[i] = percentiles of x[j-window:j] (strictly before j), j = last multiple of `step` <= i, j >= window. Causal."""
    n = len(x)
    out = np.full((n, len(qs)), np.nan)
    for j in range(window, n, step):
        seg = x[j - window:j]
        if np.isfinite(seg).sum() < window // 2:
            continue
        blk_end = j + step              # this block's bars use the percentile of bars before j only
        out[j:blk_end] = np.nanpercentile(seg, qs)
    return out


def relative_level(rsi, window, step, q=2.0):
    return block_percentiles(rsi, [q], window, step)[:, 0]


def find_events(rsi, level, h=HYST):
    """Episode starts: rsi <= level after rsi >= level+h. `level` scalar or per-bar array (nan = no level yet).
    Returns (list of signal bar indices, per-bar level array)."""
    lv = np.broadcast_to(np.asarray(level, dtype="float64"), rsi.shape)
    ev, armed = [], False
    for i in range(len(rsi)):
        r, L = rsi[i], lv[i]
        if np.isnan(r) or np.isnan(L):
            continue
        if r >= L + h:
            armed = True
        elif r <= L and armed:
            ev.append(i)
            armed = False
    return ev, lv


def forward_gross(open_, ev, h):
    """Gross return, fill = open of the bar after the signal bar, exit = open h bars later. NaN beyond data."""
    ev = np.asarray(ev, dtype=int)
    entry_i, exit_i = ev + 1, ev + 1 + h
    out = np.full(len(ev), np.nan)
    ok = exit_i < len(open_)
    out[ok] = open_[exit_i[ok]] / open_[entry_i[ok]] - 1.0
    return out


def is_dead(upper_ci):
    """H1 kill: upper end of the CI of (gross - baseline) strictly below the fee."""
    return bool(upper_ci < FEE)


def cluster_mean_se(x, groups):
    """Mean and cluster-robust SE of the mean (groups = day ids or stress-cluster ids)."""
    x = np.asarray(x, dtype="float64")
    n = len(x)
    m = x.mean()
    _, inv = np.unique(groups, return_inverse=True)
    s = np.bincount(inv, weights=x - m)
    return m, float(np.sqrt((s ** 2).sum()) / n)


def week_clusters(days):
    """7-day blocks (OURS): a coarser cluster than the day, so one stress week is not counted as 7 independent days.
    (Merging consecutive event days was tried first and collapses to ONE cluster on BTC 1m: SE 0.)"""
    return np.asarray(days) // 7


def classify(mean_diff, upper, n_days=10**6):
    """dead = upper CI below fee (H1 kill); alive = mean at or above fee with >= 30 independent days (OPUS_FRAMING s4.5);
    else inconclusive (CI too wide to kill, or too few days to call it alive)."""
    if is_dead(upper):
        return "dead"
    return "alive" if mean_diff >= FEE and n_days >= 30 else "inconclusive"


def trailing_vol(close, w=VOL_BARS):
    lr = np.r_[np.nan, np.diff(np.log(close))]
    z = np.where(np.isnan(lr), 0.0, lr)
    c1, c2 = np.r_[0, np.cumsum(z)], np.r_[0, np.cumsum(z * z)]
    n = len(close)
    v = np.full(n, np.nan)
    i = np.arange(w, n)
    hi_i = i + 1                        # cumsum index that includes bar i (bars i-w+1..i, never later)
    lo_i = hi_i - w
    s1, s2 = c1[hi_i] - c1[lo_i], c2[hi_i] - c2[lo_i]
    v[w:] = np.sqrt(np.maximum(s2 / w - (s1 / w) ** 2, 0.0))
    return v


def cell_ids(t_ms, vol, tf):
    """(UTC hour, causal vol tercile) cell per bar; -1 where undefined."""
    step = 1440 // tf
    cuts = block_percentiles(vol, [100 / 3, 200 / 3], 90 * step, step)
    ter = np.where(vol <= cuts[:, 0], 0, np.where(vol <= cuts[:, 1], 1, 2))
    hour = (t_ms // 3_600_000) % 24
    cid = (hour * 3 + ter).astype(int)
    cid[np.isnan(cuts[:, 0]) | np.isnan(vol)] = -1
    return cid


def path_stats(d, ev, h, level_arr, tf):
    """Per-event outcomes over the h bars after the fill (all measured from the fill price = next open)."""
    o, hi, lo, cl = d["open"], d["high"], d["low"], d["close"]
    n = len(o)
    lower = []
    bounce = []
    mfe = []
    mae = []
    for i in ev:
        a, b = i + 1, i + 1 + h
        if b > n:
            lower.append(np.nan); bounce.append(np.nan); mfe.append(np.nan); mae.append(np.nan)
            continue
        fill = o[a]
        lower.append(float(lo[a:b].min() < fill))
        bounce.append(float(cl[a:b].max() >= fill * (1 + FEE)))
        mfe.append(hi[a:b].max() / fill - 1)
        mae.append(lo[a:b].min() / fill - 1)
    return np.array(lower), np.array(bounce), np.array(mfe), np.array(mae)


def episode_stats(d, rsi, ev, lv, targets=(40.0, 50.0, 60.0)):
    """Descriptive (hindsight) per-episode numbers: RSI-min to price-min lag and trough close -> first close at RSI target."""
    lo, cl = d["low"], d["close"]
    lag_b, lag_p = [], []
    move = {x: [] for x in targets}
    for i in ev:
        L = lv[i]
        seg = _win(rsi, i, i + EPISODE_CAP + 1)     # hindsight episode window, descriptive only
        back = np.nonzero(seg >= L + HYST)[0]
        end = i + (back[0] - 1 if len(back) and back[0] > 0 else EPISODE_CAP)
        k = i + int(np.nanargmin(rsi[i:end + 1]))
        p = i + int(np.argmin(lo[i:end + 1]))
        lag_b.append(p - k)
        lag_p.append(lo[p] / cl[k] - 1)
        win = _win(rsi, k + 1, k + 1 + TARGET_CAP)  # hindsight, descriptive only
        for x in targets:
            hit = np.nonzero(win >= x)[0]
            move[x].append(cl[k + 1 + hit[0]] / cl[k] - 1 if len(hit) else np.nan)
    return np.array(lag_b, float), np.array(lag_p), {x: np.array(v) for x, v in move.items()}


def analyse_tf(d1, tf, rows, notes):
    d = resample(d1, tf)
    n = len(d["open"])
    rsi = rsi_series(d["close"])
    step = 1440 // tf
    levels = [(f"abs{int(L)}", L) for L in ABS_LEVELS]
    levels.append(("rel_p2_90d", relative_level(rsi, 90 * step, step)))
    vol = trailing_vol(d["close"])
    cid = cell_ids(d["open_time"], vol, tf)
    day = d["open_time"] // DAY_MS
    base = {}
    for h in HORIZONS:
        g_all = forward_gross(d["open"], np.arange(n - 1), h)
        ok = ~np.isnan(g_all) & (cid[:n - 1] >= 0)
        s = np.bincount(cid[:n - 1][ok], weights=g_all[ok], minlength=72)
        c = np.bincount(cid[:n - 1][ok], minlength=72)
        base[h] = (np.where(c > 0, s / np.maximum(c, 1), np.nan), float(g_all[ok].mean()))
    best = []
    for name, L in levels:
        ev, lv = find_events(rsi, L)
        ev = [i for i in ev if i + 1 < n]
        evi = np.array(ev, dtype=int)
        rows.append((tf, name, "all", "n_episodes", len(ev)))
        if len(ev) < 5:
            notes.append(f"{tf}m {name}: only {len(ev)} episodes, no CI")
            continue
        lag_b, lag_p, move = episode_stats(d, rsi, ev, lv)
        rows += [(tf, name, "lag", "median_rsi_min_to_price_min_bars", float(np.median(lag_b))),
                 (tf, name, "lag", "p90_rsi_min_to_price_min_bars", float(np.percentile(lag_b, 90))),
                 (tf, name, "lag", "median_price_min_vs_rsi_min_close_pct", float(np.median(lag_p) * 100))]
        for x, mv in move.items():
            got = mv[~np.isnan(mv)]
            rows.append((tf, name, f"c12_rsi{int(x)}", "share_reached", len(got) / len(mv)))
            if len(got):
                rows += [(tf, name, f"c12_rsi{int(x)}", "median_move_pct", float(np.median(got) * 100)),
                         (tf, name, f"c12_rsi{int(x)}", "mean_move_pct", float(got.mean() * 100)),
                         (tf, name, f"c12_rsi{int(x)}", "median_fee_multiple", float(np.median(got) / FEE)),
                         (tf, name, f"c12_rsi{int(x)}", "share_move_ge_1_fee", float((got >= FEE).mean()))]
        per_h = []
        for h in HORIZONS:
            g = forward_gross(d["open"], evi, h)
            ok = ~np.isnan(g) & (cid[evi] >= 0)
            if ok.sum() < 5:
                continue
            gg, e_i = g[ok], evi[ok]
            diff = gg - base[h][0][cid[e_i]]
            days = day[e_i]
            m, se = cluster_mean_se(diff, days)
            _, se_w = cluster_mean_se(diff, week_clusters(days))
            lower, bounce, mfe, mae = path_stats(d, e_i.tolist(), h, lv, tf)
            tag = f"h{h}"
            vals = {"n_events": int(ok.sum()), "n_days": int(len(np.unique(days))),
                    "mean_gross_pct": gg.mean() * 100, "mean_baseline_pct": (gg - diff).mean() * 100,
                    "mean_diff_pct": m * 100, "se_day_pct": se * 100,
                    "ci_hi_day_pct": (m + Z95 * se) * 100, "ci_hi_week_pct": (m + Z95 * se_w) * 100,
                    "mde_80pct_power_pct": Z_POWER * se * 100, "fee_pct": FEE * 100,
                    "p_lower_low_than_fill": np.nanmean(lower), "p_close_ge_fill_plus_fee": np.nanmean(bounce),
                    "median_bounce_mfe_pct": np.nanmedian(mfe) * 100, "median_mae_pct": np.nanmedian(mae) * 100}
            for k, v in vals.items():
                rows.append((tf, name, tag, k, float(v)))
            per_h.append((m, m + Z95 * se, h, int(len(np.unique(days)))))
        if per_h:
            m, up, h, nd = max(per_h)
            best.append((name, h, m, up))
            rows += [(tf, name, "verdict", "best_horizon_bars", h), (tf, name, "verdict", "best_mean_diff_pct", m * 100),
                     (tf, name, "verdict", "best_ci_hi_day_pct", up * 100),
                     (tf, name, "verdict", "level_class", classify(m, up, nd))]
    tf_dead = bool(best) and all(is_dead(b[3]) for b in best)
    rows.append((tf, "ALL", "verdict", "tf_dead", int(tf_dead)))
    return tf_dead, n


def write_outputs(rows, notes, meta, outdir):
    with open(outdir / "ECON_FLOOR.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["tf_min", "level", "section", "stat", "value"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], f"{r[4]:.6g}" if isinstance(r[4], float) else r[4]])


def _get(rows, tf, level, section, stat):
    for r in rows:
        if r[0] == tf and r[1] == level and r[2] == section and r[3] == stat:
            return r[4]
    return None


def _f(v, nd=4):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def write_md(rows, notes, meta, outdir):
    levels = [f"abs{int(L)}" for L in ABS_LEVELS] + ["rel_p2_90d"]
    L = ["# ECON_FLOOR: Stage 0 economic-floor kill test (RSI deep-buy)", "",
         "BTCUSDT 1m, DEV only (bars opened before 2024-07-01; loader refuses later bars). RSI14 Wilder on 1m/15m/1h. "
         f"Fee {FEE * 100:.2f}% round trip (SOURCED backtest/fees.py, 2 x BINANCE_TAKER). Fill = next bar open, exit = open h bars later. "
         "Episode = RSI <= level after >= level+3 (h=3, OURS). Relative level = trailing-90d 2nd percentile (causal, refreshed daily-block). "
         "Baseline = mean forward return of all bars in the same UTC-hour x trailing-vol tercile cell. CI = day-clustered 95%; week-block CI shown for stress clustering. "
         f"Data: {meta['bars']} 1m bars from {meta['files']} monthly files, {meta['gaps']} time gaps.", "",
         "## H1 verdict", ""]
    allhard = True
    for tf in TFS:
        L.append(f"**{tf}m: {'DEAD' if meta['tf_dead'][tf] else 'NOT DEAD'}**")
        allhard &= meta["tf_dead"][tf]
        for lv in levels:
            cls = _get(rows, tf, lv, "verdict", "level_class")
            if cls is None:
                L.append(f"- {lv}: n/a ({_get(rows, tf, lv, 'all', 'n_episodes')} episodes, too few for a CI)")
                continue
            L.append(f"- {lv}: {cls}; best horizon {_get(rows, tf, lv, 'verdict', 'best_horizon_bars')} bars, mean (gross - baseline) "
                     f"{_f(_get(rows, tf, lv, 'verdict', 'best_mean_diff_pct'))}%, upper day-clustered 95% CI "
                     f"{_f(_get(rows, tf, lv, 'verdict', 'best_ci_hi_day_pct'))}% vs fee {FEE * 100:.2f}%")
        L.append("")
    L += [f"Study-level: {'ALL TFs DEAD, stop the study.' if allhard else 'not all TFs dead, the study is not stopped by H1.'} "
          "Class meaning: dead = upper CI below fee; inconclusive = mean below fee but the CI is too wide to exclude it (low n); alive = mean at or above fee.", "",
          "## Per-TF gross forward return (event minus matched baseline), % of price", "",
          "| TF | level | h | n events | n days | gross % | baseline % | diff % | CI hi day % | CI hi week % | MDE 80% % |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for tf in TFS:
        for lv in levels:
            for h in HORIZONS:
                s = f"h{h}"
                if _get(rows, tf, lv, s, "n_events") is None:
                    continue
                g = lambda k, nd=4: _f(_get(rows, tf, lv, s, k), nd)
                L.append(f"| {tf}m | {lv} | {h} | {int(_get(rows, tf, lv, s, 'n_events'))} | {int(_get(rows, tf, lv, s, 'n_days'))} | "
                         f"{g('mean_gross_pct')} | {g('mean_baseline_pct')} | {g('mean_diff_pct')} | {g('ci_hi_day_pct')} | {g('ci_hi_week_pct')} | {g('mde_80pct_power_pct')} |")
    L += ["", "## Bounce, adverse move and lower-low odds (from the fill price)", "",
          "| TF | level | h | P(lower low than fill) | P(close >= fill+fee) | median MFE % | median MAE % |", "|---|---|---|---|---|---|---|"]
    for tf in TFS:
        for lv in levels:
            for h in HORIZONS:
                s = f"h{h}"
                if _get(rows, tf, lv, s, "n_events") is None:
                    continue
                g = lambda k: _f(_get(rows, tf, lv, s, k), 3)
                L.append(f"| {tf}m | {lv} | {h} | {g('p_lower_low_than_fill')} | {g('p_close_ge_fill_plus_fee')} | {g('median_bounce_mfe_pct')} | {g('median_mae_pct')} |")
    L += ["", "## RSI minimum to price minimum lag (hindsight, descriptive; episode window up to 200 bars)", "",
          "| TF | level | episodes | median lag bars | p90 lag bars | median price-min vs close at RSI-min % |", "|---|---|---|---|---|---|"]
    for tf in TFS:
        for lv in levels:
            if _get(rows, tf, lv, "lag", "median_rsi_min_to_price_min_bars") is None:
                continue
            L.append(f"| {tf}m | {lv} | {_get(rows, tf, lv, 'all', 'n_episodes')} | {_f(_get(rows, tf, lv, 'lag', 'median_rsi_min_to_price_min_bars'), 1)} | "
                     f"{_f(_get(rows, tf, lv, 'lag', 'p90_rsi_min_to_price_min_bars'), 1)} | {_f(_get(rows, tf, lv, 'lag', 'median_price_min_vs_rsi_min_close_pct'), 3)} |")
    L += ["", "## C12: RSI trough close to first close at RSI 40/50/60 (hindsight trough, descriptive; search capped at 5000 bars)", "",
          "Fee multiple = move / 0.10%. Not a tradeable entry (the trough is known only afterwards).", "",
          "| TF | level | target | share reached | median move % | mean move % | median fee multiple | share >= 1 fee |", "|---|---|---|---|---|---|---|---|"]
    for tf in TFS:
        for lv in levels:
            for x in (40, 50, 60):
                s = f"c12_rsi{x}"
                if _get(rows, tf, lv, s, "share_reached") is None:
                    continue
                g = lambda k, nd=3: _f(_get(rows, tf, lv, s, k), nd)
                L.append(f"| {tf}m | {lv} | RSI {x} | {g('share_reached')} | {g('median_move_pct')} | {g('mean_move_pct')} | {g('median_fee_multiple', 2)} | {g('share_move_ge_1_fee')} |")
    L += ["", "## Notes and decisions", ""] + [f"- {n}" for n in notes] + [
        "- DECISION (OURS): TF verdict = dead only if EVERY level with a CI has upper bound below fee at its best horizon (best = max mean diff). Hard to kill by design; low-n levels stay inconclusive.",
        "- DECISION (OURS): the first stress-cluster idea (merge consecutive event days) collapses to one cluster on BTC, so a 7-day block CI is reported next to the day CI. Verdict uses the day CI as the card says.",
        "- DECISION (OURS): matched baseline is the cell mean of all bars (UTC hour x trailing-vol tercile, causal vol cuts), a deterministic stand-in for random matched bars; it uses future bars of the sample only as a benchmark, never in a decision.",
        "- DECISION (OURS): first 200 bars per TF are dropped (RSI warm-up); the relative level starts after 90 days of history, so 2022-01..03 has no relative events.",
        "- CAUTION: 'alive' = best of three horizons picked on its own mean (selection bias) with its CI lower bound far below the fee (60m abs20: 36 days, 46 episodes, one crash-heavy sample). It is a lead for Stage 1, not an edge.",
        "- Horizons are bars of the TF (1m: 1/4/16 minutes; 15m: 15/60/240 min; 1h: 1/4/16 hours). The 0.10% fee is a hard floor in price terms on every TF.",
        "- Overlap: episodes inside one hour or one crash are not independent; days (and weeks) are the unit of evidence. No VALIDATION or HOLDOUT bar was read."]
    (outdir / "ECON_FLOOR.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    files = sorted(p for p in Path(a.klines).glob("BTCUSDT-1m-*.csv") if p.stem[-7:] < "2024-07")
    d1 = load_klines(files)
    gaps = int((np.diff(d1["open_time"]) != 60_000).sum())
    rows, notes, tf_dead = [], [f"1m time gaps in DEV: {gaps}"], {}
    for tf in TFS:
        tf_dead[tf], n = analyse_tf(d1, tf, rows, notes)
        print(f"tf={tf}m bars={n} dead={tf_dead[tf]}", flush=True)
    meta = {"bars": len(d1["open_time"]), "files": len(files), "gaps": gaps, "tf_dead": tf_dead}
    write_outputs(rows, notes, meta, Path(a.out))
    write_md(rows, notes, meta, Path(a.out))
    return rows, notes, meta


if __name__ == "__main__":
    main()
