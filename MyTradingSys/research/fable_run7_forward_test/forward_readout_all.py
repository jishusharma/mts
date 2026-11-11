"""One combined forward readout: exactly four rows (Krown S8, Malkan, T06L, C30), each with trades, net R, E+/E-, state.

Defaults (repo-relative): ledger MyTradingSys/execution/trade_ledger.jsonl; paper journals runtime_data/
malkan_level_short_forward.jsonl, t06_rsi_ma_cross_forward.jsonl, c30_h2_forward.jsonl. A missing file never
crashes: its slot prints "n 0, no data yet". State: slot rule (E-/E+/Krown FAIL) or, per EDGE_PLAN (c),
KILL at >= 30 trades with net R per trade <= 0, or a journal kill row; else RUNNING.
T06L = the long rows of the T06 journal; short rows are reported on their own line, never scored.
Run: python MyTradingSys/research/fable_run7_forward_test/forward_readout_all.py [--ledger P] [--malkan P] [--t06 P] [--c30 P] [--asof D]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forward_readout as fr  # noqa: E402

ROOT = fr.ROOT
LEDGER = ROOT / "MyTradingSys/execution/trade_ledger.jsonl"
MALKAN = ROOT / "runtime_data/malkan_level_short_forward.jsonl"
T06 = ROOT / "runtime_data/t06_rsi_ma_cross_forward.jsonl"
C30 = ROOT / "runtime_data/c30_h2_forward.jsonl"
ROWS = [("krown_s8", "Krown S8", "testnet"), ("malkan_level_short", "Malkan", "paper"),
        ("t06_rsi_ma", "T06L", "paper"), ("c30_h2_long", "C30", "paper")]
STOP_N = 30


def _exists(p):
    return str(p) if p and Path(p).is_file() else None


def combined(ledger=LEDGER, malkan=MALKAN, t06=T06, c30=C30, asof=None):
    pairs = ((_exists(malkan), "malkan_level_short"), (_exists(t06), "t06_rsi_ma"), (_exists(c30), "c30_h2_long"))
    paper = [(p, k) for p, k in pairs if p]
    res = fr.readout(_exists(ledger), asof, paper)
    by = {s["slot"]: s for s in res["slots"]}
    killed = {k["slot"] for k in res["kills"]}
    out = []
    for key, name, mode in ROWS:
        s = by[key]
        if s["n"] == 0:
            state = "n 0, no data yet"
        elif s["state"] != "RUNNING":
            state = s["state"]
        elif s["n"] >= STOP_N and s["mean_r"] <= 0:
            state = "KILL"
        elif key in killed:
            state = "KILL (journal row)"
        else:
            state = "RUNNING"
        out.append({"name": name, "mode": mode, "n": s["n"], "mean_r": s["mean_r"],
                    "e_plus": s["e_plus"], "e_minus": s["e_minus"], "state": state})
    return {"rows": out, "res": res}


def render(c):
    f = fr._f
    L = ["| Slot | Mode | Trades | Net R | E+ | E- | State |", "|---|---|---|---|---|---|---|"]
    for r in c["rows"]:
        e = r["n"] > 0
        L.append(f"| {r['name']} | {r['mode']} | {r['n']} | {f(r['mean_r'], 3) if e else '-'} | "
                 f"{f(r['e_plus']) if e else '-'} | {f(r['e_minus']) if e else '-'} | {r['state']} |")
    res = c["res"]
    sh = res["t06_short"]
    L += ["", f"T06 short (reported, not a lead): n {sh['n']}, mean R "
              f"{f(sh['mean_r'], 3) if sh['n'] else '-'}, unscored.",
          "Net R = mean fee-net R per trade. KILL: E- >= 10 after 10 obs, or 30 trades with net R <= 0, "
          "or a journal kill row (EDGE_PLAN c)."]
    if res["t06_no_side"]:
        L.append(f"T06 side field missing on {res['t06_no_side']} outcome rows (counted as long).")
    for k in res["kills"]:
        L.append("Kill row: " + ", ".join(f"{a}={b}" for a, b in sorted(k.items())))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--malkan", default=str(MALKAN))
    ap.add_argument("--t06", default=str(T06))
    ap.add_argument("--c30", default=str(C30))
    ap.add_argument("--asof")
    a = ap.parse_args(argv)
    sys.stdout.write(render(combined(a.ledger, a.malkan, a.t06, a.c30, a.asof)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
