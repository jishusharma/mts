"""Eagle_Eyes multi-timeframe bias ladder for BTCUSDT (public Binance spot data, observation only).
Per timeframe: last closed candle colour, forming candle colour, Malkan RSI(14) zone (40-60 only), %B of Bollinger 20/2.
2d, 4d and 5d are OURS: built from 1d candles, bars end on today (the forming bar holds today), not exchange candles."""
import json, sys, urllib.request, datetime as dt

UA = {"User-Agent": "Mozilla/5.0"}
BASE = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={}&limit={}"


def get(itv, n=400):
    return json.load(urllib.request.urlopen(urllib.request.Request(BASE.format(itv, n), headers=UA), timeout=20))


def agg(daily, n):
    out, i = [], len(daily)
    while i > 0:
        chunk = daily[max(0, i - n):i]
        out.append([chunk[0][0], chunk[0][1], max(x[2] for x in chunk), min(x[3] for x in chunk), chunk[-1][4]])
        i -= n
    return out[::-1]


def rsi(c, n=14):
    if len(c) < n + 2:
        return None
    g = [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]
    l = [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n]) / n, sum(l[:n]) / n
    out = [100 - 100 / (1 + ag / al) if al else 100]
    for i in range(n, len(g)):
        ag, al = (ag * (n - 1) + g[i]) / n, (al * (n - 1) + l[i]) / n
        out.append(100 - 100 / (1 + ag / al) if al else 100)
    return out


def pctb(c):
    w = c[-20:]
    m = sum(w) / len(w)
    sd = (sum((x - m) ** 2 for x in w) / len(w)) ** 0.5
    return (c[-1] - (m - 2 * sd)) / (4 * sd) if sd else float("nan")


def row(name, k):
    o = [float(x[1]) for x in k]; h = [float(x[2]) for x in k]; l = [float(x[3]) for x in k]; c = [float(x[4]) for x in k]
    col = lambda i: "GREEN" if c[i] > o[i] else "RED"
    r = rsi(c)
    zone = "n/a"
    held = ""
    if r:
        z = r[-1]
        zone = "bull>60" if z > 60 else ("bear<40" if z < 40 else "range40-60")
        last5 = r[-6:-1]
        held = "dipped<40 recently" if min(last5) < 40 <= z else ("popped>60 recently" if max(last5) > 60 >= z else "")
    return {"tf": name, "last_closed": f"{col(-2)} {(c[-2]/o[-2]-1)*100:+.2f}%", "forming": f"{col(-1)} {(c[-1]/o[-1]-1)*100:+.2f}%",
            "rsi": f"{r[-1]:.1f}" if r else "n/a", "zone": zone, "note": held, "pctB": f"{pctb(c):.2f}"}


def main():
    d1 = get("1d", 600)
    sets = [("1w", get("1w")), ("5d*", agg(d1, 5)), ("4d*", agg(d1, 4)), ("3d", get("3d")), ("2d*", agg(d1, 2)), ("1d", d1),
            ("12h", get("12h")), ("8h", get("8h")), ("4h", get("4h")), ("2h", get("2h")), ("1h", get("1h")), ("30m", get("30m")),
            ("15m", get("15m")), ("5m", get("5m")), ("3m", get("3m"))]
    print(f"BTCUSDT {dt.datetime.now(dt.UTC):%Y-%m-%d %H:%MZ}  (* = OURS, built from 1d)")
    print(f"{'tf':5s} {'last closed':14s} {'forming':14s} {'RSI':>5s} {'zone':11s} {'pctB':>5s}  note")
    for n, k in sets:
        r = row(n, k)
        print(f"{r['tf']:5s} {r['last_closed']:14s} {r['forming']:14s} {r['rsi']:>5s} {r['zone']:11s} {r['pctB']:>5s}  {r['note']}")


if __name__ == "__main__":
    main()
