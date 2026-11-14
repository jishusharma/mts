"""T12 counting step: signal and unit counts only. This script never calls simulate_plan, so it has no access to any
return, exit or P&L. It prints counts and the (outcome-free) stop distance."""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t12_core as core  # noqa: E402


def main():
    print("priority:", core.set_below_normal())
    with core.Slot("t12-count"):
        coins, funds, data_end, names = core.load_universe()
        phase = core.load_phase(core.PHASE_CSV)
        alive = core.alive_counts(coins)
        low_days = sum(1 for d, v in alive.items() if v < core.MIN_ALIVE)
        out = dict(universe=names, n_coins=len(coins), data_end_ms=data_end, dates_below_30_alive=low_days, cells={})
        for cell in ("A", "B"):
            side = core.CELLS[cell]["side"]
            agg = {s: dict(flag_days=0, flag_rev=0, fired=0, planned=0, weeks=set(), stops=[], ended=0, skip={}) for s in ("DEV", "VAL")}
            by_coin = {}
            for c in coins:
                f = funds.get(c.name)
                for r in core.day_flags(c, f, phase, cell, alive):
                    s = core.split_of(int(c.ms[r["i"]]))
                    agg[s]["flag_days"] += 1
                    agg[s]["flag_rev"] += int(r["rev"])
                for r in core.signals(c, f, phase, cell, alive):
                    s = core.split_of(int(c.ms[r["i"]]))
                    agg[s]["fired"] += 1
                    p, why = core.plan_trade(c, f, r["i"], side)
                    if p is None:
                        agg[s]["skip"][why] = agg[s]["skip"].get(why, 0) + 1
                        continue
                    agg[s]["planned"] += 1
                    agg[s]["weeks"].add(p["week"])
                    agg[s]["stops"].append(p["stop_pct"])
                    agg[s]["ended"] += int(p["ended"])
                    by_coin[c.name] = by_coin.get(c.name, 0) + 1
            res = {}
            for s, a in agg.items():
                st = np.array(a["stops"]) if a["stops"] else np.array([np.nan])
                res[s] = dict(flag_days=a["flag_days"], flag_and_reversal=a["flag_rev"], fired_after_cooldown=a["fired"],
                              trades_planned=a["planned"], distinct_entry_weeks=len(a["weeks"]), ended=a["ended"],
                              skipped=a["skip"], stop_pct_median=float(np.nanmedian(st)),
                              stop_pct_p10=float(np.nanpercentile(st, 10)), stop_pct_p90=float(np.nanpercentile(st, 90)),
                              fee_R_median=float(core.FEE_RT / np.nanmedian(st)))
            res["coins_with_trades"] = len(by_coin)
            out["cells"][cell] = res
        p = pathlib.Path(__file__).resolve().parent / "counts.json"
        p.write_text(json.dumps(out, indent=1, default=str))
        print(json.dumps({k: v for k, v in out.items() if k != "universe"}, indent=1, default=str))


if __name__ == "__main__":
    main()
