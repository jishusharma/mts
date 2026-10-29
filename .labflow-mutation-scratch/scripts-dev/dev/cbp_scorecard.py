#!/usr/bin/env python
"""Per-analyst recount of the CBP store (read-only, public aggregate counts only).

  python scripts/dev/cbp_scorecard.py [--store PATH]          # default: cbp.store_path()
  git -C F:/CryptoScrapper show <commit>:cbp_store/rows.json > snap.json; ... --store snap.json

Prints one line per analyst: rows, trades, rows with a tradable call (cbp.is_tradable). Analyst names are the store's
own short names; Michael (@MichaelPizzino) and Michaal (@michaelvdpoppe) are two different analysts, never merged.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "MyTradingSys"))
import cbp  # noqa: E402


def recount(data):
    out = {}
    for r in data.get("rows", []):
        c = out.setdefault(r.get("analyst", "UNKNOWN"), {"rows": 0, "trades": 0, "tradable_rows": 0})
        c["rows"] += 1
        c["trades"] += len(r.get("trades") or [])
        c["tradable_rows"] += 1 if cbp.is_tradable(r) else 0
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--store")
    a = ap.parse_args(argv)
    data = cbp.load(a.store)
    for name, c in sorted(recount(data).items()):
        print("%s: rows %d, trades %d, tradable rows %d" % (name, c["rows"], c["trades"], c["tradable_rows"]))
    print("total rows %d, rejected %d" % (len(data["rows"]), len(data["rejected"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
