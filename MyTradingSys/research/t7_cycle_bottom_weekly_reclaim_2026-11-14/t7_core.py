"""T7 core: cycle-bottom long (coin deep drawdown + weekly SMA10 reclaim). PRE_REG.md is the law.

Pure functions on numpy arrays; loaders and the priority/slot helpers are the only side effects.
ATR: Wilder per MyTradingSys/backtest/layers/FORMULAS.md (TR0 uses its own close as previous close, seeded by the
simple mean of the first 14 TR).
"""
import sys
import os
import time
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
_BT = pathlib.Path(__file__).resolve().parents[2] / "backtest"
sys.path.insert(0, str(_BT))
import fees  # noqa: E402  SOURCED constants

DAY = 86400000
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13      # round trip fraction of price (12 bp)
DD_FACTOR = 0.45          # OURS
DD_WINDOW = 730           # OURS
MIN_ALIVE = 365           # SOURCED design (shared rules, T7 override of 260)
SMA_W = 10                # OURS
COOLDOWN_DAYS = 28        # OURS
HOLD_DAYS = 28            # OURS: 28 daily bars in market, exit at close of entry_day + 27
ATR_N = 14                # SOURCED Wilder
STOP_ATR_MULT = 3.0       # OURS
STOP_FLOOR = 0.10         # OURS
MIN_STOP = 0.015          # SOURCED shared rules (stop >= 1.5%)
ENDED_GAP_DAYS = 30       # OURS
MIN_ALIVE_COINS = 30      # SOURCED shared rules
SMOOTH_DAYS = 10          # OURS
DEV_END_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)  # signal bar < this = DEV
PULL_MS = int(dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)
SLOT_DIR = "F:/MTS/data_cache/wave3-1114/_slots"


# ---------------------------------------------------------------- priority and slots
def set_below_normal():
    """BelowNormal priority; psutil if present, else ctypes SetPriorityClass 0x4000. Returns a proof string."""
    how = "none"
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        how = "psutil"
    except Exception:
        pass
    cls = None
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentProcess.restype = wintypes.HANDLE
        k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k.GetPriorityClass.restype = wintypes.DWORD
        h = k.GetCurrentProcess()
        if how == "none":
            k.SetPriorityClass(h, 0x4000)
            how = "ctypes"
        cls = hex(k.GetPriorityClass(h))
    except Exception:
        pass
    return "priority via %s, class %s (0x4000 = BELOW_NORMAL)" % (how, cls)


def acquire_slot(name, slot_dir=SLOT_DIR, maxn=4, stale_s=1800):
    p = pathlib.Path(slot_dir)
    p.mkdir(parents=True, exist_ok=True)
    while True:
        now = time.time()
        live = [f for f in p.glob("*.lock") if now - f.stat().st_mtime < stale_s]
        if len(live) < maxn:
            break
        time.sleep(30)
    lk = p / (name + ".lock")
    lk.write_text(str(os.getpid()))
    return lk


def release_slot(lk):
    try:
        pathlib.Path(lk).unlink()
    except OSError:
        pass


# ---------------------------------------------------------------- indicators
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


