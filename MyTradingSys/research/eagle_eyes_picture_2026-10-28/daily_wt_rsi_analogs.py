"""Daily BTC WaveTrend + RSI analog study (Eagle_Eyes, 2026-10-29).

Data: Binance spot BTCUSDT 1d klines via data-api.binance.vision (public).
Formulas: WT per LazyBear WT_CROSS_LB (n1=10, n2=21, wt2=SMA(wt1,4));
RSI 14 Wilder, with SMA 14 of RSI. All thresholds are OURS, fixed before
looking at forward returns. Descriptive only: no fees, no edge claim.
"""
import json, math, sys, urllib.request, datetime as dt

URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&startTime={}"


def fetch():
    rows, start = [], 1502928000000  # 2017-08-17
    while True:
        k = json.load(urllib.request.urlopen(URL.format(start), timeout=30))
        if not k:
            break
        rows += k
        if len(k) < 1000:
            break
        start = k[-1][0] + 86400000
    return rows


def ema(xs, n):
    a, out, e = 2 / (n + 1), [], None
    for x in xs:
        e = x if e is None else a * x + (1 - a) * e
        out.append(e)
    return out


def sma(xs, n):
    out = []
    for i in range(len(xs)):
        w = xs[max(0, i - n + 1):i + 1]
        out.append(sum(w) / len(w))
    return out


def wavetrend(h, l, c):
    ap = [(a + b + d) / 3 for a, b, d in zip(h, l, c)]
    esa = ema(ap, 10)
    d = ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    ci = [(a - e) / (0.015 * dd) if dd else 0 for a, e, dd in zip(ap, esa, d)]
    wt1 = ema(ci, 21)
    return wt1, sma(wt1, 4)


def rsi(c, n=14):
    out, ag, al = [50.0] * len(c), 0.0, 0.0
    for i in range(1, len(c)):
        ch = c[i] - c[i - 1]
        g, lo = max(ch, 0), max(-ch, 0)
        if i <= n:
            ag += g / n
            al += lo / n
        else:
            ag = (ag * (n - 1) + g) / n
            al = (al * (n - 1) + lo) / n
        out[i] = 100 - 100 / (1 + ag / al) if al else 100
    return out


def fwd(c, i, k):
    return (c[i + k] / c[i] - 1) * 100 if i + k < len(c) else None


