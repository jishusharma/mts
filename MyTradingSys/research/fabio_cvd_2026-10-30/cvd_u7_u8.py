"""U7 + U8: two Fabio CVD claims on BTC 1m taker delta. Descriptive, DEV only (2022-01-01..2024-06-30), no fees, no edge claim.
Definitions fixed before the first run (all OURS unless noted):
- Data: Binance USD-M BTCUSDT 1m (F:/MTS/data/tom_raw/klines), DEV months only; files after 2024-06 are never opened.
- Delta per 1m bar = 2 * taker_buy_volume - volume (BTC). CVD = running sum of delta.
U7 (F-CVD2 in a coil): events = pre_us_squeeze_2026-10-29/study.py definitions (box A-8h..A, BB(20,2) 15m BW percentile
  vs prior 30 days, squeeze <= 20% = the C17 coil). Box CVD = sum of 1m delta over the box. Break side = first 15m bar in
  A..A+4h whose high/low leaves the box. Split by sign of box CVD; also the strong third (|box CVD| / box volume top 33%).
U8 (F-CVD3 absorption): 15m bars; swing low = low strictly below the lows of K=2 bars each side. Pair each swing low with
  the previous swing low within 24h (96 bars). Equal low = |low - prev low| / prev low <= 0.1% (SOURCED: card U8).
  CVD at a low = CVD at the close of that 15m bar. Divergence = equal low AND CVD lower than at the prior low.
  Control = equal low with CVD equal or higher; reported raw and re-weighted to the divergence distance bins (thirds of 0.1%).
  Reference = close of the confirming bar (low bar + K). Over the next 4h (16 bars):
  REVERSAL = the window never trades below the pair's lower low AND the 4h close is above the reference.
  Also: low broken (window low < pair's lower low), mean 4h return.
"""
import glob, csv, datetime as dt, collections, statistics as st, sys, os

K, TOL, GAP, FWD = 2, 0.001, 96, 16
DEV_LAST = '2024-06'
P = 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'


def dev_files():
    out = []
    for f in sorted(glob.glob(P)):
        tag = os.path.basename(f)[len('BTCUSDT-1m-'):-4][:7]
        if tag <= DEV_LAST: out.append(f)
    return out


def load_15m(files):
    """15m bars as dict t -> [o, h, l, c, delta, volume]."""
    b = {}
    for f in files:
        for r in csv.reader(open(f)):
            if r[0] == 'open_time': continue
            t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
            if t >= 1719792000: continue  # 2024-07-01T00:00Z: DEV end guard
            k = t - t % 900; o, h, l, c, v = map(float, r[1:6]); d = 2 * float(r[9]) - v
            x = b.get(k)
            if x: x[1] = max(x[1], h); x[2] = min(x[2], l); x[3] = c; x[4] += d; x[5] += v
            else: b[k] = [o, h, l, c, d, v]
    return b


def find_equal_lows(bars, k=K, tol=TOL, gap=GAP):
    """bars: list of (t, o, h, l, c, delta), contiguous 15m. Returns one dict per equal-low pair with div flag."""
    lows = [x[3] for x in bars]; cvd = []; s = 0.0
    for x in bars: s += x[5]; cvd.append(s)
    sw = [i for i in range(k, len(bars) - k)
          if all(lows[i] < lows[j] for j in range(i - k, i + k + 1) if j != i)]
    out = []
    for a, b in zip(sw, sw[1:]):
        if b - a > gap: continue
        dist = abs(lows[b] - lows[a]) / lows[a]
        if dist > tol: continue
        out.append(dict(i=b, prev=a, dist=dist, div=cvd[b] < cvd[a], floor=min(lows[a], lows[b])))
    return out


def u8(b):
    ts = sorted(b); rows = []
    seg = [ts[0]]
    segs = []
    for t in ts[1:]:
        if t - seg[-1] != 900: segs.append(seg); seg = []
        seg.append(t)
    segs.append(seg)
    for seg in segs:
        bars = [(t, *b[t][:5]) for t in seg]
        for e in find_equal_lows(bars):
            r = e['i'] + K
            if r + FWD >= len(bars): continue
            ref = bars[r][4]; w = bars[r + 1:r + 1 + FWD]
            wl = min(x[3] for x in w); cl = w[-1][4]
            rows.append(dict(div=e['div'], dist=e['dist'], broke=wl < e['floor'],
                             rev=wl >= e['floor'] and cl > ref, ret=(cl - ref) / ref,
                             y=dt.datetime.fromtimestamp(bars[e['i']][0], dt.timezone.utc).year))
    return rows


def first_sunday(y, mo, nth):
    d = dt.date(y, mo, 1); d += dt.timedelta((6 - d.weekday()) % 7); return d + dt.timedelta(7 * (nth - 1))


def us_open(d):
    dst = first_sunday(d.year, 3, 2) <= d < first_sunday(d.year, 11, 1)
    return dt.datetime(d.year, d.month, d.day, 13 if dst else 14, 30, tzinfo=dt.timezone.utc)


