"""
MyTradingSys/backtest/layers/fabio/orderflow_bars.py - true order-flow 1m bars from Binance USD-M aggTrades.

Offline data tool (no live imports, no execution imports). Pure stdlib (no numpy/pandas/pyarrow on this box).

One aggTrades day CSV -> compact 1m bars. Aggressor side: is_buyer_maker == true means the SELLER was the
aggressor (sell); false = buy. "Trade" for size purposes = one aggTrades row (fills of one taker order at one price
in one ms, aggregated by Binance); n_trades additionally counts raw trades (last_id - first_id + 1).

Columns per 1m row (t = minute open, epoch ms UTC):
  t,o,h,l,c, buy_vol,sell_vol,delta (=buy-sell), cvd_day (running sum of delta since the day's first bar; the loader
  stitches days), n_agg (aggTrades rows), n_trades (raw trades), max_trade (largest single row qty),
  b99_buy_vol,b99_sell_vol,b99_buy_n,b99_sell_n  (rows with qty >= thr99),
  b999_* same for thr999, thr99,thr999,thr_days (thresholds used and how many prior days built them),
  poc_price (lower edge of the 10 USD bin with the most volume; ties -> lower price), poc_delta (buy-sell in it),
  poc_vol, fp (full footprint of the minute: "binlow:buy:sell|binlow:buy:sell|..." ascending price, 10 USD bins;
  parse with parse_fp).

Big-trade thresholds: the 99th / 99.9th percentile of row quantity over the ROLLING PRIOR 30 calendar days
(days D-30..D-1, causal: today is never used). Percentiles come from a per-day log-histogram (100 bins per decade,
qty 0.001..1000+, ~1.2% resolution; threshold = lower edge of the bin holding the percentile, trade is big when
qty >= threshold) stored as JSON sidecars in <out>/_qhist/. If no prior day exists the day's own histogram is used
and thr_days = 0 (look-ahead: exclude such days from any test).
"""
import argparse
import csv
import gzip
import json
import math
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BIN_USD = 10.0
NBINS = 800
COLUMNS = ["t", "o", "h", "l", "c", "buy_vol", "sell_vol", "delta", "cvd_day", "n_agg", "n_trades", "max_trade",
           "b99_buy_vol", "b99_sell_vol", "b99_buy_n", "b99_sell_n",
           "b999_buy_vol", "b999_sell_vol", "b999_buy_n", "b999_sell_n",
           "thr99", "thr999", "thr_days", "poc_price", "poc_delta", "poc_vol", "fp"]
INT_COLS = ("t", "n_agg", "n_trades", "thr_days", "b99_buy_n", "b99_sell_n", "b999_buy_n", "b999_sell_n")


def qty_bin(q):
    if q <= 0:
        return 0
    i = int(math.floor((math.log10(q) + 3.0) * 100.0))
    return 0 if i < 0 else (NBINS - 1 if i >= NBINS else i)


def bin_lower(i):
    return 10.0 ** (i / 100.0 - 3.0)


def threshold_from_hist(hist, p):
    """Lower edge of the bin containing percentile p (0..1) of the row-count distribution."""
    total = sum(hist.values())
    if total <= 0:
        raise ValueError("empty histogram")
    need = p * total
    cum = 0
    for i in sorted(hist):
        cum += hist[i]
        if cum >= need:
            return bin_lower(i)
    return bin_lower(max(hist))


def parse_agg_csv(path):
    """Yield (agg_id, price, qty, first_id, last_id, ts_ms, is_buyer_maker); header row tolerated."""
    with open(path, "r", newline="") as f:
        for line in f:
            p = line.rstrip("\r\n").split(",")
            if len(p) < 7 or not p[0][:1].isdigit():
                continue
            ts = int(p[5])
            if ts > 10 ** 14:  # microseconds -> ms
                ts //= 1000
            yield (int(p[0]), float(p[1]), float(p[2]), int(p[3]), int(p[4]), ts, p[6].strip().lower() == "true")


def day_hist(trades):
    h = {}
    for tr in trades:
        b = qty_bin(tr[2])
        h[b] = h.get(b, 0) + 1
    return h