def main():
    k = fetch()
    t = [dt.datetime.fromtimestamp(x[0] / 1000, dt.UTC).date().isoformat() for x in k]
    h, l, c = ([float(x[j]) for x in k] for j in (2, 3, 4))
    wt1, wt2 = wavetrend(h, l, c)
    r = rsi(c)
    rs = sma(r, 14)
    n = len(c)
    now = n - 1
    print(f"bars {n} {t[0]}..{t[-1]}  NOW wt1={wt1[now]:.1f} wt2={wt2[now]:.1f} rsi={r[now]:.1f} rsiSMA={rs[now]:.1f} close={c[now]:.0f}")
    print(f"  last 20 wt1: {[round(x) for x in wt1[-20:]]}")
    print(f"  max wt1 last 15={max(wt1[-15:]):.0f}  max wt1 last 60={max(wt1[-60:]):.0f}")

    def cross_dn(i, look=3):
        return any(wt1[j] < wt2[j] and wt1[j - 1] >= wt2[j - 1] for j in range(i - look + 1, i + 1))

    tiers = {
        "loose": lambda i: -50 <= wt1[i] <= -25 and wt1[i] < wt2[i] and cross_dn(i) and 36 <= r[i] <= 48 and r[i] < rs[i],
        "strict": lambda i: -50 <= wt1[i] <= -25 and wt1[i] < wt2[i] and cross_dn(i) and 36 <= r[i] <= 48 and r[i] < rs[i]
        and max(wt1[i - 14:i + 1]) < 0 and max(wt1[i - 59:i + 1]) > 30,
    }
    res = {}
    for name, f in tiers.items():
        ev, last = [], -99
        for i in range(80, n - 1):
            if f(i) and i - last >= 10:
                ev.append(i)
                last = i
        rows = []
        for i in ev:
            mn = min(wt1[i:i + 21]) if i + 20 < n else None
            dd = min(l[i + 1:i + 21]) / c[i] * 100 - 100 if i + 20 < n else None
            ru = max(h[i + 1:i + 21]) / c[i] * 100 - 100 if i + 20 < n else None
            rows.append(dict(date=t[i], close=round(c[i]), wt1=round(wt1[i]), rsi=round(r[i], 1),
                             f5=fwd(c, i, 5), f10=fwd(c, i, 10), f20=fwd(c, i, 20), f30=fwd(c, i, 30),
                             wt_min20=None if mn is None else round(mn), dd20=dd, ru20=ru))
        res[name] = rows
        done = [x for x in rows if x["f20"] is not None]
        print(f"\n[{name}] events={len(rows)} with 20d outcome={len(done)}")
        for key in ("f5", "f10", "f20", "f30"):
            v = sorted(x[key] for x in rows if x[key] is not None)
            if v:
                med = v[len(v) // 2]
                up = sum(1 for x in v if x > 0)
                print(f"  {key}: median {med:+.1f}%  up {up}/{len(v)}")
        if done:
            reach = sum(1 for x in done if x["wt_min20"] <= -53)
            print(f"  WT reached <= -53 within 20d: {reach}/{len(done)}; median dd20 {sorted(x['dd20'] for x in done)[len(done)//2]:.1f}%  median ru20 {sorted(x['ru20'] for x in done)[len(done)//2]:.1f}%")
        for x in rows:
            fmt = lambda v: "  n/a" if v is None else f"{v:+5.1f}"
            print(f"   {x['date']} c{x['close']:>6} wt{x['wt1']:>4} rsi{x['rsi']:>5}  5d{fmt(x['f5'])} 10d{fmt(x['f10'])} 20d{fmt(x['f20'])} 30d{fmt(x['f30'])}  wtmin{x['wt_min20']}")

    # fractal nearest neighbours: last 30 bars of wt1, rsi and price path
    L = 30
    def vec(i):
        base = c[i]
        return [wt1[j] / 60 for j in range(i - L + 1, i + 1)] + [(r[j] - 50) / 20 for j in range(i - L + 1, i + 1)] + \
               [(c[j] / base - 1) * 10 for j in range(i - L + 1, i + 1)]
    cur = vec(now)
    cands = []
    for i in range(80, n - 31):
        v = vec(i)
        cands.append((math.sqrt(sum((a - b) ** 2 for a, b in zip(cur, v))), i))
    cands.sort()
    picked = []
    for dist, i in cands:
        if all(abs(i - j) >= 20 for _, j in picked):
            picked.append((dist, i))
        if len(picked) == 10:
            break
    print("\n[fractal top 10, last 30 bars of WT+RSI+price shape]")
    fr = []
    for dist, i in picked:
        row = dict(date=t[i], dist=round(dist, 2), wt1=round(wt1[i]), rsi=round(r[i], 1), f10=fwd(c, i, 10), f20=fwd(c, i, 20), f30=fwd(c, i, 30))
        fr.append(row)
        print(f"   {row['date']} dist{row['dist']:>5} wt{row['wt1']:>4} rsi{row['rsi']:>5} 10d{row['f10']:+5.1f} 20d{row['f20']:+5.1f} 30d{row['f30']:+5.1f}")
    for key in ("f10", "f20", "f30"):
        v = sorted(x[key] for x in fr)
        print(f"  {key}: median {v[len(v)//2]:+.1f}%  up {sum(1 for x in v if x > 0)}/{len(v)}")
    res["fractal"] = fr
    res["now"] = dict(date=t[now], wt1=wt1[now], wt2=wt2[now], rsi=r[now], rsi_sma=rs[now], close=c[now],
                      wt1_last60=[round(x, 1) for x in wt1[-60:]], rsi_last60=[round(x, 1) for x in r[-60:]], close_last60=c[-60:], dates_last60=t[-60:])
    if len(sys.argv) > 1:
        json.dump(res, open(sys.argv[1], "w", newline="\n"), indent=1)


if __name__ == "__main__":
    main()