def u7(b):
    ts = sorted(b); idx = {t: i for i, t in enumerate(ts)}; C = [b[t][3] for t in ts]
    bw = [None] * len(ts)
    for i in range(19, len(ts)):
        w = C[i - 19:i + 1]; m = sum(w) / 20; sd = (sum((x - m) ** 2 for x in w) / 20) ** .5; bw[i] = 4 * sd / m
    rows = []; d = dt.datetime.fromtimestamp(ts[0], dt.timezone.utc).date()
    d1 = dt.datetime.fromtimestamp(ts[-1], dt.timezone.utc).date()
    while d <= d1:
        if d.weekday() < 5:
            A = int(us_open(d).timestamp()); a15 = A - A % 900
            box = [b.get(a15 - 900 * k) for k in range(1, 33)]; win = [b.get(a15 + 900 * k) for k in range(16)]
            last = idx.get(a15 - 900)
            if None not in box and None not in win and last is not None and last >= 2900 and bw[last]:
                hist = [x for x in bw[last - 2880:last] if x]; pct = sum(x < bw[last] for x in hist) / len(hist)
                bh = max(x[1] for x in box); bl = min(x[2] for x in box)
                first = 'none'
                for x in win:
                    if x[1] > bh and x[2] < bl: first = 'both'; break
                    if x[1] > bh: first = 'up'; break
                    if x[2] < bl: first = 'down'; break
                cv = sum(x[4] for x in box); vol = sum(x[5] for x in box)
                rows.append(dict(d=str(d), sq=pct <= .2, cvd=cv, share=cv / vol, first=first, px=box[0][3] - box[-1][0]))
        d += dt.timedelta(1)
    return rows


def main():
    b = load_15m(dev_files())
    print(f'15m bars {len(b)}  {dt.datetime.fromtimestamp(min(b), dt.timezone.utc):%Y-%m-%d}..'
          f'{dt.datetime.fromtimestamp(max(b), dt.timezone.utc):%Y-%m-%d}')
    R = u7(b)
    cut = sorted(abs(r['share']) for r in R)[int(len(R) * 2 / 3)]
    print('\nU7  price baseline (no CVD): box close vs box open x first break side')
    for lab, S in (('box close > open', [r for r in R if r['px'] > 0]), ('box close <= open', [r for r in R if r['px'] <= 0])):
        c = collections.Counter(r['first'] for r in S); ud = c['up'] + c['down']
        print(f"{lab} | n {len(S)} | up share {100 * c['up'] / ud:.0f}% of {ud}")
    print('\nU7  box CVD sign x first break side (A..A+4h)')
    print('group | CVD sign | n | first up | first down | both/none | up share of up+down')
    for lab, G in (('squeeze (C17)', [r for r in R if r['sq']]), ('all days', R),
                   ('all, strong third', [r for r in R if abs(r['share']) >= cut]),
                   ('all, box price up', [r for r in R if r['px'] > 0]), ('all, box price down', [r for r in R if r['px'] <= 0])):
        for sg, S in (('+', [r for r in G if r['cvd'] > 0]), ('-', [r for r in G if r['cvd'] <= 0])):
            c = collections.Counter(r['first'] for r in S); n = len(S); ud = c['up'] + c['down']
            if not n: continue
            print(f"{lab} | {sg} | {n} | {c['up']} | {c['down']} | {c['both'] + c['none']} | "
                  f"{100 * c['up'] / ud if ud else 0:.0f}%")
    U = u8(b)
    print('\nU8  equal 15m lows (<=0.1%, <=24h apart), forward 4h from confirm close')
    bins = lambda r: min(2, int(r['dist'] / (TOL / 3)))
    D = [r for r in U if r['div']]; N = [r for r in U if not r['div']]
    wD = collections.Counter(bins(r) for r in D)
    def line(lab, S, w=None):
        n = len(S)
        if not w:
            rev = sum(r['rev'] for r in S) / n; brk = sum(r['broke'] for r in S) / n; ret = st.mean(r['ret'] for r in S)
        else:
            byb = collections.defaultdict(list)
            for r in S: byb[bins(r)].append(r)
            tot = sum(w.values())
            f = lambda key: sum(w[k] / tot * st.mean(key(r) for r in byb[k]) for k in w if byb[k])
            rev = f(lambda r: r['rev']); brk = f(lambda r: r['broke']); ret = f(lambda r: r['ret'])
        print(f'{lab} | {n} | {100 * rev:.1f}% | {100 * brk:.1f}% | {100 * ret:+.3f}%')
    print('set | n | reversal 4h | low broken 4h | mean 4h return')
    line('divergence (CVD lower low)', D); line('control raw', N); line('control distance-matched', N, wD)
    for y in (2022, 2023, 2024):
        Dy = [r for r in D if r['y'] == y]; Ny = [r for r in N if r['y'] == y]
        if Dy and Ny: line(f'{y} divergence', Dy); line(f'{y} control matched', Ny, collections.Counter(bins(r) for r in Dy))


if __name__ == '__main__':
    main()
