"""us_open_trader recorder (design v1 section 7): market-data readings around the US cash open, TESTNET project, no orders.

Public market data only (no keys, no account endpoints), stdlib only. Appends one strict-JSON line per reading to
<US_OPEN_TRADER_DIR or <repo>/runtime_data/us_open_trader>/readings_<UTC day>.jsonl (git-ignored, append-only).
It replaces the stop-gap research/us_open_trader_2026-11-13/record_now.py and keeps its record keys
(ts_utc, kind, src, binance_spot, bybit, bybit_1m, bybit_15m, okx, deribit, levels_touched, gaps); added keys are
binance_perp, footprint, liquidations, notes, flags and binance_spot.last_bar_t.

Cadence, SOURCED MyTradingSys/system/OPERATOR_DECISIONS.md "2026-11-12 13:00Z" + its 13:05Z follow-up (operator words:
"hourly in the Asian/Eur sessions, every 15 mins 2 hr before US open, every min from US open -2 min to +15 min, then every
10-15 mins during the US session"). Pure next_due(now, open_dt):
    before T-2h            hourly           (hour grid)
    T-2h  .. T-2 min       every 15 min     (quarter-hour grid)
    T-2 min .. T+15 min    every minute     (both ends inclusive)
    after T+15 min .. 21:00Z   every 15 min (OURS: 15 of the operator's "10-15"; 21:00Z = design section 7, inclusive)
Slots sit OFFSET_S (OURS 5 s) after the grid minute so the venue has closed that minute's bar. The cash open comes from
MyTradingSys/tools/us_open_alert.open_utc (SOURCED: federal DST rule), never hard-coded.

Every venue call is independent and runs in its own thread with a CALL_TIMEOUT_S (5 s, SOURCED lead brief: fapi.binance.com and
www.okx.com time out on this machine) and the whole tick has a DEADLINE_S ceiling, so a dead venue cannot delay a 1-minute
reading. A failed call is recorded as {"error": ...} plus a line in "gaps", never invented. Restart-safe: CVD resumes from
the last line of the day's file; a corrupt last line restarts CVD at 0 and says so in "flags".

  python recorder.py [--once] [--open HH:MM] [--until HH:MM] [--plan plan.json] [--no-local]
"""
import sys
sys.dont_write_bytecode = True

import argparse
import json
import math
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for _p in (ROOT / "MyTradingSys" / "tools", ROOT / "MyTradingSys" / "tools" / "live_aid", ROOT / "scripts" / "dev"):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))

CALL_TIMEOUT_S = 5       # SOURCED lead brief 2026-11-13: per-call timeout so a dead venue cannot delay a 1-minute reading
DEADLINE_S = 6.0         # OURS: ceiling for one whole tick (all venue calls run in parallel)
OFFSET_S = 5             # OURS: read 5 s after the grid minute so the previous 1m bar is closed on the venue
FAR_PAST = datetime(1970, 1, 1, tzinfo=timezone.utc)
UNTIL_UTC = (21, 0)      # SOURCED design v1 section 7 ("Until 21:00Z")
SLOW_STEP_MIN = 60       # SOURCED OPERATOR_DECISIONS 11-12 13:05Z: hourly in the Asian/Eur sessions
MID_STEP_MIN = 15        # SOURCED same entry: every 15 min from 2 h before the US open
FAST_STEP_MIN = 1        # SOURCED same entry: every minute from open -2 min to +15 min
AFTER_STEP_MIN = 15      # OURS: "10-15 mins during the US session" -> the 15 end, lead brief
PRE_MIN, POST_MIN = 2, 15  # SOURCED same entry: 1-minute window = open-2 min .. open+15 min
MID_HOURS = 2            # SOURCED same entry: 15-minute window starts 2 h before the open
FOOTPRINT_REFRESH_S = 900  # OURS: local footprint files change at most every 15 min
SPOT_MIN_BARS, SPOT_MAX_BARS = 20, 1000  # OURS: lookback of spot 1m bars (1000 = Binance klines limit)
RSI_N, BB_N, BB_K = 14, 20, 2  # SOURCED stop-gap record_now.py / standard Bollinger(20,2), RSI(14)
STATIC_GAPS = [
    "liquidations: no public REST feed (local xliq_collector file used when it is running)",
    "coinglass: needs a browser (Chrome tools are off)",
    "large_trades: not fetched live (only whatever footprint_12h holds locally)",
]


