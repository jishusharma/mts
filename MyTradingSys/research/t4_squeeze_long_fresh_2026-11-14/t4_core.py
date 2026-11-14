"""T4 core: indicators, signal, phase flag, trade simulator, cost model for the trapped-shorts squeeze long on fresh coins.

Definitions are copied unchanged from the miner (combo-edge-miner-1114_2026-11-14/miner.py, read from trunk) and frozen in
PRE_REG.md of this folder. No fee constant is defined here: costs come from MyTradingSys/backtest/fees.py. Labels: SOURCED =
copied from the miner file named in the comment; OURS = the miner's own choice (seen on the old 20 coins), not the trader's.

Causality: a bar on UTC day D reads the daily funding feature of day D-1 and the BTC phase label built from closes of days <= D-1.
The two `bug` switches (phase_table, funding lag) exist only so the committed tests can prove the detectors bite; they are never on
in the real run.
"""
import os
import sys
import datetime as dt
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from MyTradingSys.backtest import fees  # noqa: E402

DAY = 86400000
STEP = 4 * 3600000
NB = 6  # 4h bars per day
DATA_END_MS = int(dt.datetime(2026, 11, 13, 20, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)  # SOURCED miner.py: bars closed by then


def day_num(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


START_DAY = day_num(2020, 1, 1)          # SOURCED miner.py: entries only from here
DEV_END_DAY = day_num(2023, 12, 31)      # DEV: signal bar UTC day <= this
VAL_START_DAY = day_num(2024, 1, 1)      # VAL: signal bar UTC day >= this
HALVINGS = [day_num(2012, 11, 28), day_num(2016, 7, 9), day_num(2020, 5, 11), day_num(2024, 4, 20)]  # OURS (miner)
LATE_AFTER = 540                         # days since halving: >= 540 is the late half (OURS, miner)
PHASES = ["UP_E", "UP_L", "MIX_E", "MIX_L", "DOWN_E", "DOWN_L"]
NONBEAR = (0, 1, 2, 3)                   # UP_E UP_L MIX_E MIX_L: the hypothesis cell
BEAR = (4, 5)                            # DOWN_E DOWN_L: control row only

COST12 = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13   # 12 bp round trip, fees.py
COST6 = COST12 / 2                                       # informational row only

STOP_ATR, MIN_STOP, TARGET_R = 2.5, 0.02, 3.0            # OURS (miner)
HOLD_DAYS = {"T3R": 30, "RIDE": 60}                      # OURS (miner)
KINDS = ("RIDE", "T3R")
NB_THRESH = 0.08                                         # OURS (miner)
FUND_PCT = 0.10                                          # OURS (miner)
SEED = 1114

FRESH = ("NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT "
         "AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN").split()
OLD20 = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI VET ZEC NEO".split()


def lower_priority():
    """Run below normal priority (shared CPU). Silent fallback."""
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        return
    except Exception:
        pass
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


# ------------------------------------------------------------------ indicators (FORMULAS s12)
def atr_sma(h, l, c, n=14):
    """Plain SMA of true range (FORMULAS s12, not Wilder); NaN until n true ranges exist (TR undefined at bar 0)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    tr = np.full(len(c), np.nan)
    tr[1:] = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])
    return pd.Series(tr).rolling(n).mean().to_numpy()


def pct_rank(x, w):
    """Share of the PRIOR w values <= x[t] (excludes the current value); NaN until w prior values exist or when x[t] is NaN.
    STRICT: the result is NaN unless the whole window of w prior values is finite (a NaN inside the window used to count as
    "not <=" while still dividing by w, which made a thin history look like a low rank; fixed, see FIXLOG.md)."""
    x = np.asarray(x, float)
    n = len(x)
    out = np.full(n, np.nan)
    if n <= w:
        return out
    for a in range(w, n, 1500):
        b = min(n, a + 1500)
        win = sliding_window_view(x[a - w:b - 1], w)
        full = np.isfinite(win).all(1)
        r = (win <= x[a:b, None]).mean(1)
        r[~full] = np.nan
        out[a:b] = r
    out[np.isnan(x)] = np.nan
    return out


def shift(a, k):
    """Value k bars ago, NaN for the first k bars."""
    a = np.asarray(a, float)
    out = np.full(len(a), np.nan)
    if k > 0:
        out[k:] = a[:-k]
    else:
        out[:] = a
    return out


# ------------------------------------------------------------------ data loading
def load_bars(path, tf):
    """Spot klines CSV, either layout: wave cache (ts,open,high,low,close,volume,...,taker_buy_base,...) or the miner cache
    (ts,o,h,l,c,v,tbv). Only bars closed by DATA_END_MS, sorted, de-duplicated."""
    df = pd.read_csv(path)
    df = df.rename(columns={"open": "o", "high": "h", "low": "l", "close": "c", "volume": "v", "taker_buy_base": "tbv"})
    df = df.drop_duplicates("ts").sort_values("ts")
    return bars_from_df(df, STEP if tf == "4h" else DAY)


def bars_from_df(df, step):
    df = df[df.ts + step <= DATA_END_MS]
    return {k: df[k].to_numpy(dtype=np.int64 if k == "ts" else float) for k in ("ts", "o", "h", "l", "c", "v", "tbv")}


FUND_SNAP_MS = 60000


def snap_ts(ts):
    """Snap funding print stamps to the nearest whole minute. The cache stamps about half of the prints 1 to 20 ms after the
    settlement instant, the rest exactly on it; without snapping a print AT a bar open is charged or dropped by that jitter alone.
    Minute (not 8h) snapping keeps the real settlement hour of coins that pay every 4h or at shifted hours."""
    ts = np.asarray(ts, np.int64)
    return ((ts + FUND_SNAP_MS // 2) // FUND_SNAP_MS) * FUND_SNAP_MS


def load_funding(path):
    df = pd.read_csv(path).sort_values("ts")
    df = df[df.ts <= DATA_END_MS]
    ts = df.ts.to_numpy(np.int64)
    return snap_ts(ts), df.rate.to_numpy(float)


# ------------------------------------------------------------------ phase labels (causal)
def phase_table(btc_ts, btc_c, bug=False):
    """Six labels = structure (UP / MIX / DOWN from BTC daily close vs SMA200d and its 20d slope) x cycle clock (days since the
    last halving < 540 early, >= 540 late). SOURCED miner.py phase_table. The label computed from the close of day d is KEYED to
    day d+1, so a bar on day D reads only closes <= D-1. bug=True keys it to day d (same-day close: look-ahead)."""
    c = np.asarray(btc_c, float)
    dnum = np.asarray(btc_ts) // DAY
    sma = pd.Series(c).rolling(200).mean().to_numpy()
    slope = sma - shift(sma, 20)
    up = (c > sma) & (slope > 0)
    dn = (c < sma) & (slope < 0)
    st = np.where(up, 0, np.where(dn, 2, 1)).astype(float)
    st[np.isnan(sma) | np.isnan(slope)] = np.nan
    hv = np.array(HALVINGS)
    since = np.array([d - hv[hv <= d].max() if (hv <= d).any() else -1 for d in dnum])
    late = (since >= LATE_AFTER).astype(float)
    lab = st * 2 + late
    keys = dnum if bug else dnum + 1
    return keys, lab


def phase_for_days(table, days):
    """Label for each UTC day number (NaN when the latest key is more than 3 days old or absent)."""
    keys, lab = table
    days = np.asarray(days)
    ix = np.searchsorted(keys, days, side="right") - 1
    ok = ix >= 0
    ixc = np.clip(ix, 0, len(keys) - 1)
    ok &= (days - keys[ixc]) <= 3
    return np.where(ok, lab[ixc], np.nan)


# ------------------------------------------------------------------ signal
def fund_lo_daily(d1_ts, fund_ts, fund_rate):
    """FUND_LO on the daily grid of the coin's 1d bars: 3-day mean of the daily mean funding <= 10th percentile of the prior 90
    daily values (SOURCED miner.py daily_flow). Missing funding or fewer than 90 prior values = False."""
    days = np.asarray(d1_ts) // DAY
    if len(fund_ts) == 0:
        return days, np.zeros(len(days), bool)
    f = pd.Series(np.asarray(fund_rate, float), index=np.asarray(fund_ts) // DAY).groupby(level=0).mean()
    fd = f.reindex(days)
    fd3 = fd.rolling(3, min_periods=3).mean().to_numpy()
    fp = pct_rank(fd3, 90)
    return days, np.asarray(fp <= FUND_PCT, bool)


def bar_features(D, flow, bug=False):
    """BRK5, NB_ABS, FUND_LO on 4h bars (SOURCED miner.py tf_features). Returns brk5, nb_abs, fund_lo, atr. flow = (days, fund_lo)
    from fund_lo_daily. A 4h bar on day D reads the funding feature of the PREVIOUS day unless bug."""
    h, c, v, tbv, ts = (D[k] for k in ("h", "c", "v", "tbv", "ts"))
    sr = pd.Series
    prior_high = sr(h).rolling(5 * NB).max().shift(1).to_numpy()   # prior 5 days of 4h bars, current bar excluded
    brk5 = c > prior_high
    delta = 2 * tbv - v
    with np.errstate(divide="ignore", invalid="ignore"):
        nt = delta / v
    bias = sr(nt).rolling(30 * NB).mean().shift(1).to_numpy()      # prior 30 days, shifted one bar
    deb = delta - bias * v
    with np.errstate(divide="ignore", invalid="ignore"):
        a3 = sr(deb).rolling(3).sum().to_numpy() / sr(v).rolling(3).sum().to_numpy()
    nb_abs = a3 >= NB_THRESH
    fdays, flo = flow
    bar_day = ts // DAY - (0 if bug else 1)
    ix = np.searchsorted(fdays, bar_day)
    ixc = np.clip(ix, 0, len(fdays) - 1)
    ok = (ix < len(fdays)) & (fdays[ixc] == bar_day)
    fund_lo = ok & flo[ixc]
    return np.asarray(brk5, bool), np.asarray(nb_abs, bool), np.asarray(fund_lo, bool), atr_sma(D["h"], D["l"], c, 14)


def onset_mask(sig):
    """Signal on the ONSET bar: true now, false on the coin's previous bar; the first bar is never an onset."""
    sig = np.asarray(sig, bool)
    prev = np.zeros(len(sig), bool)
    prev[1:] = sig[:-1]
    out = sig & ~prev
    if len(out):
        out[0] = False
    return out


# ------------------------------------------------------------------ simulator
def stop_distance(atr, sig, entry):
    """S = max(2.5 x ATR14 at the signal bar, 2% of entry)."""
    return np.maximum(STOP_ATR * atr[sig], MIN_STOP * entry)


def prior_low(l, days):
    """Lowest low of the prior `days` days (bars before the current one)."""
    return pd.Series(l).rolling(days * NB).min().shift(1).to_numpy()


def simulate(o, h, l, c, sig, S, kind, exit_lvl=None):
    """Long trade for every signal bar in `sig` (entry at the open of bar sig+1) with stop distance S (array). Returns dict of
    ret (gross fractional return), fill (exit price), xi (last occupied bar, -1 = unresolved), xt (exit-time bar index: the exit is
    at the open of xt; the funding window closes there), why (1 stop, 2 target, 3 ride signal, 4 time).
    SOURCED miner.py simulate: stop checked from the entry bar; a gap fills at the worse of stop and open; stop wins a same-bar tie
    with the target; T3R target filled at the target, time exit at the close of day 30; RIDE exits at the next open after a close at or
    below the prior-10-day low (exit_lvl), time exit at the close of day 60; a trade not resolved by the data end is unresolved."""
    n = len(c)
    sig = np.asarray(sig, np.int64)
    S = np.asarray(S, float)
    m = len(sig)
    H = HOLD_DAYS[kind] * NB
    e = sig + 1
    entry = o[e]
    stop = entry - S
    tgt = entry + TARGET_R * S
    ret = np.full(m, np.nan)
    fill_px = np.full(m, np.nan)
    xi = np.full(m, -1, np.int64)
    xt = np.full(m, -1, np.int64)
    why = np.zeros(m, np.int8)
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
        fill_s = np.where(oj >= st, st, oj)
        done = hit_s.copy()
        fill = np.zeros(alive.size)
        reason = np.zeros(alive.size, np.int8)
        fill[hit_s] = fill_s[hit_s]
        reason[hit_s] = 1
        if kind == "T3R":
            hit_t = ~hit_s & (hj >= tgt[alive])
            done |= hit_t
            fill[hit_t] = tgt[alive][hit_t]
            reason[hit_t] = 2
        if kind == "RIDE":
            lv = exit_lvl[jj]
            sg = ~done & np.isfinite(lv) & (lv - cj >= 0) & (jj + 1 < n)
            nxt = np.minimum(jj + 1, n - 1)
            done |= sg
            fill[sg] = o[nxt][sg]
            reason[sg] = 3
        if k == H - 1:
            tm = ~done
            done |= tm
            fill[tm] = cj[tm]
            reason[tm] = 4
        if done.any():
            a = alive[done]
            ret[a] = (fill[done] - entry[a]) / entry[a]
            fill_px[a] = fill[done]
            xi[a] = jj[done]
            xt[a] = jj[done] + 1
            why[a] = reason[done]
        rem = ~done
        alive = alive[rem]
    return dict(ret=ret, fill=fill_px, xi=xi, xt=xt, why=why, entry=entry, e=e)


def cum_funding(ts, step, fts, frate):
    """Cumulative funding rate paid per notional at every bar open (n+1 points: the last is the close of the last bar).
    Prints at or before a grid time are included (side='right')."""
    grid = np.append(ts, ts[-1] + step)
    cs = np.concatenate([[0.0], np.cumsum(frate)])
    return grid, cs[np.searchsorted(fts, grid, side="right")]


def funding_paid(cf, e, xt):
    """Funding paid by a LONG: sum of prints after the entry open up to and including the exit open. Longs pay positive prints and
    receive negative ones."""
    return cf[xt] - cf[e]


def net_return(ret, funding, cost=None):
    """Gross return - round-trip cost - funding paid (fraction of notional); cost defaults to the 12 bp of fees.py."""
    return ret - (COST12 if cost is None else cost) - funding


def net_r(ret, funding, risk, cost=None):
    """FORMULAS s13 over the stop distance: (gross return - cost - funding) / (S / entry)."""
    return net_return(ret, funding, cost) / risk


# ------------------------------------------------------------------ per-coin frame
class Coin:
    pass


def build_coin(sym, D4, d1, fund, table, bug_funding=False, step=STEP):
    """One coin's arrays: bars, ATR, onset signal, entry day, phase label at the entry day, entry eligibility, cumulative funding."""
    c = Coin()
    c.sym = sym
    c.ts, c.o, c.h, c.l, c.c = (D4[k] for k in ("ts", "o", "h", "l", "c"))
    n = len(c.c)
    flow = fund_lo_daily(d1["ts"], fund[0], fund[1])
    brk5, nb_abs, fund_lo, atr = bar_features(D4, flow, bug_funding)
    c.brk5, c.nb_abs, c.fund_lo, c.atr = brk5, nb_abs, fund_lo, atr
    c.onset = onset_mask(brk5 & nb_abs & fund_lo)
    c.entry_ts = np.append(c.ts[1:], c.ts[-1] + step)
    c.entry_day = c.entry_ts // DAY
    c.phase = phase_for_days(table, c.entry_day)
    fts, frate = fund
    c.first_fund = fts[0] if len(fts) else np.inf
    c.fund_last = fts[-1] if len(fts) else -1
    c.elig = (c.entry_day >= START_DAY) & (c.entry_ts >= c.first_fund) & ~np.isnan(c.phase)
    c.grid, c.cf = cum_funding(c.ts, step, fts, frate)
    c.exit_lvl = prior_low(c.l, 10)
    c.n = n
    return c


def greedy(idx, xg):
    """Non-overlapping trades: take the first signal, skip signals before its last occupied bar, repeat (idx ascending)."""
    out = []
    nxt = -1
    for i, x in zip(np.asarray(idx).tolist(), np.asarray(xg).tolist()):
        if i >= nxt:
            out.append(i)
            nxt = x
    return np.array(out, dtype=np.int64)


def split_of_signal(sig_ts):
    """DEV / VAL by the UTC day of the SIGNAL bar."""
    d = np.asarray(sig_ts) // DAY
    return np.where(d <= DEV_END_DAY, "DEV", "VAL")


def iso_week(ts_ms):
    y, w, _ = dt.datetime.fromtimestamp(ts_ms / 1000.0, dt.timezone.utc).isocalendar()
    return f"{y}-W{w:02d}"


def utc_str(ts_ms):
    return dt.datetime.fromtimestamp(ts_ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


COLUMNS = ["coin", "kind", "gate", "split", "signal_ts", "signal_utc", "entry_ts", "entry_utc", "entry_price", "stop", "risk",
           "exit_bar_ts", "exit_ts", "exit_price", "exit_reason", "hold_bars", "hold_days", "gross", "cost", "funding", "net_ret",
           "R", "R6", "phase", "brain_label", "brain_cycle", "entry_week", "entry_day", "fund_covered"]
WHY = {1: "STOP", 2: "TARGET", 3: "SIGNAL", 4: "TIME"}


def pick_signals(coin, kind, allowed, window):
    """Resolved, non-overlapping signal bars of one coin for one kind, one window ('DEV'/'VAL') and a phase gate (labels).
    Candidates = onset AND entry-eligible AND phase at the entry day in `allowed` AND ATR defined AND a next bar exists."""
    sig_day = coin.ts // DAY
    wmask = (sig_day <= DEV_END_DAY) if window == "DEV" else (sig_day >= VAL_START_DAY)
    ok = coin.onset & coin.elig & wmask & np.isfinite(coin.atr)
    ok &= np.isin(np.nan_to_num(coin.phase, nan=-1), list(allowed))
    ok[-1] = False
    cand = np.flatnonzero(ok)
    if cand.size == 0:
        return cand, None
    nxt = cand + 1                                       # entry bar = the bar after the signal bar
    entry = coin.o[nxt]
    S = stop_distance(coin.atr, cand, entry)
    sm = simulate(coin.o, coin.h, coin.l, coin.c, cand, S, kind, coin.exit_lvl)
    res = sm["xi"] >= 0
    cand = cand[res]
    if cand.size == 0:
        return cand, None
    sm = {k: v[res] for k, v in sm.items()}
    sm["S"] = S[res]
    chosen = greedy(cand, sm["xi"])                    # bar indices; exit bar = last occupied bar
    keep = np.flatnonzero(np.isin(cand, chosen))
    return cand[keep], {k: v[keep] for k, v in sm.items()}


def make_trades(coin, kind, allowed, gate, brain=None):
    """Trade rows (list of dicts) for one coin, one exit kind, both windows. brain = {date_str: (label, cycle)} descriptive."""
    rows = []
    for window in ("DEV", "VAL"):
        idx, sm = pick_signals(coin, kind, allowed, window)
        for j, s in enumerate(idx.tolist()):
            e, xt = int(sm["e"][j]), int(sm["xt"][j])
            entry, S = float(sm["entry"][j]), float(sm["S"][j])
            risk = S / entry
            gross = float(sm["ret"][j])
            fund = float(funding_paid(coin.cf, e, xt))
            net = net_return(gross, fund)
            exit_ts = int(coin.grid[xt])
            eday = int(coin.entry_day[s])
            bl, bc = ("", "")
            if brain is not None:
                bl, bc = brain.get(utc_str(eday * DAY)[:10], ("", ""))
            rows.append(dict(
                coin=coin.sym, kind=kind, gate=gate, split=window, signal_ts=int(coin.ts[s]), signal_utc=utc_str(int(coin.ts[s])),
                entry_ts=int(coin.ts[e]), entry_utc=utc_str(int(coin.ts[e])), entry_price=entry, stop=entry - S, risk=risk,
                exit_bar_ts=int(coin.ts[int(sm["xi"][j])]), exit_ts=exit_ts, exit_price=float(sm["fill"][j]),
                exit_reason=WHY[int(sm["why"][j])], hold_bars=xt - e, hold_days=(xt - e) / NB, gross=gross, cost=COST12,
                funding=fund, net_ret=net, R=net / risk, R6=net_r(gross, fund, risk, COST6),
                phase=PHASES[int(coin.phase[s])], brain_label=bl, brain_cycle=bc,
                entry_week=iso_week(int(coin.ts[e])), entry_day=eday,
                fund_covered=bool(exit_ts <= coin.fund_last + 8 * 3600000)))
    return rows
