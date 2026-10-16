"""DEV-only time-adjusted volume spike table for 1h and 4h klines."""
import argparse
import csv
from pathlib import Path

DEV_START_MS = 1640995200000  # 2022-01-01 UTC
DEV_END_MS = 1719792000000    # 2024-07-01 UTC, exclusive
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


def read_bars(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run(input_csv, output_csv, timeframe, n_weeks=8, horizon=6):
    rows = build_event_table(read_bars(input_csv), timeframe, n_weeks, horizon)
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
    parser.add_argument("--input", required=True, help="DEV kline CSV with timestamp/open/high/low/close/volume columns")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeframe", choices=tuple(BAR_MS), required=True)
    parser.add_argument("--weeks", type=int, default=8)
    parser.add_argument("--horizon", type=int, default=6)
    args = parser.parse_args()
    rows = run(args.input, args.output, args.timeframe, args.weeks, args.horizon)
    spikes = sum(row["is_spike"] for row in rows)
    ok = sum(row["status"] == "OK" and row["is_spike"] for row in rows)
    print("rows=%d spikes=%d labeled=%d not_in_data=%d output=%s" %
          (len(rows), spikes, ok, spikes - ok, args.output))


if __name__ == "__main__":
    main()
