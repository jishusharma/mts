"""T1 markdown rally-rejection short. Frozen spec: PRE_REG.md (read it first; nothing here is tuned).

    python study.py dev    DEV half (signal bar open 2019-01-01..2023-12-31). Reads data truncated at 2024-01-01: no VAL bar is loaded.
    python study.py val    VAL half (signal bar open >= 2024-01-01). Refuses unless code is unchanged since frozen.json's commit and frozen.json is committed.

Everything is computed here from raw 15m bars and the phase table; formulas follow FORMULAS.md s1 (RSI), s4 (EMA), s5 (WMA), s12 (ATR plain SMA).
Env flags STUDY_BUG=1 / PHASE_LAG=0 are deliberate look-ahead switches used only by test_study.py; dev/val refuse to run with them set.
"""
import os, sys, json, csv, hashlib, subprocess, datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE = Path(r"F:\MTS\data_cache")
PRIMARY_DIR = CACHE / "binance" / "t1-markdown-rally-rejection"
SECONDARY_DIR = CACHE / "binance_spot"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
PRIMARY = "EOS NEO IOTA ZEC DASH ZIL VET BAT ICX QTUM ONT ENJ MANA SAND THETA XTZ HBAR AAVE GRT CHZ".split()
SECONDARY = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
CODE_FILES = ["PRE_REG.md", "study.py", "fetch.py", "test_study.py", "verify_trades.py"]

MIN15, HOUR, DAY = 900_000, 3_600_000, 86_400_000
DEV_START = int(dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
SPLIT = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
FAR = 1 << 62
HOLD = 24                 # 1h bars held: entry bar j0 .. j0+23, exit at the close of bar j0+23 (24 h after the entry open)
FEE_TAKER, FEE_MAKER = 0.0012, 0.0006   # round trip, fraction of notional
STOP_FLOOR, SKIP_R, ATR_N = 0.012, 0.5, 14
SEED = 20261114
PH_IDS = {"CAPITULATION": 1, "MARKDOWN": 2, "RELIEF": 3, "ACCUM-RANGE": 4, "MARKUP": 5, "DISTRIBUTION": 6}
PH_NAMES = {v: k for k, v in PH_IDS.items()}
MD = PH_IDS["MARKDOWN"]
CYC_IDS = {"": 0, "BASE": 1, "BULL": 2, "BEAR": 3}
CYC_NAMES = {v: k for k, v in CYC_IDS.items()}


# ---------------------------------------------------------------- causality switches (tests only)
def study_bug():
    return os.environ.get("STUDY_BUG") == "1"


def phase_lag():
    return 0 if study_bug() else int(os.environ.get("PHASE_LAG", "1"))


# ---------------------------------------------------------------- bar helpers
def resample(t, o, h, l, c, v, k):
    """15m -> k x 15m, UTC-aligned buckets (floor(t / width)); a bucket is emitted only when all k source bars exist. Returns open time and OHLCV."""
    w = k * MIN15
    b = t // w
    starts = np.flatnonzero(np.r_[True, b[1:] != b[:-1]])
    cnt = np.diff(np.r_[starts, len(t)])
    ok = cnt == k
    s = starts[ok]
    return (b[s] * w, o[s], np.maximum.reduceat(h, starts)[ok], np.minimum.reduceat(l, starts)[ok], c[s + k - 1], np.add.reduceat(v, starts)[ok])


def daily_hlc(t, h, l, c):
    """complete UTC days only (96 x 15m bars): day number, high, low, close."""
    d = t // DAY
    starts = np.flatnonzero(np.r_[True, d[1:] != d[:-1]])
    cnt = np.diff(np.r_[starts, len(t)])
    ok = cnt == 96
    return d[starts][ok], np.maximum.reduceat(h, starts)[ok], np.minimum.reduceat(l, starts)[ok], c[starts + cnt - 1][ok]


def rsi_wilder(c, n):
    """FORMULAS s1: SMA seed over the first n deltas at index n, then Wilder smoothing. avg_loss == 0 -> 100 (gain) or 50 (flat)."""
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    g, ls = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    ag, al = g[:n].mean(), ls[:n].mean()

    def f(ag, al):
        if al == 0:
            return 100.0 if ag > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + ag / al)
    out[n] = f(ag, al)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + g[i - 1]) / n
        al = (al * (n - 1) + ls[i - 1]) / n
        out[i] = f(ag, al)
    return out


def _first_valid(x):
    ok = np.flatnonzero(~np.isnan(x))
    return int(ok[0]) if len(ok) else -1


def ema_series(x, n):
    """FORMULAS s4: alpha 2/(n+1), seed = SMA of the first n valid values."""
    out = np.full(len(x), np.nan)
    f = _first_valid(x)
    if f < 0 or len(x) - f < n:
        return out
    a = 2.0 / (n + 1)
    e = x[f:f + n].mean()
    out[f + n - 1] = e
    for i in range(f + n, len(x)):
        e = (x[i] - e) * a + e
        out[i] = e
    return out


