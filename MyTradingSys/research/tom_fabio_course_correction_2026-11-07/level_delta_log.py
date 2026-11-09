"""Offline logger: real 1m order-flow delta around each level reclaim in London/NY (Fabio absorption-then-aggression).

No daemon, no scheduler, no order, no exchange write. Public Binance USD-M data only (klines + aggTrades via
orderflow_live.run_cycle into a scratch dir; orderflow_live.py is NOT edited). One --once run = one fetch cycle (resumable
by minute, state in the scratch dir) + detection + append. Re-run to progress the backfill.

Labels: SOURCED = taken from a cited source; OURS = our choice, to be tested.
  Range edges 75,400 / 80,900   SOURCED  MyTradingSys/research/mts_bible/BIBLE.md:28 (card: BIBLE s2)
  PDH / PDL as levels, reclaim = probe beyond the level then a 5m close back inside   SOURCED  POSTMORTEM_OPUS.md section 3
  max_bars = 3 (close back inside within 3 bars of the probe start, same bar counts)   OURS
  delta window = 15 min up to the reclaim close, plus the 5 min reclaim bar   OURS
  Sessions logged: london (UTC 07-12) and ny (UTC 12-21), same blocks as forward_log.session_block   OURS
  A window minute with no order-flow row = None, never 0 (fail closed)   OURS
  Events whose 15 min window starts before the fetch start or ends after the fetched-through minute are not logged   OURS
A decision at bar t reads only bars <= t: the reclaim ts is the close of the reclaim bar; delta uses minutes < ts.
Output (gitignored, never commit): runtime/LEVEL_DELTA_LOG.csv and runtime/of_scratch/ next to this file.
Run: python MyTradingSys/research/tom_fabio_course_correction_2026-11-07/level_delta_log.py --once --levels 75400 80900
"""
import argparse
import csv
import json
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

COLUMNS = ["ts", "level", "kind", "side", "session", "delta_15m", "delta_bar", "cvd_chg"]
M1, M5, DAY = 60000, 300000, 86400000
RANGE_LEVELS = (75400.0, 80900.0)   # SOURCED BIBLE.md:28
MAX_BARS = 3                        # OURS
WIN_MIN = 15                        # OURS
LOGGED_SESSIONS = ("london", "ny")  # OURS
RUNTIME = Path(__file__).resolve().parent / "runtime"
DEFAULT_LOG = RUNTIME / "LEVEL_DELTA_LOG.csv"
DEFAULT_SCRATCH = RUNTIME / "of_scratch"
KLINES = "https://fapi.binance.com/fapi/v1/klines"


