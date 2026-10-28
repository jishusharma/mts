"""Read-only per-source live funnel report (L4, TOM_FABIO_REVIEW_2026-10-03.md section 2).

alert -> verdict -> attempt -> fill -> exit, per source, per UTC day.
Inputs (never written): execution/auto_trades.jsonl, execution/trade_ledger.jsonl, runtime/alerts/<tf>.jsonl.

Columns: alerts (runtime/alerts rows, source layer:<layer>:<sub>:<tf>, day of t_close), rejected / skipped
(auto_trader verdicts, day of ts), attempts, filled (outcome entered), nofill (no_fill + entry_failed),
closed (ledger rows with an exit), wins, net (sum net_pnl_usd). Ledger rows are cohorted by alert_ts day and
de-duplicated by plan_id (last wins). Alerts with no auto_trader row are not an error: only some alert
rows are actionable.

    python scripts/dev/funnel_report.py [--day YYYY-MM-DD | --days N] [--root DIR]
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COLS = ["alerts", "rejected", "skipped", "attempts", "filled", "nofill", "closed", "wins", "net"]
SKIP_EVENTS = ("skipped_busy", "skipped_auto_pause")


def read_jsonl(path):
    """Return (rows, bad_line_count). Missing file -> ([], 0)."""
    rows, bad = [], 0
    p = Path(path)
    if not p.exists():
        return rows, bad
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                bad += 1
                continue
            if isinstance(d, dict):
                rows.append(d)
            else:
                bad += 1
    return rows, bad


def alert_source(row):
    return "layer:%s:%s:%s" % (row.get("layer"), row.get("sub"), row.get("tf"))


def alert_day(row):
    t = row.get("t_close")
    if not isinstance(t, (int, float)) or isinstance(t, bool):
        return None
    return datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def build(trades, ledger, alerts):
    """{(day, source): {col: value}} from already-loaded rows."""
    t = defaultdict(lambda: dict.fromkeys(COLS, 0))
    for a in alerts:
        d = alert_day(a)
        if d:
            t[(d, alert_source(a))]["alerts"] += 1
    for r in trades:
        ev, ts = r.get("event"), str(r.get("ts") or "")[:10]
        if len(ts) != 10:
            continue
        key = (ts, r.get("source") or "unknown")
        if ev == "signal_rejected":
            t[key]["rejected"] += 1
        elif ev in SKIP_EVENTS:
            t[key]["skipped"] += 1
        elif ev == "trade_attempt":
            t[key]["attempts"] += 1
            if r.get("outcome") == "entered":
                t[key]["filled"] += 1
            else:
                t[key]["nofill"] += 1
    by_plan = {}
    for i, r in enumerate(ledger):
        by_plan[r.get("plan_id") or ("_row%d" % i)] = r
    for r in by_plan.values():
        day = str(r.get("alert_ts") or r.get("ts") or "")[:10]
        if len(day) != 10 or not r.get("exits"):
            continue
        c = t[(day, r.get("source") or "unknown")]
        c["closed"] += 1
        net = r.get("net_pnl_usd")
        if isinstance(net, (int, float)) and not isinstance(net, bool):
            c["net"] += net
            if net > 0:
                c["wins"] += 1
    return t


def render(table, days=None):
    keys = sorted(k for k in table if days is None or k[0] in days)
    out = ["| day | source | " + " | ".join(COLS) + " |", "|---|---|" + "---|" * len(COLS)]
    for k in keys:
        v = table[k]
        cells = [("%.4f" % v[c]) if c == "net" else str(v[c]) for c in COLS]
        out.append("| %s | %s | %s |" % (k[0], k[1], " | ".join(cells)))
    tot = dict.fromkeys(COLS, 0)
    for k in keys:
        for c in COLS:
            tot[c] += table[k][c]
    out.append("| TOTAL | | " + " | ".join(("%.4f" % tot[c]) if c == "net" else str(tot[c]) for c in COLS) + " |")
    return "\n".join(out)


def load_alerts(alert_dir):
    rows, bad = [], 0
    for f in sorted(Path(alert_dir).glob("*.jsonl")):
        r, b = read_jsonl(f)
        rows += r
        bad += b
    return rows, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--day", help="single UTC day YYYY-MM-DD")
    ap.add_argument("--days", type=int, help="last N UTC days incl. today")
    ap.add_argument("--root", default=str(REPO / "MyTradingSys"))
    a = ap.parse_args(argv)
    root = Path(a.root)
    trades, b1 = read_jsonl(root / "execution" / "auto_trades.jsonl")
    ledger, b2 = read_jsonl(root / "execution" / "trade_ledger.jsonl")
    alerts, b3 = load_alerts(root / "runtime" / "alerts")
    days = None
    if a.day:
        days = {a.day}
    elif a.days:
        today = datetime.now(timezone.utc).date()
        days = {(today - timedelta(n)).isoformat() for n in range(a.days)}
    print(render(build(trades, ledger, alerts), days))
    print("\nrows: trades=%d ledger=%d alerts=%d; unparseable lines: %d" % (len(trades), len(ledger), len(alerts), b1 + b2 + b3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
