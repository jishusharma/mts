"""Hand recorder for the 2026-11-13 US session (stop-gap until us_open_trader/recorder.py ships).

Public market data only, stdlib only. Appends one JSON line per reading to the git-ignored file
<repo>/runtime_data/us_open_trader/readings_<day>.jsonl. Cadence (OURS, operator order 2026-11-13): every 15 min
from the start, every minute from 15 min before the US cash open until 2 h after it, then every 15 min to 21:00Z.
Every venue call is independent: a failed call is recorded as {"error": ...}, never invented.
Not recorded (gaps): liquidations (no public REST feed; CoinGlass needs a browser, Chrome tools are off).

  python record_now.py [--open 14:30] [--until 21:00] [--once]
"""
import sys
sys.dont_write_bytecode = True

import argparse
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "runtime_data" / "us_open_trader"
LEVELS = [67568, 68000, 68100, 68120, 68490, 68516, 69000, 69571, 69620, 69846, 69980, 70000, 71113]  # PLAN_US_OPEN_2026-11-13.md


def get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "mts-recorder"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def safe(fn):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001 - a venue that does not answer is a recorded gap
        return {"error": repr(e)[:160]}


def rsi(closes, n=14):
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        ag, al = (ag * (n - 1) + g) / n, (al * (n - 1) + l) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)


def bb(closes, n=20, k=2):
    w = closes[-n:]
    m = sum(w) / n
    sd = (sum((x - m) ** 2 for x in w) / n) ** 0.5
    return {"mid": round(m, 1), "up": round(m + k * sd, 1), "lo": round(m - k * sd, 1),
            "width_pct": round(2 * k * sd / m * 100, 3)}


def ind(closes):
    return {"rsi14": round(rsi(closes), 1), "bb20": bb(closes), "close": closes[-1]}


def bybit():
    t = get("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")["result"]["list"][0]
    r = get("https://api.bybit.com/v5/market/account-ratio?category=linear&symbol=BTCUSDT&period=5min&limit=1")
    r = (r["result"]["list"] or [{}])[0]
    return {"last": float(t["lastPrice"]), "mark": float(t["markPrice"]), "oi_btc": float(t["openInterest"]),
            "oi_usd": float(t["openInterestValue"]), "funding": float(t["fundingRate"]),
            "vol24h_btc": float(t["volume24h"]), "long_share": float(r.get("buyRatio", "nan")),
            "short_share": float(r.get("sellRatio", "nan"))}


def bybit_k(interval):
    rows = get(f"https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval={interval}&limit=120")
    rows = sorted(rows["result"]["list"], key=lambda x: int(x[0]))[:-1]   # closed bars only
    return ind([float(x[4]) for x in rows])


def binance_spot_1m(limit=20):
    rows = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit={limit}")
    return [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4]),
             "vol": float(x[5]), "delta": 2 * float(x[9]) - float(x[5])} for x in rows[:-1]]   # closed bars


def okx():
    oi = get("https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP")["data"][0]
    fr = get("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP")["data"][0]
    return {"oi_btc": float(oi["oiCcy"]), "funding": float(fr["fundingRate"])}


def deribit():
    d = get("https://www.deribit.com/api/v2/public/get_book_summary_by_instrument?instrument_name=BTC-PERPETUAL")
    d = d["result"][0]
    return {"mark": d.get("mark_price"), "oi_usd": d.get("open_interest"), "funding_8h": d.get("funding_8h"),
            "vol24h_usd": d.get("volume_usd")}


def reading(state):
    now = datetime.now(timezone.utc)
    rec = {"ts_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "kind": "reading", "src": "record_now.py"}
    bars = safe(lambda: binance_spot_1m(20))
    if isinstance(bars, list) and bars:
        new = [b for b in bars if b["t"] > state.get("last_t", 0)]
        if not state.get("last_t"):
            new = bars[-1:]
        state["last_t"] = bars[-1]["t"]
        state["cvd"] = state.get("cvd", 0.0) + sum(b["delta"] for b in new)
        hi, lo = max(b["h"] for b in new or bars[-1:]), min(b["l"] for b in new or bars[-1:])
        rec["binance_spot"] = {"price": bars[-1]["c"], "hi_since_last": hi, "lo_since_last": lo,
                               "vol_btc_since_last": round(sum(b["vol"] for b in new), 3),
                               "net_delta_btc_since_last": round(sum(b["delta"] for b in new), 3),
                               "cvd_btc_since_start": round(state["cvd"], 3), "bars": len(new)}
        rec["levels_touched"] = [lv for lv in LEVELS if lo <= lv <= hi]
    else:
        rec["binance_spot"] = bars
    rec["bybit"] = safe(bybit)
    rec["bybit_1m"] = safe(lambda: bybit_k("1"))
    rec["bybit_15m"] = safe(lambda: bybit_k("15"))
    rec["okx"] = safe(okx)
    rec["deribit"] = safe(deribit)
    rec["gaps"] = ["liquidations: no public REST feed", "coinglass: needs a browser"]
    return rec


def next_due(now, open_dt):
    fast_from, fast_to = open_dt - timedelta(minutes=15), open_dt + timedelta(hours=2)
    step = 1 if fast_from <= now < fast_to else 15
    nxt = now.replace(second=5, microsecond=0) + timedelta(minutes=step - now.minute % step)
    return min(nxt, fast_from.replace(second=5)) if now < fast_from < nxt else nxt


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", default="14:30")
    ap.add_argument("--until", default="21:00")
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    hm = lambda s: now.replace(hour=int(s[:2]), minute=int(s[3:]), second=0, microsecond=0)  # noqa: E731
    open_dt, until = hm(a.open), hm(a.until)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"readings_{now:%Y-%m-%d}.jsonl"
    state = {}
    while True:
        rec = reading(state)
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec) + "\n")
        b = rec.get("bybit") or {}
        print(rec["ts_utc"], (rec.get("binance_spot") or {}).get("price"), "oi", b.get("oi_btc"),
              "touched", rec.get("levels_touched"), flush=True)
        now = datetime.now(timezone.utc)
        if a.once or now >= until:
            return 0
        time.sleep(max(1.0, (next_due(now, open_dt) - datetime.now(timezone.utc)).total_seconds()))


if __name__ == "__main__":
    sys.exit(main())
