"""Fetch Coinbase BTC-USD public daily candles (api.exchange.coinbase.com, no key) into a cache outside the repo.
Cache file: $MTS_FLOW_CACHE or C:/Users/e-ngineers/mts_cache/buyzone_test5 / coinbase_1d.json  ({UTC date: close}). Never committed."""
import json
import os
import time
import urllib.request

import pandas as pd

CACHE = os.environ.get("MTS_FLOW_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test5")
URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400&start=%s&end=%s"


def main(start="2022-12-01"):
    out = {}
    cur = pd.Timestamp(start)
    stop = pd.Timestamp.utcnow().tz_localize(None).normalize() + pd.Timedelta(days=1)
    while cur < stop:
        nxt = min(cur + pd.Timedelta(days=299), stop)
        u = URL % (cur.strftime("%Y-%m-%dT00:00:00Z"), nxt.strftime("%Y-%m-%dT00:00:00Z"))
        req = urllib.request.Request(u, headers={"User-Agent": "mts-research"})
        for attempt in range(4):
            try:
                rows = json.loads(urllib.request.urlopen(req, timeout=60).read())
                break
            except Exception:
                time.sleep(3)
                rows = []
        for t, lo, hi, op, cl, vol in rows:
            out[pd.Timestamp(t, unit="s").strftime("%Y-%m-%d")] = float(cl)
        cur = nxt
        time.sleep(0.4)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(dict(sorted(out.items())), open(os.path.join(CACHE, "coinbase_1d.json"), "w"))
    print(len(out), min(out), max(out))


if __name__ == "__main__":
    main()
