"""Missed-trade analysis: chart-observed setups vs what MTS did, scored on 1m bars.

  python MyTradingSys/observation/missed.py [--dir D] [--auto-trades P] [--bars DIR] [--horizon-h 24]

Inputs (read-only):
  <obs>/derived/observations.jsonl     from capture.py build (setups = side set, not superseded)
  MyTradingSys/execution/auto_trades.jsonl    every signal the auto-trader saw and what it did with it
  MyTradingSys/runtime/orderflow_live/YYYY-MM-DD.csv   BTCUSDT 1m bars (t ms, o, h, l, c)
  MyTradingSys/market_data/klines/BTCUSDT_5m.json      fallback when the 1m recorder has no bar at the read (last ~41 h)
Outputs: <obs>/derived/missed.csv and MISSED_REPORT.md.

Verdicts: CAUGHT (MTS entered the same side in the window), MISSED (setup hit target first, MTS did not enter),
AVOIDED (setup hit stop first, MTS did not enter), UNRESOLVED (no target, no bars, never filled, still open).
Window and horizon are analysis settings, not trading parameters; both are printed in the report.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import REPO, TF_MINUTES, obs_dir, parse_time, iso  # noqa: E402

MTS_SYMBOLS = {"BTCUSDT", "BTCUSD", "BTC-PERPETUAL", "BTC", "BTCUSDT.P"}
# Strongest MTS response first; the strongest same-side event in the window is the reason.
REASON_ORDER = ("entered", "attempt", "blocked", "rejected", "halt", "busy", "auto_pause")
EVENT_REASON = {"layer_trade_blocked": "blocked", "signal_rejected": "rejected", "skipped_halt": "halt",
                "skipped_busy": "busy", "skipped_auto_pause": "auto_pause"}
MISSED_COLUMNS = ("obs_id", "ts_market", "symbol", "timeframe", "side", "entry", "stop", "target", "verdict",
                  "mts_reason", "mts_detail", "mts_sources", "outcome", "bar_source", "fill_ts", "exit_ts", "r_multiple",
                  "mfe_r", "mae_r", "quality_flags", "session", "text")


def match_window(ts, timeframe):
    """Two bars of the read's timeframe either side, at least 10 minutes."""
    half = max(10, 2 * TF_MINUTES.get(timeframe or "1m", 1))
    return ts - timedelta(minutes=half), ts + timedelta(minutes=half)


def load_mts_events(path):
    events = []
    if not Path(path).exists():
        return events
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                r["_ts"] = parse_time(r["ts"])
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
            if r.get("side") in ("long", "short"):
                events.append(r)
    return events


def mts_response(setup, events):
    """(reason, detail, sources) for what MTS did on this side inside the window."""
    lo, hi = match_window(parse_time(setup["ts_market"]), setup.get("timeframe"))
    near = [e for e in events if lo <= e["_ts"] <= hi]
    same = [e for e in near if e["side"] == setup["side"]]
    found = {}
    for e in same:
        ev = e.get("event")
        if ev == "trade_attempt":
            reason = "entered" if e.get("outcome") == "entered" else "attempt"
            detail = e.get("plan_id") if reason == "entered" else f"outcome={e.get('outcome')}"
        elif ev in EVENT_REASON:
            reason, detail = EVENT_REASON[ev], e.get("reason") or ",".join(e.get("brakes") or []) or ""
        else:
            continue
        found.setdefault(reason, (detail, set()))[1].add(e.get("source") or "?")
    for reason in REASON_ORDER:
        if reason in found:
            detail, srcs = found[reason]
            return reason, detail, ";".join(sorted(srcs))
    if near:
        return "opposite_signal", f"{len(near)} opposite-side event(s)", ";".join(sorted({e.get("source") or "?" for e in near}))
    return "no_signal", "", ""


def load_bars(bars_dir, start, end):
    """1m bars [(t_dt, o, h, l, c)] covering start..end from orderflow_live day files."""
    bars, day = [], start.date()
    while day <= end.date():
        path = Path(bars_dir) / f"{day.isoformat()}.csv"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        t = datetime.fromtimestamp(int(row["t"]) / 1000, tz=timezone.utc)
                        bars.append((t, float(row["o"]), float(row["h"]), float(row["l"]), float(row["c"])))
                    except (KeyError, ValueError):
                        continue
        day += timedelta(days=1)
    return sorted(b for b in bars if start - timedelta(minutes=1) < b[0] <= end)


def load_klines(path, start, end):
    """Binance kline archive (list of {open_time, open, high, low, close}) -> bars like load_bars."""
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    bars = [(datetime.fromtimestamp(k["open_time"] / 1000, tz=timezone.utc), k["open"], k["high"], k["low"], k["close"])
            for k in rows]
    return sorted(b for b in bars if start < b[0] <= end)


def bars_for(t0, horizon, bars_dir, klines_path):
    """1m bars when the recorder has the bar holding the read, else 5m klines. Returns (bars, bar_minutes, source)."""
    one = load_bars(bars_dir, t0 - timedelta(minutes=1), t0 + horizon)
    if one and one[0][0] <= t0:
        return one, 1, "1m"
    five = load_klines(klines_path, t0 - timedelta(minutes=5), t0 + horizon)
    if five and five[0][0] <= t0:
        return five, 5, "5m"
    return [], 1, None


