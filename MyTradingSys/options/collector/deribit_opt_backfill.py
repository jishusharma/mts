"""Deribit BTC options historical backfill (public market data only, read-only, no keys, no orders).

Resumable: every series keeps a cursor (data/hist/_cursors.json) plus the data itself; trades are stored as one
immutable shard per UTC day. Re-running only fetches what is missing (newer gap first, then older history).

Outputs under options/data/hist/ (schemas: collector/README.md):
  dvol_1h.csv dvol_1d.csv            DVOL OHLC            get_volatility_index_data (continuation pagination)
  perp_1h.csv perp_1d.csv            BTC-PERPETUAL OHLCV  get_tradingview_chart_data (5000-bar windows)
  funding.csv                        hourly funding       get_funding_rate_history (30-day windows)
  delivery_prices.csv                btc_usd daily 08:00 settlement price   get_delivery_prices (offset pages of 100)
  instruments_expired.jsonl.gz       get_instruments expired=true, merged over runs (API only serves the last expiry)
  trades/YYYY-MM-DD.jsonl.gz         every BTC option trade of that UTC day, plus trades/_manifest.jsonl
  instruments_from_trades.csv        every option instrument ever seen in the trade shards (derived)
  _depth_report.json                 what the live and history hosts really serve (probe)

Trades come from https://history.deribit.com (Deribit's public history host, same /api/v2/public API, no auth).
The live host www.deribit.com only serves roughly the last 24 hours of trades (verified by probe, see README).

Run:  python MyTradingSys/options/collector/deribit_opt_backfill.py --max-seconds 1500
      python MyTradingSys/options/collector/deribit_opt_backfill.py --only dvol,perp --max-seconds 300
      python MyTradingSys/options/collector/deribit_opt_backfill.py --report
"""
import argparse
import csv
import gzip
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_opt_common as C  # noqa: E402

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TV_MAX_BARS = 5000                    # get_tradingview_chart_data returns at most 5001 bars
FUNDING_WINDOW_MS = 30 * C.DAY_MS     # get_funding_rate_history returns at most 744 hourly rows
TV_FLOOR_MS = C.date_to_ms("2018-08-01")      # BTC-PERPETUAL launched 2018-08-14
FUNDING_FLOOR_MS = C.date_to_ms("2018-08-01")
EMPTY_WINDOWS_STOP = 3
TRADE_DROP_KEYS = ("starbase_match_id", "starbase_timestamp")  # matching-engine internals, large and useless
TRADES_METHOD = "public/get_last_trades_by_currency_and_time"

SERIES = {
    "dvol_1h": ("dvol_1h.csv", ("ts_ms", "open", "high", "low", "close")),
    "dvol_1d": ("dvol_1d.csv", ("ts_ms", "open", "high", "low", "close")),
    "perp_1h": ("perp_1h.csv", ("ts_ms", "open", "high", "low", "close", "volume", "cost")),
    "perp_1d": ("perp_1d.csv", ("ts_ms", "open", "high", "low", "close", "volume", "cost")),
    "funding": ("funding.csv", ("ts_ms", "interest_8h", "interest_1h", "index_price", "prev_index_price")),
}


class Stop(Exception):
    """Raised inside a worker when the hard deadline passes; the unfinished day is discarded."""


def _log(msg):
    print("%s %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


# ---------------------------------------------------------------- series store + cursors

def _fmt(v):
    return "" if v is None else repr(v) if isinstance(v, float) else str(v)


class SeriesStore:
    """ts_ms-keyed rows persisted as a sorted CSV (atomic rewrite). Values are kept as text."""

    def __init__(self, path, cols):
        self.path = Path(path)
        self.cols = tuple(cols)
        self.rows = {}

    def __len__(self):
        return len(self.rows)

    def load(self):
        self.rows = {}
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8", newline="") as f:
                rd = csv.reader(f)
                header = next(rd, None)
                if header is not None and tuple(header) != self.cols:
                    raise ValueError("%s: header %r != expected %r" % (self.path, header, self.cols))
                for row in rd:
                    if row:
                        self.rows[int(row[0])] = row
        return self

    def add(self, rows):
        """Add/replace rows (sequences starting with ts_ms). Returns the number of NEW timestamps."""
        new = 0
        for r in rows:
            ts = int(r[0])
            if ts not in self.rows:
                new += 1
            self.rows[ts] = [_fmt(v) for v in r]
        return new

    def earliest(self):
        return min(self.rows) if self.rows else None

    def latest(self):
        return max(self.rows) if self.rows else None

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(self.cols)
            for ts in sorted(self.rows):
                w.writerow(self.rows[ts])
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)


