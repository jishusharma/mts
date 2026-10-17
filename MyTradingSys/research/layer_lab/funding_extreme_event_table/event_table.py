"""DEV-only funding extreme events with 24-hour forward excursions in ATR14 units."""
import argparse
import csv
import json
from pathlib import Path
import sys
import zipfile

import numpy as np

DEV_START_MS = 1640995200000
DEV_END_MS = 1719792000000  # exclusive: 2024-07-01 UTC
BASELINE_PRINTS = 90
PERCENTILE = 95  # OURS
HORIZON_MS = 24 * 60 * 60 * 1000  # OURS
BAR_MS = 60 * 60 * 1000
DEFAULT_DATA = Path("F:/MTS/data")


def _missing(t, rate, baseline=""):
    return {"t_ms": int(t), "rate": float(rate), "baseline_q95": baseline, "is_extreme": "",
            "side": "", "entry_price": "", "risk_atr": "", "mfe_R": "", "mae_R": "",
            "bars_forward": 0, "status": "NOT_IN_DATA"}


def measure_event(t, rate, funding, bars):
    """Return a row; current funding print is never included in its trailing baseline."""
    prior = [abs(float(r)) for ts, r in funding if int(ts) < int(t)][-BASELINE_PRINTS:]
    if int(t) < DEV_START_MS or int(t) >= DEV_END_MS or len(prior) < BASELINE_PRINTS:
        return _missing(t, rate)
    q95 = float(np.quantile(np.asarray(prior), PERCENTILE / 100, method="linear"))
    extreme = abs(float(rate)) >= q95
    side = "short" if rate > 0 else "long" if rate < 0 else ""
    row = _missing(t, rate, round(q95, 12))
    row.update(is_extreme=bool(extreme), side=side)
    if not extreme:
        row["status"] = "OK"
        return row
    times = np.asarray(bars.get("t", []), dtype=np.int64)
    if not len(times):
        return row
    # Use only a fully closed bar at the print time; the bar opening at t is not yet known.
    i = int(np.searchsorted(times, int(t) - BAR_MS, side="right") - 1)
    if i < 0:
        return row
    atr = float(bars["atr"][i])
    entry = float(bars["c"][i])
    if not np.isfinite(atr) or atr <= 0 or not np.isfinite(entry):
        return row
    # The outcome window is [print time, print time + 24h), clipped to DEV.
    start = int(np.searchsorted(times, int(t), side="left"))
    stop = int(np.searchsorted(times, min(int(t) + HORIZON_MS, DEV_END_MS), side="left"))
    if stop - start < 24:
        return row
    hs = np.asarray(bars["h"][start:stop], dtype=float)
    ls = np.asarray(bars["l"][start:stop], dtype=float)
    direction = -1 if rate > 0 else 1
    mfe = max(0.0, float((entry - np.min(ls)) / atr)) if direction < 0 else max(0.0, float((np.max(hs) - entry) / atr))
    mae = max(0.0, float((np.max(hs) - entry) / atr)) if direction < 0 else max(0.0, float((entry - np.min(ls)) / atr))
    row.update(entry_price=entry, risk_atr=atr, mfe_R=round(mfe, 8), mae_R=round(mae, 8),
               bars_forward=stop - start, status="OK")
    return row


def build_event_table(funding, bars):
    """One result row per DEV funding print; inputs are (timestamp, rate) and 1h arrays."""
    dev = [(int(t), float(r)) for t, r in funding if DEV_START_MS <= int(t) < DEV_END_MS]
    dev.sort()
    rows = []
    for i, (t, rate) in enumerate(dev):
        rows.append(measure_event(t, rate, dev[:i], bars))
    return rows


def load_dev_funding(data_root=DEFAULT_DATA):
    """Read BTCUSDT funding zips, filtering by DEV timestamps before parsing rates."""
    folder = Path(data_root) / "candle_close_dev_2022_2024"
    out = []
    for path in sorted(folder.glob("BTCUSDT-fundingRate-*.zip")):
        # Do not open an archive whose month begins on/after the DEV cutoff.
        month = path.stem.rsplit("-", 2)[-2:]
        if len(month) == 2 and "-".join(month) >= "2024-07":
            continue
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                with archive.open(member) as raw:
                    reader = csv.reader(line.decode("utf-8") for line in raw)
                    first = next(reader, None)
                    if not first:
                        continue
                    rows = reader if not first[0].isdigit() else iter([first, *reader])
                    for row in rows:
                        t = int(row[0])
                        if DEV_START_MS <= t < DEV_END_MS:
                            out.append((t, float(row[2])))
    return sorted(out)


def load_dev_bars(path=Path("F:/MTS/data/bigtrade/cache/perp/klines_1h.npz")):
    """Load only the permitted DEV slice of the local 1h archive."""
    with np.load(path) as src:
        all_times = src["t"]
        start = int(np.searchsorted(all_times, DEV_START_MS, side="left"))
        stop = int(np.searchsorted(all_times, DEV_END_MS, side="left"))
        return {key: src[key][start:stop].copy() for key in ("t", "h", "l", "c", "atr")}


def run(data_root=DEFAULT_DATA):
    return build_event_table(load_dev_funding(data_root), load_dev_bars())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = run(args.data_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["t_ms", "rate", "baseline_q95", "is_extreme", "side", "entry_price", "risk_atr", "mfe_R", "mae_R", "bars_forward", "status"]
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "extreme": sum(r["is_extreme"] is True for r in rows),
                      "not_in_data": sum(r["status"] == "NOT_IN_DATA" for r in rows), "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