def aggregate_day(trades, thr99, thr999, thr_days=0, bin_usd=BIN_USD):
    """trades: iterable of parse_agg_csv tuples in id order. Returns list of dict rows (COLUMNS), by minute."""
    mins = {}
    for _id, px, q, fid, lid, ts, maker in trades:
        m = ts // 60000 * 60000
        a = mins.get(m)
        if a is None:
            a = mins[m] = {"o": px, "h": px, "l": px, "c": px, "bv": 0.0, "sv": 0.0, "na": 0, "nt": 0, "mx": 0.0,
                           "big": [0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0], "fp": {}}
        if px > a["h"]:
            a["h"] = px
        if px < a["l"]:
            a["l"] = px
        a["c"] = px
        a["na"] += 1
        a["nt"] += lid - fid + 1
        if q > a["mx"]:
            a["mx"] = q
        k = math.floor(px / bin_usd) * bin_usd
        fp = a["fp"].get(k)
        if fp is None:
            fp = a["fp"][k] = [0.0, 0.0]
        side = 1 if maker else 0  # 1 = sell aggressor
        if maker:
            a["sv"] += q
        else:
            a["bv"] += q
        fp[side] += q
        if q >= thr99:
            a["big"][side] += q
            a["big"][2 + side] += 1
        if q >= thr999:
            a["big"][4 + side] += q
            a["big"][6 + side] += 1
    rows, cvd = [], 0.0
    for m in sorted(mins):
        a = mins[m]
        delta = a["bv"] - a["sv"]
        cvd += delta
        poc = max(a["fp"].items(), key=lambda kv: (kv[1][0] + kv[1][1], -kv[0]))
        b = a["big"]
        rows.append({"t": m, "o": a["o"], "h": a["h"], "l": a["l"], "c": a["c"],
                     "buy_vol": a["bv"], "sell_vol": a["sv"], "delta": delta, "cvd_day": cvd,
                     "n_agg": a["na"], "n_trades": a["nt"], "max_trade": a["mx"],
                     "b99_buy_vol": b[0], "b99_sell_vol": b[1], "b99_buy_n": b[2], "b99_sell_n": b[3],
                     "b999_buy_vol": b[4], "b999_sell_vol": b[5], "b999_buy_n": b[6], "b999_sell_n": b[7],
                     "thr99": thr99, "thr999": thr999, "thr_days": thr_days,
                     "poc_price": poc[0], "poc_delta": poc[1][0] - poc[1][1], "poc_vol": poc[1][0] + poc[1][1],
                     "fp": "|".join(f"{k:g}:{v[0]!r}:{v[1]!r}" for k, v in sorted(a["fp"].items()))})
    return rows


def rolling_thresholds(hist_dir, day, own_hist, window=30):
    """(thr99, thr999, n_prior_days) from the prior `window` calendar days' histograms; own day if none."""
    total, n = {}, 0
    for k in range(1, window + 1):
        p = Path(hist_dir) / f"{(day - timedelta(days=k)).isoformat()}.json"
        if p.exists():
            n += 1
            for b, c in json.loads(p.read_text(encoding="utf-8")).items():
                total[int(b)] = total.get(int(b), 0) + c
    src = total if n else own_hist
    if not src:
        return None, None, 0
    return threshold_from_hist(src, 0.99), threshold_from_hist(src, 0.999), n