def wma_series(x, n):
    """FORMULAS s5: weights 1..n, oldest lightest."""
    out = np.full(len(x), np.nan)
    f = _first_valid(x)
    if f < 0 or len(x) - f < n:
        return out
    w = np.arange(1, n + 1, dtype=float)
    out[f + n - 1:] = np.correlate(x[f:], w, "valid") / w.sum()
    return out


def atr_sma(h, l, c, n):
    """FORMULAS s12: plain SMA of true range over n bars; TR[0] undefined."""
    tr = np.full(len(c), np.nan)
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    out = np.full(len(c), np.nan)
    if len(c) > n:
        cs = np.cumsum(tr[1:])
        s = cs[n - 1:] - np.r_[0.0, cs[:-n]]
        out[n:] = s / n
    return out


def vwap_15m(t, h, l, c, v):
    """cumulative typical price x volume / volume of 15m bars, anchored 00:00 UTC (resets each UTC day). Value at index j includes bar j (its close)."""
    tp = (h + l + c) / 3.0
    d = t // DAY
    starts = np.flatnonzero(np.r_[True, d[1:] != d[:-1]])
    lens = np.diff(np.r_[starts, len(t)])
    pv, vv = np.cumsum(tp * v), np.cumsum(v)
    bpv = np.repeat(np.r_[0.0, pv][starts], lens)
    bvv = np.repeat(np.r_[0.0, vv][starts], lens)
    with np.errstate(invalid="ignore", divide="ignore"):
        vw = (pv - bpv) / (vv - bvv)
    vw[(vv - bvv) <= 0] = np.nan
    return vw, starts, lens


# ---------------------------------------------------------------- phase table
def read_phase_table(path=PHASE_CSV):
    """(day numbers, label id, cycle id). Provisional rows (the partial newest day) are skipped; blank labels = 0 (unavailable)."""
    days, lab, cyc = [], [], []
    for r in csv.DictReader(l for l in open(path) if not l.startswith("#")):
        if str(r.get("provisional", "False")).lower() == "true":
            continue
        days.append(dt.date.fromisoformat(r["date"]).toordinal() - 719163)
        lab.append(PH_IDS.get(r.get("label", ""), 0))
        cyc.append(CYC_IDS.get(r.get("cycle", ""), 0))
    return np.array(days), np.array(lab, dtype=np.int8), np.array(cyc, dtype=np.int8)


def markdown_for_day(dn, close, day, lag=None):
    """Independent MARKDOWN test (MTS_BRAINS_SPEC s1) for ONE UTC day from daily closes with day number <= day - lag only:
    c < SMA50, SMA50 / SMA50(10 rows earlier) - 1 <= -1%, and (BEAR or c < SMA200), BEAR = drawdown from the running max close <= -20% and c < SMA200.
    None when the row day-lag is missing or history is too short. (CAPITULATION overrides in the table; this is the MARKDOWN precondition.)"""
    lag = phase_lag() if lag is None else lag
    m = dn <= day - lag
    if not m.any() or dn[m][-1] != day - lag:
        return None
    c = np.asarray(close)[m]
    if len(c) < 200:
        return None
    s50, s50b, s200 = c[-50:].mean(), c[-60:-10].mean(), c[-200:].mean()
    bear = (c[-1] / c.max() - 1 <= -0.20) and c[-1] < s200
    return bool(c[-1] < s50 and s50 / s50b - 1 <= -0.01 and (bear or c[-1] < s200))


