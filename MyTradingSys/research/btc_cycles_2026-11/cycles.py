"""BTC four-year cycle table: halving -> peak -> bottom, 2010..now (operator 2026-11-06, d-phase-first-method-1106).

Data (public market data):
  - before 2017-08-17: blockchain.info daily market price (one value per day, so peak/low are daily-average values);
  - from 2017-08-17: Binance BTCUSDT 1d klines (true daily high/low), topped up from the public klines API.
Halving dates are block-height events (SOURCED: bitcoin protocol, blocks 210k/420k/630k/840k).
Usage: python cycles.py --bc <blockchain json> --binance <BTCUSDT_1d.csv> [--fetch-binance]
Writes cycles.csv, cycles.md and btc_daily.csv next to this file.
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
HALVINGS = [dt.date(2012, 11, 28), dt.date(2016, 7, 9), dt.date(2020, 5, 11), dt.date(2024, 4, 20)]
BINANCE_START = dt.date(2017, 8, 17)
NEXT_HALVING_EST = dt.date(2028, 4, 15)  # OURS: block 1,050,000 at ~10 min/block from block 840,000 (2024-04-20); an estimate


def d(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()


def load(bc_path, bn_path, fetch):
    rows = {}  # date -> (high, low, close)
    for v in json.loads(pathlib.Path(bc_path).read_text(encoding="utf-8"))["values"]:
        day = d(v["x"])
        if day < BINANCE_START and v["y"] > 0:
            rows[day] = (v["y"], v["y"], v["y"])
    with open(bn_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[d(int(r["open_time_ms"]) // 1000)] = (float(r["high"]), float(r["low"]), float(r["close"]))
    if fetch:
        last = max(rows)
        start = int(dt.datetime.combine(last + dt.timedelta(days=1), dt.time(), dt.timezone.utc).timestamp() * 1000)
        url = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime={start}&limit=1000"
        for k in json.loads(urllib.request.urlopen(url, timeout=60).read()):
            rows[d(k[0] // 1000)] = (float(k[2]), float(k[3]), float(k[4]))
    return dict(sorted(rows.items()))


def extreme(rows, lo, hi, kind):
    span = [(day, v) for day, v in rows.items() if lo <= day <= hi]
    if kind == "max":
        return max(span, key=lambda x: x[1][0])
    return min(span, key=lambda x: x[1][1])


def build(rows):
    today = max(rows)
    out = []
    # cycle 0: before the first halving (2011 bubble)
    p0 = extreme(rows, dt.date(2011, 1, 1), dt.date(2011, 12, 31), "max")
    b0 = extreme(rows, p0[0], dt.date(2012, 6, 30), "min")
    out.append(dict(cycle=0, halving="", peak_date=p0[0], peak=p0[1][0], bottom_date=b0[0], bottom=b0[1][1]))
    for i, h in enumerate(HALVINGS, start=1):
        p = extreme(rows, h, min(h + dt.timedelta(days=730), today), "max")
        b = extreme(rows, p[0], min(p[0] + dt.timedelta(days=500), today), "min")
        out.append(dict(cycle=i, halving=h, peak_date=p[0], peak=p[1][0], bottom_date=b[0], bottom=b[1][1]))
    for i, c in enumerate(out):
        prev = out[i - 1] if i else None
        c["halving_to_peak_d"] = (c["peak_date"] - c["halving"]).days if c["halving"] else ""
        c["peak_to_bottom_d"] = (c["bottom_date"] - c["peak_date"]).days
        c["drawdown_pct"] = round((c["bottom"] / c["peak"] - 1) * 100, 1)
        c["prev_bottom_to_peak_d"] = (c["peak_date"] - prev["bottom_date"]).days if prev else ""
        c["prev_bottom_to_peak_x"] = round(c["peak"] / prev["bottom"], 1) if prev else ""
        c["bottom_to_bottom_d"] = (c["bottom_date"] - prev["bottom_date"]).days if prev else ""
        c["bottom_is_final"] = c["bottom_date"] < today - dt.timedelta(days=60)
        nxt = HALVINGS[i] if i < len(HALVINGS) else NEXT_HALVING_EST
        c["bottom_to_next_halving_d"] = (nxt - c["bottom_date"]).days
    return out, today


def write(out, rows, today):
    with open(HERE / "btc_daily.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["date", "high", "low", "close", "source"])
        for day, (h, l, c) in rows.items():
            w.writerow([day, round(h, 2), round(l, 2), round(c, 2), "blockchain.info" if day < BINANCE_START else "binance"])
    keys = list(out[0].keys())
    with open(HERE / "cycles.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    last = rows[today][2]
    cur = out[-1]
    done = [c for c in out[1:-1]]
    p2b = [c["peak_to_bottom_d"] for c in done]
    dd = [c["drawdown_pct"] for c in done]
    lines = [f"# BTC cycles (data to {today}, close {last:,.0f})", "",
             "| cycle | halving | peak date | peak | halving to peak (d) | bottom date | bottom | peak to bottom (d) | drawdown % | prev bottom to peak (d, x) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for c in out:
        lines.append(f"| {c['cycle']} | {c['halving']} | {c['peak_date']} | {c['peak']:,.0f} | {c['halving_to_peak_d']} | {c['bottom_date']} | {c['bottom']:,.0f} | {c['peak_to_bottom_d']} | {c['drawdown_pct']} | {c['prev_bottom_to_peak_d']} d, {c['prev_bottom_to_peak_x']}x |")
    since = (today - cur["peak_date"]).days
    lines += ["", "## Cycle 4 now",
              f"- peak {cur['peak_date']} at {cur['peak']:,.0f}; {since} days since the peak; close {last:,.0f} = {round((last / cur['peak'] - 1) * 100, 1)} % from the peak; lowest since the peak {cur['bottom']:,.0f} on {cur['bottom_date']} ({cur['drawdown_pct']} %).",
              f"- cycles 1-3 peak to bottom: {p2b} days, so a cycle-4 bottom by the same clock falls {cur['peak_date'] + dt.timedelta(days=min(p2b))} .. {cur['peak_date'] + dt.timedelta(days=max(p2b))}.",
              f"- bottom to the next halving, cycles 0-3: {[c['bottom_to_next_halving_d'] for c in out[:-1]]} days; from the {cur['bottom_date']} low to the estimated {NEXT_HALVING_EST} halving: {cur['bottom_to_next_halving_d']} days.",
              f"- cycles 1-3 drawdowns: {dd} %; the same depths from the cycle-4 peak would be {', '.join(f'{cur['peak'] * (1 + x / 100):,.0f}' for x in dd)}.",
              "- Descriptive only: 3 completed halving cycles; the clock and the depth are the pattern the operator trades, not a backtest (d-phase-first-method-1106)."]
    (HERE / "cycles.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bc", required=True)
    ap.add_argument("--binance", required=True)
    ap.add_argument("--fetch-binance", action="store_true")
    a = ap.parse_args()
    rows = load(a.bc, a.binance, a.fetch_binance)
    out, today = build(rows)
    write(out, rows, today)
