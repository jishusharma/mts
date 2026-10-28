"""DEV-only event table for the four directional OI/price states."""
import argparse
import csv
import json
from pathlib import Path

DEV_START_MS = 1640995200000
DEV_END_MS = 1719792000000  # 2024-07-01 UTC exclusive (OPERATOR_DECISIONS.md:878)
STATES = {
    (1, 1): ("aggressive_long", 1),
    (1, -1): ("divergence_bearish", -1),
    (-1, 1): ("divergence_bullish", 1),
    (-1, -1): ("aggressive_short", -1),
}


def inventory(data_root=Path("F:/MTS/data"), research_root=Path("MyTradingSys/research")):
    """List local candidate files, including missing expected OI and whale inputs."""
    data_root, research_root = Path(data_root), Path(research_root)
    found = {"oi": [], "funding": [], "whale": []}
    patterns = {
        "oi": ("*metrics*", "*openinterest*", "*open_interest*"),
        "funding": ("*funding*",),
        "whale": ("*whale*", "*large_trader*", "*toptrader*"),
    }
    for kind, globs in patterns.items():
        paths = set()
        for root in (data_root, research_root):
            if root.exists():
                for pattern in globs:
                    paths.update(p for p in root.rglob(pattern) if p.is_file() and p.suffix.lower() in (".csv", ".json", ".jsonl", ".gz", ".zip", ".parquet"))
        found[kind] = sorted(str(p) for p in paths)
    return found


def classify(price_pct, oi_pct):
    """Use the 2026-10-10 study's directional sign classifier; flat inputs are not events."""
    if price_pct is None or oi_pct is None:
        return "NOT_IN_DATA", 0
    try:
        p, oi = float(price_pct), float(oi_pct)
    except (TypeError, ValueError):
        return "NOT_IN_DATA", 0
    ps, os_ = (1 if p > 0 else -1 if p < 0 else 0), (1 if oi > 0 else -1 if oi < 0 else 0)
    return STATES.get((ps, os_), ("NOT_DIRECTIONAL", 0))


def build_event_table(events, bars, horizon=8, dev_start_ms=DEV_START_MS, dev_end_ms=DEV_END_MS):
    """Return one row per supplied event, using only bars strictly after event time.

    Directional R uses entry-to-stop distance. Forward return is signed close move;
    MFE/MAE use highs/lows. Missing OI or bars is explicitly NOT_IN_DATA.
    """
    by_time = {}
    for bar in bars:
        try:
            t = int(bar["timestamp"])
            if dev_start_ms <= t < dev_end_ms:
                by_time[t] = bar
        except (KeyError, TypeError, ValueError):
            continue
    times = sorted(by_time)
    rows = []
    for event in events:
        try:
            t = int(event["timestamp"])
            entry, stop = float(event["entry"]), float(event["stop"])
            price_pct, oi_pct = event.get("price_change_pct"), event.get("oi_change_pct")
        except (KeyError, TypeError, ValueError):
            t, entry, stop, price_pct, oi_pct = 0, 0.0, 0.0, None, None
        state, direction = classify(price_pct, oi_pct)
        row = {"timestamp": t, "state": state, "price_change_pct": price_pct if price_pct is not None else "",
               "oi_change_pct": oi_pct if oi_pct is not None else "", "entry": entry if entry else "",
               "risk": "", "forward_return_R": "", "mfe_R": "", "mae_R": "", "bars_forward": 0,
               "status": "NOT_IN_DATA"}
        risk = abs(entry - stop)
        if state == "NOT_IN_DATA" or not direction or risk <= 0 or t < dev_start_ms or t >= dev_end_ms:
            rows.append(row)
            continue
        import bisect
        i = bisect.bisect_right(times, t)
        future = [by_time[x] for x in times[i:i + max(0, int(horizon))]]
        if t not in by_time or not future:
            rows.append(row)
            continue
        try:
            closes = [float(b["close"]) for b in future]
            highs = [float(b["high"]) for b in future]
            lows = [float(b["low"]) for b in future]
        except (KeyError, TypeError, ValueError):
            rows.append(row)
            continue
        row.update({"risk": risk, "forward_return_R": round(direction * (closes[-1] - entry) / risk, 8),
                    "mfe_R": round(max(0.0, direction * ((max(highs) if direction > 0 else min(lows)) - entry) / risk), 8),
                    "mae_R": round(max(0.0, -direction * ((min(lows) if direction > 0 else max(highs)) - entry) / risk), 8),
                    "bars_forward": len(future), "status": "OK"})
        rows.append(row)
    return rows


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def run(event_csv, bars_csv, output, horizon=8):
    events, bars = read_csv(event_csv), read_csv(bars_csv)
    rows = build_event_table(events, bars, horizon)
    fields = list(rows[0]) if rows else ["timestamp", "state", "price_change_pct", "oi_change_pct", "entry", "risk", "forward_return_R", "mfe_R", "mae_R", "bars_forward", "status"]
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with Path(output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", action="store_true")
    parser.add_argument("--events")
    parser.add_argument("--bars")
    parser.add_argument("--output")
    parser.add_argument("--horizon", type=int, default=8)
    args = parser.parse_args()
    if args.inventory:
        print(json.dumps(inventory(), indent=2)); return
    if not all((args.events, args.bars, args.output)):
        parser.error("--events, --bars and --output are required unless --inventory is used")
    rows = run(args.events, args.bars, args.output, args.horizon)
    print(json.dumps({"rows": len(rows), "ok": sum(r["status"] == "OK" for r in rows),
                      "not_in_data": sum(r["status"] == "NOT_IN_DATA" for r in rows), "output": args.output}, sort_keys=True))


if __name__ == "__main__":
    main()
