"""levels.py - gather the levels and volatility for one US-open plan (TESTNET module us_open_trader).

gather(day, now, fetch=None, analysts=None) -> {"price","atr15","atr1h","levels":[{"price","name","source","label"}], ...}

Session levels, prior-day/week levels and the value area come from MyTradingSys/tools/live_aid/daily_playbook.py
(key_levels, value_area via key_levels, session_stats) by import; analyst levels from scripts/dev/analyst_levels.py
(ladder, recent_rows) by import. Nothing here writes the scenario ledger. Public market data only, no credentials.

`fetch(interval, start_ms, end_ms) -> [(t_ms, o, h, l, c), ...]` is injectable (tests are offline).
"""
import datetime as dt
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
UTC = dt.timezone.utc
MIN = 60_000
INTERVAL_MS = {"15m": 15 * MIN, "1h": 60 * MIN}

ATR_N = 14                 # SOURCED (Wilder's ATR period, DESIGN.md section 4: "ATR(14) Wilder on closed bars")
HIST_DAYS_1H = 21          # OURS: 1h history for the prior-week levels and the value area (needs the prior Mon-Sun week)
HIST_BARS_15M = 200        # OURS: 15m bars fetched; ATR(14) needs only 15, the rest lets Wilder smoothing settle
ANALYST_DAYS = 5           # SOURCED (MyTradingSys/tools/live_aid/daily_playbook.py _cbp_levels: build(days=5))
CLUSTER_TOL = 0.002        # OURS: analyst calls within 0.2 % of each other form one cluster (same 0.2 % as daily_playbook GAP)
CLUSTER_MIN_CALLS = 2      # OURS: a cluster is at least 2 calls
BAND = 0.10                # SOURCED (daily_playbook.py BAND): analyst levels only within 10 % of price
HOSTS = ("https://data-api.binance.vision", "https://api.binance.com")  # SOURCED (DESIGN.md section 3: host order)

_NAMES_SESSION = {("Europe", "h"): ("EU_HIGH", "Europe session high"), ("Europe", "l"): ("EU_LOW", "Europe session low"),
                  ("Asia", "h"): ("ASIA_HIGH", "Asia session high"), ("Asia", "l"): ("ASIA_LOW", "Asia session low")}


def atr(bars, n=ATR_N):
    """Wilder ATR over (t,o,h,l,c) bars, oldest first: seed = mean of the first n true ranges, then
    atr = (atr*(n-1) + tr) / n. The first bar's true range is h-l. None when fewer than n+1 bars."""
    if len(bars) < n + 1:
        return None
    trs = []
    for i, b in enumerate(bars):
        h, l = b[2], b[3]
        trs.append(h - l if i == 0 else max(h - l, abs(h - bars[i - 1][4]), abs(l - bars[i - 1][4])))
    a = sum(trs[:n]) / n
    for tr in trs[n:]:
        a = (a * (n - 1) + tr) / n
    return a


def _urlopen():
    try:  # ISP DNS block fix used across the repo; absent -> plain urllib
        sys.path.insert(0, str(ROOT))
        from MyTradingSys.runtime.binance_doh import urlopen
        return urlopen
    except Exception:
        import urllib.request
        return urllib.request.urlopen


