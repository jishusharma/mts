"""T3 early-uptrend continuation long, fresh coins (t3-early-uptrend-continuation-1114). Definitions are frozen in PRE_REG.md.
No fee constant is defined here: costs come from MyTradingSys/backtest/fees.py. Public Binance daily spot klines only.

  python t3_study.py --window dev            # DEV only. Truncates the loaded bars at DEV_END + 62 days and asserts that no
                                          # entry-day >= 2024-01-01 outcome exists, so VAL cannot be read by accident.
  python t3_study.py --window val --unlock-val   /  --window all --unlock-val    # only after code/tests are frozen and committed

Outputs (DEV): dev_trades.csv, dev_summary.json.  (VAL/all): val_trades.csv + val_summary.json / all_trades.csv + results.json.
STUDY_BUG=1 turns on deliberate look-aheads (same-day phase label, centred volume median) so the tests can prove they bite."""
import os
import sys
import json
import math
import argparse
import datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from MyTradingSys.backtest import fees  # noqa: E402

BUG = bool(os.environ.get("STUDY_BUG"))
DATA = os.environ.get("T3_DATA", r"F:\MTS\data_cache\binance\t3-early-uptrend-1114")
BRAIN_CSV = os.environ.get("T3_BRAIN", r"F:\MTS\data_cache\mts_brains\phase_daily.csv")
DAY = 86400000
CANDS = ("NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT "
         "AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN").split()


