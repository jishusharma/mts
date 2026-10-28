import sys
sys.dont_write_bytecode = True
"""
MyTradingSys/backtest/fetch_bars.py  (T051 step B1)

Run on the DESKTOP (needs internet; the AI bridge and cloud workspace are
blocked from exchange hosts by policy, so this was syntax-checked only).

Pulls 1-minute bars for the archived snapshot period from:
  Binance USD-M futures BTCUSDT  (the prices MTS computes signals on)
  Deribit BTC-PERPETUAL mainnet  (the prices orders would fill on)
Writes Dumps/backtest/bars_binance_1m.json and bars_deribit_1m.json and
prints the Deribit-minus-Binance basis distribution.

Run: python MyTradingSys/backtest/fetch_bars.py
"""
import json, time, statistics as st, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Dumps" / "backtest"
MIN = 60_000


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MTS-T051-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def binance(start_ms, end_ms):
    bars, t = {}, start_ms
    while t < end_ms:
        url = ("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m"
               "&startTime=%d&endTime=%d&limit=1500" % (t, end_ms))
        k = get(url)
        if not k:
            break
        for b in k:
            bars[int(b[0])] = dict(t=int(b[0]), o=float(b[1]), h=float(b[2]), l=float(b[3]), c=float(b[4]), v=float(b[5]))
        nxt = int(k[-1][0]) + MIN
        if nxt <= t:
            break
        t = nxt
        time.sleep(0.25)
    return [bars[k] for k in sorted(bars)]


def deribit(start_ms, end_ms, instrument="BTC-PERPETUAL"):
    bars, t, win = {}, start_ms, 12 * 60 * MIN
    while t < end_ms:
        e = min(t + win, end_ms)
        url = ("https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name=%s"
               "&start_timestamp=%d&end_timestamp=%d&resolution=1" % (instrument, t, e))
        r = get(url).get("result") or {}
        if r.get("status") == "ok":
            for i, ts in enumerate(r.get("ticks", [])):
                bars[int(ts)] = dict(t=int(ts), o=r["open"][i], h=r["high"][i], l=r["low"][i], c=r["close"][i], v=r["volume"][i])
        t = e
        time.sleep(0.25)
    return [bars[k] for k in sorted(bars)]


def main():
    rows = json.load(open(OUT / "replay_rows.json", encoding="utf-8"))
    start_ms = int(rows[0]["t"] * 1000) // MIN * MIN - 60 * MIN
    end_ms = int(rows[-1]["t"] * 1000) // MIN * MIN + 13 * 60 * MIN  # covers the 12 h trade timeout
    print("range", start_ms, "->", end_ms)
    b = binance(start_ms, end_ms)
    json.dump(b, open(OUT / "bars_binance_1m.json", "w", encoding="utf-8"))
    print("binance 1m bars:", len(b))
    d = deribit(start_ms, end_ms)
    json.dump(d, open(OUT / "bars_deribit_1m.json", "w", encoding="utf-8"))
    print("deribit 1m bars:", len(d))
    bi = {x["t"]: x["c"] for x in b}
    diffs = [x["c"] - bi[x["t"]] for x in d if x["t"] in bi]
    if diffs:
        diffs.sort()
        q = lambda p: diffs[int(p * (len(diffs) - 1))]
        print("basis Deribit-Binance close, USD: median %.1f  p5 %.1f  p95 %.1f  (n=%d)" % (st.median(diffs), q(0.05), q(0.95), len(diffs)))


if __name__ == "__main__":
    main()
