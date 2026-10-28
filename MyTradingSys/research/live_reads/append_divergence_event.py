"""Small appender for divergence_events.csv (descriptive-only forward log, feeds
tom-corr-divergence-backtest; never a parameter source — see the CSV header). Public data only
(Binance data-api.binance.vision, Yahoo chart API); no orders, no secrets.

Usage:
    python append_divergence_event.py new UTC_ISO BTC_OPEN ES_OPEN NQ_OPEN BTC_PCT ES_PCT NQ_PCT \
        VIX R5M_1H_ES R5M_1H_NQ "footprint note"
        # appends one event row with blank out_30m/out_60m/out_120m

    python append_divergence_event.py fill UTC_ISO {30|60|120} BTC_OPEN ES_OPEN NQ_OPEN
        # pulls public BTC/ES/NQ/VIX 5m closes at UTC_ISO + the given offset (since_open() convention:
        # close of the public 5m bar covering [t-5m, t)) and writes that outcome string into the
        # matching row's out_<offset>m column.

Never edits btc/es/nq_since_open on an existing event row (those are registered once, at read time);
only appends new rows or fills a still-blank out_*m cell.
"""
import csv
import datetime as dt
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "divergence_events.csv")
UA = {"User-Agent": "Mozilla/5.0"}
BAR = 300
FIELDS = ["utc", "btc_since_open", "es_since_open", "nq_since_open", "vix", "r5m_1h_es", "r5m_1h_nq",
          "footprint_delta_note", "out_30m", "out_60m", "out_120m"]


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))


def parse_ts(iso):
    return int(dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp())


def price_at(series, t):
    ks = [x for x in series if x <= t - BAR]
    return series[max(ks)] if ks else None


def pull(t):
    """Public 5m closes at/just before t for BTC (Binance), ES/NQ/VIX (Yahoo)."""
    start_ms, end_ms = (t - 1200) * 1000, (t + 300) * 1000
    k = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m"
            f"&startTime={start_ms}&endTime={end_ms}&limit=20")
    btc5 = {x[0] // 1000: float(x[4]) for x in k}
    out = {"btc": price_at(btc5, t)}
    for sym, key in (("ES=F", "es"), ("NQ=F", "nq"), ("^VIX", "vix")):
        r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
                f"?period1={t - 1200}&period2={t + 300}&interval=5m&includePrePost=true")["chart"]["result"][0]
        series = {ts: v for ts, v in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if v is not None}
        out[key] = price_at(series, t)
    return out


def read_rows():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def cmd_new(args):
    utc, btc_open, es_open, nq_open, btc_pct, es_pct, nq_pct, vix, r_es, r_nq, note = args
    row = {"utc": utc, "btc_since_open": btc_pct, "es_since_open": es_pct, "nq_since_open": nq_pct,
           "vix": vix, "r5m_1h_es": r_es, "r5m_1h_nq": r_nq, "footprint_delta_note": note,
           "out_30m": "", "out_60m": "", "out_120m": ""}
    with open(CSV_PATH, "a", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writerow(row)
    print(f"appended event row for {utc}")


def cmd_fill(args):
    utc, offset, btc_open, es_open, nq_open = args
    offset = int(offset)
    assert offset in (30, 60, 120), "offset must be 30, 60 or 120"
    t0 = parse_ts(utc)
    t = t0 + offset * 60
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    if now < t:
        print(f"refused: {offset}m mark ({dt.datetime.fromtimestamp(t, dt.timezone.utc)}) hasn't happened yet")
        return
    p = pull(t)
    btc_open, es_open, nq_open = float(btc_open), float(es_open), float(nq_open)
    btc_pct = (p["btc"] / btc_open - 1) * 100
    es_pct = (p["es"] / es_open - 1) * 100
    nq_pct = (p["nq"] / nq_open - 1) * 100
    gap = es_pct - btc_pct
    outstr = f"BTC{btc_pct:+.2f}% ES{es_pct:+.2f}% NQ{nq_pct:+.2f}% VIX={p['vix']:.2f} gap(ES-BTC)={gap:+.2f}pp"
    rows = read_rows()
    for r in rows:
        if r["utc"] == utc:
            r[f"out_{offset}m"] = outstr
            break
    else:
        print(f"no event row found for {utc}; run 'new' first")
        return
    with open(CSV_PATH) as f:
        header_lines = [ln for ln in f if ln.startswith("#")]
    with open(CSV_PATH, "w", newline="\n") as f:
        f.writelines(header_lines)
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"filled out_{offset}m for {utc}: {outstr}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("new", "fill"):
        print(__doc__)
        sys.exit(1)
    (cmd_new if sys.argv[1] == "new" else cmd_fill)(sys.argv[2:])
