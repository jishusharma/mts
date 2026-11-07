"""
MyTradingSys/backtest/layers/adx/adx.py - Wilder ADX/DI (FORMULAS.md section 30). Context layer, no orders.
adx_di(high, low, close, n=14) -> (di_plus, di_minus, adx), lists the length of the input, None where undefined.
"""


def adx_di(high, low, close, n=14):
    m = len(close)
    if not (len(high) == len(low) == m):
        raise ValueError("high, low, close must have the same length")
    dip = [None] * m
    dim = [None] * m
    adx = [None] * m
    if m < n + 1:
        return dip, dim, adx
    tr, pdm, mdm = [], [], []
    for i in range(1, m):
        tr.append(max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])))
        up = high[i] - high[i - 1]
        dn = low[i - 1] - low[i]
        pdm.append(up if (up > dn and up > 0) else 0.0)
        mdm.append(dn if (dn > up and dn > 0) else 0.0)
    s_tr, s_p, s_m = sum(tr[:n]), sum(pdm[:n]), sum(mdm[:n])
    dx = []
    for k in range(n - 1, m - 1):
        if k >= n:
            s_tr = s_tr - s_tr / n + tr[k]
            s_p = s_p - s_p / n + pdm[k]
            s_m = s_m - s_m / n + mdm[k]
        i = k + 1
        if s_tr <= 0:
            dip[i], dim[i] = 0.0, 0.0
        else:
            dip[i], dim[i] = 100.0 * s_p / s_tr, 100.0 * s_m / s_tr
        tot = dip[i] + dim[i]
        dx.append(100.0 * abs(dip[i] - dim[i]) / tot if tot > 0 else 0.0)
        if len(dx) == n:
            adx[i] = sum(dx) / n
        elif len(dx) > n:
            adx[i] = (adx[i - 1] * (n - 1) + dx[-1]) / n
    return dip, dim, adx


def crosses(dip, dim):
    """(index, 'red'|'green'): red = DI- crosses above DI+, green = DI+ above DI-; both defined on bars i-1 and i,
    a cross needs a strict sign flip of (DI+ - DI-) from the last non-zero sign."""
    out = []
    prev = 0
    for i in range(len(dip)):
        if dip[i] is None:
            continue
        d = dip[i] - dim[i]
        s = (d > 0) - (d < 0)
        if s != 0:
            if prev != 0 and s != prev:
                out.append((i, "green" if s > 0 else "red"))
            prev = s
    return out