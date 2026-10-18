"""DEV-only time-adjusted volume spike table for 1h and 4h klines."""
import argparse
import csv
from pathlib import Path

DEV_START_MS = 1640995200000  # 2022-01-01 UTC
DEV_END_MS = 1719792000000    # 2024-07-01 UTC, exclusive
DEFAULT_NPZ = "F:/MTS/data/bigtrade/cache/perp/klines_1h.npz"
BAR_MS = {"1h": 3_600_000, "4h": 14_400_000}
SLOTS_PER_WEEK = {"1h": 168, "4h": 42}


def _number(bar, *keys):
    for key in keys:
        try:
            return float(bar[key])
        except (KeyError, TypeError, ValueError):
            continue
    raise ValueError("missing numeric field: " + "/".join(keys))


def build_event_table(bars, timeframe, n_weeks=8, horizon=6, threshold=2.0,
                      dev_start_ms=DEV_START_MS, dev_end_ms=DEV_END_MS):
    """Return per-bar rows; RV baseline uses only the prior N same-week slots.

    R is measured against the event candle's high-low range, oriented by the
    event candle body. Forward outcomes start at the next bar open.
    """
    if timeframe not in BAR_MS:
        raise ValueError("timeframe must be '1h' or '4h'")
    if int(n_weeks) <= 0 or int(horizon) <= 0:
        raise ValueError("n_weeks and horizon must be positive")
    step, cycle = BAR_MS[timeframe], SLOTS_PER_WEEK[timeframe]
    data = {}
    for bar in bars:
        try:
            t = int(float(bar.get("timestamp", bar.get("t"))))
            if dev_start_ms <= t < dev_end_ms:
                data[t] = bar
        except (TypeError, ValueError):
            continue
    times = sorted(data)
    volumes = []
    for t in times:
        try:
            volumes.append(_number(data[t], "volume", "v"))
        except ValueError:
            volumes.append(None)
    rows = []
    for i, t in enumerate(times):
        bar = data[t]
        slot = (t // step) % cycle
        prior = []
        for k in range(1, int(n_weeks) + 1):
            j = i - k * cycle
            if j < 0 or times[j] != t - k * cycle * step:
                prior = []
                break
            value = volumes[j]
            if value is None:
                prior = []
                break
            prior.append(value)
        base = sorted(prior)[len(prior) // 2] if len(prior) == int(n_weeks) else None
        # Even-sized median is the midpoint of the two central observations.
        if base is not None and len(prior) % 2 == 0:
            ordered = sorted(prior)
            base = (ordered[len(ordered) // 2 - 1] + ordered[len(ordered) // 2]) / 2
        volume = volumes[i]
        rv = volume / base if base is not None and base > 0 and volume is not None else None
        is_spike = rv is not None and rv >= float(threshold)
        row = {"timestamp": t, "timeframe": timeframe, "slot_of_week": slot,
               "volume": volume if volume is not None else "",
               "baseline_volume": base if base is not None else "",
               "relative_volume": rv if rv is not None else "",
               "is_spike": bool(is_spike), "direction": "", "risk_range": "", "forward_return_R": "",
               "mfe_R": "", "mae_R": "", "bars_forward": 0,
               "status": "OK" if rv is not None else "NOT_IN_DATA"}
        if is_spike:
            try:
                o, h, low, c = (_number(bar, *names) for names in (("open", "o"), ("high", "h"), ("low", "l"), ("close", "c")))
                risk = h - low
                direction = 1 if c > o else -1 if c < o else 0
                next_i = i + 1
                end_i = min(len(times), next_i + int(horizon))
                # Do not bridge missing candles or use a partial horizon / bars beyond DEV.
                valid = end_i == next_i + int(horizon) and all(times[j] == times[j - 1] + step for j in range(next_i, end_i))
                if risk <= 0 or not direction or next_i >= len(times) or times[next_i] != t + step or not valid:
                    row["status"] = "NOT_IN_DATA"
                else:
                    future = [data[times[j]] for j in range(next_i, end_i)]
                    entry = _number(future[0], "open", "o")
                    highs = [_number(x, "high", "h") for x in future]
                    lows = [_number(x, "low", "l") for x in future]
                    exit_close = _number(future[-1], "close", "c")
                    favorable = max(highs) - entry if direction > 0 else entry - min(lows)
                    adverse = entry - min(lows) if direction > 0 else max(highs) - entry
                    row.update({"direction": "up" if direction > 0 else "down", "risk_range": risk,
                                "forward_return_R": round(direction * (exit_close - entry) / risk, 8),
                                "mfe_R": round(max(0.0, favorable / risk), 8),
                                "mae_R": round(max(0.0, adverse / risk), 8),
                                "bars_forward": len(future)})
            except (ValueError, ZeroDivisionError):
                row["status"] = "NOT_IN_DATA"
        rows.append(row)
    return rows


def load_dev_npz(path, timeframe, dev_start_ms=DEV_START_MS, dev_end_ms=DEV_END_MS):
    """Load DEV bars (open in [start, end)) from a klines_1h npz; 4h is built from 1h.

    The mask is applied to the arrays before any bar dict exists, so later bars
    are never materialised. A 4h bar needs four consecutive 1h bars starting at
    a 4h UTC boundary; incomplete buckets are skipped.
    """
    import numpy as np
    if timeframe not in BAR_MS:
        raise ValueError("timeframe must be '1h' or '4h'")
    with np.load(path) as z:
        t = z["t"]
        keep = (t >= dev_start_ms) & (t < dev_end_ms)
        cols = {k: z[k][keep] for k in ("t", "o", "h", "l", "c", "v")}
    order = np.argsort(cols["t"], kind="stable")
    cols = {k: v[order] for k, v in cols.items()}
    hourly = {int(ts): (float(o), float(h), float(low), float(c), float(v))
              for ts, o, h, low, c, v in zip(cols["t"], cols["o"], cols["h"], cols["l"], cols["c"], cols["v"])}
    if timeframe == "1h":
        return [{"timestamp": ts, "open": b[0], "high": b[1], "low": b[2], "close": b[3], "volume": b[4]}
                for ts, b in sorted(hourly.items())]
    out = []
    for ts in sorted({x - x % BAR_MS["4h"] for x in hourly}):
        parts = [hourly.get(ts + k * BAR_MS["1h"]) for k in range(4)]
        if any(p is None for p in parts):
            continue
        out.append({"timestamp": ts, "open": parts[0][0], "high": max(p[1] for p in parts),
                    "low": min(p[2] for p in parts), "close": parts[3][3], "volume": sum(p[4] for p in parts)})
    return out


def summarize(rows):
    """Counts and mean MFE/MAE (R) over labelled spikes; gaps are counted, never zero-filled."""
    spikes = [r for r in rows if r["is_spike"]]
    ok = [r for r in spikes if r["status"] == "OK"]
    mean = lambda key: round(sum(float(r[key]) for r in ok) / len(ok), 6) if ok else None
    return {"rows": len(rows), "rows_ok": sum(r["status"] == "OK" for r in rows),
            "rows_not_in_data": sum(r["status"] != "OK" for r in rows), "spikes": len(spikes),
            "spikes_ok": len(ok), "spikes_not_in_data": len(spikes) - len(ok),
            "mean_mfe_R": mean("mfe_R"), "mean_mae_R": mean("mae_R")}


def read_bars(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run(input_path, output_csv, timeframe, n_weeks=8, horizon=6):
    if str(input_path).lower().endswith(".npz"):
        bars = load_dev_npz(input_path, timeframe)
    else:
        bars = read_bars(input_path)
    rows = build_event_table(bars, timeframe, n_weeks, horizon)
    if not output_csv:
        return rows
    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["timestamp", "timeframe", "slot_of_week", "volume", "baseline_volume", "relative_volume", "is_spike", "direction", "risk_range", "forward_return_R", "mfe_R", "mae_R", "bars_forward", "status"]
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_NPZ, help="klines_1h.npz (DEV slice taken before bars are built) or a DEV kline CSV")
    parser.add_argument("--output", default="", help="optional CSV; omit to print counts only")
    parser.add_argument("--timeframe", choices=tuple(BAR_MS), required=True)
    parser.add_argument("--weeks", type=int, default=8)
    parser.add_argument("--horizon", type=int, default=6)
    args = parser.parse_args()
    rows = run(args.input, args.output, args.timeframe, args.weeks, args.horizon)
    print(args.timeframe, summarize(rows))


if __name__ == "__main__":
    main()