def day_num(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


def day_str(n):
    return (dt.date(1970, 1, 1) + dt.timedelta(days=int(n))).isoformat()


START_DAY = day_num(2017, 9, 1)
DEV_END_DAY = day_num(2023, 12, 31)
VAL_START_DAY = day_num(2024, 1, 1)
DATA_END_MS = int(dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)  # only bars closed by 2026-11-13 24:00
HALVINGS = [day_num(2012, 11, 28), day_num(2016, 7, 9), day_num(2020, 5, 11), day_num(2024, 4, 20)]
EARLY_DAYS = 540          # UP_E: fewer than 540 days since the last halving (OURS)
SLOPE_WIN = 20            # 20-day slope of the SMA200 (OURS)
MIN_BARS = 250            # entries from the coin's 250th bar
PHASE_NAMES = ["UP_E", "UP_L", "MIX", "DOWN"]    # UP_L = other UP

COST12 = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13     # 12 bp round trip, imported from fees.py
COST6 = COST12 / 2                                         # 6 bp row, informational
FLAT_FUND_DAY = 3 * 0.0001                                 # flat assumption: 1 bp per 8 h = 3 bp / day paid by longs (OURS)

STOP_ATR, MIN_STOP, TARGET_R = 2.5, 0.02, 3.0
HOLD = {"RIDE": 60, "CAP3R": 30}
KINDS = ("RIDE", "CAP3R")
CELLS = ("A", "B")
REASON = {1: "STOP", 2: "TARGET", 3: "SIGNAL", 4: "TIME", 5: "DELIST"}
BOOT_B, BOOT_SEED, DRAWS = 2000, 1114, 1000


# ------------------------------------------------------------------ indicators (FORMULAS s1, s4, s5, s12, s30)
def atr_sma(h, l, c, n=14):
    """Plain SMA of true range (FORMULAS s12); NaN until n TRs exist."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    tr = np.full(len(c), np.nan)
    tr[1:] = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])
    return pd.Series(tr).rolling(n).mean().to_numpy()


def rsi_wilder(c, n=14):
    """Textbook Wilder RSI with SMA seed (FORMULAS s1); NaN before index n."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    g, ls = np.maximum(d, 0), np.maximum(-d, 0)
    ag, al = g[:n].mean(), ls[:n].mean()

    def val(ag, al):
        if al == 0:
            return 100.0 if ag > 0 else 50.0
        return 100 - 100 / (1 + ag / al)
    out[n] = val(ag, al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + ls[i]) / n
        out[i + 1] = val(ag, al)
    return out


def ema_sma_seed(x, n):
    """EMA alpha 2/(n+1), seed = SMA of the first n valid values (FORMULAS s4); NaN before."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    ok = np.flatnonzero(~np.isnan(x))
    if len(ok) < n:
        return out
    s = ok[0]
    a = 2.0 / (n + 1)
    i0 = s + n - 1
    out[i0] = x[s:s + n].mean()
    for i in range(i0 + 1, len(x)):
        out[i] = (x[i] - out[i - 1]) * a + out[i - 1]
    return out


def wma(x, n):
    """Linear WMA, weights 1..n oldest to newest (FORMULAS s5); NaN until n valid values."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    w = np.arange(1, n + 1, dtype=float)
    for i in range(len(x) - n + 1):
        win = x[i:i + n]
        if not np.isnan(win).any():
            out[i + n - 1] = (win * w).sum() / w.sum()
    return out


def adx_di(h, l, c, n=14):
    """Wilder DI+, DI-, ADX (FORMULAS s30.1: sum-seeded smoothing, ADX = mean of the first n DX then recursive)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    m = len(c)
    dip, dim, adx = (np.full(m, np.nan) for _ in range(3))
    if m <= 2 * n:
        return dip, dim, adx
    tr = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])
    up, dn = h[1:] - h[:-1], l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    st, sp, sm = tr[:n].sum(), pdm[:n].sum(), mdm[:n].sum()
    dx = []
    for i in range(n - 1, len(tr)):
        if i >= n:
            st = st - st / n + tr[i]
            sp = sp - sp / n + pdm[i]
            sm = sm - sm / n + mdm[i]
        a = 100 * sp / st if st else 0.0
        b = 100 * sm / st if st else 0.0
        dip[i + 1], dim[i + 1] = a, b
        dx.append(100 * abs(a - b) / (a + b) if (a + b) else 0.0)
        k = len(dx)
        if k == n:
            adx[i + 1] = float(np.mean(dx))
        elif k > n:
            adx[i + 1] = (adx[i] * (n - 1) + dx[-1]) / n
    return dip, dim, adx


def weekly_vwap(ts, h, l, c, v):
    """Weekly-anchored VWAP of the typical price (h+l+c)/3, resetting Monday 00:00 UTC; the bar's own volume is included."""
    day = np.asarray(ts) // DAY
    wk = (day + 3) // 7            # 1970-01-01 is a Thursday: (day+3)//7 increments on Mondays
    tp = (np.asarray(h, float) + np.asarray(l, float) + np.asarray(c, float)) / 3
    pv = pd.Series(tp * np.asarray(v, float)).groupby(wk).cumsum().to_numpy()
    vv = pd.Series(np.asarray(v, float)).groupby(wk).cumsum().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(vv > 0, pv / vv, np.nan)


# ------------------------------------------------------------------ BTC phase label (causal)
def phase_labels(btc_ts, btc_c, bug=None):
    """UP_E / UP_L / MIX / DOWN codes 0..3 from BTC daily closes. The label computed from the close of day d is KEYED to day d+1, so
    an entry on day D reads only closes <= D-1. bug=True keys it to day d (same-day close: look-ahead).
    UP = close > SMA200 and 20-day slope of the SMA200 > 0; DOWN = close < SMA200 and slope < 0; else MIX; UP is split into UP_E
    (fewer than 540 days since the last halving, FORMULAS s25 clock at the label's own bar) and UP_L."""
    bug = BUG if bug is None else bug
    c = np.asarray(btc_c, float)
    dnum = np.asarray(btc_ts) // DAY
    sma = pd.Series(c).rolling(200).mean().to_numpy()
    slope = np.full(len(c), np.nan)
    slope[SLOPE_WIN:] = sma[SLOPE_WIN:] - sma[:-SLOPE_WIN]
    up = (c > sma) & (slope > 0)
    dn = (c < sma) & (slope < 0)
    hv = np.array(HALVINGS)
    since = np.array([d - hv[hv <= d].max() if (hv <= d).any() else 10 ** 6 for d in dnum])
    lab = np.where(up, np.where(since < EARLY_DAYS, 0, 1), np.where(dn, 3, 2)).astype(float)
    lab[np.isnan(sma) | np.isnan(slope)] = np.nan
    keys = dnum if bug else dnum + 1
    return keys, lab


def phase_for_days(table, days):
    keys, lab = table
    days = np.asarray(days)
    ix = np.clip(np.searchsorted(keys, days), 0, len(keys) - 1)
    ok = keys[ix] == days
    return np.where(ok, lab[ix], np.nan)


# ------------------------------------------------------------------ data
class Seg:
    """One contiguous daily series of one coin (a calendar gap > 1 day starts a new segment: indicators never span a gap).
    ended = True when the segment's data genuinely stops before the global data end (gap after it, or the coin's archive ends
    earlier): open positions are then force-closed at its last close (DELIST) instead of dropped."""
    ended = False


def split_segments(sym, d, fund):
    """d: dict of arrays ts,o,h,l,c,v,tbv, sorted unique. Returns list of Seg."""
    ts = d["ts"]
    cut = np.flatnonzero(np.diff(ts) != DAY) + 1
    bounds = [0] + cut.tolist() + [len(ts)]
    out = []
    for k, (a, b) in enumerate(zip(bounds[:-1], bounds[1:])):
        s = Seg()
        s.sym = sym
        s.name = sym if len(bounds) == 2 else f"{sym}#{k + 1}"
        for key in ("ts", "o", "h", "l", "c", "v", "tbv"):
            setattr(s, key, d[key][a:b])
        s.fund = fund
        out.append(s)
    return out


def load_coin(sym, end_ms, root=None):
    root = root or DATA
    df = pd.read_csv(os.path.join(root, "spot_1d", f"{sym}USDT.csv")).drop_duplicates("ts").sort_values("ts")
    full_last = int(df.ts.max()) if len(df) else None       # last bar of the whole file (timestamp only; used to tell a real end from a DEV cut)
    df = df[df.ts + DAY <= end_ms]
    d = {k: df[k].to_numpy(dtype=np.int64 if k == "ts" else float) for k in ("ts", "o", "h", "l", "c", "v", "tbv")}
    d["full_last"] = full_last
    fp = os.path.join(root, "funding", f"{sym}USDT.csv")
    fund = None
    if os.path.exists(fp):
        f = pd.read_csv(fp).sort_values("ts")
        f = f[f.ts <= end_ms + DAY]
        if len(f):
            fund = (f.ts.to_numpy(np.int64), f.rate.to_numpy(float))
    return d, fund


def cum_funding(ts, fund):
    """Cumulative funding paid per unit notional at every bar open (n+1 boundary points, the last = close of the last bar).
    A day interval (open_{k-1}, open_k] is covered when real prints span it and it holds at least one print; a day outside the print
    range (or with no print) pays the flat assumption FLAT_FUND_DAY. Returns cf and the cumulative count of flat days."""
    n = len(ts)
    grid = np.append(ts, ts[-1] + DAY)
    if fund is None or len(fund[0]) == 0:
        inc = np.full(n, FLAT_FUND_DAY)
        flat = np.ones(n)
    else:
        fts, fr = fund
        cs = np.concatenate([[0.0], np.cumsum(fr)])
        hi = np.searchsorted(fts, grid, side="right")          # prints with ts <= boundary
        real = cs[hi[1:]] - cs[hi[:-1]]
        cnt = hi[1:] - hi[:-1]
        covered = (grid[:-1] >= fts[0] - 1) & (grid[1:] <= fts[-1] + 8 * 3600000) & (cnt > 0)
        inc = np.where(covered, real, FLAT_FUND_DAY)
        flat = (~covered).astype(float)
    return np.concatenate([[0.0], np.cumsum(inc)]), np.concatenate([[0.0], np.cumsum(flat)])


# ------------------------------------------------------------------ features: cells A and B
def coin_features(s, bug=None):
    """Signal STATES (not onsets) of cells A and B for every bar, from bars <= that bar only."""
    bug = BUG if bug is None else bug
    sr = pd.Series
    dip, dim, adx = adx_di(s.h, s.l, s.c, 14)
    adx_ok = (adx >= 20) & (dip > dim)
    if bug:
        med = sr(s.v).rolling(31, center=True).median().to_numpy()          # deliberate look-ahead
    else:
        med = sr(s.v).rolling(30).median().shift(1).to_numpy()              # prior 30 days, current bar excluded
    volx = s.v >= 2 * med
    rsi = rsi_wilder(s.c, 9)
    e3 = ema_sma_seed(rsi, 3)
    w21 = wma(rsi, 21)
    hm_buy = (w21 < rsi) & (w21 < e3)
    vw = weekly_vwap(s.ts, s.h, s.l, s.c, s.v)
    return {"A": np.asarray(adx_ok & volx, bool), "B": np.asarray(hm_buy & (s.c > vw), bool), "atr": atr_sma(s.h, s.l, s.c, 14)}


def onset(state):
    prev = np.zeros(len(state), bool)
    prev[1:] = state[:-1]
    return state & ~prev


# ------------------------------------------------------------------ trade simulator (long only, daily bars)
def simulate(o, h, l, c, atr, kind, force_end=False):
    """Every signal bar s (entry at open[s+1]). Returns dict of arrays (length n; the last bar has no entry bar):
    xi = last bar the position occupies (-1 unresolved), px = exit price, reason code, stop, S, entry, ret (gross fraction), risk = S/entry.
    Stop S = max(2.5*ATR14[s], 2% of entry); a stop fills at the worse of stop and open; if stop and target are both inside one bar the
    stop wins. RIDE: exit at the next open after a close below the prior-10-day low, time exit at the close of day 60 (entry day =
    day 1). CAP3R: +3R target (filled at the target), time exit at the close of day 30.
    force_end (the segment ends before the global data end, i.e. the coin was delisted / its archive stops): a position still open
    at the segment's last bar is closed at that bar's close, reason DELIST (code 5), so delist/crash losses are not dropped. At the
    global end (force_end False) an unresolved trade stays xi=-1 and is dropped (PRE_REG)."""
    n = len(c)
    H = HOLD[kind]
    sig = np.arange(n - 1)
    e = sig + 1
    entry = o[e]
    S = np.maximum(STOP_ATR * atr[sig], MIN_STOP * entry)
    stop = entry - S
    tgt = entry + TARGET_R * S
    xi = np.full(n - 1, -1, np.int64)
    px = np.full(n - 1, np.nan)
    rs = np.zeros(n - 1, np.int8)
    lvl = pd.Series(l).rolling(10).min().shift(1).to_numpy()
    alive = np.flatnonzero(np.isfinite(S))
    for k in range(H):
        if alive.size == 0:
            break
        jj = e[alive] + k
        keep = jj < n
        alive, jj = alive[keep], jj[keep]
        if alive.size == 0:
            break
        oj, hj, lj, cj = o[jj], h[jj], l[jj], c[jj]
        st = stop[alive]
        hit_s = lj <= st
        fill = np.zeros(alive.size)
        code = np.zeros(alive.size, np.int8)
        fill[hit_s] = np.where(oj <= st, oj, st)[hit_s]
        code[hit_s] = 1
        done = hit_s.copy()
        if kind == "CAP3R":
            hit_t = ~done & (hj >= tgt[alive])
            fill[hit_t] = tgt[alive][hit_t]
            code[hit_t] = 2
            done |= hit_t
        else:
            nxt = np.minimum(jj + 1, n - 1)
            sg = ~done & np.isfinite(lvl[jj]) & (cj < lvl[jj]) & (jj + 1 < n)
            fill[sg] = o[nxt][sg]
            code[sg] = 3
            done |= sg
        if k == H - 1:
            tm = ~done
            fill[tm] = cj[tm]
            code[tm] = 4
            done |= tm
        if done.any():
            a = alive[done]
            xi[a] = jj[done]
            px[a] = fill[done]
            rs[a] = code[done]
        alive = alive[~done]
    if force_end:
        un = np.flatnonzero((xi < 0) & np.isfinite(S))
        xi[un] = n - 1
        px[un] = c[n - 1]
        rs[un] = 5
    out = {}
    for key, arr, fillv in (("xi", xi, -1), ("px", px, np.nan), ("reason", rs, 0), ("stop", stop, np.nan), ("S", S, np.nan),
                            ("entry", entry, np.nan)):
        full = np.full(n, fillv, dtype=arr.dtype)
        full[:-1] = arr
        out[key] = full
    with np.errstate(invalid="ignore"):
        out["ret"] = (out["px"] - out["entry"]) / out["entry"]
        out["risk"] = out["S"] / out["entry"]
    return out


def greedy(idx, xi):
    """Non-overlapping trades per coin: take the first signal, skip signals before its last occupied bar, repeat."""
    out, nxt = [], -1
    for i, x in zip(np.asarray(idx).tolist(), np.asarray(xi).tolist()):
        if i >= nxt:
            out.append(i)
            nxt = x
    return np.array(out, dtype=np.int64)


# ------------------------------------------------------------------ statistics
def week_of(day):
    return (np.asarray(day) + 3) // 7


def week_boot(vals, weeks, B=BOOT_B, seed=BOOT_SEED, shift=0.0):
    """Week-cluster bootstrap of the mean: resample weeks with replacement. Mean (minus shift), 95% CI, one-sided p (H0: mean <= shift)."""
    vals = np.asarray(vals, float)
    n = len(vals)
    if n == 0:
        return dict(n=0, weeks=0, mean=None, ci_lo=None, ci_hi=None, p=None)
    _, inv = np.unique(weeks, return_inverse=True)
    g = inv.max() + 1
    sums = np.bincount(inv, weights=vals, minlength=g)
    cnt = np.bincount(inv, minlength=g).astype(float)
    rng = np.random.default_rng(seed)
    ix = rng.integers(0, g, size=(B, g))
    m = sums[ix].sum(1) / cnt[ix].sum(1) - shift
    return dict(n=int(n), weeks=int(g), mean=float(vals.mean()) - shift, ci_lo=float(np.percentile(m, 2.5)),
                ci_hi=float(np.percentile(m, 97.5)), p=float((np.sum(m <= 0) + 1) / (B + 1)))


def bh_q(p):
    p = np.asarray(p, float)
    m = len(p)
    order = np.argsort(p)
    q = p[order] * m / (np.arange(m) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.minimum(q, 1.0)
    return out


def ex_best(vals, k=5):
    v = np.sort(np.asarray(vals, float))
    return float(v[:-k].mean()) if len(v) > k else None


# ------------------------------------------------------------------ build per-segment tables
class World:
    pass


def build_world(segs, btc, bug=None, sig_override=None):
    """segs: list of Seg; btc: dict with ts, c. Computes features, phase codes, simulations and funding for every segment.
    sig_override (tests): {cell: [bool array per seg]} replaces the indicator states."""
    bug = BUG if bug is None else bug
    w = World()
    w.segs = segs
    w.table = phase_labels(btc["ts"], btc["c"], bug)
    for si, s in enumerate(segs):
        n = len(s.c)
        s.n = n
        s.day = s.ts // DAY
        f = coin_features(s, bug)
        s.atr = f["atr"]
        s.state = {c: (np.asarray(sig_override[c][si], bool) if sig_override else f[c]) for c in CELLS}
        s.phase = phase_for_days(w.table, s.day + 1)             # phase of the ENTRY day of a signal on this bar
        idx = np.arange(n)
        s.elig = (idx >= MIN_BARS - 1) & (idx < n - 1) & (s.day + 1 >= START_DAY)
        s.cf, s.flat = cum_funding(s.ts, s.fund)
        s.sim = {k: simulate(s.o, s.h, s.l, s.c, s.atr, k, force_end=bool(getattr(s, "ended", False))) for k in KINDS}
    return w


TCOLS = ["cell", "kind", "coin", "si", "i", "signal_date", "entry_date", "entry_day", "entry_px", "exit_date", "exit_px",
         "exit_reason", "stop", "S", "gross_R", "funding", "fund_flat", "net_R", "net_R6", "phase", "week", "days_held",
         "year", "ret", "risk"]


def _rows(s, si, sm, idx, cell, kind):
    e = idx + 1
    xi = sm["xi"][idx]
    fund = s.cf[xi + 1] - s.cf[e]
    flat = (s.flat[xi + 1] - s.flat[e]) > 0
    ret, risk = sm["ret"][idx], sm["risk"][idx]
    exit_day = s.day[xi] + (sm["reason"][idx] == 3)
    return dict(cell=cell, kind=kind, coin=s.name, si=si, i=idx, signal_date=[day_str(d) for d in s.day[idx]],
                entry_date=[day_str(d) for d in s.day[e]], entry_day=s.day[e], entry_px=sm["entry"][idx],
                exit_date=[day_str(d) for d in exit_day], exit_px=sm["px"][idx],
                exit_reason=[REASON[int(r)] for r in sm["reason"][idx]], stop=sm["stop"][idx], S=sm["S"][idx],
                gross_R=ret / risk, funding=fund, fund_flat=flat, net_R=(ret - COST12 - fund) / risk,
                net_R6=(ret - COST6 - fund) / risk, phase=s.phase[idx], week=week_of(s.day[e]),
                days_held=xi - e + 1, year=[int(day_str(d)[:4]) for d in s.day[e]], ret=ret, risk=risk)


def trade_frame(w, cell, kind, phase_set):
    """All non-overlapping trades of one cell/kind whose entry-day phase is in phase_set (codes). Rows are NOT window-filtered."""
    rows = []
    for si, s in enumerate(w.segs):
        sm = s.sim[kind]
        on = onset(s.state[cell]) & s.elig & (sm["xi"] >= 0) & np.isin(s.phase, phase_set)
        idx = np.flatnonzero(on)
        if not len(idx):
            continue
        idx = greedy(idx, sm["xi"][idx])
        rows.append(pd.DataFrame(_rows(s, si, sm, idx, cell, kind)))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame({c: [] for c in TCOLS})


def window_mask(df, window):
    if window == "dev":
        return (df.entry_day <= DEV_END_DAY).to_numpy()
    return (df.entry_day >= VAL_START_DAY).to_numpy()


# ------------------------------------------------------------------ baselines
def pool_for(w, kind, window):
    """All eligible coin-days of the window in UP_E with a resolved trade: the random same-phase entry pool."""
    si_l, i_l, r_l, xi_l = [], [], [], []
    delist = 0
    for si, s in enumerate(w.segs):
        sm = s.sim[kind]
        ed = s.day + 1
        m = s.elig & (sm["xi"] >= 0) & (s.phase == 0)
        m &= (ed <= DEV_END_DAY) if window == "dev" else (ed >= VAL_START_DAY)
        idx = np.flatnonzero(m)
        if not len(idx):
            continue
        xi = sm["xi"][idx]
        delist += int((sm["reason"][idx] == 5).sum())
        fund = s.cf[xi + 1] - s.cf[idx + 1]
        si_l.append(np.full(len(idx), si))
        i_l.append(idx)
        xi_l.append(xi)
        r_l.append((sm["ret"][idx] - COST12 - fund) / sm["risk"][idx])
    if not si_l:
        return None
    return dict(si=np.concatenate(si_l), i=np.concatenate(i_l), xi=np.concatenate(xi_l), r=np.concatenate(r_l), delist=delist)


def dropped_unresolved(w, cell, kind, window):
    """Signal onsets (phase UP_E, window entry day) still open at the GLOBAL data end: the only trades now dropped (xi = -1)."""
    n = 0
    for s in w.segs:
        sm = s.sim[kind]
        ed = s.day + 1
        m = onset(s.state[cell]) & s.elig & (sm["xi"] < 0) & np.isfinite(sm["S"]) & (s.phase == 0)
        m &= (ed <= DEV_END_DAY) if window == "dev" else (ed >= VAL_START_DAY)
        n += int(m.sum())
    return n


def random_baseline(pool, n, draws=DRAWS, seed=BOOT_SEED):
    """draws of n entries from the pool in random order, each accepted only if the coin has no open trade (no overlap)."""
    if pool is None or n == 0:
        return np.array([])
    rng = np.random.default_rng(seed)
    N = len(pool["r"])
    nseg = int(pool["si"].max()) + 1
    maxlen = int(max(pool["xi"].max(), pool["i"].max())) + 2
    means = np.empty(draws)
    for d in range(draws):
        occ = np.zeros((nseg, maxlen), bool)
        acc = []
        for j in rng.permutation(N):
            a, b, sg = pool["i"][j], pool["xi"][j], pool["si"][j]
            if occ[sg, a:b + 1].any():
                continue
            occ[sg, a:b + 1] = True
            acc.append(j)
            if len(acc) == n:
                break
        means[d] = pool["r"][acc].mean()
    return means


def basket_daily(w, window):
    """Equal-weight basket of all eligible coins, daily open-to-open return of day D (open[D] to open[D+1]), averaged over the
    window's UP_E days (gross, no costs). The label of day D is phase[i-1] for bar index i (phase[j] labels day[j]+1)."""
    d_l, r_l = [], []
    for s in w.segs:
        if s.n < 3:
            continue
        r = s.o[2:] / s.o[1:-1] - 1                  # bars i = 1..n-2: return of day[i]
        lab, el, dd = s.phase[:s.n - 2], s.elig[:s.n - 2], s.day[1:s.n - 1]
        m = (lab == 0) & el & ((dd <= DEV_END_DAY) if window == "dev" else (dd >= VAL_START_DAY))
        d_l.append(dd[m])
        r_l.append(r[m])
    if not d_l:
        return None
    df = pd.DataFrame({"d": np.concatenate(d_l), "r": np.concatenate(r_l)})
    g = df.groupby("d").r.mean()
    return dict(days=int(len(g)), mean_daily=float(g.mean()) if len(g) else None)


# ------------------------------------------------------------------ one trade set
def stats_row(df, pool, with_baseline=True, draws=DRAWS):
    r = df.net_R.to_numpy()
    base = week_boot(r, df.week.to_numpy())
    out = dict(n=int(len(df)), weeks=base["weeks"], mean_net_R12=base["mean"], ci_lo=base["ci_lo"], ci_hi=base["ci_hi"], p_one_sided=base["p"],
               mean_net_R6=float(df.net_R6.mean()) if len(df) else None, mean_gross_R=float(df.gross_R.mean()) if len(df) else None,
               win_rate=float((r > 0).mean()) if len(df) else None, ex_best5=ex_best(r), flat_fund_n=int(df.fund_flat.sum()),
               days_held_total=int(df.days_held.sum()) if len(df) else 0)
    if len(df):
        out["mean_net_daily"] = float((df.ret - COST12 - df.funding).sum() / df.days_held.sum())
    if with_baseline and len(df) and pool is not None:
        rm = random_baseline(pool, len(df), draws)
        rmean = float(rm.mean())
        ex = week_boot(r, df.week.to_numpy(), shift=rmean)
        out.update(random_mean=rmean, random_sd=float(rm.std()), excess=ex["mean"], excess_ci_lo=ex["ci_lo"], excess_ci_hi=ex["ci_hi"],
                   excess_p=ex["p"], random_pool=int(len(pool["r"])), random_pool_delist=int(pool["delist"]))
    return out


def per_group(df, col):
    return {str(k): dict(n=int(len(g)), mean_net_R12=float(g.net_R.mean()), win_rate=float((g.net_R > 0).mean()))
            for k, g in df.groupby(col)}


def regime_mix(w, window, trades):
    """Share of calendar days (BTC label defined, entry-day convention) and of signal trades (RIDE, both cells, all phases)."""
    keys, lab = w.table
    lo, hi = (START_DAY, DEV_END_DAY) if window == "dev" else (VAL_START_DAY, 10 ** 9)
    m = ~np.isnan(lab) & (keys >= lo) & (keys <= hi)
    days = np.bincount(lab[m].astype(int), minlength=4)
    t = trades[window_mask(trades, window)] if len(trades) else trades
    cnt = np.bincount(t.phase.astype(int), minlength=4) if len(t) else np.zeros(4, int)
    return {"calendar_days": {PHASE_NAMES[i]: int(days[i]) for i in range(4)},
            "calendar_share": {PHASE_NAMES[i]: float(days[i] / days.sum()) if days.sum() else None for i in range(4)},
            "trade_counts": {PHASE_NAMES[i]: int(cnt[i]) for i in range(4)},
            "trade_share": {PHASE_NAMES[i]: float(cnt[i] / cnt.sum()) if cnt.sum() else None for i in range(4)}}


def brain_join(df):
    """Informational: UP_E signal trades per MTS brain label / cycle (phase_daily.csv, joined on the SIGNAL date; reporting only)."""
    if not os.path.exists(BRAIN_CSV) or not len(df):
        return None
    b = pd.read_csv(BRAIN_CSV, usecols=["date", "label", "cycle"]).fillna({"label": "NONE"}).drop_duplicates("date").set_index("date")
    j = b.reindex(df.signal_date.to_numpy())
    lab, cyc = j.label.fillna("NONE").to_numpy(), j.cycle.fillna("NONE").to_numpy()
    sub = df[lab == "MARKUP"]
    return {"label_counts": pd.Series(lab).value_counts().to_dict(), "cycle_counts": pd.Series(cyc).value_counts().to_dict(),
            "up_e_and_markup": dict(n=int(len(sub)), mean_net_R12=float(sub.net_R.mean()) if len(sub) else None)}


def analyse_window(w, window, draws=DRAWS):
    res = dict(window=window, cells={}, basket=basket_daily(w, window))
    allc = []
    for cell in CELLS:
        cr = {}
        for kind in KINDS:
            full = trade_frame(w, cell, kind, [0])
            tr = full[window_mask(full, window)]
            cr[kind] = stats_row(tr, pool_for(w, kind, window), True, draws)
            row = cr[kind]
            row["per_symbol"] = per_group(tr, "coin") if len(tr) else {}
            row["per_year"] = per_group(tr, "year") if len(tr) else {}
            row["max_year_share"] = float(tr.year.value_counts(normalize=True).max()) if len(tr) else None
            row["one_year_flag"] = bool(len(tr) and tr.year.value_counts(normalize=True).max() > 0.85)
            row["exit_reasons"] = tr.exit_reason.value_counts().to_dict() if len(tr) else {}
            row["delist_forced"] = int((tr.exit_reason == "DELIST").sum()) if len(tr) else 0
            row["dropped_at_global_end"] = dropped_unresolved(w, cell, kind, window)
            ctl_all = trade_frame(w, cell, kind, [1, 2, 3])
            ctl = ctl_all[window_mask(ctl_all, window)]
            row["control_non_UP_E"] = stats_row(ctl, None, with_baseline=False)
            row["control_by_phase"] = {PHASE_NAMES[int(float(k))]: v for k, v in per_group(ctl, "phase").items()} if len(ctl) else {}
            if kind == "RIDE":
                cr["brain_join"] = brain_join(tr)
                allc += [tr, ctl]
            cr[kind + "_trades"] = tr
        res["cells"][cell] = cr
    qs = bh_q([res["cells"][c]["RIDE"].get("excess_p", 1.0) for c in CELLS])     # BH over the two cells' one-sided excess p, m = 2
    for c, q in zip(CELLS, qs):
        res["cells"][c]["RIDE"]["bh_q"] = float(q)
    res["regime_mix"] = regime_mix(w, window, pd.concat(allc, ignore_index=True))
    return res


def verdict(dev, val):
    """Bars 1-8 of PRE_REG on VAL at 12 bp, RIDE row unless stated (val None: DEV-only mode, bar 7 only)."""
    out = {}
    for c in CELLS:
        d = dev["cells"][c]["RIDE"]
        dm = d["mean_net_R12"]
        bars = {7: dict(desc="DEV mean net R > 0 (sign check)", value=dm, ok=bool(dm is not None and dm > 0))}
        if val is None:
            out[c] = dict(verdict="DEV-ONLY (no VAL read)", bars=bars)
            continue
        v, cap = val["cells"][c]["RIDE"], val["cells"][c]["CAP3R"]
        bars[1] = dict(desc="n >= 30 and >= 20 distinct entry weeks", value=(v["n"], v["weeks"]), ok=bool(v["n"] >= 30 and v["weeks"] >= 20))
        bars[2] = dict(desc="mean net R > 0", value=v["mean_net_R12"], ok=bool(v["mean_net_R12"] is not None and v["mean_net_R12"] > 0))
        bars[3] = dict(desc="EXCESS week-cluster CI low > 0", value=v.get("excess_ci_lo"), ok=bool(v.get("excess_ci_lo") is not None and v["excess_ci_lo"] > 0))
        bars[4] = dict(desc="BH q < 0.05 (m=2)", value=v.get("bh_q"), ok=bool(v.get("bh_q") is not None and v["bh_q"] < 0.05))
        bars[5] = dict(desc="ex-best-5 mean net R > 0 (CAP3R)", value=cap["ex_best5"], ok=bool(cap["ex_best5"] is not None and cap["ex_best5"] > 0))
        bk = (val["basket"] or {}).get("mean_daily")
        sd = v.get("mean_net_daily")
        bars[6] = dict(desc="signal net daily return in position >= basket daily mean", value=(sd, bk), ok=bool(sd is not None and bk is not None and sd >= bk))
        y24, y25 = v["per_year"].get("2024"), v["per_year"].get("2025")
        bars[8] = dict(desc="2024 and 2025 both mean net R > 0", value=(y24 and y24["mean_net_R12"], y25 and y25["mean_net_R12"]),
                       ok=bool(y24 and y25 and y24["mean_net_R12"] > 0 and y25["mean_net_R12"] > 0))
        if not bars[1]["ok"]:
            vd = "NOT PASS (UNDERPOWERED)"
        elif not all(bars[k]["ok"] for k in (2, 3, 4, 5, 6, 7)):
            vd = "FAIL"
        elif not bars[8]["ok"] or v["one_year_flag"]:
            vd = "SINGLE-EPISODE (bars 1-7 met; cannot count as PASS)"
        else:
            vd = "PASS"
        out[c] = dict(verdict=vd, bars=bars, one_year_flag=v["one_year_flag"])
    return out


# ------------------------------------------------------------------ driver
def load_world(window, root=None):
    root = root or DATA
    end = DATA_END_MS if window in ("val", "all") else int((DEV_END_DAY + 1 + 62) * DAY)   # DEV: bars after DEV_END+62d are never loaded
    btc, _ = load_coin("BTC", end, root)
    segs, kept, dropped = [], {}, {}
    for sym in CANDS:
        if not os.path.exists(os.path.join(root, "spot_1d", f"{sym}USDT.csv")):
            dropped[sym] = "no data file"
            continue
        d, fund = load_coin(sym, end, root)
        if not len(d["ts"]):
            dropped[sym] = "no bars in window"
            continue
        ss = split_segments(sym, d, fund)
        for k, s in enumerate(ss):
            last = k == len(ss) - 1
            # a gap after the segment is a real end; the last segment ends for real only if the whole file stops there before the global end
            s.ended = (not last) or (int(s.ts[-1]) == d["full_last"] and d["full_last"] + DAY < DATA_END_MS)
        ok = [s for s in ss if len(s.c) >= MIN_BARS]
        for s in ss:
            if len(s.c) < MIN_BARS:
                dropped[s.name] = f"{len(s.c)} bars < {MIN_BARS}"
        if ok:
            segs += ok
            kept[sym] = dict(bars=int(sum(len(s.c) for s in ok)), first=day_str(ok[0].ts[0] // DAY), last=day_str(ok[-1].ts[-1] // DAY),
                             funding_prints=0 if fund is None else int(len(fund[0])), segments=[s.name for s in ok])
    return build_world(segs, btc), kept, dropped


def assert_dev_clean(trades):
    if len(trades) and trades.entry_day.max() > DEV_END_DAY:
        raise RuntimeError("DEV guard: a trade with entry day >= 2024-01-01 reached the DEV output")


def clean_json(o):
    if isinstance(o, dict):
        return {str(k): clean_json(v) for k, v in o.items() if not str(k).endswith("_trades")}
    if isinstance(o, (list, tuple)):
        return [clean_json(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


OUTCOLS = ["cell", "kind", "coin", "signal_date", "entry_date", "entry_px", "exit_date", "exit_px", "exit_reason", "stop", "S", "gross_R",
           "funding", "net_R", "net_R6", "fund_flat", "phase"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", choices=["dev", "val", "all"], required=True)
    ap.add_argument("--unlock-val", action="store_true", help="required for val/all: VAL is read only after code+tests are frozen")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args(argv)
    if a.window != "dev" and not a.unlock_val:
        print("refused: --window val/all needs --unlock-val (VAL stays unread until the code and tests are frozen and committed)")
        return 2
    w, kept, dropped = load_world(a.window)
    res = {"meta": dict(coins_kept=kept, coins_dropped=dropped, n_segments=len(w.segs), cost12=COST12, cost6=COST6, study_bug=BUG,
                        window=a.window)}
    dev = val = None
    allf = []
    if a.window in ("dev", "all"):
        dev = res["dev"] = analyse_window(w, "dev")
        for c in CELLS:
            for k in KINDS:
                assert_dev_clean(dev["cells"][c][k + "_trades"])
                allf.append(dev["cells"][c][k + "_trades"])
    if a.window in ("val", "all"):
        val = res["val"] = analyse_window(w, "val")
        allf += [val["cells"][c][k + "_trades"] for c in CELLS for k in KINDS]
    res["verdict"] = verdict(dev, val) if dev is not None else None
    res["survivorship"] = {wn: {c: {k: dict(delist_forced=r["cells"][c][k]["delist_forced"], pool_delist=r["cells"][c][k].get("random_pool_delist"),
                                            dropped_at_global_end=r["cells"][c][k]["dropped_at_global_end"]) for k in KINDS} for c in CELLS}
                           for wn, r in (("dev", dev), ("val", val)) if r is not None}
    res["meta"]["segments_ended_early"] = [s.name for s in w.segs if s.ended]
    tag = {"dev": ("dev_trades.csv", "dev_summary.json"), "val": ("val_trades.csv", "val_summary.json"),
           "all": ("all_trades.csv", "results.json")}[a.window]
    pd.concat(allf, ignore_index=True)[OUTCOLS].to_csv(os.path.join(a.out, tag[0]), index=False)
    with open(os.path.join(a.out, tag[1]), "w") as f:
        json.dump(clean_json(res), f, indent=1)
    print("wrote", tag[0], tag[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
