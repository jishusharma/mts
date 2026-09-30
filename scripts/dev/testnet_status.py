"""Sanitized daily testnet status file, written for the cloud session to read from git.

Runs on the desktop (where the live files are). Parses the files directly (pure stdlib; never imports anything from
MyTradingSys/execution/ and never opens .secrets/ or .env) and writes
  MyTradingSys/research/testnet_status/TESTNET_STATUS_<YYYY-MM-DD>.md   (UTF-8, LF)

Sources (all under MyTradingSys/execution/ unless overridden; each may be missing -> "not found"):
  auto_trades.jsonl        auto-trader decision log (signal_rejected, skipped_*, trade_attempt, trade_closed, ...)
  trade_ledger.jsonl       one row per closed auto-trade (plan_id + net_pnl_usd, or "unresolved")
  OPERATOR_ALERTS.log      auto_trader operator alerts (text, scrubbed)
  halt_history/            archived HALT files (file NAMES and mtimes only, contents never read)
  auto_trader_config.json  account routing (family prefix -> account label), same map the trader uses
Existence of HALT / HALT_DAILY_LOSS / AUTO_PAUSE is checked (never read).

Sanitized output: no order ids, plan ids, client ids, keys or secrets, no balances. Free text is passed through
scrub(); log rows' own text fields (output, detail, reason text) are never printed, only classified.

Usage (repo root):  python scripts/dev/testnet_status.py [--hours 24] [--now ISO] [--exec-dir D] [--auto-log F]
                    [--ledger F] [--alerts-log F] [--halt-dir D] [--config F] [--out-dir D]
"""
import argparse
import json
import os
import pathlib
import re
import sys
from datetime import datetime, timedelta, timezone

REPO = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_EXEC = REPO / "MyTradingSys" / "execution"
DEFAULT_OUT = REPO / "MyTradingSys" / "research" / "testnet_status"
TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
BRAKE_FILES = ("HALT", "HALT_DAILY_LOSS", "AUTO_PAUSE")

_KW = re.compile(r"(?i)\b(api[_-]?key|client[_-]?id|client[_-]?secret|secret|token|password|passwd|authorization|"
                 r"bearer|key)\b(\s*[:=]\s*|\s+)\S+")
_ORDER = re.compile(r"\b[A-Z]{2,}-\d{6,}\b")
_PLAN = re.compile(r"\b[A-Z]-[A-Za-z]+-\d{4}-\d{4}(?:-\d+)?\b")
_DIGITS = re.compile(r"\b\d{8,}\b")
_TOKEN = re.compile(r"(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])\b[A-Za-z0-9_\-]{20,}\b")


def scrub(text, limit=200):
    """Redact key-like / id-like strings from free text and cap its length."""
    s = str(text)
    s = _KW.sub("[redacted]", s)
    for rx in (_ORDER, _PLAN, _DIGITS, _TOKEN):
        s = rx.sub("[id]", s)
    s = " ".join(s.split())
    return s[:limit]


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_.\-]", "?", name)[:60]


