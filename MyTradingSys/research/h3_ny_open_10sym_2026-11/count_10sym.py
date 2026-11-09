"""h3_ny_open_10sym_2026-11: COUNT-ONLY of H3 events (NY-day low set at open+120..150 min, held >= 30 min) per symbol, DEV only.
Rule of research/h3_ny_open_low_2026-10/BLOCKED.md. Only lows and bar times are read; no return or outcome column exists here.
A symbol with no 1m DEV klines on disk is NOT_IN_DATA (never padded). Days with a missing minute in the window are dropped."""
import datetime as dt
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc  # noqa: E402

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "LTCUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT")
DATA_DIR = Path("F:/MTS/data/tom_raw")
MIN = 60000


def day_event(date, lows):
    """lows: {open_ms: low} of 1m bars. Returns True/False for an event, None when the day is not usable (no NY open or a gap)."""
    o = ny_open_utc(date)
    if o is None:
        return None
    start = int(dt.datetime(date.year, date.month, date.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
    end = int(o.timestamp() * 1000) + 180 * MIN                       # exclusive
    ts = range(start, end, MIN)
    if any(t not in lows for t in ts):
        return None
    low_t = min(ts, key=lambda t: (lows[t], t))                        # first bar at the day low
    off = (low_t - int(o.timestamp() * 1000)) // MIN
    return 120 <= off <= 150                                          # held >= 30 min: window runs to open+180, no lower low after


def load_lows(sym, lo_ms, hi_ms):
    lows = {}
    short = sym.replace("USDT", "").lower()
    candidate_dirs = [DATA_DIR / f"klines_{short}", DATA_DIR / "klines"]
    files = []
    for d in candidate_dirs:
        found = sorted(d.glob(f"{sym}-1m-20*.csv"))
        if found:
            files = found
            break
    for f in files:
        with open(f, encoding="utf-8") as fp:
            for line in fp:
                p = line.split(",")
                if p[0].isdigit() and lo_ms <= int(p[0]) < hi_ms:
                    lows[int(p[0])] = float(p[3])
    return lows


def count(sym, d0, d1):
    ms = lambda d: int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000)  # noqa: E731
    lows = load_lows(sym, ms(d0), ms(d1))
    if not lows:
        return None
    n = days = 0
    d = d0
    while d < d1:
        r = day_event(d, lows)
        if r is not None:
            days += 1
            n += bool(r)
        d += dt.timedelta(days=1)
    return {"usable_days": days, "events": n}


if __name__ == "__main__":
    d0, d1 = dt.date(2022, 1, 1), dt.date(2024, 7, 1)                 # splits.py DEV; loader end = DEV_END
    tot = 0
    for s in SYMBOLS:
        r = count(s, d0, d1)
        print(s, "NOT_IN_DATA" if r is None else r)
        tot += 0 if r is None else r["events"]
    print("pooled_n", tot)
