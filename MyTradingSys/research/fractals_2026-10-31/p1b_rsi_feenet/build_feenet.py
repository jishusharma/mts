"""P1b: fee-net per-event R list for RSI-DIV-MTF DEV events (PRE_REG.md). Research only."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT.parent))
from MyTradingSys.backtest.fees import BINANCE_TAKER  # noqa: E402

_ET = ROOT / "research/layer_lab/rsi_divergence_event_table/event_table.py"
_SPEC = importlib.util.spec_from_file_location("rsi_event_table_p1b", _ET)
et = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(et)

DEV_END_MS = et.DEV_END_MS
STOP_R = 1.0     # OURS (PRE_REG s2)
TARGET_R = 2.0   # OURS (PRE_REG s2)
HORIZON = et.HORIZON  # SOURCED event_table.py


def dev_mask(t):
    return np.asarray(t) < DEV_END_MS


def simulate_exit(side, o, h, l, c, risk, horizon=HORIZON):
    """Walk the bars from the entry bar (index 0 of the passed arrays) one at a time.
    Returns (exit_price, reason, bars_used). Bars after the exit bar are never read."""
    entry = float(o[0])
    sgn = 1.0 if side == "long" else -1.0
    stop = entry - sgn * STOP_R * risk
    target = entry + sgn * TARGET_R * risk
    for k, (ok, hk, lk, ck) in enumerate(zip(o, h, l, c)):
        if k >= horizon:
            break
        hit_stop = lk <= stop if sgn > 0 else hk >= stop
        hit_tgt = hk >= target if sgn > 0 else lk <= target
        if hit_stop:
            gap = (ok <= stop) if sgn > 0 else (ok >= stop)
            return (float(ok) if gap else float(stop)), "stop", k + 1
        if hit_tgt:
            return float(target), "target", k + 1
        if k == horizon - 1:
            return float(ck), "time", k + 1
    return float(c[min(len(c), horizon) - 1]), "time", min(len(c), horizon)


def net_r(side, entry, exit_price, risk):
    sgn = 1.0 if side == "long" else -1.0
    gross = sgn * (exit_price - entry) / risk
    fee_r = BINANCE_TAKER * (entry + exit_price) / risk  # one taker side on entry, one on exit
    return gross, gross - fee_r


def build(data_path="F:/MTS/data/bigtrade/cache/perp/klines_1h.npz"):
    one = et._dev_1h(Path(data_path))
    four = et._to_4h(one)
    bars_tf = {"1h": one, "4h": four}
    rows = et.build_event_table(bars_tf)
    out, dropped = [], 0
    for r in rows:
        if r["status"] != "OK":
            dropped += 1
            continue
        b = bars_tf[r["timeframe"]]
        i = int(r["entry_i"])
        end = i + HORIZON
        side, risk = r["side"], float(r["r"])
        ex, why, nb = simulate_exit(side, b["o"][i:end], b["h"][i:end], b["l"][i:end], b["c"][i:end], risk)
        g, n = net_r(side, float(r["entry"]), ex, risk)
        ts = pd.Timestamp(int(r["entry_t"]), unit="ms")
        out.append(dict(time=ts.strftime("%Y-%m-%dT%H:%M:%SZ"), timeframe=r["timeframe"], side=side, entry=r["entry"],
                        exit=ex, exit_reason=why, bars=nb, r_unit=risk, r_gross=g, r_net=n, date=ts.strftime("%Y-%m-%d")))
    return pd.DataFrame(out), dropped


if __name__ == "__main__":
    df, dropped = build()
    df.to_csv(HERE / "events_feenet.csv", index=False, lineterminator="\n")
    print(len(df), "events,", dropped, "dropped (NOT_IN_DATA)")
