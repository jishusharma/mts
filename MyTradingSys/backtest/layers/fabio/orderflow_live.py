"""
MyTradingSys/backtest/layers/fabio/orderflow_live.py - LIVE 1m order-flow bar writer (roadmap R3).

Source of the contract (WHY_ENGINE_SILENT_2026-10-03.md:46): "Live order-flow bar writer (aggTrades -> 1m OF bars with
b99/fp/thr_days)". Consumer: the Fabio v3 shadow emitter (alerts/live_runner_cli.py.new, FABIO_V3_FLOW_COLS), which needs
1m bars carrying buy_vol, sell_vol, b99_buy_vol, b99_sell_vol, thr_days, fp over the whole NY window.

Schema = the offline module's, unchanged (orderflow_bars.COLUMNS, 27 columns, same semantics, same 10 USD fp bins, same
aggregate_day code path): t,o,h,l,c,buy_vol,sell_vol,delta,cvd_day,n_agg,n_trades,max_trade,b99_*,b999_*,thr99,thr999,
thr_days,poc_price,poc_delta,poc_vol,fp. Venue = Binance USD-M futures aggTrades (same as the offline archive).

Output (plain CSV so it can be appended live; the offline archive is gzip, written once per finished day):
  <out>/YYYY-MM-DD.csv         header = COLUMNS, one row per CLOSED UTC minute that had trades, ascending t
  <out>/_qhist/YYYY-MM-DD.json  that day's row-quantity histogram (feeds the 30-day causal thresholds of later days)
  <out>/_state.json             {"next_ms": first minute not yet written, "day", "cvd_day", "hist"}
Retention: CSVs older than --keep-days (default 10) are deleted; _qhist is kept (it is tiny and builds thresholds).

Big-trade thresholds are fixed for the day and causal: percentile of the prior 30 calendar days' histograms, read from
<out>/_qhist and the offline archive's _qhist (F:\\MTS\\data\\orderflow_1m\\_qhist). No prior day anywhere -> thr_days = 0
and the emitter refuses those bars (fail closed; own-day thresholds would be look-ahead).

Fetch: REST /fapi/v1/aggTrades, paged by fromId, resumable by minute (no websocket: nothing is lost on a restart and no
extra dependency). A minute is written only once it is closed. A restart re-reads from `next_ms`, so no minute is
duplicated or skipped; minutes without any trade are absent (the consumer treats a gap as "no window").

Run:  python -m MyTradingSys.backtest.layers.fabio.orderflow_live            (loop, 20 s poll)
      python -m MyTradingSys.backtest.layers.fabio.orderflow_live --once
"""
import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import orderflow_bars as ob

REPO = Path(__file__).resolve().parents[4]
DEFAULT_OUT = REPO / "MyTradingSys" / "runtime" / "orderflow_live"
OFFLINE_HIST = Path(r"F:\MTS\data\orderflow_1m\_qhist")
FAPI = "https://fapi.binance.com/fapi/v1/aggTrades"
PAGE = 1000
# Pages per cycle. aggTrades weight 20, Binance limit 2400/min, one cycle per 20 s: 25 x 20 x 3 = 1500/min.
# 200 hit HTTP 429 on a 15 h backfill (2026-10-07) and, all-or-nothing, never advanced.
MAX_PAGES = 25
# One minute with more than MAX_PAGES * PAGE trades (2026-10-14 12:30Z: 39,420 trades) can never complete in a normal cycle:
# the backfill chunk keeps only whole minutes before the last fetched one, so it stayed empty and next_ms never moved
# (writer silent 2 days, live health RED). Such a minute is refetched once with this bigger page budget.
OVERFLOW_PAGES = 50
MIN_MS = 60000


# ---------------------------------------------------------------- fetch
def default_fetch(symbol, start_ms=None, from_id=None, limit=PAGE):
    """One page of aggTrades as the raw JSON list. Network; tests inject a fake."""
    q = {"symbol": symbol, "limit": limit}
    if from_id is not None:
        q["fromId"] = from_id
    else:
        q["startTime"] = start_ms
    with urllib.request.urlopen(FAPI + "?" + urllib.parse.urlencode(q), timeout=15) as r:
        return json.loads(r.read())


