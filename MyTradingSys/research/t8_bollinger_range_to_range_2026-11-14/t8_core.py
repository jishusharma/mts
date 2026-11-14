"""T8 core: Bollinger range-to-range, signal, simulator, mirror, cost model. See PRE_REG.md (frozen, the law).

Pure functions on numpy arrays; the only file access is in the explicit loaders at the bottom.
Indicators: Bollinger FORMULAS.md s22 (population sd), ADX Wilder s30, ATR Wilder (TR0 uses its own close as previous close,
seed = simple mean of the first 14 TR). Parameters are labelled in PRE_REG.md; no private cost constants (fees.py).
"""
import sys
import os
import time
import pathlib
import datetime as dt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

sys.dont_write_bytecode = True
_BT = pathlib.Path(__file__).resolve().parents[2] / "backtest"
sys.path.insert(0, str(_BT))
import fees  # noqa: E402  SOURCED constants

DAY = 86400000
HOUR4 = 4 * 3600000
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13          # round trip, fraction of price
BB_N, BB_K = 20, 2.0
ADX_N, ADX_MAX = 14, 20.0
RANGE_N, RANGE_MAX = 30, 0.30
REENTRY_WIN = 3
WIDTH_MIN = 0.10
ATR_N, ATR_MULT = 14, 0.5
MIN_ALIVE_BARS = 260
MIN_ALIVE_COINS = 30
ENDED_GAP_DAYS = 30
DEV_END_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)   # signal bar < this = DEV
SEED = 1114
PLACEBO_WINDOW_DAYS = 56
CAND_CAP = 100


def _ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


HOLES = {"LUNA": (_ms(2022, 5, 13), _ms(2022, 6, 1)), "FTT": (_ms(2022, 11, 15), _ms(2023, 9, 23))}   # [start, end) ms

CELLS = {
    "1d": dict(bar=DAY, floor=0.015, cap=20, cool=10),
    "4h": dict(bar=HOUR4, floor=0.025, cap=42, cool=12),
}


# ---------------------------------------------------------------- process hygiene
def set_low_priority():
    """BelowNormal priority (psutil, else ctypes SetPriorityClass 0x4000). Returns a printable string."""
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        return "psutil BELOW_NORMAL set; class now %s" % psutil.Process().nice()
    except Exception:
        pass
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentProcess.restype = wintypes.HANDLE
        k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k.SetPriorityClass.restype = wintypes.BOOL
        k.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k.GetPriorityClass.restype = wintypes.DWORD
        h = k.GetCurrentProcess()
        ok = k.SetPriorityClass(h, 0x4000)
        got = k.GetPriorityClass(h)
        return "ctypes SetPriorityClass 0x4000 ok=%s; GetPriorityClass now 0x%x" % (bool(ok), got)
    except Exception as e:  # pragma: no cover
        return "priority NOT set: %r" % (e,)


SLOT_DIR = pathlib.Path(r"F:/MTS/data_cache/wave3-1114/_slots")


def acquire_slot(slot_id, max_locks=4, max_age_s=1800, wait_s=30):
    SLOT_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        now = time.time()
        live = [p for p in SLOT_DIR.glob("*.lock") if now - p.stat().st_mtime < max_age_s and p.stem != slot_id]
        if len(live) < max_locks:
            break
        time.sleep(wait_s)
    p = SLOT_DIR / (slot_id + ".lock")
    p.write_text(str(os.getpid()))
    return p


def release_slot(p):
    try:
        pathlib.Path(p).unlink()
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


def bollinger(c, n=BB_N, k=BB_K):
    """(mid, upper, lower) with population sd; NaN until n closes exist."""
    m = len(c)
    mid = np.full(m, np.nan)
    up = np.full(m, np.nan)
    lo = np.full(m, np.nan)
    if m >= n:
        w = sliding_window_view(np.asarray(c, float), n)
        mu = w.mean(1)
        sd = w.std(1)                                   # ddof=0, population
        mid[n - 1:] = mu
        up[n - 1:] = mu + k * sd
        lo[n - 1:] = mu - k * sd
    return mid, up, lo


