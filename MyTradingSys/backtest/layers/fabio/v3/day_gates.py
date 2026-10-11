"""Fabio v3 day rules and gates (FABIO_V3_SPEC.md section 6 and the section 2 calendar/window conventions).

Pure functions over dates, numbers and bar lists. No state: the CALLER owns the day's closed trades and passes
closed_nets / n_first_legs / carry in. Provenance labels (spec 7.1 ids) sit next to each rule.
"""
import datetime as dt
import math
import statistics

from .costs import MIN_MS

WINDOW_BARS = 390        # P33 SIM: NY window = 390 one-minute bars (spec section 2)
ENTRY_CUTOFF = 330       # P33 NS-fixed: no new entries at or after open+330 (spec section 2)
MAX_MISSING = 5          # P41 SIM: a session window with > 5 missing minutes is excluded (spec section 1)
MAX_FIRST_LEGS = 10      # P30 SAFETY: max 10 first legs per day (value NO-SOURCE, safety-exempt)
DAILY_STOP_R = -3.0      # P29 SAFETY: daily stop -3R (value NO-SOURCE, safety-exempt; fZ:79-81 only the idea)
RECOVERY_LEVEL_R = -1.0  # P28 NS-fixed: "-1R" level of the stop-after-recovery rule (concept ja:181-182)
GATE_PRIOR_DAYS = 20     # P40 NS-grid family: prior 20 valid weekdays for the day gate (concept 8C:85-87)
GATE_MIN_ELAPSED = 60    # P40: day gate closed before open+60 when g != off
TREND_RATIO = 0.6        # P41 SIM: ex-post day type trend iff |c_last-o_first|/(Hwin-Lwin) >= 0.6 (reporting only)
Z_POWER = 1.96 + 0.8416  # P41 SIM, spec section 8: n = ((1.96 + 0.8416) * SD / delta)^2

# P34 SIM (operator decision): NYSE full closures and 13:00 ET early closes, spec section 2 :46-48.
# Dates to VERIFY on desktop against the NYSE calendar (spec :46).
US_CLOSED = frozenset(dt.date(y, m, d) for (y, m, d) in (
    (2024, 12, 24), (2024, 12, 25),
    (2025, 1, 1), (2025, 1, 9), (2025, 1, 20), (2025, 2, 17), (2025, 4, 18), (2025, 5, 26), (2025, 6, 19),
    (2025, 7, 3), (2025, 7, 4), (2025, 9, 1), (2025, 11, 27), (2025, 11, 28), (2025, 12, 24), (2025, 12, 25),
    (2026, 1, 1), (2026, 1, 19), (2026, 2, 16), (2026, 4, 3), (2026, 5, 25), (2026, 6, 19), (2026, 7, 3),
    (2026, 9, 7), (2026, 11, 26), (2026, 11, 27), (2026, 12, 24), (2026, 12, 25)))


# ---------------------------------------------------------------- calendar
def _nth_sunday(year, month, n):
    d = dt.date(year, month, 1)
    first = d + dt.timedelta(days=(6 - d.weekday()) % 7)      # weekday(): Mon 0 .. Sun 6
    return first + dt.timedelta(days=7 * (n - 1))


def _last_sunday(year, month):
    nxt = dt.date(year + (month == 12), month % 12 + 1, 1)
    last = nxt - dt.timedelta(days=1)
    return last - dt.timedelta(days=(last.weekday() + 1) % 7)


def us_dst(date):
    """US DST in force iff second Sunday of March <= D < first Sunday of November (spec section 2)."""
    return _nth_sunday(date.year, 3, 2) <= date < _nth_sunday(date.year, 11, 1)


def uk_bst(date):
    """UK BST iff last Sunday of March <= D < last Sunday of October (spec section 2, London window)."""
    return _last_sunday(date.year, 3) <= date < _last_sunday(date.year, 10)


def _utc(date, hour, minute):
    return dt.datetime(date.year, date.month, date.day, hour, minute, tzinfo=dt.timezone.utc)


def ny_open_utc(date):
    """NY cash open for a UTC date: 13:30 UTC in US DST else 14:30; None on Sat/Sun and on US_CLOSED (spec section 2)."""
    if date.weekday() >= 5 or date in US_CLOSED:
        return None
    return _utc(date, 13, 30) if us_dst(date) else _utc(date, 14, 30)


def london_open_utc(date):
    """London window open (stage 3): 07:00 UTC in UK BST else 08:00, Mon-Fri; UK holidays NOT excluded (spec section 2)."""
    if date.weekday() >= 5:
        return None
    return _utc(date, 7, 0) if uk_bst(date) else _utc(date, 8, 0)


def asia_open_utc(date):
    """Asia window open (stage 3): 00:00 UTC (spec section 2: 'Asia: 00:00 UTC, 390 bars'; weekday rule not stated)."""
    return _utc(date, 0, 0)


