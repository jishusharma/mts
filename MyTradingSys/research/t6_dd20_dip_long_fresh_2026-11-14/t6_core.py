"""T6 core: DD20 weekly dip long, signal, simulator, cost model, phase read. See PRE_REG.md (frozen, the law).

Pure functions on numpy arrays; no file paths, no data cache access here except the explicit loaders.
Indicator formula: ATR Wilder per MyTradingSys/backtest/layers/FORMULAS.md (first TR uses its own close as
previous close, seeded by the simple mean of the first 14 TR). Parameters: 0.80 / 8 weeks / cooldown 8 weeks /
X2 = 14 days are SOURCED (edge9 study.py); the 2.5 ATR stop, the flat funding and DELIST-EXIT are OURS.
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
FEE_RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13          # round trip, fraction of price
FLAT_BP_PER_SLOT = 1.0                                            # OURS: 1 bp per 8 h slot paid by the long
FLAT_PER_SLOT = FLAT_BP_PER_SLOT / 10000.0
SLOTS_PER_DAY = 3
DD_FACTOR = 0.80                                                  # SOURCED edge9 study.py
DD_LOOKBACK = 8                                                   # SOURCED
COOLDOWN_WEEKS = 8                                                # SOURCED
HOLD_DAYS = 14                                                    # SOURCED X2: close of entry_day + 13
STOP_ATR_MULT = 2.5                                               # OURS
ATR_N = 14                                                        # SOURCED period (Wilder)
MIN_WEEKS = 60                                                    # OURS keep rule
ENDED_GAP_DAYS = 30                                               # OURS
DEV_END_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)  # entry < this = DEV
PULL_MS = int(dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)

SOURCE_UNIVERSE = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX", "AVAX", "BCH", "XLM",
                   "NEAR", "UNI", "ZEC", "AAVE", "HBAR", "XMR", "QNT", "ICP", "SHIB"]
CANDIDATES = ("NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN "
              "HBAR EGLD FTM GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND "
              "LUNA FTT XMR DASH OCEAN").split()
FRESH = [c for c in CANDIDATES if c not in SOURCE_UNIVERSE]


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
    """Daily bars of one coin. rows: array [ts_ms, open, high, low, close]. Longest contiguous run, starts on its
    first Monday 00:00 UTC. Full daily arrays are kept (exits may run into a trailing partial week); the weekly view
    uses whole 7-day weeks only."""

    def __init__(self, name, rows, pull_ms=PULL_MS):
        a = np.asarray(rows, float)
        a = a[np.argsort(a[:, 0])]
        t = (a[:, 0] // DAY).astype(np.int64)
        br = np.r_[0, np.where(np.diff(t) != 1)[0] + 1, len(t)]
        i = int(np.argmax(np.diff(br)))
        starts, ends = br[:-1], br[1:]
        run_lo, run_hi = int(starts[i]), int(ends[i])
        self.dropped_rows = int(len(t) - (run_hi - run_lo))
        a, t = a[run_lo:run_hi], t[run_lo:run_hi]
        mon = (t + 3) % 7 == 0                      # epoch day 0 is a Thursday
        if mon.any():
            first = int(np.argmax(mon))
            a, t = a[first:], t[first:]
        else:
            a, t = a[:0], t[:0]
        self.name = name
        self.ms, self.o, self.h, self.l, self.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(self.ms)
        self.nw = self.n // 7
        self.wc = self.c[6:7 * self.nw:7]
        self.atr = wilder_atr(self.h, self.l, self.c) if self.n >= ATR_N else np.full(self.n, np.nan)
        self.ended = bool(self.n == 0 or self.ms[-1] < pull_ms - ENDED_GAP_DAYS * DAY)


def bull_flag(wc, w):
    """Source tag: weekly close of week w above the mean of the 50 weekly closes ending at w; None if < 50 weeks."""
    if w < 49:
        return None
    return bool(wc[w] > wc[w - 49:w + 1].mean())


def events_dd20(coin):
    """DD20 events. Week w is complete; the event is known at the close of week w (Sunday), entry = next Monday open."""
    wc, out, last = coin.wc, [], -99
    for w in range(DD_LOOKBACK, coin.nw):
        d0 = 7 * (w + 1)
        if d0 >= coin.n:
            break
        close_w = wc[w]
        prior = wc[w - DD_LOOKBACK:w]
        if close_w <= DD_FACTOR * prior.max() and w - last >= COOLDOWN_WEEKS:
            last = w
            out.append(dict(w=w, d0=d0, bull=bull_flag(wc, w)))
    return out


class Funding:
    """Funding prints (ts ms, rate). Window rule: entry_ms < print <= end_ms; prints rounded to the second."""

    def __init__(self, ts, rate):
        ts = np.round(np.asarray(ts, float) / 1000.0).astype(np.int64) * 1000
        o = np.argsort(ts)
        self.ts, self.rate = ts[o], np.asarray(rate, float)[o]
        self.cum = np.r_[0.0, np.cumsum(self.rate)]

    def cost(self, entry_ms, end_ms):
        """-> (cost as fraction of entry notional paid by the long, used_flat)."""
        return funding_cost(self, entry_ms, end_ms)


def funding_cost(fund, entry_ms, end_ms):
    if fund is None or len(fund.ts) == 0 or fund.ts[0] > entry_ms or fund.ts[-1] < end_ms:
        ndays = (end_ms - entry_ms) // DAY
        return ndays * SLOTS_PER_DAY * FLAT_PER_SLOT, True
    lo = int(np.searchsorted(fund.ts, entry_ms, side="right"))   # prints strictly after entry
    hi = int(np.searchsorted(fund.ts, end_ms, side="right"))     # prints at or before end of exit day
    return float(fund.cum[hi] - fund.cum[lo]), False


def iso_week_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).isocalendar()
    return "%04d-W%02d" % (d[0], d[1])


def split_of(entry_ms):
    return "DEV" if entry_ms < DEV_END_MS else "VAL"


def trade_at(coin, d0, fund=None):
    """One long trade entered at the open of daily bar d0. Returns a dict or None (window incomplete on a coin that still
    trades). Both the PRIMARY (X2, no stop) and the STOP rows are computed. Fee + funding are subtracted from returns."""
    if d0 < 1 or d0 >= coin.n:
        return None
    entry_px = float(coin.o[d0])
    xd = d0 + HOLD_DAYS - 1
    delist = False
    if xd >= coin.n:
        if not coin.ended:
            return None
        xd, delist = coin.n - 1, True
    entry_ms = int(coin.ms[d0])
    end_ms = int(coin.ms[xd]) + DAY
    fee = FEE_RT
    exit_px = float(coin.c[xd])
    gross = exit_px / entry_px - 1.0
    fcost, flat = funding_cost(fund, entry_ms, end_ms)
    net_nofund = gross - fee
    net = gross - fee - fcost
    atr = float(coin.atr[d0 - 1])
    risk = STOP_ATR_MULT * atr / entry_px if atr == atr else float("nan")
    row = dict(coin=coin.name, d0=d0, signal_bar_ts=int(coin.ms[d0 - 1]), entry_ts=entry_ms, entry_px=entry_px,
               exit_ts=int(coin.ms[xd]), exit_px=exit_px, exit_reason="DELIST-EXIT" if delist else "TIME",
               gross=gross, fee=fee, funding=fcost, funding_rule="FLAT" if flat else "REAL",
               net_nofund=net_nofund, net=net, risk_unit=risk, delist=delist,
               gross_R=(gross / risk) if risk == risk else float("nan"),
               net_R=(net / risk) if risk == risk else float("nan"),
               split=split_of(entry_ms), iso_week=iso_week_of(entry_ms))
    # STOP row (OURS)
    stop_cols = dict(stop=float("nan"), stop_exit_ts=None, stop_exit_px=float("nan"), stop_reason="",
                     stop_gross=float("nan"), stop_funding=float("nan"), stop_funding_rule="",
                     stop_net=float("nan"), stop_R=float("nan"))
    if atr == atr:
        stop = entry_px - STOP_ATR_MULT * atr
        if stop > 0:
            sx, spx, why = xd, float(coin.c[xd]), "DELIST-EXIT" if delist else "TIME"
            for d in range(d0, xd + 1):
                if coin.l[d] <= stop:
                    gap = coin.o[d] <= stop
                    spx = float(coin.o[d] if gap else stop)
                    sx, why = d, ("STOP-GAP" if gap else "STOP")
                    break
            s_end = int(coin.ms[sx]) + DAY
            sf, sflat = funding_cost(fund, entry_ms, s_end)
            sg = spx / entry_px - 1.0
            sn = sg - fee - sf
            stop_cols = dict(stop=stop, stop_exit_ts=int(coin.ms[sx]), stop_exit_px=spx, stop_reason=why,
                             stop_gross=sg, stop_funding=sf, stop_funding_rule="FLAT" if sflat else "REAL",
                             stop_net=sn, stop_R=sn / risk)
    row.update(stop_cols)
    return row


def tag_row(coin, row):
    """Add the source BULL/BEAR tag of the signal week (week d0/7 - 1)."""
    b = bull_flag(coin.wc, row["d0"] // 7 - 1)
    row["bull"] = "NA" if b is None else ("BULL" if b else "BEAR")
    return row


def event_trades(coin, fund=None):
    out = []
    for ev in events_dd20(coin):
        r = trade_at(coin, ev["d0"], fund)
        if r is not None:
            out.append(tag_row(coin, r))
    return out


def all_monday_trades(coin, fund=None):
    """Every Monday entry with a signal-eligible warm-up (week >= 8), for placebo and buy-and-hold baselines."""
    out = []
    for k in range(DD_LOOKBACK + 1, coin.nw + 1):
        r = trade_at(coin, 7 * k, fund)
        if r is not None:
            out.append(tag_row(coin, r))
    return out


# ---- phase read (MTS brain, descriptive only) ----
def phase_tag(table, entry_ms):
    """table: {'YYYY-MM-DD': (label, cycle, close_used)}. The brain builds the row of day d from closes through d-1,
    so the row of the entry day itself is the latest one that is free of entry-day information."""
    day = dt.datetime.fromtimestamp(entry_ms / 1000.0, dt.timezone.utc)
    r = table.get(day.strftime("%Y-%m-%d"))
    return (r[0], r[1]) if r else ("NA", "NA")


def phase_leak_count(table, closes):
    """closes: {'YYYY-MM-DD': close}. A row leaks if close_used equals the close of its OWN day and not the prior day's.
    Returns (checked, leaks)."""
    checked = leaks = 0
    for d, (_lab, _cyc, cu) in table.items():
        if cu is None or d not in closes:
            continue
        prev = (dt.datetime.strptime(d, "%Y-%m-%d") - dt.timedelta(days=1)).strftime("%Y-%m-%d")
        if prev not in closes:
            continue
        checked += 1
        if abs(cu - closes[d]) <= 1e-9 and abs(cu - closes[prev]) > 1e-9:
            leaks += 1
    return checked, leaks


# ---- loaders (used by t6_trades / t6_stats only; tests never call these on the real cache) ----
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


def load_phase_table(path):
    import csv
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            cu = r.get("close_used")
            out[r["date"]] = (r.get("label") or "NA", r.get("cycle") or "NA", float(cu) if cu else None)
    return out
