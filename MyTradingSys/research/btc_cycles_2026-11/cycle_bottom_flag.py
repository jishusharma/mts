"""Cycle-bottom long flag: one line per day (symbols over words). Rule: RULE.md in this folder.

  python MyTradingSys/research/btc_cycles_2026-11/cycle_bottom_flag.py [--csv btc_daily.csv] [--asof YYYY-MM-DD]

Only COMPLETED bars count (date < asof). Testnet only; the trade itself is operator-called (the operator-called testnet tool).
Labels: SOURCED = analyst row quoted from scripts/dev/analyst_levels.py output (CBP store); OURS = our choice.
"""
import argparse
import csv
import os
import sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

PEAK_DATE = date(2025, 10, 6)   # SOURCED cycles.md: cycle-4 peak 126,200
PEAK = 126_200.0
# SOURCED cycles.md: cycles 1-3 peak-to-bottom 406, 363, 376 days -> window = peak + min .. peak + max
WINDOW = (PEAK_DATE + timedelta(days=363), PEAK_DATE + timedelta(days=406))   # 2026-10-04 .. 2026-11-16
# SOURCED Krown 2026-11-05 (FVakIyoNcqc): "2-day close above 80,350 needed; 3-day close above 79,675; 5-day close above 80,450"
RECLAIM_5D = 80_450.0
# SOURCED Krown 2026-11-05 (FVakIyoNcqc): "75,000 weekly close is his line in the sand"
WEEKLY_FLOOR = 75_000.0
SOURCE_ROWS = {RECLAIM_5D: "2-day close above 80,350 needed; 3-day close above 79,675; 5-day close above 80,450",
               WEEKLY_FLOOR: "75,000 weekly close is his line in the sand"}
# OURS: retest zone = low within 2 % above the reclaimed level, daily close at or above it; stop 1 % under the retest swing low;
# default leverage 2x (testnet, operator may change); 5-day blocks anchored at 1970-01-01 (the analyst's anchor is unstated).
ZONE_PCT = 2.0
STOP_BELOW_PCT = 1.0
LEVERAGE = 2
# SOURCED BIBLE.md (mts_bible, row 4 + "Breaks it"): the 2026-07-01 low 57,800 is the bottom unless a new low under 57,800 prints.
# OURS: after the clock window the same 5d + weekly gates confirm only while no completed daily low since the peak is under it.
BOTTOM_LOW = 57_800.0
EXIT_LEVEL = RECLAIM_5D   # exit: weekly close back below the reclaimed level (OURS, card step 2)


def load(path=None):
    path = path or os.path.join(HERE, "btc_daily.csv")
    with open(path, newline="") as f:
        return [dict(d=date.fromisoformat(r["date"]), h=float(r["high"]), l=float(r["low"]), c=float(r["close"]))
                for r in csv.DictReader(f)]


def weekly_closes(rows, asof):
    """{sunday: close} for Monday-Sunday UTC weeks fully completed before asof."""
    return {r["d"]: r["c"] for r in rows if r["d"].weekday() == 6 and r["d"] < asof}


def block_closes(rows, asof, n=5):
    """{last_day: close} for n-day blocks (anchored 1970-01-01) whose last day is before asof."""
    out = {}
    for r in rows:
        idx = (r["d"] - date(1970, 1, 1)).days
        if idx % n == n - 1 and r["d"] < asof:
            out[r["d"]] = r["c"]
    return out