class Cursors:
    def __init__(self, path):
        self.path = Path(path)
        self.data = C.read_json(self.path, {}) or {}
        self._lock = threading.Lock()

    def get(self, name):
        return dict(self.data.get(name, {}))

    def set(self, name, **kw):
        with self._lock:
            d = self.data.setdefault(name, {})
            d.update(kw)
            d["updated"] = C.iso(C.now_ms())
            C.atomic_write_json(self.path, self.data)


def walk_series(name, store, cursors, fetch_page, now_ms, deadline, clock=time.monotonic, flush_every=10, log=_log):
    """Resumable newest-to-oldest walk.

    fetch_page(end_ms) -> (rows, next_end_ms | None); next_end_ms None means nothing older exists.
    Invariant: the stored rows are one contiguous block [earliest, latest] (walks always start at `now` or just
    below the stored earliest), so a rerun needs (1) the newer gap, found by walking back from now until a page
    overlaps the stored latest, then (2) the older history below the stored earliest, until exhausted.
    """
    store.load()
    cur = cursors.get(name)
    complete = bool(cur.get("complete_back"))
    stats = {"name": name, "pages": 0, "added": 0, "reason": None, "complete_back": complete}

    def flush():
        cursors.set(name, complete_back=stats["complete_back"], earliest_ms=store.earliest(), latest_ms=store.latest(),
                    rows=len(store))
        store.save()

    def run(end_ms, stop_ts):
        since = 0
        while True:
            if clock() >= deadline:
                return "deadline"
            rows, next_end = fetch_page(end_ms)
            stats["pages"] += 1
            stats["added"] += store.add(rows)
            since += 1
            if since >= flush_every:
                flush()
                since = 0
            if stop_ts is not None and rows and min(int(r[0]) for r in rows) <= stop_ts:
                return "overlap"
            if next_end is None:
                return "exhausted"
            if next_end >= end_ms:
                return "no_progress"
            end_ms = next_end

    try:
        latest = store.latest()
        reason = run(now_ms, latest)
        if reason == "exhausted":
            stats["complete_back"] = True
        elif reason == "overlap" and not stats["complete_back"]:
            reason = run(store.earliest() - 1, None)
            if reason == "exhausted":
                stats["complete_back"] = True
        stats["reason"] = reason
    finally:
        flush()
    stats["rows"] = len(store)
    stats["earliest_ms"], stats["latest_ms"] = store.earliest(), store.latest()
    log("%s: pages=%d new=%d rows=%d %s..%s reason=%s complete_back=%s" % (
        name, stats["pages"], stats["added"], len(store),
        C.iso(store.earliest()) if store.rows else "-", C.iso(store.latest()) if store.rows else "-",
        stats["reason"], stats["complete_back"]))
    return stats


# ---------------------------------------------------------------- page fetchers (one per endpoint)

def make_dvol_fetch(client, resolution):
    """get_volatility_index_data: with start_timestamp=0 it returns the newest <=1000 points up to end_timestamp
    plus `continuation` = the end_timestamp for the next older page (absent at the start of the data)."""
    def fetch(end_ms):
        res = client.call("public/get_volatility_index_data", {"currency": "BTC", "start_timestamp": 0,
                                                                "end_timestamp": end_ms, "resolution": resolution})
        return [list(r) for r in (res.get("data") or [])], res.get("continuation")
    return fetch