def score(setup, bars, horizon, bar_minutes=1):
    """Walk bars from the read. Stop and target in the same bar count as the stop (conservative)."""
    out = {"outcome": "no_bars", "fill_ts": None, "exit_ts": None, "r_multiple": None, "mfe_r": None, "mae_r": None}
    t0 = parse_time(setup["ts_market"])
    path = [b for b in bars if t0 - timedelta(minutes=bar_minutes) < b[0] <= t0 + horizon]
    if not path:
        return out
    sign = 1 if setup["side"] == "long" else -1
    stop, target, entry = setup["stop"], setup.get("target"), setup.get("entry")
    i = 0
    if entry is None:
        entry, out["fill_ts"] = path[0][4], iso(path[0][0])  # at market: close of the bar holding the read
        i = 1
    else:
        while i < len(path) and not (path[i][3] <= entry <= path[i][2]):
            i += 1
        if i == len(path):
            out["outcome"] = "not_filled"
            return out
        out["fill_ts"] = iso(path[i][0])
    risk = sign * (entry - stop)
    if risk <= 0:
        out["outcome"] = "stop_beyond_entry"
        return out
    mfe = mae = 0.0
    for t, o, h, l, c in path[i:]:
        fav, adv = (h, l) if sign > 0 else (l, h)
        mfe, mae = max(mfe, sign * (fav - entry)), max(mae, sign * (entry - adv))
        if sign * (adv - stop) <= 0:
            out.update(outcome="stop", exit_ts=iso(t), r_multiple=-1.0)
            break
        if target is not None and sign * (fav - target) >= 0:
            out.update(outcome="target", exit_ts=iso(t), r_multiple=round(sign * (target - entry) / risk, 2))
            break
    else:
        out["outcome"] = "open_at_horizon" if target is not None else "no_target"
    out["mfe_r"], out["mae_r"] = round(mfe / risk, 2), round(mae / risk, 2)
    return out


def verdict(reason, outcome):
    if reason == "entered":
        return "CAUGHT"
    return {"target": "MISSED", "stop": "AVOIDED"}.get(outcome, "UNRESOLVED")


def analyse(setups, events, bars_dir, horizon, klines_path=""):
    rows = []
    for s in setups:
        covered = (s.get("symbol") or "").upper() in MTS_SYMBOLS
        if covered:
            reason, detail, sources = mts_response(s, events)
            bars, minutes, source = bars_for(parse_time(s["ts_market"]), horizon, bars_dir, klines_path)
            sc = score(s, bars, horizon, minutes) | {"bar_source": source}
        else:
            reason, detail, sources = "not_covered", f"MTS does not trade {s.get('symbol')}", ""
            sc = score(s, [], horizon) | {"bar_source": None}
        row = {k: s.get(k) for k in MISSED_COLUMNS}
        row.update(sc, mts_reason=reason, mts_detail=detail, mts_sources=sources,
                   verdict=verdict(reason, sc["outcome"]), quality_flags=";".join(s.get("quality_flags") or []))
        rows.append(row)
    return rows


def report(rows, params):
    by_v, by_r = {}, {}
    for r in rows:
        by_v[r["verdict"]] = by_v.get(r["verdict"], 0) + 1
        if r["verdict"] == "MISSED":
            by_r[r["mts_reason"]] = by_r.get(r["mts_reason"], 0) + 1
    lines = ["# Missed-trade report", "",
             f"Generated {iso(datetime.now(timezone.utc))}. Setups are chart reads (label \"chart read\"), not system data.",
             f"Settings: match window = 2 bars of the read's timeframe each side (min 10 min); horizon {params['horizon_h']} h; "
             "stop and target in one bar = stop; bars are 1m, or 5m klines where the 1m recorder has a gap (column bar_source).", "",
             "| Verdict | Count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(by_v.items())]
    if by_r:
        lines += ["", "## Why MTS missed", "", "| MTS reason | Count |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in sorted(by_r.items(), key=lambda kv: -kv[1])]
    missed = [r for r in rows if r["verdict"] == "MISSED"]
    if missed:
        lines += ["", "## Missed setups", "", "| Time (UTC) | TF | Side | Entry | Stop | Target | R | MTS reason | Detail | Flags |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for r in missed:
            lines.append(f"| {r['ts_market']} | {r['timeframe']} | {r['side']} | {r['entry']} | {r['stop']} | {r['target']} "
                         f"| {r['r_multiple']} | {r['mts_reason']} | {r['mts_detail']} | {r['quality_flags']} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--dir", help="observation store (same as capture.py)")
    p.add_argument("--auto-trades", default=str(REPO / "MyTradingSys" / "execution" / "auto_trades.jsonl"))
    p.add_argument("--bars", default=str(REPO / "MyTradingSys" / "runtime" / "orderflow_live"))
    p.add_argument("--klines", default=str(REPO / "MyTradingSys" / "market_data" / "klines" / "BTCUSDT_5m.json"))
    p.add_argument("--horizon-h", type=float, default=24.0)
    args = p.parse_args(argv)
    derived = obs_dir(args.dir) / "derived"
    src = derived / "observations.jsonl"
    if not src.exists():
        print(f"REFUSED: {src} missing; run capture.py build first", file=sys.stderr)
        return 2
    with open(src, encoding="utf-8") as f:
        setups = [r for r in map(json.loads, filter(str.strip, f)) if r.get("side") and not r.get("superseded")]
    rows = analyse(setups, load_mts_events(args.auto_trades), args.bars, timedelta(hours=args.horizon_h), args.klines)
    with open(derived / "missed.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MISSED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: r.get(k) for k in MISSED_COLUMNS} for r in rows)
    with open(derived / "MISSED_REPORT.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(report(rows, {"horizon_h": args.horizon_h}))
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(json.dumps({"setups": len(rows), **counts, "report": str(derived / "MISSED_REPORT.md")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
