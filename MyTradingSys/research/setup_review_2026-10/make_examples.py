#!/usr/bin/env python
"""Setup review 2026-10: one recent BTC example chart per catalogued Tom/Fabio setup.

Data: Binance USD-M BTCUSDT 1m archive, UTC (F:/MTS/data/tom_raw/klines). Search = last 120 days of the archive.
Every selection rule below is OURS (a picture of the conditions, never a trade signal). If the strict rule finds
nothing, each threshold is loosened once by 25 % ("relaxed"); if still nothing, a plain recent chart is drawn.
Delta proxy per minute = taker_buy_base - (volume - taker_buy_base); CVD = its running sum (OURS).
Run:  python make_examples.py   (deterministic; rewrites examples/*.png and examples.json)
"""
import glob, json, os, re, sys, textwrap, time
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'examples')
KL = 'F:/MTS/data/tom_raw/klines'
SEARCH_DAYS = 120
MIN = pd.Timedelta(minutes=1)
TFW = {'1m': 1 / 1440, '5m': 5 / 1440, '15m': 15 / 1440, '1h': 1 / 24, '1d': 1.0}
TFD = {'1m': pd.Timedelta(minutes=1), '5m': pd.Timedelta(minutes=5), '15m': pd.Timedelta(minutes=15),
       '1h': pd.Timedelta(hours=1), '1d': pd.Timedelta(days=1)}
UP, DN = '#1b9e77', '#d95f02'


def P(x):
    return f"{x:,.0f}"


# ----------------------------------------------------------------------------------------------- data
class Cx:
    pass


def load():
    names = sorted(glob.glob(KL + '/BTCUSDT-1m-*.csv'))
    keys = [re.search(r'1m-(\d{4}-\d{2})', n).group(1) for n in names]
    last = pd.Period(max(keys), 'M')
    first = last - 5
    use = [n for n, k in zip(names, keys) if pd.Period(k, 'M') >= first]
    df = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4, 5, 9]) for f in use], ignore_index=True)
    df.columns = ['t', 'o', 'h', 'l', 'c', 'v', 'tb']
    df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t)
    df = df.drop_duplicates('t').sort_values('t').reset_index(drop=True)
    df.index = pd.to_datetime(df.t, unit='ms')
    df = df.drop(columns='t')
    df['d'] = df.tb - (df.v - df.tb)
    return df, use


def agg(m, tf):
    r = m.resample(tf, label='left', closed='left')
    b = pd.DataFrame({'o': r.o.first(), 'h': r.h.max(), 'l': r.l.min(), 'c': r.c.last(), 'v': r.v.sum(), 'd': r.d.sum()})
    return b.dropna(subset=['o'])


def profile_of(day):
    tp = ((day.h + day.l + day.c) / 3).values
    bins = np.floor(tp / 10) * 10
    s = pd.Series(day.v.values).groupby(bins).sum().sort_index()
    full = np.arange(s.index.min(), s.index.max() + 10, 10)
    s = s.reindex(full, fill_value=0.0)
    vals = s.values
    ip = int(vals.argmax()); lo = hi = ip; tot = vals.sum(); acc = vals[ip]
    while acc < 0.7 * tot and (lo > 0 or hi < len(vals) - 1):
        up = vals[hi + 1] if hi + 1 < len(vals) else -1
        dn = vals[lo - 1] if lo - 1 >= 0 else -1
        if up >= dn:
            hi += 1; acc += vals[hi]
        else:
            lo -= 1; acc += vals[lo]
    return dict(val=full[lo], vah=full[hi] + 10, poc=full[ip] + 5, hist=s)


def build():
    m, files = load()
    cx = Cx()
    cx.m = m; cx.files = files
    cx.end = m.index[-1]
    cx.end_day = cx.end.normalize()
    cx.s0 = cx.end_day - pd.Timedelta(days=SEARCH_DAYS - 1)
    cx.b5, cx.b15, cx.b1h, cx.bd = agg(m, '5min'), agg(m, '15min'), agg(m, '1h'), agg(m, '1D')
    cx.bars = {'1m': m, '5m': cx.b5, '15m': cx.b15, '1h': cx.b1h, '1d': cx.bd}
    tp = (m.h + m.l + m.c) / 3
    day = m.index.normalize()
    cx.vw1 = (tp * m.v).groupby(day).cumsum() / m.v.groupby(day).cumsum()
    cx.prof = {}
    for d, g in m.groupby(day):
        if len(g) >= 1000:
            cx.prof[d] = profile_of(g)
    pdf = pd.DataFrame({k: {d: p[k] for d, p in cx.prof.items()} for k in ('val', 'vah', 'poc')})
    cx.pdf = pdf
    for nm in ('b5', 'b15'):
        b = getattr(cx, nm)
        pdates = b.index.normalize() - pd.Timedelta(days=1)
        for k in ('val', 'vah', 'poc'):
            b[k + 'p'] = pdf[k].reindex(pdates).values
    cx.vw5 = cx.vw1.resample('5min', label='left', closed='left').last().reindex(cx.b5.index)
    cx.days = [d for d in pd.date_range(cx.s0, cx.end_day, freq='D')]
    gaps = int((m.index.to_series().diff().dropna() > MIN).sum())
    cx.gaps = gaps
    return cx


# --------------------------------------------------------------------------------------------- marks
def box(t0, t1, label, y0=None, y1=None, color='#1f77b4'):
    return dict(kind='box', x0=t0, x1=t1, y0=y0, y1=y1, label=label, color=color)


def arrow(t, y, label, up=True, ox=0, oy=42):
    return dict(kind='arrow', x=t, y=y, label=label, up=up, ox=ox, oy=oy)


def hline(y, label, t0, t1, color='#555555', pos='start'):
    return dict(kind='hline', y=y, label=label, x0=t0, x1=t1, color=color, pos=pos)


def dots(xs, ys, label, color='#e377c2'):
    return dict(kind='dots', xs=xs, ys=ys, label=label, color=color)


def result(D, marks, caption, ev=None, end=None, win=None, tf='5m', **kw):
    r = dict(D=D, marks=marks, caption=caption, ev=ev, end=end, win=win, tf=tf)
    r.update(kw)
    return r


# ---------------------------------------------------------------------------------------------- finders
def thr(relax):
    return (0.75, 1.25) if relax else (1.0, 1.0)  # g for ">=" thresholds, l for "<" thresholds


def arr5(cx):
    b = cx.b5
    return dict(t=b.index, o=b.o.values, h=b.h.values, l=b.l.values, c=b.c.values, v=b.v.values, d=b.d.values)


def f_tom1a(cx, relax):
    g, l = thr(relax); a = arr5(cx); b = cx.b5
    push_t, above_t, give_t = 0.015 * g, 0.005 * g, 0.5 * g
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 49, i0 - 1, -1):
        vah = b.vahp.values[i]
        if np.isnan(vah): continue
        P_ = a['h'][i]
        if P_ < vah * (1 + above_t): continue
        if P_ < a['h'][max(0, i - 12):i + 13].max(): continue
        j0 = max(0, i - 24); seg = a['l'][j0:i + 1]; jm = j0 + int(seg.argmin()); S = seg.min()
        if jm >= i or (P_ - S) / S < push_t: continue
        nxt = a['l'][i + 1:i + 49]; k = i + 1 + int(nxt.argmin()); mn = nxt.min()
        giv = (P_ - mn) / (P_ - S)
        if giv < give_t: continue
        D = b.index[i].normalize()
        cap = (f"Price pushed up {100 * (P_ - S) / S:.1f}% in {(i - jm) * 5 // 60}h{(i - jm) * 5 % 60:02d}m to {P(P_)}, "
               f"{100 * (P_ / vah - 1):.1f}% above the prior-day value-area high ({P(vah)}), then gave back {100 * giv:.0f}% "
               f"of the push within {(k - i) * 5 // 60}h{(k - i) * 5 % 60:02d}m.")
        return result(D, [box(b.index[jm], b.index[i] + TFD['5m'], f"Push +{100 * (P_ - S) / S:.1f}% above value", S, P_, UP),
                          arrow(b.index[k], mn, f"Gave back {100 * giv:.0f}% of push", up=False, oy=-45)],
                      cap, ev=b.index[i], end=b.index[k] + pd.Timedelta(hours=1))
    return None


