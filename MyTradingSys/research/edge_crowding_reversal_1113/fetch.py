"""Fetch Bybit v5 public data (kline 4h, funding, OI 4h, account ratio 4h) for 10 USDT perps. Cache: runtime_data/edge-crowding-reversal-1113/."""
import json, os, sys, time, urllib.request, urllib.parse

COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX"]
BASE = "https://api.bybit.com/v5/market/"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "runtime_data", "edge-crowding-reversal-1113")
START = 1577836800000  # 2020-01-01


def get(ep, **p):
    url = BASE + ep + "?" + urllib.parse.urlencode(p)
    for a in range(6):
        try:
            d = json.load(urllib.request.urlopen(url, timeout=25))
            if d.get("retCode") == 0:
                return d["result"]["list"]
        except Exception:
            pass
        time.sleep(1 + a)
    return None


def pull(ep, tsidx, limit, **p):
    rows, end = [], None
    for _ in range(400):
        q = dict(p, limit=limit)
        if end:
            q["endTime"] = end
        l = get(ep, **q)
        if not l:
            break
        rows += l
        mn = min(int(x[tsidx]) if isinstance(x, list) else int(x[tsidx]) for x in l)
        if mn <= START:
            break
        end = mn - 1
        time.sleep(0.12)
    seen, out = set(), []
    for x in rows:
        t = int(x[tsidx])
        if t not in seen and t >= START:
            seen.add(t); out.append(x)
    out.sort(key=lambda x: int(x[tsidx]))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for c in COINS:
        s = c + "USDT"
        f = os.path.join(OUT, s + ".json")
        if os.path.exists(f):
            continue
        d = {
            "kline": pull("kline", 0, 1000, category="linear", symbol=s, interval="240"),
            "funding": pull("funding/history", "fundingRateTimestamp", 200, category="linear", symbol=s),
            "oi": pull("open-interest", "timestamp", 200, category="linear", symbol=s, intervalTime="4h"),
            "ratio": pull("account-ratio", "timestamp", 500, category="linear", symbol=s, period="4h"),
        }
        json.dump(d, open(f, "w"))
        print(s, {k: (len(v), v[0][0] if k == "kline" and v else None) for k, v in d.items()}, flush=True)


if __name__ == "__main__":
    main()
