"""OPR-BB-MTF-CENTER G5 DEV screen + Krown range tests M1-M4 (descriptive). Rules: PRE_REG.md (frozen before the outcome run).
DEV only (bars < 2024-07-01). Screen, ran before G3 marks by operator decision 2026-10-16.

Usage: python study.py --count   (event and arm sizes only, NO return, U/D/R or other outcome column is computed)
       python study.py --full    (outcome run, one run, every computed cell is printed / written)
"""
import csv
import datetime as dt
import hashlib
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import common as K  # noqa: E402

NY = ZoneInfo("America/New_York")
HS = (60, 120, 240)               # minutes after the entry open; primary h = 120 (OURS, middle of the draft's 1/2/4 h grid)
PRIMARY_H = 120
COOLDOWN = 120                    # minutes between ledger events per arm (OURS: = the primary horizon, no overlapping positions)
N_PRIMARY = 6                     # closes below the mid before the touch (OURS, draft grid 3/6/12 middle value)
OUT_H = (1, 2, 4)                 # U/D/R horizons in hours (draft)
M_NS, M_XS, M_YS, M_KS = (24, 48, 96), (0.0025, 0.005), (0.0025, 0.005, 0.01), (1, 2, 3)
M_N, M_X, M_HH = 48, 0.005, 24    # primary range window / zone tolerance / look-ahead bars for the M tests (OURS)


# ---------------------------------------------------------------- rules (pure functions on bar arrays)
def touch_events(C, H, L, mid, hw, N=N_PRIMARY, rule="wick", x=0.0, side=-1, slope_lag=6):
    """First touch of the BB mid after N consecutive closes on the trend side and a mid sloping with the trend.
    side=-1: lower-band trend (closes below the mid, mid lower than slope_lag bars ago, touch by the HIGH). side=+1: mirror.
    rule: 'wick' (high reaches the mid), 'near' (within x half-widths), 'close' (the bar closes across the mid).
    pre[k] = precondition holds before bar k; first[k] = pre and no touch since the precondition was met; event = first and touch."""
    n = len(C)
    cs = (C < mid) if side == -1 else (C > mid)
    if rule == "wick":
        tc = (H >= mid) if side == -1 else (L <= mid)
    elif rule == "near":
        tc = (H >= mid - x * hw) if side == -1 else (L <= mid + x * hw)
    else:
        tc = (C > mid) if side == -1 else (C < mid)
    pre, first = np.zeros(n, bool), np.zeros(n, bool)
    run, touched = 0, False
    for k in range(n):
        if k > slope_lag:
            m1, m0 = mid[k - 1], mid[k - 1 - slope_lag]
            slope = (m1 < m0) if side == -1 else (m1 > m0)
            if run >= N and slope:
                pre[k] = True
                first[k] = not touched
        if cs[k]:
            run += 1
            if run > N and tc[k]:
                touched = True
        else:
            run, touched = 0, False
    return dict(pre=pre, first=first, event=first & tc, tc=tc, cs=cs)


def classify_udr(Hw, Lw, up, lo):
    """Per row: first 1m minute where high >= up (U) or low <= lo (D); 'B' both in the same minute; 'R' neither; 'X' missing data."""
    big = 10 ** 9
    hu, hd = Hw >= up[:, None], Lw <= lo[:, None]
    iu = np.where(hu.any(1), hu.argmax(1), big)
    idn = np.where(hd.any(1), hd.argmax(1), big)
    out = np.full(len(up), "R", dtype="<U1")
    out[iu < idn] = "U"
    out[idn < iu] = "D"
    out[(iu == idn) & (iu < big)] = "B"
    out[np.isnan(Hw).any(1) | np.isnan(Lw).any(1)] = "X"
    return out


def clusters(mask):
    mask = np.asarray(mask, bool)
    return int(mask[0]) + int((mask[1:] & ~mask[:-1]).sum()) if len(mask) else 0