def adx_wilder(h, l, c, n=ADX_N):
    """ADX per FORMULAS.md s30.1; first defined at bar 2n-1; NaN before."""
    m = len(c)
    adx = np.full(m, np.nan)
    if m < 2 * n:
        return adx
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    up = h[1:] - h[:-1]
    dn = l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    # index j of these arrays = bar j+1
    s_tr, s_p, s_m = tr[:n].sum(), pdm[:n].sum(), mdm[:n].sum()
    dx = np.full(m, np.nan)

    def _dx(a, b, t):
        if t == 0:
            return 0.0
        dip, dim = 100.0 * a / t, 100.0 * b / t
        s = dip + dim
        return 0.0 if s == 0 else 100.0 * abs(dip - dim) / s

    dx[n] = _dx(s_p, s_m, s_tr)
    for i in range(n + 1, m):
        j = i - 1
        s_tr = s_tr - s_tr / n + tr[j]
        s_p = s_p - s_p / n + pdm[j]
        s_m = s_m - s_m / n + mdm[j]
        dx[i] = _dx(s_p, s_m, s_tr)
    first = 2 * n - 1
    adx[first] = dx[n:first + 1].mean()
    for i in range(first + 1, m):
        adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return adx


def range30(h, l, c, n=RANGE_N):
    """(max high - min low over last n bars) / mean close over the same n bars; NaN before n bars."""
    m = len(c)
    out = np.full(m, np.nan)
    if m >= n:
        hh = sliding_window_view(np.asarray(h, float), n).max(1)
        ll = sliding_window_view(np.asarray(l, float), n).min(1)
        mc = sliding_window_view(np.asarray(c, float), n).mean(1)
        out[n - 1:] = (hh - ll) / mc
    return out


def day_gate(h, l, c):
    """1d coin range gate array: ADX14 < 20 AND range30 <= 0.30 (False where undefined)."""
    a = adx_wilder(h, l, c)
    r = range30(h, l, c)
    with np.errstate(invalid="ignore"):
        return (a < ADX_MAX) & (r <= RANGE_MAX)


# ---------------------------------------------------------------- segments
class Seg:
    """One contiguous run of bars of one coin on one timeframe, with indicators and signal arrays.
    rows: array [ts, open, high, low, close]. `gate` and `alive` default to the own 1d definitions and are
    replaced for 4h segments by the mapped 1d values (attach_day_map)."""

    def __init__(self, coin, tf, rows, is_final=True, ended=False):
        a = np.asarray(rows, float)
        self.coin, self.tf, self.cell = coin, tf, CELLS[tf]
        self.ms, self.o, self.h, self.l, self.c = a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(self.ms)
        self.is_final, self.ended = is_final, ended
        self.mid, self.up, self.lo = bollinger(self.c)
        with np.errstate(invalid="ignore", divide="ignore"):
            self.width = (self.up - self.lo) / self.mid
        self.atr = wilder_atr(self.h, self.l, self.c) if self.n >= ATR_N else np.full(self.n, np.nan)
        if tf == "1d":
            self.gate = day_gate(self.h, self.l, self.c)
            self.alive = np.arange(self.n) >= MIN_ALIVE_BARS - 1
        else:
            self.gate = np.zeros(self.n, bool)
            self.alive = np.zeros(self.n, bool)
        self.date_ok = np.ones(self.n, bool)          # >= 30 alive coins on the bar's date (set by set_date_ok)
        with np.errstate(invalid="ignore"):
            self.out_lo = self.c < self.lo
            self.out_up = self.c > self.up
            self._in_lo = self.c > self.lo
            self._in_up = self.c < self.up
        self._raw = {}

    # raw first re-entry arrays -------------------------------------------------
    def raw_reentry(self, side):
        """bool array: first raw band re-entry at bar t (uses closes and bands through t only)."""
        if side in self._raw:
            return self._raw[side]
        out_ = self.out_lo if side > 0 else self.out_up
        in_ = self._in_lo if side > 0 else self._in_up
        n = self.n
        any3 = np.zeros(n, bool)
        for k in range(1, REENTRY_WIN + 1):
            any3[k:] |= out_[:n - k]
        r = in_ & any3
        first = r.copy()
        first[1:] &= ~r[:-1]
        self._raw[side] = first
        return first