def daily_arrays(cx):
    d = cx.bd
    return d.index, d.o.values, d.h.values, d.l.values, d.c.values


def daily_win(cx, i, after=6):
    n = len(cx.bd)
    e = min(i + after, n - 1); s = e - 44
    return cx.bd.index[s], cx.bd.index[e] + pd.Timedelta(days=1)


def f_tom1b(cx, relax):
    g, l = thr(relax); idx, o, h, lo, c = daily_arrays(cx)
    nup = int(np.floor(3 * g)); third = (1 / 3) * l
    i0 = idx.searchsorted(cx.s0)
    for i in range(len(idx) - 1, i0 - 1, -1):
        if i < 12: continue
        if not (c[i - nup:i] > o[i - nup:i]).all(): continue
        rng = h[i] - lo[i]
        if rng <= 0 or (c[i] - lo[i]) / rng > third: continue
        if h[i] <= h[i - 10:i].max(): continue
        D = idx[i]
        cap = (f"{nup}+ up days in a row, then {D:%d %b}: new 10-day high ({P(h[i])}) but the day closed at {P(c[i])}, "
               f"in the lower {100 * (c[i] - lo[i]) / rng:.0f}% of its range (weak close after a run-up).")
        t0, t1 = daily_win(cx, i)
        return result(D, [box(idx[i - nup], idx[i], f"{nup} up days in a row", None, None, UP),
                          arrow(D + pd.Timedelta(hours=12), h[i], "New high, weak close", up=True, oy=45),
                          hline(h[i - 10:i].max(), "prior 10-day high", idx[i - 10], D, '#777777')],
                      cap, ev=D, win=(t0, t1), tf='1d')
    return None


def f_tom3(cx, relax):
    g, l = thr(relax); idx, o, h, lo, c = daily_arrays(cx)
    nup = int(np.floor(5 * g)); i0 = idx.searchsorted(cx.s0)
    for i in range(len(idx) - 1, i0 - 1, -1):
        if i < 22: continue
        if not (h[i] < h[i - 1] and lo[i] > lo[i - 1]): continue
        if h[i - 1] < h[i - 20:i].max(): continue
        ups = int((c[i - 10:i] > o[i - 10:i]).sum())
        if ups < nup: continue
        D = idx[i]
        cap = (f"{D:%d %b} is an inside day (range {P(lo[i])}-{P(h[i])} sits inside {idx[i - 1]:%d %b}) right under the 20-day high "
               f"({P(h[i - 1])}), after {ups} up days out of the last 10.")
        t0, t1 = daily_win(cx, i, 4)
        return result(D, [box(D, D + pd.Timedelta(days=1), "Inside day under 20-day high", None, None, '#1f77b4'),
                          hline(h[i - 1], "20-day high", idx[i - 1], D + pd.Timedelta(days=1), '#777777')],
                      cap, ev=D, win=(t0, t1), tf='1d')
    return None


def f_tom2(cx, relax):
    g, l = thr(relax); d = cx.bd; ratio = 0.6 * l
    rng = (d.h - d.l)
    for D in reversed(cx.days):
        if D not in d.index or D - pd.Timedelta(days=1) not in cx.prof: continue
        pr = cx.prof[D - pd.Timedelta(days=1)]
        med = rng.loc[D - pd.Timedelta(days=20):D - pd.Timedelta(days=1)].median()
        r = rng.loc[D]
        if r < ratio * med and d.l.loc[D] >= pr['val'] and d.h.loc[D] <= pr['vah']:
            cap = (f"{D:%d %b} range was {P(r)} USD = {100 * r / med:.0f}% of the 20-day median range ({P(med)}); high and low both "
                   f"stayed inside the prior-day value area ({P(pr['val'])}-{P(pr['vah'])}): a quiet, balanced day.")
            return result(D, [box(D, D + pd.Timedelta(days=1), "Quiet day inside prior value", d.l.loc[D], d.h.loc[D], '#1f77b4')], cap, ev=D)
    return None


def f_tom4(cx, relax):
    g, l = thr(relax); a = arr5(cx); b = cx.b5; vw = cx.vw5.values
    need = int(np.floor(3 * g)); band = 0.002 * l; mv = 0.015 * g
    for D in reversed(cx.days):
        if D not in cx.bd.index: continue
        if (cx.bd.c.loc[D] - cx.bd.o.loc[D]) / cx.bd.o.loc[D] < mv: continue
        s = b.index.searchsorted(D); e = b.index.searchsorted(D + pd.Timedelta(days=1))
        k = b.index.searchsorted(D + pd.Timedelta(hours=6))
        near = np.abs(a['c'][s:e] - vw[s:e]) <= band * vw[s:e]
        j = k - s
        while j < e - s - need:
            if near[j] and near[j:j + need].all() and a['l'][s + j] <= vw[s + j] <= a['h'][s + j]:
                run_end = s + j + need - 1
                dayhigh = a['h'][s:run_end + 1].max()
                nh = np.where(a['h'][run_end + 1:e] > dayhigh)[0]
                if len(nh):
                    m_ = run_end + 1 + int(nh[0])
                    cap = (f"Day closed +{100 * (cx.bd.c.loc[D] - cx.bd.o.loc[D]) / cx.bd.o.loc[D]:.1f}% (open to close). After 06:00 UTC price "
                           f"touched the UTC-day VWAP ({P(vw[s + j])}) at {b.index[s + j]:%H:%M}, stayed within {100 * band:.2f}% of it for "
                           f"{need}+ bars, then made a new day high ({P(a['h'][m_])}) at {b.index[m_]:%H:%M}.")
                    return result(D, [box(b.index[s + j], b.index[run_end] + TFD['5m'], "Pullback holds at VWAP", None, None, '#ff7f0e'),
                                      arrow(b.index[m_], a['h'][m_], "New day high after VWAP test", up=True, oy=45)],
                                  cap, ev=b.index[s + j])
                j += need
            else:
                j += 1
    return None


def roll_cache(cx, nb):
    key = f'_r{nb}'
    if not hasattr(cx, key):
        b = cx.b5
        setattr(cx, key, (b.h.rolling(nb).max().values, b.l.rolling(nb).min().values))
    return getattr(cx, key)


def balance(cx, e, maxr, nb, cap=288):
    """balance window ending at 5m index e (>= nb bars, 5m range < maxr). Returns (start, hi, lo) or None."""
    rmax, rmin = roll_cache(cx, nb)
    if e < nb or np.isnan(rmax[e]) or rmax[e] / rmin[e] - 1 >= maxr: return None
    h, lo_ = cx.b5.h.values, cx.b5.l.values
    hi, lo = rmax[e], rmin[e]; k = e - nb
    while k >= 0 and e - k < cap:
        nh, nl = max(hi, h[k]), min(lo, lo_[k])
        if nh / nl - 1 >= maxr: break
        hi, lo = nh, nl; k -= 1
    return k + 1, hi, lo


def f_tom6(cx, relax):
    g, l = thr(relax); a = arr5(cx); b = cx.b5
    nb = int(round(72 * g)); maxr = 0.008 * l; vm = 2 * g
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 1, i0 - 1, -1):
        bal = balance(cx, i - 1, maxr, nb)
        if bal is None: continue
        st, hi, lo = bal
        if a['c'][i] <= hi: continue
        med = np.median(a['v'][st:i])
        if a['v'][i] < vm * med: continue
        D = b.index[i].normalize()
        cap = (f"{(i - st) * 5 / 60:.1f} h{'+ (look-back capped at 24 h)' if i - st >= 288 else ''} of balance (5m range {P(lo)}-{P(hi)}, {100 * (hi / lo - 1):.2f}%), then a 5m close at {P(a['c'][i])} "
               f"above the range with volume {a['v'][i] / med:.1f}x the balance median.")
        return result(D, [box(b.index[st], b.index[i], f"{(i - st) * 5 / 60:.0f}h{'+' if i - st >= 288 else ''} balance", lo, hi, '#1f77b4'),
                          arrow(b.index[i], a['h'][i], f"Breakout close, {a['v'][i] / med:.1f}x volume", up=True, oy=45)],
                      cap, ev=b.index[i], end=b.index[i] + pd.Timedelta(hours=2))
    return None