def to_tuple(r):
    """Binance aggTrade JSON -> parse_agg_csv tuple (agg_id, price, qty, first_id, last_id, ts_ms, is_buyer_maker)."""
    return (int(r["a"]), float(r["p"]), float(r["q"]), int(r["f"]), int(r["l"]), int(r["T"]), bool(r["m"]))


def fetch_trades(fetch_fn, symbol, start_ms, end_ms, max_pages=MAX_PAGES):
    """(trades, capped, error): all aggTrades with start_ms <= T < end_ms, ascending, deduplicated by agg id.
    Stops after max_pages (backfill is continued next cycle). An error on the first page raises (the caller writes
    nothing); an error after it returns the pages already fetched as capped, with the error, so a backfill advances."""
    out, from_id, pages, err = [], None, 0, None
    while pages < max_pages:
        try:
            rows = fetch_fn(symbol, start_ms=start_ms, from_id=from_id, limit=PAGE)
        except Exception as exc:  # noqa: BLE001
            if not out:
                raise
            err = repr(exc)
            break
        pages += 1
        if not rows:
            break
        done = False
        for r in rows:
            t = to_tuple(r)
            if t[5] >= end_ms:
                done = True
                break
            if from_id is None or t[0] >= from_id:
                out.append(t)
        from_id = int(rows[-1]["a"]) + 1
        if done or len(rows) < PAGE:
            break
    return out, pages >= max_pages or err is not None, err


# ---------------------------------------------------------------- thresholds
def live_thresholds(day, hist_dirs, window=30):
    """(thr99, thr999, n_prior_days): percentiles of the summed histograms of days D-30..D-1 found in any of
    hist_dirs (a day present in several dirs counts once). (None, None, 0) if there is no prior day."""
    total, n = {}, 0
    for k in range(1, window + 1):
        name = f"{(day - timedelta(days=k)).isoformat()}.json"
        for d in hist_dirs:
            p = Path(d) / name
            if p.exists():
                for b, c in json.loads(p.read_text(encoding="utf-8")).items():
                    total[int(b)] = total.get(int(b), 0) + c
                n += 1
                break
    if not n or not total:
        return None, None, 0
    return ob.threshold_from_hist(total, 0.99), ob.threshold_from_hist(total, 0.999), n