def build_segments(coin, tf, rows, universe_end_ms):
    a = np.asarray(rows, float)
    a = a[np.argsort(a[:, 0])]
    a = a[np.r_[True, np.diff(a[:, 0]) > 0]]
    bar = CELLS[tf]["bar"]
    br = np.r_[0, np.where(np.diff(a[:, 0]) != bar)[0] + 1, len(a)]
    segs = []
    last_ms = a[-1, 0] + bar if len(a) else 0
    ended = bool(len(a) == 0 or last_ms < universe_end_ms - ENDED_GAP_DAYS * DAY)
    for i in range(len(br) - 1):
        s = Seg(coin, tf, a[br[i]:br[i + 1]], is_final=(i == len(br) - 2), ended=ended)
        segs.append(s)
    return segs


def attach_day_map(seg4, day_map):
    """4h segment: gate/alive from the last completed 1d bar. day_map: {day_number: (gate, alive)}.
    For a 4h bar opening at ms, close time = ms + 4h; the last completed 1d bar has day number (close // DAY) - 1."""
    dn = (seg4.ms + HOUR4) // DAY - 1
    g = np.zeros(seg4.n, bool)
    al = np.zeros(seg4.n, bool)
    for i, d in enumerate(dn):
        v = day_map.get(int(d))
        if v is not None:
            g[i], al[i] = v
    seg4.gate, seg4.alive = g, al


def day_map_of(segs1d):
    m = {}
    for s in segs1d:
        dn = s.ms // DAY
        for i in range(s.n):
            m[int(dn[i])] = (bool(s.gate[i]), bool(s.alive[i]))
    return m


def alive_counts(all_segs1d):
    """{day_number: number of alive coins on that day (1d bars)}."""
    cnt = {}
    for segs in all_segs1d:
        for s in segs:
            dn = s.ms // DAY
            for d in dn[s.alive]:
                cnt[int(d)] = cnt.get(int(d), 0) + 1
    return cnt


def set_date_ok(seg, counts):
    dn = seg.ms // DAY
    seg.date_ok = np.array([counts.get(int(d), 0) >= MIN_ALIVE_COINS for d in dn], bool)


# ---------------------------------------------------------------- signals
def find_signals(seg, side, gate_override=None, use_filters=True):
    """Signal bars for one side. Returns list of dicts(t, date_ok). Cooldown starts when a signal fires.
    gate_override (bool array) is for tests only."""
    cell = seg.cell
    raw = seg.raw_reentry(side)
    gate = seg.gate if gate_override is None else gate_override
    ok = raw & gate & seg.alive
    if use_filters:
        with np.errstate(invalid="ignore"):
            ok &= (seg.width >= WIDTH_MIN)
        ok &= ~np.isnan(seg.atr)
    out, last = [], -10 ** 9
    for t in np.where(ok)[0]:
        t = int(t)
        if t - last < cell["cool"]:
            continue
        last = t
        out.append(dict(t=t, date_ok=bool(seg.date_ok[t])))
    return out


def outside_run_start(seg, t, side):
    """First bar of the consecutive outside-close run containing the most recent outside close in t-3..t-1."""
    out_ = seg.out_lo if side > 0 else seg.out_up
    j = None
    for k in range(1, REENTRY_WIN + 1):
        if t - k >= 0 and out_[t - k]:
            j = t - k
            break
    if j is None:
        return None
    while j - 1 >= 0 and out_[j - 1]:
        j -= 1
    return j


