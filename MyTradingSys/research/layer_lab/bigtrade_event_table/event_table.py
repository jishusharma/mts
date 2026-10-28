"""DEV-only forward excursion table for existing bigtrade fire CSVs."""
import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
try:
    from MyTradingSys.backtest.bigtrade import fires_kline
except ImportError:
    fires_kline = None

DEV_START_MS = 1640995200000  # 2022-01-01 UTC
DEV_END_MS = 1719792000000    # 2024-07-01 UTC (exclusive); OPERATOR_DECISIONS.md:878 DEV=2022-01-01..2024-06-30
DEFAULT_HORIZON = 20


def _bar_index(times, timestamp):
    return int(np.searchsorted(times, timestamp, side="right") - 1)


def measure_fire(fire, bars, horizon=DEFAULT_HORIZON, dev_end_ms=DEV_END_MS):
    """Measure from the fire close through at most horizon subsequent DEV bars.

    R is the absolute fire-price to stop distance. Forward bars start strictly
    after t_fire_ms; no post-DEV bar is inspected. Same-bar stop/target ties
    resolve to stop for conservative first-hit reporting.
    """
    side = str(fire.get("side", "")).lower()
    direction = 1 if side in ("long", "buy", "bull") else -1 if side in ("short", "sell", "bear") else 0
    try:
        t_fire = int(float(fire["t_fire_ms"]))
        price = float(fire.get("price") or fire.get("entry_price"))
        stop = float(fire["stop"])
    except (KeyError, TypeError, ValueError):
        direction = 0
    if not direction:
        return _missing_row(fire, "NOT_IN_DATA")
    risk = abs(price - stop)
    if risk <= 0:
        return _missing_row(fire, "NOT_IN_DATA")
    times = np.asarray(bars["t"], dtype=np.int64)
    i = _bar_index(times, t_fire)
    if i < 0 or times[i] != t_fire or t_fire < DEV_START_MS or t_fire >= dev_end_ms:
        return _missing_row(fire, "NOT_IN_DATA")
    end = min(len(times), i + 1 + max(0, int(horizon)))
    end = min(end, int(np.searchsorted(times, dev_end_ms, side="left")))
    if end <= i + 1:
        return _missing_row(fire, "NOT_IN_DATA")
    hs = np.asarray(bars["h"][i + 1:end], dtype=float)
    ls = np.asarray(bars["l"][i + 1:end], dtype=float)
    mfe = max(0.0, float((np.max(hs) - price) * direction / risk)) if direction > 0 else max(0.0, float((price - np.min(ls)) / risk))
    mae = max(0.0, float((price - np.min(ls)) / risk)) if direction > 0 else max(0.0, float((np.max(hs) - price) / risk))
    first = "none"
    for high, low in zip(hs, ls):
        stop_hit = low <= stop if direction > 0 else high >= stop
        target = price + direction * risk
        target_hit = high >= target if direction > 0 else low <= target
        if stop_hit or target_hit:
            first = "stop_1R" if stop_hit else "target_1R"
            break
    return {"key": fire.get("key", ""), "tf": fire.get("tf", ""), "side": fire.get("side", ""),
            "t_fire_ms": t_fire, "fire_price": price, "risk_price": risk, "mfe_R": round(mfe, 8),
            "mae_R": round(mae, 8), "first_hit": first, "bars_forward": end - i - 1, "status": "OK"}


def _missing_row(fire, status):
    return {"key": fire.get("key", ""), "tf": fire.get("tf", ""), "side": fire.get("side", ""),
            "t_fire_ms": fire.get("t_fire_ms", ""), "fire_price": fire.get("price", ""),
            "risk_price": "", "mfe_R": "", "mae_R": "", "first_hit": "", "bars_forward": 0, "status": status}


def build_event_table(fires, klines_by_tf, horizon=DEFAULT_HORIZON, dev_end_ms=DEV_END_MS):
    rows = []
    for fire in fires:
        if fire.get("split") not in ("TRAIN", "") or not (DEV_START_MS <= int(float(fire.get("t_fire_ms", 0) or 0)) < dev_end_ms):
            continue
        bars = klines_by_tf.get(fire.get("tf"))
        rows.append(measure_fire(fire, bars, horizon, dev_end_ms) if bars is not None else _missing_row(fire, "NOT_IN_DATA"))
    return rows


def load_fires(fires_dir):
    files = sorted(Path(fires_dir).glob("fires_*.csv"))
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            yield from csv.DictReader(fh)


def run(fires_dir=None, cache_dir=None, output=None, horizon=DEFAULT_HORIZON):
    if fires_kline is None:
        raise RuntimeError("fires_kline module unavailable")
    fires_dir = Path(fires_dir or fires_kline.FIRES_DIR)
    cache_dir = Path(cache_dir or fires_kline.CACHE_DIR)
    by_tf = {}
    for tf in fires_kline.TF_MS:
        path = cache_dir / ("klines_%s.npz" % tf)
        if path.exists():
            with np.load(path) as data:
                # Cache timestamps are candle opens; fires_kline records candle closes.
                by_tf[tf] = {key: data[key].copy() for key in ("t", "h", "l", "c")}
                by_tf[tf]["t"] = by_tf[tf]["t"] + fires_kline.TF_MS[tf]
    rows = build_event_table(load_fires(fires_dir), by_tf, horizon)
    if output:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["key", "tf", "side", "t_fire_ms", "fire_price", "risk_price", "mfe_R", "mae_R", "first_hit", "bars_forward", "status"])
            writer.writeheader()
            writer.writerows(rows)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fires-dir")
    p.add_argument("--cache-dir")
    p.add_argument("--output", required=True)
    p.add_argument("--horizon", type=int, default=DEFAULT_HORIZON)
    a = p.parse_args()
    rows = run(a.fires_dir, a.cache_dir, a.output, a.horizon)
    counts = {status: sum(row["status"] == status for row in rows) for status in ("OK", "NOT_IN_DATA")}
    print(json.dumps({"rows": len(rows), "counts": counts, "output": a.output}, sort_keys=True))


if __name__ == "__main__":
    main()