# ---------------------------------------------------------------- coin preparation (all indicator work, causal)
def prepare_coin(t, o, h, l, c, v, ptab):
    """15m bars -> dict of 1h arrays with, at each 1h bar i (open time th[i], close time th[i]+1h): classic pivots from the prior complete UTC day,
    ATR14, HM sell state read at the 30m bar closing with bar i, VWAP through bar i's close, phase/cycle of bar i's UTC day.
    STUDY_BUG=1 deliberately leaks: same-day pivots, whole-day VWAP, same-day phase (tests only)."""
    th, to, thh, tl, tc, tv = resample(t, o, h, l, c, v, 4)
    t30, _, _, _, c30, _ = resample(t, o, h, l, c, v, 2)
    n = len(th)
    # pivots
    dd, dh, dl, dc = daily_hlc(t, h, l, c)
    P_d = (dh + dl + dc) / 3.0
    R1_d, S1_d = 2 * P_d - dl, 2 * P_d - dh
    day = th // DAY
    want = day if study_bug() else day - 1
    k = np.searchsorted(dd, want)
    kc = np.minimum(k, max(len(dd) - 1, 0))
    okd = (k < len(dd)) & (dd[kc] == want) if len(dd) else np.zeros(n, bool)
    P = np.where(okd, P_d[kc] if len(dd) else np.nan, np.nan)
    R1 = np.where(okd, R1_d[kc] if len(dd) else np.nan, np.nan)
    S1 = np.where(okd, S1_d[kc] if len(dd) else np.nan, np.nan)
    # HM on 30m
    rs = rsi_wilder(c30, 9)
    e3, w21 = ema_series(rs, 3), wma_series(rs, 21)
    with np.errstate(invalid="ignore"):
        sell30 = (w21 > rs) & (w21 > e3)
    ok30 = ~(np.isnan(w21) | np.isnan(e3) | np.isnan(rs))
    j = np.searchsorted(t30, th + HOUR // 2)
    jc = np.minimum(j, max(len(t30) - 1, 0))
    hit = (j < len(t30)) & (t30[jc] == th + HOUR // 2) if len(t30) else np.zeros(n, bool)
    hm = hit & ok30[jc] & sell30[jc] if len(t30) else np.zeros(n, bool)
    # VWAP
    vw15, starts, lens = vwap_15m(t, h, l, c, v)
    if study_bug():
        last = starts + lens - 1
        vw15 = np.repeat(vw15[last], lens)
    q = np.searchsorted(t, th + 3 * MIN15)
    qc = np.minimum(q, len(t) - 1)
    hitv = (q < len(t)) & (t[qc] == th + 3 * MIN15)
    vw = np.where(hitv, vw15[qc], np.nan)
    atr = atr_sma(thh, tl, tc, ATR_N)
    # phase / cycle of the bar's UTC day (table value for that day; the table is lag 1 by construction, checked in verify_phase)
    pd_, pl, pc = ptab
    r = np.searchsorted(pd_, day)
    rc = np.minimum(r, max(len(pd_) - 1, 0))
    hp = (r < len(pd_)) & (pd_[rc] == day) if len(pd_) else np.zeros(n, bool)
    ph = np.where(hp, pl[rc], 0).astype(np.int8)
    cy = np.where(hp, pc[rc], 0).astype(np.int8)
    return dict(th=th, o=to, h=thh, l=tl, c=tc, P=P, R1=R1, S1=S1, atr=atr, hm=hm, vw=vw, ph=ph, cy=cy)


# ---------------------------------------------------------------- exit simulation (shared by taker, maker, placebo)
def sim_windows(Ow, Hw, Lw, Clast, stop, target):
    """Vectorised short exits over (N, HOLD) windows. Stop touch (high >= stop) fills at max(stop, bar open) (gap = worse); target touch (low <= target)
    fills at the level; same bar -> stop wins; neither -> close of the last bar. Returns exit offset, exit price, reason (0 time, 1 stop, 2 target)."""
    N = len(stop)
    sh, tg = Hw >= stop[:, None], Lw <= target[:, None]
    fs = np.where(sh.any(1), sh.argmax(1), 99)
    ft = np.where(tg.any(1), tg.argmax(1), 99)
    st_first = fs <= ft
    st_first &= fs < 99
    tg_first = (ft < fs)
    rows = np.arange(N)
    off = np.where(st_first, fs, np.where(tg_first, ft, HOLD - 1))
    px = np.where(st_first, np.maximum(stop, Ow[rows, np.minimum(fs, HOLD - 1)]), np.where(tg_first, target, Clast))
    return off, px, np.where(st_first, 1, np.where(tg_first, 2, 0)).astype(np.int8)


def coin_candidates(pc, lo, hi):
    """Every raw trigger (P or R1 rejection on a 1h bar whose open time is in [lo, hi)) with the filters as flags and both entry models simulated.
    Nothing is dropped for phase/HM/VWAP here: masks are applied per variant. Rows are in bar order."""
    th, o, h, l, c = pc["th"], pc["o"], pc["h"], pc["l"], pc["c"]
    n = len(th)
    P, R1, S1, atr = pc["P"], pc["R1"], pc["S1"], pc["atr"]
    with np.errstate(invalid="ignore"):
        trR1 = (h > R1) & (c < R1)
        trP = (h > P) & (c < P)
    lvl = np.where(trR1, 1, np.where(trP, 0, -1))
    i = np.flatnonzero((lvl >= 0) & (th >= lo) & (th < hi) & ~np.isnan(atr) & ~np.isnan(S1))
    i = i[(i + HOLD < n)]
    i = i[(th[i + 1] - th[i] == HOUR) & (th[i + HOLD] - th[i] == HOLD * HOUR)]
    lv = lvl[i]
    tgt = np.where(lv == 1, P[i], S1[i])
    j0 = i + 1
    W = j0[:, None] + np.arange(HOLD)
    Ow, Hw, Lw, Clast = o[W], h[W], l[W], c[j0 + HOLD - 1]
    out = dict(i=i, t=th[i], lvl=lv, ph=pc["ph"][i], cy=pc["cy"][i], hm=pc["hm"][i], vw=(c[i] < pc["vw"][i]), fill=h[j0] > c[i])
    for kind, entry, fee in (("tk", o[j0], FEE_TAKER), ("mk", c[i], FEE_MAKER)):
        D = np.maximum(np.maximum(h[i] - entry, 1.0 * atr[i]), STOP_FLOOR * entry)
        ok = (tgt < entry) & ((entry - tgt) >= SKIP_R * D)
        stop = entry + D
        off, px, why = sim_windows(Ow, Hw, Lw, Clast, stop, tgt)
        out.update({kind + "_entry": entry, kind + "_D": D, kind + "_ok": ok, kind + "_off": off, kind + "_gross": (entry - px) / D,
                    kind + "_cost": fee * entry / D, kind + "_why": why, kind + "_hold": (entry - Clast) / D, kind + "_tgt": tgt})
    out["mk_ok"] = out["mk_ok"] & out["fill"]
    out["mk_att"] = (tgt < out["mk_entry"]) & ((out["mk_entry"] - tgt) >= SKIP_R * out["mk_D"])
    return out


def pick_trades(cd, mask, kind):
    """one open position per coin: a signal on bar i' is taken only if i' >= the previous trade's exit bar (i + 1 + offset)."""
    idx = np.flatnonzero(mask & cd[kind + "_ok"])
    keep, free = [], -1
    ii, off = cd["i"], cd[kind + "_off"]
    for k in idx:
        if ii[k] >= free:
            keep.append(k)
            free = ii[k] + 1 + off[k]
    return np.array(keep, dtype=np.int64)


VARIANTS = {   # name -> (phase rule, needs HM, needs VWAP)
    "main": ("md", True, True), "no_hm": ("md", False, True), "no_vwap": ("md", True, False), "neither": ("md", False, False),
    "control_non_md": ("non", True, True),
}


def variant_mask(cd, name):
    ph, hm, vw = VARIANTS[name]
    m = (cd["ph"] == MD) if ph == "md" else ((cd["ph"] != MD) & (cd["ph"] > 0))
    if hm:
        m = m & cd["hm"]
    if vw:
        m = m & cd["vw"]
    return m


def trades_for(cands, name, kind="tk"):
    """cands: {coin: candidates dict}. Returns the trade table (dict of arrays) over all coins for one variant and one entry model."""
    rows = []
    for coin, cd in cands.items():
        k = pick_trades(cd, variant_mask(cd, name), kind)
        if len(k) == 0:
            continue
        rows.append(dict(coin=np.array([coin] * len(k)), t=cd["t"][k], day=cd["t"][k] // DAY, lvl=cd["lvl"][k], ph=cd["ph"][k], cy=cd["cy"][k],
                         entry=cd[kind + "_entry"][k], D=cd[kind + "_D"][k], tgt=cd[kind + "_tgt"][k], gross=cd[kind + "_gross"][k], cost=cd[kind + "_cost"][k],
                         hold=cd[kind + "_hold"][k], why=cd[kind + "_why"][k], off=cd[kind + "_off"][k], i=cd["i"][k]))
    if not rows:
        return empty_trades()
    return {key: np.concatenate([r[key] for r in rows]) for key in rows[0]}


def empty_trades():
    return dict(coin=np.array([], dtype=str), t=np.array([], dtype=np.int64), day=np.array([], dtype=np.int64), lvl=np.array([], dtype=int), ph=np.array([], dtype=np.int8),
                cy=np.array([], dtype=np.int8), entry=np.array([]), D=np.array([]), tgt=np.array([]), gross=np.array([]), cost=np.array([]), hold=np.array([]),
                why=np.array([], dtype=np.int8), off=np.array([], dtype=int), i=np.array([], dtype=int))


def concat_trades(parts):
    parts = [p for p in parts if len(p["t"])]
    if not parts:
        return empty_trades()
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


# ---------------------------------------------------------------- statistics
def boot_days(day, net, draws=5000, seed=SEED):
    """95% CI of mean net R per trade, bootstrap over UTC days (ratio of resampled sums), fixed seed."""
    ud, inv = np.unique(day, return_inverse=True)
    S, N = np.bincount(inv, weights=net), np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    D = len(ud)
    out = np.empty(draws)
    for a in range(0, draws, 250):
        b = min(draws, a + 250)
        idx = rng.integers(0, D, (b - a, D))
        out[a:b] = S[idx].sum(1) / N[idx].sum(1)
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def summarize(tr, ci=True, fee_scale=1.0):
    n = len(tr["t"])
    if n == 0:
        return dict(n=0, days=0)
    net = tr["gross"] - tr["cost"] * fee_scale
    w, ls = net[net > 0], -net[net <= 0]
    S = {}
    ud, inv = np.unique(tr["day"], return_inverse=True)
    Sd, Nd = np.bincount(inv, weights=net), np.bincount(inv).astype(float)
    top = np.argsort(-Sd)[:5]
    exb = float((Sd.sum() - Sd[top].sum()) / (Nd.sum() - Nd[top].sum())) if len(ud) > 5 else float("nan")
    S.update(n=n, days=int(len(ud)), win=float((net > 0).mean()),
             be_win=float(ls.mean() / (w.mean() + ls.mean())) if len(w) and len(ls) else float("nan"),
             gross=float(tr["gross"].mean()), cost=float((tr["cost"] * fee_scale).mean()), net=float(net.mean()), sd_net=float(net.std(ddof=1)) if n > 1 else float("nan"),
             exbest5=exb, hold_gross=float(tr["hold"].mean()), hold_net=float((tr["hold"] - tr["cost"] * fee_scale).mean()),
             stop_pct=float((tr["why"] == 1).mean()), target_pct=float((tr["why"] == 2).mean()), time_pct=float((tr["why"] == 0).mean()))
    if ci:
        S["ci_lo"], S["ci_hi"] = boot_days(tr["day"], net)
    return S


def group_rows(tr, key):
    out = []
    for g in sorted(set(key.tolist())):
        m = key == g
        sub = {k: v[m] for k, v in tr.items()}
        s = summarize(sub, ci=False)
        out.append(dict(group=g, n=s["n"], days=s["days"], gross=s["gross"], net=s["net"], win=s["win"]))
    return out


def by_tables(tr):
    if len(tr["t"]) == 0:
        return dict(symbol=[], year=[], cycle=[])
    yr = np.array([dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc).year for x in tr["t"]])
    return dict(symbol=group_rows(tr, tr["coin"]), year=group_rows(tr, yr), cycle=group_rows(tr, np.array([CYC_NAMES[int(x)] or "none" for x in tr["cy"]])))


# ---------------------------------------------------------------- placebo: same-phase random shorts
def build_pool(preps, lo, hi):
    """global bar store + eligible entry bars (entry bar on a MARKDOWN day, full contiguous 24-bar window, open time in [lo, hi)), keyed by (coin, UTC hour)."""
    O, H, L, C, offs, keys, gidx = [], [], [], [], {}, [], []
    base = 0
    for coin, pc in preps.items():
        th = pc["th"]
        n = len(th)
        offs[coin] = base
        O.append(pc["o"]); H.append(pc["h"]); L.append(pc["l"]); C.append(pc["c"])
        j = np.flatnonzero((pc["ph"][:n - HOLD + 1] == MD) & (th[:n - HOLD + 1] >= lo) & (th[:n - HOLD + 1] < hi))
        j = j[th[j + HOLD - 1] - th[j] == (HOLD - 1) * HOUR]
        hr = (th[j] % DAY) // HOUR
        for x, hh in zip(j, hr):
            keys.append((coin, int(hh))); gidx.append(base + int(x))
        base += n
    pool = {}
    for kk, g in zip(keys, gidx):
        pool.setdefault(kk, []).append(g)
    return dict(O=np.concatenate(O), H=np.concatenate(H), L=np.concatenate(L), C=np.concatenate(C), offs=offs, pool={k: np.array(v) for k, v in pool.items()})


def placebo(tr, preps, lo, hi, draws=1000, seed=SEED):
    """1000 draws; each real trade -> a random bar of the same coin and UTC entry hour on a MARKDOWN day with the same stop-distance % and target-distance %;
    same exit rule and same cost in R. Returns real mean net R, placebo mean of means, EXCESS, p = (1 + #(placebo >= real)) / (draws + 1)."""
    if len(tr["t"]) == 0:
        return dict(n=0)
    P = build_pool(preps, lo, hi)
    hr = ((tr["t"] + HOUR) % DAY) // HOUR   # entry bar = signal bar + 1h
    lists = [P["pool"].get((c, int(h))) for c, h in zip(tr["coin"], hr)]
    keep = np.array([x is not None and len(x) > 0 for x in lists])
    lists = [x for x, k in zip(lists, keep) if k]
    dp = (tr["D"] / tr["entry"])[keep]
    tp = ((tr["entry"] - tr["tgt"]) / tr["entry"])[keep]
    cost_r = (FEE_TAKER / dp)
    real = float((tr["gross"] - tr["cost"])[keep].mean())
    cnt = np.array([len(x) for x in lists])
    flat = np.concatenate(lists)
    start = np.r_[0, np.cumsum(cnt)[:-1]]
    rng = np.random.default_rng(seed)
    ar = np.arange(HOLD)
    means = np.empty(draws)
    for d in range(draws):
        j = flat[start + (rng.random(len(cnt)) * cnt).astype(np.int64)]
        W = j[:, None] + ar
        entry = P["O"][j]
        off, px, why = sim_windows(P["O"][W], P["H"][W], P["L"][W], P["C"][j + HOLD - 1], entry * (1 + dp), entry * (1 - tp))
        means[d] = ((entry - px) / (entry * dp) - cost_r).mean()
    return dict(n=int(keep.sum()), dropped_no_pool=int((~keep).sum()), real_net=real, placebo_mean=float(means.mean()), placebo_sd=float(means.std()), excess=real - float(means.mean()),
                p=float((1 + (means >= real).sum()) / (draws + 1)))


def verdict(s, pb):
    """PRE_REG PASS bar for ONE split on the primary sample (the lead combines DEV and VAL)."""
    if s.get("n", 0) < 150 or s.get("days", 0) < 40:
        return "UNDERPOWERED"
    ok = s["net"] > 0 and s["ci_lo"] > 0 and s["exbest5"] > 0 and pb.get("excess", -1) > 0 and pb.get("p", 1) < 0.05
    return "PASS" if ok else "FAIL"


# ---------------------------------------------------------------- analysis of one split
def analyze(preps_by_sample, lo, hi, with_placebo=True, progress=print):
    """preps_by_sample: {sample: {coin: prepared}}; returns the full result dict for signals with bar open time in [lo, hi)."""
    res = dict(lo=lo, hi=hi, samples={})
    cands_all = {}
    for sname, preps in preps_by_sample.items():
        cands_all[sname] = {coin: coin_candidates(pc, lo, hi) for coin, pc in preps.items()}
    cands_all["pooled"] = {**cands_all.get("primary", {}), **cands_all.get("secondary", {})}
    preps_all = dict(preps_by_sample)
    preps_all["pooled"] = {**preps_by_sample.get("primary", {}), **preps_by_sample.get("secondary", {})}
    trades_out = {}
    for sname, cands in cands_all.items():
        if not cands:
            continue
        S = dict(coins=len(cands), variants={}, maker={}, signals_per_phase={})
        for vn in VARIANTS:
            tr = trades_for(cands, vn)
            S["variants"][vn] = summarize(tr)
            if vn == "main":
                S["by"] = by_tables(tr)
                trades_out[sname] = tr
                if with_placebo:
                    progress(f"  placebo {sname} ...")
                    S["placebo"] = placebo(tr, preps_all[sname], lo, hi)
                S["verdict"] = verdict(S["variants"]["main"], S.get("placebo", {}))
        # maker row (6 bp, not pass-bearing)
        mk_mask = lambda cd: variant_mask(cd, "main")
        att = sum(int((mk_mask(cd) & cd["mk_att"]).sum()) for cd in cands.values())
        fil = sum(int((mk_mask(cd) & cd["mk_att"] & cd["fill"]).sum()) for cd in cands.values())
        trm = concat_trades([_one_maker(cd, coin) for coin, cd in cands.items()])
        S["maker"] = dict(summary=summarize(trm), attempted=att, filled=fil, fill_ratio=fil / att if att else float("nan"))
        # signal counts per phase (trigger + HM + VWAP, before the 0.5R skip and the one-position rule)
        cnt = {}
        for cd in cands.values():
            m = cd["hm"] & cd["vw"]
            for p in range(0, 7):
                cnt[PH_NAMES.get(p, "no-label")] = cnt.get(PH_NAMES.get(p, "no-label"), 0) + int((m & (cd["ph"] == p)).sum())
        S["signals_per_phase"] = cnt
        res["samples"][sname] = S
    return res, trades_out


def _one_maker(cd, coin):
    k = pick_trades(cd, variant_mask(cd, "main"), "mk")
    if len(k) == 0:
        return empty_trades()
    return dict(coin=np.array([coin] * len(k)), t=cd["t"][k], day=cd["t"][k] // DAY, lvl=cd["lvl"][k], ph=cd["ph"][k], cy=cd["cy"][k], entry=cd["mk_entry"][k], D=cd["mk_D"][k],
                tgt=cd["mk_tgt"][k], gross=cd["mk_gross"][k], cost=cd["mk_cost"][k], hold=cd["mk_hold"][k], why=cd["mk_why"][k], off=cd["mk_off"][k], i=cd["i"][k])


# ---------------------------------------------------------------- data loading
def load_npz(path, hi=None):
    z = np.load(path)
    t = z["t"] if "t" in z.files else z["ts"]
    t = t.astype(np.int64)
    if t[0] > 10**14:
        t = t // 1000
    elif t[0] < 10**11:
        t = t * 1000
    o, h, l, c, v = (z[k].astype(float) for k in "ohlcv")
    _, u = np.unique(t, return_index=True)
    t, o, h, l, c, v = t[u], o[u], h[u], l[u], c[u], v[u]
    if hi is not None:
        m = t < hi
        t, o, h, l, c, v = t[m], o[m], h[m], l[m], c[m], v[m]
    return t, o, h, l, c, v


def load_samples(ptab, hi=None):
    out = dict(primary={}, secondary={})
    dropped = {}
    pdir_drop = PRIMARY_DIR / "dropped.json"
    dropped = json.loads(pdir_drop.read_text()) if pdir_drop.exists() else {}
    for s in PRIMARY:
        p = PRIMARY_DIR / f"{s}USDT_15m.npz"
        if s in dropped or not p.exists():
            dropped.setdefault(s, "missing")
            continue
        out["primary"][s] = prepare_coin(*load_npz(p, hi), ptab)
    for s in SECONDARY:
        out["secondary"][s] = prepare_coin(*load_npz(SECONDARY_DIR / f"{s}USDT_15m.npz", hi), ptab)
    return out, dropped


# ---------------------------------------------------------------- regime mix and phase-lag verification
def regime_mix(ptab):
    days, lab, cyc = ptab
    d0, d1 = DEV_START // DAY, SPLIT // DAY
    mix = {}
    for name, m in (("DEV", (days >= d0) & (days < d1)), ("VAL", days >= d1)):
        mix[name] = {PH_NAMES.get(p, "no-label"): int(((lab == p) & m).sum()) for p in range(0, 7)}
        mix[name]["total_days"] = int(m.sum())
    return mix


def verify_phase(ptab, last_day):
    """Recompute the MARKDOWN precondition from BTC daily closes truncated at d-1 for every DEV day and compare with the table.
    Reads the repo's btc_daily.csv (study run only). Also checks the table's close_used against the previous day's close."""
    btc = REPO / "MyTradingSys" / "research" / "btc_cycles_2026-11" / "btc_daily.csv"
    dn, cl = [], []
    for r in csv.DictReader(open(btc)):
        dn.append(dt.date.fromisoformat(r["date"]).toordinal() - 719163); cl.append(float(r["close"]))
    dn, cl = np.array(dn), np.array(cl)
    days, lab, cyc = ptab
    stat = dict(days_checked=0, md_table_and_t2=0, md_table_not_t2=0, t2_not_md_table_capitulation=0, t2_not_md_table_other=0, no_data=0)
    close_used_mismatch = 0
    used = {}
    for r in csv.DictReader(l for l in open(PHASE_CSV) if not l.startswith("#")):
        if r["close_used"]:
            used[dt.date.fromisoformat(r["date"]).toordinal() - 719163] = float(r["close_used"])
    byday = dict(zip(dn.tolist(), cl.tolist()))
    for d, lb in zip(days.tolist(), lab.tolist()):
        if d < DEV_START // DAY or d > last_day or lb == 0:
            continue
        stat["days_checked"] += 1
        t2 = markdown_for_day(dn, cl, d, lag=1)
        if d in used and (d - 1) in byday and abs(used[d] - byday[d - 1]) > 1e-6 * byday[d - 1]:
            close_used_mismatch += 1
        if t2 is None:
            stat["no_data"] += 1
        elif lb == MD:
            stat["md_table_and_t2" if t2 else "md_table_not_t2"] += 1
        elif t2:
            stat["t2_not_md_table_capitulation" if lb == PH_IDS["CAPITULATION"] else "t2_not_md_table_other"] += 1
    stat["close_used_vs_prev_close_mismatch"] = close_used_mismatch
    return stat


# ---------------------------------------------------------------- output
def fmt(x):
    return f"{x:.4f}" if isinstance(x, float) else str(x)


def write_outputs(res, trades, tag, mix, dropped, extra):
    rows = []
    for sname, S in res["samples"].items():
        for vn, s in S["variants"].items():
            rows.append(dict(sample=sname, variant=vn, **s))
        rows.append(dict(sample=sname, variant="maker_6bp", **S["maker"]["summary"], fill_ratio=S["maker"]["fill_ratio"]))
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(HERE / f"{tag}_main.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})
    for what in ("symbol", "year", "cycle"):
        with open(HERE / f"{tag}_by_{what}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["sample", what, "n", "days", "gross", "net", "win"])
            for sname, S in res["samples"].items():
                for g in S.get("by", {}).get(what, []):
                    w.writerow([sname, g["group"], g["n"], g["days"], round(g["gross"], 5), round(g["net"], 5), round(g["win"], 4)])
    tr_path = HERE / f"{tag}_trades.csv"
    cols = ["sample", "coin", "t_utc", "level", "phase", "cycle", "entry", "D", "target", "gross_R", "cost_R_12bp", "net_R_12bp", "hold24_gross_R", "exit"]
    nrows = 0
    with open(tr_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for sname in ("primary", "secondary"):
            tr = trades.get(sname)
            if tr is None:
                continue
            for k in range(len(tr["t"])):
                w.writerow([sname, tr["coin"][k], np.datetime_as_string(np.datetime64(int(tr["t"][k]), "ms"), unit="m"), "R1" if tr["lvl"][k] else "P", PH_NAMES.get(int(tr["ph"][k]), ""),
                            CYC_NAMES[int(tr["cy"][k])], round(float(tr["entry"][k]), 8), round(float(tr["D"][k]), 8), round(float(tr["tgt"][k]), 8), round(float(tr["gross"][k]), 5),
                            round(float(tr["cost"][k]), 5), round(float(tr["gross"][k] - tr["cost"][k]), 5), round(float(tr["hold"][k]), 5), "time stop target".split()[int(tr["why"][k])]])
                nrows += 1
    size = tr_path.stat().st_size
    summ = dict(tag=tag, mix=mix, dropped=dropped, trades_csv_bytes=size, trades_rows=nrows, result=res, extra=extra)
    (HERE / f"{tag}_tables.json").write_text(json.dumps(summ, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    return size


def print_summary(res, mix, tag, dropped, extra, out):
    L = out.append
    L(f"== {tag} summary ==")
    L(f"Regime mix (days per phase from the phase table): {json.dumps(mix)}")
    L(f"dropped coins (<730 d or missing): {json.dumps(dropped)}")
    L(f"phase verification: {json.dumps(extra.get('phase_check'))}")
    for sname, S in res["samples"].items():
        L(f"-- sample {sname} ({S['coins']} coins) --")
        for vn, s in S["variants"].items():
            if s.get("n", 0) == 0:
                L(f"  {vn}: n 0")
                continue
            L(f"  {vn}: n {s['n']} days {s['days']} win {s['win']:.3f} be_win {s['be_win']:.3f} gross {s['gross']:.4f} cost {s['cost']:.4f} net {s['net']:.4f} "
              f"CI[{s['ci_lo']:.4f},{s['ci_hi']:.4f}] exbest5 {s['exbest5']:.4f} sd_net {s['sd_net']:.4f} hold24_gross {s['hold_gross']:.4f} hold24_net {s['hold_net']:.4f} "
              f"stop/target/time {s['stop_pct']:.2f}/{s['target_pct']:.2f}/{s['time_pct']:.2f}")
        m = S["maker"]["summary"]
        if m.get("n", 0):
            L(f"  maker_6bp: n {m['n']} fill_ratio {S['maker']['fill_ratio']:.3f} gross {m['gross']:.4f} cost {m['cost']:.4f} net {m['net']:.4f} CI[{m['ci_lo']:.4f},{m['ci_hi']:.4f}]")
        pb = S.get("placebo")
        if pb and pb.get("n"):
            L(f"  placebo: n {pb['n']} real_net {pb['real_net']:.4f} placebo_mean {pb['placebo_mean']:.4f} EXCESS {pb['excess']:.4f} p {pb['p']:.4f}")
        L(f"  signals per phase (trigger+HM+VWAP): {json.dumps(S['signals_per_phase'])}")
        L(f"  verdict (this split only, PRE_REG bar): {S['verdict']}")


# ---------------------------------------------------------------- frozen protocol
def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)


def rel(name):
    return (HERE / name).relative_to(REPO).as_posix()


def check_frozen():
    """val refuses unless frozen.json exists and is committed unmodified, its commit is an ancestor of HEAD, and every code file equals its recorded sha256
    both in the working tree and in that commit."""
    fp = HERE / "frozen.json"
    if not fp.exists():
        return "frozen.json missing"
    if git("ls-files", "--error-unmatch", rel("frozen.json")).returncode != 0:
        return "frozen.json is not committed"
    if git("status", "--porcelain", "--", rel("frozen.json")).stdout.strip():
        return "frozen.json has uncommitted changes"
    fr = json.loads(fp.read_text())
    if git("merge-base", "--is-ancestor", fr["code_commit"], "HEAD").returncode != 0:
        return "frozen commit is not an ancestor of HEAD"
    for f in CODE_FILES:
        want = fr["sha256"][f]
        if sha256(HERE / f) != want:
            return f"{f} changed since the freeze (working tree)"
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{fr['code_commit']}:{rel(f)}"], capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() != want:
            return f"{f} differs from the frozen commit"
    return None


def cmd(which):
    if study_bug() or "PHASE_LAG" in os.environ:
        sys.exit("refusing: STUDY_BUG / PHASE_LAG are test-only switches")
    if which == "val":
        why = check_frozen()
        if why:
            sys.exit("val refused: " + why)
        lo, hi, hi_load, tag = SPLIT, FAR, None, "val"
    else:
        lo, hi, hi_load, tag = DEV_START, SPLIT, SPLIT, "dev"
    ptab = read_phase_table()
    mix = regime_mix(ptab)
    print("Regime mix:", json.dumps(mix), flush=True)
    extra = {}
    if which == "dev":
        extra["phase_check"] = verify_phase(ptab, SPLIT // DAY - 1)
        print("phase check:", extra["phase_check"], flush=True)
    samples, dropped = load_samples(ptab, hi_load)
    print("coins:", {k: len(v) for k, v in samples.items()}, "dropped", dropped, flush=True)
    res, trades = analyze(samples, lo, hi)
    size = write_outputs(res, trades, tag, mix, dropped, extra)
    out = []
    print_summary(res, mix, tag, dropped, extra, out)
    (HERE / f"{tag}_summary.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    print("trades csv bytes", size)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("dev", "val"):
        sys.exit(__doc__)
    cmd(sys.argv[1])