def f_tom7(cx, relax):
    g, l = thr(relax); b = cx.b5; vw = cx.vw5
    rmax = 0.012 * l; ncr = int(np.floor(8 * g))
    for D in reversed(cx.days):
        s = b.index.searchsorted(D); e = b.index.searchsorted(D + pd.Timedelta(days=1))
        if e - s < 280: continue
        rg = b.h.values[s:e].max() / b.l.values[s:e].min() - 1
        if rg >= rmax: continue
        sg = np.sign(b.c.values[s:e] - vw.values[s:e])
        sg = sg[sg != 0]
        cr = np.where(np.diff(sg) != 0)[0] + 1
        if len(cr) < ncr: continue
        xs = []; ys = []
        pos = np.where(np.sign(b.c.values[s:e] - vw.values[s:e]) != 0)[0]
        for q in cr:
            ii = s + pos[q]; xs.append(b.index[ii]); ys.append(vw.values[ii])
        cap = f"Day range only {100 * rg:.2f}%; the 5m close crossed the UTC-day VWAP {len(cr)} times (pink dots)."
        return result(D, [dots(xs, ys, f"{len(cr)} VWAP crosses")], cap, ev=D)
    return None


def f_gap(cx, relax, held):
    g, l = thr(relax); m = cx.m; gmin = 0.008 * g
    mondays = [d for d in cx.days if d.weekday() == 0]
    for M in reversed(mondays):
        fk = M - pd.Timedelta(days=3) + pd.Timedelta(hours=20, minutes=59)
        if fk not in m.index or M not in m.index: continue
        fri = m.c.loc[fk]; mo = m.o.loc[M]; gap = (mo - fri) / fri
        if abs(gap) < gmin: continue
        mon = m.loc[M:M + pd.Timedelta(hours=23, minutes=59)]
        if len(mon) < 1300: continue
        if gap > 0:
            hit = mon.index[mon.l.values <= fri]
        else:
            hit = mon.index[mon.h.values >= fri]
        closed = len(hit) > 0
        mc = mon.c.iloc[-1]
        further = (mc > mo) if gap > 0 else (mc < mo)
        t0 = M - pd.Timedelta(days=3) + pd.Timedelta(hours=20); t1 = M + pd.Timedelta(days=1)
        if not held and closed:
            cap = (f"Friday 21:00 UTC close {P(fri)} vs Monday 00:00 UTC open {P(mo)}: weekend gap {100 * gap:+.2f}% (CME-gap proxy, OURS). "
                   f"Price came back to the Friday level at {hit[0]:%a %H:%M} UTC on Monday: gap closed.")
            return result(M, [box(M, t1, f"Weekend gap {100 * gap:+.1f}%", min(fri, mo), max(fri, mo), '#9467bd'),
                              hline(fri, "Fri 21:00 close (gap level)", t0, t1, '#9467bd'),
                              arrow(hit[0], fri, "Gap closed", up=(gap < 0), oy=(45 if gap < 0 else -45))],
                          cap, ev=M, win=(t0, t1), tf='15m')
        if held and not closed and further:
            cap = (f"Friday 21:00 UTC close {P(fri)} vs Monday 00:00 UTC open {P(mo)}: weekend gap {100 * gap:+.2f}% (CME-gap proxy, OURS). "
                   f"Price never returned to the Friday level on Monday and Monday closed at {P(mc)}, further in the gap direction.")
            return result(M, [box(M, t1, f"Weekend gap {100 * gap:+.1f}%", min(fri, mo), max(fri, mo), '#9467bd'),
                              hline(fri, "Fri 21:00 close (gap level)", t0, t1, '#9467bd'),
                              arrow(M + pd.Timedelta(hours=23, minutes=30), mc, "Gap still open at close", up=(gap < 0), oy=(45 if gap < 0 else -45), ox=-95)],
                          cap, ev=M, win=(t0, t1), tf='15m')
    return None


def f_tom12(cx, relax):
    g, l = thr(relax); a = arr5(cx); b = cx.b5; th = 0.003 * g
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 2, i0 - 1, -1):
        vah, poc = b.vahp.values[i], b.pocp.values[i]
        if np.isnan(vah): continue
        lvl = vah * (1 + th)
        if not (a['c'][i] >= lvl and a['c'][i - 1] < lvl): continue
        js = np.where(a['c'][i + 1:i + 25] < vah)[0]
        if not len(js): continue
        j = i + 1 + int(js[0])
        ks = np.where(a['l'][j + 1:j + 49] <= poc)[0]
        if not len(ks): continue
        k = j + 1 + int(ks[0]); D = b.index[i].normalize()
        cap = (f"5m close {P(a['c'][i])} was {100 * (a['c'][i] / vah - 1):.2f}% above the prior-day value-area high ({P(vah)}); within "
               f"{(j - i) * 5} min a 5m close came back below it, and price then reached the prior-day POC ({P(poc)}) {(k - j) * 5} min later.")
        return result(D, [arrow(b.index[i], a['h'][i], "Closes above value", up=True, oy=48, ox=-30),
                          arrow(b.index[j], a['c'][j], "Back below VAH", up=True, oy=60, ox=20),
                          arrow(b.index[k], poc, "Reaches POC", up=False, oy=-45)],
                      cap, ev=b.index[i], end=b.index[k] + pd.Timedelta(hours=1))
    return None


def f_tom14(cx, relax):
    g, l = thr(relax); m = cx.m
    o1, h1, l1, c1 = (m[k].values for k in ('o', 'h', 'l', 'c'))
    mv = c1 / np.roll(o1, 14) - 1; mv[:14] = 0
    mn, rt = 0.02 * g, 0.6 * g
    for D in reversed(cx.days):
        lo = m.index.searchsorted(D); hi = m.index.searchsorted(D + pd.Timedelta(days=1))
        if hi - lo < 1000: continue
        k = lo + int(np.abs(mv[lo:hi]).argmax())
        if abs(mv[k]) < mn or k + 361 > len(m): continue
        A, B = o1[k - 14], c1[k]
        if mv[k] > 0:
            ext = l1[k + 1:k + 361]; ei = k + 1 + int(ext.argmin()); r = (B - ext.min()) / (B - A); ev = ext.min()
        else:
            ext = h1[k + 1:k + 361]; ei = k + 1 + int(ext.argmax()); r = (ext.max() - B) / (A - B); ev = ext.max()
        if r < rt: continue
        cap = (f"Largest 15-minute move of {D:%d %b}: {100 * mv[k]:+.2f}% ({P(A)} to {P(B)}, ending {m.index[k]:%H:%M} UTC); "
               f"{100 * r:.0f}% of it was retraced within {(ei - k) / 60:.1f} h (to {P(ev)}).")
        up = mv[k] > 0
        return result(D, [box(m.index[k - 14], m.index[k] + MIN, f"15-min shock {100 * mv[k]:+.1f}%", min(A, B), max(A, B), '#d62728'),
                          arrow(m.index[ei], ev, f"Retraced {100 * r:.0f}%", up=up, oy=(45 if up else -45))],
                      cap, ev=m.index[k], end=m.index[ei] + pd.Timedelta(hours=1))
    return None


