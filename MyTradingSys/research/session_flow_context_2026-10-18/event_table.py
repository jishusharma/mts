"""DEV event table: pattern x context, day-clustered SE, heterogeneity Wald test, split-half sign check, verdict.

Reads rows_dev.csv (build_rows.py, DEV only). Rule and thresholds frozen in PRE_REG.md s.5-6.
  python MyTradingSys/research/session_flow_context_2026-10-18/event_table.py
Writes EVENT_TABLE.csv, HETEROGENEITY.csv and prints the verdict block used in REPORT.md.
"""
import csv
import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent

PATTERNS = ("NEW_LONG", "SHORT_COVER", "NEW_SHORT", "LONG_LIQ", "SR_BEAR", "SR_BULL")
DIMS = ("htf", "rangepos", "vol", "oitrend", "wkend")
M_FAMILY = 87                # OURS: 57 DEV variants already read repo-wide (verdicts.py count --split DEV, 2026-10-23) + 30 tests here
ALPHA = 0.05 / M_FAMILY      # Holm/Bonferroni bound for the first (smallest p) test
MDE_MAX_BPS = 50.0           # OURS: a cell is "powered" only if its MDE is <= 50 bps (about 4x the 12 bps round-trip cost, FORMULAS.md s.13)
POWER_Z = 0.84               # 80 % power (OURS, same as prereg_gate.py)
MIN_DAYS_CELL = 15           # OURS: a cell needs >= 15 distinct days to be tested
SPLIT_DATE = "2025-12-16"    # OURS: H1 = 2025-10-01..2025-12-15, H2 = 2025-12-16..2026-02-28


def direction(pattern, row):
    if pattern == "SR_BEAR":
        return -1
    if pattern == "SR_BULL":
        return 1
    return 1 if row["chg_bps"] > 0 else -1          # quadrant patterns: continuation = the session's own direction


def cluster_mean_se(xs, days):
    """Mean and day-clustered SE (sum of within-day deviations, no small-sample correction) and the number of days."""
    x = np.asarray(xs, dtype=float)
    n = len(x)
    m = x.mean()
    sums = {}
    for v, d in zip(x - m, days):
        sums[d] = sums.get(d, 0.0) + v
    return float(m), math.sqrt(sum(s * s for s in sums.values())) / n, len(sums)