# ---------------------------------------------------------------- state + files
def load_state(out):
    try:
        return json.loads((Path(out) / "_state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(out, st):
    p = Path(out) / "_state.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(st), encoding="utf-8", newline="\n")
    tmp.replace(p)


def append_rows(out, day, rows):
    p = Path(out) / f"{day.isoformat()}.csv"
    new = not p.exists() or p.stat().st_size == 0
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(ob.COLUMNS)
        for r in rows:
            w.writerow([repr(r[c]) if isinstance(r[c], float) else r[c] for c in ob.COLUMNS])


def write_hist(out, day, hist):
    d = Path(out) / "_qhist"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{day.isoformat()}.json").write_text(json.dumps(hist), encoding="utf-8", newline="\n")


def prune(out, today, keep_days):
    for p in Path(out).glob("????-??-??.csv"):
        try:
            if date.fromisoformat(p.name[:10]) < today - timedelta(days=keep_days):
                p.unlink()
        except ValueError:
            pass


def load_live_bars(out, since_ms=None):
    """Read the writer's CSVs back as bar dicts typed exactly like orderflow_bars.load_days (plus 'cvd' = cvd_day, the
    live files are not stitched). Ascending, only t >= since_ms. Fail closed: any read/parse problem -> []."""
    bars = []
    try:
        for p in sorted(Path(out).glob("????-??-??.csv")):
            if since_ms is not None and datetime.combine(date.fromisoformat(p.name[:10]), datetime.min.time(),
                                                         timezone.utc).timestamp() * 1000 + 86400000 <= since_ms:
                continue
            with open(p, "r", newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    b = {k: (int(v) if k in ob.INT_COLS else (v if k == "fp" else float(v))) for k, v in r.items()}
                    b["cvd"] = b["cvd_day"]
                    if since_ms is None or b["t"] >= since_ms:
                        bars.append(b)
    except (OSError, ValueError, KeyError, TypeError):
        return []
    return bars


# ---------------------------------------------------------------- one cycle
def run_cycle(out, fetch_fn, symbol="BTCUSDT", now_ms=None, since_ms=None, hist_dirs=None, keep_days=10, max_pages=MAX_PAGES):
    """Fetch and write every closed minute not yet written. Returns a dict {rows, pages, next_ms, thr_days, error}.
    Nothing is written (and state is not advanced) if the fetch fails."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    now_ms = int(time.time() * 1000) if now_ms is None else now_ms
    cur_min = now_ms // MIN_MS * MIN_MS
    st = load_state(out)
    nxt = st.get("next_ms")
    if nxt is None:
        nxt = since_ms // MIN_MS * MIN_MS if since_ms is not None else cur_min
    res = {"rows": 0, "pages": 0, "next_ms": nxt, "thr_days": None, "error": None}
    if nxt >= cur_min:
        st["next_ms"] = nxt
        save_state(out, st)
        return res
    try:
        trades, capped, res["error"] = fetch_trades(fetch_fn, symbol, nxt, cur_min, max_pages)
    except Exception as exc:  # noqa: BLE001 - any network/parse error: write nothing, retry next cycle
        res["error"] = repr(exc)
        return res
    if capped and trades and trades[-1][5] // MIN_MS * MIN_MS <= nxt // MIN_MS * MIN_MS and max_pages < OVERFLOW_PAGES:
        try:  # the first minute alone fills the page budget: refetch it with the overflow budget
            trades, capped, res["error"] = fetch_trades(fetch_fn, symbol, nxt, cur_min, OVERFLOW_PAGES)
        except Exception as exc:  # noqa: BLE001
            res["error"] = repr(exc)
            return res
    if capped and trades:  # backfill chunk: only whole minutes strictly before the last fetched one
        cut = trades[-1][5] // MIN_MS * MIN_MS
        trades = [t for t in trades if t[5] < cut]
        end = cut
    else:
        end = cur_min
    hist_dirs = hist_dirs if hist_dirs is not None else [out / "_qhist", OFFLINE_HIST]
    by_day = {}
    for t in trades:
        by_day.setdefault(datetime.fromtimestamp(t[5] / 1000.0, timezone.utc).date(), []).append(t)
    for day in sorted(by_day):
        if st.get("day") != day.isoformat():  # new day: flush the old histogram, restart cvd and histogram
            if st.get("day"):
                write_hist(out, date.fromisoformat(st["day"]), {int(k): v for k, v in st.get("hist", {}).items()})
            st["day"], st["cvd_day"], st["hist"] = day.isoformat(), 0.0, {}
        t99, t999, n = live_thresholds(day, hist_dirs)
        res["thr_days"] = n
        if t99 is None:  # nothing causal to use: write bars with thr_days 0 (consumer refuses them), own-day thresholds
            own = ob.day_hist(iter(by_day[day]))
            t99, t999 = ob.threshold_from_hist(own, 0.99), ob.threshold_from_hist(own, 0.999)
        rows = ob.aggregate_day(iter(by_day[day]), t99, t999, n)
        base = st["cvd_day"]
        for r in rows:
            r["cvd_day"] += base
        hist = {int(k): v for k, v in st["hist"].items()}
        for t in by_day[day]:
            b = ob.qty_bin(t[2])
            hist[b] = hist.get(b, 0) + 1
        append_rows(out, day, rows)
        st["cvd_day"] = rows[-1]["cvd_day"]
        st["hist"] = {str(k): v for k, v in hist.items()}
        write_hist(out, day, hist)
        res["rows"] += len(rows)
    st["next_ms"] = end
    save_state(out, st)
    prune(out, datetime.fromtimestamp(now_ms / 1000.0, timezone.utc).date(), keep_days)
    res["next_ms"], res["pages"] = end, 0
    return res


# ---------------------------------------------------------------- stall guard + loop
# OURS (2026-10-15): the recorder hung ~30 h with no log (fetch failures were swallowed, the process stayed alive, so
# loop-supervisor never relaunched it). If next_ms has not advanced for this many wall-clock minutes the process logs
# STALL and exits non-zero; loop-supervisor then relaunches it and it resumes from _state.json. A caught-up recorder
# advances next_ms every minute, so 15 min is far beyond normal; backoff (<= BACKOFF_MAX_S) stays well inside it.
STALL_MINUTES = 15
BACKOFF_MAX_S = 300
STALL_EXIT_CODE = 3
LOG_FILE = REPO / "runtime_data" / "orderflow_live.log"


def log_line(msg, path=None):
    """Timestamped line to stdout and to the (git-ignored) log file; logging must never kill the recorder."""
    line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}"
    try:
        print(line, flush=True)
    except (OSError, ValueError):
        pass
    try:
        p = Path(path or LOG_FILE)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
    except OSError:
        pass


def backoff_seconds(poll, errors):
    """Poll interval after `errors` consecutive failed cycles: doubles per failure, capped at BACKOFF_MAX_S."""
    if errors <= 0:
        return poll
    return min(BACKOFF_MAX_S, poll * (2 ** min(errors, 10)))


class StallGuard:
    """Progress = next_ms strictly greater than the best seen. Rewriting _state.json with the same next_ms is not progress."""

    def __init__(self, now, stall_minutes=STALL_MINUTES):
        self.best, self.since, self.limit = None, now, stall_minutes * 60

    def update(self, next_ms, now):
        """True while healthy, False once next_ms has not advanced for the limit."""
        if next_ms is not None and (self.best is None or next_ms > self.best):
            self.best, self.since = next_ms, now
        return now - self.since <= self.limit


def run_loop(out, fetch_fn, symbol, since_ms, keep_days, poll, once=False, sleep=time.sleep, clock=time.monotonic,
             log=log_line, stall_minutes=STALL_MINUTES, max_cycles=None, cycle=None):
    """The recorder loop. Returns the process exit code: 0/1 for --once, STALL_EXIT_CODE on a stall."""
    cycle = cycle or run_cycle
    if not load_state(out).get("next_ms") and since_ms is None:
        log(f"WARN no readable next_ms in {out}/_state.json: starting from the current minute (existing behaviour)")
    guard, errors, n = StallGuard(clock(), stall_minutes), 0, 0
    while True:
        n += 1
        try:
            r = cycle(out, fetch_fn, symbol, since_ms=since_ms, keep_days=keep_days)
        except Exception as exc:  # noqa: BLE001 - never die silently, never swallow
            r = {"rows": 0, "next_ms": None, "thr_days": None, "error": "cycle raised " + repr(exc)}
        errors = errors + 1 if r["error"] else 0
        log(f"{'ERROR' if r['error'] else 'ok'} rows={r['rows']} next_ms={r['next_ms']} thr_days={r['thr_days']} "
            f"error={r['error']} consecutive_errors={errors}")
        if once:
            return 1 if r["error"] else 0
        if not guard.update(r["next_ms"], clock()):
            log(f"STALL next_ms={guard.best} has not advanced for {stall_minutes} min (consecutive_errors={errors}): "
                f"exiting {STALL_EXIT_CODE} so loop-supervisor relaunches and resumes from _state.json")
            return STALL_EXIT_CODE
        if max_cycles is not None and n >= max_cycles:
            return 0
        sleep(backoff_seconds(poll, errors))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--poll-seconds", type=int, default=20)
    ap.add_argument("--since", help="ISO UTC start for a first run / backfill, e.g. 2026-10-03T13:30:00")
    ap.add_argument("--keep-days", type=int, default=10)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    since = None
    if a.since:
        since = int(datetime.fromisoformat(a.since).replace(tzinfo=timezone.utc).timestamp() * 1000)
    return run_loop(a.out, lambda s, **kw: default_fetch(s, kw.get("start_ms"), kw.get("from_id"), kw.get("limit", PAGE)),
                    a.symbol, since, a.keep_days, a.poll_seconds, once=a.once)


if __name__ == "__main__":
    sys.exit(main())
