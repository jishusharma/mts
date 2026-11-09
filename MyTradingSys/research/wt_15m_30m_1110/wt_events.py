"""Measure WaveTrend (LazyBear: n1=10, n2=21, wt2=sma4) events on Binance spot BTCUSDT 15m/30m, last ~180 days.
Events: strong up cross (wt1<=-53), strong down cross (wt1>=53), zero-line hold (up cross with wt1 in [-15, 5] after wt1 was >= 20
within the last 12 bars), oscillator higher low (up cross below 0 whose wt1 is higher than the previous up cross below 0).
Forward: close-to-close return after H bars; share up; vs all bars (baseline). Also: does 30m state agree?"""
import json, sys, time, urllib.request
import statistics as st

def get(tf, days):
    out, end = [], int(time.time() * 1000)
    ms = {'15m': 900000, '30m': 1800000}[tf]
    start = end - days * 86400000
    t = start
    while t < end:
        u = f'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={tf}&startTime={t}&limit=1000'
        rows = json.load(urllib.request.urlopen(u, timeout=30))
        if not rows: break
        out += rows; t = rows[-1][0] + ms
    return out

def ema(xs, n):
    a, e, o = 2 / (n + 1), None, []
    for x in xs:
        e = x if e is None else a * x + (1 - a) * e; o.append(e)
    return o

def wt(rows):
    ap = [(float(r[2]) + float(r[3]) + float(r[4])) / 3 for r in rows]
    esa = ema(ap, 10); d = ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    ci = [(a - e) / (0.015 * dd) if dd else 0 for a, e, dd in zip(ap, esa, d)]
    w1 = ema(ci, 21)
    w2 = [st.mean(w1[max(0, i - 3):i + 1]) for i in range(len(w1))]
    return w1, w2

def run(tf, H):
    rows = get(tf, 180); c = [float(r[4]) for r in rows]
    w1, w2 = wt(rows); W = 100
    ev = {'strong_up_x': [], 'strong_dn_x': [], 'zero_hold_up': [], 'osc_higher_low_up': [], 'any_up_x': [], 'any_dn_x': []}
    prev_low_x = None
    for i in range(W, len(c) - H):
        up = w1[i] > w2[i] and w1[i - 1] <= w2[i - 1]
        dn = w1[i] < w2[i] and w1[i - 1] >= w2[i - 1]
        r = c[i + H] / c[i] - 1
        if up: ev['any_up_x'].append(r)
        if dn: ev['any_dn_x'].append(r)
        if up and w1[i] <= -53: ev['strong_up_x'].append(r)
        if dn and w1[i] >= 53: ev['strong_dn_x'].append(r)
        if up and -15 <= w1[i] <= 5 and max(w1[i - 12:i]) >= 20: ev['zero_hold_up'].append(r)
        if up and w1[i] < 0:
            if prev_low_x is not None and w1[i] > prev_low_x: ev['osc_higher_low_up'].append(r)
            prev_low_x = w1[i]
    base = [c[i + H] / c[i] - 1 for i in range(W, len(c) - H)]
    res = {'tf': tf, 'H_bars': H, 'bars': len(c), 'from': time.strftime('%Y-%m-%d', time.gmtime(rows[0][0] / 1000)),
           'base_up_share': round(sum(x > 0 for x in base) / len(base), 3), 'base_mean_bp': round(st.mean(base) * 1e4, 1)}
    for k, v in ev.items():
        res[k] = {'n': len(v), 'up_share': round(sum(x > 0 for x in v) / len(v), 3) if v else None,
                  'mean_bp': round(st.mean(v) * 1e4, 1) if v else None, 'median_bp': round(st.median(v) * 1e4, 1) if v else None}
    return res

if __name__ == '__main__':
    for tf, H in (('15m', 8), ('15m', 16), ('30m', 4), ('30m', 8)):
        print(json.dumps(run(tf, H)))
