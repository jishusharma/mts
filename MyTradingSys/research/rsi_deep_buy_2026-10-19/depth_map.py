"""RSI depth map, DEV only (SPEC.md s2 Steps A-C; card rsi-deep-depth-map).

Per RSI timeframe t in {1m,3m,5m,15m,1h,4h,1d} (RSI14 Wilder on close, resampled from 1m, UTC) and anchor window W in
{1h,4h,1d,1w} (non-overlapping, UTC-aligned, complete windows only, W longer than t):
  A  ranked RSI troughs rank1..5 (local minimum within +-k bars, k in 3,5,10), visit counts with hysteresis h in 2,3,5,
     causal running-record table (n-th new low of the window and the fraction of the window elapsed then)
  B  P_touch per integer level 5..50 (share of windows whose minimum is <= L), mean visits given touched,
     P(2+ visits | touched), days covered by touched windows
  C  rare-zone line L*(q) = highest level with P_touch < q, q in 20%,10%,5%,2%
Reuses econ_floor.py (loader that refuses bars at/after the DEV cutoff, resample, RSI). Output: DEPTH_MAP.csv (aggregates
only, no prices) and DEPTH_MAP.md. Run: python depth_map.py [--klines F:/MTS/data/tom_raw/klines]

Labels. SOURCED: RSI14 on close, UTC, DEV cutoff 2024-07-01 (econ_floor / SPEC s5), the operator's definitions of
trough ladder, visit and P_touch (SPEC s2, operator 2026-10-20). OURS: k, h grids, q grid, level grid 5..50, ranks up to 5
(from the spec, tuned on DEV only), weeks start Monday 00:00 UTC, a window that starts below L counts as armed (its first
bar at/below L is a visit), a trough needs its full +-k neighbourhood inside the window, running record = strict new low.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import econ_floor as ef  # noqa: E402

CUTOFF_MS = ef.CUTOFF_MS
TFS = (1, 3, 5, 15, 60, 240, 1440)                  # minutes, SPEC s2 subset in the card
WINS = (60, 240, 1440, 10080)                       # minutes: 1h, 4h, 1d, 1w
KS = (3, 5, 10)                                     # OURS
HS = (2.0, 3.0, 5.0)                                # OURS
QS = (0.20, 0.10, 0.05, 0.02)                       # OURS
LEVELS = tuple(range(5, 51))                        # OURS
NRANK = 5
MIN_MS = 60_000
DAY_MS = 86_400_000
WEEK_OFFSET_MS = 4 * DAY_MS                         # epoch is a Thursday; shift so weeks start Monday 00:00 UTC


def assert_dev(d):
    """Refuse any bar with open at or after the DEV cutoff (VALIDATION/HOLDOUT are not readable here)."""
    t = np.asarray(d["open_time"])
    if len(t) and t.max() >= CUTOFF_MS:
        raise ValueError("bar with open >= DEV cutoff 2024-07-01 refused")


def window_matrix(t, rsi, tf_min, win_min):
    """Rows = complete UTC-aligned windows (all bars present, no NaN RSI), columns = bars. Returns (matrix, window start ms)."""
    off = WEEK_OFFSET_MS if win_min == 10080 else 0
    wms = win_min * MIN_MS
    g = (t - off) // wms
    ug, start, cnt = np.unique(g, return_index=True, return_counts=True)
    need = win_min // tf_min
    ok = cnt == need
    start, ug = start[ok], ug[ok]
    if len(start) == 0:
        return np.empty((0, need)), np.empty(0, dtype="int64")
    idx = start[:, None] + np.arange(need)[None, :]
    M = rsi[idx]
    good = ~np.isnan(M).any(axis=1)
    return M[good], (ug[good] * wms + off).astype("int64")


def ranked_troughs(R, k, n=NRANK):
    """Per row the n lowest local-minimum values, ascending (nan-padded). A trough is strictly below the k bars before it and
    at or below the k bars after it, all inside the row (an edge bar is never confirmed)."""
    R = np.asarray(R, dtype="float64")
    rows, w = R.shape
    P = np.concatenate([np.full((rows, k), -np.inf), R, np.full((rows, k), -np.inf)], axis=1)
    from numpy.lib.stride_tricks import sliding_window_view
    nb = sliding_window_view(P, 2 * k + 1, axis=1)          # nb[:, i, :] = bars i-k .. i+k of the row (padded)
    is_t = ~np.isnan(R)
    is_t &= (R[:, :, None] < nb[:, :, :k]).all(axis=2)       # strictly below the k bars before
    is_t &= (R[:, :, None] <= nb[:, :, -k:]).all(axis=2)     # at or below the k bars after
    V = np.where(is_t, R, np.inf)
    V.sort(axis=1)
    out = np.full((rows, n), np.nan)
    m = min(n, w)
    top = V[:, :m]
    out[:, :m] = np.where(np.isinf(top), np.nan, top)
    return out


def count_visits(R, level, h):
    """Visits per row: RSI closes at or below `level` after having been at least h above it. A row starts armed."""
    R = np.asarray(R, dtype="float64")
    below = R <= level
    above = R >= level + h
    s = np.where(above, 1, np.where(below, -1, 0)).astype(np.int8)
    pos = np.where(s != 0, np.arange(R.shape[1])[None, :], -1)
    pos = np.maximum.accumulate(pos, axis=1)
    filled = np.where(pos >= 0, np.take_along_axis(s, np.maximum(pos, 0), axis=1), 0)
    prev = np.zeros_like(filled)
    prev[:, 1:] = filled[:, :-1]
    return (below & (prev != -1)).sum(axis=1)


def touch_stats(R, levels, h):
    """{L: stats} with P_touch = share of rows whose minimum is <= L, visits given touched, P(2+ visits | touched)."""
    R = np.asarray(R, dtype="float64")
    n = R.shape[0]
    mins = R.min(axis=1) if n else np.empty(0)
    out = {}
    for L in levels:
        touched = mins <= L
        nt = int(touched.sum())
        if nt:
            v = count_visits(R[touched], L, h)
            mv, p2 = float(v.mean()), float((v >= 2).mean())
        else:
            mv = p2 = float("nan")
        out[L] = {"n_windows": n, "n_touched": nt, "p_touch": nt / n if n else float("nan"),
                  "mean_visits_given_touched": mv, "p_2plus_given_touched": p2, "touched": touched}
    return out


def rare_line(stats, q):
    """L*(q): highest level whose P_touch is below q (P_touch is non-decreasing in L). None if even the lowest level is >= q."""
    ok = [L for L, s in stats.items() if s["p_touch"] < q]
    return max(ok) if ok else None


def running_record_count(R):
    """Per row and bar: how many strict new running lows have been set up to and including that bar (causal)."""
    R = np.asarray(R, dtype="float64")
    filled = np.where(np.isnan(R), np.inf, R)
    prev_min = np.minimum.accumulate(filled, axis=1)
    prev_min = np.concatenate([np.full((R.shape[0], 1), np.inf), prev_min[:, :-1]], axis=1)
    return np.cumsum(filled < prev_min, axis=1)


def days_covered(starts, mask, win_min):
    st = starts[mask] // DAY_MS
    if win_min > 1440:
        st = (st[:, None] + np.arange(win_min // 1440)[None, :]).ravel()
    return int(len(np.unique(st)))


FIELDS = ["kind", "tf_min", "win_min", "k", "h", "q", "level", "rank", "record_n", "n_windows", "n_touched", "p_touch",
          "mean_visits_given_touched", "p_2plus_given_touched", "days_touched", "value_mean", "value_median",
          "value_min", "share_with_rank", "share_reached", "frac_elapsed_median", "rsi_at_record_mean", "l_star"]


def _row(**kw):
    return {f: kw.get(f, "") for f in FIELDS}


def analyse(M, starts, tf, win):
    rows = []
    n = M.shape[0]
    if n == 0:
        return rows
    for k in KS:
        T = ranked_troughs(M, k)
        for r in range(NRANK):
            col = T[:, r]
            have = ~np.isnan(col)
            rows.append(_row(kind="ladder", tf_min=tf, win_min=win, k=k, rank=r + 1, n_windows=n,
                             share_with_rank=have.mean(),
                             value_mean=col[have].mean() if have.any() else "",
                             value_median=np.median(col[have]) if have.any() else "",
                             value_min=col[have].min() if have.any() else ""))
    rc = running_record_count(M)
    w = M.shape[1]
    for r in range(1, NRANK + 1):
        reached = rc.max(axis=1) >= r
        if reached.any():
            first = (rc >= r).argmax(axis=1)[reached]
            frac = (first + 1) / w
            vals = M[reached, first]
            rows.append(_row(kind="record", tf_min=tf, win_min=win, record_n=r, n_windows=n,
                             share_reached=reached.mean(), frac_elapsed_median=np.median(frac),
                             rsi_at_record_mean=vals.mean()))
        else:
            rows.append(_row(kind="record", tf_min=tf, win_min=win, record_n=r, n_windows=n, share_reached=0.0))
    base = None
    for h in HS:
        st = touch_stats(M, LEVELS, h)
        if h == 3.0:
            base = st
        for L in LEVELS:
            s = st[L]
            rows.append(_row(kind="touch", tf_min=tf, win_min=win, h=h, level=L, n_windows=n, n_touched=s["n_touched"],
                             p_touch=s["p_touch"], mean_visits_given_touched=s["mean_visits_given_touched"],
                             p_2plus_given_touched=s["p_2plus_given_touched"],
                             days_touched=days_covered(starts, s["touched"], win)))
    for q in QS:
        ls = rare_line(base, q)
        rows.append(_row(kind="rare", tf_min=tf, win_min=win, q=q, n_windows=n, l_star="" if ls is None else ls))
    return rows


def run(klines):
    files = sorted(p for p in Path(klines).glob("BTCUSDT-1m-*.csv") if p.stem[-7:] < "2024-07")
    d1 = ef.load_klines(files)
    assert_dev(d1)
    rows = []
    for tf in TFS:
        d = ef.resample(d1, tf)
        assert_dev(d)
        rsi = ef.rsi_series(d["close"])
        for win in WINS:
            if win <= tf:
                continue
            M, starts = window_matrix(d["open_time"], rsi, tf, win)
            print(f"tf={tf}m win={win}m windows={len(M)}", flush=True)
            rows.extend(analyse(M, starts, tf, win))
    return rows, int(d1["open_time"].min()), int(d1["open_time"].max())


TFN = {1: "1m", 3: "3m", 5: "5m", 15: "15m", 60: "1h", 240: "4h", 1440: "1d"}
WN = {60: "1h", 240: "4h", 1440: "1d", 10080: "1w"}


def _f(v, p=3):
    return "" if v == "" else f"{float(v):.{p}f}"


def write_md(rows, path, t_min, t_max):
    def sel(**kw):
        return [r for r in rows if all(r[a] == b for a, b in kw.items())]
    iso = lambda ms: str(np.datetime64(int(ms), "ms"))[:10]
    L = []
    L.append("# RSI depth map, DEV only (card rsi-deep-depth-map, SPEC s2 Steps A-C)\n")
    L.append(f"Data: BTCUSDT 1m, {iso(t_min)} to {iso(t_max)} (open < 2024-07-01; no VALIDATION/HOLDOUT bar read). "
             "RSI14 Wilder on close, resampled from 1m, UTC, complete bars and complete windows only. "
             "Source of every number: `DEPTH_MAP.csv` (aggregates only). Generated by `depth_map.py`.\n")
    L.append("Read this first: this is a map of how often RSI reaches each level inside a window. It is descriptive. "
             "It says nothing about price after the touch (Steps D-G, not in this card). The R1 result "
             "(ECON_FLOOR.md): 1m abs30/abs20/rel and 15m rel are dead, abs10 inconclusive, 60m abs20 is a lead, "
             "not an edge; nothing here changes that.\n")
    L.append("## Rare-zone line L*(q)  (h=3; highest level with P_touch < q; `-` = even level 5 is touched in q or more of windows)\n")
    L.append("| RSI TF | window | windows | L*(20%) | L*(10%) | L*(5%) | L*(2%) |\n|---|---|---|---|---|---|---|")
    for tf in TFS:
        for win in WINS:
            rr = {r["q"]: r for r in sel(kind="rare", tf_min=tf, win_min=win)}
            if not rr:
                continue
            cells = [("-" if rr[q]["l_star"] == "" else str(rr[q]["l_star"])) for q in QS]
            L.append(f"| {TFN[tf]} | {WN[win]} | {rr[QS[0]]['n_windows']} | " + " | ".join(cells) + " |")
    L.append("\n## P_touch at selected levels (h=3), with mean visits given touched and P(2+ visits | touched)\n")
    L.append("Cell = P_touch / mean visits / P(2+). Days = distinct UTC days covered by touched windows at level 20 (independent-day count).\n")
    lv = (10, 20, 25, 30, 35, 40, 50)
    L.append("| RSI TF | window | " + " | ".join(f"L={x}" for x in lv) + " | days@20 |\n|---|---|" + "---|" * (len(lv) + 1))
    for tf in TFS:
        for win in WINS:
            t3 = {r["level"]: r for r in sel(kind="touch", tf_min=tf, win_min=win, h=3.0)}
            if not t3:
                continue
            cells = []
            for x in lv:
                r = t3[x]
                cells.append(f"{_f(r['p_touch'])} / {_f(r['mean_visits_given_touched'], 2) or 'n/a'} / {_f(r['p_2plus_given_touched'], 2) or 'n/a'}")
            L.append(f"| {TFN[tf]} | {WN[win]} | " + " | ".join(cells) + f" | {t3[20]['days_touched']} |")
    L.append("\n## Ranked troughs (k=5): mean RSI value of rank1..rank5 per window (share of windows that have that rank in brackets)\n")
    L.append("| RSI TF | window | rank1 | rank2 | rank3 | rank4 | rank5 |\n|---|---|---|---|---|---|---|")
    for tf in TFS:
        for win in WINS:
            lad = {r["rank"]: r for r in sel(kind="ladder", tf_min=tf, win_min=win, k=5)}
            if not lad:
                continue
            L.append(f"| {TFN[tf]} | {WN[win]} | " + " | ".join(
                f"{_f(lad[i]['value_mean'], 1) or 'n/a'} ({_f(lad[i]['share_with_rank'], 2)})" for i in range(1, NRANK + 1)) + " |")
    L.append("\n## Running record (causal): n-th new low inside the window; cell = share of windows reaching record n / median fraction of the window elapsed when it is set\n")
    L.append("| RSI TF | window | record 1 | record 2 | record 3 | record 4 | record 5 |\n|---|---|---|---|---|---|---|")
    for tf in TFS:
        for win in WINS:
            rec = {r["record_n"]: r for r in sel(kind="record", tf_min=tf, win_min=win)}
            if not rec:
                continue
            L.append(f"| {TFN[tf]} | {WN[win]} | " + " | ".join(
                f"{_f(rec[i]['share_reached'], 2)} / {_f(rec[i]['frac_elapsed_median'], 2) or 'n/a'}" for i in range(1, NRANK + 1)) + " |")
    L.append("""
