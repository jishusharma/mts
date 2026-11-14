"""NK2 (pivot S/R reclaim, incl. S2/S3/R2/R3) and NK3 (breakout retest A / fakeout fade B) on 1h bars, with phase + context attached per signal.
Frozen NK definitions come from branches JIS-NB/nk2-pivot-sr-reclaim-1114 and JIS-NB/nk3-breakout-fakeout-retest-1114 (see PRE_REG.md). Causal by construction.
Paths are built with pathlib (Path(root)/venue/slug), never string concatenation."""
import os
from pathlib import Path
import numpy as np
import ctxlib as cx
import mts_phase as mp

CACHE = Path(r"F:\MTS\data_cache")
SPOT = CACHE / "binance_spot"
CTXDIR = CACHE / "binance" / "nkp2-levels-phase-1114"
COINS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
SPLIT = 1704067200000  # 2024-01-01 UTC, by SIGNAL bar open time
H1, DAY = 3600000, 86400000
LEVELS = ["S3", "S2", "S1", "P", "R1", "R2", "R3"]
RULES = ["NK2-core", "NK2-deep", "NK3-A", "NK3-B"]
NK2_TRIG = {"NK2-core": {1: ["P", "S1"], -1: ["P", "R1"]}, "NK2-deep": {1: ["S2", "S3"], -1: ["R2", "R3"]}}
MINATR, MINPCT, NK2_BARS, NK3_BARS = 0.6, 0.005, 24, 24
N_BOX, K_RET, WMIN, WMAX, TGT_R = 20, 10, 1.5, 4.0, 2.0
BIG = 10 ** 9
RT_BP = {"taker": 12.0, "maker": 6.0}


def bug():
    return os.environ.get("STUDY_BUG", "")


def load_raw(coin):
    z = np.load(SPOT / f"{coin}USDT_15m.npz")
    ts = z["ts"] if "ts" in z.files else z["t"]
    raw = dict(t=ts.astype(np.int64), o=z["o"], h=z["h"], l=z["l"], c=z["c"], v=z["v"])
    p = CTXDIR / f"klines_1h_{coin}.npz"
    if p.exists():
        k = np.load(p)
        raw["kl"] = {x: k[x] for x in k.files}
    p = CTXDIR / f"funding_{coin}.npz"
    if p.exists():
        k = np.load(p)
        raw["fund"] = {x: k[x] for x in k.files}
    p = CTXDIR / f"oi_{coin}.npz"
    if p.exists():
        k = np.load(p)
        raw["oi"] = {x: k[x] for x in k.files}
    return raw


def atr14_simple(h, l, c):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    out = np.full(len(c), np.nan)
    cs = np.cumsum(np.r_[0, tr])
    out[13:] = (cs[14:] - cs[:-14]) / 14
    return out


def wilder_atr(h, l, c, n=14):
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def pivots(h, l, c):
    p = (h + l + c) / 3.0
    return dict(P=p, R1=2 * p - l, S1=2 * p - h, R2=p + (h - l), S2=p - (h - l), R3=h + 2 * (p - l), S3=l - 2 * (h - p))


def phase_for_bars(t1, pdays, plab):
    """phase of the UTC day the bar OPENS in; table label for day d uses closes through d-1 only. STUDY_BUG=1: the NEXT day's label (uses this day's close)."""
    d = t1 // DAY + (1 if bug() == "1" else 0)
    j = np.searchsorted(pdays, d)
    jj = np.minimum(j, len(pdays) - 1)
    ok = (j < len(pdays)) & (pdays[jj] == d)
    return np.where(ok, plab[jj], 0).astype(np.int8)


def prep(coin, pdays, plab, raw=None):
    raw = load_raw(coin) if raw is None else raw
    C = cx.compute_context(raw)
    t1, o, h, l, c = C["t1"], C["o1"], C["h1"], C["l1"], C["c1"]
    n = len(t1)
    # daily pivots from the PREVIOUS complete UTC day (BUG=1: the bar's own day = look-ahead)
    dn = C["td"] // DAY
    day = t1 // DAY
    src = day if bug() == "1" else day - 1
    pos = np.searchsorted(dn, src)
    posc = np.minimum(pos, len(dn) - 1)
    has = (pos < len(dn)) & (dn[posc] == src)
    lv = pivots(C["hd"][posc], C["ld"][posc], C["cd"][posc])
    gaps = np.r_[0, np.cumsum(np.diff(t1) != H1)]
    k = np.arange(n)
    lo, hi = np.maximum(k - 30, 0), np.minimum(k + 80, n - 1)
    nogap = (gaps[hi] - gaps[lo]) == 0
    D = dict(coin=coin, t=t1, o=o, h=h, l=l, c=c, lv=lv, atr=atr14_simple(h, l, c), atrw=wilder_atr(h, l, c), valid=has & nogap,
             ph=phase_for_bars(t1, pdays, plab), ctx=C["ctx"], n=n)
    return D


