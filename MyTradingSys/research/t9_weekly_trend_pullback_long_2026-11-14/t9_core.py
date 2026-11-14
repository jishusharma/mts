"""T9 core: weekly-trend pullback long. Signal, simulator, cost model. See PRE_REG.md (frozen, the law).

Pure functions on numpy arrays; no data-cache access except the explicit loaders at the bottom.
EMA and ATR per MyTradingSys/backtest/layers/FORMULAS.md (SMA-seeded EMA, alpha 2/(N+1); Wilder ATR, TR0 uses its own close).
Cost constants come from fees.py only.
"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
_BT = pathlib.Path(__file__).resolve().parents[2] / "backtest"
sys.path.insert(0, str(_BT))
import fees  # noqa: E402

DAY = 86400000
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13     # round trip, fraction of price
EMA_FAST, EMA_SLOW, SLOPE_WEEKS = 21, 55, 4
STOP_ATR_MULT = 0.5                                        # OURS
STOP_FLOOR = 0.015                                         # SOURCED design shared rules
ATR_N = 14
COOLDOWN_DAYS = 56
CAP_WEEKS = 12                                             # 84 days
DD_FACTOR, DD_LOOKBACK = 0.80, 8                           # T6 exclusion
SMOOTH_DAYS = 10
MIN_ALIVE_COINS = 30
ALIVE_DAYS = 260
ENDED_GAP_DAYS = 30
FLAT_PER_SLOT = 1.0 / 10000.0                              # sensitivity row only
PULL_MS = int(dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)
DEV_END_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
FIRST_FLAG_WEEK = EMA_SLOW - 1 + SLOPE_WEEKS               # index 58


def set_low_priority():
    """BelowNormal priority; psutil first, ctypes fallback. Returns the resulting class id (0x4000 = BELOW_NORMAL) or None."""
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentProcess.restype = wintypes.HANDLE
        k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k.GetPriorityClass.restype = wintypes.DWORD
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x4000)
        return int(k.GetPriorityClass(h))
    except Exception:
        return None


def ema(x, n):
    """FORMULAS.md section 4: seed = SMA of first n values at index n-1, then (x - e) * 2/(n+1) + e. NaN before."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = (x[i] - out[i - 1]) * a + out[i - 1]
    return out


def wilder_atr(h, l, c, n=ATR_N):
    m = len(c)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = np.full(m, np.nan)
    if m >= n:
        atr[n - 1] = tr[:n].mean()
        for i in range(n, m):
            atr[i] = (atr[i - 1] * (n - 1) + tr[i]) / n
    return atr