# ---------------------------------------------------------------- cadence (pure)
def open_for(day):
    import us_open_alert  # MyTradingSys/tools/us_open_alert.py (DST-aware 09:30 ET)
    return us_open_alert.open_utc(day)


def _grid_after(ref, step_min, lo, hi, hi_incl):
    """First grid time (multiple of step_min since the epoch) strictly after ref and >= lo, within hi; else None."""
    step = step_min * 60
    g = (math.floor(ref.timestamp() / step) + 1) * step
    if g < lo.timestamp():
        g = math.ceil(lo.timestamp() / step) * step
    out = datetime.fromtimestamp(g, timezone.utc)
    if out < hi or (hi_incl and out == hi):
        return out
    return None


def next_due(now, open_dt, until=None):
    """Next reading time strictly after `now` (aware UTC), or None when the day is over. Pure."""
    until = until or open_dt.replace(hour=UNTIL_UTC[0], minute=UNTIL_UTC[1], second=0, microsecond=0)
    a = open_dt - timedelta(hours=MID_HOURS)
    b = open_dt - timedelta(minutes=PRE_MIN)
    c = open_dt + timedelta(minutes=POST_MIN)
    ref = now - timedelta(seconds=OFFSET_S)
    cands = [
        _grid_after(ref, SLOW_STEP_MIN, FAR_PAST, min(a, until), False),
        _grid_after(ref, MID_STEP_MIN, a, min(b, until), False),
        _grid_after(ref, FAST_STEP_MIN, b, min(c, until), True),
        _grid_after(ref, AFTER_STEP_MIN, c + timedelta(seconds=1), until, True),
    ]
    cands = [x for x in cands if x is not None]
    return min(cands) + timedelta(seconds=OFFSET_S) if cands else None


