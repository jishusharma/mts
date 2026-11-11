"""Operator trade journal logger. Appends ONE JSON line to the private journal OUTSIDE the repo.

Path: env MTS_TRADE_JOURNAL, default F:/MTS_private/trade_journal.jsonl. Any path inside a git
repo is refused (fail closed: repo is PUBLIC). Check: python log_trade.py --check-path
Log:   python log_trade.py --symbol BTCUSDT --side LONG --entry 100 --stop 98 --reason "why"
         --readings-entry home=1,grid=0,adx15=1,adx1h=0,vfi15=1,wt30=1 [--exit 105 --readings-exit ...]
"""
import argparse, json, os, sys, uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = "F:/MTS_private/trade_journal.jsonl"
READINGS = ["home", "grid", "adx15", "adx1h", "vfi15", "wt30"]   # same six, same order as home.js
SCHEMA = json.loads((Path(__file__).with_name("journal_schema.json")).read_text(encoding="utf-8"))
REPO_ROOT = Path(__file__).resolve().parents[3]


def journal_path():
    return os.environ.get("MTS_TRADE_JOURNAL") or DEFAULT_PATH


def in_git_repo(path):
    """True when path is under this repo or under any directory holding .git (fail closed on doubt)."""
    try:
        p = Path(path).resolve()
    except Exception:
        return True
    try:
        p.relative_to(REPO_ROOT)
        return True
    except ValueError:
        pass
    return any((d / ".git").exists() for d in [p] + list(p.parents))


def _type_ok(v, t):
    for x in (t if isinstance(t, list) else [t]):
        if x == "null" and v is None: return True
        if x == "string" and isinstance(v, str): return True
        if x == "boolean" and isinstance(v, bool): return True
        if x == "number" and isinstance(v, (int, float)) and not isinstance(v, bool): return True
        if x == "object" and isinstance(v, dict): return True
    return False


def _check(v, sch, where, errs):
    if "$ref" in sch:
        _check(v, SCHEMA["definitions"][sch["$ref"].split("/")[-1]], where, errs); return
    if "anyOf" in sch:
        for s in sch["anyOf"]:
            e = []; _check(v, s, where, e)
            if not e: return
        errs.append(f"{where}: matches no allowed form"); return
    if "enum" in sch:
        if not any(v == e and type(v) is type(e) for e in sch["enum"]):
            errs.append(f"{where}: {v!r} not in {sch['enum']}")
        return
    if "type" in sch and not _type_ok(v, sch["type"]):
        errs.append(f"{where}: wrong type"); return
    if isinstance(v, dict):
        for k in sch.get("required", []):
            if k not in v: errs.append(f"{where}.{k}: missing")
        for k, s in sch.get("properties", {}).items():
            if k in v: _check(v[k], s, f"{where}.{k}", errs)


def validate(row):
    errs = []
    _check(row, SCHEMA, "row", errs)
    return errs


def parse_readings(s):
    out = {}
    for part in (s or "").split(","):
        if part.strip():
            k, _, v = part.partition("=")
            out[k.strip()] = int(v)
    return out


def append_row(row, path=None):
    path = path or journal_path()
    if in_git_repo(path):
        raise SystemExit(f"REFUSED: journal path is inside a git repo (public): {path}")
    errs = validate(row)
    if errs:
        raise SystemExit("REJECTED: " + "; ".join(errs))
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return str(p)


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--check-path", action="store_true")
    a.add_argument("--symbol"); a.add_argument("--side", choices=["LONG", "SHORT"])
    a.add_argument("--entry", type=float); a.add_argument("--stop", type=float); a.add_argument("--exit", type=float)
    a.add_argument("--reason"); a.add_argument("--notes", default="")
    a.add_argument("--utc-entry"); a.add_argument("--utc-exit")
    a.add_argument("--readings-entry"); a.add_argument("--readings-exit")
    n = a.parse_args(argv)
    path = journal_path()
    if n.check_path:
        if in_git_repo(path):
            print(f"REFUSED: {path} is inside a git repo"); return 2
        print(f"OK: {path}"); return 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = {"id": uuid.uuid4().hex[:12], "utc_entry": n.utc_entry or now, "utc_exit": n.utc_exit,
           "symbol": n.symbol, "side": n.side, "entry": n.entry, "stop": n.stop, "exit": n.exit,
           "reason_text": n.reason, "readings_entry": parse_readings(n.readings_entry),
           "readings_exit": parse_readings(n.readings_exit) if n.readings_exit else None, "notes": n.notes}
    print("logged to " + append_row(row, path)); return 0


if __name__ == "__main__":
    sys.exit(main())