class Coin:
    """rows: [ts_ms, open, high, low, close] daily. Longest contiguous run from its first Monday; whole weeks for the
    weekly view; full daily arrays kept so exits can run into a trailing partial week."""

    def __init__(self, name, rows, pull_ms=PULL_MS):
        a = np.asarray(rows, float)
        a = a[np.argsort(a[:, 0])]
        t = (a[:, 0] // DAY).astype(np.int64)
        br = np.r_[0, np.where(np.diff(t) != 1)[0] + 1, len(t)]
        i = int(np.argmax(np.diff(br)))
        lo, hi = int(br[i]), int(br[i + 1])
        self.dropped_rows = int(len(t) - (hi - lo))
        a, t = a[lo:hi], t[lo:hi]
        mon = (t + 3) % 7 == 0                      # epoch day 0 is a Thursday
        if mon.any():
            f = int(np.argmax(mon))
            a, t = a[f:], t[f:]
        else:
            a, t = a[:0], t[:0]
        self.name = name
        self.ms, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(self.ms)
        self.nw = self.n // 7
        k = 7 * self.nw
        self.wc = self.c[6:k:7] if self.nw else np.array([])
        self.wh = self.h[:k].reshape(self.nw, 7).max(1) if self.nw else np.array([])
        self.wl = self.l[:k].reshape(self.nw, 7).min(1) if self.nw else np.array([])
        self.e21 = ema(self.wc, EMA_FAST)
        self.e55 = ema(self.wc, EMA_SLOW)
        self.atr = wilder_atr(self.h, self.l, self.c) if self.n >= ATR_N else np.full(self.n, np.nan)
        self.ended = bool(self.n == 0 or self.ms[-1] < pull_ms - ENDED_GAP_DAYS * DAY)
        self.flag = np.zeros(self.nw, bool)
        self.touch = np.zeros(self.nw, bool)
        self.dd20 = np.zeros(self.nw, bool)
        for w in range(self.nw):
            if w >= FIRST_FLAG_WEEK:
                self.flag[w] = bool(self.e21[w] > self.e55[w] and self.e55[w] > self.e55[w - SLOPE_WEEKS]
                                    and self.wc[w] > self.e55[w])
                self.touch[w] = bool(self.wl[w] <= self.e21[w] and self.wc[w] >= self.e21[w])
            if w >= DD_LOOKBACK:
                self.dd20[w] = bool(self.wc[w] <= DD_FACTOR * self.wc[w - DD_LOOKBACK:w].max())


def iso_week_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def day_str(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d")


def split_of_signal(signal_ms):
    """Split by SIGNAL bar (the Sunday daily bar of the completed week)."""
    return "DEV" if signal_ms < DEV_END_MS else "VAL"


# ---------------- BTC smoothed cycle ----------------
def smooth_cycle(dates, raw, hold=SMOOTH_DAYS):
    """Causal smoothing: a new raw state counts only after `hold` consecutive days; until then the prior state holds.
    First state = first non-empty raw state. Returns {date: state}."""
    out, cur, cand, run = {}, None, None, 0
    for d, r in zip(dates, raw):
        if not r:
            out[d] = cur
            continue
        if cur is None:
            cur = r
            cand, run = None, 0
        elif r == cur:
            cand, run = None, 0
        else:
            if r == cand:
                run += 1
            else:
                cand, run = r, 1
            if run >= hold:
                cur, cand, run = r, None, 0
        out[d] = cur
    return out


# ---------------- signals ----------------
def signals(coin, state_by_day, gate=("BULL", "BASE")):
    """One dict per signal (no outcomes). Signal on completed week w; entry at the Monday open d0 = 7*(w+1).
    state_by_day: {'YYYY-MM-DD': smoothed BTC state} read on the entry day."""
    out, last_entry = [], None
    for w in range(FIRST_FLAG_WEEK, coin.nw):
        d0 = 7 * (w + 1)
        if d0 >= coin.n:
            break
        if not (coin.flag[w] and coin.touch[w]) or coin.dd20[w]:
            continue
        entry_ms = int(coin.ms[d0])
        st = state_by_day.get(day_str(entry_ms))
        if st not in gate:
            continue
        if last_entry is not None and entry_ms < last_entry + COOLDOWN_DAYS * DAY:
            continue
        entry = float(coin.o[d0])
        atr = float(coin.atr[d0 - 1])
        if not (atr == atr) or entry <= 0:
            continue
        stop = min(float(coin.wl[w]) - STOP_ATR_MULT * atr, entry * (1 - STOP_FLOOR))
        if stop <= 0:
            continue
        last_entry = entry_ms
        out.append(dict(coin=coin.name, w=w, d0=d0, entry_ms=entry_ms, signal_ms=int(coin.ms[d0 - 1]),
                        entry=entry, stop=stop, risk=(entry - stop) / entry, btc_state=st,
                        split=split_of_signal(int(coin.ms[d0 - 1])), iso_week=iso_week_of(entry_ms)))
    return out


# ---------------- funding ----------------
class Funding:
    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts)
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]


def funding_cost(fund, entry_ms, end_ms):
    """-> (cost paid by the long as fraction of entry notional, covered). Not covered: 0.0, False (NOT_IN_DATA)."""
    if fund is None or len(fund.ts) == 0 or fund.ts[0] > entry_ms or fund.ts[-1] < end_ms:
        return 0.0, False
    lo = int(np.searchsorted(fund.ts, entry_ms, side="right"))
    hi = int(np.searchsorted(fund.ts, end_ms, side="right"))
    return float(fund.cum[hi] - fund.cum[lo]), True


