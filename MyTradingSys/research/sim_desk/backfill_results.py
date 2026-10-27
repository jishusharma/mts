"""Backfill sim_desk/results/<id>.json for every catalogued test that has a source note on trunk.

SOURCE-EXTRACTED: every number below is copied from the text of the committed source file (nothing is re-run,
nothing is invented). Where the source does not state a field the file says null plus a short reason in `missing`.
Each extracted number keeps the line it came from in `evidence` so it can be checked. Rows already exported by
export_results.py or the desk (provenance != "source-extracted") are never overwritten.

Usage: python backfill_results.py [--results DIR] [--dry]
Then:  python build_catalogue.py ; python artifact/build_artifact.py
"""
import argparse
import json
import os
import re
import subprocess

import build_catalogue as bc

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
PROV = "source-extracted"
MAXTXT = 20000

RE_TRADES = [re.compile(r"(?<![\d.])(\d[\d,]*)\s+(?:filled\s+|total\s+|DEV\s+|OOS\s+)?trades\b", re.I),
             re.compile(r"\btrades?\s*(?:=|:)\s*(\d[\d,]*)\b", re.I),
             re.compile(r"\bn\s*=\s*(\d[\d,]*)\b")]
RE_NETR = [re.compile(r"net\s*R[^\n\d+\-]{0,40}([+\-]?\d+\.\d+)", re.I),
           re.compile(r"(?:mean|avg|average)[^\n\d+\-]{0,30}([+\-]?\d+\.\d+)\s*R\b", re.I),
           re.compile(r"([+\-]\d+\.\d+)\s*R\s+(?:net|after fees|per trade)", re.I)]
RE_RANGE = re.compile(r"(20\d\d-\d\d-\d\d)\s*(?:\.\.|…|to|–|—|-|→)\s*(20\d\d-\d\d-\d\d)")
RE_FAIL = re.compile(r"\bfail|no edge|negative|does not|did not|not pass|nothing survives|insufficient|inconclusive|"
                     r"fees? (?:eat|kill)|not significant|no anchor|0 of \d+", re.I)
RE_PARAM_HEAD = re.compile(r"^#+\s*.*(rule|param|setting|design|setup|method|frozen|what was|spec|approach)", re.I)


def line_of(text, m):
    a = text.rfind("\n", 0, m.start()) + 1
    b = text.find("\n", m.end())
    return bc.clean(text[a: b if b >= 0 else len(text)], 200)


def first_match(text, pats):
    best = None
    for p in pats:
        m = p.search(text)
        if m and (best is None or m.start() < best[0].start()):
            best = (m, p)
    return best


