"""T09 exit-rule arithmetic: how often does the live layer bracket (stop 1%, target 2%, time exit 8 bars of the signal tf)
end by time, on DEV BTCUSDT 1m bars, for entries every few minutes (signal-independent: the layers have no stop/target of
their own, auto_trader.layer_signal). Also the backtest bracket of the RSI studies (1% / 2% / 100 bars).
Rule used (pessimistic, same as bt_engine): stop checked before target inside one 1m bar. Entry = close of minute i, exits scanned from minute i+1.
Run from the worktree root. Writes scripts/T09/out/exit_result.json."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import parity_core as pc  # noqa: E402

STOP, TARGET = 0.01, 0.02


def shares(close, high, low, hold, stride, side):
    n = len(close)
    idx = np.arange(0, n - hold - 1, stride)
    res = {"stop": 0, "target": 0, "time": 0}
    CH = 2000
    for ii in np.array_split(idx, max(1, -(-len(idx) // CH))):
        e = close[ii][:, None]
        cols = ii[:, None] + 1 + np.arange(hold)[None, :]
        hi, lo = high[cols], low[cols]
        if side == "long":
            hs = lo <= e * (1 - STOP); ht = hi >= e * (1 + TARGET)
        else:
            hs = hi >= e * (1 + STOP); ht = lo <= e * (1 - TARGET)
        fs = np.where(hs.any(1), hs.argmax(1), hold + 1)
        ft = np.where(ht.any(1), ht.argmax(1), hold + 1)
        stop_first = (fs <= ft) & (fs <= hold)
        tgt_first = (ft < fs) & (ft <= hold)
        res["stop"] += int(stop_first.sum()); res["target"] += int(tgt_first.sum())
        res["time"] += int((~stop_first & ~tgt_first).sum())
    tot = sum(res.values())
    return {"n": tot, **{k: round(v / tot, 4) for k, v in res.items()}}


def main():
    bars = pc.load_dev_1m()
    close = np.array([b["c"] for b in bars]); high = np.array([b["h"] for b in bars]); low = np.array([b["l"] for b in bars])
    out = {"live_rule": {}, "backtest_rsi_rule": {}, "rule": "stop 1%, target 2%, stop-first inside a 1m bar"}
    for tf, mins in (("1m", 1), ("5m", 5), ("15m", 15), ("1h", 60)):
        hold = 8 * mins
        stride = max(5, mins)
        out["live_rule"][tf] = {"hold_minutes": hold, **{s: shares(close, high, low, hold, stride, s) for s in ("long", "short")}}
    for tf, mins in (("15m", 15), ("1h", 60)):
        hold = 100 * mins
        out["backtest_rsi_rule"][tf] = {"hold_minutes": hold, **{s: shares(close, high, low, hold, 180, s) for s in ("long", "short")}}
    pc.OUT.mkdir(parents=True, exist_ok=True)
    (pc.OUT / "exit_result.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