def make_perp_fetch(client, resolution, step_ms):
    """get_tradingview_chart_data BTC-PERPETUAL: window [end - 5000 bars, end]; max 5001 bars per call."""
    state = {"empty": 0}

    def fetch(end_ms):
        start = end_ms - TV_MAX_BARS * step_ms
        res = client.call("public/get_tradingview_chart_data", {"instrument_name": "BTC-PERPETUAL",
                                                                 "start_timestamp": start, "end_timestamp": end_ms,
                                                                 "resolution": resolution})
        ticks = res.get("ticks") or []
        rows = [[ticks[i], res["open"][i], res["high"][i], res["low"][i], res["close"][i],
                 res["volume"][i], res["cost"][i]] for i in range(len(ticks))]
        state["empty"] = 0 if rows else state["empty"] + 1
        nxt = start - 1
        if state["empty"] >= 2 or nxt < TV_FLOOR_MS:
            nxt = None
        return rows, nxt
    return fetch


def make_funding_fetch(client):
    """get_funding_rate_history BTC-PERPETUAL: hourly rows in [end - 30d, end] (<= 744 per call)."""
    state = {"empty": 0}

    def fetch(end_ms):
        start = end_ms - FUNDING_WINDOW_MS
        res = client.call("public/get_funding_rate_history", {"instrument_name": "BTC-PERPETUAL",
                                                               "start_timestamp": start, "end_timestamp": end_ms})
        rows = [[r["timestamp"], r.get("interest_8h"), r.get("interest_1h"), r.get("index_price"),
                 r.get("prev_index_price")] for r in (res or [])]
        state["empty"] = 0 if rows else state["empty"] + 1
        nxt = start - 1
        if state["empty"] >= EMPTY_WINDOWS_STOP or nxt < FUNDING_FLOOR_MS:
            nxt = None
        return rows, nxt
    return fetch


# ---------------------------------------------------------------- delivery prices, expired instruments

def backfill_delivery(client, hist_dir, cursors, deadline, clock=time.monotonic, log=_log):
    """get_delivery_prices btc_usd: newest first, 100 per page, offset pagination. Stops early once a page is
    entirely known and the older history was already completed."""
    path = Path(hist_dir) / "delivery_prices.csv"
    store = SeriesStore(path, ("ts_ms", "date", "delivery_price"))
    store.load()
    cur = cursors.get("delivery_prices")
    complete = bool(cur.get("complete_back"))
    offset, pages, added, reason = 0, 0, 0, "exhausted"
    try:
        while True:
            if clock() >= deadline:
                reason = "deadline"
                break
            res = client.call("public/get_delivery_prices", {"index_name": "btc_usd", "offset": offset, "count": 100})
            data = res.get("data") or []
            total = res.get("records_total", 0)
            pages += 1
            page_new = 0
            for d in data:
                ts = C.date_to_ms(d["date"])
                known = store.rows.get(ts)
                if known is None or known[2] != _fmt(d["delivery_price"]):
                    page_new += 1
                store.add([[ts, d["date"], d["delivery_price"]]])
            added += page_new
            offset += len(data)
            if not data or offset >= total:
                complete = True
                break
            if complete and page_new == 0:
                reason = "overlap"
                break
    finally:
        cursors.set("delivery_prices", complete_back=complete, earliest_ms=store.earliest(), latest_ms=store.latest(),
                    rows=len(store))
        store.save()
    log("delivery_prices: pages=%d changed=%d rows=%d %s..%s reason=%s" % (
        pages, added, len(store), C.iso(store.earliest()) if store.rows else "-",
        C.iso(store.latest()) if store.rows else "-", reason))
    return {"name": "delivery_prices", "pages": pages, "added": added, "rows": len(store), "reason": reason}


