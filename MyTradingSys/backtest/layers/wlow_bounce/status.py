"""Read-only status of the weekly-low bounce setup from PUBLIC Binance USD-M klines. OBSERVATION ONLY: no orders, no keys, no account data.

  python -m MyTradingSys.backtest.layers.wlow_bounce.status [--log PATH] [--json]

Prints IDLE / ARMED / ACTIVE (closed 1h candles) plus current RSI, upper BB gap, prior weekly low, and the flow readings
(net delta of the last K bars, episode CVD change, open interest level and change over the last K hours). OI has no DEV history, so
it is a live-tracking field only; with --log each ARMED/ACTIVE reading is appended (jsonl) so a forward sample builds
(keep the log under a git-ignored path; the repo is public).
Setup is UNVALIDATED: research/wlow_bounce_bbrsi60_2026-10-16/RESULT.md (INCONCLUSIVE, n=8 on DEV).
"""
import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.wlow_bounce import detector as D

BASE = "https://fapi.binance.com"


def _get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as r:
        return json.loads(r.read().decode())


def fetch_candles(now_ms=None, limit=500):
    """Closed 1h candles only (drops the forming bar)."""
    now_ms = now_ms or int(time.time() * 1000)
    rows = _get("/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=%d" % limit)
    return [{"t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5]), "tbv": float(r[9])}
            for r in rows if int(r[6]) < now_ms]


def fetch_oi(k):
    """(current OI in coins, OI change vs k hourly points ago) from public endpoints; (None, None) on any error."""
    try:
        cur = float(_get("/fapi/v1/openInterest?symbol=BTCUSDT")["openInterest"])
        hist = _get("/futures/data/openInterestHist?symbol=BTCUSDT&period=1h&limit=%d" % (k + 1))
        chg = cur - float(hist[0]["sumOpenInterest"]) if len(hist) >= k + 1 else None
        return cur, chg
    except Exception:
        return None, None


def report(candles, oi=(None, None), p=D.PARAMS):
    st = D.status_now(candles, p)
    bb, rsi = D.indicators(candles, p)
    i = len(candles) - 1
    K = p["K"]
    out = {"asof_bar_open": datetime.fromtimestamp(candles[i]["t"] / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "state": st["state"], "close": candles[i]["c"], "rsi14": rsi[i], "bb_upper": bb[i],
           "gap_to_upper_pct": (candles[i]["c"] / bb[i] - 1) * 100 if bb[i] else None,
           "net_delta_last_K": D.delta_sum(candles, i - K + 1, i), "oi_now": oi[0], "oi_change_last_K_h": oi[1]}
    e = st["event"]
    if e and st["state"] in ("ARMED", "ACTIVE"):
        out["prior_weekly_low"] = e["W"]
        out["break_bar"] = candles[e["start"]]["t"]
        out["bounce_bar"] = candles[e["bounce"]]["t"] if e["bounce"] is not None else None
        out["trigger_bar"] = candles[e["trigger"]]["t"] if e["trigger"] is not None else None
        out["episode_cvd_change"] = D.delta_sum(candles, e["start"], i)
        out["phase"] = e["status"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--log")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    candles = fetch_candles()
    r = report(candles, fetch_oi(D.PARAMS["K"]))
    if a.log and r["state"] in ("ARMED", "ACTIVE"):
        with open(a.log, "a", newline="\n") as f:
            f.write(json.dumps(r) + "\n")
    if a.json:
        print(json.dumps(r))
    else:
        print("wlow-bounce status (observation only, UNVALIDATED): %s" % r["state"])
        for k, v in r.items():
            if k != "state":
                print("  %s: %s" % (k, round(v, 3) if isinstance(v, float) else v))


if __name__ == "__main__":
    main()