# ---------------- simulator ----------------
def simulate(coin, d0, risk, fund=None):
    """Long entered at the open of daily bar d0 with stop = entry*(1-risk). Exit order each day: stop (low <= stop, stop wins
    ties; gap open <= stop fills at the open); at week end a completed weekly close < EMA55w exits at the next Monday open;
    cap: Monday open d0+84. Returns dict or None (unresolved on a coin that still trades / bad input)."""
    if d0 < 1 or d0 >= coin.n or not (risk > 0):
        return None
    entry = float(coin.o[d0])
    stop = entry * (1 - risk)
    ex_i, ex_px, why = None, None, None
    ended_exit = False
    last_week_start = d0 + 7 * CAP_WEEKS
    k = 0
    while True:
        ws = d0 + 7 * k                      # Monday index of trade week k
        we = ws + 6
        for d in range(ws, min(we, coin.n - 1) + 1):
            if coin.l[d] <= stop:
                gap = coin.o[d] <= stop
                ex_i, ex_px, why = d, float(coin.o[d] if gap else stop), "STOP-GAP" if gap else "STOP"
                break
        if ex_i is not None:
            break
        if we >= coin.n:                      # week not complete in the data: unresolved
            break
        nxt = we + 1                          # next Monday open
        wk = we // 7                          # weekly index of the completed week (coin weeks start at d=0 Monday)
        trend_out = wk < coin.nw and coin.wc[wk] < coin.e55[wk]
        if trend_out or nxt >= last_week_start:
            if nxt >= coin.n:
                break                         # exit open not in data
            ex_i, ex_px, why = nxt, float(coin.o[nxt]), "TREND" if trend_out else "CAP"
            break
        k += 1
    if ex_i is None:
        if not coin.ended:
            return None
        ex_i, ex_px, why, ended_exit = coin.n - 1, float(coin.c[coin.n - 1]), "ENDED", True
    entry_ms = int(coin.ms[d0])
    exit_ms = int(coin.ms[ex_i])
    # funding window: entry open < print <= exit instant (open of exit bar for open exits, end of bar for stop / ended)
    end_ms = exit_ms + (DAY if why in ("STOP", "STOP-GAP", "ENDED") else 0)
    if why == "STOP-GAP":
        end_ms = exit_ms
    fcost, covered = funding_cost(fund, entry_ms, end_ms)
    gross = ex_px / entry - 1.0
    net = gross - FEE_RT - fcost
    flat = fcost if covered else ((end_ms - entry_ms) // (DAY // 3)) * FLAT_PER_SLOT
    return dict(entry_i=d0, exit_i=ex_i, entry_ts=entry_ms, exit_ts=exit_ms, entry_px=entry, exit_px=ex_px, stop=stop,
                risk=risk, exit_reason=why, ended=ended_exit, days=(end_ms - entry_ms) / DAY, gross=gross, fee=FEE_RT, funding=fcost, funding_covered=covered,
                net=net, net_flat=gross - FEE_RT - flat, gross_R=gross / risk, fee_R=FEE_RT / risk, net_R=net / risk,
                net_flat_R=(gross - FEE_RT - flat) / risk)


def trade_from_signal(coin, sig, fund=None):
    t = simulate(coin, sig["d0"], sig["risk"], fund)
    if t is None:
        return None
    t.update(coin=coin.name, signal_ms=sig["signal_ms"], btc_state=sig["btc_state"], split=sig["split"],
             iso_week=sig["iso_week"], w=sig["w"])
    return t


def candidate_mondays(coin, state_by_day, gate=("BULL", "BASE")):
    """Every Monday entry whose preceding completed week has the coin flag true and DD20 false and BTC gate true:
    the like-for-like placebo pool (touch trigger removed). -> list of dict(d0, entry_ms, signal_ms, split, btc_state)."""
    out = []
    for w in range(FIRST_FLAG_WEEK, coin.nw):
        d0 = 7 * (w + 1)
        if d0 >= coin.n:
            break
        if not coin.flag[w] or coin.dd20[w]:
            continue
        ms = int(coin.ms[d0])
        st = state_by_day.get(day_str(ms))
        if st not in gate:
            continue
        out.append(dict(d0=d0, entry_ms=ms, signal_ms=int(coin.ms[d0 - 1]), split=split_of_signal(int(coin.ms[d0 - 1])),
                        btc_state=st, w=w, iso_week=iso_week_of(ms)))
    return out


# ---------------- loaders (tests never call these) ----------------
def load_coin(path, name):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4))
    return Coin(name, np.atleast_2d(a))


def load_funding(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    a = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1)))
    return Funding(a[:, 0], a[:, 1]) if a.size else None


def load_btc_state(path):
    import csv
    dates, raw = [], []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            dates.append(r["date"])
            raw.append(r.get("cycle") or "")
    return smooth_cycle(dates, raw)


def universe(wave2, miner):
    """Union of the two spot_1d folders. -> {coin: (spot_path, funding_path)}; wave2 wins when a coin is in both."""
    out = {}
    for root in (pathlib.Path(wave2), pathlib.Path(miner)):
        sp = root / "spot_1d"
        if not sp.exists():
            continue
        for p in sorted(sp.glob("*USDT.csv")):
            name = p.name[:-8]
            if name not in out:
                out[name] = (p, root / "funding" / p.name)
    return out


# ---------------- heavy-job slots ----------------
SLOT_DIR = "F:/MTS/data_cache/wave3-1114/_slots"


def acquire_slot(job_id, max_locks=4, max_age_s=1800, sleep_s=30):
    import os
    import time
    os.makedirs(SLOT_DIR, exist_ok=True)
    while True:
        now = time.time()
        live = [f for f in os.listdir(SLOT_DIR) if f.endswith(".lock")
                and now - os.path.getmtime(os.path.join(SLOT_DIR, f)) < max_age_s and f != job_id + ".lock"]
        if len(live) < max_locks:
            break
        time.sleep(sleep_s)
    path = os.path.join(SLOT_DIR, job_id + ".lock")
    open(path, "w").write(str(os.getpid()))
    return path


def release_slot(path):
    import os
    try:
        os.remove(path)
    except OSError:
        pass
