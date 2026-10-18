#!/usr/bin/env python3
"""research_kit_lint.py - which research/backtest scripts re-implement Holm / day-clustered SE instead of importing
MyTradingSys/backtest/research_kit.py? Report only (never a gate); always exits 0.

    python scripts/dev/research_kit_lint.py [--root <repo>] [--allow <tsv>] [--write-allow]

A script is listed when it defines a function named like holm / cluster_se / cluster_mean_se / diff_cluster /
day_cluster / clustered... and does not import research_kit. Scripts already known are in
scripts/dev/research_kit_lint_allow.tsv (path, functions, note); anything else prints under NEW, so a fresh copy is
visible. STALE lists allowlist rows that no longer offend (delete them). --write-allow rewrites the allowlist from the
current offenders (use once, or after deleting fixed rows by hand and re-running without it).
"""
import argparse
import re
import sys
from pathlib import Path

SCAN = ("MyTradingSys/research", "MyTradingSys/backtest")
KIT = "MyTradingSys/backtest/research_kit.py"
DEF = re.compile(r"^\s*def\s+(\w*holm\w*|\w*cluster\w*_se\w*|\w*cluster_(?:mean|diff)\w*|\w*diff_cluster\w*"
                 r"|\w*day_?clust\w*|\w*clustered\w*)\s*\(", re.M)
IMPORT = re.compile(r"^\s*(?:from\s+research_kit\b|import\s+research_kit\b|from\s+backtest\.research_kit\b"
                    r"|from\s+MyTradingSys\.backtest\.research_kit\b|from\s+\.?research_kit\b)", re.M)
DEFAULT_ALLOW = Path(__file__).resolve().parent / "research_kit_lint_allow.tsv"


def offenders(root):
    out = {}
    for base in SCAN:
        for p in sorted((root / base).rglob("*.py")) if (root / base).is_dir() else []:
            rel = p.relative_to(root).as_posix()
            if rel == KIT or p.name.startswith("test_") or "__pycache__" in rel:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            names = sorted(set(DEF.findall(text)))
            if names and not IMPORT.search(text):
                out[rel] = names
    return out


def read_allow(path):
    rows = {}
    try:
        for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines()):
            parts = line.split("\t")
            if i == 0 and parts[0] == "path" or not line.strip():
                continue
            rows[parts[0]] = parts[1] if len(parts) > 1 else ""
    except OSError:
        pass
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--allow", default=str(DEFAULT_ALLOW))
    ap.add_argument("--write-allow", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root)
    found = offenders(root)
    if a.write_allow:
        lines = ["path\tfunctions\tnote"] + ["%s\t%s\texisting offender, pre-lint" % (k, ",".join(v)) for k, v in found.items()]
        Path(a.allow).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("wrote %d rows to %s" % (len(found), a.allow))
        return 0
    allow = read_allow(a.allow)
    new = {k: v for k, v in found.items() if k not in allow}
    old = {k: v for k, v in found.items() if k in allow}
    stale = [k for k in allow if k not in found]
    print("research_kit_lint (report only): %d script(s) define their own holm / clustered-SE instead of importing %s"
          % (len(found), KIT))
    print("NEW (%d) - import research_kit instead, or add to the allowlist with a reason:" % len(new))
    for k, v in new.items():
        print("  %s  [%s]" % (k, ", ".join(v)))
    print("ALLOWED (%d) - known offenders in %s" % (len(old), Path(a.allow).name))
    for k, v in old.items():
        print("  %s  [%s]" % (k, ", ".join(v)))
    print("STALE allowlist rows (%d) - no longer offend, delete them:" % len(stale))
    for k in stale:
        print("  " + k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
