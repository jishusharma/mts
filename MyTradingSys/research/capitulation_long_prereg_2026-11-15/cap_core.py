"""Capitulation-long signal counter + power gate (no event outcomes are read here; see PRE_REG.md)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
import research_kit as rk

CACHE = Path("F:/MTS/data_cache/binance_spot")
COINS = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "LINK", "LTC", "AVAX"]
# OURS unless noted
ATR_N = 14          # SOURCED Wilder default
FLUSH_ATR = 2.0     # flush day return <= -2.0 x ATR%
VOL_X = 3.0         # day volume >= 3 x median of prior 20 days
VOL_N = 20
RED_K, RED_OF = 3, 4  # >=3 red days in last 4 (incl flush)
HOLD = 5            # exit close of day d+5 (entry open d+1)
STOP_ATR = 2.0
DEV_END = np.datetime64("2023-12-31")


def daily(coin):
    _z = np.load(CACHE / f"{coin}USDT_15m.npz")
    z = {k: _z[k] for k in _z.files}
    t = z["t"] if "t" in z else z["ts"]
    t = t // 1000 if t[0] > 1e11 else t
    day = (t // 86400).astype(np.int64)
    u, first = np.unique(day, return_index=True)
    last = np.r_[first[1:], len(day)]
    o = z["o"][first]; c = z["c"][last - 1]
    h = np.array([z["h"][a:b].max() for a, b in zip(first, last)])
    l = np.array([z["l"][a:b].min() for a, b in zip(first, last)])
    v = np.array([z["v"][a:b].sum() for a, b in zip(first, last)])
    n = last - first
    ok = n == 96
    return u, o, h, l, c, v, ok


def atr_pct(h, l, c):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    a = np.full(len(c), np.nan)
    if len(c) > ATR_N:
        a[ATR_N] = tr[1:ATR_N + 1].mean()
        for i in range(ATR_N + 1, len(c)):
            a[i] = (a[i - 1] * (ATR_N - 1) + tr[i]) / ATR_N
    return a / c


def signals(coin):
    u, o, h, l, c, v, ok = daily(coin)
    ap = atr_pct(h, l, c)
    out = []
    for d in range(max(VOL_N, ATR_N) + 2, len(c) - HOLD - 1):
        if not ok[d - VOL_N:d + 1].all() or u[d + 1] != u[d] + 1:
            continue
        ret = c[d] / c[d - 1] - 1
        red = sum(c[j] < o[j] for j in range(d - RED_OF + 1, d + 1))
        if ret <= -FLUSH_ATR * ap[d - 1] and v[d] >= VOL_X * np.median(v[d - VOL_N:d]) and red >= RED_K:
            out.append((coin, int(u[d]), d))
    return out


def fwd_sd(coin):
    """SD of unconditional HOLD-day close-to-close % return (all days): the noise level, not an event outcome."""
    u, o, h, l, c, v, ok = daily(coin)
    r = (c[HOLD + 1:] / c[1:-HOLD] - 1) * 100
    return r


def main():
    ev, sds = [], []
    for k in COINS:
        ev += signals(k); sds.append(fwd_sd(k))
    sd = float(np.concatenate(sds).std())
    dev_end = int(DEV_END.astype("datetime64[D]").astype(int))
    rows = {}
    for name, f in [("DEV", lambda d: d <= dev_end), ("VAL", lambda d: d > dev_end), ("ALL", lambda d: True)]:
        sel = [e for e in ev if f(e[1])]
        days = sorted({e[1] for e in sel})
        rows[name] = {"signals": len(sel), "distinct_days": len(days),
                      "per_coin": {k: sum(1 for e in sel if e[0] == k) for k in COINS}}
    out = {"coins": COINS, "sd_unconditional_5d_pct": sd, "split": rows}
    # power gate: n = distinct days (cross-coin events on one day are one cluster)
    for name in ("VAL", "ALL"):
        n = max(rows[name]["distinct_days"], 1)
        out["power_" + name] = {}
        for eff in (1.0, 2.0, 3.0):
            out["power_" + name][f"plausible_gross_{eff}pct"] = rk.power_check(n, sd, eff, cost=rk.TAKER_RT_PCT)
        out["power_" + name]["n_days_needed_for_2pct"] = int(np.ceil((rk.MDE_Z * sd / (2.0 - rk.TAKER_RT_PCT)) ** 2))
    Path(__file__).with_name("power_gate.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