def merge_expired_instruments(client, hist_dir, now_ms, log=_log):
    """get_instruments(expired=true) only serves the most recent expiry day (no pagination exists), so this is
    merged into a growing file: run it at least every few days to lose nothing."""
    path = Path(hist_dir) / "instruments_expired.jsonl.gz"
    known = {}
    if path.exists():
        for line in C.read_gz_lines(path):
            if line.strip():
                d = json.loads(line)
                known[d["instrument_name"]] = d
    res = client.call("public/get_instruments", {"currency": "BTC", "kind": "option", "expired": "true"})
    new = 0
    for ins in res or []:
        if ins["instrument_name"] not in known:
            new += 1
            ins = dict(ins)
            ins["_first_seen_ms"] = now_ms
            known[ins["instrument_name"]] = ins
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(tmp, "wt", encoding="utf-8", newline="\n") as f:
        for name in sorted(known):
            f.write(json.dumps(known[name], separators=(",", ":")) + "\n")
    os.replace(tmp, path)
    log("instruments_expired: api_rows=%d new=%d total=%d" % (len(res or []), new, len(known)))
    return {"name": "instruments_expired", "api_rows": len(res or []), "new": new, "rows": len(known)}


# ---------------------------------------------------------------- trades

def _trade_line(t):
    return json.dumps({k: v for k, v in t.items() if k not in TRADE_DROP_KEYS}, separators=(",", ":")) + "\n"


def fetch_day(client, day_ms, count, tmp_path, hard_deadline, clock=time.monotonic):
    """Fetch every BTC option trade of the UTC day [day_ms, day_ms+24h) into tmp_path (gzip, one JSON per line).
    Pagination: sorting=asc, next page starts AT the last timestamp (inclusive) and trades already written for that
    millisecond are skipped by trade_id, so same-ms trades split across a page boundary are neither lost nor doubled.
    Returns meta dict. Raises Stop if hard_deadline passes (caller discards tmp_path)."""
    end_ms = day_ms + C.DAY_MS - 1
    start = day_ms
    boundary = set()
    n = calls = same_ms_advances = out_of_window = 0
    first_ts = last_ts = None
    with gzip.open(tmp_path, "wt", encoding="utf-8", newline="\n") as f:
        while True:
            if clock() > hard_deadline:
                raise Stop()
            res = client.call(TRADES_METHOD, {"currency": "BTC", "kind": "option", "start_timestamp": start,
                                              "end_timestamp": end_ms, "count": count, "sorting": "asc"})
            calls += 1
            trades = res.get("trades") or []
            wrote = 0
            for t in trades:
                ts = t["timestamp"]
                if ts == start and t["trade_id"] in boundary:
                    continue
                if ts < day_ms or ts > end_ms:
                    out_of_window += 1
                    continue
                f.write(_trade_line(t))
                wrote += 1
                if first_ts is None:
                    first_ts = ts
                last_ts = ts
            n += wrote
            if not res.get("has_more") or not trades:
                break
            page_last = trades[-1]["timestamp"]
            ids_last = {t["trade_id"] for t in trades if t["timestamp"] == page_last}
            if page_last == start:
                if wrote == 0:  # a full page of already-written same-ms trades: step past that ms (only lossy if
                    # more than `count` trades share ONE millisecond, which the API cannot page through at all)
                    same_ms_advances += 1
                    start = page_last + 1
                    boundary = set()
                    continue
                ids_last |= boundary
            boundary = ids_last
            start = page_last
    return {"n_trades": n, "calls": calls, "first_ts": first_ts, "last_ts": last_ts, "same_ms_advances": same_ms_advances,
            "out_of_window": out_of_window}


class Manifest:
    def __init__(self, path):
        self.path = Path(path)
        self.done = {}
        self._lock = threading.Lock()
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        self.done[d["date"]] = d
                    except (ValueError, KeyError):
                        continue

    def add(self, entry):
        with self._lock:
            with open(self.path, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(entry, separators=(",", ":")) + "\n")
                f.flush()
                os.fsync(f.fileno())
            self.done[entry["date"]] = entry


def day_list(date_from, date_to):
    """UTC day starts (ms), newest first, from date_to down to date_from inclusive."""
    lo, hi = C.date_to_ms(date_from), C.date_to_ms(date_to)
    return list(range(hi, lo - 1, -C.DAY_MS))


