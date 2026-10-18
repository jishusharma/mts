"""MTS Layer and Backtest Map: what was backtested, with which layers, and a configurator that writes a task card.

  python scripts/dev/make_layer_map.py                 # writes MyTradingSys/system/artifacts/layer_map.html
  python scripts/dev/make_layer_map.py --out page.html

Read-only over the repo. Hand-kept rows live in MyTradingSys/system/layer_map.json (backtests, layers, params);
this script adds: report-file existence, TRIAL_REGISTRY.csv run counts, and the list of result-like reports that the
curated file does not index yet. The page cannot run a backtest; it only writes a NEXT_SESSION.md task card.
Zero model tokens to refresh; publish with the Artifact tool.
"""
import argparse
import collections
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
CFG = REPO / "MyTradingSys" / "system" / "layer_map.json"
TPL = Path(__file__).resolve().parent / "layer_map.tpl.html"
OUT = REPO / "MyTradingSys" / "system" / "artifacts" / "layer_map.html"
TRIALS = REPO / "MyTradingSys" / "research" / "fast_track_2026-09-27" / "bt_runs" / "TRIAL_REGISTRY.csv"
RES_WORDS = ("RESULT", "REPORT", "BACKTEST", "VERDICT", "MATRIX", "_BT")
SKIP_PARTS = ("_archive", "archive", "screenshots", "fyi_archive", "layer_lab/reports", "fast_track_2026-09-27/review")
GAPS = [
    "No machine-readable per-backtest record of which layers were on: only Tom core and Fabio v3 write variant rows (TRIAL_REGISTRY.csv); everything else is prose in a report.",
    "B154 (2026-10-10) found no result file carries per-event rows, so which layer blocked which trade cannot be recomputed from disk; 'effects' holds only counts the reports state.",
    "Runs by Opus/Codex lab write reports to research/layer_lab/reports with no layer list field; TRIALS.md is empty.",
    "Several rows are marked read depth 'header': verdict not read for this map. Add a Sonnet task to read them if the number matters.",
]


def commit():
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def trials():
    out = []
    if TRIALS.exists():
        rows = list(csv.DictReader(TRIALS.open(encoding="utf-8")))
        by = collections.OrderedDict()
        for r in rows:
            by.setdefault((r["run_id"], r["date"]), 0)
            by[(r["run_id"], r["date"])] += 1
        out = [{"run": k[0], "date": k[1], "rows": v} for k, v in by.items()]
    return out


def unindexed(indexed):
    root = REPO / "MyTradingSys"
    names = []
    for p in list((root / "research").rglob("*.md")) + list((root / "backtest").rglob("*.md")):
        rel = p.relative_to(REPO).as_posix()
        if any(s in rel for s in SKIP_PARTS) or rel in indexed:
            continue
        if any(w in p.name.upper() for w in RES_WORDS):
            names.append(rel)
    return sorted(names)


def verdict_bucket(v):
    s = (v or "").lower()
    if not s or "not recorded" in s or "not read" in s:
        return "verdict not read"
    if "smoke" in s or "descriptive" in s or "no-source" in s:
        return "not a result (smoke / descriptive / NO-SOURCE)"
    if any(k in s for k in ("no edge", "fail", "no cell", "no validated", "no anchor", "insufficient")):
        return "no edge / fail / insufficient n"
    return "mixed or other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    ids = {l["id"] for l in cfg["layers"]}
    for b in cfg["backtests"]:
        b["exists"] = (REPO / b["report"]).exists()
        for x in b["layers"]:
            if x not in ids:
                raise SystemExit("backtest %s names unknown layer %s" % (b["id"], x))
    indexed = {b["report"] for b in cfg["backtests"]}
    vc = collections.Counter(verdict_bucket(b.get("verdict")) for b in cfg["backtests"])
    single = sum(1 for b in cfg["backtests"] if len(b["layers"]) == 1)
    data = {
        "asof": cfg["asof"], "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"), "commit": commit(),
        "layers": cfg["layers"], "backtests": cfg["backtests"], "verdictCounts": dict(vc), "trials": trials(),
        "unindexed": unindexed(indexed), "gaps": GAPS,
        "headline": "%d backtests/studies on %d layer families are indexed; %d tested a single layer alone. No indexed run found a validated edge: "
                    "the closed ones are FAIL, no edge or insufficient n, and the Tom/Fabio encoding on BTC is under a STOP while it is redefined. "
                    "The map shows what each run switched on; where the repo does not say, the cell reads 'not recorded'." % (len(cfg["backtests"]), len({l['family'] for l in cfg['layers']}), single),
    }
    html = TPL.read_text(encoding="utf-8").replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print("wrote %s (%d backtests, %d layers, %d unindexed reports, %d bytes)" % (out, len(cfg["backtests"]), len(cfg["layers"]), len(data["unindexed"]), len(html)))


if __name__ == "__main__":
    main()