def default_fetch(interval, start_ms, end_ms):
    """Public klines, hosts in order, paged. Raises OSError when every host fails."""
    step, uo, last = INTERVAL_MS[interval], _urlopen(), None
    for host in HOSTS:
        out, t0 = [], start_ms
        try:
            while t0 < end_ms:
                url = "%s/api/v3/klines?symbol=BTCUSDT&interval=%s&limit=1000&startTime=%d&endTime=%d" % (host, interval, t0, end_ms)
                with uo(url, timeout=15) as f:
                    rows = json.load(f)
                if not rows:
                    break
                out += [(int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in rows]
                t0 = int(rows[-1][0]) + step
                if len(rows) < 1000:
                    break
            return out
        except (OSError, ValueError) as ex:
            last = ex
    raise OSError("all kline hosts failed: %s" % last)


def _closed(bars, interval, now_ms):
    return sorted((tuple(b[:5]) for b in bars if int(b[0]) + INTERVAL_MS[interval] <= now_ms), key=lambda b: b[0])


def analyst_clusters(ladder_rows, price):
    """Analyst calls (analyst_levels.ladder rows) -> clusters [{"price","calls","analysts"}], nearest-first not required.
    Group sorted levels while each is within CLUSTER_TOL of the group's first; keep groups with >= CLUSTER_MIN_CALLS
    calls inside BAND of price; cluster price = median level."""
    lv = sorted((r for r in ladder_rows if r.get("level")), key=lambda r: r["level"])
    groups = []
    for r in lv:
        if groups and r["level"] <= groups[-1][0]["level"] * (1 + CLUSTER_TOL):
            groups[-1].append(r)
        else:
            groups.append([r])
    out = []
    for g in groups:
        if len(g) < CLUSTER_MIN_CALLS:
            continue
        ps = sorted(r["level"] for r in g)
        mid = ps[len(ps) // 2] if len(ps) % 2 else (ps[len(ps) // 2 - 1] + ps[len(ps) // 2]) / 2
        if abs(mid / price - 1) > BAND:
            continue
        out.append({"price": mid, "calls": len(g), "analysts": sorted({r.get("analyst", "?") for r in g})})
    return out


def _default_analysts(now):
    sys.path.insert(0, str(ROOT / "scripts" / "dev"))
    import analyst_levels as al
    return al.ladder(al.recent_rows(ANALYST_DAYS, now))


def gather(day, now, fetch=None, analysts=None):
    """Levels + ATR for `day` as of `now` (UTC aware datetime). `analysts(now) -> ladder rows` is injectable too."""
    fetch = fetch or default_fetch
    sys.path.insert(0, str(ROOT / "MyTradingSys" / "tools" / "live_aid"))
    import daily_playbook as dp  # pure functions only: key_levels, session_stats. Never dp.build / dp.main (they write the ledger)
    now_ms = int(now.timestamp() * 1000)
    start_1h = int((now - dt.timedelta(days=HIST_DAYS_1H)).timestamp() * 1000) // 3_600_000 * 3_600_000
    h1 = _closed(fetch("1h", start_1h, now_ms), "1h", now_ms)
    start_15 = now_ms - HIST_BARS_15M * INTERVAL_MS["15m"]
    m15 = _closed(fetch("15m", start_15, now_ms), "15m", now_ms)
    atr15, atr1h = atr(m15), atr(h1)
    if atr15 is None or not h1:
        raise ValueError("not enough closed bars for ATR(14) on 15m (%d) / 1h (%d)" % (len(m15), len(h1)))
    price = m15[-1][4]
    levels = []

    def add(p, name, source, label):
        levels.append({"price": round(float(p), 2), "name": name, "source": source, "label": label})

    stats = dp.session_stats(h1, day)  # SOURCED windows (daily_playbook SESSIONS, OURS there)
    for (sess, key), (name, text) in _NAMES_SESSION.items():
        s = stats.get(sess)
        if s:
            add(s[key], name, "session", "%s %s" % (text, "%s" % format(round(s[key]), ",")) + ("" if s["complete"] else " (session still open)"))
    for k, p in dp.key_levels(h1, day, now).items():
        if k in dp.NAMES and p:
            add(p, k, "key", "%s %s" % (dp.NAMES[k], format(round(p), ",")))
    note = ""
    try:
        rows = (analysts or _default_analysts)(now)
        for c in analyst_clusters(rows, price):
            add(c["price"], "ANALYST_%d" % round(c["price"]), "analyst",
                "analyst cluster %s (%d calls: %s)" % (format(round(c["price"]), ","), c["calls"], ", ".join(c["analysts"])))
        if not any(l["source"] == "analyst" for l in levels):
            note = "no analyst cluster within %d%% of price" % round(BAND * 100)
    except Exception as ex:  # feed down or store absent: the plan still builds from session levels, and says so
        note = "analyst feed unavailable (%s: %s); plan uses session and prior-day levels only" % (type(ex).__name__, str(ex)[:120])
    levels.sort(key=lambda l: -l["price"])
    return {"day": day.isoformat(), "frozen_utc": now.strftime("%Y-%m-%dT%H:%MZ"), "price": price, "atr15": atr15, "atr1h": atr1h,
            "levels": levels, "analyst_note": note}