def f_tom15(cx, relax):
    g, l = thr(relax); b = cx.b1h; nc = int(np.floor(3 * g))
    o, h, lo, c = b.o.values, b.h.values, b.l.values, b.c.values
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 1, i0 - 1, -1):
        if i < 500: continue
        up = (c[i - nc + 1:i + 1] > o[i - nc + 1:i + 1]).all(); dn = (c[i - nc + 1:i + 1] < o[i - nc + 1:i + 1]).all()
        if up and h[i] >= h[i - 480:i].max():
            kind, lvl = 'high', h[i - 480:i].max()
        elif dn and lo[i] <= lo[i - 480:i].min():
            kind, lvl = 'low', lo[i - 480:i].min()
        else:
            continue
        D = b.index[i].normalize(); t = b.index[i]
        e = min(t + pd.Timedelta(hours=36), cx.end + MIN); s = e - pd.Timedelta(days=5)
        cap = (f"{nc} {'green' if kind == 'high' else 'red'} 1h candles in a row ending at a new 20-day {kind} "
               f"({P(h[i] if kind == 'high' else lo[i])}; previous 20-day {kind} {P(lvl)}), {t:%d %b %H:%M} UTC.")
        return result(D, [box(b.index[i - nc + 1], t + TFD['1h'], f"{nc} same-colour candles at 20-day {kind}", None, None, '#1f77b4'),
                          hline(lvl, f"previous 20-day {kind}", s, e, '#777777')],
                      cap, ev=t, win=(s, e), tf='1h')
    return None


def f_tom16(cx, relax):
    g, l = thr(relax); b = cx.b1h; a = arr5(cx); b5 = cx.b5; vm = 4 * g
    h, lo, v = b.h.values, b.l.values, b.v.values
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 7, i0 - 1, -1):
        if i < 730: continue
        med = np.median(v[i - 720:i])
        if v[i] < vm * med or h[i] < h[i - 720:i].max(): continue
        s5 = b5.index.searchsorted(b.index[i] + TFD['1h'])
        ks = np.where(a['c'][s5:s5 + 72] < lo[i])[0]
        if not len(ks): continue
        k = s5 + int(ks[0]); D = b.index[i].normalize()
        cap = (f"The {b.index[i]:%H:%M} UTC hour on {D:%d %b} printed a 30-day high ({P(h[i])}) with volume {v[i] / med:.1f}x the 30-day hourly median; "
               f"{'in the first 5m bar' if k == s5 else str((k - s5) * 5) + ' min'} after that hour ended a 5m close ({P(a['c'][k])}) fell below the hour's low ({P(lo[i])}).")
        return result(D, [box(b.index[i], b.index[i] + TFD['1h'], f"High-volume hour, {v[i] / med:.1f}x", lo[i], h[i], '#d62728'),
                          hline(lo[i], "spike-hour low", b.index[i], b.index[i] + pd.Timedelta(hours=9), '#d62728', 'end'),
                          arrow(b5.index[k], a['c'][k], "Closes below spike-hour low", up=False, oy=-45)],
                      cap, ev=b.index[i], end=b5.index[k] + pd.Timedelta(hours=1))
    return None


def lvn_band(pr):
    s = pr['hist']; idx = s.index.values
    best = None
    start = int(np.ceil(pr['val'] / 50.0) * 50)
    while start + 50 <= pr['vah']:
        v = s.reindex(np.arange(start, start + 50, 10), fill_value=0.0).sum()
        if best is None or v < best[0]: best = (v, start)
        start += 50
    return best


def f_tom17(cx, relax):
    g, l = thr(relax); m = cx.m; tr = 0.003 * g
    c1, h1, l1 = m.c.values, m.h.values, m.l.values
    for D in reversed(cx.days):
        pd_ = D - pd.Timedelta(days=1)
        if pd_ not in cx.prof: continue
        bd_ = lvn_band(cx.prof[pd_])
        if bd_ is None: continue
        bl = bd_[1]; bh = bl + 50
        lo = m.index.searchsorted(D); hi = m.index.searchsorted(D + pd.Timedelta(days=1))
        for k in range(hi - 16, lo + 90, -1):
            inside = bl <= c1[k] <= bh and not (bl <= c1[k - 1] <= bh)
            if not inside: continue
            up_ = (h1[k + 1:k + 16].max() - c1[k]) / c1[k]; dn_ = (c1[k] - l1[k + 1:k + 16].min()) / c1[k]
            if max(up_, dn_) < tr: continue
            t = m.index[k]
            cap = (f"Prior-day profile's thinnest 50-USD band inside its value area is {P(bl)}-{P(bh)}. Price entered it at {t:%H:%M} UTC and "
                   f"travelled {100 * max(up_, dn_):.2f}% {'up' if up_ >= dn_ else 'down'} in the next 15 minutes (thin zone = little trading there before).")
            return result(D, [box(t - pd.Timedelta(hours=1, minutes=30), t + pd.Timedelta(hours=1, minutes=30), "Thin zone (lowest-volume band)", bl, bh, '#9467bd'),
                              arrow(t, c1[k], "Price enters thin zone", up=(up_ < dn_), oy=(-45 if up_ < dn_ else 45)),
                              box(t, t + pd.Timedelta(minutes=15), "Next 15 min", None, None, '#ff7f0e')],
                          cap, ev=t, win=(t - pd.Timedelta(hours=1, minutes=30), t + pd.Timedelta(hours=1, minutes=30)), tf='1m')
    return None


def f_fab1(cx, relax):
    g, l = thr(relax); a = arr5(cx); b = cx.b5
    cvd5 = np.cumsum(a['d']); abs72 = np.abs(cvd5[72:] - cvd5[:-72])
    maxr = 0.01 * l; cm = 1.5 * g; frac = 0.75 if relax else 10 / 12; vm = 2 * g
    i0 = b.index.searchsorted(cx.s0)
    med_cache = {}
    for i in range(len(b) - 1, i0 - 1, -1):
        bal = balance(cx, i - 1, maxr, 72)
        if bal is None: continue
        st, hi, lo = bal; e = i - 1
        s = cvd5[e - 72:e + 1:6]; net = s[-1] - s[0]
        if net == 0: continue
        up = net > 0
        if (up and a['c'][i] <= hi) or ((not up) and a['c'][i] >= lo): continue
        fr = (np.sign(np.diff(s)) == np.sign(net)).mean()
        if fr < frac: continue
        D = b.index[i].normalize()
        if D not in med_cache:
            q = b.index.searchsorted(D)
            med_cache[D] = np.median(abs72[max(0, q - 8640 - 72):q - 72:3]) if q > 8800 else np.nan
        med6 = med_cache[D]
        if np.isnan(med6) or abs(net) < cm * med6: continue
        med = np.median(a['v'][st:i])
        if a['v'][i] < vm * med: continue
        cap = (f"{(i - st) * 5 / 60:.1f} h{'+ (look-back capped at 24 h)' if i - st >= 288 else ''} balance (5m range {P(lo)}-{P(hi)}, {100 * (hi / lo - 1):.2f}%) while the CVD proxy {'climbed' if up else 'fell'} steadily "
               f"({100 * fr:.0f}% of half-hour steps in one direction, net {net:+,.0f} BTC = {abs(net) / med6:.1f}x the 30-day 6h median), then the first 5m close "
               f"{'above' if up else 'below'} the balance at {P(a['c'][i])} with volume {a['v'][i] / med:.1f}x the balance median.")
        return result(D, [box(b.index[st], b.index[i], f"{(i - st) * 5 / 60:.0f}h{'+' if i - st >= 288 else ''} balance, CVD {'rising' if up else 'falling'}", lo, hi, '#1f77b4'),
                          arrow(b.index[i], a['h'][i] if up else a['l'][i], f"Break on {a['v'][i] / med:.1f}x volume", up=up, oy=(45 if up else -45))],
                      cap, ev=b.index[i], end=b.index[i] + pd.Timedelta(hours=2), cvd=True)
    return None


