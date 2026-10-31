"""P1 pipeline: join event days to phase tags, per-cell stats, family-wise shift test (PRE_REG.md)."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "phase_tag"))
import harness  # noqa: E402

DEV_START, DEV_END = pd.Timestamp("2022-01-01"), pd.Timestamp("2024-06-30")
TAGS = ("cowen_side", "sma200_side", "wsma10_phase")


def load_tags(path=None):
    return pd.read_csv(path or os.path.join(HERE, "..", "phase_tag", "tags.csv"), parse_dates=["date"])


def join_events(events, tags, tag):
    """events: DataFrame[date, r]. Tag of event day t = tags row dated t (itself built from bars <= t-1).
    Returns DataFrame[date, r, label, week_parity] in time order, DEV only, blank tags dropped."""
    ev = events.copy()
    ev["date"] = pd.to_datetime(ev["date"]).dt.normalize()
    ev = ev[(ev["date"] >= DEV_START) & (ev["date"] <= DEV_END)].sort_values("date", kind="stable")
    m = ev.merge(tags[["date", tag]], on="date", how="left").rename(columns={tag: "label"})
    m = m[m["label"].notna() & (m["label"].astype(str) != "")].reset_index(drop=True)
    m["week_parity"] = (m["date"].dt.isocalendar().week.astype(int) % 2).astype(str)
    return m


def block_ci(y, dates, block_days=10, n_boot=2000, rng=None):
    rng = rng or np.random.default_rng(0)
    y = np.asarray(y, float)
    if len(y) == 0:
        return (float("nan"), float("nan"))
    b = np.asarray((pd.DatetimeIndex(dates) - pd.Timestamp("2000-01-01")).days) // block_days
    ub = np.unique(b)
    groups = [y[b == u] for u in ub]
    means = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.integers(0, len(groups), len(groups))
        means[i] = np.concatenate([groups[j] for j in pick]).mean()
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


def _episodes(dates, mask):
    """Three longest runs of consecutive labelled events' calendar span for one cell -> list of index arrays."""
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return []
    d = pd.to_datetime(dates).to_numpy()
    runs, cur = [], [idx[0]]
    for a, b in zip(idx[:-1], idx[1:]):
        if b == a + 1:
            cur.append(b)
        else:
            runs.append(cur)
            cur = [b]
    runs.append(cur)
    runs.sort(key=len, reverse=True)
    return [np.array(r) for r in runs[:3]]


def analyse(m, label_col="label", n_shifts=1000, rng=None):
    """Per-cell table plus flagged cells for one label column. Verdict per PRE_REG section 1."""
    rng = rng or np.random.default_rng(1)
    y = m["r"].to_numpy(float)
    names = sorted(m[label_col].unique())
    lab = m[label_col].map({n: i for i, n in enumerate(names)}).to_numpy(int)
    nt = harness.shift_null_test(y, lab, n_shifts=n_shifts, rng=rng) if len(names) > 1 else {"flagged": [], "gaps": {}}
    pooled = y.mean()
    years = m["date"].dt.year.to_numpy()
    rows = []
    for i, nme in enumerate(names):
        mask = lab == i
        n = int(mask.sum())
        mean = float(y[mask].mean())
        lo, hi = block_ci(y[mask], m["date"][mask], rng=rng)
        row = {"cell": nme, "n": n, "mean_r": mean, "ci_lo": lo, "ci_hi": hi, "flagged": i in nt["flagged"]}
        if n < 30:
            row["verdict"] = "N_TOO_SMALL"
        elif n < 200:
            row["verdict"] = "REPORT_ONLY"
        elif not row["flagged"]:
            row["verdict"] = "FAIL"
        else:
            sgn = np.sign(mean - pooled)
            yrs = [yy for yy in np.unique(years[mask]) if (mask & (years == yy)).sum() >= 10]
            ok_y = len(yrs) >= 2 and all(np.sign(y[mask & (years == yy)].mean() - pooled) == sgn for yy in yrs)
            eps = _episodes(m["date"], mask)
            good = 0
            for e in eps:
                elo, ehi = block_ci(y[e], m["date"].iloc[e], rng=rng)
                same = np.sign(y[e].mean() - pooled) == sgn
                crosses = (sgn > 0 and ehi < pooled) or (sgn < 0 and elo > pooled)
                good += int(same and not crosses)
            row["verdict"] = "PASS" if (ok_y and len(eps) >= 3 and good >= 2) else "NOT_DECIDABLE"
        rows.append(row)
    return pd.DataFrame(rows), nt
