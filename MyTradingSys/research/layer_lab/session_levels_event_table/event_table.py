"""DEV-only event table for session-level failed breaks and four-hour excursions."""
import csv
import importlib.util
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DETECTOR = ROOT / "MyTradingSys/backtest/layers/session_levels/session_levels.py"
DATA = Path("F:/MTS/data/candle_close_dev_2022_2024")
DEV_END = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
MIN_MS = 60000
HORIZON_BARS = 240
SPEC = importlib.util.spec_from_file_location("session_levels_source", DETECTOR)
_source = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_source)


def load_dev_bars(data_dir=DATA):
    """Load only BTCUSDT 1m archive rows opening before 2024-07-01 UTC."""
    bars = []
    for path in sorted(Path(data_dir).glob("BTCUSDT-1m-*.zip")):
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            for name in names:
                with archive.open(name) as raw:
                    rows = csv.DictReader(line.decode("utf-8") for line in raw)
                    for row in rows:
                        t = int(row["open_time"])
                        if t < DEV_END:
                            bars.append({"t": t, "o": float(row["open"]), "h": float(row["high"]),
                                         "l": float(row["low"]), "c": float(row["close"])})
    bars.sort(key=lambda bar: bar["t"])
    return bars


def build_event_table(bars, source="DEV"):
    """Return high and low events; unavailable/incomplete forward windows are NOT_IN_DATA."""
    bars = sorted((b for b in bars if b["t"] < DEV_END), key=lambda b: b["t"])
    by_time = {b["t"]: b for b in bars}
    events = []
    for side in ("high", "low"):
        for event in _source.failed_break_events(bars, side=side):
            base = event["day"] * _source.DAY_MS
            touch_t = base + event["touch_min"] * MIN_MS
            fail_t = base + event["fail_min"] * MIN_MS
            risk = abs(event["spike"] - event["level"])
            future = [by_time.get(fail_t + i * MIN_MS) for i in range(1, HORIZON_BARS + 1)]
            complete = risk > 0 and all(bar is not None for bar in future)
            if complete:
                if side == "high":
                    mfe = max((event["entry"] - bar["l"]) / risk for bar in future)
                    mae = max((bar["h"] - event["entry"]) / risk for bar in future)
                else:
                    mfe = max((bar["h"] - event["entry"]) / risk for bar in future)
                    mae = max((event["entry"] - bar["l"]) / risk for bar in future)
                status = "OK"
            else:
                mfe = mae = None
                status = "NOT_IN_DATA"
            events.append({"source": source, "day_utc": datetime.fromtimestamp(base / 1000, timezone.utc).date().isoformat(),
                           "side": side, "touch_time_ms": touch_t, "fail_time_ms": fail_t,
                           "level": event["level"], "spike": event["spike"], "r_price": risk,
                           "entry": event["entry"], "mfe_r": mfe, "mae_r": mae, "forward_status": status})
    return sorted(events, key=lambda row: (row["fail_time_ms"], row["side"]))


def run(data_dir=DATA):
    return build_event_table(load_dev_bars(data_dir))


def write_csv(rows, output):
    fields = ["source", "day_utc", "side", "touch_time_ms", "fail_time_ms", "level", "spike", "r_price",
              "entry", "mfe_r", "mae_r", "forward_status"]
    with Path(output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).with_name("events.csv")))
    args = parser.parse_args()
    rows = run()
    write_csv(rows, args.output)
    counts = {status: sum(row["forward_status"] == status for row in rows) for status in ("OK", "NOT_IN_DATA")}
    print(f"events={len(rows)} high={sum(r['side']=='high' for r in rows)} low={sum(r['side']=='low' for r in rows)} forward={counts}")