def f_fab2(cx, relax):
    g, l = thr(relax); b = cx.b15; m = cx.m
    sel = b.index >= cx.s0
    ad = np.abs(b.d.values); ar = np.abs(b.c.values - b.o.values) / b.o.values
    qh = np.quantile(ad[sel], 1 - 0.02 * l); ql = np.quantile(ar[sel], 0.30 * l); mvt = 0.005 * g
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 9, i0 - 1, -1):
        if ad[i] < qh or ar[i] > ql: continue
        cl = b.c.values[i]
        if b.d.values[i] > 0:
            ext = b.l.values[i + 1:i + 9]; mvv = (cl - ext.min()) / cl; ei = i + 1 + int(ext.argmin()); px = ext.min()
        else:
            ext = b.h.values[i + 1:i + 9]; mvv = (ext.max() - cl) / cl; ei = i + 1 + int(ext.argmax()); px = ext.max()
        if mvv < mvt: continue
        sgn = 'buying' if b.d.values[i] > 0 else 'selling'
        D = b.index[i].normalize()
        cap = (f"15-min window {b.index[i]:%H:%M} UTC: aggressive {sgn} (delta proxy {b.d.values[i]:+,.0f} BTC, top {100 * 0.02 * l:.1f}% of the last 120 days) "
               f"but price moved only {100 * ar[i]:.2f}% (bottom {100 * 0.30 * l:.0f}%). Within 2h price then moved {100 * mvv:.2f}% the other way.")
        return result(D, [box(b.index[i], b.index[i] + TFD['15m'], f"Heavy {sgn}, no progress", b.l.values[i], b.h.values[i], '#9467bd'),
                          arrow(b.index[ei], px, "Move against the delta", up=(b.d.values[i] < 0), oy=(45 if b.d.values[i] < 0 else -45))],
                      cap, ev=b.index[i], end=b.index[ei] + pd.Timedelta(hours=1), cvd=True)
    return None


def f_fab4(cx, relax):
    g, l = thr(relax); a = arr5(cx); b = cx.b5; th = 0.002 * g
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 8, i0 - 1, -1):
        vah, val = b.vahp.values[i], b.valp.values[i]
        if np.isnan(vah): continue
        for side in (1, -1):
            lvl = vah * (1 + th) if side > 0 else val * (1 - th)
            out = a['c'][i] >= lvl if side > 0 else a['c'][i] <= lvl
            prev_out = a['c'][i - 1] >= lvl if side > 0 else a['c'][i - 1] <= lvl
            if not out or prev_out: continue
            inn = (a['c'][i + 1:i + 7] <= vah) if side > 0 else (a['c'][i + 1:i + 7] >= val)
            js = np.where(inn)[0]
            if not len(js): continue
            j = i + 1 + int(js[0])
            if side > 0:
                ks = np.where(a['l'][j + 1:j + 73] <= val)[0]
            else:
                ks = np.where(a['h'][j + 1:j + 73] >= vah)[0]
            if not len(ks): continue
            k = j + 1 + int(ks[0]); D = b.index[i].normalize()
            edge = val if side > 0 else vah
            cap = (f"5m close {P(a['c'][i])} was {100 * th:.1f}%+ {'above the prior-day value-area high' if side > 0 else 'below the prior-day value-area low'} "
                   f"({P(vah if side > 0 else val)}); {(j - i) * 5} min later it was back inside, and {(k - j) * 5 // 60}h{(k - j) * 5 % 60:02d}m after that price reached "
                   f"the opposite edge ({P(edge)}).")
            return result(D, [arrow(b.index[i], a['h'][i] if side > 0 else a['l'][i], "Breakout close outside value", up=(side > 0), oy=(48 if side > 0 else -48), ox=-30),
                              arrow(b.index[j], a['c'][j], "Back inside value", up=(side > 0), oy=(62 if side > 0 else -62), ox=25),
                              arrow(b.index[k], edge, "Reaches opposite edge", up=(side < 0), oy=(45 if side < 0 else -45))],
                          cap, ev=b.index[i], end=b.index[k] + pd.Timedelta(hours=1), cvd=True)
    return None


def f_fab5(cx, relax):
    g, l = thr(relax); b = cx.b15; tch = 0.001 * l; rise = 0.007 * g
    i0 = b.index.searchsorted(cx.s0)
    for i in range(len(b) - 9, i0 - 1, -1):
        val = b.valp.values[i]
        if np.isnan(val): continue
        if not (abs(b.l.values[i] - val) / val <= tch) or b.d.values[i] >= 0: continue
        cl = b.c.values[i]; hh = b.h.values[i + 1:i + 9]; kp = i + 1 + int(hh.argmax())
        if (hh.max() - cl) / cl < rise: continue
        if b.l.values[i:kp + 1].min() < val * (1 - tch): continue
        D = b.index[i].normalize()
        cap = (f"15-min bar {b.index[i]:%H:%M} UTC touched the prior-day value-area low ({P(val)}, low {P(b.l.values[i])}) with a negative delta proxy "
               f"({b.d.values[i]:+,.0f} BTC: sellers aggressive) yet the low held, and price rose {100 * (hh.max() - cl) / cl:.2f}% within 2 h.")
        return result(D, [box(b.index[i], b.index[i] + TFD['15m'], "Sellers hit value low, it holds", b.l.values[i] * 0.9995, b.h.values[i], '#9467bd'),
                          arrow(b.index[kp], hh.max(), f"Rises {100 * (hh.max() - cl) / cl:.1f}%", up=False, oy=-45)],
                      cap, ev=b.index[i], end=b.index[kp] + pd.Timedelta(hours=1), cvd=True)
    return None


def f_fab6(cx, relax):
    b = cx.b5; a = arr5(cx)
    for D in reversed(cx.days):
        if D.weekday() > 4: continue
        s = b.index.searchsorted(D + pd.Timedelta(hours=13, minutes=30)); e = b.index.searchsorted(D + pd.Timedelta(hours=14))
        if e - s != 6: continue
        hi, lo = a['h'][s:e].max(), a['l'][s:e].min()
        q = b.index.searchsorted(D + pd.Timedelta(hours=21))
        out = np.where((a['c'][e:q] > hi) | (a['c'][e:q] < lo))[0]
        if not len(out): continue
        k = e + int(out[0]); up = a['c'][k] > hi
        cap = (f"First 30 minutes of the US open (13:30-14:00 UTC) ranged {P(lo)}-{P(hi)} ({100 * (hi / lo - 1):.2f}%). The first 5m close outside it was "
               f"{b.index[k]:%H:%M} UTC at {P(a['c'][k])} ({'above' if up else 'below'}).")
        return result(D, [box(b.index[s], b.index[e], "First 30 min box", lo, hi, '#1f77b4'),
                          arrow(b.index[k], a['c'][k], "First close outside box", up=(not up), oy=(-45 if up else 45))],
                      cap, ev=b.index[s], win=(D + pd.Timedelta(hours=12), D + pd.Timedelta(hours=21)), cvd=True)
    return None


def zigzag(h, lo, thr_):
    piv = []; n = len(h); hi_i = lo_i = 0; trend = 0; ext = 0
    for i in range(1, n):
        if trend == 0:
            if h[i] > h[hi_i]: hi_i = i
            if lo[i] < lo[lo_i]: lo_i = i
            if lo_i < i and (h[i] - lo[lo_i]) / lo[lo_i] >= thr_:
                piv.append((lo_i, 'L')); trend = 1; ext = lo_i + int(np.argmax(h[lo_i:i + 1]))
            elif hi_i < i and (h[hi_i] - lo[i]) / h[hi_i] >= thr_:
                piv.append((hi_i, 'H')); trend = -1; ext = hi_i + int(np.argmin(lo[hi_i:i + 1]))
        elif trend == 1:
            if h[i] > h[ext]: ext = i
            elif (h[ext] - lo[i]) / h[ext] >= thr_:
                piv.append((ext, 'H')); trend = -1; ext = i
        else:
            if lo[i] < lo[ext]: ext = i
            elif (h[i] - lo[ext]) / lo[ext] >= thr_:
                piv.append((ext, 'L')); trend = 1; ext = i
    return piv


