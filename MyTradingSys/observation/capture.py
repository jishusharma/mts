"""Capture channel for live sessions (schema obs.v1) and the normalizer that turns captures into a dataset.

Live sessions only append; nothing here reads or writes the running system.

  python MyTradingSys/observation/capture.py add --session <id> --kind chart_read --symbol BTCUSDT --tf 15m \
      --at 2026-10-08T02:47+05:30 --side short --entry 83550 --stop 83800 --target 82706 --text "..."
  python MyTradingSys/observation/capture.py build          # captures/*.jsonl -> derived/observations.jsonl, setups.csv

Storage: --dir, else env MTS_OBS_DIR, else <repo>/runtime_data/observations (gitignored, lives on JIS-NB).
Rules come from methodology/live_session_protocol.md (rule 4 labels, rule 9 corrections),
methodology/chart_read_protocol.md (six layers, "no invalidation, no read") and VVP-002 C.1 (footprint zones).
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

SCHEMA = "obs.v1"
REPO = Path(__file__).resolve().parents[2]

KINDS = ("chart_read", "trade_call", "question", "answer", "system_quote", "note", "correction")
LABELS = ("chart read", "system", "inferred", "operator")
# live_session_protocol rule 4: chart numbers are "chart read", pasted numbers are "system".
DEFAULT_LABEL = {"chart_read": "chart read", "trade_call": "chart read", "system_quote": "system",
                 "question": "operator", "answer": "inferred", "note": "inferred", "correction": "inferred"}
FORCED_LABEL = {"chart_read": "chart read", "system_quote": "system"}
TF_MINUTES = {"1m": 1, "3m": 3, "4m": 4, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "3h": 180, "4h": 240,
              "6h": 360, "7h": 420, "8h": 480, "12h": 720, "1d": 1440, "1w": 10080}
SIDES = ("long", "short")
SIX_LAYERS = ("panel", "neutral", "cross_view", "htf", "falsify", "invalidation")
SETUP_COLUMNS = ("obs_id", "ts_market", "session", "kind", "symbol", "timeframe", "side", "entry", "stop",
                 "target", "level", "trigger", "chart_source", "zones_marked", "quality_flags", "text")


class ObsError(ValueError):
    pass


def obs_dir(explicit=None):
    return Path(explicit or os.environ.get("MTS_OBS_DIR") or REPO / "runtime_data" / "observations")


def parse_time(value, tz=None):
    """ISO time -> aware UTC datetime. Naive times need tz (chart clocks differ: IST vs UTC), else refuse."""
    s = value.strip().replace(" ", "T")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        raise ObsError(f"time not ISO 8601: {value!r}")
    if dt.tzinfo is None:
        if not tz:
            raise ObsError(f"time {value!r} has no offset; pass --tz (e.g. +05:30 for an IST chart clock)")
        dt = datetime.fromisoformat(s + (tz if tz[0] in "+-" else "+" + tz))
    return dt.astimezone(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(v, name):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        raise ObsError(f"{name} must be a number, got {v!r}")


def validate(rec):
    """Return the record with defaults filled, or raise ObsError. Same check for add and build."""
    r = dict(rec)
    if r.get("schema") != SCHEMA:
        raise ObsError(f"schema must be {SCHEMA}")
    for f in ("ts_logged", "ts_market", "session", "kind", "text"):
        if not r.get(f):
            raise ObsError(f"missing {f}")
    if r["kind"] not in KINDS:
        raise ObsError(f"kind must be one of {KINDS}")
    r["label"] = r.get("label") or DEFAULT_LABEL[r["kind"]]
    if r["label"] not in LABELS:
        raise ObsError(f"label must be one of {LABELS}")
    forced = FORCED_LABEL.get(r["kind"])
    if forced and r["label"] != forced:
        raise ObsError(f"kind {r['kind']} must be labeled {forced!r} (live_session_protocol rule 4)")
    parse_time(r["ts_market"]), parse_time(r["ts_logged"])
    tf = r.get("timeframe")
    if tf is not None and tf not in TF_MINUTES:
        raise ObsError(f"timeframe must be one of {tuple(TF_MINUTES)}")
    if r["kind"] in ("chart_read", "trade_call") and (not r.get("symbol") or not tf):
        raise ObsError(f"{r['kind']} needs symbol and timeframe")
    if r["kind"] == "trade_call" and not r.get("side"):
        raise ObsError("trade_call needs side")
    if r["kind"] == "correction" and not r.get("supersedes"):
        raise ObsError("correction needs supersedes=<obs_id>")
    for f in ("entry", "stop", "target"):
        r[f] = _num(r.get(f), f)
    side = r.get("side")
    if side is not None:
        if side not in SIDES:
            raise ObsError(f"side must be one of {SIDES}")
        if r["stop"] is None:
            raise ObsError("a setup with a side needs stop (chart_read_protocol: no invalidation, no read)")
        sign = 1 if side == "long" else -1
        if r["entry"] is not None:
            if sign * (r["entry"] - r["stop"]) <= 0:
                raise ObsError(f"{side} stop must be {'below' if sign > 0 else 'above'} entry")
            if r["target"] is not None and sign * (r["target"] - r["entry"]) <= 0:
                raise ObsError(f"{side} target must be {'above' if sign > 0 else 'below'} entry")
    r.setdefault("chart", {})
    r.setdefault("layers", {})
    unknown = set(r["layers"]) - set(SIX_LAYERS)
    if unknown:
        raise ObsError(f"unknown six-layer keys {sorted(unknown)}; use {SIX_LAYERS}")
    r.setdefault("refs", [])
    return r


def make_id(rec):
    body = json.dumps({k: rec.get(k) for k in ("ts_logged", "session", "kind", "ts_market", "text")}, sort_keys=True)
    return hashlib.sha1(body.encode("utf-8")).hexdigest()[:12]


def append(rec, directory=None, now=None):
    """Validate, stamp, append one line to captures/<UTC date>.jsonl. Returns the stored record."""
    rec = dict(rec, schema=SCHEMA)
    rec.setdefault("ts_logged", iso(now or datetime.now(timezone.utc)))
    rec = validate(rec)
    rec["obs_id"] = rec.get("obs_id") or make_id(rec)
    path = obs_dir(directory) / "captures" / (rec["ts_logged"][:10] + ".jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0))
    try:
        os.write(fd, line)
    finally:
        os.close(fd)
    return rec


def quality_flags(r):
    """Protocol gaps that do not block capture but lower trust in the read."""
    flags = []
    if r["kind"] == "chart_read":
        missing = [k for k in SIX_LAYERS if not r["layers"].get(k)]
        if missing:
            flags.append("six_layer_missing:" + "+".join(missing))
    src = (r["chart"].get("source") or "").lower()
    if "footprint" in src and not r["chart"].get("zones_marked"):
        flags.append("footprint_no_zones")  # VVP-002 C.1: no proof claim without POC/VAH/VAL marked
    if r.get("side") and r.get("target") is None:
        flags.append("no_target")
    if r.get("side") and r.get("entry") is None:
        flags.append("entry_at_market")
    return flags


def load_captures(directory=None):
    """All capture lines -> (valid records, rejects). Rejects keep file:line and the reason; nothing is dropped silently."""
    good, rejects, seen = [], [], set()
    for path in sorted((obs_dir(directory) / "captures").glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    r = validate(json.loads(line))
                except (json.JSONDecodeError, ObsError) as e:
                    rejects.append({"where": f"{path.name}:{n}", "reason": str(e)})
                    continue
                r["obs_id"] = r.get("obs_id") or make_id(r)
                if r["obs_id"] in seen:
                    continue
                seen.add(r["obs_id"])
                good.append(r)
    return good, rejects


def build(directory=None):
    """Normalize: UTC times, superseded flag, quality flags. Writes derived/observations.jsonl and setups.csv."""
    recs, rejects = load_captures(directory)
    superseded = {r["supersedes"] for r in recs if r.get("supersedes")}
    for r in recs:
        r["ts_market"] = iso(parse_time(r["ts_market"]))
        r["superseded"] = r["obs_id"] in superseded
        r["quality_flags"] = quality_flags(r)
    recs.sort(key=lambda r: (r["ts_market"], r["ts_logged"]))
    setups = [r for r in recs if r.get("side") and not r["superseded"]]
    out = obs_dir(directory) / "derived"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "observations.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    with open(out / "setups.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SETUP_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in setups:
            row = {k: r.get(k) for k in SETUP_COLUMNS}
            row["chart_source"] = r["chart"].get("source")
            row["zones_marked"] = r["chart"].get("zones_marked")
            row["quality_flags"] = ";".join(r["quality_flags"])
            w.writerow(row)
    with open(out / "rejects.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(rejects, f, indent=1)
    return {"observations": len(recs), "setups": len(setups), "rejects": len(rejects), "dir": str(out)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--dir", help="observation store (default env MTS_OBS_DIR or runtime_data/observations)")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="append one observation")
    a.add_argument("--session", required=True, help="source session id or name")
    a.add_argument("--kind", required=True, choices=KINDS)
    a.add_argument("--text", required=True, help="the read / question / call, verbatim")
    a.add_argument("--at", required=True, help="market time the read refers to (ISO; naive needs --tz)")
    a.add_argument("--tz", help="offset for a naive --at, e.g. +05:30 (IST chart) or +00:00")
    a.add_argument("--label", choices=LABELS)
    a.add_argument("--symbol")
    a.add_argument("--tf", dest="timeframe", choices=tuple(TF_MINUTES))
    a.add_argument("--side", choices=SIDES)
    a.add_argument("--entry"); a.add_argument("--stop"); a.add_argument("--target")
    a.add_argument("--level", help="named level, e.g. weekly_vah")
    a.add_argument("--trigger", help="what would make it actionable")
    a.add_argument("--chart-source", help="tradingview / binance / footprint / heatmap ...")
    a.add_argument("--image", help="screenshot filename")
    a.add_argument("--zones-marked", action="store_true", help="POC/VAH/VAL lines visible (VVP-002 C.1)")
    for k in SIX_LAYERS:
        a.add_argument(f"--{k.replace('_', '-')}", dest=f"L_{k}", help=f"six-layer: {k}")
    a.add_argument("--supersedes", help="obs_id this corrects")
    a.add_argument("--ref", action="append", default=[], help="thread link, message id, file path")
    sub.add_parser("build", help="normalize captures into derived/")
    args = p.parse_args(argv)
    try:
        if args.cmd == "add":
            rec = {k: getattr(args, k) for k in ("session", "kind", "text", "label", "symbol", "timeframe", "side",
                                                 "entry", "stop", "target", "level", "trigger", "supersedes")}
            rec = {k: v for k, v in rec.items() if v is not None}
            rec["ts_market"] = iso(parse_time(args.at, args.tz))
            rec["chart"] = {k: v for k, v in (("source", args.chart_source), ("image", args.image)) if v}
            if args.zones_marked:
                rec["chart"]["zones_marked"] = True
            rec["layers"] = {k: getattr(args, f"L_{k}") for k in SIX_LAYERS if getattr(args, f"L_{k}")}
            rec["refs"] = args.ref
            stored = append(rec, args.dir)
            print(f"OK {stored['obs_id']} {stored['kind']} [{stored['label']}] {stored['ts_market']}")
        else:
            print(json.dumps(build(args.dir)))
    except ObsError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
