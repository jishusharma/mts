"""Live Aid learning loop (card live-aid-learning-loop-1111).

Scores each Live Aid flag against the 1h price move, diffs with the previous daily file and writes
MyTradingSys/research/live_aid_learning/<date>.md. Public data only (replay / flag log), never runtime data.

Input, first found: --log <flag-log CSV: kind,side,state,at,r1h>; review events.json (replay.js output);
else the committed aggregate tables.md of research/live_aid_review_2026-11-11 (same scoring, grouped).
Hit = r1h > 0 (as analyze.py). Rule (OURS, not sourced): 'test' only if n >= 30 and |hit - 50| >= 10 points.
Usage: python scripts/dev/live_aid_learn.py --date 2026-11-11 [--log flags.csv]
"""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "MyTradingSys" / "research" / "live_aid_review_2026-11-11"
OUT = ROOT / "MyTradingSys" / "research" / "live_aid_learning"
MIN_N, MIN_GAP = 30, 10.0  # OURS


def verdict(n, hit):
    if n >= MIN_N and abs(hit - 50) >= MIN_GAP:
        return "test: %s the flag (n %d, %.0f%%)" % ("drop or invert" if hit < 50 else "keep and weight", n, hit)
    why = "n < %d" % MIN_N if n < MIN_N else "gap < %d pts" % MIN_GAP
    return "NOT-ENOUGH-EVIDENCE (%s)" % why


def mk(name, n, hit):
    return {"name": name, "n": n, "hit": hit, "verdict": verdict(n, hit)}


def score(events):
    ev = [e for e in events if e.get("r1h") not in (None, "")]
    groups = {}
    for e in ev:
        k = e["kind"]
        groups.setdefault(k, []).append(e)
        if k == "idea":
            if e.get("state"):
                groups.setdefault("idea " + e["state"], []).append(e)
            if e.get("state") in ("REJECTED", "FAILED BREAK") and e.get("at"):
                groups.setdefault("idea fade @ " + e["at"], []).append(e)
    return [mk(k, len(v), 100.0 * sum(1 for e in v if float(e["r1h"]) > 0) / len(v)) for k, v in groups.items()]


def split(rows):
    imp = [r for r in rows if r["verdict"].startswith("test")]
    return imp, [r for r in rows if r not in imp]


def load_tables_md(path):
    rows, sec = [], None
    names = {"By flag kind": "%s", "Idea by level state": "idea %s", "Idea fades (rejected / failed break) by level": "idea fade @ %s"}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            sec = names.get(line[4:].strip())
            continue
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)%\s*\|", line)
        if sec and m:
            rows.append(mk(sec % m.group(1), int(m.group(2)), float(m.group(3))))
    return rows