def write_rows(path, rows):
    with gzip.open(path, "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([repr(r[c]) if isinstance(r[c], float) else r[c] for c in COLUMNS])


def parse_fp(s):
    """'100:1.0:3.5|110:2.0:0.0' -> [(bin_low, buy, sell), ...]"""
    out = []
    for part in s.split("|"):
        k, b, sl = part.split(":")
        out.append((float(k), float(b), float(sl)))
    return out


def load_days(out_dir, start=None, end=None):
    """Load orderflow_1m/*.csv.gz -> chronological list of dict bars with stitched CVD under 'cvd'."""
    bars, carry = [], 0.0
    for p in sorted(Path(out_dir).glob("????-??-??.csv.gz")):
        d = date.fromisoformat(p.name[:10])
        if (start and d < start) or (end and d > end):
            continue
        with gzip.open(p, "rt", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                b = {k: (int(v) if k in INT_COLS else (v if k == "fp" else float(v))) for k, v in r.items()}
                b["cvd"] = carry + b["cvd_day"]
                bars.append(b)
        if bars:
            carry = bars[-1]["cvd"]
    return bars


def free_gb(path):
    return shutil.disk_usage(path).free / 1e9


def log(out_dir, msg):
    with open(Path(out_dir) / "_progress.log", "a", newline="\n", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}\n")
    print(msg, flush=True)


def process_day(day, raw_dir, out_dir, hist_only=False):
    """hist_only: write just the day's qty-histogram sidecar (warm-up for a parallel chunk), no bars."""
    out_dir = Path(out_dir)
    dst = out_dir / f"{day.isoformat()}.csv.gz"
    if hist_only:
        hp = out_dir / "_qhist" / f"{day.isoformat()}.json"
        if hp.exists():
            return "skip"
    elif dst.exists():
        return "skip"
    csv_path = Path(raw_dir) / "aggTrades" / f"BTCUSDT-aggTrades-{day.isoformat()}.csv"
    if not csv_path.exists():
        r = subprocess.run([sys.executable, str(REPO / "MyTradingSys" / "backtest" / "fetch_binance_archive.py"),
                            "--start", day.isoformat(), "--end", day.isoformat(),
                            "--datasets", "aggTrades", "--out", str(raw_dir)], capture_output=True, text=True)
        if not csv_path.exists():
            return "nodata " + (r.stdout + r.stderr).strip()[-200:]
    hist_dir = out_dir / "_qhist"
    hist_dir.mkdir(exist_ok=True)
    if hist_only:
        h = day_hist(parse_agg_csv(csv_path))
        (hist_dir / f"{day.isoformat()}.json").write_text(json.dumps(h), encoding="utf-8", newline=chr(10))
        csv_path.unlink()
        return "hist_only"
    own = {}

    def counted():  # streams the file once, building the day's qty histogram on the way
        for tr in parse_agg_csv(csv_path):
            b = qty_bin(tr[2])
            own[b] = own.get(b, 0) + 1
            yield tr

    t99, t999, n = rolling_thresholds(hist_dir, day, None)
    if n == 0:  # no prior day: need own-day histogram first (look-ahead, thr_days=0)
        own.update(day_hist(parse_agg_csv(csv_path)))
        if not own:
            return "empty"
        t99, t999 = threshold_from_hist(own, 0.99), threshold_from_hist(own, 0.999)
        rows = aggregate_day(parse_agg_csv(csv_path), t99, t999, 0)
    else:
        rows = aggregate_day(counted(), t99, t999, n)
    if not rows:
        return "empty"
    ntr = sum(r["n_agg"] for r in rows)
    (hist_dir / f"{day.isoformat()}.json").write_text(json.dumps(own), encoding="utf-8", newline="\n")
    tmp = Path(str(dst) + ".tmp")
    write_rows(tmp, rows)
    tmp.replace(dst)
    csv_path.unlink()
    return f"ok trades={ntr} bars={len(rows)} thr99={t99:.4f} thr999={t999:.4f} prior_days={n}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--raw", default=r"F:\MTS\data\binance_raw")
    ap.add_argument("--out", default=r"F:\MTS\data\orderflow_1m")
    ap.add_argument("--min-free-gb", type=float, default=30.0)
    ap.add_argument("--warm-days", type=int, default=0,
                    help="first write histogram sidecars for the N days before --start (parallel chunk warm-up)")
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    d, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    for k in range(a.warm_days, 0, -1):
        wd = d - timedelta(days=k)
        log(a.out, f"{wd} warm {process_day(wd, a.raw, a.out, hist_only=True)}")
    while d <= end:
        if free_gb(a.out) < a.min_free_gb:
            log(a.out, f"STOP free space < {a.min_free_gb} GB")
            break
        t0 = datetime.now()
        try:
            res = process_day(d, a.raw, a.out)
        except Exception as e:  # noqa: BLE001
            res = f"ERROR {e!r}"
        log(a.out, f"{d} {res} ({(datetime.now() - t0).total_seconds():.0f}s, free {free_gb(a.out):.1f} GB)")
        d += timedelta(days=1)


if __name__ == "__main__":
    main()