def detect_ranges(H, L, n, x):
    """Greedy non-overlapping n-bar windows whose high zone (within x of the high) and low zone (within x of the low) each have >= 2 separate reactions."""
    out, j, N = [], n - 1, len(H)
    while j < N:
        h, l = H[j - n + 1:j + 1], L[j - n + 1:j + 1]
        if np.isnan(h).any() or np.isnan(l).any():
            j += 1
            continue
        hi, lo = h.max(), l.min()
        if clusters(h >= hi * (1 - x)) >= 2 and clusters(l <= lo * (1 + x)) >= 2:
            out.append((j - n + 1, j, float(hi), float(lo)))
            j += n
        else:
            j += 1
    return out


def win(arr, t0, w):
    idx = np.asarray(t0, np.int64)[:, None] + np.arange(w)[None, :]
    return np.where(idx < len(arr), arr[np.minimum(idx, len(arr) - 1)], np.nan)


def open_idx(d):
    u = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(dt.timezone.utc)
    return int((int(u.timestamp() * 1000) - K.TS0) // K.MS)


# ---------------------------------------------------------------- state
def prep(A):
    P = {}
    for name, m in (("30m", 30), ("1h", 60), ("4h", 240)):
        a = K.agg(A, m)
        lo, mid, up = K.bb(a["C"])
        P[name] = dict(a=a, lo=lo, mid=mid, up=up, hw=(up - lo) / 2, atr=K.atr_sma(a["H"], a["L"], a["C"], 14), m=m,
                       rsi=K.rsi_wilder(a["C"]), dl=2.0 * a["TBV"] - a["V"])
    return P


def cond30(P, ks, m, y):
    """The last m closed 30m bars at the touch-bar close all closed within +/- y half-widths of their own 30m mid."""
    p = P["30m"]
    ok = np.ones(len(ks), bool)
    for i in range(m):
        j = 2 * ks + 1 - i
        ok &= np.abs(p["a"]["C"][j] - p["mid"][j]) <= y * p["hw"][j]
    return ok


def eases(P, ks):
    p = P["30m"]
    j = 2 * ks + 1
    d4 = np.array([np.sum(p["dl"][x - 3:x + 1]) for x in j])
    return dict(delta4=d4 >= 0, rsi=p["rsi"][j] > p["rsi"][np.maximum(j - 4, 0)])


def sets(P):
    p = P["1h"]
    a = p["a"]
    ev = {}
    for N in (3, 6, 12):
        ev[("wick", N)] = touch_events(a["C"], a["H"], a["L"], p["mid"], p["hw"], N, "wick")
    for rule, x in (("near", 0.10), ("near", 0.25), ("close", 0.0)):
        ev[(f"{rule}{x}", 6)] = touch_events(a["C"], a["H"], a["L"], p["mid"], p["hw"], 6, rule, x)
    ev["mirror"] = touch_events(a["C"], a["H"], a["L"], p["mid"], p["hw"], 6, "wick", side=1)
    q = P["30m"]
    ev["30m"] = touch_events(q["a"]["C"], q["a"]["H"], q["a"]["L"], q["mid"], q["hw"], 6, "wick")
    main = ev[("wick", 6)]
    ks = np.nonzero(main["event"])[0]
    tdec = (ks + 1) * 60 - 1
    up_close = a["C"][ks] > p["mid"][ks]
    S = dict(ev=ev, ks=ks, up=ks[up_close], dn=ks[~up_close])
    for nm, side, close_cond in (("up", 1, a["C"] > p["mid"]), ("dn", -1, a["C"] < p["mid"])):
        k_arm = S[nm]
        t = (k_arm + 1) * 60 - 1
        S[nm + "_keep"] = k_arm[K.cooldown_mask(t, np.zeros(len(t), int), COOLDOWN)]
        ctrl = np.nonzero(main["tc"] & ~main["pre"] & close_cond)[0]
        tc_ = (ctrl + 1) * 60 - 1
        S[nm + "_ctrl"] = ctrl[K.cooldown_mask(tc_, np.zeros(len(tc_), int), COOLDOWN)]
    return S


def count_text(A, P, S):
    a = P["1h"]["a"]
    ev = S["ev"]
    L = ["## Count section (no return, U/D/R or other outcome column was computed)", "",
         f"1m bars missing on the DEV tape: {int(np.isnan(A['O']).sum())} of {len(A['O'])}. 1h bars {len(a['O'])} ({int(np.isnan(a['O']).sum())} incomplete), 30m bars {len(P['30m']['a']['O'])}, 4h bars {len(P['4h']['a']['O'])}.",
         f"First-touch events, 1h, N=6, wick rule (primary): **n = {len(S['ks'])}** (closing above the mid {len(S['up'])}, below {len(S['dn'])}). Precondition met before the bar (any touch state): {int(ev[('wick', 6)]['pre'].sum())} bars.",
         "Other event sets: " + "; ".join(f"{k if isinstance(k, str) else '%s N=%d' % k}: {int(v['event'].sum())}" for k, v in ev.items() if k != ("wick", 6)) + ".",
         f"Verdict arms after the {COOLDOWN}-minute cooldown: AU (touch bar closes above its mid, LONG) n = {len(S['up_keep'])}, control (touch, no precondition, closes above) n = {len(S['up_ctrl'])}; "
         f"AD (closes below, SHORT) n = {len(S['dn_keep'])}, control n = {len(S['dn_ctrl'])}.",
         f"Krown range detector (1h): " + ", ".join(f"n={n},x={x}: {len(detect_ranges(a['H'], a['L'], n, x))}" for n in M_NS for x in M_XS)
         + "; (4h): " + ", ".join(f"n={n},x={x}: {len(detect_ranges(P['4h']['a']['H'], P['4h']['a']['L'], n, x))}" for n in M_NS for x in M_XS) + ".",
         "OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed."]
    return "\n".join(L)


# ---------------------------------------------------------------- tables
def udr_rows(A, P, name, ks, tf, side, hours, fixed_tf=None):
    """Counter-trend band first / trend-continuation band first / neither, bands fixed at the event bar (draft outcome U/D/R)."""
    p = P[tf]
    t = (np.asarray(ks) + 1) * p["m"] - 1
    rows = []
    for h in hours:
        Hw, Lw = win(A["H"], t + 1, h * 60), win(A["L"], t + 1, h * 60)
        cls = classify_udr(Hw, Lw, p["up"][ks], p["lo"][ks])
        ok = cls != "X"
        n = int(ok.sum())
        cu, ct = ("U", "D") if side == -1 else ("D", "U")
        rows.append([name, h, n, K.fmt_ci(int((cls == cu).sum()), n), K.fmt_ci(int((cls == ct).sum()), n), K.fmt_ci(int((cls == "R").sum()), n), int((cls == "B").sum())])
    return rows


UDR_HEAD = ["set", "H (h)", "n", "P(counter-trend band first)", "P(trend-continuation band first)", "P(neither)", "both in one minute"]


def m_text(P, tf):
    d = P[tf]
    H, L, C = d["a"]["H"], d["a"]["L"], d["a"]["C"]
    out = [f"### {tf}: M1 range detector (n bars, zone tolerance x): number of ranges and median height % of the low", ""]
    rows = []
    for n in M_NS:
        for x in M_XS:
            r = detect_ranges(H, L, n, x)
            rows.append([n, f"{100 * x:.2f} %", len(r), f"{np.median([100 * (a[2] - a[3]) / a[3] for a in r]):.2f}" if r else "n/a"])
    out += [K.md_table(["n", "x", "ranges", "median height %"], rows), ""]
    rng = detect_ranges(H, L, M_N, M_X)
    ends_taken = np.zeros(len(H), bool)
    for s, e, _, _ in rng:
        ends_taken[s:e + 1] = True
    # M2: BB bands / mid vs the range edges / midpoint, against random windows of the same length that fail the range test
    gen = np.random.default_rng(0)
    cand = [j for j in range(M_N - 1, len(H)) if not ends_taken[j - M_N + 1:j + 1].any() and not np.isnan(H[j - M_N + 1:j + 1]).any()
            and not (clusters(H[j - M_N + 1:j + 1] >= H[j - M_N + 1:j + 1].max() * (1 - M_X)) >= 2 and clusters(L[j - M_N + 1:j + 1] <= L[j - M_N + 1:j + 1].min() * (1 + M_X)) >= 2)]
    pick = gen.choice(len(cand), size=min(len(rng), len(cand)), replace=False) if cand else []
    ctrl = [(cand[i] - M_N + 1, cand[i], float(H[cand[i] - M_N + 1:cand[i] + 1].max()), float(L[cand[i] - M_N + 1:cand[i] + 1].min())) for i in pick]
    rows = []
    for lab, wins in (("ranges (n=48, x=0.5 %)", rng), ("random windows failing the range test (seed 0)", ctrl)):
        for y in M_YS:
            nb = nm = den = 0
            for s, e, hi, lo in wins:
                up, lw, md = d["up"][s:e + 1], d["lo"][s:e + 1], d["mid"][s:e + 1]
                ok = ~np.isnan(up)
                mp = (hi + lo) / 2
                nb += int(((np.abs(up - hi) / hi <= y) & (np.abs(lw - lo) / lo <= y))[ok].sum())
                nm += int((np.abs(md - mp) / mp <= y)[ok].sum())
                den += int(ok.sum())
            rows.append([lab, f"{100 * y:.2f} %", len(wins), den, K.fmt_ci(nb, den), K.fmt_ci(nm, den)])
    out += ["M2 band vs edges: share of bars with BOTH bands within y of the range high/low, and with the BB mid within y of the range midpoint", "",
            K.md_table(["windows", "y", "windows n", "bars", "both bands near edges", "BB mid near midpoint"], rows), ""]
    # M3 pokes beyond an edge that close back inside within k bars, against closes outside the BB band
    rows = []
    for k in M_KS:
        nb = ne = nbb = 0
        n_poke = n_in = 0
        for s, e, hi, lo in rng:
            for b in range(e + 1, min(e + 25, len(H))):
                up_, dn_ = H[b] > hi, L[b] < lo
                if up_ and dn_:
                    break
                if up_ or dn_:
                    n_poke += 1
                    c = next((b + i for i in range(k) if b + i < len(C) and ((C[b + i] <= hi) if up_ else (C[b + i] >= lo))), None)
                    if c is not None:
                        n_in += 1
                        w_l, w_h = L[c + 1:c + 1 + M_HH], H[c + 1:c + 1 + M_HH]
                        if len(w_l) == M_HH and not np.isnan(w_l).any() and not np.isnan(d["lo"][c]):
                            ne += 1
                            nb_hit = (w_l.min() <= lo) if up_ else (w_h.max() >= hi)
                            nbb_hit = (w_l.min() <= d["lo"][c]) if up_ else (w_h.max() >= d["up"][c])
                            nb += int(nb_hit)
                            nbb += int(nbb_hit)
                    break
        rows.append([f"poke back inside within k={k}", f"{n_poke} pokes, {n_in} back inside", K.fmt_ci(nb, ne), K.fmt_ci(nbb, ne)])
    c_up = np.nonzero(C > d["up"])[0]
    c_dn = np.nonzero(C < d["lo"])[0]
    keep = [c for c in np.concatenate((c_up, c_dn)) if c > 0 and not (C[c - 1] > d["up"][c - 1] or C[c - 1] < d["lo"][c - 1])]
    hit = tot = 0
    for c in keep:
        w_l, w_h = L[c + 1:c + 1 + M_HH], H[c + 1:c + 1 + M_HH]
        if len(w_l) == M_HH and not np.isnan(w_l).any():
            tot += 1
            hit += int((w_l.min() <= d["lo"][c]) if C[c] > d["up"][c] else (w_h.max() >= d["up"][c]))
    rows.append(["control: first close outside the BB band (opposite band, fixed at the event bar)", f"{len(keep)} events", "n/a", K.fmt_ci(hit, tot)])
    out += [f"M3 pokes: reach the opposite range edge / the opposite BB band (fixed at the close-back bar) within {M_HH} bars", "",
            K.md_table(["event", "n", "opposite range edge reached", "opposite BB band reached"], rows), ""]
    # M4 midpoint touches: next-close side
    rows = []
    for lab, getmid in (("range midpoint", None), ("BB mid inside the range", d["mid"])):
        for appr in ("from below", "from above"):
            cnt = [0, 0, 0]
            tot = 0
            for s, e, hi, lo in rng:
                for b in range(s + 1, e + 1):
                    m_ = (hi + lo) / 2 if getmid is None else getmid[b]
                    if np.isnan(m_) or b + 3 >= len(C) or not (L[b] <= m_ <= H[b]):
                        continue
                    if (C[b - 1] < m_) != (appr == "from below"):
                        continue
                    tot += 1
                    for i in range(3):
                        cnt[i] += int(C[b + 1 + i] > m_)
            rows.append([lab, appr, tot] + [K.fmt_ci(c, tot) for c in cnt])
    out += ["M4 midpoint: share of the next 1 / 2 / 3 closes ABOVE the midpoint after a bar that touches it (descriptive; touches in one range overlap)", "",
            K.md_table(["midpoint", "approach", "n", "next close above", "2nd close above", "3rd close above"], rows), ""]
    return "\n".join(out)


# ---------------------------------------------------------------- full run
def full(A, P, S):
    mdd_bh = K.S.bh_mdd(A)
    p = P["1h"]
    a = p["a"]
    trials = []

    def gs(ks, side):
        t = (np.asarray(ks) + 1) * 60 - 1
        return t, K.net_cells(A, t, np.full(len(t), side), HS), (t + 1 + K.DELAY) // K.DAYMIN

    def arm(name, ks, side, cks, h, verdict=False):
        t, G, day = gs(ks, side)
        tc, Gc, dayc = gs(cks, side)
        r = K.verdict_arm(G[h], day, Gc[h], dayc, t, mdd_bh)
        trials.append([name, side, h, r["n"], f"{r['mean']:.5f}", f"{r['se']:.5f}", f"{r['net']:.5f}", f"{r['t_net']:.3f}", f"{r['diff']:.5f}", f"{r['t_diff']:.3f}",
                       r["verdict"] if verdict else "secondary"])
        return r if verdict else dict(r, verdict="secondary")

    AU = arm("AU: touch bar closes above its mid, LONG at its close, h=120", S["up_keep"], 1, S["up_ctrl"], PRIMARY_H, True)
    AD = arm("AD: touch bar closes below its mid, SHORT at its close, h=120", S["dn_keep"], -1, S["dn_ctrl"], PRIMARY_H, True)
    sec = []
    for h in HS:
        if h != PRIMARY_H:
            sec.append((f"AU h={h}", arm(f"AU h={h}", S["up_keep"], 1, S["up_ctrl"], h)))
            sec.append((f"AD h={h}", arm(f"AD h={h}", S["dn_keep"], -1, S["dn_ctrl"], h)))
    ks = S["ks"]
    # U/D/R tables
    udr = udr_rows(A, P, "primary: 1h, N=6, wick, first touch", ks, "1h", -1, OUT_H)
    c30 = {(m, y): cond30(P, ks, m, y) for m in (2, 3) for y in (0.25, 0.5)}
    on = c30[(2, 0.25)]
    other = []
    other += udr_rows(A, P, "30m centre-close ON (m=2, y=0.25)", ks[on], "1h", -1, (2,))
    other += udr_rows(A, P, "30m centre-close OFF", ks[~on], "1h", -1, (2,))
    for (m, y), v in c30.items():
        if (m, y) != (2, 0.25):
            other += udr_rows(A, P, f"30m centre-close ON (m={m}, y={y})", ks[v], "1h", -1, (2,))
    es = eases(P, ks)
    for nm, v in es.items():
        other += udr_rows(A, P, f"pressure eases ({nm}) true", ks[v], "1h", -1, (2,))
        other += udr_rows(A, P, f"pressure eases ({nm}) false", ks[~v], "1h", -1, (2,))
    dsign = p["dl"][ks] > 0
    other += udr_rows(A, P, "touch-bar taker delta > 0", ks[dsign], "1h", -1, (2,))
    other += udr_rows(A, P, "touch-bar taker delta <= 0", ks[~dsign], "1h", -1, (2,))
    sess = np.zeros(len(ks), bool)
    for i, k in enumerate(ks):
        d = dt.date(2022, 1, 1) + dt.timedelta(days=int(((k + 1) * 60 - 1) // K.DAYMIN))
        if d.weekday() < 5:
            sess[i] = 0 <= (k + 1) * 60 - open_idx(d) <= 60
    other += udr_rows(A, P, "decision 0-60 min after the US open", ks[sess], "1h", -1, (2,))
    other += udr_rows(A, P, "decision elsewhere", ks[~sess], "1h", -1, (2,))
    relw = (p["up"] - p["lo"]) / p["mid"]
    medw = np.nanmedian(relw)
    wide = relw[ks] > medw
    other += udr_rows(A, P, "BB width above DEV median", ks[wide], "1h", -1, (2,))
    other += udr_rows(A, P, "BB width at/below DEV median", ks[~wide], "1h", -1, (2,))
    for key, ev in S["ev"].items():
        if key in (("wick", 6), "mirror", "30m"):
            continue
        k2 = np.nonzero(ev["event"])[0]
        other += udr_rows(A, P, f"variant {key}", k2, "1h", -1, (2,))
    mir = np.nonzero(S["ev"]["mirror"]["event"])[0]
    ctrl_rows = udr_rows(A, P, "control: mirror (up-trend touch from above, bands fixed)", mir, "1h", 1, OUT_H)
    k30 = np.nonzero(S["ev"]["30m"]["event"])[0]
    ctrl_rows += udr_rows(A, P, "control: 30m mid touch (N=6), bands of the 30m bar", k30, "30m", -1, OUT_H)
    pre_bars = np.nonzero(S["ev"][("wick", 6)]["pre"])[0]
    gen = np.random.default_rng(0)
    rnd = gen.choice(pre_bars, size=min(len(pre_bars), 3000), replace=False)
    ctrl_rows += udr_rows(A, P, "control: same trend state, random hours (no touch required, seed 0, <= 3000)", np.sort(rnd), "1h", -1, OUT_H)
    nopre = np.nonzero(S["ev"][("wick", 6)]["tc"] & ~S["ev"][("wick", 6)]["pre"])[0]
    ctrl_rows += udr_rows(A, P, "control: wick touch of the mid with no precondition", nopre, "1h", -1, OUT_H)
    # close-side tables (touch bar and the next 3)
    cs = []
    for off in range(0, 4):
        j = ks + off
        j = j[j < len(a["C"])]
        up_ = int((a["C"][j] > p["mid"][j]).sum())
        cs.append([f"bar k+{off}" if off else "touch bar k", len(j), K.fmt_ci(up_, len(j))])
    allup = allun = mixed = 0
    for j in range(1, 4):
        pass
    nxt = np.array([[a["C"][k + o] > p["mid"][k + o] if k + o < len(a["C"]) else np.nan for o in (1, 2, 3)] for k in ks], float)
    for j in (1, 2, 3):
        sub = nxt[:, :j]
        ok = ~np.isnan(sub).any(1)
        au, ad = int((sub[ok].sum(1) == j).sum()), int((sub[ok].sum(1) == 0).sum())
        cs.append([f"next {j} closes: all above / all below / mixed", int(ok.sum()), f"{au} / {ad} / {int(ok.sum()) - au - ad}"])
    # MFE / MAE
    exc = []
    for side, nm in ((1, "LONG from touch-bar close"), (-1, "SHORT from touch-bar close")):
        for h in HS:
            fav, adv = K.excursion(A, (ks + 1) * 60 - 1 + 1 + K.DELAY, np.full(len(ks), side), h, p["atr"][ks])
            exc.append([nm, h, int((~np.isnan(fav)).sum()), f"{np.nanmedian(fav):.2f}", f"{np.nanmedian(adv):.2f}"])
    word = K.headline([AU["verdict"], AD["verdict"]])
    L = [word, "",
         "# RESULT: OPR-BB-MTF-CENTER, 1h touch of the BB mid in a lower-band trend, DEV screen (primary cell 1 min extra delay, h=120, cost 0.14 % round trip) + Krown M1-M4 descriptive tables", "",
         "**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. Rules frozen in PRE_REG.md (committed before this file). "
         "SOURCED = the operator's words in the draft (closes around the centre decide direction/confirmation/range; 30m centre closes; next 1-4 h); every threshold, entry, horizon and cost is OURS, written in PRE_REG.md before the run (the operator states no entry or stop).", "",
         f"Study word = {word} (PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: AU {AU['verdict']}; AD {AD['verdict']}.", "",
         "## Verdict arms (mean G % of notional after funding; SE day-clustered; control = wick touches of the 1h mid with NO precondition, same closing side, same cooldown)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row("AU: touch bar closes above its mid, LONG, h=120", AU), K.arm_row("AD: touch bar closes below its mid, SHORT, h=120", AD)]), "",
         f"Buy-and-hold DEV max drawdown {mdd_bh:.2f} % of price. PASS needs n >= {K.N_MIN}, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD.", "",
         "## Secondary cells (no verdict)", "", K.md_table(K.ARM_HEAD, [K.arm_row(nm, r) for nm, r in sec]), "",
         "## U / D / R (primary events; counter-trend band = the touch bar's UPPER band, trend-continuation = its LOWER band; fixed levels; Wilson 95 % CI; cells with n < 10 are not read)", "",
         K.md_table(UDR_HEAD, udr), "",
         "## U / D / R, H = 2 h, by condition (30m centre-close, pressure eases, flow, session, width, variants)", "", K.md_table(UDR_HEAD, other), "",
         "## Controls (mirror shows the trend-continuation band as the UPPER band)", "", K.md_table(UDR_HEAD, ctrl_rows), "",
         "## Close side of the 1h mid (touch bar and the next three closed bars)", "", K.md_table(["bar", "n", "closes above its own mid"], cs), "",
         "## MFE / MAE in ATR(14, 1h) from the entry open after the touch-bar close (medians)", "", K.md_table(["side", "h (min)", "n", "median MFE", "median MAE"], exc), "",
         "## Krown range tests M1-M4 (descriptive only; OURS definitions; no verdict; not a confirmation or refutation of Krown)", "", m_text(P, "1h"), m_text(P, "4h"),
         "## Data and decisions", "", "OI NOT_IN_DATA on DEV. The 'pressure eases' CVD-slope measure equals the 30m taker-delta measure over the same bars, so only delta4 and RSI are printed. Funding flat 1 bp per settlement crossed. A PASS would be a gross-effect finding on the Binance tape only.", "",
         count_text(A, P, S)]
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "trials.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cell", "side", "h", "n", "mean_G", "se", "net", "t_net", "diff_vs_ctrl", "t_diff", "verdict"])
        w.writerows(trials)
    t_all, G_all, _ = gs(ks, 1)
    with open(HERE / "ledger.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["touch_bar_open_utc_ms", "closes_above_mid", "G_long_h120"])
        for i, k in enumerate(ks):
            w.writerow([K.TS0 + int(k) * 3600 * 1000, int(a["C"][k] > p["mid"][k]), f"{G_all[PRIMARY_H][i]:.5f}"])
    sha = hashlib.sha256((HERE / "PRE_REG.md").read_bytes()).hexdigest()
    with open(HERE / "EXPOSURE_LEDGER.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["study", "run_utc", "data_source", "window_read", "split", "rule_sha256", "verdict", "decision_informed"])
        w.writerow(["opr_bb_mtf_center_2026-10-16", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "F:/MTS/data/tom_raw/klines 1m",
                    "2022-01-01..2024-06-30", "DEV", sha, word, "whether a 1h touch of the BB mid in a lower-band trend has a gross effect above 0.14 % (screen before G3 marks); Krown M1-M4 descriptive"])
    print(word)
    print("\n".join(L[1:14]))
    return 0


def main(argv):
    if "--count" not in argv and "--full" not in argv:
        print(__doc__)
        return 1
    A = K.load()
    P = prep(A)
    S = sets(P)
    if "--count" in argv:
        txt = count_text(A, P, S)
        (HERE / "COUNT.md").write_text("# COUNT (pre-outcome)\n\n" + txt + "\n", encoding="utf-8", newline="\n")
        print(txt)
        return 0
    return full(A, P, S)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
