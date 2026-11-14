"""Fetch public daily klines: Binance SPOT (data-api.binance.vision, 2017-08+) and Bybit linear BTCUSDT (2020+).
Writes data/binance_spot_1d.csv and data/bybit_1d.csv (git-ignored). Pre-2017 history comes from the repo's
research/btc_cycles_2026-11/btc_daily.csv (blockchain.info index, high/low/close only)."""
import csv, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def get(url):
    for i in range(4):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=30).read())
        except Exception as e:  # network flake: retry
            err = e
            time.sleep(2)
    raise err


def binance():
    rows, start = [], 1502928000000  # 2017-08-17
    while True:
        k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&startTime={start}")
        if not k:
            break
        rows += [(int(x[0]), x[1], x[2], x[3], x[4], x[5]) for x in k]
        start = int(k[-1][0]) + 86400000
        if len(k) < 1000:
            break
    return rows


def bybit():
    rows, end = [], int(time.time() * 1000)
    while True:
        j = get(f"https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=D&limit=1000&end={end}")
        k = j["result"]["list"]
        if not k:
            break
        rows += [(int(x[0]), x[1], x[2], x[3], x[4], x[5]) for x in k]
        end = int(k[-1][0]) - 1
        if len(k) < 1000:
            break
    return sorted(set(rows))


def save(name, rows):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts_ms", "open", "high", "low", "close", "volume"])
        w.writerows(rows)
    print(name, len(rows), rows[0][0], rows[-1][0])


if __name__ == "__main__":
    save("binance_spot_1d.csv", binance())
    save("bybit_1d.csv", bybit())
