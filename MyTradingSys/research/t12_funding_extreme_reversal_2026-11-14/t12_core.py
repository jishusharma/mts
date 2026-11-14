"""T12 core: funding extreme reversal (1d, two cells). See PRE_REG.md (frozen, the law).

Pure functions on numpy arrays. plan_trade() decides signal/eligibility from information through the signal bar
(and exogenous funding coverage); simulate_plan() is the only place an outcome (price path) is computed.
Cost: 12 bp round trip imported from MyTradingSys/backtest/fees.py; no private cost constants.
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
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13      # fraction of price, round trip
FLOOR = 0.0001            # 0.01% per 8h (SOURCED baseline, used as floor)
P_LO, P_HI = 5.0, 95.0    # OURS
PWIN = 180                # OURS trailing window, ending d-1
PMIN_VALID = 150          # OURS min valid F3 values in the window
SMOOTH_DAYS = 3
ATR_N = 14
ATR_MULT = 2.5            # OURS
MIN_STOP = 0.06           # OURS
HOLD = 10                 # OURS: entry day + 9, close of day 10
COOLDOWN = 10             # OURS
MIN_BARS = 260
MIN_ALIVE = 30
ENDED_GAP_DAYS = 30
CYCLE_CONFIRM = 10        # OURS
CELLS = {
    "A": dict(side=+1, labels=("MARKDOWN", "CAPITULATION", "RELIEF", "ACCUM-RANGE")),
    "B": dict(side=-1, labels=("MARKUP", "DISTRIBUTION")),
}
HOLES = {"LUNA": (dt.date(2022, 5, 13), dt.date(2022, 5, 31)), "FTT": (dt.date(2022, 11, 15), dt.date(2023, 9, 22))}


def _ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


DEV_END_MS = _ms(2024, 1, 1)      # signal bar open < this = DEV
VAL_END_MS = _ms(2026, 11, 1)     # signal bar open < this (VAL ends 2026-10-31)


def set_below_normal():
    """BelowNormal priority; returns a string proving the class that took."""
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        return "psutil nice=%s" % psutil.Process().nice()
    except Exception:
        pass
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = wintypes.HANDLE
        k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k.GetPriorityClass.restype = wintypes.DWORD
        h = k.GetCurrentProcess()
        ok = k.SetPriorityClass(h, 0x4000)
        return "ctypes SetPriorityClass ok=%s -> GetPriorityClass 0x%x (0x4000 = BELOW_NORMAL)" % (ok, k.GetPriorityClass(h))
    except Exception as e:  # not Windows
        return "priority NOT set: %r" % (e,)


class Slot:
    """Heavy-job slot: F:/MTS/data_cache/wave3-1114/_slots/<id>.lock; wait while >= 4 locks younger than 30 min."""

    def __init__(self, ident, root="F:/MTS/data_cache/wave3-1114/_slots"):
        self.p = pathlib.Path(root)
        self.ident = ident

    def __enter__(self):
        import time
        self.p.mkdir(parents=True, exist_ok=True)
        while True:
            live = [f for f in self.p.glob("*.lock") if time.time() - f.stat().st_mtime < 1800 and f.stem != self.ident]
            if len(live) < 4:
                break
            time.sleep(30)
        (self.p / (self.ident + ".lock")).write_text("t12")
        return self

    def __exit__(self, *a):
        try:
            (self.p / (self.ident + ".lock")).unlink()
        except OSError:
            pass


def wilder_atr(h, l, c, n=ATR_N):
    """ATR Wilder (FORMULAS.md): TR0 uses its own close as previous close; seed = mean of first n TR."""
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
    """Daily bars [ts_ms, o, h, l, c]. Split into contiguous segments at missing days (holes). Everything per bar:
    seg_start, seg_end (index of the segment's first/last bar), atr (Wilder, per segment), ended (segment is the
    coin's last and stopped trading >= 30 days before the data end)."""

    def __init__(self, name, rows, data_end_ms):
        a = np.asarray(rows, float)
        a = a[np.argsort(a[:, 0])]
        self.name = name
        self.ms, self.o, self.h, self.l, self.c = a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(self.ms)
        t = self.ms // DAY
        br = np.r_[0, np.where(np.diff(t) != 1)[0] + 1, self.n]
        self.seg_start = np.zeros(self.n, np.int64)
        self.seg_end = np.zeros(self.n, np.int64)
        self.atr = np.full(self.n, np.nan)
        for s, e in zip(br[:-1], br[1:]):
            self.seg_start[s:e] = s
            self.seg_end[s:e] = e - 1
            self.atr[s:e] = wilder_atr(self.h[s:e], self.l[s:e], self.c[s:e])
        self.last_ms = int(self.ms[-1]) if self.n else 0
        self.coin_ended = bool(self.n == 0 or self.last_ms < data_end_ms - ENDED_GAP_DAYS * DAY)


class Funding:
    """Funding prints (ts ms, rate). Prints rounded to the second. Daily sums/counts by UTC day of the print."""

    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts, kind="stable")
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]
        self.d0 = int(self.ts[0] // DAY) if len(self.ts) else 0
        nd = int(self.ts[-1] // DAY) - self.d0 + 1 if len(self.ts) else 0
        days = (self.ts // DAY - self.d0).astype(np.int64)
        self.dsum = np.bincount(days, weights=self.rate, minlength=nd) if nd else np.zeros(0)
        self.dcnt = np.bincount(days, minlength=nd) if nd else np.zeros(0, np.int64)
        # F3 per calendar day (index = day - d0): sum of 3 daily sums / 9 (per-8h equivalent), valid iff each of the
        # 3 days holds >= 3 prints
        self.f3 = np.full(nd, np.nan)
        for k in range(2, nd):
            if self.dcnt[k - 2:k + 1].min() >= 3:
                self.f3[k] = self.dsum[k - 2:k + 1].sum() / 9.0

    def f3_at(self, day):
        k = day - self.d0
        return self.f3[k] if 0 <= k < len(self.f3) else float("nan")

    def window(self, day):
        """Trailing PWIN F3 values for days day-PWIN .. day-1 (strictly before day)."""
        k = day - self.d0
        lo, hi = k - PWIN, k
        if lo < 0 or hi > len(self.f3):
            return np.full(0, np.nan)
        return self.f3[lo:hi]

    def cost(self, entry_ms, end_ms):
        """-> (sum of rates in entry_ms < print <= end_ms, number of prints)."""
        lo = int(np.searchsorted(self.ts, entry_ms, side="right"))
        hi = int(np.searchsorted(self.ts, end_ms, side="right"))
        return float(self.cum[hi] - self.cum[lo]), hi - lo


def extreme_flag(fund, day, side):
    """True if the funding extreme holds on day (uses F3 through day and the 180 values ending day-1)."""
    f = fund.f3_at(day)
    if f != f:
        return False
    w = fund.window(day)
    w = w[~np.isnan(w)]
    if len(w) < PMIN_VALID:
        return False
    if side > 0:
        return bool(f <= -FLOOR and f <= np.percentile(w, P_LO))
    return bool(f >= FLOOR and f >= np.percentile(w, P_HI))


def smooth_cycle(raw, confirm=CYCLE_CONFIRM):
    """raw: list of cycle strings by consecutive day. A state counts only after `confirm` consecutive days;
    until then the prior state holds."""
    out, cur, run_state, run = [], None, None, 0
    for r in raw:
        if r == run_state:
            run += 1
        else:
            run_state, run = r, 1
        if cur is None:
            cur = r
        elif run_state != cur and run >= confirm:
            cur = run_state
        out.append(cur)
    return out


class Phase:
    """BTC phase table: label of day d is built by the brain from closes through d-1 (usable on d)."""

    def __init__(self, days, labels, cycles):
        self.lab = {int(d): l for d, l in zip(days, labels)}
        sm = smooth_cycle(list(cycles))
        self.cyc = {int(d): c for d, c in zip(days, sm)}

    def label(self, day):
        return self.lab.get(int(day), "")

    def cycle(self, day):
        return self.cyc.get(int(day), "NA")


def load_phase(path):
    import csv
    days, labs, cycs = [], [], []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            d = dt.datetime.strptime(r["date"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
            days.append(int(d.timestamp() // 86400))
            labs.append(r.get("label") or "")
            cycs.append(r.get("cycle") or "NA")
    return Phase(days, labs, cycs)


def alive_counts(coins):
    """dict day -> number of coins with >= MIN_BARS bars of history in the current segment (spot only)."""
    cnt = {}
    for c in coins:
        idx = np.arange(c.n)
        ok = (idx - c.seg_start) >= MIN_BARS - 1
        for d in (c.ms[ok] // DAY):
            cnt[int(d)] = cnt.get(int(d), 0) + 1
    return cnt


def day_flags(coin, fund, phase, cell, alive=None):
    """Yield per signal bar i of the coin: dict(i, flag, rev). flag = alive coin, enough alive coins on the date,
    phase label in the cell gate, funding extreme. rev = reversal bar. Uses bars/funding through bar i only."""
    cfg = CELLS[cell]
    side = cfg["side"]
    out = []
    if fund is None:
        return out
    for i in range(MIN_BARS - 1, coin.n):
        if i - coin.seg_start[i] < MIN_BARS - 1:
            continue
        ms = int(coin.ms[i])
        if ms >= VAL_END_MS:
            break
        day = ms // DAY
        if alive is not None and alive.get(int(day), 0) < MIN_ALIVE:
            continue
        lab = phase.label(day)
        if lab not in cfg["labels"]:
            continue
        if not extreme_flag(fund, day, side):
            continue
        if side > 0:
            rev = bool(coin.c[i] > coin.o[i] and coin.c[i] > coin.h[i - 1])
        else:
            rev = bool(coin.c[i] < coin.o[i] and coin.c[i] < coin.l[i - 1])
        out.append(dict(i=i, flag=True, rev=rev, label=lab))
    return out


def signals(coin, fund, phase, cell, alive=None):
    """Fired signals after the per-coin cooldown (the clock moves when a signal fires)."""
    out, last = [], -10 ** 9
    for r in day_flags(coin, fund, phase, cell, alive):
        if r["rev"] and r["i"] - last >= COOLDOWN:
            last = r["i"]
            out.append(r)
    return out


def iso_week_idx(day):
    """Monday-start week index of an epoch day (epoch day 0 is a Thursday): a Sunday belongs to the week of its Monday."""
    return (int(day) + 3) // 7


def iso_week_label(day):
    d = dt.datetime.fromtimestamp(int(day) * 86400, dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def split_of(sig_ms):
    return "DEV" if sig_ms < DEV_END_MS else "VAL"


def plan_trade(coin, fund, i, side, stop_pct=None):
    """Decide the trade from info through signal bar i. Returns (plan, None) or (None, reason).
    Entry = open of bar i+1 (must be the next calendar day, same segment). Stop distance =
    max(2.5 x ATR14[i], 6% of entry) unless stop_pct is forced (placebo: same stop % as the real trade).
    Planned exit = close of bar entry+HOLD-1. If the segment ends first: a coin that ended trades to its last bar (ENDED),
    otherwise skip. Funding coverage of the planned window is required (>= 3 prints per day), no imputation."""
    j = i + 1
    if j >= coin.n or coin.seg_start[j] != coin.seg_start[i]:
        return None, "no_entry_bar"
    entry = float(coin.o[j])
    atr = float(coin.atr[i])
    if stop_pct is None:
        if atr != atr:
            return None, "no_atr"
        dist = max(ATR_MULT * atr, MIN_STOP * entry)
        stop_pct = dist / entry
    x = j + HOLD - 1
    ended = False
    if x > coin.seg_end[j]:
        last_seg = coin.seg_end[j] == coin.n - 1
        if last_seg and coin.coin_ended:
            x, ended = int(coin.seg_end[j]), True
        else:
            return None, "window_past_segment"
    entry_ms = int(coin.ms[j])
    end_ms = int(coin.ms[x]) + DAY
    nd = (end_ms - entry_ms) // DAY
    if fund is None:
        return None, "no_funding"
    _, npr = fund.cost(entry_ms, end_ms)
    if npr < 3 * nd or len(fund.ts) == 0 or fund.ts[0] > entry_ms or fund.ts[-1] < end_ms:
        return None, "no_funding"
    sig_ms = int(coin.ms[i])
    return dict(coin=coin.name, side=side, i=i, j=j, x=x, entry=entry, stop_pct=stop_pct, ended=ended,
                sig_ms=sig_ms, entry_ms=entry_ms, split=split_of(sig_ms),
                week=iso_week_idx(entry_ms // DAY), iso_week=iso_week_label(entry_ms // DAY)), None


def simulate_plan(coin, fund, p):
    """The only outcome computation. Stop wins ties: a bar whose range touches the stop exits at the stop (open if it
    gaps through), even if its close would have been favourable. Returns dict with gross/fee/funding in price
    fraction and in R (R = stop distance as a fraction of entry)."""
    side, entry, j, x = p["side"], p["entry"], p["j"], p["x"]
    sp = p["stop_pct"]
    stop = entry * (1.0 - side * sp)
    xs, px, why = x, float(coin.c[x]), "ENDED" if p["ended"] else "TIME"
    for d in range(j, x + 1):
        if side > 0 and coin.l[d] <= stop:
            gap = coin.o[d] <= stop
            xs, px, why = d, float(coin.o[d] if gap else stop), "STOP-GAP" if gap else "STOP"
            break
        if side < 0 and coin.h[d] >= stop:
            gap = coin.o[d] >= stop
            xs, px, why = d, float(coin.o[d] if gap else stop), "STOP-GAP" if gap else "STOP"
            break
    end_ms = int(coin.ms[xs]) + DAY
    fsum, _ = fund.cost(p["entry_ms"], end_ms)
    gross = side * (px / entry - 1.0)
    fundc = side * fsum              # long pays +rate; short receives it (cost negative when rate positive)
    netp = gross - FEE_RT
    nett = gross - FEE_RT - fundc
    r = dict(p)
    r.update(exit_i=xs, exit_px=px, reason=why, days=xs - j + 1, gross=gross, fee=FEE_RT, fund=fundc,
             netp=netp, nett=nett, gross_R=gross / sp, fee_R=FEE_RT / sp, fund_R=fundc / sp,
             netp_R=netp / sp, nett_R=nett / sp)
    return r


def flagged_next_day(coin, fund, i, side):
    """Baseline unit: flagged-state day i -> signed open-to-close return of bar i+1 and the carry cost of that day."""
    j = i + 1
    if j >= coin.n or coin.seg_start[j] != coin.seg_start[i]:
        return None
    ret = side * (float(coin.c[j]) / float(coin.o[j]) - 1.0)
    em = int(coin.ms[j])
    fsum, npr = fund.cost(em, em + DAY)
    if npr < 3:
        return None
    return ret, side * fsum


def load_coin(path, name, data_end_ms):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4))
    return Coin(name, np.atleast_2d(a), data_end_ms)


def load_funding(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    a = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1)))
    return Funding(a[:, 0], a[:, 1]) if a.size else None


CACHE = pathlib.Path("F:/MTS/data_cache")
W2 = CACHE / "binance" / "wave2-1114"
MN = CACHE / "binance" / "combo-edge-miner-1114"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"


def universe_names():
    """Union of the two funding folders' file lists (read at run time); wave2 files win for a coin in both."""
    a = {p.stem for p in (W2 / "funding").glob("*.csv")}
    b = {p.stem for p in (MN / "funding").glob("*.csv")}
    return sorted(a | b)


def _first(folder, name):
    for root in (W2, MN):
        p = root / folder / (name + ".csv")
        if p.exists():
            return p
    return None


def load_universe():
    """-> (coins list, {name: Funding}, data_end_ms, names). data_end = latest bar of any coin."""
    names = universe_names()
    raw = {}
    for n in names:
        p = _first("spot_1d", n)
        if p is not None:
            raw[n] = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4)))
    data_end = max(int(a[:, 0].max()) for a in raw.values())
    coins = [Coin(n, raw[n], data_end) for n in names if n in raw]
    funds = {n: load_funding(_first("funding", n)) for n in names}
    return coins, funds, data_end, names
