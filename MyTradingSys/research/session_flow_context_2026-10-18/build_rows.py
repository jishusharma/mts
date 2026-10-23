"""Per-session flow rows for BTCUSDT perp (ASIA/LDN/US/LATE), as-of features + next-session outcome.

Definitions are frozen in PRE_REG.md (read it first). Every threshold is labelled there SOURCED or OURS.
Only DEV rows can be selected; VALIDATION / HOLDOUT raise PermissionError (sealed until the PRE_REG says so).

  python MyTradingSys/research/session_flow_context_2026-10-18/build_rows.py [--raw <dir>] [--out rows_dev.csv]
"""
import argparse
import bisect
import csv
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest" / "bt"))
import bt_data  # noqa: E402

MIN = 60000
HOUR = 3600000
DAY = 86400000
NAN = float("nan")

# ---- session split: UTC 00:00 / 08:00 / 13:30 / 20:00 (OURS) ----
SESSIONS = (("ASIA", 0, 8 * 60), ("LDN", 8 * 60, 13 * 60 + 30), ("US", 13 * 60 + 30, 20 * 60), ("LATE", 20 * 60, 24 * 60))

# ---- context parameters (all OURS unless marked; see PRE_REG.md s.3) ----
HTF_WIN_DAYS = 30           # trailing return window; threshold below is SOURCED (backtest/tom_bt.py:290 trend_tag thr=0.075)
HTF_THR = 0.075             # SOURCED: repo code MyTradingSys/backtest/tom_bt.py:290 (not the trader's words)
RANGE_DAYS = 15             # OURS: middle of the operator's "10-20d range"
RANGE_LO, RANGE_HI = 1 / 3, 2 / 3   # OURS terciles
VOL_HIST = 20               # OURS: previous 20 same-name sessions
VOL_MIN_HIST = 10           # OURS
VOL_LO, VOL_HI = 1 / 3, 2 / 3       # OURS
OI_TREND_DAYS = 5           # OURS
OI_TREND_THR = 0.02         # OURS dead band +/-2 %
OI_MAX_AGE = 10 * MIN       # OURS: an OI sample older than 10 min is NOT_IN_DATA
SR_LOOKBACK = DAY           # OURS: prior 24 h high/low
COVER_MIN = 0.90            # OURS: a session needs >= 90 % of its 1m bars

# ---- splits by session start date (OURS, fixed before any outcome read) ----
SPLIT_EDGES = (("WARMUP", "2025-09-01", "2025-09-30"), ("DEV", "2025-10-01", "2026-02-28"),
               ("VALIDATION", "2026-03-01", "2026-06-30"), ("HOLDOUT", "2026-07-01", "2099-12-31"))


def split_of(date_str):
    for name, a, b in SPLIT_EDGES:
        if a <= date_str <= b:
            return name
    return "OUT"


def select_split(rows, split="DEV"):
    if split != "DEV":
        raise PermissionError("%s is sealed: PRE_REG.md s.8 allows exactly one VALIDATION read after the DEV table, HOLDOUT once after that" % split)
    return [r for r in rows if split_of(r["date"]) == "DEV"]


def day_start_ms(ms):
    return ms - ms % DAY


def session_bounds(day_ms):
    return [(n, day_ms + a * MIN, day_ms + b * MIN) for n, a, b in SESSIONS]


def session_stats(bars):
    o, c = bars[0]["o"], bars[-1]["c"]
    h = max(b["h"] for b in bars)
    l = min(b["l"] for b in bars)
    vol = sum(b["v"] for b in bars)
    delta = sum(2 * b["tbv"] - b["v"] for b in bars)       # FORMULAS.md s.14 / bt_data.cvd_delta
    return {"o": o, "c": c, "h": h, "l": l, "vol": vol, "delta": delta,
            "delta_norm": delta / vol if vol else NAN,
            "chg_bps": (c / o - 1) * 1e4, "range_pct": (h - l) / o}


def oi_at(oi_t, oi_v, t):
    """Latest OI sample with sample time <= t and age <= OI_MAX_AGE, else NaN (never 0)."""
    i = bisect.bisect_right(oi_t, t) - 1
    if i < 0 or t - oi_t[i] > OI_MAX_AGE:
        return NAN
    return oi_v[i]


def oi_chg(oi_t, oi_v, t0, t1):
    a, b = oi_at(oi_t, oi_v, t0), oi_at(oi_t, oi_v, t1)
    if math.isnan(a) or math.isnan(b) or a == 0:
        return NAN
    return b / a - 1


def quadrant(chg_bps, oi_change):
    if oi_change is None or math.isnan(oi_change) or chg_bps == 0 or oi_change == 0:
        return "NA"
    if chg_bps > 0:
        return "NEW_LONG" if oi_change > 0 else "SHORT_COVER"
    return "NEW_SHORT" if oi_change > 0 else "LONG_LIQ"


def sweep_reclaim(h, l, c, prior_h, prior_l):
    bear = h > prior_h and c < prior_h
    bull = l < prior_l and c > prior_l
    if bear and bull:
        return "BOTH"
    return "SR_BEAR" if bear else ("SR_BULL" if bull else "NONE")


def htf_bucket(ret30):
    if ret30 is None or math.isnan(ret30):
        return "NA"
    return "UP" if ret30 > HTF_THR else ("DOWN" if ret30 < -HTF_THR else "BALANCE")


def rangepos_bucket(x):
    if x is None or math.isnan(x):
        return "NA"
    return "LOW" if x < RANGE_LO else ("HIGH" if x > RANGE_HI else "MID")


def vol_pct(x, hist):
    if len(hist) < VOL_MIN_HIST:
        return NAN
    return sum(1 for v in hist if v <= x) / len(hist)


