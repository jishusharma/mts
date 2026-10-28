"""
MyTradingSys/backtest/layers/fabio/run_backtest.py

W4 Fabio L1 backtest driver. Loads BTCUSDT 1m klines (2022-01 .. now), resamples to
5m/15m/1h (reusing layers.timeframe.tf_resample), runs the three Fabio rule detectors
(cvd_absorption, escalation, volume_fvg) over a grid of their UNDEFINED-in-source
parameters, does a 70/30 chronological IS/OOS split per timeframe, scores forward
returns with layers.runner, and computes PBO with bt.ref_pbo.ref_pbo_cscv on IS
daily-bucketed returns (same methodology as the D3 RSI study in BACKTEST_L1_REPORT.md).

tf_resample.resample() does not aggregate taker-buy-volume (tbv), which every Fabio
rule needs; this driver sums tbv itself with tf_resample.bucket_start().

Escalation scans every swing level to the end of the series (O(swings x bars)), which
is infeasible on 5m; the driver runs it on disjoint chunks with warm-up context
(chunked_events), so a level lives at most ~1500 bars. Documented in the report.

Never touches MyTradingSys.execution or Tom core code. Fabio stays a separate layer.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.bt.bt_data import load_klines
from MyTradingSys.backtest.bt.ref_pbo import ref_pbo_cscv
from MyTradingSys.backtest.layers.timeframe.tf_resample import resample, bucket_start
from MyTradingSys.backtest.layers.runner import forward_return_stats, baseline_return_stats
from MyTradingSys.backtest.layers.fabio.fabio_cvd_absorption import cvd_absorption_events
from MyTradingSys.backtest.layers.fabio.fabio_escalation import escalation_events
from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import (
    swing_legs, build_profile, value_area, lowest_volume_level, random_va_level,
)

REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
from MyTradingSys.backtest.fees import BINANCE_TAKER as _BT  # B081
FEE_ROUND_TRIP = 2 * _BT  # taker in + taker out
HORIZONS = (1, 5, 20)


def load_registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def resample_with_tbv(bars_1m, tf, registry):
    """resample() for OHLCV + a same-bucket sum of tbv, merged in by matching t."""
    out = resample(bars_1m, tf, registry)
    if not out:
        return out
    tbv_by_bucket = {}
    for bar in bars_1m:
        start = bucket_start(bar["t"], tf, registry)
        tbv_by_bucket[start] = tbv_by_bucket.get(start, 0.0) + bar.get("tbv", 0.0)
    for bar in out:
        bar["tbv"] = tbv_by_bucket.get(bar["t"], 0.0)
    return out


def chronological_split(bars, is_frac=0.70):
    n_is = int(len(bars) * is_frac)
    return bars[:n_is], bars[n_is:], n_is


def _day(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).date()


def daily_bucketed_returns(events, closes, bars, horizon, days=None):
    """Mean h=`horizon` return per UTC day on a COMMON day axis (`days`, default: every
    day present in `bars`); 0.0 for a no-signal day. Same axis for every variant so the
    CSCV matrix rows line up."""
    per_event = {}
    for e in events:
        i = e["i"]
        if i + horizon >= len(closes):
            continue
        sgn = 1.0 if e["side"] == "long" else -1.0
        per_event.setdefault(_day(bars[i]["t"]), []).append(sgn * (closes[i + horizon] - closes[i]) / closes[i])
    if days is None:
        days = sorted({_day(b["t"]) for b in bars})
    return [sum(per_event[d]) / len(per_event[d]) if d in per_event else 0.0 for d in days]


def chunked_events(fn, bars, own=1000, warm=500, **params):
    """Run an O(swings x bars) detector on disjoint chunks of `own` bars, each preceded
    by `warm` bars of context; keep only events whose index is in the chunk's own range.
    A level therefore lives at most own+warm bars. Still causal inside each chunk."""
    out = []
    n = len(bars)
    for start in range(0, n, own):
        lo = max(0, start - warm)
        hi = min(n, start + own)
        for e in fn(bars[lo:hi], **params):
            gi = e["i"] + lo
            if gi >= start:
                e = dict(e)
                e["i"] = gi
                out.append(e)
    out.sort(key=lambda e: e["i"])
    return out


def pbo_from_columns(cols, S=12):
    """PBO (CSCV) from equal-length per-variant daily return columns. None if too little data."""
    if len(cols) < 2:
        return None
    T = len(cols[0])
    S = min(S, (T // 2) * 2)
    if S < 4:
        return None
    M = [list(r) for r in zip(*cols)]
    try:
        return ref_pbo_cscv(M, S=S)[0]
    except Exception:
        return None


def _stats_dict(events, closes):
    if not events or not closes:
        return {h: {"n": 0, "mean_return": None, "hit_rate": None, "mae": None} for h in HORIZONS}
    return forward_return_stats([{"i": e["i"], "side": e["side"]} for e in events], closes, horizons=HORIZONS)


def grid_search_and_oos(events_fn, grid, bars_is, bars_oos, horizon=5, min_events=5, S=12):
    """events_fn(bars, **params) -> list[event]. Picks the IS-best param combo by mean
    forward return at `horizon` (>= min_events IS events), reports its IS and OOS stats
    at every horizon, and PBO over the IS grid (daily-bucketed returns)."""
    if len(bars_is) < 50 or len(bars_oos) < 10:
        return {"chosen": None, "reason": "too_few_bars", "pbo": None, "n_variants": len(grid)}
    closes_is = [b["c"] for b in bars_is]
    closes_oos = [b["c"] for b in bars_oos]
    days = sorted({_day(b["t"]) for b in bars_is})
    results, cols = [], []
    for params in grid:
        try:
            ev = events_fn(bars_is, **params)
        except Exception as exc:
            results.append({"params": params, "error": str(exc), "n_is": 0})
            cols.append([0.0] * len(days))
            continue
        st = _stats_dict(ev, closes_is)
        results.append({"params": params, "n_is": st[horizon]["n"], "mean_is": st[horizon]["mean_return"], "is_stats": st})
        cols.append(daily_bucketed_returns(ev, closes_is, bars_is, horizon, days))
    pbo_val = pbo_from_columns(cols, S=S)
    grid_summary = [{"params": r["params"], "n_is": r.get("n_is"), "mean_is": r.get("mean_is")} for r in results]
    qualifying = [r for r in results if r.get("n_is", 0) >= min_events and r.get("mean_is") is not None]
    if not qualifying:
        return {"chosen": None, "reason": "no_variant_with_min_events", "pbo": pbo_val,
                "n_variants": len(grid), "all_grid": grid_summary}
    chosen = max(qualifying, key=lambda r: r["mean_is"])
    ev_oos = events_fn(bars_oos, **chosen["params"])
    return {"chosen": chosen["params"], "n_variants": len(grid), "is_stats": chosen["is_stats"],
            "oos_stats": _stats_dict(ev_oos, closes_oos), "pbo": pbo_val, "all_grid": grid_summary}


CVD_GRID = [{"left": w, "right": w, "price_tolerance": t} for w in (2, 3, 5) for t in (0.0005, 0.001, 0.002, 0.005)]
ESCALATION_GRID = [
    {"level_tolerance": lt, "aggression_k": ak, "record_lookback": rl}
    for lt in (0.001, 0.002) for ak in (1.5, 2.0, 3.0) for rl in (20, 50)
]


def escalation_fn(bars, **p):
    return chunked_events(escalation_events, bars, **p)


def cvd_fn(bars, **p):
    return cvd_absorption_events(bars, **p)


def run_fvg(bars, n_is, n_bins=20, seed=42, max_wait=200):
    """FAB-005/006: after each swing leg confirms, wait for price to first touch the
    lowest-volume VA bin (real) or a random VA bin (control). Two trade readings of the
    touch, both reported: 'bounce' (touched from above -> long, from below -> short) and
    'through' (the opposite)."""
    if len(bars) < 2 * n_bins:
        return {"n_legs": 0, "reason": "too_few_bars"}
    legs = swing_legs(bars, left=2, right=2, use_body=True)
    ev = {(k, m): [] for k in ("real", "control") for m in ("bounce", "through")}
    closes = [b["c"] for b in bars]
    for leg in legs:
        a_i, b_i = min(leg["a_i"], leg["b_i"]), max(leg["a_i"], leg["b_i"])
        if b_i - a_i < n_bins:
            continue
        try:
            profile = build_profile(bars, a_i, b_i, n_bins=n_bins)
            va = value_area(profile, pct=0.70)
            lv = {"real": lowest_volume_level(profile, va), "control": random_va_level(profile, va, seed=seed + a_i)}
        except ValueError:
            continue
        start = leg["confirmed_i"]
        for name, lvl in lv.items():
            mid = (lvl["price_lo"] + lvl["price_hi"]) / 2.0
            from_above = closes[start] > mid
            for i in range(start + 1, min(start + 1 + max_wait, len(bars) - 1)):
                if bars[i]["l"] <= mid <= bars[i]["h"]:
                    ev[(name, "bounce")].append({"i": i, "side": "long" if from_above else "short"})
                    ev[(name, "through")].append({"i": i, "side": "short" if from_above else "long"})
                    break

    def split(events):
        is_ev = [e for e in events if e["i"] < n_is]
        oos_ev = [e for e in events if e["i"] >= n_is]
        return {"is_stats": _stats_dict(is_ev, closes), "oos_stats": _stats_dict(oos_ev, closes)}

    out = {"n_legs": len(legs)}
    for (name, mode), events in ev.items():
        out[f"{name}_{mode}"] = split(events)
    return out


def run_tf(tf, bars_1m, registry, out_dir=None, cvd_grid=None, esc_grid=None):
    bars = resample_with_tbv(bars_1m, tf, registry)
    bars_is, bars_oos, n_is = chronological_split(bars)
    result = {"tf": tf, "n_bars": len(bars), "n_bars_is": n_is, "n_bars_oos": len(bars) - n_is}
    if bars_oos:
        result["baseline_oos"] = baseline_return_stats([b["c"] for b in bars_oos], horizons=HORIZONS)
    result["cvd_absorption"] = grid_search_and_oos(cvd_fn, cvd_grid or CVD_GRID, bars_is, bars_oos)
    result["escalation"] = grid_search_and_oos(escalation_fn, esc_grid or ESCALATION_GRID, bars_is, bars_oos)
    result["volume_fvg"] = run_fvg(bars, n_is)
    if out_dir is not None:
        with open(Path(out_dir) / f"{tf}_result.json", "w", newline="\n", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--out", default=str(REPO / "Dumps" / "backtest" / "runs" / "fabio_l1"))
    ap.add_argument("--tfs", default="5m,15m,1h")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = load_registry()

    bars_1m = load_klines(args.data_root)
    last_t = bars_1m[-1]["t"] if bars_1m else 0
    bars_1m += [b for b in load_klines(args.data_root2) if b["t"] > last_t]
    bars_1m.sort(key=lambda b: b["t"])
    print(f"Loaded {len(bars_1m)} 1m bars", file=sys.stderr, flush=True)

    summary = {}
    for tf in args.tfs.split(","):
        print(f"Running {tf} ...", file=sys.stderr, flush=True)
        summary[tf] = run_tf(tf, bars_1m, registry, out_dir)
        print(f"  {tf} done", file=sys.stderr, flush=True)

    with open(out_dir / "summary.json", "w", newline="\n", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, default=str)
    print(f"Done. Results in {out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