def session_block(ts_ms):
    h = (int(ts_ms) // 3600000) % 24
    return "asia" if h < 7 else "london" if h < 12 else "ny" if h < 21 else "late"


def find_reclaims(bars5m, levels, max_bars=MAX_BARS):
    """bars5m: ascending dicts t(open ms),h,l,c. levels: [(price, kind)]; kind range_hi / pdh = resistance
    (probe above, close back below, side short); otherwise support (probe below, close back above, side long).
    A probe starts at the first bar of an excursion (previous close inside); it is a reclaim if some bar within max_bars
    of the start (same bar included) closes back inside. Logged only in LOGGED_SESSIONS. Uses bars <= the reclaim bar."""
    out = []
    for price, kind in levels:
        res = kind in ("range_hi", "pdh")
        i, n = 1, len(bars5m)
        while i < n:
            b, prev = bars5m[i], bars5m[i - 1]
            beyond = b["h"] > price if res else b["l"] < price
            fresh = prev["c"] <= price if res else prev["c"] >= price
            if not (beyond and fresh):
                i += 1
                continue
            hit = None
            for j in range(i, min(i + max_bars, n)):
                if (bars5m[j]["c"] <= price) if res else (bars5m[j]["c"] >= price):
                    hit = j
                    break
            if hit is None:
                i += max_bars   # knife: no reclaim; skip past the window
                continue
            ts = bars5m[hit]["t"] + M5
            sess = session_block(ts - 1)
            if sess in LOGGED_SESSIONS:
                seg = bars5m[i:hit + 1]
                out.append({"ts": ts, "level": float(price), "kind": kind, "side": "short" if res else "long",
                            "session": sess, "extreme": max(x["h"] for x in seg) if res else min(x["l"] for x in seg)})
            i = hit + 1
    return sorted(out, key=lambda e: (e["ts"], e["level"]))


def delta_at(of_bars_1m, ts, win_min=WIN_MIN):
    """Sum of 1m delta over the win_min minutes up to ts (minutes [ts-win, ts)), the 5 min reclaim bar, and the cvd change
    over the window. Any absent minute -> that field None (never 0). cvd_chg = cvd_day(last) - (cvd_day(first) - delta(first));
    None if the window crosses a UTC day (cvd_day restarts)."""
    by_t = {int(b["t"]): b for b in of_bars_1m}

    def total(n):
        ts_list = [ts - k * M1 for k in range(n, 0, -1)]
        if any(t not in by_t for t in ts_list):
            return None, None
        return sum(by_t[t]["delta"] for t in ts_list), ts_list

    d15, win = total(win_min)
    dbar, _ = total(5)
    cvd = None
    if win is not None and win[0] // DAY == win[-1] // DAY:
        first, last = by_t[win[0]], by_t[win[-1]]
        cvd = last["cvd_day"] - (first["cvd_day"] - first["delta"])
    return {"delta_15m": d15, "delta_bar": dbar, "cvd_chg": cvd}


def append_rows(path, rows):
    """Append rows (dict by COLUMNS; None -> empty), dedupe on ts+level. Returns rows written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if path.exists() and path.stat().st_size:
        with open(path, "r", newline="", encoding="utf-8") as f:
            seen = {(r["ts"], float(r["level"])) for r in csv.DictReader(f)}
    new = not path.exists() or path.stat().st_size == 0
    n = 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(COLUMNS)
        for r in rows:
            k = (str(r["ts"]), float(r["level"]))
            if k in seen:
                continue
            seen.add(k)
            w.writerow(["" if r.get(c) is None else r[c] for c in COLUMNS])
            n += 1
    return n


def pd_levels(daily):
    """{utc_day_ms: (pdh, pdl)} from daily klines [{t,h,l}]: the PRIOR day's extremes apply to the next day."""
    return {b["t"] + DAY: (b["h"], b["l"]) for b in sorted(daily, key=lambda x: x["t"])}


def fetch_klines(interval, start_ms, end_ms, limit=1500):
    from MyTradingSys.runtime.binance_doh import urlopen
    q = {"symbol": "BTCUSDT", "interval": interval, "startTime": start_ms, "endTime": end_ms, "limit": limit}
    with urlopen(KLINES + "?" + urllib.parse.urlencode(q), timeout=15) as r:
        rows = json.loads(r.read())
    return [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])} for k in rows]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--once", action="store_true", required=True, help="one fetch cycle + detect + append; no daemon")
    ap.add_argument("--levels", type=float, nargs="*", default=list(RANGE_LEVELS))
    ap.add_argument("--hours", type=int, default=24, help="lookback for the 5m bars / order-flow backfill")
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    ap.add_argument("--scratch", default=str(DEFAULT_SCRATCH))
    a = ap.parse_args(argv)
    from MyTradingSys.backtest.layers.fabio import orderflow_live as ofl
    now = int(time.time() * 1000)
    start = (now - a.hours * 3600000) // M1 * M1
    rng_hi, rng_lo = (max(a.levels), min(a.levels)) if a.levels else (None, None)
    bars = [b for b in fetch_klines("5m", start - M5 * 5, now) if b["t"] + M5 <= now]   # closed bars only
    daily = pd_levels(fetch_klines("1d", (start // DAY - 2) * DAY, now))
    res = ofl.run_cycle(a.scratch, ofl.default_fetch, since_ms=start, now_ms=now, hist_dirs=[Path(a.scratch) / "_qhist"])
    through = res["next_ms"]
    of_bars = ofl.load_live_bars(a.scratch, since_ms=start)
    events = []
    for day in sorted({b["t"] // DAY * DAY for b in bars}):
        lv = [(p, k) for p, k in ((rng_hi, "range_hi"), (rng_lo, "range_lo")) if p is not None]
        if day in daily:
            lv += [(daily[day][0], "pdh"), (daily[day][1], "pdl")]
        events += find_reclaims([b for b in bars if b["t"] // DAY * DAY == day], lv)
    rows = []
    for e in events:
        if e["ts"] - WIN_MIN * M1 < start or e["ts"] > through:
            continue   # window not (yet) covered by the fetch
        rows.append({**e, **delta_at(of_bars, e["ts"])})
    n = append_rows(a.log, rows)
    print(f"events={len(events)} eligible={len(rows)} appended={n} "
          f"of_through={datetime.fromtimestamp(through / 1000, timezone.utc):%Y-%m-%d %H:%M}Z fetch_error={res['error']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
