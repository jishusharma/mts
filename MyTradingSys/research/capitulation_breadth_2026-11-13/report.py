"""Render RESULT.md from results.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
pc = lambda x: "-" if x is None else "%+.1f%%" % (100 * x)
cells, ev, td = R["cells"], R["events"], R["today"]
L = []
npass = sum(c["verdict"] == "PASS" for c in cells)
L.append("# RESULT: capitulation breadth event study (edge6-capitulation-breadth-1113)\n")
L.append("**Verdict: %s. %d of 12 cells pass; no cell has a VALIDATION CI above zero or survives BH 10 %%. The market-wide event is not a tradable long signal in this data.**\n" % ("FAIL" if npass == 0 else "PASS (%d)" % npass, npass))
L.append("Regime mix: BTC daily close vs 200d SMA, 2021-01-01..2026-11: bull 49 %% / bear 38 %% / range 13 %%; 2024-01-01..now: bull 56 %% / bear 29 %% / range 15 %%. Data: %s .. %s UTC, %d closed 4h bars, 60 coins (PRE_REG.md), Binance public spot klines. Events: T=30 %%: %d, T=50 %%: %d.\n" % (R["first"], R["last"], R["n_bars"], R["n_events"]["0.3"], R["n_events"]["0.5"]))
L.append("Note: the first T=30 event (2020-12-24) sits in the warm-up where only a few coins have an RSI; kept for completeness (DEV).\n")
L.append("Survivorship limit: only coins still trading in Nov 2026 are in the universe, so every number is an upper bound (see PRE_REG.md).\n")
L.append("## Today (2026-11-13)\n")
L.append("Last closed bar %s: B = %.1f %% (%d of 60 coins defined), lowest B in the last 5 days %.1f %%, highest %.1f %%. No event fired in the last 7 days for either threshold. **2026-11-13 did NOT qualify**: B is near zero, the quiet state, not a washout (B at 1.7 %% is above only %.0f %% of all bars, i.e. it is ordinary; record B = %.0f %%). Last 12 bars of B: %s.\n" %
         (td["last_bar"], 100 * td["B_last"], td["n_defined"], 100 * td["B_min_5d"], 100 * td["B_max_5d"], 100 * td["B_hist_pct"], 100 * td["B_max_ever"], td["B_tail"]))
L.append("## Event table (main deliverable)\n")
L.append("Returns are GROSS, from the entry close (or from the event-bar close when no confirm); top10 = equal-weight top-10 by 30-day volume; 2d = 12 bars, 7d = 42 bars; MAE = lowest 4h low within 7 days of the entry vs entry (BTC, top10 mean of coins); DD = BTC close vs its prior 30-day high. `-` = 7 days not yet elapsed.\n")
L.append("| T | event bar (UTC) | split | B | BTC DD 30d | entry | BTC 2d | BTC 7d | top10 2d | top10 7d | MAE BTC | MAE top10 |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
for e in ev:
    L.append("| %d%% | %s | %s | %.0f%% | %s | %s | %s | %s | %s | %s | %s | %s |" % (round(100 * e["T"]), e["date"], e["split"], 100 * e["B"], pc(e["dd"]), e["entry"],
             pc(e["btc2"]), pc(e["btc7"]), pc(e["top2"]), pc(e["top7"]), pc(e["mae_btc"]), pc(e["mae_top"])))
L.append("")
for T in (0.30, 0.50):
    sel = [e for e in ev if e["T"] == T and e["tr"] and e["complete"]]
    if sel:
        import numpy as np
        L.append("T=%d%% (events with confirm and 7d elapsed, n=%d): mean gross 7d BTC %s, top10 %s; worst 7d top10 %s (%s); worst MAE top10 %s." % (round(100 * T), len(sel),
                 pc(np.mean([e["btc7"] for e in sel])), pc(np.mean([e["top7"] for e in sel])), pc(min(e["top7"] for e in sel)),
                 min(sel, key=lambda e: e["top7"])["date"], pc(min(e["mae_top"] for e in sel))))
L.append("")
L.append("## Cell table (VALIDATION = events from 2024-01-01; return = fee-net per event, 12 bp round trip per coin)\n")
L.append("| cell | events DEV (trades) | events VAL (trades) | mean % per event VAL | 95% CI | win% | placebo a p | placebo b diff | worst event | BH | verdict |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
for c in cells:
    nm = "T%d %s %s" % (round(100 * c["T"]), c["basket"], c["exit"])
    if "mean_val" in c:
        L.append("| %s | %d (%d) | %d (%d) | %s | [%s, %s] | %.0f%% | %.3f | %s | %s (%s) | %s | %s |" % (nm, c["n_events_dev"], c["n_dev"], c["n_events_val"], c["n_val"], pc(c["mean_val"]),
                 pc(c["ci"][0]), pc(c["ci"][1]), 100 * c["win"], c["plac_a_p"], pc(c.get("plac_b_diff")), pc(c["worst"]), c["worst_date"][:10], "yes" if c["bh"] else "no", c["verdict"]))
    else:
        L.append("| %s | %d (%d) | %d (%d) | - | - | - | - | - | - | no | %s |" % (nm, c["n_events_dev"], c["n_dev"], c["n_events_val"], c["n_val"], c["verdict"]))
L.append("")
L.append("DEV fee-net mean per event: " + "; ".join("T%d %s %s %s" % (round(100 * c["T"]), c["basket"], c["exit"], pc(c["dev_mean"])) for c in cells) + ".\n")
L.append("Placebo b diff = mean(confirm entry) - mean(event-bar entry) over the same events: the confirm adds nothing reliable where the diff is near zero or negative. Placebo a p = share of 1000 same-year random-entry draws with a mean at least the real one.\n")
json_note = "Code: fetch.py, universe.py, breadth_lib.py (tested by test_breadth.py), study.py, report.py; numbers in results.json."
L.append(json_note)
open(os.path.join(HERE, "RESULT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
