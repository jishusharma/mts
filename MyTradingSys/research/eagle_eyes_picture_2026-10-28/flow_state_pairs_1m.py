"""C2 flow-state pairs on 1m (card flow-state-pairs-on-1m-oi-up-negative-de). Descriptive, SEEN window, no fees, no edge claim.
Data (public): Binance USD-M BTCUSDT 1m klines (price, taker net delta = 2*taker_buy - volume, CVD = running sum)
and 5m openInterestHist. CoinGlass 1m OI history is not on disk and has no keyless API (DECISION, OURS): a 1m bar's
OI direction = the change of the 5m OI bucket that holds it (stamp t0 -> t0+300).
Thresholds (all OURS, from the 10-28 shots): burst = |net delta| >= P95 of |net delta| in the window;
OI up / down = bucket change >= +0.05% / <= -0.05%.
  A: negative burst, OI up.  B: positive burst, OI up, green bar, 5-bar CVD change > 0 ("all positive").
  C: positive burst, OI down.
Forward move = close[t+h]/close[t]-1, h = 15/30/60 min. Cache: F:/MTS/data/flow_state_1m (outside the repo)."""
import csv, io, json, os, statistics as st, sys, time, urllib.request, zipfile, datetime as dt

BURST_PCT = 0.95   # OURS
OI_THR = 0.0005    # OURS, 0.05 % per 5m bucket
HORIZONS = (15, 30, 60)
CACHE = 'F:/MTS/data/flow_state_1m'
NAMED = ['2026-10-28T20:46', '2026-10-28T20:56', '2026-10-28T20:00']


def oi_change(oi, t):
    """OI change over the last 5m bucket that ends at or before the close (t+60) of the 1m bar opening at t
    (no look-ahead; lags up to 4 min); None if a stamp is missing."""
    s = (t + 60) // 300 * 300
    a, b = oi.get(s - 300), oi.get(s)
    return None if not a or not b else b / a - 1


def classify(bar, doi, cvd5, thr):
    """bar = dict(o, c, d). Returns 'A', 'B', 'C' or None."""
    if doi is None or abs(bar['d']) < thr:
        return None
    if bar['d'] < 0:
        return 'A' if doi >= OI_THR else None
    if doi <= -OI_THR:
        return 'C'
    if doi >= OI_THR and bar['c'] > bar['o'] and cvd5 > 0:
        return 'B'
    return None


def forward(bars, i, h):
    j = i + h
    if j >= len(bars) or bars[j]['t'] - bars[i]['t'] != 60 * h:
        return None
    return bars[j]['c'] / bars[i]['c'] - 1


def burst_threshold(bars):
    a = sorted(abs(b['d']) for b in bars)
    return a[int(BURST_PCT * (len(a) - 1))]


def run(bars, oi):
    thr = burst_threshold(bars)
    cvd, run_sum = [], 0.0
    for b in bars:
        run_sum += b['d']; cvd.append(run_sum)   # cvd[i] = CVD through bar i
    events = []
    for i, b in enumerate(bars):
        if i < 5:
            continue
        doi = oi_change(oi, b['t'])
        case = classify(b, doi, cvd[i] - cvd[i - 5], thr)
        if case:
            events.append(dict(i=i, t=b['t'], case=case, d=b['d'], doi=doi, fw={h: forward(bars, i, h) for h in HORIZONS}))
    return thr, events


