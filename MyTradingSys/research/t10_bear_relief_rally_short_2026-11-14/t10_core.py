"""T10 core: BEAR-phase relief-rally SHORT on 1d bars. Signal, simulator, funding, smoothing, process helpers.
PRE_REG.md next to this file is the law. Pure functions on numpy arrays; loaders at the bottom.
ATR is Wilder per MyTradingSys/backtest/layers/FORMULAS.md (TR0 uses its own close as previous close; seed = simple
mean of the first 14 TR). Fee comes from fees.py (no private cost constants).
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
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13      # round trip, fraction of price (12 bp)
RALLY_MULT = 1.12            # OURS
RALLY_LOOKBACK = 10          # OURS
RESCUE_MULT = 1.08           # OURS, descriptive rescue row only
SMA_COIN_SLOW = 50           # OURS
SMA_COIN_FAST = 20           # OURS
DOWN_SLOPE_LAG = 10          # OURS
BTC_SMA = 200                # SOURCED idea (BIBLE s5), use OURS
ATR_N = 14                   # SOURCED period (Wilder)
STOP_ATR_MULT = 0.5          # OURS
STOP_HH_BARS = 5             # OURS
STOP_FLOOR = 0.05            # OURS
HOLD_BARS = 10               # OURS (entry bar + 9 more; time exit at that bar's close)
COOLDOWN = 10                # OURS
MIN_HISTORY = 260            # SOURCED shared rules
MIN_ALIVE = 30               # SOURCED shared rules
ENDED_GAP_DAYS = 30          # OURS
SMOOTH_DAYS = 10             # OURS (shared rules)
EPISODE_GAP_DAYS = 14        # SOURCED spec
PLACEBO_WINDOW_DAYS = 56     # +/- 8 ISO weeks, SOURCED shared rules


def _eday(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


HOLES = {"LUNA": (_eday(2022, 5, 13), _eday(2022, 5, 31)), "FTT": (_eday(2022, 11, 15), _eday(2023, 9, 22))}
DEV_LAST_DAY = _eday(2023, 12, 31)      # signal day <= this = DEV


def split_of_day(day):
    return "DEV" if day <= DEV_LAST_DAY else "VAL"


def day_str(day):
    return (dt.date(1970, 1, 1) + dt.timedelta(days=int(day))).strftime("%Y-%m-%d")


def iso_week_of_day(day):
    d = (dt.date(1970, 1, 1) + dt.timedelta(days=int(day))).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


# ---------------------------------------------------------------- indicators
def sma(x, n):
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def prior_min(x, n):
    """out[i] = min(x[i-n .. i-1]); nan for i < n. Never includes bar i."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def trailing_max(x, n):
    """out[i] = max(x[i-n+1 .. i]) (includes bar i); nan for i < n-1."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].max()
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


# ---------------------------------------------------------------- coin runs
class Run:
    """A contiguous stretch of daily bars of one coin (no missing day inside)."""

    def __init__(self, name, a, is_last, pull_ms, idx):
        self.name, self.idx = name, idx
        self.ms, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(self.ms)
        self.day = (self.ms // DAY).astype(np.int64)
        self.ended = bool(is_last and self.ms[-1] < pull_ms - ENDED_GAP_DAYS * DAY)
        self.is_last = is_last
        self.sma20 = sma(self.c, SMA_COIN_FAST)
        self.sma50 = sma(self.c, SMA_COIN_SLOW)
        self.atr = wilder_atr(self.h, self.l, self.c) if self.n >= ATR_N else np.full(self.n, np.nan)
        self.low10 = prior_min(self.c, RALLY_LOOKBACK)
        self.hh5 = trailing_max(self.h, STOP_HH_BARS)
        lag = np.full(self.n, np.nan)
        if self.n > DOWN_SLOPE_LAG:
            lag[DOWN_SLOPE_LAG:] = self.sma50[:-DOWN_SLOPE_LAG]
        with np.errstate(invalid="ignore"):
            self.down = (self.c < self.sma50) & (self.sma50 < lag)
            self.rej = (self.h >= self.sma20) & (self.c < self.o) & (self.c < np.r_[np.nan, self.l[:-1]])
            self.rally12 = self.c >= RALLY_MULT * self.low10
            self.rally8 = self.c >= RESCUE_MULT * self.low10
        self.alive = np.zeros(self.n, bool)
        self.alive[MIN_HISTORY - 1:] = True


def make_runs(name, rows, pull_ms):
    a = np.asarray(rows, float)
    a = a[np.argsort(a[:, 0])]
    a = a[np.r_[True, np.diff(a[:, 0]) > 0]]
    t = (a[:, 0] // DAY).astype(np.int64)
    br = np.r_[0, np.where(np.diff(t) != 1)[0] + 1, len(t)]
    runs = []
    for k in range(len(br) - 1):
        runs.append(Run(name, a[br[k]:br[k + 1]], k == len(br) - 2, pull_ms, k))
    return runs


def btc_gate(rows):
    """dict epoch-day -> True when BTC close (that day) < SMA200 of closes through that day. Contiguous BTC assumed
    inside each run; a run shorter than 200 bars gives no gate day."""
    g = {}
    for r in make_runs("BTC", rows, 0):
        s = sma(r.c, BTC_SMA)
        for i in range(BTC_SMA - 1, r.n):
            g[int(r.day[i])] = bool(r.c[i] < s[i])
    return g


def alive_counts(all_runs):
    cnt = {}
    for r in all_runs:
        for i in range(MIN_HISTORY - 1, r.n):
            d = int(r.day[i])
            cnt[d] = cnt.get(d, 0) + 1
    return cnt


# ---------------------------------------------------------------- signal
def signal_mask(run, gate, alive_n, rally="12"):
    """Boolean arrays over run bars, all computed from bars through t: (cond_all, cond_screened_out_by_alive)."""
    ral = run.rally12 if rally == "12" else run.rally8
    base = np.zeros(run.n, bool)
    for i in range(MIN_HISTORY - 1, run.n):
        base[i] = gate.get(int(run.day[i]), False)
    raw = base & run.alive & run.down & ral & run.rej
    many = np.array([alive_n.get(int(d), 0) >= MIN_ALIVE for d in run.day])
    return raw, raw & many


def flagged_mask(run, gate, alive_n):
    """Placebo / baseline flag: BTC gate true, coin downtrend true, alive, >= 30 coins alive. No rally condition."""
    base = np.zeros(run.n, bool)
    for i in range(MIN_HISTORY - 1, run.n):
        base[i] = gate.get(int(run.day[i]), False) and alive_n.get(int(run.day[i]), 0) >= MIN_ALIVE
    return base & run.alive & run.down


def scan_signals(run, gate, alive_n, rally="12"):
    """Signals after the per-coin cooldown. Returns (accepted list of t, counts dict)."""
    raw, ok = signal_mask(run, gate, alive_n, rally)
    acc, last, blocked = [], -10 ** 9, 0
    for t in np.where(ok)[0]:
        if t - last >= COOLDOWN:
            acc.append(int(t))
            last = int(t)
        else:
            blocked += 1
    return acc, dict(raw=int(raw.sum()), alive_excluded=int(raw.sum() - ok.sum()), cooldown_blocked=blocked,
                     accepted=len(acc))


# ---------------------------------------------------------------- simulator
def sim_short(run, e, stop_px, target_px, xd):
    """Short entered at the open of bar e. Bars e..xd checked in order. Stop wins ties; a bar that opens at or above
    the stop (after the entry bar) fills at the open; the target fills at the target price (no gap bonus).
    Returns (exit_index, exit_px, reason)."""
    for i in range(e, xd + 1):
        if i > e and run.o[i] >= stop_px:
            return i, float(run.o[i]), "STOP-GAP"
        if run.h[i] >= stop_px:
            return i, float(stop_px), "STOP"
        if run.l[i] <= target_px:
            return i, float(target_px), "TARGET"
    return xd, float(run.c[xd]), "TIME"


def window_end(run, e):
    """-> (xd, ended_flag) or (None, reason) when the 10-bar window is not complete and the coin still trades."""
    xd = e + HOLD_BARS - 1
    if xd < run.n:
        return xd, False
    if run.is_last and run.ended:
        return run.n - 1, True
    return None, "INCOMPLETE-WINDOW"


def hole_hit(name, d_from, d_to):
    h = HOLES.get(name)
    return bool(h and d_from <= h[1] and d_to >= h[0])


class Funding:
    """Funding prints (ts ms, rate). Window rule: entry_ms < print <= end_ms. A short RECEIVES positive rates."""

    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts)
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]

    def income_short(self, entry_ms, end_ms):
        """-> fraction of entry notional earned by the short, or NaN when the cache does not cover the window."""
        if len(self.ts) == 0 or self.ts[0] > entry_ms or self.ts[-1] < end_ms:
            return float("nan")
        lo = int(np.searchsorted(self.ts, entry_ms, side="right"))
        hi = int(np.searchsorted(self.ts, end_ms, side="right"))
        return float(self.cum[hi] - self.cum[lo])


def entry_screen(run, t):
    """Outcome-free feasibility screen of a signal. -> (None, (e, xd, ended, entry, stop_px, target_px)) or (reason, None)."""
    e = t + 1
    if e >= run.n:
        return "NO-ENTRY-BAR", None
    entry = float(run.o[e])
    xd, ended = window_end(run, e)
    if xd is None:
        return ended, None
    if hole_hit(run.name, int(run.day[t]), int(run.day[xd])):
        return "HOLE", None
    atr = run.atr[t]
    if not (atr == atr) or not (run.hh5[t] == run.hh5[t]) or not (run.low10[t] == run.low10[t]):
        return "NO-INDICATOR", None
    stop_px = max(float(run.hh5[t] + STOP_ATR_MULT * atr), entry * (1 + STOP_FLOOR))
    target_px = float(run.low10[t])
    if target_px >= entry:
        return "TARGET-NOT-BELOW-ENTRY", None
    return None, (e, xd, ended, entry, stop_px, target_px)


def make_trade(run, t, fund=None, rally_tag="12"):
    """One short trade from the signal on bar t (entry = open of bar t+1). Returns (row, None) or (None, skip_reason)."""
    why0, info = entry_screen(run, t)
    if why0:
        return None, why0
    e, xd, ended, entry, stop_px, target_px = info
    stop_pct = stop_px / entry - 1.0
    tgt_pct = 1.0 - target_px / entry
    xi, xpx, why = sim_short(run, e, stop_px, target_px, xd)
    if why == "TIME" and ended:
        why = "ENDED"
    gross = (entry - xpx) / entry
    net = gross - FEE_RT
    end_ms = int(run.ms[xi]) + DAY
    fin = fund.income_short(int(run.ms[e]), end_ms) if fund is not None else float("nan")
    row = dict(coin=run.name, run=run.idx, t=int(t), signal_day=int(run.day[t]), entry_day=int(run.day[e]),
               exit_day=int(run.day[xi]), entry_px=entry, exit_px=xpx, stop_px=stop_px, target_px=target_px,
               stop_pct=stop_pct, tgt_pct=tgt_pct, exit_reason=why, hold_days=int(xi - e + 1),
               gross=gross, fee=FEE_RT, net=net,
               gross_R=gross / stop_pct, fee_R=FEE_RT / stop_pct, net_R=net / stop_pct,
               fund=fin, fund_R=(fin / stop_pct) if fin == fin else float("nan"),
               total_R=(net + (fin if fin == fin else 0.0)) / stop_pct,
               fund_rule="REAL" if fin == fin else "NOT_IN_DATA",
               split=split_of_day(int(run.day[t])), iso_week=iso_week_of_day(int(run.day[e])), rally=rally_tag)
    return row, None


def placebo_outcome_R(run, tc, stop_pct, tgt_pct):
    """Price-only fee-net R of a short entered at the open of bar tc+1 with the REAL trade's stop % and target % and the
    10-bar cap. None when the window is incomplete. No funding (price-only comparison)."""
    e = tc + 1
    if e >= run.n:
        return None
    xd, ended = window_end(run, e)
    if xd is None:
        return None
    entry = float(run.o[e])
    xi, xpx, why = sim_short(run, e, entry * (1 + stop_pct), entry * (1 - tgt_pct), xd)
    return ((entry - xpx) / entry - FEE_RT) / stop_pct


# ---------------------------------------------------------------- cycle smoothing, episodes
def smooth_cycle(raw):
    """raw: list of (key, state) in time order. A new state is adopted only after SMOOTH_DAYS consecutive days of it; until
    then the prior state holds. The adoption day is the SMOOTH_DAYS-th day. Returns {key: smoothed state}."""
    out, cur, cand, k = {}, None, None, 0
    for key, s in raw:
        if cur is None:
            cur = s
        elif s == cur:
            cand, k = None, 0
        else:
            if s == cand:
                k += 1
            else:
                cand, k = s, 1
            if k >= SMOOTH_DAYS:
                cur, cand, k = s, None, 0
        out[key] = cur
    return out


def episodes(entry_days):
    """Chain entry days (all coins) into episodes: a gap of more than EPISODE_GAP_DAYS starts a new one. Returns a list
    of episode ids aligned with the INPUT order."""
    order = sorted(range(len(entry_days)), key=lambda i: entry_days[i])
    ids, ep, prev = [0] * len(entry_days), -1, None
    for i in order:
        if prev is None or entry_days[i] - prev > EPISODE_GAP_DAYS:
            ep += 1
        ids[i] = ep
        prev = entry_days[i]
    return ids


# ---------------------------------------------------------------- process helpers
def lower_priority():
    """BelowNormal priority. psutil if installed, else ctypes SetPriorityClass 0x4000. Prints the resulting class once."""
    cls = None
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        cls = "psutil nice=%s" % psutil.Process().nice()
    except Exception:
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
            cls = "ctypes GetPriorityClass=0x%X (0x4000 = BELOW_NORMAL)" % k.GetPriorityClass(h)
        except Exception as ex:   # pragma: no cover
            cls = "FAILED to set priority: %r" % (ex,)
    print("priority:", cls)
    return cls


def slot_acquire(slot_id, root=r"F:/MTS/data_cache/wave3-1114/_slots", max_locks=4, max_age_s=1800, wait_s=30):
    import time
    p = pathlib.Path(root)
    p.mkdir(parents=True, exist_ok=True)
    while True:
        live = [f for f in p.glob("*.lock") if time.time() - f.stat().st_mtime < max_age_s]
        if len(live) < max_locks:
            break
        time.sleep(wait_s)
    lk = p / (slot_id + ".lock")
    lk.write_text(str(time.time()))
    return lk


def slot_release(lk):
    try:
        pathlib.Path(lk).unlink()
    except OSError:
        pass


# ---------------------------------------------------------------- loaders (runners only; tests never touch the cache)
def load_rows(path):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4))
    return np.atleast_2d(a)


def load_funding(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    a = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1)))
    return Funding(a[:, 0], a[:, 1]) if a.size else None
