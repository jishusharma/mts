"""Deribit BTC options full-chain snapshot (public market data only, read-only, no keys, no orders).

One snapshot = one JSON line appended (as its own gzip member) to  options/data/chain/YYYY-MM-DD.jsonl.gz  (UTC date):
  {"v":1,"ts_ms":..,"iso":..,"index":<btc_usd index>,"dvol":<latest DVOL close>,"dvol_ts":..,
   "params":{..},"n_rows":..,"n_ticker":..,"n_ticker_fail":..,"elapsed_s":..,"rows":[{...}, ...]}

Cheapest way to get greeks/IV for the whole chain (decision, 2026-10-09):
  * ONE call public/get_book_summary_by_currency(BTC, option) returns every live option (~960 rows) with bid/ask/mark
    price, mark_iv, open interest, volume, underlying_price - but NO greeks and NO bid_iv/ask_iv.
  * public/ticker per instrument adds delta/gamma/vega/theta/rho + bid_iv/ask_iv + best bid/ask size, 1 call each.
    So tickers are fetched only for the nearest-ATM subset: per expiry <= --max-dte days, the --atm-strikes strikes
    either side of the ATM strike (ATM = strike nearest the expiry's underlying/forward price), both calls and puts.
    Default 8/90 is ~250-300 tickers (~70 s at 4 req/s). Rows outside the subset keep mark_iv only; their greeks can
    be recomputed offline from mark_iv + underlying_price.

Run:   python MyTradingSys/options/collector/deribit_opt_snapshot.py            (one snapshot)
       python MyTradingSys/options/collector/deribit_opt_snapshot.py --every 900   (loop; Ctrl+C to stop)
No Windows task is created by this module; scheduling is the operator's call (see collector/README.md).
"""
import argparse
import json
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_opt_common as C  # noqa: E402

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INST_RE = re.compile(r"^BTC-(\d{1,2})([A-Z]{3})(\d{2})-(\d+)-([CP])$")
MONTHS = {m: i + 1 for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
EXPIRY_HOUR_MS = 8 * C.HOUR_MS  # Deribit options expire 08:00 UTC

# fields kept from get_book_summary_by_currency rows (dropped: creation_timestamp == snapshot time,
# estimated_delivery_price == index, base_currency, quote_currency, mid_price)
SUMMARY_KEEP = ("instrument_name", "bid_price", "ask_price", "mark_price", "mark_iv", "open_interest", "volume",
                "volume_usd", "last", "high", "low", "price_change", "underlying_price", "underlying_index",
                "interest_rate")
GREEK_KEYS = ("delta", "gamma", "vega", "theta", "rho")


def parse_instrument(name):
    """'BTC-27NOV26-88000-C' -> (expiry_ms, strike, 'C') or None."""
    m = INST_RE.match(name)
    if not m or m.group(2) not in MONTHS:
        return None
    import calendar
    day, mon, yy = int(m.group(1)), MONTHS[m.group(2)], 2000 + int(m.group(3))
    exp = calendar.timegm((yy, mon, day, 0, 0, 0)) * 1000 + EXPIRY_HOUR_MS
    return exp, int(m.group(4)), m.group(5)


def select_ticker_subset(summary_rows, now_ms, atm_n=8, max_dte=90):
    """Instrument names to fetch tickers for: per expiry with 0 <= dte <= max_dte, the strikes within +-atm_n
    strike steps of the ATM strike (nearest strike to the expiry's median underlying_price), calls and puts."""
    by_exp = {}
    for r in summary_rows:
        p = parse_instrument(r.get("instrument_name", ""))
        if p is None:
            continue
        exp, strike, cp = p
        dte = (exp - now_ms) / C.DAY_MS
        if dte < 0 or dte > max_dte:
            continue
        by_exp.setdefault(exp, []).append((strike, cp, r))
    names = []
    for exp, items in by_exp.items():
        unders = [r.get("underlying_price") for _, _, r in items if r.get("underlying_price")]
        if not unders:
            continue
        ref = statistics.median(unders)
        strikes = sorted({s for s, _, _ in items})
        atm_i = min(range(len(strikes)), key=lambda i: abs(strikes[i] - ref))
        keep = set(strikes[max(0, atm_i - atm_n): atm_i + atm_n + 1])
        names.extend(r["instrument_name"] for s, _, r in items if s in keep)
    return sorted(set(names))


def build_row(summary, ticker=None):
    row = {k: summary.get(k) for k in SUMMARY_KEEP if k in summary}
    if ticker:
        g = ticker.get("greeks") or {}
        for k in GREEK_KEYS:
            row[k] = g.get(k)
        row["bid_iv"] = ticker.get("bid_iv")
        row["ask_iv"] = ticker.get("ask_iv")
        row["best_bid_amount"] = ticker.get("best_bid_amount")
        row["best_ask_amount"] = ticker.get("best_ask_amount")
        # ticker-time values, so greeks can be re-derived consistently (ticker is seconds-minutes after the summary)
        row["t_ts"] = ticker.get("timestamp")
        row["t_mark_price"] = ticker.get("mark_price")
        row["t_mark_iv"] = ticker.get("mark_iv")
        row["t_underlying_price"] = ticker.get("underlying_price")
        row["t_index_price"] = ticker.get("index_price")
    return row


def latest_dvol(client, now_ms):
    """(ts, close) of the latest DVOL candle, or (None, None)."""
    for res, span in (("60", 3 * C.HOUR_MS), ("3600", 6 * C.HOUR_MS)):
        res_ = client.call("public/get_volatility_index_data", {"currency": "BTC", "start_timestamp": now_ms - span,
                                                                 "end_timestamp": now_ms, "resolution": res})
        data = (res_ or {}).get("data") or []
        if data:
            return data[-1][0], data[-1][4]
    return None, None


def take_snapshot(client, atm_n=8, max_dte=90, workers=3, clock_ms=C.now_ms, log=lambda m: None):
    """Fetch one snapshot dict. Fails closed (raises) if the index or the book summary cannot be fetched;
    ticker/DVOL failures are recorded in the record, not fatal."""
    t_start = time.time()
    ts_ms = clock_ms()
    idx = client.call("public/get_index_price", {"index_name": "btc_usd"})
    summary = client.call("public/get_book_summary_by_currency", {"currency": "BTC", "kind": "option"})
    if not isinstance(summary, list) or not summary:
        raise C.DeribitError("public/get_book_summary_by_currency", "empty", "no option rows returned")
    dvol_ts, dvol = None, None
    dvol_err = None
    try:
        dvol_ts, dvol = latest_dvol(client, ts_ms)
    except C.DeribitError as e:
        dvol_err = str(e)
    names = select_ticker_subset(summary, ts_ms, atm_n, max_dte)
    tickers = {}
    n_fail = 0

    def safe(name):
        try:
            return name, client.call("public/ticker", {"instrument_name": name})
        except C.DeribitError as e:
            return name, e

    if workers <= 1:
        results = [safe(n) for n in names]
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(safe, names))
    for n, res in results:
        if isinstance(res, Exception):
            n_fail += 1
            log("ticker failed %s: %s" % (n, res))
        else:
            tickers[n] = res
    rows = [build_row(s, tickers.get(s.get("instrument_name"))) for s in summary]
    snap = {
        "v": 1, "ts_ms": ts_ms, "iso": C.iso(ts_ms),
        "index": idx.get("index_price") if isinstance(idx, dict) else None,
        "dvol": dvol, "dvol_ts": dvol_ts,
        "params": {"atm_strikes": atm_n, "max_dte": max_dte},
        "n_rows": len(rows), "n_ticker": len(tickers), "n_ticker_fail": n_fail,
        "elapsed_s": round(time.time() - t_start, 1),
        "rows": rows,
    }
    if dvol_err:
        snap["dvol_err"] = dvol_err
    return snap


