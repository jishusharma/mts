"""rulebook_check.py: every folder under MyTradingSys/backtest/layers has a row in the indicator rule book INDEX.

  python scripts/dev/rulebook_check.py [--root <repo>]    # exit 1 and list the folders with no `layer:<folder>` token

INDEX = MyTradingSys/research/indicator_rulebooks/INDEX.md. A layer folder is any directory under backtest/layers
that holds at least one file and whose name does not start with `_` or `.` (fixtures, caches). A row covers a folder
when its "Layers" column holds the token `layer:<folder>`. Operator order 2026-11-13 (OPERATOR_DECISIONS.md).
"""
import argparse
import re
import sys
from pathlib import Path

LAYERS = "MyTradingSys/backtest/layers"
INDEX = "MyTradingSys/research/indicator_rulebooks/INDEX.md"
SKIP_DIRS = {"__pycache__", "fixtures", "params"}


def layer_folders(root):
    base = Path(root) / LAYERS
    out = []
    for d in sorted(base.iterdir()) if base.is_dir() else []:
        if not d.is_dir() or d.name.startswith((".", "_")) or d.name in SKIP_DIRS:
            continue
        if any(p.is_file() for p in d.rglob("*") if "__pycache__" not in p.parts):
            out.append(d.name)
    return out


def indexed(root):
    p = Path(root) / INDEX
    text = p.read_text(encoding="utf-8") if p.is_file() else ""
    return set(re.findall(r"`layer:([A-Za-z0-9_]+)`", text))


def missing(root):
    have = indexed(root)
    return [f for f in layer_folders(root) if f not in have]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    a = ap.parse_args(argv)
    miss = missing(a.root)
    if miss:
        print("rulebook_check FAIL: no INDEX row (layer:<folder> token) for: " + ", ".join(miss))
        print(f"fix: add a row to {INDEX} (template: MyTradingSys/research/indicator_rulebooks/TEMPLATE.md)")
        return 1
    print(f"rulebook_check OK: {len(layer_folders(a.root))} layer folders, all in INDEX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