def make_entry(seg, t, side):
    """Entry plan for the signal on bar t. Returns (plan or None, skip_reason). Uses bars through t plus the open of t+1."""
    cell = seg.cell
    e = t + 1
    if e >= seg.n:
        return None, "NO_ENTRY_BAR"
    entry = float(seg.o[e])
    rs = outside_run_start(seg, t, side)
    if rs is None:
        return None, "NO_OUTSIDE"
    atr = float(seg.atr[t])
    if side > 0:
        raw = float(seg.l[rs:t + 1].min()) - ATR_MULT * atr
        stop = min(raw, entry * (1 - cell["floor"]))
        target = float(seg.up[t])
        if target <= entry:
            return None, "TARGET_BEHIND"
    else:
        raw = float(seg.h[rs:t + 1].max()) + ATR_MULT * atr
        stop = max(raw, entry * (1 + cell["floor"]))
        target = float(seg.lo[t])
        if target >= entry:
            return None, "TARGET_BEHIND"
    stop_pct = abs(entry - stop) / entry
    tgt_pct = abs(target - entry) / entry
    return dict(e=e, entry=entry, stop=stop, target=target, stop_pct=stop_pct, tgt_pct=tgt_pct, rs=rs), ""


def window_status(seg, e):
    """(last_idx, status) by availability only. status in OK, INCOMPLETE, GAP_SPAN, ENDED."""
    last = e + seg.cell["cap"] - 1
    if last < seg.n:
        return last, "OK"
    if not seg.is_final:
        return seg.n - 1, "GAP_SPAN"
    if seg.ended:
        return seg.n - 1, "ENDED"
    return seg.n - 1, "INCOMPLETE"


def hole_hit(seg, e, last):
    h = HOLES.get(seg.coin)
    if h is None:
        return False
    s, en = int(seg.ms[e]), int(seg.ms[last]) + seg.cell["bar"]
    return s < h[1] and en > h[0]


def simulate(seg, e, side, entry, stop, target, last):
    """Walk bars e..last. Stop checked first each bar (stop wins ties). target=None: hold to last close.
    Returns (k_exit, exit_px, reason). reason in STOP, STOP_GAP, TARGET, TIME."""
    o, h, l, c = seg.o, seg.h, seg.l, seg.c
    for k in range(e, last + 1):
        if side > 0:
            if l[k] <= stop:
                if k > e and o[k] <= stop:
                    return k, float(o[k]), "STOP_GAP"
                return k, float(stop), "STOP"
            if target is not None and h[k] >= target:
                return k, float(target), "TARGET"
        else:
            if h[k] >= stop:
                if k > e and o[k] >= stop:
                    return k, float(o[k]), "STOP_GAP"
                return k, float(stop), "STOP"
            if target is not None and l[k] <= target:
                return k, float(target), "TARGET"
    return last, float(c[last]), "TIME"


# ---------------------------------------------------------------- funding
class Funding:
    """Funding prints (ts ms, rate). Window rule: entry_ms < print <= end_ms; prints rounded to the second."""

    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts)
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]

    def sum_rate(self, entry_ms, end_ms):
        """-> (sum of rates in (entry, end], covered). Not covered: (0.0, False); never imputed."""
        if len(self.ts) == 0 or self.ts[0] > entry_ms or self.ts[-1] < end_ms:
            return 0.0, False
        lo = int(np.searchsorted(self.ts, entry_ms, side="right"))
        hi = int(np.searchsorted(self.ts, end_ms, side="right"))
        return float(self.cum[hi] - self.cum[lo]), True


def funding_part(fund, entry_ms, end_ms, side):
    """Funding cost as a fraction of entry notional paid by the position (long pays +rate, short receives it)."""
    if fund is None:
        return 0.0, False
    s, cov = fund.sum_rate(entry_ms, end_ms)
    return side * s, cov


