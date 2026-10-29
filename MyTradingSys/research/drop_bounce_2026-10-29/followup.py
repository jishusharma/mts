"""Follow-up: the bounce failed and price came back near the low. What next? Descriptive only, no fees, no edge claim.
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


# Follow-up (fixed before the run, OURS): from each event, the bounce must reach >= 55% retrace within 120 bars (bar p = its high),
# then price falls back to <= L*1.010 (bar r, first time after p, within 120 bars of p). Outcome from r: low < L within 60 / 240 bars.
# Fade delta share = taker delta over p..r; "sellers on the fade" = share <= -0.10.
ev = []; last = -10**9
for i in range(260, n - 600):
    if i - last < 240: continue
    if not (abs(c[i] - mid[i]) <= 0.0015 * mid[i]): continue
    if t[i] - t[i - 240] != 240 * 60 or t[i + 600] - t[i] != 600 * 60: continue
    seg = l[i - 60:i - 19]; j = i - 60 + int(np.argmin(seg)); L = l[j]
    if l[j + 1:i + 1].min() < L: continue
    hseg = h[i - 240:j]
    if len(hseg) == 0: continue
    k = i - 240 + int(np.argmax(hseg)); H = h[k]
    if (H - L) / H < 0.025: continue
    R = (c[i] - L) / (H - L)
    if not (0.25 <= R <= 0.55): continue
    last = i
    tgt = L + 0.55 * (H - L); w = h[i + 1:i + 121]
    if not (w >= tgt).any(): continue
    if l[i + 1:i + 121].min() < L: continue
    p = i + 1 + int(np.argmax(h[i + 1:i + 121]))
    seg2 = l[p + 1:p + 121]
    hit = np.nonzero(seg2 <= L * 1.010)[0]
    if len(hit) == 0: continue
    r = p + 1 + int(hit[0])
    if r > p + 1 and l[p + 1:r].min() < L: continue
    fv = cv[r + 1] - cv[p]; ft = ctb[r + 1] - ctb[p]
    fut = l[r + 1:r + 241]
    ev.append(dict(fs=(2 * ft - fv) / fv if fv else np.nan, b60=fut[:60].min() < L, b240=fut.min() < L,
                   up240=c[r + 240] > c[r], mxup=h[r + 1:r + 241].max() / c[r] - 1))
E = pd.DataFrame(ev)
def rep(x, nm): print(f"{nm}: n={len(x)} | low broken within 1h {x.b60.mean():.0%}, within 4h {x.b240.mean():.0%} | close up after 4h {x.up240.mean():.0%} | median max up {x.mxup.median():+.2%}")
rep(E, 'bounce >=55% then back within 1% of low')
rep(E[E.fs <= -0.10], 'fade with net selling (delta share <= -0.10)')
rep(E[E.fs > -0.10], 'fade without net selling')
