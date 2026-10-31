"""Krown "silver cross" (daily EMA21 crosses above EMA55), 1-month hold, DEV-only fee-net check. PRE_REG.md is the spec.

Run: python silver_cross_dev.py [--klines F:/MTS/data/tom_raw/klines]
Refuses to run unless PRE_REG.md ends with a FROZEN_UTC line. Reads klines 2022-01..2024-06 only (loader refuses any bar
opening at/after 2024-07-01). Fee = 2 x fees.BINANCE_TAKER (SOURCED backtest/fees.py). Everything else is labelled in PRE_REG.md.
Output: RESULT.csv (aggregates and per-event rows, no account data).
"""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MTS = HERE.parents[1]
sys.path.insert(0, str(MTS / "backtest"))
import fees  # noqa: E402

FEE_RT = fees.BINANCE_TAKER * 2                 # SOURCED fees.py (0.10 % round trip)
FAST, SLOW, HOLD = 21, 55, 30                    # 21/55 SOURCED (bXug2l6qICc 00:00:44); 30 days OURS ("one month")
CUTOFF_MS = int(np.datetime64("2024-07-01T00:00", "ms").astype("int64"))
FIRST_EVENT_MS = int(np.datetime64("2022-04-01T00:00", "ms").astype("int64"))
DAY_MS = 86_400_000
BOOT_N, SEED = 10000, 20261031                   # OURS
CLAIM_HIT = 0.83                                 # SOURCED bXug2l6qICc 00:03:08


def require_frozen(path):
    txt = Path(path).read_text(encoding="utf-8")
    last = [ln for ln in txt.splitlines() if ln.strip()][-1] if txt.strip() else ""
    if not last.startswith("FROZEN_UTC:"):
        raise SystemExit("PRE_REG.md is not frozen (last line must be FROZEN_UTC: ...); refusing to run")
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_klines(paths, cutoff_ms=CUTOFF_MS):
    import pandas as pd
    df = pd.concat([pd.read_csv(p, usecols=["open_time", "open", "high", "low", "close"]) for p in paths], ignore_index=True)
    t = df["open_time"].to_numpy(dtype="int64")
    if len(t) and t.max() > 10**14:
        t = t // 1000
    if len(t) and t.max() >= cutoff_ms:
        raise ValueError("bar with open >= DEV cutoff 2024-07-01 refused (VALIDATION/HOLDOUT not readable here)")
    order = np.argsort(t, kind="stable")
    t = t[order]
    keep = np.r_[True, np.diff(t) > 0]
    out = {"open_time": t[keep]}
    for k in ("open", "high", "low", "close"):
        out[k] = df[k].to_numpy(dtype="float64")[order][keep]
    return out


def daily(d):
    """Complete UTC daily bars (1440 one-minute bars). Returns dict of arrays with day-start ms."""
    g = d["open_time"] // DAY_MS
    ug, start, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == 1440
    start, cnt, ug = start[ok], cnt[ok], ug[ok]
    end = start + cnt
    return {"day_ms": ug * DAY_MS,
            "open": d["open"][start],
            "high": np.array([d["high"][s:e].max() for s, e in zip(start, end)]),
            "low": np.array([d["low"][s:e].min() for s, e in zip(start, end)]),
            "close": d["close"][end - 1]}


def ema(x, span):
    a = 2.0 / (span + 1.0)
    out = np.empty(len(x), dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out


def cross_up_days(close, fast=FAST, slow=SLOW):
    """Day indices t where diff(t-1) <= 0 and diff(t) > 0 (diff = EMA fast - EMA slow). Uses closes up to t only."""
    close = np.asarray(close, dtype=float)
    if len(close) < 2:
        return np.array([], dtype=int)
    diff = ema(close, fast) - ema(close, slow)
    return np.flatnonzero((diff[:-1] <= 0) & (diff[1:] > 0)) + 1


def trades(opens, closes, fast=FAST, slow=SLOW, hold=HOLD, first_day=0):
    """One trade per cross at index t >= first_day: entry open[t+1], exit open[t+1+hold]; dropped if the exit is beyond the data."""
    out = []
    n = len(closes)
    for t in cross_up_days(closes, fast, slow):
        t = int(t)
        if t < first_day:
            continue
        ei, xi = t + 1, t + 1 + hold
        if xi >= n:
            continue
        gross = opens[xi] / opens[ei] - 1.0
        net = gross - FEE_RT
        out.append({"cross_i": t, "entry_i": ei, "exit_i": xi, "gross": gross, "net": net, "hit": bool(net > 0)})
    return out


def block_ids(entry_idx, hold=HOLD):
    """Chain entries within `hold` days of the previous entry into one block (overlapping holds)."""
    ids, b, prev = [], 0, None
    for e in entry_idx:
        if prev is not None and e - prev > hold:
            b += 1
        ids.append(b)
        prev = e
    return ids


def boot_ci(values, blocks, n=BOOT_N, seed=SEED):
    """Resample whole blocks with replacement. Returns (mean_lo, mean_hi, hit_lo, hit_hi) of net return and share > 0."""
    v = np.asarray(values, dtype=float)
    b = np.asarray(blocks)
    groups = [v[b == k] for k in np.unique(b)]
    rng = np.random.default_rng(seed)
    means, hits = [], []
    for _ in range(n):
        pick = rng.integers(0, len(groups), len(groups))
        s = np.concatenate([groups[i] for i in pick])
        means.append(s.mean())
        hits.append((s > 0).mean())
    q = lambda a: (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)))
    return q(means) + q(hits)