def _gammainc_upper(a, x):
    """Regularised upper incomplete gamma Q(a, x) (series for x < a+1, continued fraction otherwise)."""
    if x <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:
        ap, s, dl = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1
            dl *= x / ap
            s += dl
            if abs(dl) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gln)
    b = x + 1 - a
    c = 1e300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        dl = d * c
        h *= dl
        if abs(dl - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(w, df):
    return _gammainc_upper(df / 2.0, w / 2.0)


def wald_equal_means(xs, days, cells, min_n=10):
    """Cluster-robust Wald test that the cell means are equal. Returns (W, df, p); (nan, 0, nan) if < 2 usable cells."""
    x = np.asarray(xs, dtype=float)
    cells = np.asarray(cells)
    keep = [c for c in sorted(set(cells.tolist())) if (cells == c).sum() >= min_n]
    if len(keep) < 2:
        return float("nan"), 0, float("nan")
    ud = sorted(set(days))
    di = {d: i for i, d in enumerate(ud)}
    dayidx = np.array([di[d] for d in days])
    K = len(keep)
    m = np.zeros(K)
    n = np.zeros(K)
    S = np.zeros((len(ud), K))
    for k, c in enumerate(keep):
        mask = cells == c
        n[k] = mask.sum()
        m[k] = x[mask].mean()
        np.add.at(S[:, k], dayidx[mask], x[mask] - m[k])
    V = (S.T @ S) / np.outer(n, n)
    R = np.hstack([-np.ones((K - 1, 1)), np.eye(K - 1)])
    dvec = R @ m
    cov = R @ V @ R.T
    rank = int(np.linalg.matrix_rank(cov))
    W = float(dvec @ np.linalg.pinv(cov) @ dvec)
    return W, rank, chi2_sf(W, rank)


def load(path):
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            for k in ("chg_bps", "next_ret_bps", "next_range_pct"):
                r[k] = float(r[k])
            out.append(r)
    return out


def events(rows, pattern):
    out = []
    for r in rows:
        hit = r["sr"] == pattern if pattern.startswith("SR_") else r["quadrant"] == pattern
        if hit and not math.isnan(r["next_ret_bps"]):
            out.append((r, direction(pattern, r) * r["next_ret_bps"]))
    return out


def main():
    rows = load(HERE / "rows_dev.csv")
    z = NormalDist().inv_cdf(1 - 0.05 / (2 * M_FAMILY))
    cells_out, het_out = [], []
    for p in PATTERNS:
        ev = events(rows, p)
        xs = [x for _, x in ev]
        days = [r["date"] for r, _ in ev]
        groups = [("ALL", "ALL", list(range(len(ev))))]
        for dim in DIMS:
            for c in sorted(set(r[dim] for r, _ in ev)):
                groups.append((dim, c, [i for i, (r, _) in enumerate(ev) if r[dim] == c]))
        for dim, c, idx in groups:
            if not idx:
                continue
            gx = [xs[i] for i in idx]
            gd = [days[i] for i in idx]
            m, se, nd = cluster_mean_se(gx, gd)
            h1 = [xs[i] for i in idx if days[i] < SPLIT_DATE]
            h2 = [xs[i] for i in idx if days[i] >= SPLIT_DATE]
            agree = "" if not h1 or not h2 else int((np.mean(h1) > 0) == (np.mean(h2) > 0))
            mean_rng = float(np.mean([ev[i][0]["next_range_pct"] for i in idx])) * 1e4
            cells_out.append({"pattern": p, "dim": dim, "cell": c, "n": len(idx), "n_days": nd, "mean_bps": round(m, 2),
                              "se_day_bps": round(se, 2), "t": round(m / se, 2) if se > 0 else "",
                              "mde_bps": round((z + POWER_Z) * se, 1), "powered": int((z + POWER_Z) * se <= MDE_MAX_BPS and nd >= MIN_DAYS_CELL),
                              "h1_h2_sign_agree": agree, "next_range_bps": round(mean_rng, 1)})
        for dim in DIMS:
            sub = [i for i, (r, _) in enumerate(ev) if r[dim] != "NA"]
            cc = [ev[i][0][dim] for i in sub]
            ok = {c for c in set(cc) if len({days[i] for i in sub if ev[i][0][dim] == c}) >= MIN_DAYS_CELL}
            sub = [i for i in sub if ev[i][0][dim] in ok]
            W, df, pv = wald_equal_means([xs[i] for i in sub], [days[i] for i in sub], [ev[i][0][dim] for i in sub], min_n=1)
            het_out.append({"pattern": p, "dim": dim, "cells_tested": len(ok), "W": round(W, 3) if df else "", "df": df, "p": ("%.4g" % pv) if df else ""})
    with open(HERE / "EVENT_TABLE.csv", "w", newline="\n") as f:
        w = csv.DictWriter(f, list(cells_out[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(cells_out)
    with open(HERE / "HETEROGENEITY.csv", "w", newline="\n") as f:
        w = csv.DictWriter(f, list(het_out[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(het_out)
    tested = [h for h in het_out if h["df"]]
    sig = [h for h in tested if float(h["p"]) <= ALPHA]
    nonall = [c for c in cells_out if c["dim"] != "ALL"]
    powered = sum(c["powered"] for c in nonall)
    agree = [c["h1_h2_sign_agree"] for c in nonall if c["h1_h2_sign_agree"] != ""]
    all_agree = [c["h1_h2_sign_agree"] for c in cells_out if c["dim"] == "ALL" and c["h1_h2_sign_agree"] != ""]
    if sig:
        verdict = "CONSISTENT-DEV (heterogeneity p <= %.2g in %d of %d tests; one VALIDATION check next)" % (ALPHA, len(sig), len(tested))
    elif powered < 0.5 * len(nonall):
        verdict = "INCONCLUSIVE (underpowered: %d of %d context cells have MDE <= %g bps and >= %d days)" % (powered, len(nonall), MDE_MAX_BPS, MIN_DAYS_CELL)
    else:
        verdict = "NOT SUPPORTED on DEV (no heterogeneity at p <= %.2g, cells powered)" % ALPHA
    print("VERDICT:", verdict)
    print("heterogeneity tests %d, smallest p %s, alpha %.3g" % (len(tested), min((float(h["p"]) for h in tested), default=float("nan")), ALPHA))
    print("within-cell H1/H2 sign agreement: %d of %d cells; pooled (ALL) patterns: %d of %d" % (sum(agree), len(agree), sum(all_agree), len(all_agree)))
    print("cells %d, powered %d" % (len(nonall), powered))


if __name__ == "__main__":
    main()
