"""Design look (SEEN window, gross arithmetic, not a test): what ladder shapes would have done on the DOWN-high take-outs of
phase1_recent.py, incl. the operator's 2026-11-01 "martingale inside a martingale" (a ladder per range tier 0.65 / 1.0 / 1.5 %,
each tier bigger). Every shape: legs sell at fixed prices above H1 (filled when a 15m high reaches the price), ONE stop for all
legs at H1 + X (filled at that price; a bar that reaches a leg and the stop fills the leg first, worst case), target = L1 touch
(all legs out at L1; a bar that reaches L1 and the stop counts the stop), time = close of the 96th 15m bar after the take-out.
P&L in unit-% of H1: units x (entry - exit) / H1 x 100, minus fees.py BINANCE_TAKER x 2 per unit per leg. All numbers OURS.
Usage: python phase1_ladder_look.py <repo> <cache> [--until 2026-11-01T07:45] [--card FILE]  (--card appends the table to a card)
"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_range as R  # noqa: E402

_spec = importlib.util.spec_from_file_location("mts_fees", os.path.join(os.path.dirname(os.path.dirname(HERE)), "backtest", "fees.py"))
fees = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(fees)
FEE = fees.BINANCE_TAKER * 2 * 100  # % per unit per leg round trip (taker in + taker out), SOURCED from fees.py
HOLD = 96
SHAPES = {
    # name: (legs [(step % above H1, units)], stop X %); the single short enters at the first 15m close back under H1 instead
    "A single short, stop 1.0": ("close", 1.0),
    "A single short, stop 1.5": ("close", 1.5),
    "flat 3 legs 1-1-1, stop 1.0": ([(0.0, 1), (0.3, 1), (0.6, 1)], 1.0),
    "martingale 1-2-4, stop 1.0": ([(0.0, 1), (0.3, 2), (0.6, 4)], 1.0),
    "nested tiers 0.65/1.0/1.5, sizes 1/2/4, stop 1.5": ([(0.0, 1), (0.3, 1), (0.65, 2), (0.85, 2), (1.0, 4), (1.25, 4)], 1.5),
    "nested tiers, flat sizes 1/1/1, stop 1.5": ([(0.0, 1), (0.3, 1), (0.65, 1), (0.85, 1), (1.0, 1), (1.25, 1)], 1.5),
}


def book(e, legs, X):
    """One event, one shape: returns (net unit-%, units used, outcome)."""
    P = R.P
    lvl, l1, take = e["h1"], e["l1"], e["_take"]
    end = min(P.N - 1, take + HOLD)
    stop_px = lvl * (1 + X / 100)
    open_, used = [], 0
    todo = [] if legs == "close" else [(lvl * (1 + s / 100), u) for s, u in legs]

    def out(px_exit, why):
        return sum(u * ((px - px_exit) / lvl * 100 - FEE) for px, u in open_), used, why
    for k in range(take, end + 1):
        hi, lo, cl = P.H[k], P.L[k], P.C[k]
        if legs == "close":
            if not open_:
                if cl < lvl:
                    open_.append((cl, 1)); used = 1  # entered at this close; exits are checked from the next bar
                continue
        else:
            for px, u in [t for t in todo if hi >= t[0]]:
                open_.append((px, u)); used += u; todo.remove((px, u))
        if open_ and hi >= stop_px:
            return out(stop_px, "stop")
        if open_ and lo <= l1:
            return out(l1, "L1")
    if open_:
        return out(P.C[end], "24h")
    return 0.0, 0, "no fill"


def main():
    R._load()
    args = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    ev = [e for e in R.P.run(1) if e["_take"] is not None and e["phase"] == "DOWN"]
    rows = []
    for name, (legs, X) in SHAPES.items():
        res = [book(e, legs, X) for e in ev]
        filled = [r for r in res if r[2] != "no fill"]
        net = [r[0] for r in filled]
        outs = {o: sum(1 for r in filled if r[2] == o) for o in ("L1", "24h", "stop")}
        maxu = max(r[1] for r in filled) if filled else 0
        rows.append([name, "%d/%d" % (len(filled), len(ev)), "%d / %d / %d" % (outs["L1"], outs["24h"], outs["stop"]),
                     "%+.2f" % (sum(net) / len(net)) if net else "-", "%+.2f" % sum(net) if net else "-",
                     "%+.2f" % min(net) if net else "-", "%+.2f" % (sum(net) / len(net) / maxu) if net and maxu else "-", str(maxu)])
    cols = ["shape", "events filled", "exits L1 / 24h / stop", "mean net unit-%", "sum", "worst event", "mean net per max unit", "max units"]
    print("## Q3. Ladder shapes on the DOWN-high take-outs (design look, gross arithmetic, n=%d)\n" % len(ev))
    print(R.table(cols, rows))
    print("\nunit-%% = units x move in %% of H1, fee %.2f %% per unit per leg; 'per max unit' divides by the largest stack the shape can carry "
          "(the margin it needs). Single short enters at the first 15m close back under H1." % FEE)
    if "--card" in args:
        p = args["--card"]
        d = json.load(open(p, encoding="utf-8"))
        d["examples"] = [x for x in d["examples"] if x.get("title") != "Ladder shapes on the DOWN-high take-outs"]
        d["examples"].append({"kind": "table", "title": "Ladder shapes on the DOWN-high take-outs", "cols": cols, "rows": rows,
                              "caption": "design look, gross arithmetic on %d events: unit-%% = units x move in %% of H1, fee %.2f %% per unit per leg; "
                                         "'per max unit' = mean net divided by the biggest stack the shape carries. Operator 2026-11-01: ladder per tier "
                                         "0.65 / 1.0 / 1.5 ('martingale inside a martingale')" % (len(ev), FEE)})
        d["source_files"] = sorted(set(d["source_files"] + ["MyTradingSys/research/c26_roadmap_2026-11-01/phase1_ladder_look.py"]))
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f, indent=1, ensure_ascii=False); f.write("\n")


if __name__ == "__main__":
    main()
