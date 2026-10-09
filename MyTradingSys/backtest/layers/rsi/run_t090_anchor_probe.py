"""T090: anchor robustness of the 7h operator bullish RSI-divergence lead (T088). Shifts 1m bars by -offset h, resamples
with the registry rule (7h day-reset, 6h, 8h), scores with run_divergence_mtf.run_tf. BTCUSDT only (no other symbol on disk)."""
import json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.bt.bt_data import load_klines
from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
from MyTradingSys.backtest.layers.rsi import run_divergence_mtf as R

def main(out):
    reg = json.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
    mp = json.loads(R.PARAMS_PATH.read_text(encoding="utf-8"))
    taker = R.load_taker()
    root = REPO.parent / "BinanceDataFeed" / "Dumps" / "backtest"
    bars = load_klines(str(root / "raw_1m_2022"))
    last = bars[-1]["t"]
    bars += [b for b in load_klines(str(root / "raw")) if b["t"] > last]
    bars.sort(key=lambda b: b["t"])
    jobs = [("7h", h) for h in (0, 18, 22, 23, 3, 5, 12)] + [("6h", h) for h in range(6)] + [("8h", h) for h in (0, 1, 2, 4, 6)]
    res = {}
    for tf, h in jobs:
        sh = h * 3600000
        shifted = [dict(b, t=b["t"] - sh) for b in bars]
        rb = resample(shifted, tf, reg)
        r = R.run_tf(rb, mp, taker, False)
        c = r["columns"]["operator"]["bullish"]
        res["%s@%02d" % (tf, h)] = {"n_bars": r["n_bars"], "op_bull": c}
        print(tf, h, c.get("n_events"), json.dumps({k: c[k] for k in c if k in ("verdict",)}), flush=True)
    Path(out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
if __name__ == "__main__":
    main(sys.argv[1])
