"""Core logic for the NK breakout/fakeout study (see PRE_REG.md). Causal by construction; STUDY_BUG env injects look-ahead for tests."""
import os
import numpy as np

N_BOX, K_RET, MINATR, MINPCT = 20, 10, 0.6, 0.005
WMIN, WMAX = 1.5, 4.0
H_X1, H_X2, TGT_R = 24, 48, 2.0
DAY = 86400000
TAIL = K_RET + 2 + H_X2 + 3  # bars needed after a breakout bar


def bug():
    return os.environ.get("STUDY_BUG", "")


def wilder(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def atr(h, l, c, n=14):
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    return wilder(tr, n)


def resample(t, o, h, l, c, v, k):
    """group k consecutive 15m bars aligned to the UTC boundary of k*15m; keep complete groups."""
    per = k * 15 * 60000
    g = t // per
    idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    ends = np.r_[idx[1:], len(t)]
    st = [(a, b) for a, b in zip(idx, ends) if b - a == k and t[a] % per == 0]
    a = np.array([s[0] for s in st])
    b = np.array([s[1] for s in st])
    return (t[a], o[a], np.array([h[x:y].max() for x, y in zip(a, b)]), np.array([l[x:y].min() for x, y in zip(a, b)]),
            c[b - 1], np.array([v[x:y].sum() for x, y in zip(a, b)]))


def daily_phase_table(t, o, h, l, c, v):
    """(day_numbers, label) with label[d] in {1 UP,-1 DOWN,0 RANGE} using daily bars <= d."""
    td, od, hd, ld, cd, vd = resample(t, o, h, l, c, v, 96)
    n = len(td)
    up = np.r_[0.0, hd[1:] - hd[:-1]]
    dn = np.r_[0.0, ld[:-1] - ld[1:]]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(hd, ld, cd, 14)
    sp = wilder(pdm, 14)
    sm = wilder(mdm, 14)
    with np.errstate(all="ignore"):
        pdi = 100 * sp / a
        mdi = 100 * sm / a
        dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    dx0 = np.nan_to_num(dx, nan=0.0)
    adx = np.full(n, np.nan)
    if n > 40:
        adx[27] = np.mean(dx0[14:28])
        for i in range(28, n):
            adx[i] = (adx[i - 1] * 13 + dx0[i]) / 14
    ma = np.full(n, np.nan)
    cs = np.cumsum(np.r_[0, cd])
    ma[19:] = (cs[20:] - cs[:-20]) / 20
    slope = np.full(n, np.nan)
    slope[5:] = ma[5:] - ma[:-5]
    lab = np.zeros(n, dtype=np.int8)
    lab[(adx >= 20) & (pdi > mdi) & (slope > 0)] = 1
    lab[(adx >= 20) & (mdi > pdi) & (slope < 0)] = -1
    return td // DAY, lab


def phase_for_bars(t, days, lab):
    """phase of each bar = label of the previous available day (causal). Bug 1: label of the same day."""
    d = t // DAY
    if bug() == "1":
        j = np.searchsorted(days, d, side="right") - 1
    else:
        j = np.searchsorted(days, d, side="left") - 1
    out = np.zeros(len(t), dtype=np.int8)
    ok = j >= 0
    out[ok] = lab[j[ok]]
    return out


def features(t, o, h, l, c):
    n = len(c)
    a = atr(h, l, c, 14)
    ap = np.r_[np.nan, a[:-1]]  # ATR through bar i-1
    s = np.lib.stride_tricks.sliding_window_view
    Hb = np.full(n, np.nan)
    Lb = np.full(n, np.nan)
    if n > N_BOX + 1:
        Hb[N_BOX:] = s(h, N_BOX).max(axis=1)[:-1]
        Lb[N_BOX:] = s(l, N_BOX).min(axis=1)[:-1]
    blast = np.zeros(n, bool)
    with np.errstate(all="ignore"):
        width = (Hb - Lb) / ap
        if n > 140:
            w = s(c, 20)
            m = np.full(n, np.nan)
            sd = np.full(n, np.nan)
            m[19:] = w.mean(axis=1)
            sd[19:] = w.std(axis=1)
            bw = 4 * sd / m
            rank = np.full(n, np.nan)
            ww = s(bw, 100)[:-1]  # window ending at bar i-1, for i=100..n-1
            cur = ww[:, -1]
            rank[100:] = (ww <= cur[:, None]).mean(axis=1)
            rank[:125] = np.nan
            bwr = np.r_[np.nan, bw[1:] / bw[:-1]]
            blast = (rank <= 0.25) & (bwr >= 1.15)
    return dict(atr_prev=ap, H=Hb, L=Lb, width=width, blast=blast)


def signals(t, o, h, l, c, F, phase):
    """Signals of type A (retest) and B (fakeout fade). Uses only data <= entry bar (bug 2 peeks B+2)."""
    n = len(c)
    ok = (F["width"] >= WMIN) & (F["width"] <= WMAX)
    brk_up = (c > F["H"]) & ok
    brk_dn = (c < F["L"]) & ok
    out = []
    for i in np.flatnonzero(brk_up | brk_dn):
        if i + TAIL >= n or np.isnan(F["atr_prev"][i]):
            continue
        db = 1 if brk_up[i] else -1
        H_, L_ = F["H"][i], F["L"][i]
        ph = int(phase[i])
        at = F["atr_prev"][i]
        bl = bool(F["blast"][i])
        if db == 1:
            taken = h[i + 1] > h[i]
            inside = c[i + 1] <= H_
            if bug() == "2":
                taken = taken or h[i + 2] > h[i]
        else:
            taken = l[i + 1] < l[i]
            inside = c[i + 1] >= L_
            if bug() == "2":
                taken = taken or l[i + 2] < l[i]
        if taken:
            if ph == 0:
                continue
            for j in range(i + 2, i + 2 + K_RET):
                if (db == 1 and l[j] < H_) or (db == -1 and h[j] > L_):
                    px = min(H_, o[j]) if db == 1 else max(L_, o[j])
                    nat = (px - l[i]) if db == 1 else (h[i] - px)
                    out.append(dict(type="A", i=i, e=j, dir=db, px=px, nat=nat, atr=at, ph=ph,
                                    fit=int(ph == db), blast=bl, chk=True))
                    break
        elif inside:
            d = -db
            px = c[i + 1]
            nat = (h[i] - px) if d == -1 else (px - l[i])
            out.append(dict(type="B", i=i, e=i + 1, dir=d, px=px, nat=nat, atr=at, ph=ph,
                            fit=int(ph == 0 or ph == d), blast=bl, chk=False))
    return out


def stop_dist(nat, atr_, px):
    return np.maximum(np.maximum(nat, MINATR * atr_), MINPCT * px)


def sim(O, Hh, Ll, C, idx, px, d, dist, mode, chk):
    """Vectorised trade sim. Returns (gross R, exit_idx). Stops checked from idx (if chk) else idx+1."""
    n = len(idx)
    stop = px - d * dist
    tgt = px + d * TGT_R * dist
    done = np.zeros(n, bool)
    exitpx = np.zeros(n)
    exi = np.zeros(n, np.int64)
    H = H_X1 if mode == "X1" else H_X2
    cur_stop = stop.copy()
    for k in range(0, H + 1):
        b = idx + k
        if k == 0:
            hit = chk & np.where(d == 1, Ll[b] <= stop, Hh[b] >= stop)
            exitpx[hit] = stop[hit]
            exi[hit] = b[hit]
            done |= hit
            continue
        if mode == "X2" and k >= 2:
            prev = np.where(d == 1, Ll[b - 1], Hh[b - 1])
            cur_stop = np.where(d == 1, np.maximum(cur_stop, prev), np.minimum(cur_stop, prev))
        hit_s = (~done) & np.where(d == 1, Ll[b] <= cur_stop, Hh[b] >= cur_stop)
        fill = np.where(d == 1, np.minimum(cur_stop, O[b]), np.maximum(cur_stop, O[b]))
        exitpx[hit_s] = fill[hit_s]
        exi[hit_s] = b[hit_s]
        done |= hit_s
        if mode == "X1":
            hit_t = (~done) & np.where(d == 1, Hh[b] >= tgt, Ll[b] <= tgt)
            exitpx[hit_t] = tgt[hit_t]
            exi[hit_t] = b[hit_t]
            done |= hit_t
        if k == H:
            r = ~done
            exitpx[r] = C[b][r]
            exi[r] = b[r]
    return d * (exitpx - px) / dist, exi