def vol_bucket(p):
    if p is None or math.isnan(p):
        return "NA"
    return "LOW" if p <= VOL_LO else ("HIGH" if p >= VOL_HI else "MID")


def oitrend_bucket(x):
    if x is None or math.isnan(x):
        return "NA"
    return "UP" if x > OI_TREND_THR else ("DOWN" if x < -OI_TREND_THR else "FLAT")


def weekday_bucket(start_ms):
    wd = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).weekday()   # Mon=0
    return "WEEKEND" if wd >= 5 else "WEEKDAY"


def build_rows(bars, oi_t, oi_v):
    """All sessions found in `bars` (list of {'t','o','h','l','c','v','tbv'} sorted by t). Features use bars with
    t + 1m <= session end only; `next_*` columns are the outcome (the following session)."""
    if not bars:
        return []
    t = np.array([b["t"] for b in bars], dtype=np.int64)
    O = np.array([b["o"] for b in bars]); H = np.array([b["h"] for b in bars]); L = np.array([b["l"] for b in bars])
    C = np.array([b["c"] for b in bars])
    rows, hist = [], {n: [] for n, _, _ in SESSIONS}
    d = day_start_ms(int(t[0]) + DAY - 1)          # first full day
    last_day = day_start_ms(int(t[-1]))
    while d <= last_day:
        for name, s, e in session_bounds(d):
            i, j = int(np.searchsorted(t, s)), int(np.searchsorted(t, e))
            if j - i < COVER_MIN * (e - s) / MIN:
                continue
            st = session_stats(bars[i:j])
            # HTF 30d return as of e
            i30 = int(np.searchsorted(t, e - HTF_WIN_DAYS * DAY))
            ret30 = C[j - 1] / O[i30] - 1 if i30 < j and t[i30] - (e - HTF_WIN_DAYS * DAY) <= HOUR else NAN
            # range position inside the trailing RANGE_DAYS range as of e
            ir = int(np.searchsorted(t, e - RANGE_DAYS * DAY))
            if ir < j and t[ir] - (e - RANGE_DAYS * DAY) <= HOUR:
                hi, lo = H[ir:j].max(), L[ir:j].min()
                rpx = (C[j - 1] - lo) / (hi - lo) if hi > lo else NAN
            else:
                rpx = NAN
            # prior 24h sweep-reclaim
            ip = int(np.searchsorted(t, s - SR_LOOKBACK))
            sr = sweep_reclaim(st["h"], st["l"], st["c"], H[ip:i].max(), L[ip:i].min()) if i - ip >= COVER_MIN * 1440 else "NA"
            # vol percentile vs previous same-name sessions
            vp = vol_pct(st["range_pct"], hist[name][-VOL_HIST:])
            hist[name].append(st["range_pct"])
            oich = oi_chg(oi_t, oi_v, s - 1, e - 1)           # strictly before the boundary: the sample stamped at e is not yet known
            oitr = oi_chg(oi_t, oi_v, e - OI_TREND_DAYS * DAY - 1, e - 1)
            date = datetime.fromtimestamp(s / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            rows.append({
                "date": date, "session": name, "start_ms": s, "end_ms": e,
                "chg_bps": st["chg_bps"], "delta_norm": st["delta_norm"], "range_pct": st["range_pct"],
                "oi_chg": oich, "quadrant": quadrant(st["chg_bps"], oich), "delta_agree": int((st["delta"] > 0) == (st["chg_bps"] > 0)),
                "sr": sr,
                "ret30": ret30, "htf": htf_bucket(ret30),
                "rangepos_x": rpx, "rangepos": rangepos_bucket(rpx),
                "vol_pct": vp, "vol": vol_bucket(vp),
                "oitrend_x": oitr, "oitrend": oitrend_bucket(oitr),
                "wkend": weekday_bucket(s),
                "next_ret_bps": NAN, "next_range_pct": NAN,
            })
        d += DAY
    for a, b in zip(rows, rows[1:]):                # outcome = the immediately following session
        if b["start_ms"] == a["end_ms"]:
            a["next_ret_bps"], a["next_range_pct"] = b["chg_bps"], b["range_pct"]
    return rows


FIELDS = ["date", "session", "start_ms", "end_ms", "chg_bps", "delta_norm", "range_pct", "oi_chg", "quadrant", "delta_agree",
          "sr", "ret30", "htf", "rangepos_x", "rangepos", "vol_pct", "vol", "oitrend_x", "oitrend", "wkend",
          "next_ret_bps", "next_range_pct"]


def load_dev(raw):
    """Load ONLY data before the end of DEV (2026-03-01 00:00 UTC): the sealed splits are never read."""
    end_ms = int(datetime(2026, 3, 1, tzinfo=timezone.utc).timestamp() * 1000)
    start_ms = int(datetime(2025, 9, 1, tzinfo=timezone.utc).timestamp() * 1000)
    bars = bt_data.load_klines(raw, "klines", start_ms=start_ms, end_ms=end_ms)
    met = bt_data.load_metrics(raw, start_ms=start_ms, end_ms=end_ms)
    return bars, [m["t"] for m in met], [m["oi"] for m in met]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.environ.get("MTS_RAW", "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw"))
    ap.add_argument("--out", default=str(HERE / "rows_dev.csv"))
    a = ap.parse_args(argv)
    bars, oi_t, oi_v = load_dev(a.raw)
    rows = select_split(build_rows(bars, oi_t, oi_v), "DEV")
    with open(a.out, "w", newline="\n") as f:
        w = csv.DictWriter(f, FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (("%.10g" % r[k]) if isinstance(r[k], float) else r[k]) for k in FIELDS})
    print("bars %d, oi samples %d, DEV rows %d -> %s" % (len(bars), len(oi_t), len(rows), a.out))


if __name__ == "__main__":
    main()
