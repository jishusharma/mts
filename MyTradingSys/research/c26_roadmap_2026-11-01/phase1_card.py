"""Simulator result card for the Phase 1 design looks (sim_desk/DESIGN.md "Result files").

A look script called with `--card <sim_desk/results/<id>.json>` writes its tables as one card so the operator can check
the same numbers on the simulator page (operator 2026-11-01: every test he is shown must be on the simulator).
Percent, bars and timestamps only: columns that hold prices are dropped from every table (the repo is public).
"""
import json
import sys

SRC = "MyTradingSys/research/c26_roadmap_2026-11-01/"
FAM = "Eagle_Eyes chart ideas (operator, 10-30/31)"
WIN = ("RECENT design window 2026-06-21 .. 2026-11-01 (SEEN: looked at here, nothing here is evidence; "
       "DEV scores come from phase3_dev.py, card c26-h1-structural-lower-high)")
FEE = {"name": "Costs", "value_plain": "0.10 % per round trip (Binance taker x2, backtest/fees.py); slippage and funding not modelled",
       "label": "SOURCED"}
NO_PRICE = ("H1", "short band above", "long band below entry")


def arg(name):
    """Value of `--name value` after <repo> <cache> on the command line (None when absent)."""
    return dict(zip(sys.argv[3::2], sys.argv[4::2])).get(name)


def P(name, value, label="OURS"):
    return {"name": name, "value_plain": value, "label": label}


def table(title, cols, rows, caption=""):
    keep = [i for i, c in enumerate(cols) if c not in NO_PRICE]
    return {"kind": "table", "title": title, "caption": caption, "cols": [cols[i] for i in keep],
            "rows": [[r[i] for i in keep] for r in rows]}


def card(id_, title, what, how, verdict, tone, why, kpis, examples, files, date="2026-11-01"):
    return {"id": id_, "kind": "backtest", "family": FAM, "provenance": "run", "title": title, "date": date, "what": what,
            "how": how, "window": WIN, "verdict": {"label": verdict, "tone": tone}, "why": why, "kpis": kpis,
            "examples": examples, "evidence": [SRC + "PHASE1_RANGE.md"], "missing": [],
            "source_files": [SRC + f for f in files], "commit": "see git log"}


def write(path, d):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
        f.write("\n")