def atr_ema(high, low, close, n=14):
    pc = np.r_[close[0], close[:-1]]
    tr = np.maximum(high - low, np.maximum(abs(high - pc), abs(low - pc)))
    out = np.empty(len(tr))
    out[0] = tr[0]
    for i in range(1, len(tr)):
        out[i] = out[i - 1] + (tr[i] - out[i - 1]) / n
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--prereg", default=str(HERE / "PRE_REG.md"))
    ap.add_argument("--out", default=str(HERE / "RESULT.csv"))
    a = ap.parse_args(argv)
    sha = require_frozen(a.prereg)
    paths = [Path(a.klines) / f"BTCUSDT-1m-{y}-{m:02d}.csv" for y in (2022, 2023, 2024) for m in range(1, 13)
             if (y, m) <= (2024, 6)]
    d = daily(load_klines(paths))
    day = d["day_ms"]
    contiguous = bool(np.all(np.diff(day) == DAY_MS))
    first_day = int(np.searchsorted(day, FIRST_EVENT_MS))
    tr = trades(d["open"], d["close"], first_day=first_day)
    atr = atr_ema(d["high"], d["low"], d["close"])
    rows = []
    for t in tr:
        if not contiguous and day[t["exit_i"]] - day[t["entry_i"]] != HOLD * DAY_MS:
            continue                                  # gap in the daily series: hold would not be 30 calendar days
        risk = 2 * atr[t["cross_i"]] / d["open"][t["entry_i"]]
        t["R"] = t["net"] / risk
        t["entry_date"] = str(np.datetime64(int(day[t["entry_i"]]), "ms"))[:10]
        rows.append(t)
    # all-days baseline, same rule, context only
    allnet = np.array([d["open"][i + HOLD] / d["open"][i] - 1 - FEE_RT for i in range(first_day, len(day) - HOLD)
                       if day[i + HOLD] - day[i] == HOLD * DAY_MS])
    n = len(rows)
    net = np.array([r["net"] for r in rows])
    blocks = block_ids([r["entry_i"] for r in rows])
    ci = boot_ci(net, blocks) if n else (float("nan"),) * 4
    summ = {"prereg_sha256": sha, "n_events": n, "n_blocks": (max(blocks) + 1) if n else 0,
            "hit_rate": float((net > 0).mean()) if n else float("nan"),
            "mean_net_ret": float(net.mean()) if n else float("nan"),
            "mean_R": float(np.mean([r["R"] for r in rows])) if n else float("nan"),
            "ci_mean_lo": ci[0], "ci_mean_hi": ci[1], "ci_hit_lo": ci[2], "ci_hit_hi": ci[3],
            "claim_hit": CLAIM_HIT, "fee_rt": FEE_RT, "baseline_n": len(allnet),
            "baseline_hit": float((allnet > 0).mean()), "baseline_mean_net": float(allnet.mean()),
            "daily_bars": len(day), "contiguous": contiguous, "first_day_idx": first_day}
    with open(a.out, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["key", "value"])
        for k, v in summ.items():
            w.writerow([k, v])
        w.writerow([])
        w.writerow(["entry_date", "gross", "net", "hit", "R"])
        for r in rows:
            w.writerow([r["entry_date"], f"{r['gross']:.6f}", f"{r['net']:.6f}", r["hit"], f"{r['R']:.4f}"])
    for k, v in summ.items():
        print(k, v)
    for r in rows:
        print(r["entry_date"], f"{r['gross']:.4f}", f"{r['net']:.4f}", r["hit"], f"{r['R']:.3f}")


if __name__ == "__main__":
    main()
