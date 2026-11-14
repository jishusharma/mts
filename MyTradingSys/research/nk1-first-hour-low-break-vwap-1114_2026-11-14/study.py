"""NK first-hour low-break + close-back + near-VWAP. Implements PRE_REG.md exactly. Flipped coordinates: price' = side*price, so every
signal/exit is written once as a LONG. STUDY_BUG=1 -> look-ahead variant (taker entry at the next bar's best price) used only by test_study.py."""
import os
import datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

MS5 = 300000
DAY = 86400000
SPLIT_DAY = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000) // DAY
NY = ZoneInfo("America/New_York")
SESS = {0: ("UTC", 144), 1: ("NY", 78)}
NEAR = 0.001
BIGK = 2.5
MINR = 0.005
ATRK = 0.6
FEE_T, FEE_M = 0.0012, 0.0006
BIG = 10 ** 9


def daily(a):
    d = (a[:, 0] // DAY).astype(np.int64)
    ud, st = np.unique(d, return_index=True)
    en = np.r_[st[1:], len(a)]
    ok = (en - st) >= 250
    ud, st, en = ud[ok], st[ok], en[ok]
    O = a[st, 1]
    C = a[en - 1, 4]
    H = np.array([a[s:e, 2].max() for s, e in zip(st, en)])
    L = np.array([a[s:e, 3].min() for s, e in zip(st, en)])
    return ud, O, H, L, C


def phases(ud, H, L, C):
    """dict day -> phase (+1 UP, -1 DOWN, 0 RANGE) for the day AFTER each complete day, from data through that day's close."""
    n = len(C)
    out = {}
    if n < 50:
        return out
    pc = np.r_[C[0], C[:-1]]
    tr = np.maximum(H - L, np.maximum(abs(H - pc), abs(L - pc)))
    up = np.r_[0, H[1:] - H[:-1]]
    dn = np.r_[0, L[:-1] - L[1:]]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    p = 14
    st = np.zeros(n); sp = np.zeros(n); sm = np.zeros(n)
    st[p] = tr[1:p + 1].sum(); sp[p] = pdm[1:p + 1].sum(); sm[p] = mdm[1:p + 1].sum()
    for i in range(p + 1, n):
        st[i] = st[i - 1] - st[i - 1] / p + tr[i]
        sp[i] = sp[i - 1] - sp[i - 1] / p + pdm[i]
        sm[i] = sm[i - 1] - sm[i - 1] / p + mdm[i]
    with np.errstate(all="ignore"):
        pdi = 100 * sp / st
        mdi = 100 * sm / st
        dx = 100 * abs(pdi - mdi) / (pdi + mdi)
    adx = np.full(n, np.nan)
    s0 = 2 * p
    adx[s0] = np.nanmean(dx[p + 1:s0 + 1])
    for i in range(s0 + 1, n):
        adx[i] = (adx[i - 1] * (p - 1) + dx[i]) / p
    cs = np.cumsum(np.r_[0, C])
    ma = np.full(n, np.nan)
    ma[19:] = (cs[20:] - cs[:n - 19]) / 20
    for i in range(s0 + 6, n):
        if ud[i] - ud[i - 6] > 8 or np.isnan(adx[i]):
            continue
        slope = ma[i] / ma[i - 5] - 1
        if adx[i] >= 20 and pdi[i] > mdi[i] and slope > 0:
            ph = 1
        elif adx[i] >= 20 and mdi[i] > pdi[i] and slope < 0:
            ph = -1
        else:
            ph = 0
        out[int(ud[i]) + 1] = ph
    return out


def open_ms(day, kind):
    if kind == 0:
        return day * DAY
    d = dt.datetime.fromtimestamp(day * DAY / 1000, dt.timezone.utc)
    o = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY)
    return int(o.timestamp() * 1000)


def sim(e, entryF, Rd, et, lowF, highF, openF, closeF, vwF, sd, n, tgt2):
    """Exit price (flipped) for a long entered at the open of bar e. Stop first on ties."""
    stop = entryF - Rd
    sh = np.flatnonzero(lowF[e:] <= stop)
    si = sh[0] if sh.size else BIG
    ti = BIG
    tg = None
    t2 = None
    if et == 0:
        tg = vwF[e - 1:n - 1] + 1.5 * sd[e - 1:n - 1]
        th = np.flatnonzero(highF[e:] >= tg)
        if th.size:
            ti = th[0]
    elif et == 1:
        t2 = max(tgt2, entryF + Rd)
        th = np.flatnonzero(highF[e:] >= t2)
        if th.size:
            ti = th[0]
    if si <= ti and si < BIG:
        return min(stop, openF[e + si])
    if ti < BIG:
        lvl = tg[ti] if et == 0 else t2
        return max(lvl, openF[e + ti])
    return closeF[n - 1]