def exit_sim(D, k0, d, e, stop, tgt, basis, tgt_first):
    """walk bars k0..k0+24 (clipped). close basis: stop = bar CLOSE beyond stop, exit at that close. intraday: touch, fill at worse of stop and open.
    target: intrabar touch fills at the level. stop wins same-bar ties. returns (exit px, exit index)."""
    n = D["n"]
    kend = min(n - 1, k0 + NK2_BARS)
    ho, lo, co, oo = D["h"][k0:kend + 1], D["l"][k0:kend + 1], D["c"][k0:kend + 1], D["o"][k0:kend + 1]
    if d > 0:
        hs = co <= stop if basis == "close" else lo <= stop
        ht = ho >= tgt
    else:
        hs = co >= stop if basis == "close" else ho >= stop
        ht = lo <= tgt
    if not tgt_first:
        ht = ht.copy()
        ht[0] = False
    fs = int(np.argmax(hs)) if hs.any() else BIG
    ft = int(np.argmax(ht)) if ht.any() else BIG
    if fs == BIG and ft == BIG:
        k = len(co) - 1
        return co[k], k0 + k
    if fs <= ft:
        px = co[fs] if basis == "close" else (min(stop, oo[fs]) if d > 0 else max(stop, oo[fs]))
        return px, k0 + fs
    return tgt, k0 + ft


def nk2_trade(D, i, d, basis, maker):
    """signal at 1h bar i close, entry next open (taker) or limit at the trigger close that must be traded THROUGH by bar i+1 (maker)."""
    n = D["n"]
    if i + 2 >= n or np.isnan(D["atr"][i]):
        return None
    nb = i + 1
    if maker:
        lim = D["c"][i]
        if d > 0:
            if not D["l"][nb] < lim:
                return None
            e = min(lim, D["o"][nb])
        else:
            if not D["h"][nb] > lim:
                return None
            e = max(lim, D["o"][nb])
    else:
        e = D["o"][nb]
    if d > 0:
        swing = D["l"][max(0, i - 5):i + 1].min()
        dist = max(e - swing, MINATR * D["atr"][i], MINPCT * e)
        stop = e - dist
        cands = [D["lv"][k][i] for k in LEVELS if D["lv"][k][i] > e]
        if not cands or min(cands) - e < dist:
            return None
        tgt = min(cands)
    else:
        swing = D["h"][max(0, i - 5):i + 1].max()
        dist = max(swing - e, MINATR * D["atr"][i], MINPCT * e)
        stop = e + dist
        cands = [D["lv"][k][i] for k in LEVELS if D["lv"][k][i] < e]
        if not cands or e - max(cands) < dist:
            return None
        tgt = max(cands)
    xpx, xi = exit_sim(D, nb, d, e, stop, tgt, basis, tgt_first=not maker)
    return dict(g=d * (xpx - e) / dist, df=dist / e, e=e, x=xpx, xi=xi)


def nk2_signals(D, d, levels):
    c = D["c"]
    cond = np.zeros(D["n"], bool)
    lvl = np.full(D["n"], -1, dtype=np.int8)
    for X in levels:
        lv = D["lv"][X]
        m = np.zeros(D["n"], bool)
        if d > 0:
            m[1:] = (c[:-1] < lv[1:]) & (c[1:] >= lv[1:])
        else:
            m[1:] = (c[:-1] > lv[1:]) & (c[1:] <= lv[1:])
        new = m & ~cond
        lvl[new] = LEVELS.index(X)
        cond |= m
    return np.flatnonzero(cond & D["valid"]), lvl


def nk3_events(D):
    """all breakout events of both directions, no phase gate. signal bar s = B+1 (the bar whose close arms the order / fills the fade)."""
    n = D["n"]
    o, h, l, c, ap = D["o"], D["h"], D["l"], D["c"], np.r_[np.nan, D["atrw"][:-1]]
    sw = np.lib.stride_tricks.sliding_window_view
    Hb = np.full(n, np.nan)
    Lb = np.full(n, np.nan)
    Hb[N_BOX:] = sw(h, N_BOX).max(axis=1)[:-1]
    Lb[N_BOX:] = sw(l, N_BOX).min(axis=1)[:-1]
    with np.errstate(all="ignore"):
        width = (Hb - Lb) / ap
        ok = (width >= WMIN) & (width <= WMAX)
        up, dn = (c > Hb) & ok, (c < Lb) & ok
    tail = K_RET + 2 + NK3_BARS + 3
    out = []
    for B in np.flatnonzero(up | dn):
        if B + tail >= n or not D["valid"][B] or np.isnan(ap[B]):
            continue
        db = 1 if up[B] else -1
        H_, L_ = Hb[B], Lb[B]
        s = B + 1
        if db == 1:
            taken = h[s] > h[B]
            inside = c[s] <= H_
        else:
            taken = l[s] < l[B]
            inside = c[s] >= L_
        if taken:
            for j in range(B + 2, B + 2 + K_RET):
                if (db == 1 and l[j] < H_) or (db == -1 and h[j] > L_):
                    px = min(H_, o[j]) if db == 1 else max(L_, o[j])
                    nat = (px - l[B]) if db == 1 else (h[B] - px)
                    out.append(dict(type="A", s=s, e=j, d=db, px=px, nat=nat, atr=ap[B], B=B))
                    break
        elif inside:
            d = -db
            px = c[s]
            nat = (h[B] - px) if d == -1 else (px - l[B])
            out.append(dict(type="B", s=s, e=s, d=d, px=px, nat=nat, atr=ap[B], B=B))
    return out