# ---------------------------------------------------------------- trades
def split_of(ms):
    return "DEV" if ms < DEV_END_MS else "VAL"


def week_index(ms):
    """Monday-based week number (epoch day 0 is a Thursday): Monday 00:00 starts a new week, Sunday belongs to the old one."""
    return int((ms // DAY + 3) // 7)


def iso_week_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def date_of(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d")


def run_leg(seg, plan, side, last, fund):
    """Simulate one leg and cost it. Returns dict with exit info and returns in fraction and R."""
    e, entry = plan["e"], plan["entry"]
    sp = plan["stop_pct"]
    if side == plan["side"]:
        stop, target = plan["stop"], plan["target"]
    else:                                             # mirror leg: reflected distances
        stop = entry * (1 - side * sp)
        target = entry * (1 + side * plan["tgt_pct"])
    k, px, why = simulate(seg, e, side, entry, stop, target, last)
    gross = side * (px / entry - 1.0)
    end_ms = int(seg.ms[k]) + seg.cell["bar"]
    fp, cov = funding_part(fund, int(seg.ms[e]), end_ms, side)
    net_nofund = gross - FEE_RT
    net = net_nofund - fp
    return dict(k=k, px=px, reason=why, bars=k - e + 1, gross=gross, fee=FEE_RT, fund=fp, fund_cov=cov,
                net_nofund=net_nofund, net=net, gross_R=gross / sp, fee_R=FEE_RT / sp, net_R=net / sp,
                nofund_R=net_nofund / sp, exit_ms=end_ms, stop=stop, target=target)


def plan_trades(seg, counts=None):
    """Signals -> entry plans, by availability only (NO outcome is read). Yields (side, t, plan, last, status).
    counts (dict) collects the reasons signals were dropped."""
    cnt = counts if counts is not None else {}
    out = []
    for side in (1, -1):
        for sg in find_signals(seg, side):
            t = sg["t"]
            cnt["signals"] = cnt.get("signals", 0) + 1
            if not sg["date_ok"]:
                cnt["lt30_alive_dates"] = cnt.get("lt30_alive_dates", 0) + 1
                continue
            plan, why = make_entry(seg, t, side)
            if plan is None:
                cnt["skip_" + why] = cnt.get("skip_" + why, 0) + 1
                continue
            plan["side"] = side
            last, st = window_status(seg, plan["e"])
            if st in ("INCOMPLETE", "GAP_SPAN"):
                cnt["skip_" + st] = cnt.get("skip_" + st, 0) + 1
                continue
            if hole_hit(seg, plan["e"], last):
                cnt["skip_HOLE"] = cnt.get("skip_HOLE", 0) + 1
                continue
            cnt["trades"] = cnt.get("trades", 0) + 1
            out.append((side, t, plan, last, st))
    return out


def trades_for_seg(seg, fund, counts=None):
    """All trades of one segment, both sides, with mirror legs."""
    out = []
    for side, t, plan, last, st in plan_trades(seg, counts):
        real = run_leg(seg, plan, side, last, fund)
        mir = run_leg(seg, plan, -side, last, fund)
        sig_ms, ent_ms = int(seg.ms[t]), int(seg.ms[plan["e"]])
        out.append(dict(
            coin=seg.coin, tf=seg.tf, side=side, split=split_of(sig_ms), sig_t=t, e=plan["e"], seg=seg,
            signal_ms=sig_ms, entry_ms=ent_ms, signal_date=date_of(sig_ms), entry_date=date_of(ent_ms),
            entry_px=plan["entry"], stop_pct=plan["stop_pct"], tgt_pct=plan["tgt_pct"], last=last,
            ended=(st == "ENDED"), status=st, week=week_index(ent_ms), iso_week=iso_week_of(ent_ms),
            exit_ms=real["exit_ms"], exit_px=real["px"], reason=real["reason"], bars=real["bars"],
            gross=real["gross"], fee=real["fee"], fund=real["fund"], fund_cov=real["fund_cov"],
            net_nofund=real["net_nofund"], net=real["net"], gross_R=real["gross_R"], fee_R=real["fee_R"],
            net_R=real["net_R"], nofund_R=real["nofund_R"],
            m_reason=mir["reason"], m_gross_R=mir["gross_R"], m_net_R=mir["net_R"], m_net=mir["net"]))
    return out


# ---------------------------------------------------------------- phase read (BTC, descriptive strata)
def smooth_cycle(cycles, need=10):
    """cycles: list of raw cycle strings in date order -> smoothed list. A new state counts only after `need` consecutive
    days of that value; until then the prior state holds (initial prior = 'NA')."""
    out, state, run_val, run = [], "NA", None, 0
    for v in cycles:
        if v == run_val:
            run += 1
        else:
            run_val, run = v, 1
        if run >= need and v:
            state = v
        out.append(state)
    return out


def load_phase_table(path):
    import csv
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"], r.get("label") or "NA", r.get("cycle") or ""))
    rows.sort()
    sm = smooth_cycle([r[2] for r in rows])
    return {d: (lab, sc) for (d, lab, _), sc in zip(rows, sm)}


def phase_tag(table, entry_ms):
    r = table.get(date_of(entry_ms))
    return r if r else ("NA", "NA")


# ---------------------------------------------------------------- loaders
def _load_csv(path):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4))
    return np.atleast_2d(a)


def load_funding(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    a = np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1))
    a = np.atleast_2d(a)
    return Funding(a[:, 0], a[:, 1]) if a.size else None


