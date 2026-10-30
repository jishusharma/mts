"""US cash-open countdown line (T054 step 5 / N3). CONTEXT ONLY: it never gates, filters or sizes a trade.

Pure functions, stdlib only, no clock reads (the caller passes `now`). A dashboard imports it later:
    from us_open_alert import us_open_line
    line = us_open_line(datetime.now(timezone.utc))   # None when nothing to show

US cash open = 09:30 America/New_York = 13:30 UTC in US daylight time (EDT), 14:30 UTC in winter (EST).
DST rule (US since 2007, SOURCED: federal law): starts 2nd Sunday of March 02:00 EST (07:00 UTC),
ends 1st Sunday of November 02:00 EDT (06:00 UTC). Computed by hand so Windows without tzdata works.
Not handled: NYSE holidays and half days (pass `holidays` as a set of dates to skip them). The 60-minute
window is OURS (display choice, not a trading parameter).
"""
from datetime import date, datetime, timedelta, timezone

WINDOW_MIN = 60  # OURS: show the line only when the open is within this many minutes


def _nth_sunday(year, month, n):
    d = date(year, month, 1)
    first = d + timedelta(days=(6 - d.weekday()) % 7)
    return first + timedelta(weeks=n - 1)


def is_us_dst(utc_dt):
    """True while US Eastern is on daylight time at the given UTC instant."""
    y = utc_dt.year
    start = datetime(y, 3, _nth_sunday(y, 3, 2).day, 7, tzinfo=timezone.utc)
    end = datetime(y, 11, _nth_sunday(y, 11, 1).day, 6, tzinfo=timezone.utc)
    return start <= utc_dt < end


def open_utc(day):
    """UTC datetime of the 09:30 ET cash open on calendar date `day`."""
    # DST state at the open itself (the switch is Sunday 02:00, so any weekday open is unambiguous)
    probe = datetime(day.year, day.month, day.day, 13, 30, tzinfo=timezone.utc)
    hour = 13 if is_us_dst(probe) else 14
    return datetime(day.year, day.month, day.day, hour, 30, tzinfo=timezone.utc)


def next_open(now, holidays=frozenset()):
    """First weekday cash open strictly after `now` (aware UTC datetime)."""
    now = now.astimezone(timezone.utc)
    d = now.date()
    for _ in range(14):
        if d.weekday() < 5 and d not in holidays:
            o = open_utc(d)
            if o > now:
                return o
        d += timedelta(days=1)
    raise ValueError("no open found")


def us_open_line(now, window_min=WINDOW_MIN, holidays=frozenset()):
    """'US open in N min (HH:MM UTC)' when 0 < N <= window_min, else None. Context only."""
    o = next_open(now, holidays)
    mins = int((o - now.astimezone(timezone.utc)).total_seconds() // 60)
    # ceil so "in 1 min" holds until the open; seconds remainder rounds up
    if (o - now.astimezone(timezone.utc)).total_seconds() % 60:
        mins += 1
    if mins < 1 or mins > window_min:
        return None
    return "US open in %d min (%s UTC) - context only" % (mins, o.strftime("%H:%M"))