def backfill_trades(client, hist_dir, date_from, date_to, workers, count, soft_deadline, hard_deadline,
                    clock=time.monotonic, log=_log, max_fail_streak=8):
    """Newest-first, one shard per UTC day, `workers` days in parallel (requests are rate limited globally).
    Resume = shards in the manifest are skipped; unfinished days (tmp files) are refetched from scratch."""
    tdir = Path(hist_dir) / "trades"
    tdir.mkdir(parents=True, exist_ok=True)
    for stale in tdir.glob("*.tmp"):
        stale.unlink()
    manifest = Manifest(tdir / "_manifest.jsonl")
    days = [d for d in day_list(date_from, date_to) if C.utc_date(d) not in manifest.done]
    tally = {"days_total": len(day_list(date_from, date_to)), "days_already": len(day_list(date_from, date_to)) - len(days),
             "days_done": 0, "days_failed": 0, "trades": 0, "calls": 0, "aborted": 0, "skipped_deadline": 0}
    lock = threading.Lock()
    state = {"fail_streak": 0, "abort": False}

    def work(day_ms):
        if state["abort"] or clock() >= soft_deadline:
            with lock:
                tally["skipped_deadline"] += 1
            return
        date = C.utc_date(day_ms)
        tmp = tdir / (date + ".jsonl.gz.tmp")
        final = tdir / (date + ".jsonl.gz")
        try:
            meta = fetch_day(client, day_ms, count, tmp, hard_deadline, clock)
        except Stop:
            tmp.unlink(missing_ok=True)
            with lock:
                tally["aborted"] += 1
            return
        except Exception as e:  # noqa: BLE001 - one failed day must not kill the others
            tmp.unlink(missing_ok=True)
            with lock:
                tally["days_failed"] += 1
                state["fail_streak"] += 1
                if state["fail_streak"] >= max_fail_streak:
                    state["abort"] = True
            log("trades %s FAILED: %s: %s" % (date, type(e).__name__, e))
            return
        if meta["n_trades"] > 0:
            os.replace(tmp, final)
            meta["file"] = final.name
            meta["bytes"] = final.stat().st_size
        else:
            tmp.unlink(missing_ok=True)
            meta["file"] = None
            meta["bytes"] = 0
        meta["date"] = date
        meta["fetched_ms"] = C.now_ms()
        manifest.add(meta)
        with lock:
            state["fail_streak"] = 0
            tally["days_done"] += 1
            tally["trades"] += meta["n_trades"]
            tally["calls"] += meta["calls"]
            if tally["days_done"] % 25 == 0:
                log("trades: %d days done (latest %s n=%d), %d trades so far" % (
                    tally["days_done"], date, meta["n_trades"], tally["trades"]))

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        list(ex.map(work, days))
    log("trades: %s" % json.dumps(tally))
    return tally


# ---------------------------------------------------------------- depth probe, derived instrument table, report

def probe_depth(live, history, now_ms, hist_dir=None, log=_log):
    """Earliest option trade each host serves (start_timestamp=0, sorting=asc, count=1) + live-host window probe."""
    rep = {"probed_at": C.iso(now_ms)}
    for label, cl in (("live_www", live), ("history", history)):
        res = cl.call(TRADES_METHOD, {"currency": "BTC", "kind": "option", "start_timestamp": 0, "end_timestamp": now_ms,
                                      "count": 1, "sorting": "asc"})
        t = (res.get("trades") or [None])[0]
        rep[label + "_earliest_trade"] = None if t is None else {"ts_ms": t["timestamp"], "iso": C.iso(t["timestamp"]),
                                                                  "instrument": t["instrument_name"]}
    ages_h = (6, 12, 18, 23, 24, 25, 30, 48, 24 * 7, 24 * 30)
    win = {}
    for h in ages_h:
        e = now_ms - h * C.HOUR_MS
        res = live.call(TRADES_METHOD, {"currency": "BTC", "kind": "option", "start_timestamp": e - C.HOUR_MS,
                                        "end_timestamp": e, "count": 1, "sorting": "asc"})
        win[str(h)] = len(res.get("trades") or [])
    rep["live_www_trades_in_1h_window_by_age_hours"] = win
    if hist_dir:
        C.atomic_write_json(Path(hist_dir) / "_depth_report.json", rep)
    log("depth: %s" % json.dumps(rep))
    return rep


