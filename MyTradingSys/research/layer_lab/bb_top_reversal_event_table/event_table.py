"""DEV-only 15m BB top-reversal event table with 16-bar short MFE/MAE in R."""
import argparse
import csv
import math
from pathlib import Path

import numpy as np

BB_N = 20
BB_MULT = 2.0
BAR_MS = 900_000
DEV_START_MS = 1640995200000  # 2022-01-01 UTC
DEV_END_MS = 1719792000000    # 2024-07-01 UTC, exclusive
HORIZON = 16
DEFAULT_INPUT = Path("F:/MTS/data/bigtrade/cache/perp/klines_15m.npz")


def _finite(bar, *keys):
    try:
        value = float(next(bar[k] for k in keys))
    except (KeyError, StopIteration, TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def build_event_table(bars, horizon=HORIZON, dev_start_ms=DEV_START_MS, dev_end_ms=DEV_END_MS):
    """Return setup rows; flag uses the green candle and next red candle only.

    Green high must reach its BB(20,2) upper band. The next bar must be red
    and close below the green open. Entry is the following bar open. Forward
    short MFE/MAE include that entry bar and cover up to ``horizon`` bars.
    Risk R is OURS: red candle high minus entry.
    """
    if int(horizon) <= 0:
        raise ValueError("horizon must be positive")
    data = {}
    for bar in bars:
        t = _finite(bar, "t", "timestamp")
        if t is None:
            continue
        t = int(t)
        if dev_start_ms <= t < dev_end_ms:
            data[t] = bar
    times = sorted(data)
    rows = []
    for green_i in range(BB_N - 1, len(times) - 1):
        green_t, red_t = times[green_i], times[green_i + 1]
        if red_t != green_t + BAR_MS:
            continue
        green = data[green_t]
        red = data[red_t]
        window = [data[times[j]] for j in range(green_i - BB_N + 1, green_i + 1)]
        closes = [_finite(b, "c", "close") for b in window]
        vals = [_finite(green, "o", "open"), _finite(green, "h", "high"),
                _finite(green, "c", "close"), _finite(red, "o", "open"),
                _finite(red, "h", "high"), _finite(red, "c", "close")]
        if any(x is None for x in closes + vals):
            continue
        if any(times[j] != times[j - 1] + BAR_MS for j in range(green_i - BB_N + 2, green_i + 1)):
            continue
        green_open, green_high, green_close, red_open, red_high, red_close = vals
        if not (green_close > green_open and red_close < red_open and red_close < green_open):
            continue
        mean = sum(closes) / BB_N
        variance = sum((x - mean) ** 2 for x in closes) / BB_N
        upper = mean + BB_MULT * math.sqrt(variance)
        if green_high < upper:
            continue
        entry_i = green_i + 2
        row = {"timestamp": red_t, "green_timestamp": green_t, "event_index": green_i + 1,
               "green_upper": upper, "red_high": red_high, "entry": "", "risk_r": "",
               "mfe_R": "", "mae_R": "", "bars_forward": 0, "status": "NOT_IN_DATA"}
        if entry_i >= len(times) or times[entry_i] != red_t + BAR_MS:
            rows.append(row)
            continue
        entry = _finite(data[times[entry_i]], "o", "open")
        risk = red_high - entry
        if entry is None or risk <= 0:
            rows.append(row)
            continue
        end_i = min(len(times), entry_i + int(horizon))
        future_times = times[entry_i:end_i]
        if any(future_times[j] != future_times[j - 1] + BAR_MS for j in range(1, len(future_times))):
            rows.append(row)
            continue
        highs = [_finite(data[t], "h", "high") for t in future_times]
        lows = [_finite(data[t], "l", "low") for t in future_times]
        if len(future_times) < int(horizon) or any(x is None for x in highs + lows):
            rows.append(row)
            continue
        row.update({"entry": entry, "risk_r": risk,
                    "mfe_R": max(0.0, (entry - min(lows)) / risk),
                    "mae_R": max(0.0, (max(highs) - entry) / risk),
                    "bars_forward": len(future_times), "status": "OK"})
        rows.append(row)
    return rows


def load_dev_npz(path=DEFAULT_INPUT):
    """Load only the DEV timestamp slice; bars opening on/after 2024-07-01 are excluded."""
    path = Path(path)
    if not path.exists():
        return None
    with np.load(path) as archive:
        timestamps = archive["t"]
        mask = (timestamps >= DEV_START_MS) & (timestamps < DEV_END_MS)
        indices = np.flatnonzero(mask)
        arrays = {key: archive[key] for key in ("t", "o", "h", "l", "c")}
        return [{"t": int(arrays["t"][i]), "o": float(arrays["o"][i]),
                 "h": float(arrays["h"][i]), "l": float(arrays["l"][i]),
                 "c": float(arrays["c"][i])} for i in indices]


def write_csv(rows, output):
    fields = ["timestamp", "green_timestamp", "event_index", "green_upper", "red_high", "entry",
              "risk_r", "mfe_R", "mae_R", "bars_forward", "status"]
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="15m NPZ; only DEV timestamps are loaded")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    bars = load_dev_npz(args.input)
    if bars is None:
        print("NOT_IN_DATA: input not found: " + args.input)
        return 2
    rows = build_event_table(bars)
    write_csv(rows, args.output)
    print("bars=%d events=%d labeled=%d not_in_data=%d output=%s" %
          (len(bars), len(rows), sum(r["status"] == "OK" for r in rows),
           sum(r["status"] != "OK" for r in rows), args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
