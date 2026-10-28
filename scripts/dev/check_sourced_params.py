"""Guard: no layer param ships without a label (SOURCED | OURS | OPERATOR-HYPOTHESIS), and no SOURCED param without a locator.

Reads MyTradingSys/backtest/layers/{rsi,krown,kurisko}/params/*.json (CLAUDE.md Numbers rule; MOVED_RULES.md).
Two shapes: "krown" {params: {name: {value,label,source[,quote]}}} and "flat" (rsi: file-level source, *_quote keys).
Problems (a problem is "file::param::kind"):
  no-label        a krown-shape param without a valid label
  no-source       a param (or flat file) without a non-empty source
  sourced-no-quote  SOURCED with neither a `quote` nor a locator in source (rule id KR-/TOP-, R<n>/S<n>, KURISKO_SPEC, *.md)
  unknown-rule    a KR-xxx id absent from research/krown_ta101_2026-10-13/KROWN_RULES.csv
  not-in-ledger   an extract_<video id>.md absent from research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv
Known gaps live in ALLOWLIST with owner and expiry; an expired or stale (no longer firing) entry fails too.
Exit 0 = clean (after allowlist). Run: python scripts/dev/check_sourced_params.py [--root DIR]
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAYERS = ("rsi", "krown", "kurisko")
LABELS = {"SOURCED", "OURS", "OPERATOR-HYPOTHESIS"}
LOCATOR = re.compile(r"\b(KR-[A-Z]\d+|TOP-\d+|R\d+|S\d+|KURISKO_SPEC)\b|\.md\b")
RULE_ID = re.compile(r"\bKR-[A-Z]\d+\b")
EXTRACT = re.compile(r"extract_([A-Za-z0-9_-]{11})\.md")

# (file basename, param or "*" for the file, kind) -> (owner, expiry YYYY-MM-DD). Filled from the first real-tree run.
ALLOWLIST = {}


def load_ledger(root):
    p = root / "MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv"
    if not p.exists():
        return None
    with open(p, encoding="utf8", newline="") as f:
        return {r["video_id"] for r in csv.DictReader(f)}


def load_rules(root):
    p = root / "MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv"
    if not p.exists():
        return None
    with open(p, encoding="utf8", newline="") as f:
        return {r["rule_id"] for r in csv.DictReader(f)}


def _cite_problems(text, ledger, rules):
    out = []
    for m in EXTRACT.finditer(text):
        if ledger is not None and m.group(1) not in ledger:
            out.append("not-in-ledger")
    for m in RULE_ID.finditer(text):
        if rules is not None and m.group(0) not in rules:
            out.append("unknown-rule")
    return out


def check_file(path, ledger, rules):
    """Return a list of (param, kind) problems for one params JSON."""
    d = json.loads(Path(path).read_text(encoding="utf8"))
    out = []
    if isinstance(d.get("params"), dict):
        for name, v in d["params"].items():
            if not isinstance(v, dict) or v.get("label") not in LABELS:
                out.append((name, "no-label"))
                continue
            src = str(v.get("source") or "")
            if not src.strip():
                out.append((name, "no-source"))
                continue
            if v["label"] == "SOURCED":
                if not v.get("quote") and not LOCATOR.search(src):
                    out.append((name, "sourced-no-quote"))
                out += [(name, k) for k in _cite_problems(src + " " + str(v.get("quote") or ""), ledger, rules)]
        return out
    src = str(d.get("source") or "")
    if not src.strip():
        return [("*", "no-source")]
    if src.strip().lower() == "operator":   # operator-chosen defaults = OURS
        return out
    if not LOCATOR.search(src + " " + str(d.get("note") or "")) and not any(k.endswith("_quote") for k in d):
        out.append(("*", "sourced-no-quote"))
    out += [("*", k) for k in _cite_problems(src, ledger, rules)]
    return out


def scan(root):
    root = Path(root)
    ledger, rules = load_ledger(root), load_rules(root)
    res, n = [], 0
    for layer in LAYERS:
        for f in sorted((root / "MyTradingSys/backtest/layers" / layer / "params").glob("*.json")):
            d = json.loads(f.read_text(encoding="utf8"))
            n += len(d["params"]) if isinstance(d.get("params"), dict) else 1
            res += [(f.name, p, k) for p, k in check_file(f, ledger, rules)]
    return n, res


def evaluate(n, res, today=None):
    """-> (failures, allowlisted count). Expired and stale allowlist entries are failures."""
    today = (today or date.today()).isoformat()
    fails, allowed, seen = [], 0, set()
    for item in res:
        if item in ALLOWLIST:
            seen.add(item)
            if ALLOWLIST[item][1] < today:
                fails.append(f"EXPIRED allowlist {item} (owner {ALLOWLIST[item][0]}, expiry {ALLOWLIST[item][1]})")
            else:
                allowed += 1
        else:
            fails.append("%s::%s::%s" % item)
    fails += [f"STALE allowlist {k} no longer fires: remove it" for k in ALLOWLIST if k not in seen]
    return fails, allowed


def main(argv):
    root = REPO
    if "--root" in argv:
        root = Path(argv[argv.index("--root") + 1])
    n, res = scan(root)
    if "--list" in argv:
        for r in res:
            print(r)
    fails, allowed = evaluate(n, res)
    print(f"check_sourced_params: {n} params checked, {allowed} allowlisted, {len(fails)} failing")
    for f in fails:
        print("FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