def entry_allowed(i, open_idx):
    """No new entries (first legs or adds) at or after open+330 (spec section 2). i is the DECISION bar."""
    return (i - open_idx) < ENTRY_CUTOFF


def window_bars(bars, date, session="ny"):
    """The 390 one-minute bars [open, open+390 min) of `session` on `date`, or None if the day is excluded.

    Excluded (spec section 1): no window that day (weekend / US_CLOSED for ny), any bar of the window with
    thr_days == 0 (own-day thresholds = look-ahead), or more than 5 missing minutes in the window.
    """
    opener = {"ny": ny_open_utc, "london": london_open_utc, "asia": asia_open_utc}[session]
    op = opener(date)
    if op is None:
        return None
    t0 = int(op.timestamp() * 1000)
    t1 = t0 + WINDOW_BARS * MIN_MS
    win = [b for b in bars if t0 <= b["t"] < t1]
    if WINDOW_BARS - len(win) > MAX_MISSING:
        return None
    if any(b.get("thr_days", 0) == 0 for b in win):
        return None
    return win


# ---------------------------------------------------------------- day R and first-leg rules
def aggregate_day_r(days, trades):
    """Day R per day in `days` order: sum over the day's trades of risk_u * net_r (risk_u default 1.0); none -> 0.0."""
    out = []
    for d in days:
        out.append(math.fsum(t.get("risk_u", 1.0) * t["net_r"] for t in trades if t["day"] == d))
    return out


def _prefix(closed_nets, carry):
    p = [0.0, float(carry)]
    for n in closed_nets:
        p.append(p[-1] + n)
    return p


def first_leg_allowed(closed_nets, n_first_legs=0, carry=0.0):
    """Spec section 6: False iff any of
      n_first_legs >= 10 (P30 SAFETY); C <= -3 (P29 SAFETY); some P_k <= -1 and a later P_m >= 0 (P28, stop after
      recovery); peak > 0 and C <= 0 (P26, floor at 0), with prefix sums P = [0, carry, carry+n1, ...], C = last.
    Open trades keep being managed regardless (that is the caller's concern).
    """
    if n_first_legs >= MAX_FIRST_LEGS:
        return False
    p = _prefix(closed_nets, carry)
    c, peak = p[-1], max(p)
    if c <= DAILY_STOP_R:
        return False
    for k in range(len(p)):
        if p[k] <= RECOVERY_LEVEL_R and any(p[m] >= 0 for m in range(k + 1, len(p))):
            return False
    if peak > 0 and c <= 0:
        return False
    return True


def first_leg_risk(closed_nets, n_first_legs=0, carry=0.0):
    """Spec section 6 (v3.1): 0 if first legs are not allowed; else min(1, C) if peak > 0; else 1 (P27 carry / risk <= C)."""
    if not first_leg_allowed(closed_nets, n_first_legs, carry):
        return 0.0
    p = _prefix(closed_nets, carry)
    if max(p) > 0:
        return min(1.0, p[-1])
    return 1.0


# ---------------------------------------------------------------- volatility gate / reporting helpers
def day_gate_open(elapsed, day_range, prior_ranges, g):
    """Day gate for models A and C (spec section 6, P40): at bar i >= open+60, G = day_range / median(prior ranges of
    the same elapsed minutes over the prior 20 valid weekdays); open iff G >= g. g None / 'off' -> always open.
    elapsed = i - open_idx. Fail closed: no prior ranges, or a median <= 0, means G is undefined -> closed.
    """
    if g is None or g == "off":
        return True
    if elapsed < GATE_MIN_ELAPSED:
        return False
    pr = list(prior_ranges)[-GATE_PRIOR_DAYS:]
    if not pr:
        return False
    med = statistics.median(pr)
    if not med > 0:
        return False
    return day_range / med >= g - 1e-12


def day_type(bars):
    """Ex-post day type, REPORTING ONLY (spec section 6): trend iff |c_last - o_first| / (Hwin - Lwin) >= 0.6, else balance."""
    hi, lo = max(b["h"] for b in bars), min(b["l"] for b in bars)
    rng = hi - lo
    if not rng > 0:
        return "balance"
    return "trend" if abs(bars[-1]["c"] - bars[0]["o"]) / rng >= TREND_RATIO else "balance"


def sample_size(sd, delta):
    """n = ceil(((1.96 + 0.8416) * SD / delta)^2) (spec section 8)."""
    return int(math.ceil((Z_POWER * sd / delta) ** 2 - 1e-9))


def ci_halfwidth(sd, n):
    """95% CI half-width 1.96 * SD / sqrt(n) (spec section 8; n 30, SD 1.5 -> 0.537R)."""
    return 1.96 * sd / math.sqrt(n)
