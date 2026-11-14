"""T11 core: breadth washout long (1d). Signal, leg simulator, cost model, BTC state. PRE_REG.md is the law.

Pure numpy; loaders are explicit and only used by t11_run.py. Tests never touch the data cache.
Indicator formulas: RSI Wilder per MyTradingSys/backtest/layers/FORMULAS.md section 1 (seed = mean of first 14 deltas,
RSI defined from index 14; avg_loss == 0 gives 100 if avg_gain > 0 else 50). ATR Wilder (first TR uses its own close as
previous close, seeded by the mean of the first 14 TR). Parameters are labelled SOURCED or OURS in PRE_REG.md.
"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
_BT = pathlib.Path(__file__).resolve().parents[2] / "backtest"
sys.path.insert(0, str(_BT))
import fees  # noqa: E402  SOURCED constants

DAY = 86400000
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13      # round trip, fraction of price (12 bp)
RSI_N = 14                  # SOURCED Wilder
BREADTH_LVL = 30.0          # SOURCED (Wilder 30)
ENTRY_RSI = 35.0            # OURS
BREADTH_TRIG = 0.15         # OURS
GAP_DAYS = 7                # OURS  (>= 7 days with B < trigger before an event)
MERGE_DAYS = 14             # OURS  (events within 14 days merge into one episode)
MIN_BARS = 200              # OURS  alive rule (T11 spec; the shared 260 is overridden by the T11 section)
MIN_ALIVE = 30              # OURS
ATR_N = 14                  # SOURCED period
ATR_MULT = 2.5              # OURS
STOP_FLOOR = 0.08           # OURS
HOLD_DAYS = 10              # OURS: entry day is day 1, exit at the close of day 10 (= d0 + 9)
PLACEBO_B = 0.10            # OURS: placebo pool needs breadth < 10%
WINDOW_DAYS = 56            # SHARED RULES: same-window placebo = +/- 8 ISO weeks
SMOOTH_DAYS = 10            # OURS (shared rules): BTC state counts only after 10 consecutive days
SMA_N = 200                 # BTC SMA200d
ENDED_GAP_DAYS = 30         # OURS: coin is ENDED if its last bar is > 30 days before the pull
PULL_MS = int(dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)
DEV_END_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)   # signal bar open < this = DEV


def _ed(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() // 86400)


HOLES = {"LUNA": (_ed(2022, 5, 13), _ed(2022, 5, 31)), "FTT": (_ed(2022, 11, 15), _ed(2023, 9, 22))}


def set_below_normal():
    """Lower this process priority; return the resulting Windows priority class (0x4000 = BELOW_NORMAL) or -1."""
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
        k.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k.GetPriorityClass.restype = wintypes.DWORD
        k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k.SetPriorityClass.restype = wintypes.BOOL
        h = k.GetCurrentProcess()
        if k.GetPriorityClass(h) != 0x4000:
            k.SetPriorityClass(h, 0x4000)
        return int(k.GetPriorityClass(h))
    except Exception:
        return -1


# ------------------------------------------------------------------ indicators
def rsi_wilder(c, n=RSI_N):
    """FORMULAS.md section 1. Indices 0..n-1 are NaN."""
    c = np.asarray(c, float)
    m = len(c)
    out = np.full(m, np.nan)
    if m <= n:
        return out
    d = np.diff(c)
    g, l = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    ag, al = g[:n].mean(), l[:n].mean()

    def val(a, b):
        if b == 0:
            return 100.0 if a > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + a / b)

    out[n] = val(ag, al)
    for i in range(n + 1, m):
        ag = (ag * (n - 1) + g[i - 1]) / n
        al = (al * (n - 1) + l[i - 1]) / n
        out[i] = val(ag, al)
    return out


def wilder_atr(h, l, c, n=ATR_N):
    """ATR Wilder: TR0 uses its own close as previous close; seed = mean of first n TR."""
    m = len(c)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = np.full(m, np.nan)
    if m >= n:
        atr[n - 1] = tr[:n].mean()
        for i in range(n, m):
            atr[i] = (atr[i - 1] * (n - 1) + tr[i]) / n
    return atr


# ------------------------------------------------------------------ coin and market
class Coin:
    """Daily bars of one coin: rows [ts_ms, open, high, low, close]. Longest contiguous run of days is kept."""

    def __init__(self, name, rows, pull_ms=PULL_MS):
        a = np.asarray(rows, float)
        a = a[np.argsort(a[:, 0])]
        t = (a[:, 0] // DAY).astype(np.int64)
        br = np.r_[0, np.where(np.diff(t) != 1)[0] + 1, len(t)]
        i = int(np.argmax(np.diff(br)))
        lo, hi = int(br[i]), int(br[i + 1])
        self.dropped_rows = int(len(t) - (hi - lo))
        a, t = a[lo:hi], t[lo:hi]
        self.name = name
        self.ms, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.day0 = int(t[0])
        self.n = len(self.ms)
        self.rsi = rsi_wilder(self.c)
        self.atr = wilder_atr(self.h, self.l, self.c) if self.n >= ATR_N else np.full(self.n, np.nan)
        self.ended = bool(self.ms[-1] < pull_ms - ENDED_GAP_DAYS * DAY)

    @property
    def last_day(self):
        return self.day0 + self.n - 1


class Funding:
    """Funding prints (ts ms, rate). Window rule: entry_ms < print <= end_ms; prints rounded to the second."""

    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts)
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]

    def covers(self, entry_ms, end_ms):
        return len(self.ts) > 0 and self.ts[0] <= entry_ms and self.ts[-1] >= end_ms

    def cost_to(self, entry_ms, end_ms_arr):
        """Funding paid by the long (fraction of entry notional) for each end time; entry scalar."""
        lo = int(np.searchsorted(self.ts, entry_ms, side="right"))
        hi = np.searchsorted(self.ts, end_ms_arr, side="right")
        return self.cum[hi] - self.cum[lo]


class Market:
    """Day grid over all coins. rsi[c, d], alive[c, d] (bar present, >= MIN_BARS bars of history, RSI defined)."""

    def __init__(self, coins):
        self.coins = coins
        self.dmin = min(c.day0 for c in coins)
        self.dmax = max(c.last_day for c in coins)
        nd = self.dmax - self.dmin + 1
        self.nd = nd
        self.rsi = np.full((len(coins), nd), np.nan)
        self.alive = np.zeros((len(coins), nd), bool)
        for i, c in enumerate(coins):
            o = c.day0 - self.dmin
            self.rsi[i, o:o + c.n] = c.rsi
            al = np.zeros(c.n, bool)
            al[MIN_BARS - 1:] = True
            al &= ~np.isnan(c.rsi)
            self.alive[i, o:o + c.n] = al
        self.n_alive = self.alive.sum(0)
        low = (self.rsi <= BREADTH_LVL) & self.alive
        self.n_low = low.sum(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            self.breadth = np.where(self.n_alive > 0, self.n_low / np.maximum(self.n_alive, 1), np.nan)

    def di(self, day):
        return day - self.dmin


def find_events(breadth, gap=GAP_DAYS, trig=BREADTH_TRIG):
    """Event day index: B[d] >= trig and B[d-gap..d-1] all < trig (NaN counts as below). Uses data through d only."""
    out = []
    b = np.asarray(breadth, float)
    for d in range(gap, len(b)):
        if not (b[d] >= trig):
            continue
        prev = b[d - gap:d]
        if np.all(~(prev >= trig)):
            out.append(d)
    return out


def merge_episodes(days, merge=MERGE_DAYS):
    """days: sorted event days. Chain merge: an event within `merge` days of the previous event joins its episode.
    Returns list of episode ids (0-based), same length as days."""
    ids, cur, last = [], -1, None
    for d in days:
        if last is None or d - last > merge:
            cur += 1
        ids.append(cur)
        last = d
    return ids


def smooth_state(raw, k=SMOOTH_DAYS):
    """BTC smoothed state: a new raw state is adopted only on its k-th consecutive day; before that the prior holds."""
    out, cur, cand, cnt = [], None, None, 0
    for r in raw:
        if cur is None:
            cur = r
        elif r == cur:
            cand, cnt = None, 0
        else:
            if r == cand:
                cnt += 1
            else:
                cand, cnt = r, 1
            if cnt >= k:
                cur, cand, cnt = cand, None, 0
        out.append(cur)
    return out


def sma_flag(close, n=SMA_N):
    """close[t] > mean(close[t-n+1..t]); NaN-like None before n bars. Returns float array 1.0/0.0/nan."""
    c = np.asarray(close, float)
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    cs = np.cumsum(np.r_[0.0, c])
    m = (cs[n:] - cs[:-n]) / n
    out[n - 1:] = (c[n - 1:] > m).astype(float)
    return out


# ------------------------------------------------------------------ legs
def iso_week_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def split_of_ms(bar_open_ms):
    """Signal bar OPEN time (ms) -> DEV (bar date <= 2023-12-31) or VAL (>= 2024-01-01)."""
    return "DEV" if bar_open_ms < DEV_END_MS else "VAL"


def leg_signals(mkt, d):
    """Legs for event day index d: every alive coin with RSI14 <= 35 at the close of d, entry at the d+1 open.
    No outcome is computed here. Returns a list of dicts (coin index, local index of entry bar, entry px, stop dist)."""
    out = []
    for i, c in enumerate(mkt.coins):
        if not mkt.alive[i, d]:
            continue
        if not (mkt.rsi[i, d] <= ENTRY_RSI):
            continue
        t_loc = mkt.dmin + d - c.day0                       # local index of the signal bar
        d0 = t_loc + 1
        if d0 >= c.n:
            continue
        entry = float(c.o[d0])
        dist = max(ATR_MULT * float(c.atr[t_loc]), STOP_FLOOR * entry)
        out.append(dict(ci=i, coin=c.name, d0=d0, entry=entry, dist=dist, pct=dist / entry,
                        rsi=float(mkt.rsi[i, d])))
    return out


def _hole_hit(name, day_a, day_b):
    h = HOLES.get(name)
    return bool(h and day_a <= h[1] and day_b >= h[0])


def path_arrays(coin, d0s, fund=None, H=HOLD_DAYS):
    """Vectorised relative price paths for entries at local bar indices d0s (array). Returns dict of arrays or the
    reason a row is invalid. Rows: rel_open[k], rel_low[k], rel_close[k] relative to entry open (value/entry - 1) for
    k = 0..H-1; fund[k] = funding cost (fraction of entry) paid by the long up to the end of day k; nreal = number of
    real days (ENDED coins are padded by repeating the last bar). valid[m] False when window incomplete on a coin that
    still trades, or when the window overlaps a LUNA/FTT hole."""
    d0s = np.asarray(d0s, int)
    M = len(d0s)
    ks = np.arange(H)
    raw = d0s[:, None] + ks[None, :]
    xd = d0s + H - 1
    incomplete = xd >= coin.n
    valid = np.ones(M, bool)
    if not coin.ended:
        valid &= ~incomplete
    nreal = np.where(incomplete, coin.n - d0s, H)
    nreal = np.clip(nreal, 1, H)
    idx = np.minimum(raw, coin.n - 1)
    idx = np.clip(idx, 0, coin.n - 1)
    entry = coin.o[np.clip(d0s, 0, coin.n - 1)]
    rel_open = coin.o[idx] / entry[:, None] - 1.0
    rel_low = coin.l[idx] / entry[:, None] - 1.0
    rel_close = coin.c[idx] / entry[:, None] - 1.0
    ex_day = coin.day0 + np.minimum(xd, coin.n - 1)
    ent_day = coin.day0 + d0s
    hole = np.array([_hole_hit(coin.name, int(a), int(b)) for a, b in zip(ent_day, ex_day)], bool)
    valid &= ~hole
    valid &= (d0s >= 0) & (d0s < coin.n)
    fnd = np.zeros((M, H))
    nid = np.ones(M, bool)                                    # NOT_IN_DATA flag per row
    if fund is not None and len(fund.ts):
        end_all = coin.ms[idx] + DAY                          # end of day k (UTC midnight after bar k)
        for m in range(M):
            e_ms = int(coin.ms[min(int(d0s[m]), coin.n - 1)])
            if fund.covers(e_ms, int(end_all[m, -1])):
                fnd[m] = fund.cost_to(e_ms, end_all[m])
                nid[m] = False
    return dict(rel_open=rel_open, rel_low=rel_low, rel_close=rel_close, fund=fnd, nreal=nreal, valid=valid,
                hole=hole, incomplete=incomplete, funding_nid=nid, entry=entry, ent_day=ent_day, ex_day=ex_day)


def outcome_vec(P, pct):
    """Apply the stop rule to path arrays P with stop distance pct (fraction of entry; scalar or per-row).
    Stop wins ties: any bar whose low <= stop exits at the stop (or the open when it gaps through); otherwise the close
    of the last real day. Returns dict of arrays: gross, fund, net, net_R, gross_R, k_exit (0-based), reason code."""
    ro, rl, rc, fnd, nreal = P["rel_open"], P["rel_low"], P["rel_close"], P["fund"], P["nreal"]
    M, H = rl.shape
    pct = np.broadcast_to(np.asarray(pct, float), (M,)).copy()
    lvl = -pct
    hit = rl <= lvl[:, None] + 1e-12                          # tolerance: float noise at an exact touch
    # bars beyond the real window (ENDED padding) cannot trigger
    hit &= np.arange(H)[None, :] < nreal[:, None]
    anyhit = hit.any(1)
    first = np.argmax(hit, axis=1)
    rows = np.arange(M)
    k_exit = np.where(anyhit, first, nreal - 1)
    gap = anyhit & (ro[rows, first] <= lvl + 1e-12)
    gross = np.where(anyhit, np.where(gap, ro[rows, first], lvl), rc[rows, nreal - 1])
    fund = fnd[rows, k_exit]
    net = gross - FEE_RT - fund
    reason = np.where(anyhit, np.where(gap, 2, 1), 0)           # 0 TIME, 1 STOP, 2 STOP-GAP
    return dict(gross=gross, fund=fund, net=net, net_R=net / pct, gross_R=gross / pct, fee_R=FEE_RT / pct,
                k_exit=k_exit, reason=reason, days_held=k_exit + 1)


REASONS = ("TIME", "STOP", "STOP-GAP")


def simulate_leg(coin, d0, pct, fund=None):
    """One leg. Returns a dict or None (invalid window). Same code path as the placebo pool (path_arrays/outcome_vec)."""
    P = path_arrays(coin, [d0], fund)
    if not P["valid"][0]:
        return None
    o = outcome_vec(P, pct)
    k = int(o["k_exit"][0])
    ended_exit = bool(P["incomplete"][0])
    reason = REASONS[int(o["reason"][0])]
    if reason == "TIME" and ended_exit:
        reason = "ENDED-EXIT"
    xi = min(d0 + k, coin.n - 1)
    return dict(coin=coin.name, entry_ts=int(coin.ms[d0]), exit_ts=int(coin.ms[xi]), entry_px=float(coin.o[d0]),
                pct=float(pct), gross=float(o["gross"][0]), fee=FEE_RT, funding=float(o["fund"][0]),
                funding_rule="NOT_IN_DATA" if P["funding_nid"][0] else "REAL", net=float(o["net"][0]),
                gross_R=float(o["gross_R"][0]), net_R=float(o["net_R"][0]), fee_R=float(o["fee_R"][0]),
                days_held=int(o["days_held"][0]), exit_reason=reason, ended=reason == "ENDED-EXIT",
                nreal=int(P["nreal"][0]), ent_day=int(P["ent_day"][0]))


# ------------------------------------------------------------------ loaders (run script only)
def load_coin(path, name):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4))
    return Coin(name, np.atleast_2d(a))


def load_funding(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    a = np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1))
    a = np.atleast_2d(a)
    return Funding(a[:, 0], a[:, 1]) if a.size else None


def load_phase_cycle(path):
    """-> {epoch_day: raw cycle} from phase_daily.csv (row of day d uses closes through d-1)."""
    import csv
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            cyc = (r.get("cycle") or "").strip()
            if cyc:
                y, m, d = (int(x) for x in r["date"].split("-"))
                out[_ed(y, m, d)] = cyc
    return out
