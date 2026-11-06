"""Re-score fabio_of (09-30) with the plan stop instead of the 0.15 % floor (decision d-stops-follow-trade-1106).

Reuses the archived driver's event/simulate code (same events, same management, current fees.py costs). Variants:
  OLD  = floor 0.0015 (the retired 0.15 % minimum stop, OURS)
  PLAN = floor 0 (stop 1 tick beyond the trigger extreme / broken level: the plan's invalidation as the spec states it)
Entry 'mkt' = regime A (taker in) ; 'limit' = regime B (maker in at the level, fades only; target maker, stops taker).
Usage: python rescore_fabio.py [--out F:/MTS/data/fabio_of_rescore] [--md MyTradingSys/backtest/layers/fabio/RESCORE.md]
"""
import argparse
import importlib.util
import itertools
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
ARCH = REPO / "MyTradingSys/archive/cleanup-2026-10-08/fabio_of_model/run_of_model.py"
from MyTradingSys.backtest.layers.fabio.orderflow_bars import load_days  # noqa: E402

spec = importlib.util.spec_from_file_location("run_of_model_arch", ARCH)
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)
M = D.M


def agg(trs):
    n = len(trs)
    if not n:
        return {"n": 0, "gross": None, "net": None, "win": None}
    return {"n": n, "gross": sum(t["gross_R"] for t in trs) / n, "net": sum(t["net_R"] for t in trs) / n,
            "win": sum(1 for t in trs if t["net_R"] > 0) / n,
            "med_risk_bp": statistics.median(t["risk"] / t["entry"] * 1e4 for t in trs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"F:\MTS\data\orderflow_1m")
    ap.add_argument("--out", default=r"F:\MTS\data\fabio_of_rescore")
    ap.add_argument("--md", default=str(REPO / "MyTradingSys/backtest/layers/fabio/RESCORE_tables.json"))
    a = ap.parse_args()
    bars = load_days(a.data)
    times, info = D.prepare(bars)
    days = sorted({D.day_of(b["t"]) for b in bars if b["thr_days"] >= D.MIN_THR_DAYS})
    n_is = int(len(days) * 0.7)
    oos = set(days[n_is:])
    evs, _ = D.collect_events(bars, times, info, "true")
    res = []
    for (tf, pct, k), ev in evs.items():
        for entry, mgmt, floor in itertools.product(D.ENTRIES, D.MGMTS, D.FLOORS):
            trs = D.simulate(bars, ev, tf, entry, mgmt, floor)
            for t in trs:
                t["oos"] = t["day"] in oos
            res.append({"tf": tf, "pct": pct, "k": k, "entry": entry, "mgmt": mgmt, "floor": floor, "trades": trs})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in ("balance_fade", "imb_break"):
        for scope in ("all", "ny"):
            for entry in ("mkt", "limit"):
                if model == "imb_break" and entry == "limit":
                    pass  # imb_break always enters at market in simulate(); the limit grid cell equals mkt: skipped
                if model == "imb_break" and entry == "limit":
                    continue
                for floor in (0.0015, 0.0):
                    pool = {"all90": [], "oos": []}
                    per_var = []
                    for r in res:
                        if r["entry"] != entry or r["floor"] != floor:
                            continue
                        trs = [t for t in r["trades"] if t["model"] == model and (scope == "all" or t["session"] == scope)]
                        pool["all90"] += trs
                        o = [t for t in trs if t["oos"]]
                        pool["oos"] += o
                        per_var.append(agg(o)["net"] if len(o) >= 30 else None)
                    ok = [x for x in per_var if x is not None]
                    rows.append({"model": model, "scope": scope, "entry": entry, "floor": floor,
                                 "all90": agg(pool["all90"]), "oos": agg(pool["oos"]),
                                 "variants_oos_n30": len(ok), "variants_net_pos": sum(1 for x in ok if x > 0),
                                 "median_var_net": statistics.median(ok) if ok else None})
    (out / "rescore.json").write_text(json.dumps(rows, indent=1), encoding="utf-8", newline="\n")
    Path(a.md).write_text(json.dumps(rows, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
