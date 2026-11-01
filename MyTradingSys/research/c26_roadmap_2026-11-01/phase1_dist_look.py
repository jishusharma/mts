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
import phase1_card as CARD  # noqa: E402

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
    qcols = ["quantity", "p25", "p50", "p75", "p90"]
    print(R.table(qcols, rows))
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
    gcols = ["stop (% of H1, MAE quantile p50/p75/p90 + 1.0)", "target (% of H1, MFE quantile p25/p50/p75)", "exits tgt / 24h / stop",
             "mean net %", "sum", "worst"]
    print(R.table(gcols, grid))
    print("\nStops and targets are read off the same 30 events they are scored on: a SEEN-window shape, not a result. Fee %.2f %% per round trip." % FEE)
    if CARD.arg("--card"):
        means = [float(g[3]) for g in grid]
        p50 = {r[0].split(" (")[0].split(":")[0]: r[2] for r in rows}  # quantity -> p50
        CARD.write(CARD.arg("--card"), CARD.card(
            "c26-q10-path-distribution",
            "C26 Q10: the probability-distribution layer on the take-out: quantiles of the path (overshoot, wait, MAE, MFE, L1) and a stop x target grid read off them",
            [CARD.P("Events", "C26 held highs taken out in a DOWN phase (phase1_recent.py), 15m Binance spot BTCUSDT"),
             CARD.P("Layer", "operator's standing probability-distribution layer (research/prob_dist_layer_brief_2026-10-16/BRIEF.md, design D2 "
                             "'outcome after event'): read what price did off its own quantiles instead of a fixed stop and target"),
             CARD.P("Path", "overshoot above H1 before the first 15m close back under it; bars waited; after that entry close within 96 bars: MAE = highest "
                            "high above entry, MFE = deepest low under entry, L1 = the pull-back low; all in % of H1"),
             CARD.P("Grid", "short from the entry close; stop = MAE p50 / p75 / p90 and 1.0 %%; target = MFE p25 / p50 / p75; else exit at the 24h close; "
                            "stop checked before target; fee %.2f %% per round trip" % FEE),
             CARD.P("Quantiles", "linear interpolation, p25 / p50 / p75 / p90"),
             CARD.FEE],
            "phase1_dist_look.py <repo> <cache> --until 2026-11-01T07:45 --card <this file>. The stops and targets are read off the same %d events they are "
            "scored on, so the grid is a shape, not a result: Phase 2 freezes the quantiles on SEEN and scores them once on VALIDATION." % len(E),
            "Design look on SEEN, n=%d: the stop x target grid is flat, mean net %+.2f to %+.2f %%: the drift after the reclaim makes the trade, not the exit shape"
            % (len(E), min(means), max(means)), "info",
            ["Every stop x target pair lands in the same narrow band of mean net, so the exit shape is not where the edge would come from.",
             "Half the reclaims come on the take-out bar or the next (wait p50 %s bars) with overshoot p50 %s %%; the slow tenth (p90) is the Q7 band-overshoot case."
             % (p50.get("bars to the first close back under H1", "?"), p50.get("overshoot above H1 before the reclaim", "?")),
             "MFE p50 %s %% against MAE p50 %s %% is about 2:1 before fees, but L1 p50 %s %% sits at half the available move, so L1 as target takes the first half."
             % (p50.get("MFE after entry", "?"), p50.get("MAE after entry", "?"), p50.get("L1 below entry", "?")),
             "Right use: freeze stop / target quantiles from SEEN (Phase 2 card), score once on VALIDATION; a grid searched on VALIDATION is the overfit the roadmap forbids."],
            [{"label": "take-outs / entries", "value": "%d / %d" % (len(D), len(E))},
             {"label": "overshoot p50 (% of H1)", "value": p50.get("overshoot above H1 before the reclaim", "?")},
             {"label": "MAE p50 (%)", "value": p50.get("MAE after entry", "?")}, {"label": "MFE p50 (%)", "value": p50.get("MFE after entry", "?")},
             {"label": "L1 below entry p50 (%)", "value": p50.get("L1 below entry", "?")},
             {"label": "grid mean net, worst .. best pair", "value": "%+.2f .. %+.2f %%" % (min(means), max(means))}],
            [CARD.table("Quantiles of the path around the take-out (% of H1, bars)", qcols, rows),
             CARD.table("Stop x target grid read off those quantiles, fee-net", gcols, grid, "exits: target / 24h close / stop; mean, sum and worst in % per trade")],
            ["phase1_dist_look.py", "PHASE1_RANGE.md"]))


if __name__ == "__main__":
    main()
