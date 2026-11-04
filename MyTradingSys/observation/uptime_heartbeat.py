import sys
sys.dont_write_bytecode = True

"""
Uptime from a heartbeat file (D3 M4), not from a reviver.

write_beat appends one JSON line {"utc", "host"}; read_uptime buckets 1-minute slots
per UTC day and returns per-day and window percent. Fails closed: missing/unreadable
file, no valid beat for the host = NOT_IN_DATA; torn lines, wrong-host lines and
stamps more than FUTURE_LIMIT_S ahead of now get no credit. A minute counts once.

Defaults (DECISION OURS unless stated):
- slot = 1 minute (OURS)
- future limit = 2 minutes (OURS)
- bar = 95.0 percent (SOURCED MyTradingSys/system/GO_LIVE_BAR.md:13)
- file = MyTradingSys/observation/uptime_heartbeat.jsonl (gitignored runtime data)
- current UTC day is measured over the minutes elapsed so far, not the full day.
No network, exchange or account input. Wiring the writer into a loop is out of scope.
"""

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

SLOT_S = 60
FUTURE_LIMIT_S = 120
BAR_PCT = 95.0
DEFAULT_FILE = Path(__file__).resolve().parent / "uptime_heartbeat.jsonl"
_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _now(now):
    return now if now is not None else datetime.now(timezone.utc)


def write_beat(path=None, host="JIS-NB", now=None):
    """Append one beat line in a single write call (O_APPEND, one line)."""
    path = Path(path) if path else DEFAULT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"utc": _now(now).astimezone(timezone.utc).strftime(_FMT), "host": host}) + "\n"
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    return path


def _slots(path, host, now):
    """Set of valid slot indexes (epoch seconds // 60); None when unreadable."""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    limit = now.timestamp() + FUTURE_LIMIT_S
    out = set()
    for raw in text.splitlines():
        try:
            row = json.loads(raw)
            if row.get("host") != host:
                continue
            t = datetime.strptime(row["utc"], _FMT).replace(tzinfo=timezone.utc).timestamp()
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        if t > limit:
            continue
        out.add(int(t // SLOT_S))
    return out


def read_uptime(path=None, host="JIS-NB", days=14, now=None):
    now = _now(now).astimezone(timezone.utc)
    res = {"status": "NOT_IN_DATA", "host": host, "days": {}, "pct": None, "pass": False, "bar": BAR_PCT}
    slots = _slots(path or DEFAULT_FILE, host, now)
    if not slots:
        return res
    now_slot = int(now.timestamp() // SLOT_S)
    last = datetime.fromtimestamp((now_slot - 1) * SLOT_S, timezone.utc)  # last fully elapsed minute
    today = last.replace(hour=0, minute=0, second=0, microsecond=0)
    got = total = 0
    for i in range(days - 1, -1, -1):
        d0 = today - timedelta(days=i)
        s0 = int(d0.timestamp() // SLOT_S)
        s1 = min(s0 + 1440, now_slot)
        n = s1 - s0
        if n <= 0:
            continue
        c = sum(1 for s in range(s0, s1) if s in slots)
        res["days"][d0.strftime("%Y-%m-%d")] = round(100.0 * c / n, 2)
        got += c
        total += n
    if total == 0:
        return res
    res["status"] = "OK"
    res["pct"] = round(100.0 * got / total, 2)
    res["pass"] = res["pct"] >= BAR_PCT
    return res


def _main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("--host", default="JIS-NB")
    r.add_argument("--days", type=int, default=14)
    r.add_argument("--file", default=None)
    r.add_argument("--now", default=None)
    b = sub.add_parser("beat")
    b.add_argument("--host", default="JIS-NB")
    b.add_argument("--file", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "beat":
        print(write_beat(a.file, a.host))
        return 0
    now = datetime.strptime(a.now, _FMT).replace(tzinfo=timezone.utc) if a.now else None
    res = read_uptime(a.file, a.host, a.days, now)
    if res["status"] != "OK":
        print(f"{a.host}: NOT_IN_DATA")
        return 0
    for d, p in res["days"].items():
        print(f"{d}  {p:.1f}")
    print(f"{a.days}-day {res['pct']:.1f} percent: {'PASS' if res['pass'] else 'FAIL'} (bar {BAR_PCT})")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