def load_klines(path):
    """1m closes as {open_ms: close}; accepts a bare kline list or the fixture shape {"klines": [...]}."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return {int(k[0]): float(k[4]) for k in (d["klines"] if isinstance(d, dict) else d)}


def _ms(t):
    s = str(t).replace("Z", "+00:00")
    if re.fullmatch(r"\d{9,}", s):
        return int(s)
    d = datetime.fromisoformat(s)
    return int((d if d.tzinfo else d.replace(tzinfo=timezone.utc)).timestamp() * 1000)


def fetch_klines(start_ms, end_ms):
    """Public Binance spot 1m closes {open_ms: close} for [start, end + 2 h] (data-api.binance.vision, same source as the page)."""
    import urllib.request
    out, t, end = {}, int(start_ms) // 60000 * 60000, int(end_ms) + 7200000
    while t < end:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime=%d&endTime=%d&limit=1000" % (t, end)
        r = json.loads(urllib.request.urlopen(u, timeout=30).read())
        if not r:
            break
        out.update({int(k[0]): float(k[4]) for k in r})
        t = int(r[-1][0]) + 60000
    return out


def load_logs(paths, klines=None):
    """Several day files (flag_log_<day>.csv from the page auto-save), duplicates (same t, kind, side, level) dropped."""
    seen, rows = set(), []
    for p in paths:
        for r in load_log(p, klines):
            k = (r.get("t"), r.get("kind"), r.get("side"), r.get("level"), r.get("kind") == "board" and r.get("evidence"))
            if k not in seen:
                seen.add(k)
                rows.append(r)
    return rows


def load_log(path, klines=None):
    """Old header kind,side,state,at,r1h, or the page header t,kind,side,level,evidence,price (home.js FLAG_COLS):
    level->at, evidence->state, r1h = close 60 min after t vs price, sign flipped for SHORT, None without a kline."""
    with open(path, newline="", encoding="utf-8") as f:
        out = []
        for r in csv.DictReader(f):
            if "r1h" not in r and "t" in r and "price" in r:
                r = {**r, "at": r.get("level", ""), "state": r.get("evidence", "")}
                r1h = None
                try:
                    c, px = (klines or {}).get(_ms(r["t"]) // 60000 * 60000 + 3600000), float(r["price"])
                    if c is not None and px and r.get("side") != "NEUTRAL":   # NEUTRAL = no direction claimed, nothing to score
                        r1h = round((c / px - 1) * 100 * (-1 if r.get("side") in ("SHORT", "DOWN") else 1), 4)
                except (ValueError, TypeError):
                    pass
                out.append({**r, "r1h": r1h})
            else:
                out.append({**r, "r1h": float(r["r1h"]) if r.get("r1h") else None})
        return out


def parse_prev(text):
    out = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*\d+\s*\|\s*(\d+(?:\.\d+)?)%\s*\|", line)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


def render(date, rows, src, prev, prev_date):
    rows = sorted(rows, key=lambda r: -r["n"])
    L = ["# Live Aid learning, %s" % date, "",
         "Source: %s. Hit = price moved the flag's way after 1h (descriptive, no fees). Rule (OURS): n >= %d and hit rate %.0f points from 50%%."
         % (src, MIN_N, MIN_GAP), "",
         "| change (flag group) | evidence n | hit rate | vs %s | test or NOT-ENOUGH-EVIDENCE |" % (prev_date or "previous"),
         "|---|---|---|---|---|"]
    for r in rows:
        d = "%+.0f pts" % (r["hit"] - prev[r["name"]]) if r["name"] in prev else "first run"
        L.append("| %s | %d | %.0f%% | %s | %s |" % (r["name"], r["n"], r["hit"], d, r["verdict"]))
    imp, rest = split(rows)
    L += ["", "## Worked / did not work (implement list)"]
    L += ["- %s: %s" % (r["name"], r["verdict"]) for r in imp] or ["- none passes the rule today"]
    L += ["", "## For the operator (max 6)"]
    L += ["- %s: n %d, %.0f%%, %s" % (r["name"], r["n"], r["hit"], r["verdict"]) for r in sorted(rest, key=lambda r: -abs(r["hit"] - 50))[:6]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--log", nargs="+", help="flag log CSV(s); a folder or glob is expanded (runtime_data/live_aid/flag_log_*.csv)")
    ap.add_argument("--klines", help="1m closes json (page-header CSV needs it for r1h); 'auto' = fetch public Binance 1m for the log's span")
    ap.add_argument("--since", help="MM-DD: score only replay events from this day on (replay events.json only)")
    ap.add_argument("--out-dir", default=str(OUT))
    a = ap.parse_args(argv)
    ev = REVIEW / "events.json"
    if a.log:
        import glob
        files = sorted(f for g in a.log for f in (glob.glob(str(Path(g) / "flag_log_*.csv")) if Path(g).is_dir() else glob.glob(g) or [g]))
        kl = None
        if a.klines == "auto":
            ts = [_ms(r["t"]) for f in files for r in load_log(f)]
            kl = fetch_klines(min(ts), max(ts)) if ts else {}
        elif a.klines:
            kl = load_klines(a.klines)
        rows, src = score(load_logs(files, kl)), "flag log %d file(s)" % len(files)
    elif ev.exists():
        evs = json.loads(ev.read_text())
        if a.since:
            evs = [e for e in evs if e["t"][:5] >= a.since]
        rows, src = score(evs), "replay events.json" + (" from " + a.since if a.since else "")
    else:
        rows, src = load_tables_md(REVIEW / "tables.md"), "replay aggregates (live_aid_review_2026-11-11/tables.md)"
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    earlier = sorted(p for p in out.glob("*.md") if p.stem < a.date)
    prev = parse_prev(earlier[-1].read_text(encoding="utf-8")) if earlier else {}
    (out / (a.date + ".md")).write_text(render(a.date, rows, src, prev, earlier[-1].stem if earlier else None), encoding="utf-8")
    print("wrote %s rows=%d" % (out / (a.date + ".md"), len(rows)))


if __name__ == "__main__":
    main()