def nk3_trade(D, ev, basis, maker):
    d, px = ev["d"], ev["px"]
    k0 = ev["e"]
    if maker and ev["type"] == "B":  # fade is a market entry at the B+1 close; maker row = limit at that price, traded through by the next bar
        nb = k0 + 1
        if d > 0:
            if not D["l"][nb] < px:
                return None
            px = min(px, D["o"][nb])
        else:
            if not D["h"][nb] > px:
                return None
            px = max(px, D["o"][nb])
        B = ev["B"]
        nat = (px - D["l"][B]) if d == 1 else (D["h"][B] - px)
        dist = max(nat, MINATR * ev["atr"], MINPCT * px)
        stop, tgt = px - d * dist, px + d * TGT_R * dist
        xpx, xi = exit_sim(D, nb, d, px, stop, tgt, basis, tgt_first=False)
    else:
        dist = max(ev["nat"], MINATR * ev["atr"], MINPCT * px)
        stop, tgt = px - d * dist, px + d * TGT_R * dist
        if ev["type"] == "A":  # filled intrabar on bar e: stop checked on it, target only from the next bar
            xpx, xi = exit_sim(D, k0, d, px, stop, tgt, basis, tgt_first=False)
        else:
            xpx, xi = exit_sim(D, k0 + 1, d, px, stop, tgt, basis, tgt_first=True)
    return dict(g=d * (xpx - px) / dist, df=dist / px, e=px, x=xpx, xi=xi)


def build_trades(coins=COINS, progress=True):
    """all trades for all rules. key (rule, basis, mode) -> dict of arrays. Sequential: one position per coin per rule per direction.
    columns: coin, t (signal bar open ms), ph, d, lvl, ctx (8 x n), g, df, e, x, xi (exit bar index, within coin)."""
    pdays, plab = mp.phase_table_for_study()
    cfgs = [(b, "taker") for b in ("close", "intraday")] + [("close", "maker"), ("intraday", "maker")]
    store = {}
    for r in RULES:
        for b, m in cfgs:
            store[(r, b, m)] = []
    for ci, coin in enumerate(coins):
        D = prep(coin, pdays, plab)
        if progress:
            print("prep", coin, D["n"], flush=True)
        ev_all = nk3_events(D)
        sigs = {(r, d): nk2_signals(D, d, NK2_TRIG[r][d]) for r in NK2_TRIG for d in (1, -1)}
        for r in RULES:
            for b, m in cfgs:
                rows = []
                if r.startswith("NK2"):
                    for d in (1, -1):
                        sig, lvl = sigs[(r, d)]
                        busy = -1
                        for i in sig:
                            if i <= busy:
                                continue
                            tr = nk2_trade(D, int(i), d, b, m == "maker")
                            if tr is None:
                                continue
                            busy = tr["xi"]
                            rows.append((ci, D["t"][i], D["ph"][i], d, lvl[i], D["ctx"][:, i].copy(), tr))
                else:
                    evs = [e for e in ev_all if e["type"] == r[-1]]
                    for d in (1, -1):
                        busy = -1
                        for ev in sorted((e for e in evs if e["d"] == d), key=lambda e: e["s"]):
                            if ev["e"] <= busy:
                                continue
                            tr = nk3_trade(D, ev, b, m == "maker")
                            if tr is None:
                                continue
                            busy = tr["xi"]
                            rows.append((ci, D["t"][ev["s"]], D["ph"][ev["s"]], d, -1, D["ctx"][:, ev["s"]].copy(), tr))
                store[(r, b, m)].append(rows)
    out = {}
    for k, parts in store.items():
        rows = [x for p in parts for x in p]
        out[k] = dict(
            coin=np.array([x[0] for x in rows], dtype=np.int16), t=np.array([x[1] for x in rows], dtype=np.int64),
            ph=np.array([x[2] for x in rows], dtype=np.int8), d=np.array([x[3] for x in rows], dtype=np.int8),
            lvl=np.array([x[4] for x in rows], dtype=np.int8), ctx=np.array([x[5] for x in rows], dtype=np.int8).reshape(len(rows), 8),
            g=np.array([x[6]["g"] for x in rows]), df=np.array([x[6]["df"] for x in rows]), e=np.array([x[6]["e"] for x in rows]),
            x=np.array([x[6]["x"] for x in rows]))
    return out


def fee_r(T, bp):
    """round trip fee in R: taker/maker leg fee = bp/2 on entry notional and on exit notional."""
    return (bp / 2e4) * (T["e"] + T["x"]) / (T["df"] * T["e"])
