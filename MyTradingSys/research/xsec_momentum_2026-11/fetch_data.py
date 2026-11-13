"""fetch_data.py - Bybit v5 public data for the xsec momentum study (daily klines + funding history). Raw cache only, no outcome computed.
  python fetch_data.py [--cache DIR]
Candidates = linear USDT LinearPerpetual symbols with launchTime <= 2021-12-31 (history since 2021). Delisted perps are not served by
instruments-info, so survivorship of the CANDIDATE list is a stated limitation (PRE_REG)."""
import argparse
import json
import os
import sys
import time
import urllib.request

BASE = "https://api.bybit.com/v5/market/"
LAUNCH_CUTOFF_MS = 1640908800000  # 2021-12-31 00:00 UTC
START_MS = 1577836800000          # 2020-01-01
DAY_MS = 86400000


def get(path, retries=5):
    for k in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + path, headers={"User-Agent": "mts-research"}), timeout=30) as r:
                d = json.load(r)
            if d.get("retCode") == 0:
                return d["result"]
            time.sleep(1 + k)
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError("fetch failed " + path)


def instruments():
    out, cur = [], ""
    while True:
        r = get("instruments-info?category=linear&limit=1000" + (("&cursor=" + cur) if cur else ""))
        out += r["list"]
        cur = r.get("nextPageCursor") or ""
        if not cur:
            return out


def daily(sym):
    rows, end = {}, int(time.time() * 1000)
    while end > START_MS:
        r = get("kline?category=linear&symbol=%s&interval=D&limit=1000&end=%d" % (sym, end))["list"]
        if not r:
            break
        for x in r:
            rows[int(x[0])] = [int(x[0])] + [float(v) for v in x[1:7]]  # t,o,h,l,c,vol,turnover
        oldest = min(int(x[0]) for x in r)
        if oldest >= end:
            break
        end = oldest - 1
    return [rows[k] for k in sorted(rows) if rows[k][0] >= START_MS]


def funding(sym, first_ms):
    rows, end = {}, int(time.time() * 1000)
    while end > max(first_ms, START_MS):
        r = get("funding/history?category=linear&symbol=%s&limit=200&endTime=%d" % (sym, end))["list"]
        if not r:
            break
        for x in r:
            rows[int(x["fundingRateTimestamp"])] = float(x["fundingRate"])
        oldest = min(int(x["fundingRateTimestamp"]) for x in r)
        if oldest >= end:
            break
        end = oldest - 1
    return sorted(rows.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="runtime_data/edge-xsec-momentum-1113")
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    ins = [i for i in instruments() if i["quoteCoin"] == "USDT" and i["contractType"] == "LinearPerpetual"
           and int(i["launchTime"]) <= LAUNCH_CUTOFF_MS]
    json.dump(ins, open(os.path.join(a.cache, "instruments.json"), "w"))
    print("candidates", len(ins), flush=True)
    for i in ins:
        s = i["symbol"]
        f = os.path.join(a.cache, s + ".json")
        if os.path.exists(f):
            continue
        d = daily(s)
        fu = funding(s, d[0][0] if d else START_MS)
        json.dump({"daily": d, "funding": fu}, open(f, "w"))
        print(s, len(d), len(fu), flush=True)


if __name__ == "__main__":
    sys.exit(main())
