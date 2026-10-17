"""DEV-only candle pattern event table with causal forward excursions."""
import argparse
import csv
from datetime import datetime, timezone
import importlib.util
from pathlib import Path

import numpy as np
from patterns import DETECTORS

DEV_END_MS = 1719792000000
HOUR_MS = 3600000
DEFAULT_INPUT = Path(r"F:/MTS/data/bigtrade/cache/perp/klines_1h.npz")


def _helper(relative, name):
    path = Path(__file__).resolve().parents[1] / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_dev_bars(path=DEFAULT_INPUT):
    """Load only the registered DEV slice; do not create rows for later bars."""
    with np.load(path, allow_pickle=False) as data:
        t = data["t"]
        mask = (t >= 1640995200000) & (t < DEV_END_MS)
        stamps = t[mask]
        arrays = {key: data[key][mask] for key in ("o", "h", "l", "c")}
    rows = [{"t": int(stamps[i]), **{k: float(v[i]) for k, v in arrays.items()}}
            for i in range(len(stamps))]
    guard = _helper("dev_split_guard/event_table.py", "candle_dev_guard")
    guard.assert_dev(rows, "t")
    return rows


def resample_4h(bars):
    """Aggregate only aligned buckets containing all four consecutive hourly bars."""
    by_time = {int(row["t"]): row for row in bars}
    result = []
    for start in sorted(by_time):
        dt = datetime.fromtimestamp(start / 1000, tz=timezone.utc)
        if dt.hour % 4 or dt.minute or dt.second or dt.microsecond:
            continue
        stamps = [start + j * HOUR_MS for j in range(4)]
        if not all(stamp in by_time for stamp in stamps):
            continue
        group = [by_time[stamp] for stamp in stamps]
        result.append({"t": start, "o": group[0]["o"], "h": max(x["h"] for x in group),
                       "l": min(x["l"] for x in group), "c": group[-1]["c"]})
    guard = _helper("dev_split_guard/event_table.py", "candle_dev_guard_4h")
    guard.assert_dev(result, "t")
    return result


def build_event_table(events, bars, horizon=20, interval_ms=None):
    rows = []
    step = interval_ms
    if step is None and len(bars) > 1:
        step = int(bars[1]["t"]) - int(bars[0]["t"])
    for event in events:
        i = int(event["index"])
        side = int(event["side"])
        if i < 0 or i >= len(bars) or side not in (-1, 1):
            rows.append({"event_time": None, "mfe_R": None, "mae_R": None,
                         "bars_forward": 0, "status": "NOT_IN_DATA"})
            continue
        b = bars[i]
        price, risk = float(b["c"]), float(b["h"]) - float(b["l"])
        count = max(0, int(horizon))
        times = [int(row["t"]) for row in bars]
        by_time = {int(row["t"]): row for row in bars}
        future_times = [right for left, right in zip(times, times[1:]) if left >= int(b["t"])][:count]
        future = [by_time[stamp] for stamp in future_times]
        close_time = int(b["t"]) + (step or 0)
        continuous = (len(future) == count and step is not None and
                      all(int(x["t"]) == int(b["t"]) + step * (j + 1)
                          for j, x in enumerate(future)))
        if risk <= 0 or not count or not continuous:
            rows.append({"event_time": close_time, "pattern": event.get("pattern", ""),
                         "side": side, "signal_index": i, "mfe_R": None, "mae_R": None,
                         "bars_forward": len(future), "status": "NOT_IN_DATA"})
            continue
        favorable = [((float(x["h"]) - price) if side == 1 else (price - float(x["l"]))) for x in future]
        adverse = [((price - float(x["l"])) if side == 1 else (float(x["h"]) - price)) for x in future]
        rows.append({"event_time": close_time, "pattern": event.get("pattern", ""), "side": side,
                     "signal_index": i, "event_price": price, "risk_price": risk,
                     "mfe_R": max(0.0, max(favorable) / risk),
                     "mae_R": max(0.0, max(adverse) / risk), "bars_forward": len(future), "status": "OK"})
    return rows


def events_for(bars):
    events = []
    for name, detector in DETECTORS.items():
        for i in range(len(bars)):
            side = int(detector(bars, i))
            if side:
                # Volatility patterns return 1 as their canonical detector hit; this is an
                # event-table orientation convention, not a directional trading claim.
                events.append({"pattern": name, "index": i, "side": side})
    return events


def run(input_path=DEFAULT_INPUT, output=None, horizon=20):
    hourly = load_dev_bars(input_path)
    frames = (("1h", hourly, HOUR_MS), ("4h", resample_4h(hourly), 4 * HOUR_MS))
    all_rows, summary = [], []
    for tf, bars, interval in frames:
        by_pattern = {name: [] for name in DETECTORS}
        for event in events_for(bars):
            by_pattern[event["pattern"]].append(event)
        for name, events in by_pattern.items():
            rows = build_event_table(events, bars, horizon, interval)
            all_rows.extend(dict(timeframe=tf, **row) for row in rows)
            ok = [row for row in rows if row["status"] == "OK"]
            summary.append({"timeframe": tf, "pattern": name, "rows": len(rows), "OK": len(ok),
                            "NOT_IN_DATA": len(rows) - len(ok),
                            "mean_mfe_R": float(np.mean([r["mfe_R"] for r in ok])) if ok else None,
                            "mean_mae_R": float(np.mean([r["mae_R"] for r in ok])) if ok else None})
    if output:
        fields = sorted({key for row in all_rows for key in row})
        with open(output, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_rows)
    return summary, all_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output")
    parser.add_argument("--horizon", type=int, default=20)
    args = parser.parse_args()
    summary, rows = run(args.input, args.output, args.horizon)
    print("timeframe pattern rows OK NOT_IN_DATA mean_MFE_R mean_MAE_R")
    for row in summary:
        print("{timeframe} {pattern} {rows} {OK} {NOT_IN_DATA} {mean_mfe_R} {mean_mae_R}".format(**row))
    print("TOTAL rows=%d OK=%d NOT_IN_DATA=%d" % (len(rows), sum(x["status"] == "OK" for x in rows),
                                                    sum(x["status"] != "OK" for x in rows)))


if __name__ == "__main__":
    main()
