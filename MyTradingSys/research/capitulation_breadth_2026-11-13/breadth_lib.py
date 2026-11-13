"""Core functions: Wilder RSI, breadth series, event detection, confirm, exits. Closed bars only; fwd_* helpers read forward ONLY after the entry bar is fixed."""
import numpy as np

def wilder_rsi(c, n=14):
    c = np.asarray(c, float); out = np.full(len(c), np.nan)
    if len(c) <= n: return out
    d = np.diff(c); g = np.where(d > 0, d, 0.0); l = np.where(d < 0, -d, 0.0)
    ag, al = g[:n].mean(), l[:n].mean()
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + g[i]) / n; al = (al * (n - 1) + l[i]) / n
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out

def breadth(rsi_mat, thr_rsi=25.0):
    """rsi_mat [coins x bars] NaN before listing. B = share with RSI<=thr among coins with defined RSI. NaN if <10 coins defined."""
    ok = ~np.isnan(rsi_mat); n = ok.sum(0)
    k = (np.where(ok, rsi_mat, 99) <= thr_rsi).sum(0)
    return np.where(n >= 10, k / np.maximum(n, 1), np.nan)

def find_events(B, thr, quiet=30):
    """EVENT = first bar with B>=thr after >= quiet consecutive bars with defined B < thr."""
    ev, run = [], 0
    for t in range(len(B)):
        if np.isnan(B[t]): run = 0; continue
        if B[t] >= thr:
            if run >= quiet: ev.append(t)
            run = 0
        else: run += 1
    return ev

def find_entry(B, btc_c, t, maxwait=3):
    """First j in t+1..t+maxwait with B[j] < B[j-1] (B falls back) AND btc close[j] > btc close[j-1]. None if no confirm."""
    for j in range(t + 1, min(t + maxwait, len(B) - 1) + 1):
        if B[j] < B[j - 1] and btc_c[j] > btc_c[j - 1]: return j
    return None

def fwd_exit(kind, j, win_lo, o, h, l, c, caps=None):
    """Exit for one price series (arrays o,h,l,c) entered at close of bar j. kind: ('hold',n) or ('stop2r', cap).
    Returns (exit_price, exit_bar). For stop2r the trigger series is BTC (passed in trig) -- see fwd_stop2r."""
    n = kind[1]; k = min(j + n, len(c) - 1)
    return c[k], k

def fwd_stop2r(j, win_lo, bo, bh, bl, bc, cap=42):
    """BTC trigger: stop = win_lo, target = entry + 2R (R = entry - stop), stop-first per bar, gap fills at min(stop, open)/max(tp, open) ... returns (bar, btc_exit_price)."""
    entry = bc[j]; R = entry - win_lo; tp = entry + 2 * R
    last = min(j + cap, len(bc) - 1)
    for k in range(j + 1, last + 1):
        if bl[k] <= win_lo: return k, min(win_lo, bo[k])
        if bh[k] >= tp: return k, max(tp, bo[k]) if bo[k] >= tp else tp
    return last, bc[last]
