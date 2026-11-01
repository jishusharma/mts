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


def main():
    print("| stop % | cost R (fees.py) | cost R (stress 0.14 %) | win p | RR | gross R | net R | N for 80 % power | power at n=" +
          " / ".join(str(n) for n in NS) + " | MDE net R at n=" + " / ".join(str(n) for n in NS) + " |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for stop, c, cs, p, rr, gross, net, n80, pw, md in rows():
        # net <= 0 after fees: nothing to detect (power_mde's two-sided power would then measure the LOSS); floating
        # residue near 0 (e.g. 0.40 x 2.0 at a 0.5 % stop) counts as 0.
        dead = net <= 1e-9 or n80 == float("inf")
        n80s = "never (net <= 0)" if dead else "%d" % round(n80)
        pws = "n/a" if dead else " / ".join("%.0f%%" % (100 * x) for x in pw)
        print("| %.1f | %.2f | %.2f | %.2f | %.1f | %+.2f | %+.2f | %s | %s | %s |" % (
            stop, c, cs, p, rr, gross, net, n80s, pws,
            " / ".join("%.2f" % x for x in md)))


if __name__ == "__main__":
    main()