# ---------------------------------------------------------------- pure helpers
def clean(x):
    """Make a structure strict-JSON safe: NaN/inf -> None, tuples -> lists."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    return x


def rsi(closes, n=RSI_N):
    if len(closes) < n + 1:
        raise ValueError("rsi needs %d closes, got %d" % (n + 1, len(closes)))
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        ag, al = (ag * (n - 1) + g) / n, (al * (n - 1) + l) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)


def bb(closes, n=BB_N, k=BB_K):
    if len(closes) < n:
        raise ValueError("bb needs %d closes, got %d" % (n, len(closes)))
    w = closes[-n:]
    m = sum(w) / n
    sd = (sum((x - m) ** 2 for x in w) / n) ** 0.5
    return {"mid": round(m, 1), "up": round(m + k * sd, 1), "lo": round(m - k * sd, 1),
            "width_pct": round(2 * k * sd / m * 100, 3)}


def ind(closes):
    return {"rsi14": round(rsi(closes), 1), "bb20": bb(closes), "close": closes[-1]}


def levels_from_plan(plan):
    """Plan json -> sorted level list: every order trigger, plan["levels"], and the 5-digit numbers written in order["level"]."""
    out = set()
    for o in plan.get("orders") or []:
        if isinstance(o.get("trigger"), (int, float)):
            out.add(int(o["trigger"]))
        for m in re.findall(r"\b\d{2},\d{3}\b", str(o.get("level", ""))):  # OURS: "69,571" style numbers in the plan text
            out.add(int(m.replace(",", "")))
    for v in plan.get("levels") or []:
        if isinstance(v, (int, float)):
            out.add(int(v))
    return sorted(out)


def load_levels(path):
    """(levels, note). No plan json (or unreadable) -> ([], note), never a guess."""
    p = Path(path)
    if not p.exists():
        return [], "no plan json at %s: levels_touched stays empty" % p.name
    try:
        return levels_from_plan(json.loads(p.read_text(encoding="utf-8"))), None
    except (ValueError, OSError, AttributeError) as e:
        return [], "plan json unreadable (%s): levels_touched stays empty" % type(e).__name__


# ---------------------------------------------------------------- state / restart
def new_state():
    return {"cvd": 0.0, "last_t": 0, "flags": [], "fp": None}


def _ts_ms(ts_utc):
    return int(datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000)


def load_state(path):
    """Resume CVD from the day's file. Corrupt LAST line -> cvd 0 + flag. Missing/empty file -> fresh, no flag."""
    st = new_state()
    p = Path(path)
    if not p.exists():
        return st
    try:
        lines = [x for x in p.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    except OSError:
        st["flags"].append("cvd_reset: day file unreadable")
        return st
    for i, line in enumerate(reversed(lines)):
        try:
            rec = json.loads(line)
            if not isinstance(rec, dict):
                raise ValueError("not an object")
        except ValueError:
            if i == 0:
                st["flags"].append("cvd_reset: corrupt last line in day file, CVD restarted at 0")
                return st
            continue
        s = rec.get("binance_spot")
        if isinstance(s, dict) and isinstance(s.get("cvd_btc_since_start"), (int, float)):
            st["cvd"] = float(s["cvd_btc_since_start"])
            if isinstance(s.get("last_bar_t"), int):
                st["last_t"] = s["last_bar_t"]
            else:  # stop-gap line: newest closed bar at ts_utc opened one minute before that minute
                try:
                    st["last_t"] = _ts_ms(rec["ts_utc"]) // 60000 * 60000 - 60000
                except (KeyError, ValueError):
                    st["last_t"] = 0
            return st
    return st


# ---------------------------------------------------------------- venue calls (each independent)
def http_get(url, timeout=CALL_TIMEOUT_S):
    req = urllib.request.Request(url, headers={"User-Agent": "mts-recorder"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _f(x):
    return float(x)


def spot_bars(fetch, limit):
    rows = fetch("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=%d" % limit, CALL_TIMEOUT_S)
    return [{"t": int(x[0]), "o": _f(x[1]), "h": _f(x[2]), "l": _f(x[3]), "c": _f(x[4]), "vol": _f(x[5]),
             "delta": 2 * _f(x[9]) - _f(x[5])} for x in rows[:-1]]  # last row is the forming bar; delta = taker buy - taker sell


def bybit_tick(fetch):
    t = fetch("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT", CALL_TIMEOUT_S)["result"]["list"][0]
    return {"last": _f(t["lastPrice"]), "mark": _f(t["markPrice"]), "oi_btc": _f(t["openInterest"]),
            "oi_usd": _f(t["openInterestValue"]), "funding": _f(t["fundingRate"]), "vol24h_btc": _f(t["volume24h"])}


def bybit_ratio(fetch):
    r = fetch("https://api.bybit.com/v5/market/account-ratio?category=linear&symbol=BTCUSDT&period=5min&limit=1", CALL_TIMEOUT_S)
    rows = r["result"]["list"]
    if not rows:
        raise ValueError("empty account-ratio list")
    return {"long_share": _f(rows[0]["buyRatio"]), "short_share": _f(rows[0]["sellRatio"])}


def bybit_k(fetch, interval):
    rows = fetch("https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=%s&limit=120" % interval, CALL_TIMEOUT_S)
    rows = sorted(rows["result"]["list"], key=lambda x: int(x[0]))[:-1]  # closed bars only
    return ind([_f(x[4]) for x in rows])


def okx_oi(fetch):
    d = fetch("https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP", CALL_TIMEOUT_S)["data"][0]
    return {"oi_btc": _f(d["oiCcy"])}


def okx_fr(fetch):
    d = fetch("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP", CALL_TIMEOUT_S)["data"][0]
    return {"funding": _f(d["fundingRate"])}


def deribit(fetch):
    d = fetch("https://www.deribit.com/api/v2/public/get_book_summary_by_instrument?instrument_name=BTC-PERPETUAL",
              CALL_TIMEOUT_S)["result"][0]
    return {"mark": d.get("mark_price"), "oi_usd": d.get("open_interest"), "funding_8h": d.get("funding_8h"),
            "vol24h_usd": d.get("volume_usd")}


def fapi_premium(fetch):
    d = fetch("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT", CALL_TIMEOUT_S)
    return {"mark": _f(d["markPrice"]), "funding": _f(d["lastFundingRate"])}


def fapi_oi(fetch):
    return {"oi_btc": _f(fetch("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", CALL_TIMEOUT_S)["openInterest"])}


# local sources (reused by import, no download)
def default_footprint(price, now_ms):
    import footprint_12h  # scripts/dev/footprint_12h.py: us_bias_inputs reads the local 12h bars on D:, never downloads
    return footprint_12h.us_bias_inputs(now_ms, price=price)


def default_liq(now_ms):
    import xliq_collector  # MyTradingSys/tools/live_aid: local events file written by the collector when it runs
    if not Path(xliq_collector.EVENTS).exists():
        raise FileNotFoundError("xliq_events.jsonl absent (collector not running)")
    ev = xliq_collector.load_events(now_ms=now_ms)
    return {v: xliq_collector.venue_summary(e, min((x[0] for x in e), default=None), now_ms) for v, e in ev.items()}


def _run_parallel(tasks, deadline_s):
    """tasks: {name: callable}. Returns {name: ("ok", value) | ("err", text)}; unfinished at the deadline -> timeout error."""
    ex = ThreadPoolExecutor(max_workers=max(1, len(tasks)))
    futs = {n: ex.submit(fn) for n, fn in tasks.items()}
    wait(list(futs.values()), timeout=deadline_s)
    out = {}
    for n, f in futs.items():
        if not f.done():
            out[n] = ("err", "timeout>%ss" % deadline_s)
        elif f.exception() is not None:
            out[n] = ("err", repr(f.exception())[:160])
        else:
            out[n] = ("ok", f.result())
    ex.shutdown(wait=False, cancel_futures=True)
    return out


def _merge(res, names, gaps, label):
    """Merge sub-calls of one venue: all failed -> {"error"}, else the fields that answered (failures become gap lines)."""
    ok = {}
    for n in names:
        kind, v = res[n]
        if kind == "ok":
            ok.update(v)
        else:
            gaps.append("%s: %s" % (n if len(names) > 1 else label, v))
    if not ok:
        return {"error": "; ".join(res[n][1] for n in names)[:160]}
    return ok


def reading(now, state, fetch, levels, notes, local=True, deadline_s=DEADLINE_S, footprint_fn=None, liq_fn=None):
    """One tick. Mutates `state` (cvd, last_t, fp cache, flags). Never raises for a venue failure."""
    now_ms = int(now.timestamp() * 1000)
    last_t = state.get("last_t", 0)
    need = SPOT_MIN_BARS if not last_t else min(SPOT_MAX_BARS, max(SPOT_MIN_BARS, (now_ms - last_t) // 60000 + 2))
    tasks = {
        "binance_spot": lambda: spot_bars(fetch, need),
        "bybit": lambda: bybit_tick(fetch), "bybit_ratio": lambda: bybit_ratio(fetch),
        "bybit_1m": lambda: bybit_k(fetch, "1"), "bybit_15m": lambda: bybit_k(fetch, "15"),
        "okx_oi": lambda: okx_oi(fetch), "okx_fr": lambda: okx_fr(fetch),
        "deribit": lambda: deribit(fetch),
        "fapi_mark": lambda: fapi_premium(fetch), "fapi_oi": lambda: fapi_oi(fetch),
    }
    res = _run_parallel(tasks, deadline_s)
    gaps = list(STATIC_GAPS)
    flags = list(state.get("flags") or [])
    state["flags"] = []
    rec = {"ts_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "kind": "reading", "src": "us_open_trader/recorder.py"}

    kind, bars = res["binance_spot"]
    touched = []
    if kind == "ok" and bars:
        if last_t and bars[0]["t"] > last_t + 60000:
            flags.append("cvd_gap: bars between %d and %d not covered, CVD understates" % (last_t, bars[0]["t"]))
        new = [b for b in bars if b["t"] > last_t] if last_t else bars[-1:]
        state["last_t"] = bars[-1]["t"]
        state["cvd"] = state.get("cvd", 0.0) + sum(b["delta"] for b in new)
        span = new or bars[-1:]
        hi, lo = max(b["h"] for b in span), min(b["l"] for b in span)
        rec["binance_spot"] = {"price": bars[-1]["c"], "hi_since_last": hi, "lo_since_last": lo,
                               "vol_btc_since_last": round(sum(b["vol"] for b in new), 3),
                               "net_delta_btc_since_last": round(sum(b["delta"] for b in new), 3),
                               "cvd_btc_since_start": round(state["cvd"], 3), "bars": len(new), "last_bar_t": bars[-1]["t"]}
        touched = [lv for lv in levels if lo <= lv <= hi]
    else:
        err = bars if kind == "err" else "empty kline list"
        rec["binance_spot"] = {"error": err}
        gaps.append("binance_spot: %s" % err)
    rec["levels_touched"] = touched

    bk, bv = res["bybit"]
    if bk == "ok":
        rk, rv = res["bybit_ratio"]
        if rk != "ok":
            gaps.append("bybit_ratio: %s" % rv)
        rec["bybit"] = dict(bv, **(rv if rk == "ok" else {"long_share": None, "short_share": None}))
    else:
        rec["bybit"] = {"error": bv}
        gaps.append("bybit: %s" % bv)
    for key in ("bybit_1m", "bybit_15m", "deribit"):
        k, v = res[key]
        rec[key] = v if k == "ok" else {"error": v}
        if k != "ok":
            gaps.append("%s: %s" % (key, v))
    rec["okx"] = _merge(res, ("okx_oi", "okx_fr"), gaps, "okx")
    if "error" in rec["okx"]:
        gaps.append("okx: %s" % rec["okx"]["error"])
    perp = _merge(res, ("fapi_mark", "fapi_oi"), gaps, "binance_perp")
    rec["binance_perp"] = perp
    if "error" in perp:
        gaps.append("binance_perp: %s (fapi.binance.com does not answer on this machine)" % perp["error"])

    if local:
        price = (rec["binance_spot"] or {}).get("price")
        old = state.get("fp")
        if old and now_ms - old[0] < FOOTPRINT_REFRESH_S * 1000:
            rec["footprint"] = old[1]
        else:
            try:
                rec["footprint"] = (footprint_fn or default_footprint)(price, now_ms)
            except Exception as e:  # noqa: BLE001 - a missing local file is a recorded gap
                rec["footprint"] = {"error": repr(e)[:160]}
            state["fp"] = (now_ms, rec["footprint"])
        try:
            rec["liquidations"] = (liq_fn or default_liq)(now_ms)
        except Exception as e:  # noqa: BLE001
            rec["liquidations"] = {"error": repr(e)[:160]}
    rec["gaps"] = gaps
    if notes:
        rec["notes"] = list(notes)
    if flags:
        rec["flags"] = flags
    return clean(rec)


# ---------------------------------------------------------------- runner
def out_dir():
    env = os.environ.get("US_OPEN_TRADER_DIR")
    return Path(env) if env else ROOT / "runtime_data" / "us_open_trader"


def _hm(now, s):
    return now.replace(hour=int(s[:2]), minute=int(s[3:5]), second=0, microsecond=0)


def main(argv=None, fetch=None, clock=None, sleep=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", help="HH:MM UTC override; default = us_open_alert.open_utc (DST-aware)")
    ap.add_argument("--until", default="%02d:%02d" % UNTIL_UTC)
    ap.add_argument("--plan", help="plan json (default research/us_open_trader_<day>/plan_<day>.json)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--no-local", action="store_true", help="skip footprint/liquidation local files")
    a = ap.parse_args(argv)
    fetch = fetch or http_get
    clock = clock or (lambda: datetime.now(timezone.utc))
    sleep = sleep or time.sleep
    now = clock()
    day = now.strftime("%Y-%m-%d")
    open_dt = _hm(now, a.open) if a.open else open_for(now.date())
    until = _hm(now, a.until)
    plan = Path(a.plan) if a.plan else ROOT / "MyTradingSys" / "research" / ("us_open_trader_" + day) / ("plan_%s.json" % day)
    levels, note = load_levels(plan)
    notes = [note] if note else []
    d = out_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / ("readings_%s.jsonl" % day)
    state = load_state(path)
    if not a.once and next_due(now, open_dt, until) is None and now > until + timedelta(seconds=OFFSET_S):
        print("past %s UTC, nothing to record" % a.until, flush=True)
        return 0
    while True:
        now = clock()
        rec = reading(now, state, fetch, levels, notes, local=not a.no_local)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, allow_nan=False) + "\n")
        print(rec["ts_utc"], (rec.get("binance_spot") or {}).get("price"), "touched", rec.get("levels_touched"),
              "gaps", len(rec["gaps"]), flush=True)
        if a.once:
            return 0
        nd = next_due(clock(), open_dt, until)
        if nd is None:
            return 0
        sleep(max(1.0, (nd - clock()).total_seconds()))


if __name__ == "__main__":
    sys.exit(main())