def iso_week_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def date_of(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d")


def week_index(ms):
    """Monday-aligned week number (epoch day 0 is a Thursday)."""
    return int((ms // DAY + 3) // 7)


def split_of(signal_ms):
    return "DEV" if signal_ms < DEV_END_MS else "VAL"


# ---------------------------------------------------------------- data segments
class Seg:
    """One contiguous run of daily bars of one coin (history resets at any gap, so the LUNA/FTT holes are never spanned).
    rows: [ts_ms, open, high, low, close]. Full ISO weeks (Monday..Sunday) only are used as weekly bars.
    `final` = this is the last segment of the coin file; `ended` = the segment stops (gap follows, or the data ends more
    than 30 days before the pull)."""

    def __init__(self, name, rows, final=True, pull_ms=PULL_MS, seg_id=0):
        a = np.asarray(rows, float)
        a = a[np.argsort(a[:, 0])]
        self.name, self.seg_id = name, seg_id
        self.ms, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(self.ms)
        self.atr = wilder_atr(self.h, self.l, self.c) if self.n >= ATR_N else np.full(self.n, np.nan)
        self.ended = bool((not final) or self.n == 0 or self.ms[-1] < pull_ms - ENDED_GAP_DAYS * DAY)
        day = (self.ms // DAY).astype(np.int64)
        mon = np.where((day + 3) % 7 == 0)[0]
        self.wstart = np.array([i for i in mon if i + 6 < self.n], dtype=int)   # full weeks only
        self.wclose_idx = self.wstart + 6                                        # Sunday index
        self.wc = self.c[self.wclose_idx] if len(self.wstart) else np.array([])

    def alive_at(self, s):
        """History rule: at least MIN_ALIVE daily bars through index s inclusive."""
        return s + 1 >= MIN_ALIVE

    def dd_state(self, s, wc_k):
        """Coin in DD at completed weekly bar ending at index s: weekly close <= 0.45 x max daily close of the prior
        730 days (window = available history, >= 365 bars)."""
        lo = max(0, s - DD_WINDOW + 1)
        return bool(self.alive_at(s) and wc_k <= DD_FACTOR * self.c[lo:s + 1].max())

    def dd_weeks(self):
        """All completed weekly bars in DD state (flag only, no cross). -> list of (k, s, d0)."""
        out = []
        for k, s in enumerate(self.wclose_idx):
            if s + 1 < self.n and self.dd_state(int(s), self.wc[k]):
                out.append((k, int(s), int(s) + 1))
        return out

    def alive_sundays(self):
        return [int(self.ms[s]) for s in self.wclose_idx if self.alive_at(int(s))]


def sma(a, k, w):
    return float(np.mean(a[k - w + 1:k + 1]))


def events(seg):
    """Reclaim signals known at the Sunday close of week k; entry d0 = the next Monday. Only data through index s is used.
    weekly close > SMA10, previous weekly close <= previous SMA10, coin in DD state. Cooldown 28 days per coin
    (clock moves only when an event with an entry bar fires)."""
    out, last_entry = [], None
    for k in range(SMA_W, len(seg.wc)):
        s = int(seg.wclose_idx[k])
        d0 = s + 1
        if d0 >= seg.n:
            break
        if not seg.alive_at(s):
            continue
        if not (seg.wc[k] > sma(seg.wc, k, SMA_W) and seg.wc[k - 1] <= sma(seg.wc, k - 1, SMA_W)):
            continue
        if not seg.dd_state(s, seg.wc[k]):
            continue
        if last_entry is not None and (seg.ms[d0] - last_entry) < COOLDOWN_DAYS * DAY:
            continue
        last_entry = seg.ms[d0]
        out.append(dict(k=k, s=s, d0=d0))
    return out


# ---------------------------------------------------------------- funding
class Funding:
    """Funding prints (ts ms, rate). Window: entry_ms < print <= end_ms; prints rounded to the second."""

    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts)
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]


def funding_cost(fund, entry_ms, end_ms):
    """-> (cost paid by the long as a fraction of entry notional, rule). No imputation: when the cache does not cover the
    whole window the cost is 0 and the rule is NOT_IN_DATA."""
    if fund is None or len(fund.ts) == 0 or fund.ts[0] > entry_ms or fund.ts[-1] < end_ms:
        return 0.0, "NOT_IN_DATA"
    lo = int(np.searchsorted(fund.ts, entry_ms, side="right"))
    hi = int(np.searchsorted(fund.ts, end_ms, side="right"))
    return float(fund.cum[hi] - fund.cum[lo]), "REAL"


# ---------------------------------------------------------------- simulator
def stop_risk(seg, d0, entry_px):
    """Stop distance as a fraction of entry: max(3 ATR14 (prior close) / entry, 10%). NaN if ATR undefined."""
    a = seg.atr[d0 - 1]
    if a != a:
        return float("nan")
    return max(STOP_ATR_MULT * float(a) / entry_px, STOP_FLOOR)


def trade_at(seg, d0, fund=None, risk=None, use_stop=True, hold=HOLD_DAYS):
    """One long entered at the open of daily bar d0. Exit = first of stop (daily low <= stop; stop wins ties; a bar that
    opens at or below the stop fills at the open) or the close of d0 + hold - 1. Returns None when the window is
    incomplete on a segment that has not ended."""
    if d0 < 1 or d0 >= seg.n:
        return None
    entry_px = float(seg.o[d0])
    xd = d0 + hold - 1
    ended_flag = False
    if xd >= seg.n:
        if not seg.ended:
            return None
        xd, ended_flag = seg.n - 1, True
    r = stop_risk(seg, d0, entry_px) if risk is None else risk
    if r != r:
        return None
    stop = entry_px * (1.0 - r)
    exit_px, why, ed = float(seg.c[xd]), ("ENDED" if ended_flag else "TIME"), xd
    if use_stop:
        for d in range(d0, xd + 1):
            if seg.l[d] <= stop:
                gap = seg.o[d] <= stop
                exit_px, why, ed = float(seg.o[d] if gap else stop), ("STOP-GAP" if gap else "STOP"), d
                break
    entry_ms = int(seg.ms[d0])
    end_ms = int(seg.ms[ed]) + DAY
    fcost, frule = funding_cost(fund, entry_ms, end_ms)
    gross = exit_px / entry_px - 1.0
    net = gross - FEE_RT - fcost
    return dict(coin=seg.name, seg=seg.seg_id, d0=d0, signal_ts=int(seg.ms[d0 - 1]), entry_ts=entry_ms,
                entry_px=entry_px, stop=stop, risk=r, exit_ts=int(seg.ms[ed]), exit_px=exit_px, exit_reason=why,
                days=ed - d0 + 1, gross=gross, fee=FEE_RT, funding=fcost, funding_rule=frule,
                net_nofund=gross - FEE_RT, net=net, gross_R=gross / r, net_R=net / r, fee_R=FEE_RT / r,
                split=split_of(int(seg.ms[d0 - 1])), iso_week=iso_week_of(entry_ms), week_i=week_index(entry_ms),
                ended=ended_flag)


def event_trades(seg, fund=None):
    out = []
    for ev in events(seg):
        t = trade_at(seg, ev["d0"], fund)
        if t is not None:
            out.append(t)
    return out


# ---------------------------------------------------------------- alive counts, BTC state
def alive_counts(segs):
    """{sunday_ms: number of coins alive (>= 365 daily bars of history) at that completed weekly bar}."""
    cnt = {}
    for s in segs:
        for ms in s.alive_sundays():
            cnt[ms] = cnt.get(ms, 0) + 1
    return cnt


def smooth_states(raw, days=SMOOTH_DAYS):
    """raw: list of (date_str, state) sorted. The smoothed state switches to the raw state only once the raw state has
    held for `days` consecutive days (the days-th day counts); until then the prior smoothed state holds."""
    out, cur, prev, run = {}, None, None, 0
    for d, st in raw:
        run = run + 1 if st == prev else 1
        prev = st
        if cur is None:
            cur = st
        elif run >= days:
            cur = st
        out[d] = cur
    return out


def load_state_table(path):
    import csv
    raw = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            raw.append((r["date"], r.get("cycle") or "NA"))
    raw.sort()
    return smooth_states(raw)


# ---------------------------------------------------------------- BTC descriptive row (a)
def btc_reclaim_events(btc, state):
    """BTC-only event (descriptive): weekly close above SMA200d after >= 8 consecutive weekly closes below it, smoothed
    state BEAR on >= 20 of the last 52 weeks, and the min over the last 52 weeks of (weekly close / max close of the
    prior 730 days - 1) <= -0.45. Returns list of dict(k, s, d0, reclaim_low)."""
    out = []
    below, dd, bear = [], [], []
    for k, s in enumerate(btc.wclose_idx):
        s = int(s)
        if s + 1 < 200:
            below.append(None)
            dd.append(None)
            bear.append(0)
            continue
        sm = float(btc.c[s - 199:s + 1].mean())
        below.append(bool(btc.wc[k] < sm))
        lo = max(0, s - DD_WINDOW + 1)
        dd.append(float(btc.wc[k] / btc.c[lo:s + 1].max() - 1.0))
        bear.append(1 if state.get(date_of(btc.ms[s])) == "BEAR" else 0)
        if s + 1 >= btc.n or k < 60 or below[k] is not False:
            continue
        if not all(b is True for b in below[k - 8:k]):
            continue
        if sum(bear[k - 51:k + 1]) < 20:
            continue
        if min(x for x in dd[k - 51:k + 1] if x is not None) > -0.45:
            continue
        ws = int(btc.wstart[k])
        out.append(dict(k=k, s=s, d0=s + 1, reclaim_low=float(btc.l[ws:s + 1].min())))
    return out


# ---------------------------------------------------------------- loaders
def load_segments(path, name):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4))
    a = np.atleast_2d(a)
    a = a[np.argsort(a[:, 0])]
    t = (a[:, 0] // DAY).astype(np.int64)
    br = np.r_[0, np.where(np.diff(t) != 1)[0] + 1, len(t)]
    segs = []
    for j in range(len(br) - 1):
        segs.append(Seg(name, a[br[j]:br[j + 1]], final=(j == len(br) - 2), seg_id=j))
    return segs


def load_funding(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    a = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1)))
    return Funding(a[:, 0], a[:, 1]) if a.size else None


def universe(cache_root="F:/MTS/data_cache/binance"):
    """Union of the two folders' spot_1d file lists, one entry per coin (wave2 folder wins for BTC and ETH).
    -> sorted list of (coin, spot_path, funding_path)."""
    out = {}
    for folder in ("combo-edge-miner-1114", "wave2-1114"):
        for p in sorted(pathlib.Path(cache_root, folder, "spot_1d").glob("*USDT.csv")):
            coin = p.name[:-8]
            out[coin] = (coin, str(p), str(pathlib.Path(cache_root, folder, "funding", p.name)))
    return [out[k] for k in sorted(out)]
