"""Build sim_desk/results/_catalogue.json: one row per known test on trunk (tracked files only).

Sources: system/layer_map.json (backtest rows with verdicts), research/**/RESULT*.md|VERDICT*.md study notes,
trials ledgers (trials.csv / TRIALS.md), the DSA audit T01..T10 notes. Read-only. `kind` is INFERRED from file
text and names (kind_source says so); `verdict` is the first verdict line as written; `exported` = a
results/<id>.json exists for it.

Usage: python build_catalogue.py [--out FILE]
"""
import argparse
import csv
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))  # repo root
RESULTS = os.path.join(HERE, "results")
TRADE_WORDS = re.compile(r"\bnet R\b|\bfees?\b|\btrades?\b|\bfilled\b|\bwin rate\b|\bPF\b|\bmean\b", re.I)
AUDIT_WORDS = re.compile(r"audit|review|inventory|reconcile|provenance|parity|check", re.I)
STUDY_FILE = re.compile(r"(^|/)(RESULTS?|VERDICT|[A-Z0-9_]*_RESULTS?)[^/]*\.md$", re.I)
# result file -> exported test id (a test appears "exported" when results/<id>.json exists)
EXPORTED_BY_SOURCE = {
    "MyTradingSys/research/levels_confluence_2026-10-14": "levels_ladder",
    "MyTradingSys/research/dsa_backtest_audit_2026-10-16/T09_live_parity.md": "t09_live_parity",
    "MyTradingSys/research/dsa_backtest_audit_2026-10-16/T06_cost_fill_realism.md": "t06_cost_fill",
    "MyTradingSys/research/dsa_backtest_audit_2026-10-16/T07_stale_verdicts.md": "t07_stale_verdicts",
    "MyTradingSys/research/wavetrend_2026-10-17/RESULT.md": "wavetrend_atlas",
}


def tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "MyTradingSys"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def read(p):
    try:
        with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def clean(s, n=240):
    s = re.sub(r"[*`#|]+", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def title_of(text, fallback):
    for ln in text.splitlines():
        if ln.startswith("#"):
            return clean(ln.lstrip("# "), 120)
    return fallback


def verdict_of(text):
    for ln in text.splitlines():
        if re.search(r"verdict", ln, re.I) and len(ln.strip()) > 12:
            return clean(re.sub(r"^.*?verdict[:\s*-]*", "", ln, flags=re.I) or ln)
    body = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    return clean(body[0]) if body else "no verdict line"


def kind_of(path, text, verdict):
    if AUDIT_WORDS.search(path):
        return "audit"
    if TRADE_WORDS.search(text[:6000]) or TRADE_WORDS.search(verdict):
        return "backtest"
    return "thought_experiment"


def family_of(path):
    parts = path.split("/")
    if "research" in parts:
        d = parts[parts.index("research") + 1]
        return re.sub(r"[_-]?20\d\d-\d\d(-\d\d)?$", "", d).replace("_", " ") or d
    return parts[1] if len(parts) > 1 else "other"


def tag(row):
    row["tag"] = (row["verdict"] + " " + row["title"]).lower()
    fl = "failed" if re.search(r"\bfail|no edge|negative|does not pay|inconclusive|nothing survives|no anchor|closed", row["tag"]) else "other"
    row["status"] = "FAILED" if fl == "failed" else "SEE_VERDICT"
    del row["tag"]
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=RESULTS, help="folder holding the results/*.json files (default: the committed one)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    results = a.results
    a.out = a.out or os.path.join(results, "_catalogue.json")
    files = tracked()
    fset = set(files)
    have = {f[:-5] for f in os.listdir(results) if f.endswith(".json") and not f.startswith("_")}
    rows, seen = [], set()

    def add(id_, family, title, kind, kind_source, verdict, source, extra=None):
        if source in seen:
            return
        seen.add(source)
        exp = EXPORTED_BY_SOURCE.get(source)
        r = {"id": id_, "family": family, "title": title, "kind": kind, "kind_source": kind_source, "verdict": verdict,
             "source": source, "exported": bool(exp and exp in have), "result_id": exp if exp and exp in have else None}
        if extra:
            r.update(extra)
        rows.append(tag(r))

    # 1. exported first: make sure their source is claimed
    for src, rid in EXPORTED_BY_SOURCE.items():
        p = os.path.join(results, rid + ".json")
        if os.path.isfile(p):
            d = json.load(open(p, encoding="utf-8"))
            add(rid, d["family"], d["title"], d.get("kind", "backtest"), "result file", d["verdict"]["label"], src)
    # 2. layer_map.json backtests (hand-kept, one row per backtest/study)
    lm = json.loads(read("MyTradingSys/system/layer_map.json") or "{}")
    for b in lm.get("backtests", []):
        src = b.get("report") or "MyTradingSys/system/layer_map.json#" + b["id"]
        txt = read(src) if src in fset else ""
        fam = (b.get("layers") or ["other"])[0].replace("_", " ")
        add("lm-" + b["id"].lower(), fam, clean(b["title"], 120), kind_of(src, txt + (b.get("effects") or ""), b.get("verdict") or ""),
            "inferred from text", clean(b.get("verdict") or "no verdict"), src, {"date": b.get("date"), "window": b.get("market")})
    # 3. study result notes
    for p in files:
        if p.startswith("MyTradingSys/research/") and STUDY_FILE.search(p) and p.endswith(".md") and "/dsa_backtest_audit" not in p:
            t = read(p)
            v = verdict_of(t)
            add("st-" + re.sub(r"\W+", "-", p[len("MyTradingSys/research/"):-3]).strip("-").lower(), family_of(p),
                title_of(t, os.path.basename(p)), kind_of(p, t, v), "inferred from text", v, p)
    # 4. DSA audit notes T01..T10
    for p in files:
        m = re.search(r"dsa_backtest_audit_2026-10-16/(T\d\d_[^/]+)\.md$", p)
        if m:
            t = read(p)
            add("audit-" + m.group(1).lower(), "Audit: DSA backtest audit", title_of(t, m.group(1)), "audit", "path", verdict_of(t), p)
    # 5. trials ledgers (one row each; counts rows)
    for p in files:
        if re.search(r"(^|/)(trials\.csv|TRIALS\.md)$", p):
            t = read(p)
            n = max(0, (len(list(csv.reader(t.splitlines()))) - 1)) if p.endswith(".csv") else sum(1 for l in t.splitlines() if l.startswith("|")) - 2
            add("ledger-" + re.sub(r"\W+", "-", p[len("MyTradingSys/research/"):]).strip("-").lower(), "Trial ledgers", "Trial ledger: " + family_of(p),
                "backtest", "path", "%d trial rows logged (every variant tried)" % max(n, 0), p)
    # 6. study folders with no row yet: one row each, best summary note (kind and verdict inferred, flagged)
    by_dir = {}
    for p in files:
        m = re.match(r"MyTradingSys/research/([^/]+)/(.+)$", p)
        if m and p.endswith(".md") and re.search(r"20\d\d-\d\d|_bt|backtest|audit|study|screen", m.group(1), re.I):
            by_dir.setdefault(m.group(1), []).append(p)
    covered = {r["source"].split("/")[2] for r in rows if r["source"].startswith("MyTradingSys/research/")}
    pref = re.compile(r"(REPORT|SUMMARY|VERDICT|RESULT|README|FINDINGS|ATLAS)", re.I)
    for d, ps in sorted(by_dir.items()):
        if d in covered or d.startswith(("sim_desk", "thinker", "mts_doctor", "layer_lab")):
            continue
        best = sorted(ps, key=lambda q: (not pref.search(os.path.basename(q)), q.count("/"), -len(read(q))))[0]
        t = read(best)
        v = verdict_of(t)
        add("dir-" + re.sub(r"\W+", "-", d).strip("-").lower(), family_of(best), title_of(t, d), kind_of(best, t, v), "inferred from text", v, best,
            {"folder_files": len(ps)})
    # 7. runs saved by the local desk (results/desk-*.json): one row each, so a saved run is never uncatalogued
    for rid in sorted(h for h in have if h.startswith("desk-")):
        d = json.load(open(os.path.join(results, rid + ".json"), encoding="utf-8"))
        add(rid, d.get("family", "Desk runs"), d.get("title", rid), d.get("kind", "backtest"), "result file", d["verdict"]["label"],
            "MyTradingSys/research/sim_desk/results/" + rid + ".json", {"exported": True, "result_id": rid})
    rows.sort(key=lambda r: (not r["exported"], r["family"].lower(), r["title"].lower()))
    doc = {"_doc": "Catalogue of known tests on trunk. kind is inferred (kind_source). Built by sim_desk/build_catalogue.py.",
           "count": len(rows), "exported": sum(1 for r in rows if r["exported"]), "rows": rows}
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=0, ensure_ascii=False)
        f.write("\n")
    return a.out, doc


if __name__ == "__main__":
    o, d = main()
    print(o, d["count"], d["exported"])
