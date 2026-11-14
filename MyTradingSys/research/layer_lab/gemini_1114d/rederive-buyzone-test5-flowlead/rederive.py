"""Independent re-derivation of buyzone_test5_flowlead_2026-11-14 from PRE_REG.md."""

from __future__ import annotations

import datetime as dt
import json
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

FLOW_DIR = Path(os.environ.get("MTS_FLOW_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test5"))
DATA_DIR = Path(os.environ.get("MTS_DATA_CACHE", "C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d"))


def load_klines() -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray]:
    """Load BTCUSDT 1d klines and drop the last (possibly partial) bar."""
    raw = json.loads((DATA_DIR / "BTCUSDT.json").read_text(encoding="utf-8"))
    raw = raw[:-1]  # drop last bar per PRE_REG.md
    dates = [
        dt.datetime.fromtimestamp(r[0] / 1000.0, tz=dt.timezone.utc).strftime("%Y-%m-%d")
        for r in raw
    ]
    highs = np.array([float(r[2]) for r in raw], dtype=float)
    lows = np.array([float(r[3]) for r in raw], dtype=float)
    closes = np.array([float(r[4]) for r in raw], dtype=float)
    return dates, highs, lows, closes


def compute_phases(dates: List[str], highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, str]:
    """Compute daily phase labels per buyzone_test1_ladder_2026-11-14/PRE_REG.md."""
    n = len(dates)
    sma200 = np.full(n, np.nan)
    sma350 = np.full(n, np.nan)
    for i in range(n):
        if i >= 199:
            sma200[i] = float(np.mean(closes[i - 199 : i + 1]))
        if i >= 349:
            sma350[i] = float(np.mean(closes[i - 349 : i + 1]))

    phases: Dict[str, str] = {}
    for t in range(380, n):
        c = closes[t]
        s200 = sma200[t]
        s200_prev = sma200[t - 30]
        s350 = sma350[t]
        s350_prev = sma350[t - 30]
        max_high_365 = float(np.max(highs[max(0, t - 364) : t + 1]))
        dd = 1.0 - c / max_high_365
        hl = float(np.min(lows[t - 59 : t + 1])) >= float(np.min(lows[t - 179 : t - 59]))

        if c > s200 and s200 > s200_prev:
            label = "UP"
        elif dd >= 0.40 and hl:
            label = "BASE"
        elif c < s350 and s350 < s350_prev and dd >= 0.40:
            label = "POSTPEAK_BEAR"
        elif c < s200 and s200 < s200_prev:
            label = "DOWN"
        else:
            label = "RANGE"
        phases[dates[t]] = label
    return phases


def load_flow_days() -> Dict[str, dict]:
    """Load 2023-01-01+ flow days where both spot and fut exist."""
    spot_dir = FLOW_DIR / "spot"
    fut_dir = FLOW_DIR / "fut"
    spot_files = {p.stem for p in spot_dir.glob("*.json") if p.stem >= "2023-01-01"}
    fut_files = {p.stem for p in fut_dir.glob("*.json") if p.stem >= "2023-01-01"}
    both = sorted(spot_files & fut_files)
    out = {}
    for d in both:
        s = json.loads((spot_dir / f"{d}.json").read_text(encoding="utf-8"))
        f = json.loads((fut_dir / f"{d}.json").read_text(encoding="utf-8"))
        tot = float(s["total"]) + float(f["total"])
        net1 = (float(s["buy1"]) - float(s["sell1"])) + (float(f["buy1"]) - float(f["sell1"]))
        net5 = (float(s["buy5"]) - float(s["sell5"])) + (float(f["buy5"]) - float(f["sell5"]))
        out[d] = {
            "F1": 1e4 * net1 / tot if tot > 0 else 0.0,
            "F5": 1e4 * net5 / tot if tot > 0 else 0.0,
        }
    return out


def assign_quintile(val: float, cuts: np.ndarray) -> int:
    """Assign 1..5 using 20/40/60/80th percentile cutoffs."""
    # cuts = [p20, p40, p60, p80]
    if val <= cuts[0]:
        return 1
    if val <= cuts[1]:
        return 2
    if val <= cuts[2]:
        return 3
    if val <= cuts[3]:
        return 4
    return 5


def compute_spread(vals: np.ndarray, rets: np.ndarray, cuts: np.ndarray) -> Tuple[float, Dict[int, int], Dict[int, float]]:
    """Compute Q5 - Q1 spread in bp and per-quintile counts/means."""
    qs = np.array([assign_quintile(v, cuts) for v in vals])
    counts = {q: int(np.sum(qs == q)) for q in range(1, 6)}
    means = {q: float(np.mean(rets[qs == q])) * 1e4 if counts[q] > 0 else float("nan") for q in range(1, 6)}
    spread = means[5] - means[1]
    return spread, counts, means


