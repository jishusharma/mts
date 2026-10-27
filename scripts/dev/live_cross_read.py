"""BTC vs ES/NQ/VIX cross-market read: the since-open table, rolling 5m-return correlation and the 1m
legend check Eagle_Eyes did by hand on 2026-10-26 (research/live_reads/2026-10-26_cross_market_tools/
live.py, chk1m.py), as one reproducible script. Read-only public market data; no orders, no secrets.

    python scripts/dev/live_cross_read.py                      # live: BTC data-api.binance.vision, ES/NQ/VIX Yahoo
    python scripts/dev/live_cross_read.py --fixture FILE.json  # offline (tests, reruns on a saved pull)

Fixture JSON: {"btc_5m": {"<unix_ts>": close, ...}, "others_5m": {"ES=F": {...}, "NQ=F": {...}, "^VIX": {...}},
"open_ts": <unix_ts>, "btc_1m": [[openTimeMs, O, H, L, C, V, ...], ...]} (btc_1m optional, for --legend).

Binance klines are stamped by OPEN time: the bar keyed `t` covers [t, t+bar_seconds) and its close is the
price at t+bar_seconds, not at t. The old hand-run tool used the bar keyed at the open timestamp itself as
the "price at open", which is really the price 5 minutes later (bug-fixed here: since_open() uses the
PRIOR bar's close, the one that actually closes at the open timestamp).
"""
import argparse
import datetime as dt
import json
import math
import statistics as st
import sys
import urllib.request

sys.dont_write_bytecode = True
UA = {"User-Agent": "Mozilla/5.0"}
BAR_SECONDS_5M = 300
YAHOO_SYMBOLS = ("ES=F", "NQ=F", "^VIX")


def _get(url, timeout=20):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout))


def fetch_btc_5m(limit=300):
    """{unix_ts: close} for the last `limit` BTCUSDT 5m bars."""
    k = _get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=%d" % limit)
    return {x[0] // 1000: float(x[4]) for x in k}


def fetch_btc_1m(limit=240):
    """Raw BTCUSDT 1m klines (for legend_check), newest last."""
    return _get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=%d" % limit)


def fetch_yahoo_5m(symbol):
    """{unix_ts: close} for one Yahoo symbol, last 2 days of 5m bars (pre/post market included)."""
    r = _get("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=2d&interval=5m&includePrePost=true"
              % symbol)["chart"]["result"][0]
    closes = r["indicators"]["quote"][0]["close"]
    return {t: v for t, v in zip(r["timestamp"], closes) if v is not None}


def at_or_before(series, t):
    """Close of the bar stamped at or before t; None if the series has nothing that early."""
    ks = [x for x in series if x <= t]
    return series[max(ks)] if ks else None


def since_open(series, open_ts, bar_seconds=BAR_SECONDS_5M):
    """(baseline, last, pct_change) since open_ts. baseline is the close of the bar stamped
    open_ts - bar_seconds: that bar covers [open_ts - bar_seconds, open_ts), so its close IS the price at
    open_ts. The bar stamped open_ts itself closes bar_seconds later (the fixed bug)."""
    baseline = at_or_before(series, open_ts - bar_seconds)
    if not series:
        return None, None, None
    last_ts = max(series)
    last = series[last_ts]
    if baseline is None:
        return None, last, None
    return baseline, last, (last / baseline - 1) * 100


def corr(x, y):
    n = len(x)
    if n < 5:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


def rolling_r(series_a, series_b, bar_seconds=BAR_SECONDS_5M, windows=((12, "last 1h"), (36, "last 3h"), (96, "last 8h"))):
    """[(label, r, n)] correlation of bar-to-bar returns of series_a vs series_b, over the last n common
    consecutive bars, for each window (n capped to what is available)."""
    common = sorted(set(series_a) & set(series_b))

    def rets(d):
        return {common[i]: d[common[i]] / d[common[i - 1]] - 1
                 for i in range(1, len(common)) if common[i] - common[i - 1] == bar_seconds}

    ra, rb = rets(series_a), rets(series_b)
    ks = sorted(set(ra) & set(rb))
    out = []
    for n, label in windows:
        sel = ks[-n:]
        out.append((label, corr([ra[t] for t in sel], [rb[t] for t in sel]), len(sel)))
    return out


def legend_check(klines_1m, bb_window=20):
    """(mid, upper, lower) of BB(bb_window, 2) from the last bb_window 1m closes, forming bar included
    (chk1m.py's spot legend check)."""
    closes = [float(x[4]) for x in klines_1m[-bb_window:]]
    m = sum(closes) / len(closes)
    sd = st.pstdev(closes)
    return m, m + 2 * sd, m - 2 * sd


def report(btc_5m, others_5m, open_ts, now=None):
    """Printed report lines: since-open table, then rolling BTC-vs-each correlation."""
    now = now or dt.datetime.now(dt.timezone.utc)
    lines = ["now %s (open %s)" % (now.strftime("%H:%MZ"),
                                    dt.datetime.fromtimestamp(open_ts, dt.timezone.utc).strftime("%H:%MZ")),
             "", "SINCE OPEN:"]
    series = {"BTC": btc_5m}
    series.update(others_5m)
    for name, s in series.items():
        baseline, last, pct = since_open(s, open_ts)
        if baseline is None or last is None:
            lines.append("  %-5s no bar before open" % name)
        else:
            lines.append("  %-5s open %.2f now %.2f  %+.2f%%" % (name, baseline, last, pct))
    lines += ["", "ROLLING 5m-return correlation (BTC vs each):"]
    for name, s in others_5m.items():
        lines.append("  vs %s:" % name)
        for label, r, n in rolling_r(btc_5m, s):
            lines.append("    %-10s r=%+.2f n=%d" % (label, r, n))
    return lines


def default_open_ts(now=None):
    """13:30Z today (US cash open), the fixed reference the hand-run tool used."""
    now = now or dt.datetime.now(dt.timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(today.replace(hour=13, minute=30).timestamp())


def load_fixture(path):
    d = json.loads(open(path, encoding="utf-8").read())
    btc_5m = {int(k): v for k, v in d["btc_5m"].items()}
    others_5m = {sym: {int(k): v for k, v in s.items()} for sym, s in d.get("others_5m", {}).items()}
    return btc_5m, others_5m, d["open_ts"], d.get("btc_1m")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture", help="offline JSON fixture instead of a live fetch")
    ap.add_argument("--legend", action="store_true", help="also print the 1m BB(20,2) legend check")
    a = ap.parse_args(argv)
    btc_1m = None
    if a.fixture:
        btc_5m, others_5m, open_ts, btc_1m = load_fixture(a.fixture)
    else:
        btc_5m = fetch_btc_5m()
        others_5m = {sym: fetch_yahoo_5m(sym) for sym in YAHOO_SYMBOLS}
        open_ts = default_open_ts()
        if a.legend:
            btc_1m = fetch_btc_1m()
    for line in report(btc_5m, others_5m, open_ts):
        print(line)
    if a.legend and btc_1m:
        mid, up, lo = legend_check(btc_1m)
        print("\nBB20,2 incl forming: mid %.1f up %.1f lo %.1f" % (mid, up, lo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
