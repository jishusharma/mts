"""Throw-away REFERENCE for the WaveTrend parity contract (not the production module).

Pure python loops, no numpy, written from source_snapshot/*.pine lines 14-21.
Used only to (a) show the contract's conventions are decidable, (b) measure how
much the EMA seed choice matters, (c) give flat/tie behaviours. Golden numbers
for the module card must come from a spreadsheet, not from this file.
"""
import math

NAN = float("nan")
isnan = math.isnan


def ema(xs, n, seed="first"):
    """seed 'first': ema[0]=x[0]. seed 'sma': NaN until n values, then SMA(n).
    NaN input -> NaN output and the state is lost (re-seeds when n valid values exist)."""
    a = 2.0 / (n + 1)
    out, prev, buf = [], None, []
    for x in xs:
        if isnan(x):
            out.append(NAN); prev = None; buf = []; continue
        if prev is None:
            if seed == "first":
                prev = x
            else:
                buf.append(x)
                if len(buf) < n:
                    out.append(NAN); continue
                prev = sum(buf[-n:]) / n
        else:
            prev = a * x + (1 - a) * prev
        out.append(prev)
    return out


def sma(xs, n):
    out = []
    for i in range(len(xs)):
        w = xs[max(0, i - n + 1):i + 1]
        out.append(sum(w) / n if len(w) == n and not any(isnan(v) for v in w) else NAN)
    return out


def wavetrend(h, l, c, n1=10, n2=21, seed="first"):
    ap = [(a + b + d) / 3.0 for a, b, d in zip(h, l, c)]
    esa = ema(ap, n1, seed)
    dev = ema([abs(a - e) if not isnan(e) else NAN for a, e in zip(ap, esa)], n1, seed)
    ci = [(a - e) / (0.015 * d) if (not isnan(d) and d != 0.0) else NAN
          for a, e, d in zip(ap, esa, dev)]          # d==0 -> NaN (Pine: division by zero = na)
    wt1 = ema(ci, n2, seed)
    return wt1, sma(wt1, 4)


def cross_events(wt1, wt2, mode="le"):
    """+1 up-cross, -1 down-cross, 0 none, evaluated at bar t from bars t and t-1 only.
    mode 'le' : up = w1>w2 and prev w1<=w2 ; down = w1<w2 and prev w1>=w2  (tie on prev bar counts as cross)
    mode 'strict': prev must be strictly on the other side (a touch-and-leave is no cross)"""
    ev = [0]
    for i in range(1, len(wt1)):
        a, b, pa, pb = wt1[i], wt2[i], wt1[i - 1], wt2[i - 1]
        if any(isnan(v) for v in (a, b, pa, pb)):
            ev.append(0); continue
        if mode == "le":
            up, dn = a > b and pa <= pb, a < b and pa >= pb
        else:
            up, dn = a > b and pa < pb, a < b and pa > pb
        ev.append(1 if up else -1 if dn else 0)
    return ev
