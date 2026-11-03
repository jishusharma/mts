"""Fetch CME BTC futures (front-month continuous, Yahoo ticker BTC=F) daily bars with volume (card krown-data-cme-btc-volume).

Source: Yahoo Finance public chart endpoint, no login, no key. CME's own volume pages block scripted access
(HTTP message "IP address is blocked due to suspected web scraping"), so they were not used and not bypassed.
Output (never in git): <out>/CME_BTC_F_1d.csv, same columns as COINBASE_BTC-USD_1d.csv (open_time_ms UTC midnight);
volume = contracts (5 BTC each) of the Yahoo continuous front-month series, NOT total all-expiry CME volume.
Appends one row to DATA_MANIFEST.csv and prints coverage. Only timestamps/volume counts are inspected.
DECISION (OURS): Yahoo BTC=F front-month as the free proxy; it is a proxy, label it so.
"""
import argparse, csv, hashlib, json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://query1.finance.yahoo.com/v8/finance/chart/BTC=F?period1=1500000000&period2=%d&interval=1d"
COLS = ["open_time_ms", "open", "high", "low", "close", "volume", "close_time_ms", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", default=str(Path(__file__).resolve().parents[1] / "DATA_MANIFEST.csv"))
    a = ap.parse_args()
    url = URL % int(datetime.now(timezone.utc).timestamp())
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    res = json.load(urllib.request.urlopen(req, timeout=60))["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    gmt = res["meta"].get("gmtoffset", 0)
    rows = {}
    for i, t in enumerate(res["timestamp"]):
        if q["close"][i] is None:
            continue
        day = datetime.fromtimestamp(t + gmt, timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        ms = int(day.timestamp() * 1000)
        rows[ms] = [ms, q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i] or 0,
                    ms + 86399999, "", "", "", ""]
    out = Path(a.out) / "CME_BTC_F_1d.csv"
    with open(out, "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        for k in sorted(rows):
            w.writerow(rows[k])
    ks = sorted(rows)
    days = [(k - ks[0]) // 86400000 for k in ks]
    wk = [d for d in days if datetime.fromtimestamp(ks[0] / 1000 + d * 86400, timezone.utc).weekday() < 5]
    missing_weekdays = (max(days) + 1) - len(days) - sum(1 for d in range(max(days) + 1)
                       if datetime.fromtimestamp(ks[0] / 1000 + d * 86400, timezone.utc).weekday() >= 5)
    zero = sum(1 for k in ks if not rows[k][5])
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    with open(a.manifest, "a", newline="\n") as f:
        csv.writer(f, lineterminator="\n").writerow(["CME_BTC_F", "1d", "all", url.split("&period2")[0] + "&period2=NOW&interval=1d", "", sha, "API_YAHOO_FRONT_MONTH"])
    iso = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")
    print("rows", len(ks), "first", iso(ks[0]), "last", iso(ks[-1]), "missing_weekdays", missing_weekdays,
          "zero_volume_days", zero, "sha256", sha)


if __name__ == "__main__":
    sys.exit(main())
