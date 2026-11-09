"""PHASE_LABEL: BTC cycle phase x last closed weekly RSI14 zone, from closed bars only (eh-o2-phase-lens, PRE_REG.md).

Pure functions. Inputs: daily bars as (t_open_ms, high, low, close), ascending, UTC days; halving dates (ms, day starts).
A daily bar is usable at time t only when t_open + 1 day <= t. A weekly RSI value is usable only at its week close
(Monday 00:00 UTC after the week). The cycles.csv turn dates are NOT inputs: peaks and bottoms are detected point in time.

Day counts SOURCED: BIBLE.md:8-10 and btc_cycles_2026-11/cycles.md:6-8,13 (halving to peak 372 / 526 / 548 d; peak to
bottom 406 / 363 / 376 d). RSI lines 40/60 SOURCED (Malkan; research_kit.py RSI_BULL/RSI_BEAR). Phase names, the
knowability rule (peak known 363 d after it with no new high; bottom known after a 100 % rally), TRANSITION and the
zone use are OURS (PRE_REG.md "Knowability rule").
"""
import bisect
import os
import sys
from datetime import datetime, timezone

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 5)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402  (read-only import)

DAY_MS = 86_400_000
WEEK_MS = 7 * DAY_MS


def _ms(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


# SOURCED cycles.csv / BIBLE.md:8-12; 2028-04-15 is the BIBLE.md:12 estimate (OURS there), only an end bound here.
HALVINGS = [_ms(2012, 11, 28), _ms(2016, 7, 9), _ms(2020, 5, 11), _ms(2024, 4, 20), _ms(2028, 4, 15)]
PEAK_WIN_LO, PEAK_WIN_HI = 372, 548       # SOURCED: halving -> peak, cycles 1-3 range
BOTTOM_WIN_LO, BOTTOM_WIN_HI = 363, 406   # SOURCED: peak -> bottom, cycles 1-3 range
PEAK_KNOWN_D = 363                        # OURS (brief): a peak is known 363 d later (start of the bottom window)
BOTTOM_RALLY_X = 2.0                      # OURS (brief): bottom known once a close is >= 2 x the low
RSI_N = 14                                # SOURCED (Malkan RSI14)
ZONE_HI, ZONE_LO = 60.0, 40.0             # SOURCED (Malkan 40/60)

PHASES = ("ACCUMULATION", "BULL", "PEAK_WINDOW", "BEAR", "BOTTOM_WINDOW", "TRANSITION")
ZONES = ("HIGH", "MID", "LOW")


def zone_of(rsi):
    if rsi is None:
        return None
    if rsi > ZONE_HI:
        return "HIGH"
    if rsi < ZONE_LO:
        return "LOW"
    return "MID"


def _day_floor(t):
    return (int(t) // DAY_MS) * DAY_MS


def _halving_ctx(D, halvings):
    i = bisect.bisect_right(halvings, D) - 1
    if i < 0:
        raise ValueError("t before the first halving in the list")
    nxt = halvings[i + 1] if i + 1 < len(halvings) else None
    return halvings[i], nxt


def _closed_since(daily, H, D):
    """Daily bars with H <= t_open < D (closed by day start D)."""
    return [b for b in daily if H <= b[0] < D]


def _peak_of(days):
    """(t_open, high) of the highest high; the first occurrence on ties."""
    best = None
    for b in days:
        if best is None or b[1] > best[1]:
            best = b
    return best


def peak_known(t, daily, halvings=HALVINGS):
    D = _day_floor(t)
    H, _ = _halving_ctx(D, halvings)
    pk = _peak_of(_closed_since(daily, H, D))
    return pk is not None and (D - pk[0]) >= PEAK_KNOWN_D * DAY_MS


def _bottom_known(after_peak):
    m = None
    for b in after_peak:
        if m is None or b[2] < m:
            m = b[2]
        if b[3] >= BOTTOM_RALLY_X * m:
            return True
    return False


def cycle_phase(t, daily, halvings=HALVINGS):
    """Reference (from-scratch, O(n^2)) cycle phase at time t, using only daily bars closed before the day of t.
    ACCUMULATION is sticky until the next halving (PRE_REG rule 3: "known bottom -> ACCUMULATION until Hn"), so a new
    high after a confirmed bottom (2024-03) does not reopen BEAR."""
    D = _day_floor(t)
    H, _ = _halving_ctx(D, halvings)
    since = _closed_since(daily, H, D)
    for Dp in range(H, D + 1, DAY_MS):
        if _raw_phase(Dp, H, [b for b in since if b[0] < Dp]) == "ACCUMULATION":
            return "ACCUMULATION"
    return _raw_phase(D, H, since)


def _raw_phase(D, H, days):
    dH = (D - H) // DAY_MS
    pk = _peak_of(days)
    known = pk is not None and (D - pk[0]) >= PEAK_KNOWN_D * DAY_MS
    if not (dH > PEAK_WIN_HI or known):
        return "BULL" if dH < PEAK_WIN_LO else "PEAK_WINDOW"
    if pk is None:
        return "BEAR"
    if _bottom_known([b for b in days if b[0] > pk[0]]):
        return "ACCUMULATION"
    d = (D - pk[0]) // DAY_MS
    if d < BOTTOM_WIN_LO:
        return "BEAR"
    if d <= BOTTOM_WIN_HI:
        return "BOTTOM_WINDOW"
    return "TRANSITION"


def daily_phase_series(daily, halvings=HALVINGS, start=None, end=None):
    """Incremental O(n) phase per UTC day start (from the first bar day to the last bar day + 1). Same rule as
    cycle_phase; returns (day_starts, phases)."""
    if not daily:
        return [], []
    d0 = _day_floor(start if start is not None else daily[0][0])
    d1 = _day_floor(end if end is not None else daily[-1][0] + DAY_MS)
    out_t, out_p = [], []
    j = 0  # next daily bar index not yet absorbed
    H = None
    acc = False        # sticky ACCUMULATION until the next halving
    pk = None          # (t_open, high)
    m = None           # running min low after the peak
    bknown = False
    for D in range(d0, d1 + 1, DAY_MS):
        h, _ = _halving_ctx(D, halvings)
        if h != H:
            H, pk, m, bknown, acc = h, None, None, False, False
            while j < len(daily) and daily[j][0] < H:
                j += 1
        while j < len(daily) and daily[j][0] < D:
            b = daily[j]
            j += 1
            if b[0] < H:
                continue
            if pk is None or b[1] > pk[1]:
                pk, m, bknown = (b[0], b[1]), None, False
                continue
            if m is None or b[2] < m:
                m = b[2]
            if b[3] >= BOTTOM_RALLY_X * m:
                bknown = True
        dH = (D - H) // DAY_MS
        known = pk is not None and (D - pk[0]) >= PEAK_KNOWN_D * DAY_MS
        if not (dH > PEAK_WIN_HI or known):
            ph = "BULL" if dH < PEAK_WIN_LO else "PEAK_WINDOW"
        elif pk is None:
            ph = "BEAR"
        elif bknown:
            ph = "ACCUMULATION"
        else:
            d = (D - pk[0]) // DAY_MS
            ph = "BEAR" if d < BOTTOM_WIN_LO else ("BOTTOM_WINDOW" if d <= BOTTOM_WIN_HI else "TRANSITION")
        if ph == "ACCUMULATION":
            acc = True
        if acc:
            ph = "ACCUMULATION"
        out_t.append(D)
        out_p.append(ph)
    return out_t, out_p


def _week_start(t):
    # 1970-01-01 was a Thursday; Monday-aligned weeks start 3 days later (1970-01-05).
    off = 4 * DAY_MS
    return ((int(t) - off) // WEEK_MS) * WEEK_MS + off


def weekly_rsi(daily, n=RSI_N):
    """Weekly RSI14 from daily closes, weeks Monday 00:00 UTC. Returns (usable_times, rsi): usable_time = week close."""
    wk, closes = [], []
    for b in daily:
        w = _week_start(b[0])
        if wk and wk[-1] == w:
            closes[-1] = b[3]
        else:
            wk.append(w)
            closes.append(b[3])
    rsi = rsi_core(closes, n) if len(closes) > n else [None] * len(closes)
    return [w + WEEK_MS for w in wk], rsi


def _month_start(t):
    d = datetime.fromtimestamp(int(t) / 1000, tz=timezone.utc)
    return _ms(d.year, d.month, 1)


def _next_month(ms_):
    d = datetime.fromtimestamp(ms_ / 1000, tz=timezone.utc)
    return _ms(d.year + (d.month == 12), d.month % 12 + 1, 1)


def monthly_rsi(daily, n=RSI_N):
    """Monthly RSI14 from daily closes. Returns (usable_times = month close, rsi)."""
    mo, closes = [], []
    for b in daily:
        m = _month_start(b[0])
        if mo and mo[-1] == m:
            closes[-1] = b[3]
        else:
            mo.append(m)
            closes.append(b[3])
    rsi = rsi_core(closes, n) if len(closes) > n else [None] * len(closes)
    return [_next_month(m) for m in mo], rsi


class PhaseLabeler:
    """Fast as-of lookups: phase(t), weekly_rsi_at(t), zone(t), label(t) -> (phase, zone)."""

    def __init__(self, daily, halvings=HALVINGS, weekly_daily=None):
        self.daily = daily
        self.halvings = halvings
        self.days, self.phases = daily_phase_series(daily, halvings)
        self.wt, self.wr = weekly_rsi(weekly_daily if weekly_daily is not None else daily)

    def phase(self, t):
        D = _day_floor(t)
        i = bisect.bisect_right(self.days, D) - 1
        if i < 0 or self.days[i] != D:
            return None
        return self.phases[i]

    def weekly_rsi_at(self, t):
        i = bisect.bisect_right(self.wt, t) - 1
        return None if i < 0 else self.wr[i]

    def zone(self, t):
        return zone_of(self.weekly_rsi_at(t))

    def label(self, t):
        return self.phase(t), self.zone(t)


def phase_label(t, daily, halvings=HALVINGS):
    """Pure one-shot PHASE_LABEL at time t: (cycle phase, weekly RSI zone), closed bars only."""
    closed = [b for b in daily if b[0] + DAY_MS <= t]
    wt, wr = weekly_rsi(closed) if closed else ([], [])
    i = bisect.bisect_right(wt, t) - 1
    return cycle_phase(t, daily, halvings), zone_of(None if i < 0 else wr[i])