## FIXED vs VARIED (every parameter labelled)

FIXED:
- RSI period 14 on close, Wilder, UTC alignment, complete bars only: SOURCED (econ_floor.py, `rsi_core`; SPEC s5).
- DEV = bars with open < 2024-07-01 only; the loader refuses anything later: SOURCED (SPEC s5, econ_floor.py `CUTOFF_MS`).
- Window = non-overlapping UTC block, complete only (a window with a missing bar or an undefined RSI is dropped): OURS.
- Weeks start Monday 00:00 UTC (the epoch is a Thursday, so a shift is applied): OURS.
- A window starts armed (if it opens at or below L its first such bar is a visit; so every touched window has >= 1 visit): OURS.
- A trough needs its full +-k neighbourhood inside the window (strictly below the k bars before, at or below the k after), so a window edge is never a trough: OURS.
- Running record = strict new running low; fraction elapsed = (bar index + 1) / bars in window: OURS.
- Level grid = integers 5..50: OURS (SPEC s2).
- Rare-zone line L*(q) = highest level with P_touch < q (P_touch rises with L, so this is the edge of the rare region): OURS.

VARIED (rows in the CSV; every value is a trial row in the ledger, none is preferred here):
- RSI timeframe t in 1m, 3m, 5m, 15m, 1h, 4h, 1d; window W in 1h, 4h, 1d, 1w with W longer than t: OURS (SPEC s2; 2m and 30m left out by the card).
- Trough half-width k in 3, 5, 10: OURS. The markdown shows k=5 only; all three are in the CSV.
- Hysteresis h in 2, 3, 5 points: OURS. The markdown shows h=3 (the study-wide fixed value, OPUS_FRAMING s1); L*(q) is computed at h=3 and does not depend on h.
- q in 20%, 10%, 5%, 2%: OURS, to be tuned on DEV, checked once on VALIDATION.

Caveats. Hindsight: the ranked-trough ladder uses the whole completed window, so it is descriptive and may not condition a trade; the running-record table is causal (bar t depends on bars up to t only, tested). 1d and 4h timeframes have few windows in 30 months, see the `windows` column before reading a cell. Windows of the same day are not independent; the independent-day count is in the days column and the CSV.
""")
    Path(path).write_text("\n".join(L), encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    rows, t0, t1 = run(a.klines)
    out = Path(a.out)
    with open(out / "DEPTH_MAP.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, (float, np.floating)) else v) for k, v in r.items()})
    write_md(rows, out / "DEPTH_MAP.md", t0, t1)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