def state(rows, asof):
    """Walk completed days in order: WAIT -> CONFIRMED (5-day close > reclaim, last weekly close >= floor, inside window)
    -> IN (retest of reclaimed level held on a daily close) -> back to WAIT with exit_day set (weekly close below reclaim).
    A weekly close below the reclaim before entry voids CONFIRMED back to WAIT."""
    done = [r for r in rows if r["d"] < asof]
    wk = weekly_closes(rows, asof)
    b5 = block_closes(rows, asof)
    st = dict(state="WAIT", confirmed_on=None, entry_day=None, entry=None, stop=None, exit_day=None)
    last_wk = None
    zone_top = RECLAIM_5D * (1 + ZONE_PCT / 100)
    streak_low = None
    min_low = None
    for r in done:
        d = r["d"]
        if d >= PEAK_DATE:
            min_low = r["l"] if min_low is None else min(min_low, r["l"])
        if d in wk:
            last_wk = wk[d]
            if st["state"] == "CONFIRMED" and last_wk < EXIT_LEVEL:
                st.update(state="WAIT", confirmed_on=None)
            elif st["state"] == "IN" and last_wk < EXIT_LEVEL:
                st.update(state="WAIT", exit_day=d, prev_entry_day=st["entry_day"], entry_day=None, entry=None,
                          stop=None, confirmed_on=None)  # re-armed: a new confirmation is needed
        if st["state"] == "WAIT" and d in b5 and b5[d] > RECLAIM_5D \
                and (WINDOW[0] <= d <= WINDOW[1] or (d > WINDOW[1] and min_low is not None and min_low >= BOTTOM_LOW)) \
                and last_wk is not None and last_wk >= WEEKLY_FLOOR:
            st.update(state="CONFIRMED", confirmed_on=d)
            streak_low = None
            continue
        if st["state"] == "CONFIRMED" and d > st["confirmed_on"]:
            if r["l"] <= zone_top:
                streak_low = r["l"] if streak_low is None else min(streak_low, r["l"])
                if r["c"] >= RECLAIM_5D:
                    st.update(state="IN", entry_day=d, entry=r["c"], stop=round(streak_low * (1 - STOP_BELOW_PCT / 100), 2))
            else:
                streak_low = None
    st["last_weekly"] = last_wk
    st["last_5d"] = b5[max(b5)] if b5 else None
    st["in_window"] = WINDOW[0] <= asof <= WINDOW[1]
    return st


def flag_line(rows, asof=None):
    if asof is None:
        asof = datetime.now(timezone.utc).date()
    s = state(rows, asof)
    px = max((r for r in rows if r["d"] <= asof), key=lambda r: r["d"])["c"]
    day = (asof - PEAK_DATE).days
    dd = (px / PEAK - 1) * 100
    yes = lambda b: "Y" if b else "n"  # noqa: E731
    c5 = s["last_5d"] is not None and s["last_5d"] > RECLAIM_5D
    cw = s["last_weekly"] is not None and s["last_weekly"] >= WEEKLY_FLOOR
    head = "CYCLE4 d%d [%d-%d]%s dd%+.1f%% | 5d>%s %s | wk>=%s %s | " % (
        day, (WINDOW[0] - PEAK_DATE).days, (WINDOW[1] - PEAK_DATE).days, "" if s["in_window"] else " OUT",
        dd, format(RECLAIM_5D, ",.0f"), yes(c5), format(WEEKLY_FLOOR, ",.0f"), yes(cw))
    lo, hi = RECLAIM_5D, RECLAIM_5D * (1 + ZONE_PCT / 100)
    if s["state"] == "WAIT":
        tail = "WAIT (no bottom confirm) | zone if confirmed %s-%s" % (format(lo, ",.0f"), format(hi, ",.0f"))
    elif s["state"] == "CONFIRMED":
        tail = "CONFIRMED %s | BUY ZONE %s-%s (daily close >= %s) | lev %dx testnet" % (
            s["confirmed_on"], format(lo, ",.0f"), format(hi, ",.0f"), format(lo, ",.0f"), LEVERAGE)
    elif s["state"] == "IN":
        tail = "ENTRY OK %s @%s stop %s lev %dx | exit: weekly close < %s" % (
            s["entry_day"], format(s["entry"], ",.0f"), format(s["stop"], ",.0f"), LEVERAGE, format(EXIT_LEVEL, ",.0f"))
    else:
        tail = "?"
    if s["state"] == "WAIT" and s.get("exit_day"):
        tail += " | last trade exited %s (weekly close < %s)" % (s["exit_day"], format(EXIT_LEVEL, ",.0f"))
    return head + tail


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--asof", type=date.fromisoformat)
    a = ap.parse_args(argv)
    print(flag_line(load(a.csv), a.asof))


if __name__ == "__main__":
    sys.exit(main())
