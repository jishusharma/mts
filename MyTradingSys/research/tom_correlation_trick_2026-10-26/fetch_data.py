"""Fetch daily history for the TOM-CTX-DIV test and write a data audit. Public market data only.

Usage: python fetch_data.py   -> writes data/*.csv (gitignored size small, but kept out of git) and AUDIT.txt
"""
import csv
import datetime as dt
import json
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
H = {"User-Agent": "Mozilla/5.0"}
YAHOO = {"DAX": "%5EGDAXI", "ES": "ES%3DF", "NIKKEI": "%5EN225", "NQ": "NQ%3DF", "DXY": "DX-Y.NYB"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60))


def yahoo(sym):
    d = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1500000000&period2=1793000000&interval=1d")
    r = d["chart"]["result"][0]
    ts, q = r["timestamp"], r["indicators"]["quote"][0]
    out = []
    for i, t in enumerate(ts):
        if q["close"][i] is None or q["open"][i] is None:
            continue
        out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(),
                    q["open"][i], q["close"][i]))
    return out


def btc():
    out, start = [], 1500000000000
    while True:
        k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&startTime={start}")
        if not k:
            break
        for x in k:
            out.append((dt.datetime.fromtimestamp(x[0] / 1000, dt.timezone.utc).date().isoformat(),
                        float(x[1]), float(x[4])))
        start = k[-1][0] + 86400000
        if len(k) < 1000:
            break
    return out


def main():
    DATA.mkdir(exist_ok=True)
    lines = []
    sets = {n: yahoo(s) for n, s in YAHOO.items()}
    sets["BTC"] = btc()
    for n, rows in sets.items():
        with open(DATA / f"{n}.csv", "w", newline="\n") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "close"])
            w.writerows(rows)
        lines.append(f"{n}: n={len(rows)} first={rows[0][0]} last={rows[-1][0]} bar=1d")
    (HERE / "AUDIT.txt").write_text("\n".join(lines) + "\n", newline="\n") if False else \
        open(HERE / "AUDIT.txt", "w", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