def params_of(text):
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if RE_PARAM_HEAD.match(ln):
            out = []
            for l in lines[i + 1: i + 40]:
                if l.startswith("#"):
                    break
                t = bc.clean(re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", l), 220)
                if len(t) > 12 and not l.strip().startswith("|---"):
                    out.append(t)
                if len(out) == 6:
                    break
            if out:
                return out
    return []


def tone_of(row):
    t = (row["verdict"] + " " + row["title"]).lower()
    if row.get("status") == "FAILED":
        return "bad"
    if re.search(r"inconclusive|insufficient|unvalidated|not enough", t):
        return "warn"
    if re.search(r"\bpass|survives|adopt|confirmed", t) and not re.search(r"not pass|nothing survives", t):
        return "good"
    return "info"


def commit_of(src):
    try:
        out = subprocess.run(["git", "-C", bc.ROOT, "log", "-1", "--format=%h", "--", src.split("#")[0]],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def build(row):
    src = row["source"]
    text = bc.read(src.split("#")[0])[:MAXTXT] if src.split("#")[0] in FILES else ""
    missing, evidence, kpis = {}, [], []
    nosrc = "source note has no text on trunk (layer_map entry only)" if not text else None

    # trades
    m = first_match(text, RE_TRADES) if text else None
    if m:
        n = m[0].group(1).replace(",", "")
        lab = "sample size n (first in the source, may not be trades)" if m[1] is RE_TRADES[2] else "trades (first count in the source)"
        kpis.append({"label": lab, "value": n})
        evidence.append({"field": "n_trades", "value": int(n), "quote": line_of(text, m[0])})
    else:
        missing["n_trades"] = nosrc or "the source does not state a trade count"
    # net R
    m = first_match(text, RE_NETR) if text else None
    if m:
        v = m[0].group(1)
        kpis.append({"label": "net R after fees (first value in the source)", "value": v, "tone": "bad" if v.startswith("-") else None})
        evidence.append({"field": "net_r", "value": float(v), "quote": line_of(text, m[0])})
    else:
        missing["net_r"] = nosrc or "the source states no net-R figure (it reports another unit, e.g. percent per year, or no return)"
    # window
    wm = RE_RANGE.search(text) if text else None
    if wm:
        window = "%s to %s (as written in the source)" % (wm.group(1), wm.group(2))
    elif row.get("window"):
        window = str(row["window"]) + " (as written in layer_map)"
    else:
        window = None
        missing["window"] = nosrc or "the source states no test window"
    # parameters
    ps = params_of(text) if text else []
    if not ps:
        missing["parameters"] = nosrc or "no rule or parameter section found in the source"
    # why
    why = []
    if text:
        for ln in text.splitlines():
            t = ln.strip()
            if t.startswith(("#", "|")) or len(t) < 25:
                continue
            if RE_FAIL.search(t):
                why.append(bc.clean(re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", t), 260))
            if len(why) == 4:
                break
    why_val = why or None
    if not why:
        missing["why"] = nosrc or "no sentence in the source states why it passed or failed"
    if row["kind"] != "backtest":
        missing.setdefault("n_trades", "not a trade test (%s)" % row["kind"].replace("_", " "))
    ledger = re.match(r"(\d+) trial rows", row["verdict"])
    if ledger:
        kpis.insert(0, {"label": "trial rows logged", "value": ledger.group(1)})

    for k in kpis:
        if k.get("tone") is None:
            k.pop("tone", None)
    return {
        "id": row["id"], "kind": row["kind"], "family": row["family"].title() if row["family"].islower() else row["family"],
        "title": row["title"], "provenance": PROV, "date": row.get("date"),
        "what": [{"name": "Rule or setup, line %d from the source" % (i + 1), "value_plain": p, "label": "OURS"} for i, p in enumerate(ps)],
        "how": "Not re-run. Numbers and sentences below were copied from the committed source note; the verdict is the line as written there.",
        "window": window,
        "verdict": {"label": row["verdict"], "tone": tone_of(row)},
        "why": why_val if why_val else [],
        "kpis": kpis, "examples": [{"kind": "none", "title": "Examples", "caption": "no example trades exported: source-extracted, the source holds no trade list"}],
        "evidence": evidence, "missing": missing,
        "source_files": [src], "commit": commit_of(src),
    }


FILES = set()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=RESULTS)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    FILES.update(bc.tracked())
    _, cat = bc.main(["--results", a.results, "--out", os.path.join(a.results, "_catalogue.json")])
    made = nulls = skipped = 0
    for row in cat["rows"]:
        p = os.path.join(a.results, row["id"] + ".json")
        if os.path.isfile(p):
            try:
                if json.load(open(p, encoding="utf-8")).get("provenance") != PROV:
                    skipped += 1   # hand-made or desk file: leave alone
                    continue
            except ValueError:
                pass
        res = build(row)
        nulls += 1 if res["missing"] else 0
        made += 1
        if not a.dry:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                json.dump(res, f, indent=1, ensure_ascii=False)
                f.write("\n")
    if not a.dry:
        bc.main(["--results", a.results])   # exported flags now see the new files
    files = [f for f in os.listdir(a.results) if f.endswith(".json") and not f.startswith("_")]
    final = json.load(open(os.path.join(a.results, "_catalogue.json"), encoding="utf-8")) if not a.dry else cat
    print("catalogue rows %d | written %d | left alone %d | rows with a null field %d | result files %d | exported in catalogue %d"
          % (len(cat["rows"]), made, skipped, nulls, len(files), final["exported"]))
    return cat, made, nulls


if __name__ == "__main__":
    main()
