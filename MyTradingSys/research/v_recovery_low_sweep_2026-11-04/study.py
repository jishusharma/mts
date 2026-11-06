"""v_recovery_low_sweep_2026-11-04: BTC 1h 5-day-low sweep + >=50% win-back within 3 bars. See PRE_REG.md.
Passes: --pass count (event counts, no returns), --pass dev (DEV only). VALIDATION/HOLDOUT never loaded (loader end = DEV_END)."""
import argparse, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk, splits  # noqa: E402
LOOK, WINBACK, MAXBARS = 120, 0.5, 3          # OURS (5 d of 1h bars, 50 %, 3 h)
HZ = {"4h": 4, "24h": 24, "72h": 72}
DAY = 86400000
HOUR = 3600000


def load(end_ms, start_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = {}
    for root, ds in (("F:/MTS/data/dev_ext_2019_2021", "klines"), ("F:/MTS/data/bigtrade", "spot_raw")):
        for b in load_klines(root, ds, start_ms=start_ms, end_ms=end_ms):
            bars[b["t"]] = b
    return [bars[k] for k in sorted(bars)]


def ms(s):
    import pandas as pd
    return int(pd.Timestamp(s).tz_localize("UTC").timestamp() * 1000)


def events(b, lo, hi):
    """Event = first close within 3 bars after (and incl.) the sweep bar whose close >= midpoint(prior 120-bar low, running sweep low).
    Prior low uses bars before the sweep bar only; win-back uses closes only. Non-overlapping: scan resumes after the recovery bar."""
    out, i = [], LOOK
    while i < len(b):
        pl = min(x["l"] for x in b[i - LOOK:i])
        if b[i]["l"] < pl:
            sw = b[i]["l"]
            for j in range(i, min(i + MAXBARS, len(b) - 1) + 1):
                sw = min(sw, b[j]["l"])
                if b[j]["c"] >= sw + WINBACK * (pl - sw):
                    out.append((j, pl, sw))
                    break
            else:
                i += 1
                continue
            i = j + 1
            continue
        i += 1
    return [e for e in out if lo <= b[e[0]]["t"] + HOUR < hi]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev"))
    a = ap.parse_args()
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    reg = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    lo, hi = ms(splits.DEV_START), ms(splits.DEV_END)
    m1 = load(hi, ms("2021-12-01"))
    assert m1[-1]["t"] < hi
    b = resample(m1, "1h", reg)
    ev = events(b, lo, hi)
    res = {"events": len(ev), "event_days": len({b[j]["t"] // DAY for j, _, _ in ev})}
    if a.pass_ == "dev":
        for nm, h in HZ.items():
            g, d = [], []
            for j, _, _ in ev:
                if j + h < len(b):
                    g.append((b[j + h]["c"] - b[j]["c"]) / b[j]["c"] * 100.0)
                    d.append(int(b[j]["t"] // DAY))
            g = np.array(g); net = g - rk.TAKER_RT_PCT
            m, se = rk.cluster_mean_se(net, d)
            res[nm] = {"n": len(g), "gross": float(g.mean()), "net": m, "median_net": float(np.median(net)), "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se}
    (HERE / ("counts.json" if a.pass_ == "count" else "dev.json")).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(res)


if __name__ == "__main__":
    main()