ROOT = pathlib.Path(r"F:/MTS/data_cache/binance")
SRC = ["wave2-1114", "combo-edge-miner-1114"]
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"


def universe_names():
    names = []
    for d in SRC:
        for p in sorted((ROOT / d / "spot_1d").glob("*USDT.csv")):
            n = p.name[:-8]
            if n not in names:
                names.append(n)
    return sorted(names)


def coin_path(tf, name):
    for d in SRC:
        p = ROOT / d / ("spot_" + tf) / (name + "USDT.csv")
        if p.exists():
            return p
    return None


def coin_funding(name):
    for d in SRC:
        p = ROOT / d / "funding" / (name + "USDT.csv")
        if p.exists():
            return load_funding(p)
    return None


def load_universe(tfs=("1d", "4h"), names=None):
    """-> dict tf -> {coin: [Seg...]}, funding dict, counts per date, universe_end_ms. 4h gates come from 1d."""
    names = names or universe_names()
    raw1 = {}
    for n in names:
        p = coin_path("1d", n)
        if p is not None:
            raw1[n] = _load_csv(p)
    uend = max(float(a[:, 0].max()) for a in raw1.values()) + DAY
    segs1 = {n: build_segments(n, "1d", a, uend) for n, a in raw1.items()}
    counts = alive_counts(list(segs1.values()))
    for ss in segs1.values():
        for s in ss:
            set_date_ok(s, counts)
    out = {"1d": segs1}
    if "4h" in tfs:
        segs4 = {}
        for n in raw1:
            p = coin_path("4h", n)
            if p is None:
                continue
            ss = build_segments(n, "4h", _load_csv(p), uend)
            dm = day_map_of(segs1[n])
            for s in ss:
                attach_day_map(s, dm)
                set_date_ok(s, counts)
            segs4[n] = ss
        out["4h"] = segs4
    funds = {n: coin_funding(n) for n in raw1}
    return out, funds, counts, uend


def build_trades(segs_by_coin, funds, tf):
    """All trades of one timeframe plus skip counts (reasons only). No pooled statistic."""
    rows, counts = [], {}
    for n in sorted(segs_by_coin):
        for s in segs_by_coin[n]:
            rows.extend(trades_for_seg(s, funds.get(n), counts))
    rows.sort(key=lambda r: (r["entry_ms"], r["coin"], r["side"]))
    return rows, counts