def f_fab8(cx, relax):
    g, l = thr(relax); b = cx.b1h; m = cx.m; sw = 0.02 * g
    piv = zigzag(b.h.values, b.l.values, sw)
    c1, h1, l1 = m.c.values, m.h.values, m.l.values
    for q in range(len(piv) - 2, -1, -1):
        (ia, ta), (ib, tb) = piv[q], piv[q + 1]
        A = b.l.values[ia] if ta == 'L' else b.h.values[ia]
        B = b.h.values[ib] if tb == 'H' else b.l.values[ib]
        if (ib - ia) > 72 or abs(B - A) / A < sw: continue
        tA, tB = b.index[ia], b.index[ib]
        seg = m.loc[tA:tB + pd.Timedelta(minutes=59)]
        if len(seg) < 60: continue
        pr = profile_of(seg); bd_ = lvn_band(pr)
        if bd_ is None: continue
        bl = bd_[1]; bh = bl + 50
        s = m.index.searchsorted(tB + pd.Timedelta(hours=1)); e = min(len(m), s + 36 * 60)
        hit = np.where((l1[s:e] <= bh) & (h1[s:e] >= bl))[0]
        if not len(hit): continue
        r = s + int(hit[0]); tr = m.index[r]
        if tr + pd.Timedelta(hours=2) > cx.end: continue
        D = tr.normalize()
        t0 = min(tA - pd.Timedelta(hours=2), D - pd.Timedelta(days=1)); t1 = tr + pd.Timedelta(hours=3)
        direction = 'up' if tb == 'H' else 'down'
        cap = (f"Swing {direction} {P(A)} -> {P(B)} ({100 * abs(B - A) / A:.1f}% in {(ib - ia)}h, A {tA:%d %b %H:%M}, B {tB:%d %b %H:%M}). Fixed-range 1m profile A->B: "
               f"70% value area {P(pr['val'])}-{P(pr['vah'])}, thinnest 50-USD band inside it {P(bl)}-{P(bh)}. Price returned to that band at {tr:%d %b %H:%M} UTC (next 2 h shown).")
        return result(D, [box(tB + pd.Timedelta(hours=1), t1, "Thin zone of the swing (lowest volume)", bl, bh, '#9467bd'),
                          arrow(tA, A, "A: swing start", up=(ta == 'H'), oy=(-45 if ta == 'L' else 45), ox=0),
                          arrow(tB, B, "B: swing end", up=(tb == 'L'), oy=(45 if tb == 'H' else -45)),
                          arrow(tr, (bl + bh) / 2, "Price returns to thin zone", up=(tb == 'H'), oy=(-50 if tb == 'H' else 50), ox=-10)],
                      cap, ev=tr, win=(t0, t1))
    return None


# ----------------------------------------------------------------------------------------------- setups
SETUPS = [
    ('TOM-1a', 'imbalance fade', f_tom1a, 'a push of >=1.5% within 2h that ends >=0.5% above the prior-day value-area high, then gives back >=50% of the push within 4h'),
    ('TOM-1b', 'swing top', f_tom1b, 'daily: >=3 consecutive up days, then a day closing in its lower third with the high above the prior 10 days'),
    ('TOM-2', 'counter trade in balance', f_tom2, 'UTC day with range <60% of the median range of the prior 20 days, high and low both inside the prior-day value area'),
    ('TOM-3', 'limit sell below the last volume step', f_tom3, 'daily: inside day right under a 20-day high after >=5 up days of the last 10'),
    ('TOM-4', 'trend continuation pullback', f_tom4, 'day with close-open >=+1.5%; after 06:00 UTC price touched the UTC-day VWAP, stayed within 0.2% for >=3 5m bars, then made a new day high'),
    ('TOM-6', 'breakout', f_tom6, '>=6h with 5m range <0.8%, then a 5m close above the range high with 5m volume >=2x the balance median'),
    ('TOM-7', 'VWAP scalp', f_tom7, 'day with range <1.2% where the 5m close crosses the UTC-day VWAP >=8 times'),
    ('TOM-8', 'gap close (CME-gap proxy)', lambda cx, r: f_gap(cx, r, False), 'Monday 00:00 UTC open vs Friday 21:00 UTC close differ by >=0.8% and the gap is closed within the Monday'),
    ('TOM-9', 'gap holds (CME-gap proxy)', lambda cx, r: f_gap(cx, r, True), 'same gap proxy, NOT closed within Monday and Monday closes further in the gap direction'),
    ('TOM-10', 'closing-auction reversal', None, 'NO BTC equivalent (24/7 market, no closing auction)'),
    ('TOM-11', 'cross-market lead (crude oil vs index)', None, 'NO data on disk for crude oil / index'),
    ('TOM-12', 'break-in', f_tom12, '5m close >=0.3% above the prior-day VAH, within 2h a 5m close back below VAH, then price reaches the prior-day POC within 4h'),
    ('TOM-14', 'news shock V reversal', f_tom14, "day's largest 15-minute move >=2%, then >=60% retraced within 6h"),
    ('TOM-15', 'candle formations at a range edge', f_tom15, 'three same-colour 1h candles ending at a 20-day high or low'),
    ('TOM-16', 'top after forced buying', f_tom16, 'hour with volume >=4x the 30-day hourly median at a 30-day high, then a 5m close below that hour low within 6h'),
    ('TOM-17', 'low-volume-node scalp', f_tom17, "price enters the prior-day profile's lowest-volume 50-USD band inside the value area and the next 15 min travel >=0.3%"),
    ('FAB-1', 'balance with CVD pressure, break on volume', f_fab1, '>=6h with 5m range <1% while the CVD proxy moves (near-)monotonically >=1.5x its 30-day 6h median move, then first 5m close outside in the CVD direction with volume >=2x balance median'),
    ('FAB-2', 'absorbed push', f_fab2, '15-min window with |delta proxy| in the top 2% but price change in the bottom 30%, then >=0.5% move against the delta sign within 2h'),
    ('FAB-4', 'failed breakout back into balance', f_fab4, '5m close >=0.2% outside the prior-day value area, back inside within 30 min, then reaches the opposite edge within 6h'),
    ('FAB-5', 'buyers protect a level', f_fab5, 'touch of prior-day VAL within 0.1% with negative 15-min delta proxy, low holds, then +0.7% within 2h'),
    ('FAB-6', 'IVB first 30 minutes of the US open', f_fab6, 'weekday 13:30-14:00 UTC range, then a 5m close outside it'),
    ('FAB-8', 'volume-defined fair value gap', f_fab8, 'last swing A->B >=2% within 3 days, fixed-range 1m profile A->B, lowest-volume 50-USD band inside its value area, price returns to it'),
]
CVD_IDS = {'FAB-1', 'FAB-2', 'FAB-4', 'FAB-5', 'FAB-6', 'FAB-8'}
DAILY_IDS = {'TOM-1b', 'TOM-3'}
NOLEVEL_IDS = {'TOM-1b', 'TOM-3', 'TOM-15'}   # multi-week / hourly views: levels and VWAP of one day make no sense
RELAX_NOTE = {True: 'relaxed: every threshold loosened by 25% once (no strict match in the last 120 days)', False: 'strict rule matched'}


# --------------------------------------------------------------------------------------------- drawing
def default_win(cx, r):
    D = r['D']; t0 = D - pd.Timedelta(days=1); t1 = D + pd.Timedelta(days=1)
    if r.get('end') is not None and r['end'] > t1:
        t1 = (r['end'] + pd.Timedelta(hours=1)).ceil('h')
    return t0, min(t1, cx.end + MIN)


