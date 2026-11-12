"""Daily 12h BTC footprint record + US-session bias input (card footprint-12h-daily-us-bias-1112; operator 2026-11-12).

  python scripts/dev/footprint_12h.py [--tf 15m|1h|2h|12h] [--days 30] [--no-rest] [--line] [--js]

--tf (card footprint-multi-tf-large-trades-cadence-1112): bar length; 15m/1h/2h bars (UTC-aligned) go to D:/MTS_data/footprint_<tf>/ so the
12h record is untouched, file BTCUSDT_<date>_<HHMM>.json. Those records add large_trades: aggTrades with qty >= p99.9 of that bar
(LARGE_Q, OURS, chosen unchecked), max 50, [ts_ms, price, qty, taker side]. Short bars are rebuilt whole (exact threshold); a resumed
12h bar merges per-chunk picks. footprint_bias_data.js gets "tf": {15m,1h,2h: {line,...}}; Live Aid re-reads that file on a 60 s
in-page timer paced by footprint_cadence.js (no OS scheduler).

WHAT: Binance USD-M BTCUSDT aggTrades (PUBLIC data only) folded into 12h footprint bars. Bars are UTC 00:00-12:00 and 12:00-24:00,
which equals 05:30-17:30 and 17:30-05:30 IST: the same boundaries as Binance's own 12h klines. Whether CoinGlass Legend uses them
too is checked in MyTradingSys/research/footprint_12h_1112/CHECK.md (a Legend chart in UTC+5:30 would show bars at 05:30 / 17:30).
Output: D:/MTS_data/footprint_12h/BTCUSDT_<date>_<00|12>.json (market data, NOT committed: the repo is public).

PER BAR: price rows (BUCKET_USD, OURS, default 10 USD), buy vol (taker buys, is_buyer_maker false), sell vol (is_buyer_maker true =
the buyer was the maker, so the taker SOLD), delta per row and per bar (BTC), POC (max total row; tie -> nearest the bar mid, then
lower), value area 70 % (VA_FRAC, OURS: from the POC add the larger of the next row above / below until 70 % of volume),
stacked imbalances, top-5 single-row absorptions, open/high/low/close from the trades.
Imbalance (OURS): diagonal. Buy imbalance at row i: buy[i] >= IMB_RATIO * sell[i-1]; sell imbalance at row i: sell[i] >= IMB_RATIO *
buy[i+1]; IMB_RATIO 3, the dominant side must be >= IMB_MIN_VOL BTC (zero-denominator guard); STACK_ROWS 3 consecutive rows = a stack.
Absorption (OURS): at the lowest / highest 25 % of the bar's rows, the aggressive volume that hit the edge (sell vol low, buy vol high)
and did not carry price beyond it; ranked by that volume. "Biggest absorption" = rank 1. Descriptive only, nothing is scored.

SOURCES: completed UTC days = data.binance.vision daily zip (sha256-checked). A bar the archive does not yet hold (today's) and the
bar still forming come from public REST fapi aggTrades (paged by id, throttled REST_SLEEP s per call, MAX_PAGES cap); a bar not
finished or cut by the cap is written partial:true with the last agg id, and the next run RESUMES from that id (rows are additive).
Idempotent: a run rebuilds only missing or partial bars; the first run backfills BACKFILL_DAYS (30).

NO SCHEDULER (SCHEDULING_POLICY.md): "daily" = on demand. Triggers: (1) scripts/dev/us_prep.py P1-P3 calls build_footprint() here
and copies footprint_bias_data.js to the main checkout; (2) Live Aid is a static page opened from disk (there is no Live Aid server),
so the page checks the latest completed 12h bar in footprint_bias_data.js and, when it is missing, shows the one command to run.
us_bias_inputs() is the US-session bias input; bias_line() its one plain line, labelled context, not measured.
Fail closed: a source that cannot be read gives UNKNOWN, never a made-up number.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import math
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
try:
    from MyTradingSys.runtime.binance_doh import urlopen as _urlopen  # ISP DNS block fix for Binance hosts
except ImportError:  # pragma: no cover
    _urlopen = urllib.request.urlopen

DATA_ROOT = Path("D:/MTS_data")
OUTDIR = DATA_ROOT / "footprint_12h"
JS_OUT = ROOT / "MyTradingSys" / "tools" / "live_aid" / "footprint_bias_data.js"
SYMBOL = "BTCUSDT"
BUCKET_USD = 10.0      # OURS
VA_FRAC = 0.70         # OURS (spec)
IMB_RATIO = 3.0        # OURS (spec default)
IMB_MIN_VOL = 1.0      # OURS, BTC
STACK_ROWS = 3         # OURS (spec)
EDGE_FRAC = 0.25       # OURS
TOP_ABS = 5
BACKFILL_DAYS = 30
MAX_PAGES = 1500       # ~1.5M trades; a 12h bar is ~0.6M
REST_SLEEP = 0.25      # s between pages (fapi aggTrades weight 20, limit 2400/min: ~4 calls/s is ~80 %)
HALF_MS = 12 * 3600 * 1000
TF_MS = {"15m": 900000, "1h": 3600000, "2h": 7200000, "12h": HALF_MS}  # --tf choices; every one divides a UTC day
TF_ORDER = ("15m", "1h", "2h", "12h")
LARGE_Q = 99.9         # OURS (chosen, unchecked): a "large trade" = aggTrade qty >= this percentile of the bar's trades
LARGE_CAP = 50         # per bar, largest first
ARCHIVE = "https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip"
FAPI = "https://fapi.binance.com/fapi/v1/aggTrades"
UNKNOWN = "UNKNOWN"
LABEL = "context, not measured"


# ---------- pure maths (tested) ----------
def fold(price, qty, ibm, bucket=BUCKET_USD):
    """Arrays -> {row_low_cents: [buy, sell]}, plus first/last/high/low price and trade count. ibm True = buyer was maker = taker SOLD."""
    price = np.asarray(price, dtype="float64")
    qty = np.asarray(qty, dtype="float64")
    ibm = np.asarray(ibm, dtype=bool)
    if price.size == 0:
        return {"rows": {}, "n": 0}
    step = int(round(bucket * 100))
    key = (np.rint(price * 100).astype("int64") // step) * step
    uk, inv = np.unique(key, return_inverse=True)
    sell = np.bincount(inv, weights=np.where(ibm, qty, 0.0), minlength=uk.size)
    buy = np.bincount(inv, weights=np.where(ibm, 0.0, qty), minlength=uk.size)
    rows = {int(k): [float(b), float(s)] for k, b, s in zip(uk, buy, sell)}
    return {"rows": rows, "n": int(price.size), "open": float(price[0]), "close": float(price[-1]),
            "high": float(price.max()), "low": float(price.min())}


def large_trades(price, qty, ibm, ts, q=LARGE_Q, cap=LARGE_CAP):
    """Prints with qty >= the q-th percentile (linear) of this bar's trades -> [[ts, price, qty, 'buy'|'sell'], ...], largest first
    (ties: earliest first), at most `cap`. Side is the taker: is_buyer_maker True = the taker sold."""
    qty = np.asarray(qty, dtype="float64")
    if qty.size == 0:
        return []
    thr = float(np.percentile(qty, q))
    idx = np.nonzero(qty >= thr)[0]
    price, ibm, ts = np.asarray(price, dtype="float64"), np.asarray(ibm, dtype=bool), np.asarray(ts)
    idx = sorted(idx.tolist(), key=lambda i: (-qty[i], ts[i]))[:cap]
    return [[int(ts[i]), float(price[i]), float(qty[i]), "sell" if ibm[i] else "buy"] for i in idx]


def merge_large(a, b, cap=LARGE_CAP):
    return sorted(a + b, key=lambda t: (-t[2], t[0]))[:cap]


def merge_rows(a, b):
    out = {k: list(v) for k, v in a.items()}
    for k, (bu, se) in b.items():
        cur = out.setdefault(k, [0.0, 0.0])
        cur[0] += bu
        cur[1] += se
    return out


def _dense(rows, bucket):
    step = int(round(bucket * 100))
    lo, hi = min(rows), max(rows)
    keys = list(range(lo, hi + step, step))
    return keys, [rows.get(k, [0.0, 0.0]) for k in keys]


def poc_va(rows, bucket=BUCKET_USD, frac=VA_FRAC):
    """POC row (low, USD) and the 70 % value area (low row, high row, share). rows = {cents: [buy, sell]}."""
    keys, v = _dense(rows, bucket)
    tot = [b + s for b, s in v]
    total = sum(tot)
    if total <= 0:
        return None
    mid = (len(keys) - 1) / 2.0
    best = max(range(len(keys)), key=lambda i: (round(tot[i], 9), -abs(i - mid), -i))
    lo = hi = best
    acc = tot[best]
    while acc < frac * total - 1e-12 and (lo > 0 or hi < len(keys) - 1):
        up = tot[hi + 1] if hi < len(keys) - 1 else -1.0
        dn = tot[lo - 1] if lo > 0 else -1.0
        if up >= dn:
            hi += 1
            acc += tot[hi]
        else:
            lo -= 1
            acc += tot[lo]
    return {"poc": keys[best] / 100.0, "va_low": keys[lo] / 100.0, "va_high": keys[hi] / 100.0, "va_share": round(acc / total, 4)}


def stacked_imbalances(rows, bucket=BUCKET_USD, ratio=IMB_RATIO, min_rows=STACK_ROWS, min_vol=IMB_MIN_VOL):
    """Diagonal imbalances, then runs of >= min_rows consecutive rows on the same side. Returns [{side, low, high, rows}]."""
    keys, v = _dense(rows, bucket)
    n = len(keys)
    flag = [0] * n  # +1 buy imbalance, -1 sell imbalance
    for i in range(n):
        buy, sell = v[i]
        if i > 0 and buy >= min_vol and buy >= ratio * v[i - 1][1]:
            flag[i] = 1
        elif i < n - 1 and sell >= min_vol and sell >= ratio * v[i + 1][0]:
            flag[i] = -1
    out, i = [], 0
    while i < n:
        if flag[i] == 0:
            i += 1
            continue
        j = i
        while j + 1 < n and flag[j + 1] == flag[i]:
            j += 1
        if j - i + 1 >= min_rows:
            out.append({"side": "buy" if flag[i] > 0 else "sell", "low": keys[i] / 100.0, "high": keys[j] / 100.0 + bucket, "rows": j - i + 1})
        i = j + 1
    return out


def absorptions(rows, bucket=BUCKET_USD, edge=EDGE_FRAC, top=TOP_ABS):
    """Top single-row absorptions: sell vol in the lowest `edge` of rows (buyers absorbed it), buy vol in the highest (sellers absorbed it)."""
    keys, v = _dense(rows, bucket)
    n = len(keys)
    k = max(1, int(math.ceil(n * edge)))
    cand = []
    for i in range(min(k, n)):
        if v[i][1] > 0:
            cand.append({"price": keys[i] / 100.0, "vol": round(v[i][1], 3), "kind": "buyers absorbed selling", "side": "buy"})
    for i in range(max(n - k, 0), n):
        if v[i][0] > 0:
            cand.append({"price": keys[i] / 100.0, "vol": round(v[i][0], 3), "kind": "sellers absorbed buying", "side": "sell"})
    cand.sort(key=lambda c: (-c["vol"], c["price"]))
    return cand[:top]


def bar_record(rows, ohlc, start_ms, partial, source, last_id, through_ms, trades, bucket=BUCKET_USD, tf_ms=HALF_MS, large=None):
    buy = sum(r[0] for r in rows.values())
    sell = sum(r[1] for r in rows.values())
    pv = poc_va(rows, bucket) if rows else None
    st = dt.datetime.fromtimestamp(start_ms / 1000, dt.timezone.utc)
    rec = {"symbol": SYMBOL, "venue": "binance_usdm_perp", "units": "BTC",
            "bar_start_utc": st.strftime("%Y-%m-%dT%H:%MZ"), "bar_start_ms": start_ms, "bar_end_ms": start_ms + tf_ms,
            "slot": "%02d" % st.hour, "partial": bool(partial), "source": source, "through_ms": through_ms, "last_agg_id": last_id,
            "trades": trades, "bucket_usd": bucket,
            "params": {"va_frac": VA_FRAC, "imb_ratio": IMB_RATIO, "imb_min_vol_btc": IMB_MIN_VOL, "stack_rows": STACK_ROWS,
                       "edge_frac": EDGE_FRAC, "label": "bucket/ratio/edge are OURS"},
            "open": ohlc.get("open"), "high": ohlc.get("high"), "low": ohlc.get("low"), "close": ohlc.get("close"),
            "buy_vol": round(buy, 3), "sell_vol": round(sell, 3), "delta": round(buy - sell, 3),
            "poc": pv and pv["poc"], "value_area": pv and {"pct": VA_FRAC, "low": pv["va_low"], "high": pv["va_high"], "share": pv["va_share"]},
            "stacks": stacked_imbalances(rows, bucket) if rows else [], "absorptions": absorptions(rows, bucket) if rows else [],
            "rows": [[k / 100.0, round(b, 3), round(s, 3), round(b - s, 3)] for k, (b, s) in sorted(rows.items())]}
    if large is not None:  # a 12h record built without it stays byte-identical to the shipped shape
        rec["tf"] = _tf_name(tf_ms)
        rec["large_trades"] = large
        rec["large_rule"] = "qty >= p%s of the bar's aggTrades (OURS), max %d, largest first; [ts_ms, price, qty_btc, taker side]" % (LARGE_Q, LARGE_CAP)
    return rec


# ---------- files ----------
def outdir_for(tf="12h"):
    return OUTDIR if tf == "12h" else DATA_ROOT / ("footprint_" + tf)


def bar_path(start_ms, outdir=None, tf="12h"):
    st = dt.datetime.fromtimestamp(start_ms / 1000, dt.timezone.utc)
    name = "%s_%s_%02d.json" % (SYMBOL, st.strftime("%Y-%m-%d"), st.hour) if tf == "12h" \
        else "%s_%s_%02d%02d.json" % (SYMBOL, st.strftime("%Y-%m-%d"), st.hour, st.minute)
    return Path(outdir or outdir_for(tf)) / name


def load_bar(start_ms, outdir=None, tf="12h"):
    p = bar_path(start_ms, outdir, tf)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_bar(rec, outdir=None, tf="12h"):
    p = bar_path(rec["bar_start_ms"], outdir, tf)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, separators=(",", ":")), encoding="utf-8", newline="\n")
    tmp.replace(p)
    return p


def bar_start_of(ms, tf_ms=HALF_MS):
    return ms - ms % tf_ms


def _tf_name(tf_ms):
    return {v: k for k, v in TF_MS.items()}[tf_ms]


def needs_build(start_ms, now_ms, outdir=None, tf_ms=HALF_MS):
    """True when the bar file is missing or still partial (and the bar has started)."""
    if start_ms > now_ms:
        return False
    cur = load_bar(start_ms, outdir, _tf_name(tf_ms))
    return cur is None or bool(cur.get("partial"))


# ---------- sources ----------
def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with _urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (418, 429) and attempt < 3:  # rate limit: obey Retry-After, never hammer
                time.sleep(min(float(e.headers.get("Retry-After") or 20), 120))
                continue
            raise


def archive_day(day):
    """(price, qty, ibm, ts, ids) arrays for one UTC day from the archive zip, or None on 404. sha256-checked."""
    import pandas as pd
    blob = _get(ARCHIVE % day)
    if blob is None:
        return None
    chk = _get((ARCHIVE % day) + ".CHECKSUM")
    if chk is None or hashlib.sha256(blob).hexdigest() != chk.decode().split()[0]:
        raise RuntimeError("archive checksum missing or mismatch %s" % day)
    z = zipfile.ZipFile(io.BytesIO(blob))
    with z.open(z.namelist()[0]) as f:
        head = f.peek(1)[:1]
        names = ["agg_trade_id", "price", "quantity", "first_trade_id", "last_trade_id", "transact_time", "is_buyer_maker"]
        df = pd.read_csv(f, usecols=["agg_trade_id", "price", "quantity", "transact_time", "is_buyer_maker"],
                         **({} if head.isalpha() else dict(header=None, names=names)))
    return (df["price"].to_numpy(), df["quantity"].to_numpy(), df["is_buyer_maker"].astype(str).str.lower().eq("true").to_numpy(),
            df["transact_time"].to_numpy(), df["agg_trade_id"].to_numpy())


def rest_page(params):
    q = "&".join("%s=%s" % kv for kv in params.items())
    return json.loads(_get("%s?symbol=%s&%s" % (FAPI, SYMBOL, q), timeout=20).decode())


def rest_trades(start_ms, end_ms, from_id=None, max_pages=MAX_PAGES, sleep=REST_SLEEP, page=rest_page, clock=time.sleep, log=None):
    """Page public aggTrades for [start_ms, end_ms) -> (arrays, complete). Resumes after from_id when given."""
    px, qy, ib, ts, ids = [], [], [], [], []
    complete = False
    p = {"fromId": from_id + 1, "limit": 1000} if from_id is not None else {"startTime": start_ms, "limit": 1000}
    for n in range(max_pages):
        rows = page(p)
        if not rows:
            complete = True
            break
        done = False
        for r in rows:
            if r["T"] >= end_ms:
                done = True
                break
            px.append(float(r["p"])); qy.append(float(r["q"])); ib.append(bool(r["m"])); ts.append(r["T"]); ids.append(r["a"])
        if done:
            complete = True
            break
        if len(rows) < 1000:
            break  # reached "now": the bar is still forming
        p = {"fromId": rows[-1]["a"] + 1, "limit": 1000}
        clock(sleep)
        if log and n % 100 == 99:
            log("  rest page %d" % (n + 1))
    return (np.array(px), np.array(qy), np.array(ib, dtype=bool), np.array(ts, dtype="int64"), np.array(ids, dtype="int64")), complete


# ---------- build ----------
def build_from_arrays(arr, start_ms, source, now_ms, complete_hint=True, prior=None, bucket=BUCKET_USD, tf_ms=HALF_MS):
    price, qty, ibm, ts, ids = arr
    m = (ts >= start_ms) & (ts < start_ms + tf_ms)
    f = fold(price[m], qty[m], ibm[m], bucket)
    rows, trades = f["rows"], f["n"]
    ohlc = {k: f.get(k) for k in ("open", "high", "low", "close")}
    large = large_trades(price[m], qty[m], ibm[m], ts[m])
    last_id = int(ids[m].max()) if m.any() else None
    through = int(ts[m].max()) if m.any() else None
    if prior and prior.get("rows"):  # resume: rows are additive
        old = {int(round(r[0] * 100)): [r[1], r[2]] for r in prior["rows"]}
        rows = merge_rows(old, rows)
        trades += prior.get("trades", 0)
        ohlc = {"open": prior["open"], "close": ohlc["close"] if m.any() else prior["close"],
                "high": max(prior["high"], ohlc["high"]) if m.any() else prior["high"],
                "low": min(prior["low"], ohlc["low"]) if m.any() else prior["low"]}
        last_id = last_id or prior.get("last_agg_id")
        through = through or prior.get("through_ms")
        source = prior["source"] if prior["source"] == source else "mixed"
        large = merge_large(prior.get("large_trades") or [], large)  # resumed 12h bar: per-chunk percentile, merged (see docstring)
    partial = (not complete_hint) or now_ms < start_ms + tf_ms
    return bar_record(rows, ohlc, start_ms, partial, source, last_id, through, trades, bucket, tf_ms, large)


def build_bar(start_ms, now_ms, outdir=None, day_cache=None, rest=True, log=print, max_pages=MAX_PAGES, tf_ms=HALF_MS):
    """Build/rebuild one bar and write it. Returns the record, or None when no source could supply it."""
    day = dt.datetime.fromtimestamp(start_ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d")
    end_ms = start_ms + tf_ms
    tf = _tf_name(tf_ms)
    day_start = start_ms - start_ms % (2 * HALF_MS)
    if now_ms >= day_start + 2 * HALF_MS:  # the UTC day is over: the archive zip may hold it (published after ~00:30Z)
        cache = day_cache if day_cache is not None else {}
        if day not in cache:
            try:
                cache[day] = archive_day(day)
            except Exception as e:  # noqa: BLE001
                log("archive %s: %s" % (day, e))
                cache[day] = None
        if cache[day] is not None:
            rec = build_from_arrays(cache[day], start_ms, "archive", now_ms, tf_ms=tf_ms)
            rec["partial"] = False
            save_bar(rec, outdir, tf)
            return rec
    if not rest:
        return None
    prior = load_bar(start_ms, outdir, tf)
    # intraday bars are small: rebuild them whole so the p99.9 threshold is exact; only the 12h bar resumes by agg id
    prior = prior if tf_ms == HALF_MS and prior and prior.get("partial") and prior.get("last_agg_id") and prior.get("source") != "archive" else None
    try:
        arr, complete = rest_trades(start_ms, end_ms, prior and prior["last_agg_id"], max_pages=max_pages, log=log)
    except Exception as e:  # noqa: BLE001
        log("rest %s: %s" % (start_ms, e))
        return None
    if arr[0].size == 0 and not prior:
        return None
    rec = build_from_arrays(arr, start_ms, "rest", now_ms, complete_hint=complete, prior=prior, tf_ms=tf_ms)
    if now_ms >= end_ms and not complete:
        rec["partial"] = True
    save_bar(rec, outdir, tf)
    return rec


def ensure(now_ms=None, days=BACKFILL_DAYS, outdir=None, rest=True, log=print, tf_ms=HALF_MS):
    """Rebuild only missing or partial bars of the last `days` days up to and including the forming bar. Returns {built, ok, gaps}."""
    now_ms = now_ms or int(time.time() * 1000)
    cur = bar_start_of(now_ms, tf_ms)
    first = cur - (days * 2 * HALF_MS) // tf_ms * tf_ms
    built, gaps, cache = [], [], {}
    s = first
    rest_from = cur - min(3 * HALF_MS, 12 * tf_ms)  # older archive gaps stay gaps (12 min of REST each at 12h)
    while s <= cur:
        if needs_build(s, now_ms, outdir, tf_ms):
            use_rest = rest and s >= rest_from
            rec = build_bar(s, now_ms, outdir, cache, use_rest, log, tf_ms=tf_ms)
            (built if rec else gaps).append(s)
            if rec:
                log("%s %s%s delta %+.1f" % (rec["bar_start_utc"], rec["source"], " PARTIAL" if rec["partial"] else "", rec["delta"]))
        s += tf_ms
        if s % (2 * HALF_MS) == 0:
            cache.clear()
    return {"built": built, "gaps": gaps}


# ---------- US-session bias ----------
def load_recent(now_ms=None, days=BACKFILL_DAYS, outdir=None):
    now_ms = now_ms or int(time.time() * 1000)
    out, s = [], bar_start_of(now_ms) - days * 2 * HALF_MS
    while s <= bar_start_of(now_ms):
        b = load_bar(s, outdir)
        if b:
            out.append(b)
        s += HALF_MS
    return out


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    return None if not n else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0)


def us_bias_inputs(now_ms=None, price=None, outdir=None, bars=None):
    """For the last 2 COMPLETED 12h bars: delta sign and size vs the 30-day median |delta|, price vs the bar's POC and value area,
    nearest unfilled stacked imbalance (across both bars), biggest absorption. Anything unreadable is UNKNOWN."""
    now_ms = now_ms or int(time.time() * 1000)
    bars = bars if bars is not None else load_recent(now_ms, outdir=outdir)
    done = [b for b in bars if not b.get("partial") and b["bar_end_ms"] <= now_ms]
    if len(done) < 1:
        return {"status": UNKNOWN, "why": "no completed bar on disk", "label": LABEL}
    med = _median([abs(b["delta"]) for b in done])
    last2 = done[-2:]
    out = {"status": "ok", "label": LABEL, "asof_ms": now_ms, "latest_bar": done[-1]["bar_start_utc"], "median_abs_delta": med, "bars": []}
    for b in reversed(last2):  # newest first
        d = b["delta"]
        e = {"bar": b["bar_start_utc"], "delta": d, "side": "buyers" if d > 0 else "sellers" if d < 0 else "flat",
             "x_median": round(abs(d) / med, 2) if med else UNKNOWN, "poc": b["poc"], "va": b["value_area"]}
        if price is not None and b["poc"] is not None:
            va = b["value_area"]
            e["price_vs_poc"] = "above" if price > b["poc"] else "below" if price < b["poc"] else "at"
            e["price_vs_va"] = "above" if price > va["high"] + b.get("bucket_usd", BUCKET_USD) else "below" if price < va["low"] else "inside"
        else:
            e["price_vs_poc"] = e["price_vs_va"] = UNKNOWN
        out["bars"].append(e)
    after = [b for b in bars if b["bar_start_ms"] > last2[0]["bar_start_ms"]]
    cands = []
    for b in last2:
        later = [x for x in bars if x["bar_start_ms"] > b["bar_start_ms"]]
        lo = min([x["low"] for x in later if x.get("low")] or [None]) if later else None
        hi = max([x["high"] for x in later if x.get("high")] or [None]) if later else None
        for s in b["stacks"]:
            filled = (s["side"] == "buy" and lo is not None and lo < s["low"]) or (s["side"] == "sell" and hi is not None and hi > s["high"])
            if not filled:
                cands.append(dict(s, bar=b["bar_start_utc"]))
    out["nearest_stack"] = UNKNOWN
    if price is not None and cands:
        c = min(cands, key=lambda s: 0 if s["low"] <= price <= s["high"] else min(abs(price - s["low"]), abs(price - s["high"])))
        out["nearest_stack"] = c
    elif price is None:
        out["nearest_stack"] = UNKNOWN
    else:
        out["nearest_stack"] = None
    ab = [dict(a, bar=b["bar_start_utc"]) for b in last2 for a in b["absorptions"]]
    out["biggest_absorption"] = max(ab, key=lambda a: a["vol"]) if ab else None
    out["price"] = price if price is not None else UNKNOWN
    return out


def _k(x):
    return "%+.2fK" % (x / 1000.0) if abs(x) >= 1000 else "%+.0f" % x


def bias_line(inp):
    """ONE plain line for the Live Aid US open panel."""
    if inp.get("status") != "ok":
        return "12h footprint: UNKNOWN (%s) [%s]" % (inp.get("why", "no data"), LABEL)
    b = inp["bars"][0]
    x = ("%.1fx normal" % b["x_median"]) if isinstance(b["x_median"], float) else "size vs normal UNKNOWN"
    who = {"buyers": "buyers won", "sellers": "sellers won", "flat": "no side won"}[b["side"]]
    parts = ["%s last bar (%s, %s)" % (who, _k(b["delta"]), x)]
    if b["price_vs_poc"] != UNKNOWN:
        parts.append("price %s its POC %s%s" % (b["price_vs_poc"], "{:,.0f}".format(b["poc"]),
                                                "" if b["price_vs_va"] == "inside" else " and %s its value area" % b["price_vs_va"]))
    else:
        parts.append("price vs POC %s UNKNOWN" % "{:,.0f}".format(b["poc"]))
    s = inp["nearest_stack"]
    if isinstance(s, dict):
        parts.append("nearest %s wall %s" % ("buyer" if s["side"] == "buy" else "seller", "{:,.0f}".format((s["low"] + s["high"]) / 2.0)))
    elif s is None:
        parts.append("no unfilled stacked imbalance")
    a = inp["biggest_absorption"]
    if a:
        parts.append("biggest absorption %s (%.0f BTC)" % ("{:,.0f}".format(a["price"]), a["vol"]))
    return "12h footprint: " + "; ".join(parts) + " [" + LABEL + "]"


def tf_line(tf, bar, price=None):
    """ONE short line for a 15m / 1h / 2h bar: delta, price vs POC, largest print. UNKNOWN when there is no bar."""
    if not bar:
        return "%s footprint: UNKNOWN (no bar on disk) [%s]" % (tf, LABEL)
    parts = ["delta %s BTC" % ("%+.1f" % bar["delta"])]
    ref = price if price is not None else bar.get("close")
    if bar.get("poc") is not None and ref is not None:
        parts.append("price %s POC %s" % ("above" if ref > bar["poc"] else "below" if ref < bar["poc"] else "at", "{:,.0f}".format(bar["poc"])))
    else:
        parts.append("price vs POC UNKNOWN")
    lt = bar.get("large_trades") or []
    if lt:
        t = max(lt, key=lambda x: (x[2], -x[0]))
        parts.append("largest print %.0f BTC %s @ %s" % (t[2], t[3], "{:,.0f}".format(t[1])))
    else:
        parts.append("no large print")
    return "%s footprint%s: %s [%s]" % (tf, " (forming)" if bar.get("partial") else "", "; ".join(parts), LABEL)


def tf_lines(now_ms=None, price=None, outdirs=None, tfs=("15m", "1h", "2h")):
    """{tf: {line, bar_start_ms, partial}} from the newest bar on disk of each tf (the forming bar, else the one before)."""
    now_ms = now_ms or int(time.time() * 1000)
    out = {}
    for tf in tfs:
        ms, od = TF_MS[tf], (outdirs or {}).get(tf)
        bar = None
        for s in (bar_start_of(now_ms, ms), bar_start_of(now_ms, ms) - ms):
            bar = load_bar(s, od, tf)
            if bar:
                break
        out[tf] = {"line": tf_line(tf, bar, price), "bar_start_ms": bar["bar_start_ms"] if bar else None,
                   "partial": bool(bar and bar.get("partial"))}
    return out


def live_price(fetch=None):
    try:
        j = json.loads(_get("https://fapi.binance.com/fapi/v1/ticker/price?symbol=" + SYMBOL, timeout=10).decode())
        return float(j["price"])
    except Exception:  # noqa: BLE001
        return None


def write_js(path=None, now_ms=None, price=None, outdir=None):
    """footprint_bias_data.js (git-ignored, like playbook_data.js) for live_aid.html."""
    now_ms = now_ms or int(time.time() * 1000)
    inp = us_bias_inputs(now_ms, price, outdir)
    last_done = bar_start_of(now_ms) - HALF_MS
    data = {"line": bias_line(inp), "built_ms": now_ms, "latest_completed_bar_ms": last_done, "label": LABEL,
            "have_latest": bool(load_bar(last_done, outdir) and not load_bar(last_done, outdir).get("partial")), "inputs": inp,
            "tf": tf_lines(now_ms, price)}
    p = Path(path or JS_OUT)
    p.write_text("window.FOOTPRINT_BIAS = " + json.dumps(data) + ";\n", encoding="utf-8", newline="\n")
    return p, data


def build_footprint(root=ROOT, log=print):
    """Called by us_prep.py: ensure the record, then write the Live Aid js. One status line; never raises."""
    try:
        r = ensure(log=log)
        for tf in ("15m", "1h"):  # the forming bar only: the cadence timer in Live Aid re-reads it; deeper history = --tf ... --days
            ensure(days=0, log=log, tf_ms=TF_MS[tf])
        p, d = write_js(price=live_price())
        return "FOOTPRINT ok: built %d, gaps %d; %s" % (len(r["built"]), len(r["gaps"]), d["line"])
    except Exception as e:  # noqa: BLE001
        return "FOOTPRINT FAILED: %s" % e


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tf", choices=TF_ORDER, default="12h", help="bar length; files go to D:/MTS_data/footprint_<tf>/ (12h = the shipped record)")
    ap.add_argument("--days", type=int, default=None, help="default 30 for 12h, 1 for the shorter bars")
    ap.add_argument("--no-rest", action="store_true")
    ap.add_argument("--line", action="store_true", help="print the bias line")
    ap.add_argument("--js", action="store_true", help="also write footprint_bias_data.js")
    a = ap.parse_args(argv)
    days = a.days if a.days is not None else (BACKFILL_DAYS if a.tf == "12h" else 1)
    r = ensure(days=days, rest=not a.no_rest, tf_ms=TF_MS[a.tf])
    print("built %d bars, %d gaps" % (len(r["built"]), len(r["gaps"])))
    px = live_price()
    if a.js:
        print("wrote", write_js(price=px)[0])
    if a.line or a.js:
        print(bias_line(us_bias_inputs(price=px)))


if __name__ == "__main__":
    main()
