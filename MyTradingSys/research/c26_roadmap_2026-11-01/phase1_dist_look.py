"""Design look (SEEN window, descriptive, not a test): the probability-distribution layer (research/prob_dist_layer_brief_2026-10-16
D2 "outcome-after-event table") applied to the C26 event: the DOWN-high take-out of phase1_recent.py. Instead of the fixed
stop 1 % / target L1 of phase1_ladder_look.py, print the empirical distribution of what price did, so entry and exit can be
read off quantiles (OURS; all numbers in % of H1):
  overshoot      = highest high above H1 from the take-out bar to the first 15m close back under H1 (where legs would fill)
  bars to reclaim= 15m bars from the take-out to that first close under H1 (how long the entry waits)
  MAE after entry= highest high above the entry close within the 96-bar hold (where a stop must sit to survive)
  MFE after entry= deepest low under the entry close within the hold (what a target could have taken)
  L1 distance    = entry close to L1
Then a small stop x target grid in quantiles of those two distributions, fee-net (fees.py BINANCE_TAKER x 2).
Usage: python phase1_dist_look.py <repo> <cache> [--until 2026-11-01T07:45]
"""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_range as R  # noqa: E402

_spec = importlib.util.spec_from_file_location("mts_fees", os.path.join(os.path.dirname(os.path.dirname(HERE)), "backtest", "fees.py"))
fees = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(fees)
FEE = fees.BINANCE_TAKER * 2 * 100  # SOURCED
HOLD = 96
QS = (0.25, 0.5, 0.75, 0.9)


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    i = (len(xs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def path(e):
    P = R.P
    lvl, l1, take = e["h1"], e["l1"], e["_take"]
    end = min(P.N - 1, take + HOLD)
    back = next((m for m in range(take, end + 1) if P.C[m] < lvl), None)
    d = dict(over=(max(P.H[take:(back if back is not None else end) + 1]) - lvl) / lvl * 100, wait=back - take if back is not None else None)
    if back is None or back == end:
        return d
    ent = P.C[back]
    hi = [P.H[k] for k in range(back + 1, end + 1)]
    lo = [P.L[k] for k in range(back + 1, end + 1)]
    d.update(ent=ent, mae=(max(hi) - ent) / lvl * 100, mfe=(ent - min(lo)) / lvl * 100, l1d=(ent - l1) / lvl * 100,
             H=hi, L=lo, C=[P.C[k] for k in range(back + 1, end + 1)])
    return d


def book(d, stop, tgt):
    """Short from the entry close; stop = % of H1 above entry, tgt = % of H1 below entry; stop first on a bar that touches both."""
    sp, tp = d["ent"] * (1 + stop / 100), d["ent"] * (1 - tgt / 100)
    for h, l, c in zip(d["H"], d["L"], d["C"]):
        if h >= sp:
            return -stop - FEE, "stop"
        if l <= tp:
            return tgt - FEE, "tgt"
    return (d["ent"] - d["C"][-1]) / d["ent"] * 100 - FEE, "24h"


def main():
    R._load()
    ev = [e for e in R.P.run(1) if e["_take"] is not None and e["phase"] == "DOWN"]
    D = [path(e) for e in ev]
    E = [d for d in D if "ent" in d]
    print("## Q10. Distribution of the path around the DOWN-high take-out (design look, OURS, n=%d take-outs, %d entries)\n" % (len(D), len(E)))
    rows = [["overshoot above H1 before the reclaim (%)"] + ["%.2f" % pct([d["over"] for d in D], q) for q in QS],
            ["bars to the first close back under H1"] + ["%.0f" % pct([d["wait"] for d in D if d["wait"] is not None], q) for q in QS],
            ["MAE after entry: highest high above entry (%)"] + ["%.2f" % pct([d["mae"] for d in E], q) for q in QS],
            ["MFE after entry: deepest low under entry (%)"] + ["%.2f" % pct([d["mfe"] for d in E], q) for q in QS],
            ["L1 below entry (%)"] + ["%.2f" % pct([d["l1d"] for d in E], q) for q in QS]]
    print(R.table(["quantity", "p25", "p50", "p75", "p90"], rows))
    print("\n%d of %d take-outs never closed back under H1 inside the hold (no entry)." % (len(D) - len(E), len(D)))
    stops = [round(pct([d["mae"] for d in E], q), 2) for q in (0.5, 0.75, 0.9)] + [1.0]
    tgts = [round(pct([d["mfe"] for d in E], q), 2) for q in (0.25, 0.5, 0.75)]
    grid = []
    for s in sorted(set(stops)):
        for t in sorted(set(tgts)):
            res = [book(d, s, t) for d in E]
            n = len(res)
            grid.append(["%.2f" % s, "%.2f" % t, "%d / %d / %d" % tuple(sum(1 for r in res if r[1] == w) for w in ("tgt", "24h", "stop")),
                         "%+.2f" % (sum(r[0] for r in res) / n), "%+.2f" % sum(r[0] for r in res), "%+.2f" % min(r[0] for r in res)])
    print()
    print(R.table(["stop (% of H1, MAE quantile p50/p75/p90 + 1.0)", "target (% of H1, MFE quantile p25/p50/p75)", "exits tgt / 24h / stop",
                   "mean net %", "sum", "worst"], grid))
    print("\nStops and targets are read off the same 30 events they are scored on: a SEEN-window shape, not a result. Fee %.2f %% per round trip." % FEE)


if __name__ == "__main__":
    main()
