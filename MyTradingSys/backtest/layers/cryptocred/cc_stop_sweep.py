"""CryptoCred stop-rule sweep - D20/B143. Resumable matrix driver."""
import os
import sys
import json
import time
from pathlib import Path
sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R
from MyTradingSys.backtest.layers.cryptocred.cc_setups import _r_target

ROOT1 = "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1m_2022"
ROOT2 = "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw"
OUT = Path("MyTradingSys/research/cryptocred_stop_2026-10-10/stop_sweep_result.json")
TF_MS = 3600000
BUDGET = 140.0

RULES = {
    "pct_0.1": ("NO-SOURCE", 0.001),
    "pct_0.25": ("NO-SOURCE", 0.0025),
    "pct_0.5": ("NO-SOURCE", 0.005),
    "pct_1.0": ("NO-SOURCE", 0.01),
    "atr_1.0": ("CC-invalidation", 1.0),
    "atr_2.0": ("CC-invalidation", 2.0),
}
SETUPS = ["setup1_sr_flip", "setup2_fib_pullback", "setup3_failed_msb_reversal"]
RULE_ORDER = ["pct_0.1", "pct_0.5", "atr_1.0", "atr_2.0"]


def atr_wilder(bars, n=14):
    out = [None] * len(bars)
    if len(bars) <= n + 1:
        return out
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i]["h"], bars[i]["l"], bars[i - 1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    a = sum(trs[:n]) / n
    out[n] = a
    for i in range(n + 1, len(bars)):
        a = (a * (n - 1) + trs[i - 1]) / n
        out[i] = a
    return out


def resweep(signals, bars, rule, param, atr):
    out = []
    for s in signals:
        e = s["entry_price"]
        side = s["side"]
        if rule.startswith("pct"):
            stop = e * (1 - param) if side == "long" else e * (1 + param)
        else:
            i = next((k for k, b in enumerate(bars) if b["t"] == s["entry_t"]), 0)
            a = atr[i] if (atr and i < len(atr) and atr[i]) else (e * 0.004)
            d = param * a
            stop = e - d if side == "long" else e + d
        s2 = dict(s)
        s2["stop"] = stop
        s2["targets"] = [(_r_target(e, stop, side, s["meta"]["target_r"]), 1.0)]
        out.append(s2)
    return out


def main():
    t0 = time.time()
    rows = json.loads(OUT.read_text(encoding="utf-8-sig")) if OUT.exists() else []
    done = {(r["setup"], r["rule"]) for r in rows}
    todo = [(s, r) for s in SETUPS for r in RULE_ORDER if (s, r) not in done]
    if not todo:
        print("ALL DONE", len(rows))
        os._exit(0)
    bars_1m, tf_bars, funding = R.load_data(ROOT1, ROOT2, "1h")
    atr = atr_wilder(tf_bars, 14)
    cache = {}
    for s, r in todo:
        if time.time() - t0 > BUDGET:
            print("budget stop", flush=True)
            break
        if s not in cache:
            cache[s] = R.SETUPS[s](tf_bars)
        tag, param = RULES[r]
        sigs = resweep(cache[s], tf_bars, r, param, atr)
        trades = R.build_trades(sigs, bars_1m, funding, "all_taker", TF_MS, max_bars=1440)
        if not trades:
            rows.append({"setup": s, "rule": r, "src": tag, "n": 0, "net_r": None, "hit": None})
        else:
            rs = [t["net_r"] for t in trades]
            rows.append({"setup": s, "rule": r, "src": tag, "n": len(trades),
                         "net_r": sum(rs) / len(rs), "hit": sum(1 for x in rs if x > 0) / len(rs)})
        OUT.write_text(json.dumps(rows, indent=1), encoding="utf-8", newline="\n")
        print("done", s, r, "elapsed", int(time.time() - t0), flush=True)
    for r in rows:
        print("{setup:26} {rule:9} {src:15} n={n:4} net_r={net_r} hit={hit}".format(**r), flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