def snapshot_path(data_dir, ts_ms):
    return Path(data_dir) / "chain" / (C.utc_date(ts_ms) + ".jsonl.gz")


def write_snapshot(data_dir, snap):
    path = snapshot_path(data_dir, snap["ts_ms"])
    C.append_gz_line(path, json.dumps(snap, separators=(",", ":")))
    return path


def loop(every, run_once, max_cycles=None, sleep=time.sleep, clock=time.monotonic, max_consec_fail=5, log=print):
    """Run run_once every `every` seconds on a fixed grid (no drift; missed slots are skipped, not queued).
    Returns 0 after max_cycles, 2 after max_consec_fail consecutive failures."""
    start = clock()
    cycles = 0
    fails = 0
    while True:
        try:
            run_once()
            fails = 0
        except Exception as e:  # noqa: BLE001 - a collector loop must survive one bad cycle
            fails += 1
            log("cycle failed (%d consecutive): %s: %s" % (fails, type(e).__name__, e))
            if fails >= max_consec_fail:
                return 2
        cycles += 1
        if max_cycles and cycles >= max_cycles:
            return 0
        elapsed = clock() - start
        next_slot = (int(elapsed // every) + 1) * every
        sleep(max(0.0, next_slot - elapsed))


def main(argv=None, client=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    ap.add_argument("--atm-strikes", type=int, default=8, help="tickers for ATM +- N strikes per expiry (default 8)")
    ap.add_argument("--max-dte", type=float, default=90, help="ticker only expiries <= this many days out (default 90)")
    ap.add_argument("--every", type=float, default=0, help="loop interval seconds (0 = one snapshot and exit)")
    ap.add_argument("--max-cycles", type=int, default=0, help="stop the loop after N snapshots (0 = run until Ctrl+C)")
    ap.add_argument("--rate", type=float, default=4.0, help="max requests/second (hard cap 5)")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    client = client or C.DeribitPublic(C.LIVE_BASE, rate=a.rate, log=lambda m: print("  [http] " + m, flush=True))

    def run_once():
        snap = take_snapshot(client, a.atm_strikes, a.max_dte, a.workers, log=lambda m: print("  " + m, flush=True))
        path = write_snapshot(a.data_dir, snap)
        print("%s snapshot rows=%d tickers=%d fail=%d index=%s dvol=%s %.1fs -> %s" % (
            snap["iso"], snap["n_rows"], snap["n_ticker"], snap["n_ticker_fail"], snap["index"], snap["dvol"],
            snap["elapsed_s"], path), flush=True)

    if a.every and a.every > 0:
        return loop(a.every, run_once, a.max_cycles or None)
    try:
        run_once()
    except C.DeribitError as e:
        print("SNAPSHOT FAILED (nothing written): %s" % e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