def block_bootstrap_ci(
    days: List[str], vals: np.ndarray, rets: np.ndarray, cuts: np.ndarray, n_boot: int = 10000, seed: int = 1114
) -> Tuple[float, float]:
    """7-calendar-day block bootstrap percentile 95% CI of Q5 - Q1 spread (in bp)."""
    qs = np.array([assign_quintile(v, cuts) for v in vals])
    # Group into 7-calendar-day blocks from epoch
    epoch = dt.date(1970, 1, 1)
    blocks_map: Dict[int, List[int]] = {}
    for i, d_str in enumerate(days):
        d_obj = dt.date.fromisoformat(d_str)
        blk = (d_obj - epoch).days // 7
        blocks_map.setdefault(blk, []).append(i)
    block_indices = [np.array(idxs, dtype=int) for idxs in blocks_map.values()]
    n_blocks = len(block_indices)

    # Precompute block sums and counts for Q1 and Q5
    q1_sums = np.array([float(np.sum(rets[idx][qs[idx] == 1])) for idx in block_indices])
    q1_cnts = np.array([int(np.sum(qs[idx] == 1)) for idx in block_indices])
    q5_sums = np.array([float(np.sum(rets[idx][qs[idx] == 5])) for idx in block_indices])
    q5_cnts = np.array([int(np.sum(qs[idx] == 5)) for idx in block_indices])

    rng = np.random.default_rng(seed)
    spreads = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        pick = rng.integers(0, n_blocks, size=n_blocks)
        c1 = int(np.sum(q1_cnts[pick]))
        c5 = int(np.sum(q5_cnts[pick]))
        if c1 == 0 or c5 == 0:
            spreads[b] = float("nan")
        else:
            m1 = float(np.sum(q1_sums[pick])) / c1
            m5 = float(np.sum(q5_sums[pick])) / c5
            spreads[b] = (m5 - m1) * 1e4
    valid = spreads[~np.isnan(spreads)]
    return float(np.percentile(valid, 2.5)), float(np.percentile(valid, 97.5))


def placebo_shuffle(
    phases: List[str], vals: np.ndarray, rets: np.ndarray, cuts: np.ndarray, actual_spread: float, n_draws: int = 2000, seed: int = 1114
) -> Tuple[float, float, float]:
    """Within-phase permutation test, 2000 draws, seed 1114."""
    rng = np.random.default_rng(seed)
    phase_groups: Dict[str, np.ndarray] = {}
    for p in sorted(set(phases)):
        phase_groups[p] = np.array([i for i, ph in enumerate(phases) if ph == p], dtype=int)

    draws = np.empty(n_draws, dtype=float)
    perm_vals = vals.copy()
    for d in range(n_draws):
        for p, idxs in phase_groups.items():
            perm_vals[idxs] = rng.permutation(vals[idxs])
        sp, _, _ = compute_spread(perm_vals, rets, cuts)
        draws[d] = sp
    p025 = float(np.percentile(draws, 2.5))
    p975 = float(np.percentile(draws, 97.5))
    pct = float(np.mean(draws <= actual_spread) * 100.0)
    return p025, p975, pct


def main() -> None:
    dates, highs, lows, closes = load_klines()
    date_to_idx = {d: i for i, d in enumerate(dates)}
    phases_map = compute_phases(dates, highs, lows, closes)
    flow_map = load_flow_days()

    rows = []
    for d, fl in sorted(flow_map.items()):
        idx = date_to_idx.get(d)
        if idx is None or idx + 1 >= len(dates):
            continue
        ret24 = closes[idx + 1] / closes[idx] - 1.0
        ret72 = closes[idx + 3] / closes[idx] - 1.0 if idx + 3 < len(dates) else None
        rows.append(
            {
                "date": d,
                "phase": phases_map[d],
                "F1": fl["F1"],
                "F5": fl["F5"],
                "ret24": float(ret24),
                "ret72": float(ret72) if ret72 is not None else None,
            }
        )

    dev = [r for r in rows if r["date"] <= "2023-12-31"]
    val = [r for r in rows if r["date"] >= "2024-01-01"]
    rec = [r for r in rows if r["date"] >= "2025-07-01"]
    print(f"Total ret24 rows: {len(rows)} | DEV: {len(dev)} | VAL: {len(val)} | RECENT: {len(rec)}")
    print(f"First day: {rows[0]['date']} | Last day: {rows[-1]['date']}")

    for feat in ["F1", "F5"]:
        dev_vals = np.array([r[feat] for r in dev], dtype=float)
        cuts = np.percentile(dev_vals, [20, 40, 60, 80])
        print(f"\n=== Feature {feat} === cuts={cuts.round(6).tolist()}")
        for split_name, split_rows in [("DEV", dev), ("VAL", val), ("RECENT", rec)]:
            s_days = [r["date"] for r in split_rows]
            s_phases = [r["phase"] for r in split_rows]
            s_vals = np.array([r[feat] for r in split_rows], dtype=float)
            s_rets = np.array([r["ret24"] for r in split_rows], dtype=float)
            sp, cnts, means = compute_spread(s_vals, s_rets, cuts)
            ci_lo, ci_hi = block_bootstrap_ci(s_days, s_vals, s_rets, cuts)
            p025, p975, pct = placebo_shuffle(s_phases, s_vals, s_rets, cuts, sp)
            print(
                f"  {split_name:6s} n={len(split_rows)} spread={sp:+.3f} bp "
                f"CI=[{ci_lo:+.3f}, {ci_hi:+.3f}] placebo_band=[{p025:+.3f}, {p975:+.3f}] "
                f"pct={pct:.2f}% q_counts={cnts}"
            )


if __name__ == "__main__":
    main()
