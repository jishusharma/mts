"""Rumers harness: power gate BEFORE any rule is frozen (Lab_Guy, 2026-11-01).

Costs come only from backtest/fees.py (all-taker Binance, regime "taker both legs"); research_kit.TAKER_RT_PCT (0.14 %,
fee + 2+2 bp slippage) is printed as the stress column. Win rate / RR pairs are OURS (plausible ranges, not Rumers claims):
the extract cards replace them with the video's claimed hit-rate and RR once the captions land.
Output: a markdown table on stdout (pasted into HARNESS.md).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.fees import BINANCE_TAKER  # noqa: E402
from MyTradingSys.backtest.power_mde import power_mde  # noqa: E402
from MyTradingSys.backtest.research_kit import TAKER_RT_PCT, cost_in_r  # noqa: E402

FEE_RT_PCT = BINANCE_TAKER * 2 * 100  # 0.10 % round trip
STOPS_PCT = (0.3, 0.5, 1.0, 2.0)  # OURS
SHAPES = ((0.40, 2.0), (0.55, 1.0), (0.33, 3.0))  # (win prob, gross RR), OURS; each has gross mean +0.20 R / +0.10 R / +0.32 R
NS = (30, 100, 300, 1000)  # OURS: fills in DEV 2022-04..2024-06 (27 months)


def rows():
    out = []
    for stop in STOPS_PCT:
        c = cost_in_r(FEE_RT_PCT, stop)
        cs = cost_in_r(TAKER_RT_PCT, stop)
        for p, rr in SHAPES:
            gross = p * rr - (1 - p)
            r = {n: power_mde(p, rr, c, n) for n in NS}
            n80 = r[NS[0]]["trades_for_80_power"]
            out.append((stop, c, cs, p, rr, gross, r[NS[0]]["mean_net_r"], n80, [r[n]["power"] for n in NS],
                        [r[n]["mde_net_r"] for n in NS]))
    return out


COLS = ["stop %", "cost R (fees.py)", "cost R (stress 0.14 %)", "win p", "RR", "gross R", "net R", "N for 80 % power",
        "power at n=" + " / ".join(str(n) for n in NS), "MDE net R at n=" + " / ".join(str(n) for n in NS)]


def cells():
    out = []
    for stop, c, cs, p, rr, gross, net, n80, pw, md in rows():
        # net <= 0 after fees: nothing to detect (power_mde's two-sided power would then measure the LOSS); floating
        # residue near 0 (e.g. 0.40 x 2.0 at a 0.5 % stop) counts as 0.
        dead = net <= 1e-9 or n80 == float("inf")
        n80s = "never (net <= 0)" if dead else "%d" % round(n80)
        pws = "n/a" if dead else " / ".join("%.0f%%" % (100 * x) for x in pw)
        out.append(["%.1f" % stop, "%.2f" % c, "%.2f" % cs, "%.2f" % p, "%.1f" % rr, "%+.2f" % gross, "%+.2f" % net, n80s, pws,
                    " / ".join("%.2f" % x for x in md)])
    return out


def sim_card(table):
    """Simulator result card (sim_desk/DESIGN.md schema) for the harness: what every Rumers rule will face before it runs."""
    dead = sum(1 for r in table if r[7].startswith("never"))
    return {
        "id": "dir-rumers_2026-11-01", "kind": "thought_experiment", "parity": None, "family": "Rumers (the.rumers)",
        "provenance": "run", "date": "2026-11-01",
        "title": "Rumers rules: test harness and fee / power gate (no rule run yet)",
        "what": [
            {"name": "Source", "value_plain": "10 @the.rumers videos (coordinator order 2026-11-01); rules come from the caption extracts, "
             "not yet on trunk (YouTube caption block on this machine)", "label": "SOURCED"},
            {"name": "Fees", "value_plain": "backtest/fees.py Binance taker 0.05 % per side (0.10 % round trip); stress column 0.14 % "
             "(research_kit, fee + 2+2 bp slippage)", "label": "SOURCED"},
            {"name": "Stops, win rates, RR", "value_plain": "stops 0.3 / 0.5 / 1 / 2 %, win 40 % x 2R, 55 % x 1R, 33 % x 3R: plausible "
             "shapes, replaced by each video's own claim once extracted", "label": "OURS"},
            {"name": "Run rules", "value_plain": "DEV 2022-04-01..2024-06-30 BTC 1m, decision on a closed bar and +-1 bar shift check, "
             "Holm over all rules, every variant in the trial registry, labels SOURCED / OURS", "label": "OURS"},
        ],
        "how": "power_table.py: for each stop and shape, cost in R from fees.py, then power_mde (two-sided, alpha 0.05) gives the "
               "fills needed for 80 % power and the smallest net edge each sample size can see. Re-run: python power_table.py --sim-json <file>.",
        "window": "none yet (a gate computed before any data is read); rule runs will use DEV 2022-04-01..2024-06-30",
        "verdict": {"label": "Not run yet: harness ready, waiting for the caption extracts", "tone": "warn"},
        "why": [
            "%d of %d stop / shape cells lose after fees alone (net <= 0 R), including every 0.3 %% stop: tight-stop rules need "
            "a large RR to survive." % (dead, len(table)),
            "A 27-month DEV swing rule with 50-300 fills only detects a net edge of about 0.3-0.5 R; smaller edges read NOT ENOUGH DATA, not PASSED.",
            "Each Rumers rule gets its own card here when it runs, with example trades on the chart.",
        ],
        "kpis": [{"label": "cells dead on fees", "value": "%d / %d" % (dead, len(table)), "tone": "bad"},
                 {"label": "fee round trip", "value": "%.2f %%" % FEE_RT_PCT},
                 {"label": "rules run", "value": "0"}],
        "examples": [{"kind": "table", "title": "Fee and power gate per stop and win-rate shape", "cols": COLS, "rows": table,
                      "caption": "never (net <= 0) = the shape loses after fees at that stop, so no sample size helps"}],
        "source_files": ["MyTradingSys/research/rumers_2026-11-01/HARNESS.md", "MyTradingSys/research/rumers_2026-11-01/power_table.py"],
        "commit": "this card",
    }


def main():
    table = cells()
    print("| " + " | ".join(COLS) + " |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in table:
        print("| " + " | ".join(r) + " |")
    if "--sim-json" in sys.argv:
        import json
        with open(sys.argv[sys.argv.index("--sim-json") + 1], "w", encoding="utf-8", newline="\n") as f:
            json.dump(sim_card(table), f, indent=1, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
