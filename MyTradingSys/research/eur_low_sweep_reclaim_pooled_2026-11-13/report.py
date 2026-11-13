"""Build REPORT.md from results.json (written by study.py --run). Verdict rule exactly as PRE_REG.md."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S

res = json.load(open(os.path.join(HERE, "results.json")))
get = lambda cell, sp: res.get(str(cell) + "|" + sp, {"n": 0})

# regime mix over event days (BTC prior-day close vs SMA20, +-2 %)
t0, o, h, l, c = S.load("BTCUSDT")
dc = {}
for d in range(len(c) // 288):
    v = c[d * 288:(d + 1) * 288]
    v = v[~np.isnan(v)]
    if len(v):
        dc[d] = v[-1]
from datetime import datetime, timezone
reg = {}
for d in sorted(dc):
    prior = [dc.get(d - k) for k in range(1, 21)]
    if d < 20 or any(p is None for p in prior):
        continue
    x = prior[0] / (sum(prior) / 20) - 1
    reg[datetime.fromtimestamp((t0 + d * S.DAY) / 1000, timezone.utc).strftime("%Y-%m-%d")] = "up" if x > 0.02 else "down" if x < -0.02 else "range"
ev_days = set()
for sym in S.SYMS:
    _, evs = S.events_for(sym)
    ev_days |= {e["date"] for e in evs}
vals = [reg[d] for d in ev_days if d in reg]
mix = {k: 100 * vals.count(k) / len(vals) for k in ("up", "down", "range")}

cells = S.CELLS
p = [get(c_, "VAL").get("p", 1.0) if get(c_, "VAL")["n"] else 1.0 for c_ in cells]
rej = S.bh(p, 0.10)
passes, rows = [], []
for i, cell in enumerate(cells):
    v = get(cell, "VAL")
    ok = bool(v["n"] >= 30 and v["mean"] > 0 and v["lo"] > 0 and v["beats"] and i in rej)
    if ok:
        passes.append(cell)
    cell_name = "%s %s %s" % cell
    def f(sp):
        x = get(cell, sp)
        return "n/a" if not x["n"] else "%d / %+.3f [%+.3f, %+.3f]" % (x["n"], x["mean"], x["lo"], x["hi"])
    vv = get(cell, "VAL")
    plc = "n/a" if not vv["n"] else "%+.3f (p95 %+.3f) %s" % (vv["pl_mean"], vv["pl_p95"], "beats" if vv["beats"] else "no")
    rows.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (cell_name, f("DEV"), f("VAL"), f("RECENT"),
                "n/a" if not vv["n"] else "%.1f %%" % (100 * vv["hit"]), plc,
                "n/a" if not vv["n"] else "%.3f" % vv["p"], "BH-reject" if i in rej else "no"))
    rows[-1] += " **PASS-GATE-BLOCKED** |" if ok else " FAIL |" if vv["n"] >= 30 else " UNDERPOWERED |"
minn = max(get(c_, "VAL")["n"] for c_ in cells)
verdict = ("PASS-GATE-BLOCKED (%s)" % "; ".join("%s %s %s" % c_ for c_ in passes)) if passes else (
    "UNDERPOWERED" if minn < 30 else "FAIL, cannot see an effect below ~0.25 R")
best = max((c_ for c_ in cells if get(c_, "VAL")["n"]), key=lambda c_: get(c_, "VAL")["mean"])
bv = get(best, "VAL")
L = ["# EUR-low sweep -> reclaim -> long (mirror short), pooled BTC + ETH + SOL, Bybit 5m linear (2026-11-13)", "",
     "Rule, data, split, fees, placebo, inference and verdict vocabulary as frozen in PRE_REG.md (committed before any outcome). No parameter was searched.",
     "", "**VERDICT: %s**" % verdict, "",
     "- Best VALIDATION cell by mean (descriptive, not selected): %s, n %d, fee-net mean R %+.3f [%+.3f, %+.3f], placebo %+.3f (p95 %+.3f)." % (
         "%s %s %s" % best, bv["n"], bv["mean"], bv["lo"], bv["hi"], bv["pl_mean"], bv["pl_p95"]),
     "- Power: gate BLOCK recorded in PRE_REG.md (MDE ~0.25 R on VALIDATION before fees); a FAIL does not exclude a smaller edge.",
     "- Fees: taker 5 bp/side; maker cell = 2 bp entry + 5 bp exit (fees.py); no funding, no slippage (optimistic).",
     "- Regime mix: up %.1f %% / down %.1f %% / range %.1f %% (event days, BTC prior close vs SMA20 +-2 %%, rule in PRE_REG)." % (mix["up"], mix["down"], mix["range"]),
     "", "## Cells (n / fee-net mean R [95 % day-cluster bootstrap CI]); placebo and BH on VALIDATION", "",
     "| cell (side exit entry) | DEV | VALIDATION | RECENT | VAL hit | VAL placebo mean R | VAL p (1-sided) | BH 10 % | verdict |",
     "|---|---|---|---|---|---|---|---|---|"] + rows
L += ["", "## Per coin, VALIDATION (n, mean R)", "", "| cell | BTC | ETH | SOL |", "|---|---|---|---|"]
for cell in cells:
    cs = []
    for s in S.SYMS:
        x = get(cell, "VAL:" + s)
        cs.append("n/a" if not x["n"] else "%d, %+.3f" % (x["n"], x["mean"]))
    L.append("| %s %s %s | %s |" % (cell + (" | ".join(cs),)))
open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(L) + "\n")
print(verdict)
