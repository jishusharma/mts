"""Fractal (shape) search: past 1m windows shaped like 2026-10-29 19:55-21:30Z (operator green box, shot 38a360af27ef):
step drop, pause at mid, second capitulation leg, V bounce, band contraction drifting up. Descriptive only, no fees.
Definitions fixed before the first run (OURS):
- Template = Binance spot BTCUSDT 1m closes 19:55-21:30Z (96 bars), saved as template.csv (public market data).
- Archive = Binance USD-M BTCUSDT 1m (F:/MTS/data/tom_raw/klines). Shape score = Pearson correlation of the 96 closes
  (z-normalised). Window must have no time gap, range (max-min)/first between 2% and 6% (template 3.2%), and the
  window low must sit in its middle third (bars 32-63) like the template.
- Matches: corr >= 0.85, greedy best-first, no two within 240 bars. Need 240 future bars without a gap.
- Outcomes over the next 240 bars (L = window low): BREAK below L, RETEST within 0.3% of L, HOLD; close after 60/240 bars
  vs the window's last close; max up / max down excursion; share of next 60 closes below the 1m BB(20,2) lower band,
  between lower and mid, above mid.
"""
import glob, sys, json, urllib.request, datetime as dt
import numpy as np, pandas as pd

HERE = 'MyTradingSys/research/drop_bounce_2026-10-29/'
try:
    tp = pd.read_csv(HERE + 'template.csv')
except FileNotFoundError:
    s = int(dt.datetime(2026, 10, 29, 19, 55, tzinfo=dt.timezone.utc).timestamp() * 1000)
    k = json.load(urllib.request.urlopen(f'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={s}&limit=96', timeout=20))
    tp = pd.DataFrame({'t': [r[0] // 1000 for r in k], 'h': [float(r[2]) for r in k], 'l': [float(r[3]) for r in k], 'c': [float(r[4]) for r in k]})
    tp.to_csv(HERE + 'template.csv', index=False)
y = tp.c.to_numpy(float); m = len(y); y = (y - y.mean()) / y.std()

fs = sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'))
df = pd.concat([pd.read_csv(f, usecols=[0, 2, 3, 4]) for f in fs], ignore_index=True)
df.columns = ['t', 'h', 'l', 'c']
df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t) // 1000
df = df.drop_duplicates('t').sort_values('t').reset_index(drop=True)
t, h, l, c = (df[k].to_numpy(float) for k in 'thlc'); n = len(c)
# sliding Pearson via FFT
N = 1 << int(np.ceil(np.log2(n + m)))
xy = np.fft.irfft(np.fft.rfft(c, N) * np.conj(np.fft.rfft(np.r_[y, np.zeros(N - m)])), N)[:n - m + 1]
cs, cs2 = np.r_[0, np.cumsum(c)], np.r_[0, np.cumsum(c * c)]
mu = (cs[m:] - cs[:-m]) / m; sd = np.sqrt(np.maximum((cs2[m:] - cs2[:-m]) / m - mu ** 2, 1e-12))
corr = xy / (m * sd)  # y has mean 0, std 1
mid = pd.Series(c).rolling(20).mean().to_numpy(); bsd = pd.Series(c).rolling(20).std(ddof=0).to_numpy(); lob = mid - 2 * bsd
order = np.argsort(-corr); taken = []; ev = []
for s in order:
    if corr[s] < 0.85: break
    e = s + m - 1
    if e + 240 >= n or s < 20: continue
    if t[e] - t[s] != (m - 1) * 60 or t[e + 240] - t[e] != 240 * 60: continue
    if any(abs(s - x) < 240 for x in taken): continue
    wl = l[s:e + 1]; rng = (h[s:e + 1].max() - wl.min()) / c[s]
    if not (0.02 <= rng <= 0.06): continue
    if not (32 <= int(np.argmin(wl)) <= 63): continue
    taken.append(s); L = wl.min(); fl, fh = l[e + 1:e + 241], h[e + 1:e + 241]
    brk = fl.min() < L; ret = (not brk) and fl.min() <= L * 1.003
    w = slice(e + 1, e + 61)
    ev.append(dict(t=pd.to_datetime(t[s], unit='s'), corr=corr[s], rng=rng, brk=brk, ret=ret,
                   up60=c[e + 60] > c[e], up240=c[e + 240] > c[e], mxup=fh.max() / c[e] - 1, mxdn=fl.min() / c[e] - 1,
                   below=np.mean(c[w] < lob[w]), lowmid=np.mean((c[w] >= lob[w]) & (c[w] < mid[w])), above=np.mean(c[w] >= mid[w])))
E = pd.DataFrame(ev)
print(f'matches n={len(E)} (corr>=0.85; median corr {E["corr"].median():.2f})')
def rep(x, name):
    print(f"{name}: n={len(x)} | BREAK {x.brk.mean():.0%} RETEST {x.ret.mean():.0%} HOLD {(~x.brk & ~x.ret).mean():.0%} | "
          f"up after 60m {x.up60.mean():.0%}, after 4h {x.up240.mean():.0%} | median max up {x.mxup.median():+.2%}, max down {x.mxdn.median():+.2%} | "
          f"next 60m closes: below lower {x.below.mean():.0%}, lower-mid {x.lowmid.mean():.0%}, above mid {x.above.mean():.0%}")
rep(E, 'ALL'); rep(E[E['corr'] >= 0.9], 'corr>=0.90')
print(E.sort_values('corr', ascending=False).head(8).to_string(index=False, float_format=lambda v: f'{v:.3f}'))
if len(sys.argv) > 1: E.to_csv(sys.argv[1], index=False)