def run(coins, bug=None):
    """coins: sym -> array(t,o,h,l,c,v). Returns list of trade dicts (one per coin-session-side signal)."""
    if bug is None:
        bug = os.environ.get("STUDY_BUG") == "1"
    trades = []
    for ci, (sym, a) in enumerate(coins.items()):
        t = a[:, 0]
        ud, dO, dH, dL, dC = daily(a)
        ph = phases(ud, dH, dL, dC)
        pdh = {int(d) + 1: h for d, h in zip(ud, dH)}
        pdl = {int(d) + 1: lo for d, lo in zip(ud, dL)}
        H, L, C, O, V = a[:, 2], a[:, 3], a[:, 4], a[:, 1], a[:, 5]
        rg = H - L
        crg = np.r_[0, np.cumsum(rg)]
        pcl = np.r_[C[0], C[:-1]]
        tr = np.maximum(rg, np.maximum(abs(H - pcl), abs(L - pcl)))
        ctr = np.r_[0, np.cumsum(tr)]
        for day, phase in ph.items():
            if day not in pdh:
                continue
            for kind in (0, 1):
                nb = SESS[kind][1]
                om = open_ms(day, kind)
                i0 = int(np.searchsorted(t, om))
                if i0 < 21 or i0 + nb > len(t) or t[i0] != om or t[i0 + nb - 1] != om + (nb - 1) * MS5:
                    continue
                sl = slice(i0, i0 + nb)
                sO, sH, sL, sC, sV = O[sl], H[sl], L[sl], C[sl], V[sl]
                cv = np.cumsum(sV)
                if cv[0] <= 0:
                    continue
                typ = (sH + sL + sC) / 3
                vw = np.cumsum(typ * sV) / cv
                sd = np.sqrt(np.maximum(np.cumsum(typ * typ * sV) / cv - vw * vw, 0))
                mr20 = (crg[i0] - crg[i0 - 20]) / 20
                for side in (1, -1):
                    matched = (phase == 0) or (phase == side)
                    lowF = sL if side > 0 else -sH
                    highF = sH if side > 0 else -sL
                    openF, closeF, vwF = side * sO, side * sC, side * vw
                    L0 = lowF[:3].min()
                    bk = next((k for k in range(3, 12) if lowF[k] < L0), None)
                    if bk is None:
                        continue
                    bc = next((k for k in range(bk, 12) if closeF[k] > L0), None)
                    if bc is None:
                        continue
                    if sH[bc] - sL[bc] > BIGK * mr20:
                        continue
                    j = next((k for k in range(bc, 12) if closeF[k] >= vwF[k] - NEAR * abs(vwF[k]) and closeF[k] > L0), None)
                    if j is None:
                        continue
                    e = j + 1
                    atr = (ctr[i0 + j + 1] - ctr[i0 + j + 1 - 14]) / 14
                    struct = lowF[:j + 1].min()
                    tgt2 = side * (pdh[day] if side > 0 else pdl[day])
                    rec = dict(coin=ci, sym=sym, day=day, kind=kind, side=side, phase=phase, matched=matched,
                               split=0 if day < SPLIT_DAY else 1)

                    def mk(entryF):
                        Rd = max(entryF - struct, MINR * abs(entryF), ATRK * atr)
                        rets = [(sim(e, entryF, Rd, et, lowF, highF, openF, closeF, vwF, sd, nb, tgt2) - entryF) / abs(entryF) for et in range(3)]
                        return Rd / abs(entryF), rets
                    entT = lowF[e] if bug else openF[e]
                    rec["R"], rec["ret"] = mk(entT)
                    lim = closeF[j]
                    if lowF[e] <= lim:
                        rec["Rm"], rec["retm"] = mk(min(openF[e], lim))
                    else:
                        rec["Rm"], rec["retm"] = None, None
                    pl = np.zeros((10, 3))
                    for q, e2 in enumerate(range(3, 13)):
                        en2 = openF[e2]
                        Rd2 = rec["R"] * abs(en2)
                        for et in range(3):
                            pl[q, et] = (sim(e2, en2, Rd2, et, lowF, highF, openF, closeF, vwF, sd, nb, tgt2) - en2) / abs(en2)
                    rec["pl"] = pl
                    trades.append(rec)
    return trades