def parse_ts(s):
    try:
        return datetime.strptime(str(s), TS_FMT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def read_jsonl(path):
    """(rows, unparseable_count) or (None, 0) when the file does not exist / cannot be read."""
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, 0
    rows, bad = [], 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            bad += 1
            continue
        if isinstance(r, dict):
            rows.append(r)
        else:
            bad += 1
    return rows, bad


def load_config(path):
    try:
        cfg = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        accts = cfg.get("accounts") or {}
        return {str(k): str(v) for k, v in accts.items()}, True
    except (OSError, ValueError, AttributeError):
        return {}, False


def family_of(source):
    source = str(source or "")
    if source == "tom" or source.startswith("tom:"):
        return "tom"
    if source.startswith("layer:"):
        parts = source.split(":")
        return parts[1] if len(parts) > 1 and parts[1] else "layer"
    return source.split(":")[0] or "?"


def route(source, accounts):
    """Account label for a source: first matching prefix in config order (as the trader does), else 'main'."""
    for prefix, label in accounts.items():
        if str(source or "").startswith(prefix):
            return label
    return "main"


def account_of(row, accounts):
    if "account" in row:
        return row["account"] or "main"
    return route(row.get("source"), accounts)


COLS = ("Alerts", "Entered", "Closed", "Wins", "Net USD", "Busy", "AutoPause", "Unmapped", "Rejected", "Halt",
        "Failed", "Unresolved")


def blank():
    return {"alerts": 0, "entered": 0, "closed": 0, "wins": 0, "net": 0.0, "busy": 0, "auto_pause": 0,
            "unmapped": 0, "rejected": 0, "halt": 0, "failed": 0, "unresolved": 0}


def analyse(log_rows, ledger_rows, accounts, t0, t1):
    rows, open_by_acct, skipped_halt = {}, {}, 0

    def cell(row):
        return rows.setdefault((family_of(row.get("source")), account_of(row, accounts)), blank())

    def in_win(r):
        t = parse_ts(r.get("ts"))
        return t is not None and t0 <= t <= t1

    # open positions from the WHOLE log: entered without a later trade_closed for the same plan
    pending = {}
    for r in log_rows or []:
        pid = r.get("plan_id")
        if r.get("event") == "trade_attempt" and r.get("outcome") == "entered" and pid:
            pending[pid] = account_of(r, accounts)
        elif r.get("event") == "trade_closed" and pid:
            pending.pop(pid, None)
    for acct in pending.values():
        open_by_acct[acct] = open_by_acct.get(acct, 0) + 1

    starts_with_brakes = 0
    for r in log_rows or []:
        if not in_win(r):
            continue
        ev = r.get("event")
        if ev == "start" and r.get("brakes"):
            starts_with_brakes += 1
        if ev not in ("signal_rejected", "skipped_halt", "skipped_auto_pause", "skipped_busy", "trade_attempt"):
            continue
        c = cell(r)
        c["alerts"] += 1
        if ev == "signal_rejected":
            c["unmapped" if str(r.get("reason", "")).startswith("unmapped") else "rejected"] += 1
        elif ev == "skipped_halt":
            c["halt"] += 1
            skipped_halt += 1
        elif ev == "skipped_auto_pause":
            c["auto_pause"] += 1
        elif ev == "skipped_busy":
            c["busy"] += 1
        else:
            out = r.get("outcome")
            if out == "entered":
                c["entered"] += 1
            elif out != "dry_run":
                c["failed"] += 1

    ignored = 0
    for r in ledger_rows or []:
        if not r.get("plan_id") or not ("net_pnl_usd" in r or r.get("unresolved")):
            ignored += 1                              # transfer-like / non-trade row: never a trade
            continue
        if not in_win(r):
            continue
        c = cell(r)
        if r.get("unresolved"):
            c["unresolved"] += 1
            continue
        net = r.get("net_pnl_usd")
        if not isinstance(net, (int, float)):
            c["unresolved"] += 1
            continue
        c["closed"] += 1
        c["net"] += net
        c["wins"] += 1 if net > 0 else 0
    return rows, open_by_acct, skipped_halt, starts_with_brakes, ignored


def expected_keys(accounts):
    keys = {("tom", "main")}
    for prefix, label in accounts.items():
        parts = prefix.split(":")
        if prefix.startswith("layer:") and len(parts) > 1 and parts[1]:
            keys.add((parts[1], label))
    return keys


def fmt_ts(dt):
    return dt.strftime(TS_FMT)


def build_report(paths, now, hours):
    t1, t0 = now, now - timedelta(hours=hours)
    accounts, cfg_ok = load_config(paths["config"])
    log_rows, log_bad = read_jsonl(paths["auto_log"])
    led_rows, led_bad = read_jsonl(paths["ledger"])
    rows, open_by_acct, skipped_halt, start_brakes, ignored = analyse(log_rows, led_rows, accounts, t0, t1)
    for k in expected_keys(accounts):
        rows.setdefault(k, blank())
    hl = f"{hours:g} h"
    L = []
    L.append(f"# Testnet status {now.strftime('%Y-%m-%d')}")
    L.append("")
    L.append(f"- Window: {fmt_ts(t0)} to {fmt_ts(t1)} ({hl}). Generated {fmt_ts(now)} by scripts/dev/testnet_status.py "
             "on the desktop.")
    L.append("- Sanitized: no order/plan/client ids, keys or balances; P/L is per-trade net USD only.")
    L.append("")
    L.append("## Sources")
    if log_rows is None:
        L.append(f"- {paths['auto_log'].name}: not found")
    else:
        L.append(f"- {paths['auto_log'].name}: found, {len(log_rows)} rows, {log_bad} unparseable line(s)")
    if led_rows is None:
        L.append(f"- {paths['ledger'].name}: not found")
    else:
        L.append(f"- {paths['ledger'].name}: found, {len(led_rows)} rows, {led_bad} unparseable line(s), "
                 f"{ignored} non-trade row(s) ignored")
    L.append(f"- {paths['config'].name}: " + (f"found, {len(accounts)} routing prefixes" if cfg_ok else
                                               "not found (routing unknown: unrouted sources shown as main)"))
    L.append("")
    L.append(f"## Per family x account ({hl})")
    L.append("")
    L.append("| Family | Account | " + " | ".join(COLS) + " |")
    L.append("|---|---|" + "|".join("---:" for _ in COLS) + "|")
    for (fam, acct) in sorted(rows):
        c = rows[(fam, acct)]
        vals = [c["alerts"], c["entered"], c["closed"], c["wins"], f"{c['net']:+.4f}", c["busy"], c["auto_pause"],
                c["unmapped"], c["rejected"], c["halt"], c["failed"], c["unresolved"]]
        L.append(f"| {safe_name(fam)} | {safe_name(acct)} | " + " | ".join(str(v) for v in vals) + " |")
    L.append("")
    L.append("Alerts = signals the trader logged a decision for (rejected, skipped, attempted). Entered = trade_attempt "
             "outcome entered. Closed/Wins/Net = resolved ledger rows stamped in the window (win = net > 0). "
             "Failed = attempt that did not enter. Unresolved = ledger row without an outcome.")
    L.append("")
    L.append("## Zero-trade flags")
    flags = [f"- FLAG 0 trades in {hl}: {safe_name(f)} / {safe_name(a)}" for (f, a), c in sorted(rows.items())
             if c["entered"] == 0]
    if log_rows is None:
        L.append("- auto_trades.jsonl not found: flags below are not meaningful")
    L += flags or ["- none"]
    L.append("")
    L.append("## Open positions (last logged, not live)")
    L.append("")
    L.append("Entered in auto_trades.jsonl with no later trade_closed (whole log). Not an exchange reading.")
    L.append("")
    L.append("| Account | Open (last logged) |")
    L.append("|---|---:|")
    labels = sorted(set(accounts.values()) | {"main"} | set(open_by_acct))
    for a in labels:
        L.append(f"| {safe_name(a)} | {open_by_acct.get(a, 0)} |")
    L.append("")
    L.append("## HALT / brake events")
    L.append("")
    present = [b for b in BRAKE_FILES if paths["exec"].joinpath(b).exists()]
    L.append("- Brake files at run time: " + (", ".join(present) if present else "none present")
             + " (existence only; checked when this script ran)")
    L.append(f"- skipped_halt decisions in window: {skipped_halt}")
    L.append(f"- auto_trader starts with a brake set in window: {start_brakes}")
    hd = paths["halt_dir"]
    if not hd.is_dir():
        L.append(f"- {hd.name}/: not found")
    else:
        inwin, older = [], 0
        for p in sorted(hd.iterdir()):
            if not p.is_file() or p.name.startswith("."):
                continue
            mt = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if t0 <= mt <= t1:
                inwin.append((mt, p.name))
            else:
                older += 1
        L.append(f"- {hd.name}/: found, {len(inwin)} archived in window, {older} older")
        for mt, name in sorted(inwin):
            L.append(f"  - {fmt_ts(mt)} {safe_name(name)}")
    L.append("")
    L.append("## OPERATOR_ALERTS.log")
    L.append("")
    try:
        lines = paths["alerts_log"].read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        lines = None
    if lines is None:
        L.append(f"- {paths['alerts_log'].name}: not found")
    else:
        keep = []
        for ln in lines:
            t = parse_ts(ln.split(" ", 1)[0])
            if t is not None and t0 <= t <= t1:
                keep.append(f"{fmt_ts(t)} {scrub(ln.split(' ', 1)[1] if ' ' in ln else '')}")
        L.append(f"- {paths['alerts_log'].name}: found, {len(lines)} line(s), {len(keep)} in window")
        L += [f"  - {k}" for k in keep]
    L.append("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--now", help="window end, UTC, YYYY-MM-DDTHH:MM:SSZ (default: now)")
    ap.add_argument("--exec-dir", default=str(DEFAULT_EXEC))
    ap.add_argument("--auto-log")
    ap.add_argument("--ledger")
    ap.add_argument("--alerts-log")
    ap.add_argument("--halt-dir")
    ap.add_argument("--config")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    ex = pathlib.Path(a.exec_dir)
    paths = {"exec": ex,
             "auto_log": pathlib.Path(a.auto_log) if a.auto_log else ex / "auto_trades.jsonl",
             "ledger": pathlib.Path(a.ledger) if a.ledger else ex / "trade_ledger.jsonl",
             "alerts_log": pathlib.Path(a.alerts_log) if a.alerts_log else ex / "OPERATOR_ALERTS.log",
             "halt_dir": pathlib.Path(a.halt_dir) if a.halt_dir else ex / "halt_history",
             "config": pathlib.Path(a.config) if a.config else ex / "auto_trader_config.json"}
    now = parse_ts(a.now) if a.now else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:
        ap.error("--now must look like 2026-09-30T12:00:00Z")
    text = build_report(paths, now, a.hours)
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"TESTNET_STATUS_{now.strftime('%Y-%m-%d')}.md"
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