_NAME_RE = re.compile(r'"instrument_name":"([^"]+)"')
_TS_RE = re.compile(r'"timestamp":(\d+)')
_INST_RE = re.compile(r"^BTC-(\d{1,2})([A-Z]{3})(\d{2})-(\d+)-([CP])$")


def derive_instruments(hist_dir, log=_log):
    """Scan the trade shards -> instruments_from_trades.csv (every option instrument that ever traded)."""
    stats = {}
    shards = sorted((Path(hist_dir) / "trades").glob("*.jsonl.gz"))
    for sh in shards:
        with gzip.open(sh, "rt", encoding="utf-8") as f:
            for line in f:
                m = _NAME_RE.search(line)
                t = _TS_RE.search(line)
                if not m or not t:
                    continue
                nm, ts = m.group(1), int(t.group(1))
                s = stats.get(nm)
                if s is None:
                    stats[nm] = [ts, ts, 1]
                else:
                    if ts < s[0]:
                        s[0] = ts
                    if ts > s[1]:
                        s[1] = ts
                    s[2] += 1
    out = Path(hist_dir) / "instruments_from_trades.csv"
    tmp = out.with_name(out.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(("instrument_name", "expiry_code", "strike", "type", "first_trade_ms", "last_trade_ms", "n_trades"))
        for nm in sorted(stats):
            m = _INST_RE.match(nm)
            code = "%s%s%s" % (m.group(1), m.group(2), m.group(3)) if m else ""
            w.writerow((nm, code, m.group(4) if m else "", m.group(5) if m else "", *stats[nm]))
    os.replace(tmp, out)
    log("instruments_from_trades: shards=%d instruments=%d" % (len(shards), len(stats)))
    return {"shards": len(shards), "instruments": len(stats)}


def report(data_dir):
    """Facts parsed from the files themselves (never from logs)."""
    hist = Path(data_dir) / "hist"
    out = {"series": {}, "files": {}}
    for name, (fn, cols) in SERIES.items():
        p = hist / fn
        if p.exists():
            st = SeriesStore(p, cols).load()
            out["series"][name] = {"rows": len(st), "first": C.iso(st.earliest()) if st.rows else None,
                                   "last": C.iso(st.latest()) if st.rows else None, "bytes": p.stat().st_size}
    p = hist / "delivery_prices.csv"
    if p.exists():
        st = SeriesStore(p, ("ts_ms", "date", "delivery_price")).load()
        out["series"]["delivery_prices"] = {"rows": len(st), "first": C.iso(st.earliest()), "last": C.iso(st.latest()),
                                            "bytes": p.stat().st_size}
    p = hist / "instruments_expired.jsonl.gz"
    if p.exists():
        out["series"]["instruments_expired"] = {"rows": C.count_gz_lines(p), "bytes": p.stat().st_size}
    p = hist / "instruments_from_trades.csv"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            out["series"]["instruments_from_trades"] = {"rows": sum(1 for _ in f) - 1, "bytes": p.stat().st_size}
    tdir = hist / "trades"
    if tdir.exists():
        shards = sorted(tdir.glob("*.jsonl.gz"))
        n = 0
        for sh in shards:
            n += C.count_gz_lines(sh)
        man = Manifest(tdir / "_manifest.jsonl")
        dates = sorted(man.done)
        nonempty = [d for d in dates if man.done[d].get("n_trades")]
        out["trades"] = {"shard_files": len(shards), "trades_in_shards": n,
                         "bytes": sum(s.stat().st_size for s in shards),
                         "manifest_days": len(dates), "manifest_first_day": dates[0] if dates else None,
                         "manifest_last_day": dates[-1] if dates else None,
                         "first_day_with_trades": nonempty[0] if nonempty else None,
                         "empty_days": len(dates) - len(nonempty),
                         "manifest_trades_sum": sum(man.done[d].get("n_trades", 0) for d in dates)}
    cdir = Path(data_dir) / "chain"
    if cdir.exists():
        files = sorted(cdir.glob("*.jsonl.gz"))
        out["chain"] = {"files": len(files), "snapshots": sum(C.count_gz_lines(f) for f in files),
                        "bytes": sum(f.stat().st_size for f in files)}
    return out


# ---------------------------------------------------------------- orchestration

def main(argv=None, clients=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    ap.add_argument("--only", default="instruments,delivery,dvol,perp,funding,trades",
                    help="comma list of: instruments,delivery,dvol,perp,funding,trades")
    ap.add_argument("--max-seconds", type=float, default=1500, help="total wall-clock cap (soft)")
    ap.add_argument("--grace", type=float, default=90, help="extra seconds in-flight trade days may use after the cap")
    ap.add_argument("--trades-from", default=None, help="earliest UTC day YYYY-MM-DD (default: first day with trades)")
    ap.add_argument("--trades-to", default=None, help="latest UTC day (default: yesterday, complete days only)")
    ap.add_argument("--workers", type=int, default=4, help="parallel trade days")
    ap.add_argument("--trade-count", type=int, default=10000, help="trades per page (API max 10000)")
    ap.add_argument("--rate", type=float, default=4.0, help="global max requests/second (hard cap 5)")
    ap.add_argument("--report", action="store_true", help="print facts parsed from the files and exit")
    ap.add_argument("--derive-instruments", action="store_true", help="only rebuild instruments_from_trades.csv")
    ap.add_argument("--no-derive", action="store_true", help="skip the instruments_from_trades.csv rebuild")
    a = ap.parse_args(argv)

    data_dir = Path(a.data_dir)
    hist = data_dir / "hist"
    hist.mkdir(parents=True, exist_ok=True)
    if a.report:
        print(json.dumps(report(data_dir), indent=1, sort_keys=True))
        return 0
    if a.derive_instruments:
        derive_instruments(hist)
        return 0

    only = {s.strip() for s in a.only.split(",") if s.strip()}
    t0 = time.monotonic()
    soft = t0 + a.max_seconds
    hard = soft + a.grace
    live, history = clients or (C.DeribitPublic(C.LIVE_BASE, rate=a.rate, log=_log),
                                C.DeribitPublic(C.HISTORY_BASE, rate=a.rate, log=_log))
    cursors = Cursors(hist / "_cursors.json")
    now = C.now_ms()
    failures = []

    def guarded(label, fn):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            failures.append(label)
            _log("%s FAILED: %s: %s" % (label, type(e).__name__, e))

    if "instruments" in only:
        guarded("instruments", lambda: merge_expired_instruments(live, hist, now))
    if "delivery" in only:
        guarded("delivery", lambda: backfill_delivery(live, hist, cursors, soft))
    for key in ("dvol", "perp", "funding"):
        if key not in only:
            continue
        if key == "dvol":
            plan = [("dvol_1h", make_dvol_fetch(live, "3600")), ("dvol_1d", make_dvol_fetch(live, "1D"))]
        elif key == "perp":
            plan = [("perp_1h", make_perp_fetch(live, "60", C.HOUR_MS)), ("perp_1d", make_perp_fetch(live, "1D", C.DAY_MS))]
        else:
            plan = [("funding", make_funding_fetch(live))]
        for name, fetch in plan:
            fn, cols = SERIES[name]
            guarded(name, lambda n=name, f=fetch, p=hist / fn, c=cols: walk_series(n, SeriesStore(p, c), cursors, f, now, soft))
    if "trades" in only:
        def run_trades():
            rep = probe_depth(live, history, now, hist)
            first = (rep.get("history_earliest_trade") or {}).get("iso", "2016-11-29")[:10]
            d_from = a.trades_from or first
            d_to = a.trades_to or C.utc_date(now - C.DAY_MS)
            return backfill_trades(history, hist, d_from, d_to, a.workers, a.trade_count, soft, hard)
        guarded("trades", run_trades)
        if not a.no_derive:
            guarded("derive_instruments", lambda: derive_instruments(hist))
    _log("done in %.0fs; requests live=%d (retries %d) history=%d (retries %d); failures=%s" % (
        time.monotonic() - t0, live.n_requests, live.n_retries, history.n_requests, history.n_retries, failures or "none"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
