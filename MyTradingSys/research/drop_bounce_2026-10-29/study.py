"""After a fast 1m drop and a partial bounce back to the 1m BB mid: what happens next? Descriptive only, no fees, no edge claim.
Operator ask 2026-10-29 ~21:30Z (shots 7495630a229a, ab1b2752e4c1): 80.9k -> 78,267 low at 20:47Z, bounce to the 1m BB mid.
Definitions fixed before the first run (all OURS):
- Data: Binance USD-M BTCUSDT 1m archive (F:/MTS/data/tom_raw/klines, 2022-01..2026-09), UTC.
- Event at 1m bar t: H = max high in [t-240, t-20]; L = min low in [t-60, t-20] (low 20-60 min old, after H's bar);
  drop (H-L)/H >= 2.5%; no new low after L up to t; retrace R = (C_t - L)/(H - L) in [0.25, 0.55];
  close within 0.15% of the 1m BB(20,2) mid. One event per 4 h (the first).
- Outcomes over the next 240 1m bars: BREAK = a low below L; RETEST = low within 0.3% of L, no break; HOLD = neither.
  First hit: L*(1.003) retest band vs L + 0.618(H-L).  Next 60 bars: share of 1m closes below the lower band /
  between lower and mid / above mid (judged against the band at that bar).
- Bounce quality = taker-buy delta share of the bounce leg (L bar .. t): (2*takerBuy - vol)/vol; also bounce vol / drop vol per bar.
  Split at the event median.
"""
import glob, sys
import numpy as np, pandas as pd

fs = sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'))
df = pd.concat([pd.read_csv(f, usecols=[0, 2, 3, 4, 5, 9]) for f in fs], ignore_index=True)
df.columns = ['t', 'h', 'l', 'c', 'v', 'tb']
df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t) // 1000
df = df.drop_duplicates('t').sort_values('t').reset_index(drop=True)
t, h, l, c, v, tb = (df[k].to_numpy(float) for k in ['t', 'h', 'l', 'c', 'v', 'tb'])
n = len(c)
cs = pd.Series(c); mid = cs.rolling(20).mean().to_numpy(); sd = cs.rolling(20).std(ddof=0).to_numpy()
lo_b = mid - 2 * sd
cv, ctb = np.concatenate([[0], np.cumsum(v)]), np.concatenate([[0], np.cumsum(tb)])

ev = []; last = -10**9
for i in range(260, n - 241):
    if i - last < 240: continue
    if not (abs(c[i] - mid[i]) <= 0.0015 * mid[i]): continue
    if t[i] - t[i - 240] != 240 * 60 or t[i + 240] - t[i] != 240 * 60: continue  # gap check on both windows
    seg = l[i - 60:i - 19]; j = i - 60 + int(np.argmin(seg)); L = l[j]
    if l[j + 1:i + 1].min() < L: continue
    hseg = h[i - 240:j];
    if len(hseg) == 0: continue
    k = i - 240 + int(np.argmax(hseg)); H = h[k]
    if (H - L) / H < 0.025: continue
    R = (c[i] - L) / (H - L)
    if not (0.25 <= R <= 0.55): continue
    fl, fh = l[i + 1:i + 241], h[i + 1:i + 241]
    brk = fl.min() < L; ret = (not brk) and fl.min() <= L * 1.003
    up = L + 0.618 * (H - L)
    a = np.argmax(fl <= L * 1.003) if (fl <= L * 1.003).any() else 999
    b = np.argmax(fh >= up) if (fh >= up).any() else 999
    first = 'none' if a == b == 999 else ('low' if a < b else ('up' if b < a else 'same'))
    w = slice(i + 1, i + 61)
    below = np.mean(c[w] < lo_b[w]); lowmid = np.mean((c[w] >= lo_b[w]) & (c[w] < mid[w])); abv = np.mean(c[w] >= mid[w])
    bv = cv[i + 1] - cv[j]; bt = ctb[i + 1] - ctb[j]; dv = cv[j + 1] - cv[k]
    ds = (2 * bt - bv) / bv if bv else np.nan
    vr = (bv / (i + 1 - j)) / (dv / (j + 1 - k)) if dv else np.nan
    ev.append(dict(t=pd.to_datetime(t[i], unit='s'), drop=(H - L) / H, R=R, brk=brk, ret=ret, first=first,
                   below=below, lowmid=lowmid, above=abv, ds=ds, vr=vr, c60=c[i + 60] > c[i]))
    last = i
E = pd.DataFrame(ev)
def row(name, x):
    m = len(x)
    if m == 0: return f'{name}: n=0'
    return (f"{name}: n={m} | BREAK {x.brk.mean():.0%} RETEST {x.ret.mean():.0%} HOLD {(~x.brk & ~x.ret).mean():.0%}"
            f" | first: low-retest {np.mean(x['first']=='low'):.0%} 61.8% {np.mean(x['first']=='up'):.0%} neither {np.mean(x['first']=='none'):.0%}"
            f" | next 60m closes: below lower {x.below.mean():.0%}, lower-mid {x.lowmid.mean():.0%}, above mid {x.above.mean():.0%}"
            f" | close up after 60m {x.c60.mean():.0%}")
print(row('ALL', E))
md = E.ds.median(); print(f'bounce delta share median {md:+.3f}; bounce/drop volume-per-bar median {E.vr.median():.2f}')
print(row('bounce delta share >= median (more taker buying)', E[E.ds >= md]))
print(row('bounce delta share <  median', E[E.ds < md]))
print(row('bounce delta share > 0 (net taker buying)', E[E.ds > 0]))
print(row('bounce vol/bar >= drop vol/bar x0.5', E[E.vr >= 0.5]))
print(row('bounce vol/bar <  drop vol/bar x0.5', E[E.vr < 0.5]))
print(row('drop 2.5-3.5%', E[E['drop'] < 0.035]))
for y in sorted(E.t.dt.year.unique()): print(row(f'year {y}', E[E.t.dt.year == y]))
if len(sys.argv) > 1: E.to_csv(sys.argv[1], index=False)