def draw(cx, sid, name, r, status, path):
    tf = r['tf']; D = r['D']
    t0, t1 = r['win'] if r.get('win') else default_win(cx, r)
    full = cx.bars[tf]
    b = full[(full.index >= t0) & (full.index < t1)]
    w = TFW[tf]
    x = mdates.date2num(b.index.values) + w / 2
    use_cvd = r.get('cvd', False) and sid in CVD_IDS
    show_lv = tf in ('1m', '5m', '15m') and sid not in NOLEVEL_IDS
    nrow = 3 if use_cvd else 2
    tfn = {'1m': '1-minute', '5m': '5-minute', '15m': '15-minute', '1h': '1-hour', '1d': 'daily'}[tf]
    lines = [f"What you are looking at: {r['caption']}",
             f"Candles: {tfn}, UTC. Green = close above open. Status: {status}. A picture of the conditions only, not a trade signal."]
    if show_lv:
        lines.append("Orange = UTC-day VWAP, OURS anchor: BTC has no open. Blue dashed + shading = prior-day value area (70%, 10-USD bins); purple = prior-day POC (most-traded price).")
    wrapped = '\n'.join(textwrap.fill(s_, 175) for s_ in lines)
    fig, axs = plt.subplots(nrow, 1, figsize=(12, 7.6), dpi=110, sharex=True,
                            gridspec_kw={'height_ratios': [5, 1.2, 1.7][:nrow], 'hspace': 0.06})
    fig.subplots_adjust(left=0.065, right=0.90 if show_lv else 0.97, top=0.945, bottom=0.115 + 0.012 * wrapped.count('\n'))
    ax, av = axs[0], axs[1]
    axh = ax.get_position().height * 7.6 * 72; axw = ax.get_position().width * 12 * 72
    up = (b.c.values >= b.o.values)
    col = np.where(up, UP, DN)
    body = np.maximum(np.abs(b.c.values - b.o.values), b.c.values * 0.00015)
    ax.vlines(x, b.l.values, b.h.values, color=col, lw=0.8, zorder=2)
    ax.bar(x, body, bottom=np.minimum(b.o.values, b.c.values), width=w * 0.72, color=col, zorder=3, linewidth=0)
    av.bar(x, b.v.values, width=w * 0.8, color=col, alpha=0.6)
    av.set_ylabel('volume (BTC)', fontsize=8)
    lo_, hi_ = b.l.values.min(), b.h.values.max()
    has_arrow = any(mk['kind'] == 'arrow' for mk in r['marks'])
    pad = (hi_ - lo_) * (0.13 if has_arrow else 0.07)
    ymin, ymax = lo_ - pad, hi_ + pad
    ax.set_ylim(ymin, ymax); ax.set_xlim(mdates.date2num(t0), mdates.date2num(t1))
    xl = mdates.date2num(t0); xr = mdates.date2num(t1); xspan = xr - xl
    off = []
    # prior-day levels (in force from the example day's 00:00) + UTC-day VWAP
    if show_lv:
        pd_ = D - pd.Timedelta(days=1)
        xs0 = max(mdates.date2num(D), mdates.date2num(t0))
        if pd_ in cx.prof:
            pr = cx.prof[pd_]
            ax.axhspan(max(pr['val'], ymin), min(pr['vah'], ymax), xmin=(xs0 - xl) / xspan, color='#1f77b4', alpha=0.07, zorder=0)
            for nm, v, c_, ls, lw_ in (('prior-day VAH', pr['vah'], '#1f77b4', '--', 1.2), ('prior-day VAL', pr['val'], '#1f77b4', '--', 1.2), ('prior-day POC', pr['poc'], '#7b3294', '-', 1.8)):
                if ymin <= v <= ymax:
                    ax.hlines(v, xs0, xr, color=c_, ls=ls, lw=lw_, zorder=1)
                    ax.text(xr, v, f' {nm} {P(v)}', fontsize=7.5, color=c_, va='center', ha='left', clip_on=False)
                else:
                    off.append(f"{nm} {P(v)}")
        vw = cx.vw1.loc[max(D, t0):min(D + pd.Timedelta(days=1) - MIN, t1 - MIN)]
        vw = vw.resample({'1m': '1min', '5m': '5min', '15m': '15min', '1h': '1h'}[tf]).last().dropna()
        if len(vw):
            if vw.max() < ymin or vw.min() > ymax:
                off.append(f"UTC-day VWAP {P(vw.iloc[-1])}")
            xv = mdates.date2num(vw.index.values) + w / 2
            ax.plot(xv, vw.values, color='#ff7f0e', lw=1.6, zorder=4)
            ax.text(xv[-1], vw.values[-1], ' UTC-day VWAP', fontsize=7.5, color='#ff7f0e', va='center', ha='left', clip_on=False)
        # shading + labels for prior day / example day
        if t0 <= D - pd.Timedelta(days=1):
            ax.axvspan(mdates.date2num(max(t0, D - pd.Timedelta(days=1))), mdates.date2num(D), color='#888888', alpha=0.06, zorder=0)
            ax.text(mdates.date2num(max(t0, D - pd.Timedelta(days=1))) + 0.01, ymax - pad * 0.08, 'PRIOR DAY (its volume profile gives the lines)', fontsize=7.5, color='#555', va='top')
        ax.text(mdates.date2num(D) + 0.01, ymax - pad * 0.08, 'EXAMPLE DAY', fontsize=7.5, color='#555', va='top')
    # marks
    for mk in r['marks']:
        k = mk['kind']
        if k == 'box':
            xa, xb = mdates.date2num(mk['x0']), mdates.date2num(mk['x1'])
            if xb - xa < 0.012 * xspan:
                cmid = (xa + xb) / 2; xa, xb = cmid - 0.006 * xspan, cmid + 0.006 * xspan
            ya = mk['y0'] if mk['y0'] is not None else ymin; yb = mk['y1'] if mk['y1'] is not None else ymax
            if mk['y0'] is not None:
                padb = (yb - ya) * 0.03 + (ymax - ymin) * 0.004; ya -= padb; yb += padb
            ax.add_patch(Rectangle((xa, ya), xb - xa, yb - ya, fill=True, facecolor=mk['color'], alpha=0.14, edgecolor=mk['color'], lw=1.6, zorder=1.5))
            ax.add_patch(Rectangle((xa, ya), xb - xa, yb - ya, fill=False, edgecolor=mk['color'], lw=1.6, zorder=5))
            right = xa > xl + 0.55 * xspan
            lx = min(xb, xr - 0.003 * xspan) if right else max(xa, xl)
            if mk['y1'] is not None:
                ty, va_ = min(yb, ymax - (ymax - ymin) * 0.04), 'bottom'
            else:
                ty, va_ = ymin + (ymax - ymin) * 0.02, 'bottom'
            ax.text(lx, ty, ' ' + mk['label'] + ' ', fontsize=8.5, fontweight='bold', color=mk['color'], va=va_,
                    ha='right' if right else 'left', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec=mk['color'], alpha=0.9), zorder=8, clip_on=True)
            if use_cvd:
                axs[2].axvspan(xa, xb, color=mk['color'], alpha=0.14)
        elif k == 'arrow':
            xx = mdates.date2num(mk['x']) + w / 2
            fr = (mk['y'] - ymin) / (ymax - ymin)
            oy = mk['oy']; need = 30
            avail_up, avail_dn = (1 - fr) * axh, fr * axh
            if oy > 0 and oy + need > avail_up:
                oy = -abs(oy) if avail_dn > avail_up else max(14, avail_up - need)
            elif oy < 0 and -oy + need > avail_dn:
                oy = abs(oy) if avail_up > avail_dn else -max(14, avail_dn - need)
            half = 2.7 * len(mk['label']) + 6
            ox = mk['ox']
            dr, dl = (xr - xx) / xspan * axw, (xx - xl) / xspan * axw
            ox = max(-(dl - half), min(ox, dr - half))
            ax.annotate(mk['label'], xy=(xx, mk['y']), xytext=(ox, oy), textcoords='offset points', fontsize=8.5, fontweight='bold', ha='center',
                        va='bottom' if oy > 0 else 'top', arrowprops=dict(arrowstyle='-|>', color='#222', lw=1.4), color='#222',
                        bbox=dict(boxstyle='round,pad=0.25', fc='#fff7c2', ec='#222', alpha=0.95), zorder=9, annotation_clip=False)
        elif k == 'hline':
            if ymin <= mk['y'] <= ymax:
                x0_, x1_ = max(mdates.date2num(mk['x0']), xl), min(mdates.date2num(mk['x1']), xr)
                ax.hlines(mk['y'], x0_, x1_, color=mk['color'], ls=':', lw=1.6, zorder=2)
                bb = dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.8)
                if mk.get('pos') == 'end':
                    ax.text(x1_, mk['y'], mk['label'] + ' ', fontsize=8, color=mk['color'], va='top', ha='right', bbox=bb, zorder=8)
                elif x0_ > xl + 0.15 * xspan:
                    ax.text(x0_ - 0.004 * xspan, mk['y'], mk['label'] + ' ', fontsize=8, color=mk['color'], va='bottom', ha='right', bbox=bb, zorder=8)
                else:
                    ax.text(x0_ + 0.006 * xspan, mk['y'], ' ' + mk['label'], fontsize=8, color=mk['color'], va='bottom', ha='left', bbox=bb, zorder=8)
        elif k == 'dots':
            ax.scatter(mdates.date2num(pd.DatetimeIndex(mk['xs']).values) + w / 2, mk['ys'], s=38, color=mk['color'], edgecolor='k', zorder=7, label=mk['label'])
            ax.legend(loc='upper right', fontsize=8)
    if off:
        ax.text(0.005, 0.015, 'Off-scale (outside this view): ' + '; '.join(off), transform=ax.transAxes, fontsize=7.5, color='#555', va='bottom')
    if use_cvd:
        cv = np.cumsum(b.d.values)
        axs[2].plot(x, cv, color='#4c4c4c', lw=1.3)
        axs[2].axhline(0, color='#aaa', lw=0.6)
        axs[2].set_ylabel('CVD proxy (BTC)', fontsize=8)
        axs[2].text(0.005, 0.93, 'CVD proxy from taker volume, OURS (taker-buy minus taker-sell, running sum from chart start)', transform=axs[2].transAxes, fontsize=7.5, va='top', color='#333')
    # axes cosmetics
    span = (t1 - t0) / pd.Timedelta(days=1)
    last = axs[-1]
    if tf == '1d':
        last.xaxis.set_major_locator(mdates.DayLocator(interval=5)); last.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    else:
        if span <= 0.2: loc = mdates.MinuteLocator(byminute=range(0, 60, 15))
        elif span <= 0.5: loc = mdates.HourLocator()
        elif span <= 1.6: loc = mdates.HourLocator(byhour=range(0, 24, 2))
        elif span <= 3.2: loc = mdates.HourLocator(byhour=range(0, 24, 6))
        elif span <= 6.5: loc = mdates.HourLocator(byhour=(0, 12))
        else: loc = mdates.DayLocator()
        last.xaxis.set_major_locator(loc); last.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
    for a_ in axs:
        a_.grid(True, color='#ddd', lw=0.5, zorder=0)
        a_.tick_params(labelsize=8)
    for a_ in axs[:-1]:
        a_.tick_params(labelbottom=False)
    if tf != '1d':
        d_ = t0.normalize() + pd.Timedelta(days=1)
        while d_ < t1:
            for a_ in axs:
                a_.axvline(mdates.date2num(d_), color='#555', lw=0.9, ls='-', alpha=0.5, zorder=1)
            d_ += pd.Timedelta(days=1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylabel('BTCUSDT (USD)', fontsize=8)
    dstr = f"{D:%Y-%m-%d}"
    fig.suptitle(f"{sid} {name} | {dstr} | example chosen by OURS rule", fontsize=12.5, fontweight='bold', x=0.06, ha='left', y=0.985)
    fig.text(0.06, 0.012, wrapped, fontsize=8, va='bottom', ha='left', color='#222')
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return (t0, t1, tfn)


def plain_result(cx, sid):
    D = cx.end_day
    if sid in DAILY_IDS:
        n = len(cx.bd)
        return result(cx.bd.index[-1], [], 'No rule match: plain recent chart (last 45 daily candles).', win=(cx.bd.index[n - 45], cx.bd.index[-1] + pd.Timedelta(days=1)), tf='1d')
    if sid in ('TOM-8', 'TOM-9'):
        M = [d for d in cx.days if d.weekday() == 0][-1]
        return result(M, [], 'No rule match: plain recent chart (latest Friday 20:00 to Monday 24:00).', win=(M - pd.Timedelta(days=3) + pd.Timedelta(hours=20), M + pd.Timedelta(days=1)), tf='15m')
    if sid == 'TOM-15':
        return result(D, [], 'No rule match: plain recent chart (last 5 days of 1h candles).', win=(cx.end_day + pd.Timedelta(days=1) - pd.Timedelta(days=5), cx.end_day + pd.Timedelta(days=1)), tf='1h')
    if sid == 'FAB-6':
        D = [d for d in cx.days if d.weekday() < 5][-1]
        return result(D, [], 'No rule match: plain recent chart.', win=(D + pd.Timedelta(hours=12), D + pd.Timedelta(hours=21)), cvd=True)
    return result(D, [], 'No rule match: plain recent chart (latest full UTC day and the day before).', cvd=True)


# ------------------------------------------------------------------------------------------------ main
def main():
    t00 = time.time()
    os.makedirs(OUT, exist_ok=True)
    cx = build()
    print(f"archive end {cx.end:%Y-%m-%d %H:%MZ}; search {cx.s0:%Y-%m-%d} .. {cx.end_day:%Y-%m-%d} ({SEARCH_DAYS} d); files {len(cx.files)}; minute gaps {cx.gaps}; loaded in {time.time() - t00:.0f}s")
    rows = []
    for sid, name, fn, rule in SETUPS:
        png = os.path.join(OUT, f"{sid}.png")
        if fn is None:
            if os.path.exists(png): os.remove(png)
            rows.append(dict(id=sid, name=name, date_utc=None, window=None, selection_rule=rule, note='no BTC equivalent' if sid == 'TOM-10' else 'no BTC equivalent: no crude-oil or index data on disk',
                             status='none', png=None))
            print(f"{sid:7s} | -          | no BTC equivalent (no PNG)")
            continue
        r = fn(cx, False); status = 'match'
        if r is None:
            r = fn(cx, True); status = 'relaxed'
        if r is None:
            r = plain_result(cx, sid); status = 'none'
        stxt = {'match': 'strict rule matched', 'relaxed': RELAX_NOTE[True], 'none': 'no rule match: plain recent chart'}[status]
        t0, t1, tfn = draw(cx, sid, name, r, stxt, png)
        note = ('no rule match: plain recent chart. ' if status == 'none' else ('RELAXED threshold (-/+25%): ' if status == 'relaxed' else '')) + r['caption']
        rows.append(dict(id=sid, name=name, date_utc=f"{r['D']:%Y-%m-%d}", window=f"{t0:%Y-%m-%d %H:%M}Z to {t1:%Y-%m-%d %H:%M}Z, {tfn} candles",
                         selection_rule=rule + ('; relaxed by 25% once' if status == 'relaxed' else ''), note=note, status=status, png=f"examples/{sid}.png"))
        print(f"{sid:7s} | {r['D']:%Y-%m-%d} | {status}")
    with open(os.path.join(HERE, 'examples.json'), 'w', newline='\n', encoding='utf-8') as f:
        json.dump(rows, f, indent=1, ensure_ascii=False); f.write('\n')
    pngs = [p for p in os.listdir(OUT) if p.endswith('.png')]
    tot = sum(os.path.getsize(os.path.join(OUT, p)) for p in pngs)
    print(f"{len(pngs)} PNG, {tot / 1e6:.1f} MB; total {time.time() - t00:.0f}s")


if __name__ == '__main__':
    main()
