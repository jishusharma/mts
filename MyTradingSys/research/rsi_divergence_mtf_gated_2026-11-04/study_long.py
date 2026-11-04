"""rsi_divergence_mtf_gated LONG-window DEV pass (PRE_REG_LONG.md). Reuses study.py cell logic unchanged.

Data: public SPOT klines 2017-08.. (F:/MTS/Dumps/backtest/spot_2017/<SYMBOL>/<tf>/klines) at 15m/1h/4h/1d directly; weekly and
monthly RSI come from resampling the spot 1d bars. Not spliced with futures. Passes: count (no returns), dev, val (survivors only).
Regimes: primary = research_kit.regime_tag (Malkan weekly-AND-monthly 60/40, SOURCED). Proxy P40 (OURS, coordinator d-bear-proxy-1104):
bear = weekly RSI14 <= 40 alone (monthly ignored) AND close below SMA200; bull/range exactly as primary.
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
_spec = importlib.util.spec_from_file_location("rsi_gated_study", HERE / "study.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
rk, splits, DAY = S.rk, S.splits, S.DAY

SPOT_ROOT = "F:/MTS/Dumps/backtest/spot_2017"
SYMBOL = "BTCUSDT"
LONG_START = "2017-08-01"             # first month on disk; PRE_DEV in splits.py terms, declared NEW DEV by PRE_REG_LONG.md
FAMILY_PRIMARY = len(S.HOLM_ARMS) * len(S.TFS) * 2 * len(S.ENTRIES)       # 32
FAMILY_PROXY = len(S.HOLM_ARMS) * len(S.TFS) * 1 * len(S.ENTRIES)         # 16 (bearish aligned under P40)
FAMILY_M = FAMILY_PRIMARY + FAMILY_PROXY                                   # 48


def make_regime_at(daily, weekly_rsi, monthly_rsi, bear_proxy=False):
    """As-of regime per UTC day. bear_proxy=True: a day 'below SMA200' with weekly RSI <= RSI_BEAR (monthly ignored) is bear."""
    cache = {}

    def regime_at(t):
        d = int(t // DAY)
        if d not in cache:
            tag = rk.regime_tag(d * DAY, daily, weekly_rsi, monthly_rsi)
            reg = tag["regime"]
            if bear_proxy and tag["side"] == "below":
                w = rk._last_closed(weekly_rsi, d * DAY)
                if w is not None and w <= rk.RSI_BEAR:
                    reg = "bear"
            cache[d] = reg
        return cache[d]
    return regime_at


def gate_all_tagged(events, regime_at, kind):
    """Ungated control restricted to events whose regime is known (so aligned/counter/range/all share one time span)."""
    return S.gate_events(events, regime_at, kind, "all")


def load_spot(tf, end_ms, root=SPOT_ROOT, symbol=SYMBOL):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = load_klines(Path(root) / symbol / tf, end_ms=end_ms)
    if bars:
        assert bars[-1]["t"] < end_ms
    return bars


def build_context(daily_bars, registry):
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    daily = ([x["t"] + DAY for x in daily_bars], [x["c"] for x in daily_bars])
    return daily, S.rsi_series(resample(daily_bars, "1w", registry)), S.rsi_series(resample(daily_bars, "1M", registry))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    ap.add_argument("--root", default=SPOT_ROOT)
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    if a.pass_ == "val":
        survivors = json.loads((HERE / "dev_survivors_long.json").read_text(encoding="utf-8"))
        if not survivors:
            print("no long-DEV survivors: VALIDATION not read")
            return 0
        if (HERE / "val_cells_long.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
        lo_ms, hi_ms = S.ms(splits.VALIDATION_START), S.ms(splits.VALIDATION_END)
    else:
        lo_ms, hi_ms = S.ms(pd.Timestamp(LONG_START)), S.ms(splits.DEV_END)
    d1 = load_spot("1d", hi_ms, a.root)
    daily, wk, mo = build_context(d1, registry)
    reg_p = make_regime_at(daily, wk, mo)
    reg_x = make_regime_at(daily, wk, mo, bear_proxy=True)
    rows = []
    for tf in S.TFS:
        bars = d1 if tf == "1d" else load_spot(tf, hi_ms, a.root)
        for arm in S.ARMS:
            for kind, (sgn, aligned) in S.KINDS.items():
                evs = S.find_events(bars, kind, arm, tf)
                variants = [("primary", reg_p, ("all", "aligned", "counter", "range"))]
                if kind == "bearish" and arm in S.HOLM_ARMS:
                    variants.append(("P40", reg_x, ("aligned",)))
                for rdef, reg, modes in variants:
                    for mode in modes:
                        ge = S.gate_events(evs, reg, kind, mode)
                        for entry in S.ENTRIES:
                            if a.pass_ == "val" and not (mode == "aligned" and [rdef, tf, arm, kind, entry] in survivors):
                                continue
                            trs, nsig = S.trades_for(ge, bars, kind, entry, lo_ms=lo_ms, hi_ms=hi_ms)
                            row = {"regime_def": rdef, "tf": tf, "arm": arm, "kind": kind, "gate": mode, "entry": entry, "signals": nsig}
                            if a.pass_ == "count":
                                row.update({"n": len(trs), "days": len({x["day"] for x in trs})})
                            else:
                                dr = S.regime_drift(bars, reg, sgn, tf, aligned, lo_ms=lo_ms, hi_ms=hi_ms) if mode == "aligned" else None
                                row.update(S.cell_stats(trs, dr))
                            rows.append(row)
        print(tf, "done", file=sys.stderr, flush=True)
    if a.pass_ == "dev":
        fam = [r for r in rows if r["gate"] == "aligned" and r["arm"] in S.HOLM_ARMS and r.get("n", 0) > 0]
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=FAMILY_M)
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            r["survivor"] = bool(r["n"] >= S.MIN_N and r["days"] >= S.MIN_DAYS and r["net"] > 0 and q < 0.05
                                 and r["excess_t"] == r["excess_t"] and r["excess_t"] >= 2)
        with open(HERE / "dev_survivors_long.json", "w", newline="\n") as f:
            json.dump([[r["regime_def"], r["tf"], r["arm"], r["kind"], r["entry"]] for r in fam if r.get("survivor")], f)
    name = {"count": "counts_long.csv", "dev": "dev_cells_long.csv", "val": "val_cells_long.csv"}[a.pass_]
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("regime_def", "tf", "arm", "kind", "gate", "entry"), k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    starts = S.week_starts(lo_ms, hi_ms)
    tp, tx = [reg_p(t) for t in starts], [reg_x(t) for t in starts]
    line = (rk.regime_mix_line(tp) + f" | bear weeks primary {tp.count('bear')} (weekly AND monthly <=40), "
            f"proxy P40 {tx.count('bear')} (weekly <=40 alone, OURS)")
    (HERE / ("regime_mix_%s_long.txt" % a.pass_)).write_text(line + "\nproxy P40 mix: " + rk.regime_mix_line(tx) + "\n",
                                                             encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
