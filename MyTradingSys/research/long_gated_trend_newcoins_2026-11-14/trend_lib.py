"""Per-coin signal state machines for the 10 pre-registered rules. Each returns W[d] = signed weight SET AT THE CLOSE of day d
(uses bars <= d only). The caller shifts by one day (fill at next open). NaN inputs -> flat."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest", "layers", "adx")))
from adx import adx_di

RISK, FLOOR, CAP = 0.01, 0.01, 0.5


def size(dist):
    return float(np.clip(RISK / max(dist, FLOOR), 0.0, CAP))


def _roll(a, n, fn):
    """fn over the PREVIOUS n values (excluding today); NaN if any NaN / not enough history."""
    out = np.full(len(a), np.nan)
    for i in range(n, len(a)):
        w = a[i - n:i]
        if not np.isnan(w).any(): out[i] = fn(w)
    return out


def sma(a, n):
    out = np.full(len(a), np.nan)
    for i in range(n - 1, len(a)):
        w = a[i - n + 1:i + 1]
        if not np.isnan(w).any(): out[i] = w.mean()
    return out


def donchian(h, l, c, n_in, n_out):
    hh, ll = _roll(h, n_in, np.max), _roll(l, n_in, np.min)
    ho, lo = _roll(h, n_out, np.max), _roll(l, n_out, np.min)
    W = np.zeros(len(c)); s = 0; w = 0.0
    for d in range(len(c)):
        if np.isnan(hh[d]) or np.isnan(ho[d]) or np.isnan(c[d]):
            s = 0; w = 0.0
        else:
            if s == 1 and c[d] < lo[d]: s = 0
            elif s == -1 and c[d] > ho[d]: s = 0
            if s == 0:
                if c[d] > hh[d]: s = 1; w = size((c[d] - lo[d]) / c[d])
                elif c[d] < ll[d]: s = -1; w = size((ho[d] - c[d]) / c[d])
        W[d] = s * w if s else 0.0
    return W


def tsm(c, dow, n):
    """dow[d] = weekday of bar d (Mon=0). Rebalance at Monday close."""
    W = np.zeros(len(c)); cur = 0.0
    for d in range(len(c)):
        if d >= max(n, 21) and dow[d] == 0 and not np.isnan(c[d]) and not np.isnan(c[d - n]):
            r = c[d - 20:d + 1]
            if not np.isnan(r).any():
                sd = np.std(np.diff(r) / r[:-1], ddof=1)
                cur = (1.0 if c[d] / c[d - n] - 1 > 0 else -1.0) * size(2 * sd)
        elif np.isnan(c[d]): cur = 0.0
        W[d] = cur
    return W


def atr_sma(h, l, c, n=14):
    tr = np.full(len(c), np.nan)
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    return sma(tr, n)


def adx_rule(h, l, c):
    """ADX14 state machine on one bar series. Returns weights at each bar close."""
    ok = ~np.isnan(c)
    W = np.zeros(len(c))
    if ok.sum() < 40: return W
    i0 = int(np.argmax(ok))
    dip, dim, adx = adx_di(list(h[i0:]), list(l[i0:]), list(c[i0:]), 14)
    f = lambda x: np.array([np.nan if v is None else v for v in x], float)
    dip, dim, adx = [np.concatenate([np.full(i0, np.nan), f(x)]) for x in (dip, dim, adx)]
    atr = atr_sma(h, l, c)
    s = 0; w = 0.0
    for d in range(1, len(c)):
        if np.isnan(adx[d]) or np.isnan(adx[d - 1]) or np.isnan(atr[d]):
            s = 0; w = 0.0
        else:
            if s == 1 and (adx[d] < 20 or dim[d] > dip[d]): s = 0
            elif s == -1 and (adx[d] < 20 or dip[d] > dim[d]): s = 0
            if s == 0 and adx[d] > 25 and adx[d] > adx[d - 1]:
                if dip[d] > dim[d]: s = 1; w = size(2 * atr[d] / c[d])
                elif dim[d] > dip[d]: s = -1; w = size(2 * atr[d] / c[d])
        W[d] = s * w if s else 0.0
    return W


def adx_3d(o, h, l, c):
    """Rule 6: ADX14 on 3-day blocks (blocks of days d%3 in {0,1,2}); weight set at block close day, held until next block close."""
    n = len(c); nb = n // 3
    bh, bl, bc = np.full(nb, np.nan), np.full(nb, np.nan), np.full(nb, np.nan)
    for b in range(nb):
        sl = slice(3 * b, 3 * b + 3)
        if not (np.isnan(c[sl]).any() or np.isnan(h[sl]).any() or np.isnan(l[sl]).any()):
            bh[b], bl[b], bc[b] = h[sl].max(), l[sl].min(), c[3 * b + 2]
    wb = adx_rule(bh, bl, bc)
    W = np.zeros(n)
    for b in range(nb):
        W[3 * b + 2:3 * b + 5] = wb[b]   # set at block-close day, held through the next 2 days (until next block close)
    return W[:n]


def ma_rule(c):
    m20, m50 = sma(c, 20), sma(c, 50)
    W = np.zeros(len(c)); s = 0; w = 0.0
    for d in range(len(c)):
        if np.isnan(m50[d]) or np.isnan(m20[d]):
            s = 0; w = 0.0
        else:
            if s == 1 and c[d] < m20[d]: s = 0
            elif s == -1 and c[d] > m20[d]: s = 0
            if s == 0:
                if c[d] > m50[d] and m20[d] > m50[d] and c[d] > m20[d]: s = 1; w = size((c[d] - m20[d]) / c[d])
                elif c[d] < m50[d] and m20[d] < m50[d] and c[d] < m20[d]: s = -1; w = size((m20[d] - c[d]) / c[d])
        W[d] = s * w if s else 0.0
    return W


def gate(W, btc_c, btc_m200):
    """Longs only while BTC close > its 200d SMA, shorts only while below; undefined -> flat."""
    bull = btc_c > btc_m200; bear = btc_c < btc_m200
    ok = np.where(W > 0, bull, np.where(W < 0, bear, True))
    return np.where(ok, W, 0.0)
