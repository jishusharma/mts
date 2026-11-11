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


def load_log(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{**r, "r1h": float(r["r1h"]) if r.get("r1h") else None} for r in csv.DictReader(f)]


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
    ap.add_argument("--log")
    ap.add_argument("--out-dir", default=str(OUT))
    a = ap.parse_args(argv)
    ev = REVIEW / "events.json"
    if a.log:
        rows, src = score(load_log(a.log)), "flag log " + Path(a.log).name
    elif ev.exists():
        rows, src = score(json.loads(ev.read_text())), "replay events.json"
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