def _csv(url):
    """Daily zip from data.binance.vision (fapi.binance.com is unreachable from JIS-NB) -> rows without the header."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'mts-research'}), timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
    except urllib.error.HTTPError as e:
        print('MISSING %s (%s)' % (url.rsplit('/', 1)[-1], e.code))
        return []
    rows = list(csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='utf-8')))
    return [x for x in rows if x and x[0][:1].isdigit()]


def fetch(start, end):
    os.makedirs(CACHE, exist_ok=True)
    p = '%s/BTCUSDT_v2_%d_%d.json' % (CACHE, start, end)
    if os.path.exists(p):
        return json.load(open(p))
    base = 'https://data.binance.vision/data/futures/um/daily'
    kl, oi, monthly = [], {}, {}
    for day in range(start, end, 86400):
        s = dt.datetime.fromtimestamp(day, dt.timezone.utc).strftime('%Y-%m-%d')
        rows = _csv('%s/klines/BTCUSDT/1m/BTCUSDT-1m-%s.zip' % (base, s))
        if not rows:  # a daily zip can be missing (10-28 is): take that day from the monthly zip
            m = s[:7]
            if m not in monthly:
                monthly[m] = _csv('https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-%s.zip' % m)
            rows = [x for x in monthly[m] if day * 1000 <= int(x[0]) < (day + 86400) * 1000]
            print('filled %s from monthly zip: %d bars' % (s, len(rows)))
        kl += [[int(x[0])] + x[1:] for x in rows]
        for x in _csv('%s/metrics/BTCUSDT/BTCUSDT-metrics-%s.zip' % (base, s)):
            t = int(dt.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())
            oi[str(t)] = float(x[2])
        time.sleep(0.2)
    d = dict(klines=kl, oi=oi)
    with open(p, 'w', newline='\n') as f:
        json.dump(d, f)
    return d


def bybit_day(s):
    """1m bars (o, c, taker net delta) for one UTC day from the public Bybit linear trade dump. Used only where the
    Binance USD-M archive has no klines (10-28): a venue switch, so it gets its own P95 burst threshold (OURS)."""
    os.makedirs(CACHE, exist_ok=True)
    p = '%s/bybit_BTCUSDT_%s.json' % (CACHE, s)
    if os.path.exists(p):
        return json.load(open(p))
    import gzip
    with urllib.request.urlopen('https://public.bybit.com/trading/BTCUSDT/BTCUSDT%s.csv.gz' % s, timeout=300) as r:
        rows = list(csv.reader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(r.read())), encoding='utf-8')))
    tr = sorted((float(x[0]), x[2], float(x[3]), float(x[4])) for x in rows if x and x[0][:1].isdigit())
    bars = {}
    for ts, side, size, px in tr:
        t = int(ts) // 60 * 60
        b = bars.setdefault(t, dict(t=t, o=px, c=px, d=0.0))
        b['c'] = px
        b['d'] += size if side == 'Buy' else -size
    out = [bars[t] for t in sorted(bars)]
    with open(p, 'w', newline='\n') as f:
        json.dump(out, f)
    return out


def utc(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%m-%d %H:%MZ')


def main():
    end = int(dt.datetime(2026, 11, 5, tzinfo=dt.timezone.utc).timestamp())  # last complete daily zip
    start = end - 14 * 86400
    raw = fetch(start, end)
    bars = [dict(t=k[0] // 1000, o=float(k[1]), c=float(k[4]), d=2 * float(k[9]) - float(k[5])) for k in raw['klines']]
    oi = {int(k): v for k, v in raw['oi'].items()}
    thr, ev = run(bars, oi)
    print('1m bars %d %s..%s  OI pts %d  burst |delta| >= %.1f BTC (P95)' % (len(bars), utc(bars[0]['t']), utc(bars[-1]['t']), len(oi), thr))
    print('| Case | n | n (1 per 15 min) | 15m med | 15m up | 30m med | 30m up | 60m med | 60m up |')
    print('|---|---|---|---|---|---|---|---|---|')
    for c in 'ABC':
        xs = [e for e in ev if e['case'] == c]
        dec, last = [], -10 ** 9
        for e in xs:
            if e['t'] - last >= 900:
                dec.append(e); last = e['t']
        row = ['%s' % c, str(len(xs)), str(len(dec))]
        for h in HORIZONS:
            f = [e['fw'][h] for e in xs if e['fw'][h] is not None]
            row += ['%+.3f%%' % (100 * st.median(f)), '%.0f%%' % (100 * sum(x > 0 for x in f) / len(f))] if f else ['-', '-']
        print('| ' + ' | '.join(row) + ' |')
    days = {utc(b['t'])[:5] for b in bars}
    gaps = [s for s in sorted({n[:10] for n in NAMED}) if s[5:] not in days]
    for s in gaps:
        bb = bybit_day(s)
        thr_b, ev_b = run(bb, oi)
        print('\n%s from Bybit linear trades (Binance USD-M archive gap): %d bars, burst |delta| >= %.1f BTC (day P95); A %d B %d C %d'
              % (s, len(bb), thr_b, *[sum(e['case'] == c for e in ev_b) for c in 'ABC']))
        named(bb, ev_b, oi, [n for n in NAMED if n.startswith(s)])
    named(bars, ev, oi, [n for n in NAMED if n[:10] not in gaps])
    print('\nEvents (case time delta OI5m fwd15/30/60):')
    for e in ev:
        print(e['case'], utc(e['t']), '%+.0f' % e['d'], '%+.3f%%' % (100 * e['doi']), ' '.join('-' if e['fw'][h] is None else '%+.2f%%' % (100 * e['fw'][h]) for h in HORIZONS))


def named(bars, ev, oi, names):
    idx = {b['t']: i for i, b in enumerate(bars)}
    for s in names:
        t = int(dt.datetime.strptime(s, '%Y-%m-%dT%H:%M').replace(tzinfo=dt.timezone.utc).timestamp())
        i = idx.get(t)
        if i is None:
            print(s, 'not in window'); continue
        b = bars[i]; e = next((e for e in ev if e['t'] == t), None)
        fw = ' '.join('%dm %s' % (h, '-' if forward(bars, i, h) is None else '%+.3f%%' % (100 * forward(bars, i, h))) for h in HORIZONS)
        doi = oi_change(oi, t)
        cvd5 = sum(x['d'] for x in bars[max(0, i - 4):i + 1])
        print('%s o %.1f c %.1f delta %+.1f cvd5 %+.1f OI5m %s case %s | %s' % (utc(t), b['o'], b['c'], b['d'], cvd5, 'n/a' if doi is None else '%+.3f%%' % (100 * doi), e['case'] if e else 'none', fw))


if __name__ == '__main__':
    sys.exit(main())
