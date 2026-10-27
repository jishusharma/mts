"""Eagle_Eyes live watcher (OURS levels from the 2026-10-26 read). Polls every 60 s, records every row to
watch_rows.csv, prints a line only when a trigger flips (plus a heartbeat every 10 min). Public data only: Binance spot
(data-api.binance.vision) and Yahoo chart API. Observation, never orders."""
import csv, json, math, os, sys, time, urllib.request, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "watch_rows.csv")
UA = {"User-Agent": "Mozilla/5.0"}
# OURS: since-open baselines = price at 13:30Z 2026-10-26 (13:25 bar close for ES/NQ, 13:30 1m open for BTC)
OPEN = {"BTC": 79952.00, "ES": 7683.50, "NQ": 29230.50}
BTC_TOP, BTC_BOT = 80250.0, 79451.0      # 14:21 spot high / 13:36 spot low
ES_HI, ES_OPEN = 7698.5, 7683.5          # overnight high / 13:30 level
GAP_CLOSED, GAP_WIDE = 0.15, 0.80        # ES since-open minus BTC since-open, percentage points
R_UP, R_DOWN = 0.40, 0.0                 # 1h BTC-ES 5m-return correlation


LAST, STALE = {}, {"es": False}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))


def yahoo(sym, itv):
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval={itv}&includePrePost=true")["chart"]["result"][0]
    q = r["indicators"]["quote"]
    c = q[0].get("close") if q else None
    if not c:  # Yahoo sends no bars when the ES/NQ feed stalls (10-27 03:53Z): empty, not an error
        return {}
    return {t: v for t, v in zip(r["timestamp"], c) if v is not None}


def corr(x, y):
    n = len(x)
    if n < 6:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


def poll():
    btc = float(get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT")["price"])
    es1, nq1 = yahoo("ES=F", "1m"), yahoo("NQ=F", "1m")
    STALE["es"] = not es1 or not nq1
    if STALE["es"]:  # keep BTC triggers alive: reuse the last ES/NQ, flagged ES_STALE
        es, nq = LAST.get("es"), LAST.get("nq")
        if es is None:
            raise RuntimeError("no ES yet")
    else:
        es, nq = es1[max(es1)], nq1[max(nq1)]
        LAST["es"], LAST["nq"] = es, nq
    k = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=40")
    b5 = {x[0] // 1000: float(x[4]) for x in k}
    e5 = yahoo("ES=F", "5m")
    ks = sorted(set(b5) & set(e5))[-13:]
    rb = [b5[ks[i]] / b5[ks[i - 1]] - 1 for i in range(1, len(ks))]
    re_ = [e5[ks[i]] / e5[ks[i - 1]] - 1 for i in range(1, len(ks))]
    pct = lambda v, o: (v / o - 1) * 100
    row = {"utc": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "btc": round(btc, 2), "es": es, "nq": nq,
           "btc_pct": round(pct(btc, OPEN["BTC"]), 3), "es_pct": round(pct(es, OPEN["ES"]), 3), "nq_pct": round(pct(nq, OPEN["NQ"]), 3),
           "r5m_1h_es": round(corr(rb, re_), 2)}
    row["gap_es_minus_btc"] = round(row["es_pct"] - row["btc_pct"], 3)
    return row


def states(r):
    return {
        "BTC>=80250": r["btc"] >= BTC_TOP,
        "BTC<=79451": r["btc"] <= BTC_BOT,
        "BTC<=79836": r["btc"] <= 79836.0,      # OURS: 2H forming low 20:40Z
        "BTC<=79923": r["btc"] <= 79923.0,      # OURS: 16:40Z 5m low, lost 20:15Z
        "ES>7698.5": r["es"] > ES_HI,
        "ES<7683.5": r["es"] < ES_OPEN,
        "GAP<=0.15(converged)": r["gap_es_minus_btc"] <= GAP_CLOSED,
        "GAP>=0.80(widening)": r["gap_es_minus_btc"] >= GAP_WIDE,
        "r1h>=0.40(re-coupled)": r["r5m_1h_es"] >= R_UP,
        "r1h<=0(decoupled)": r["r5m_1h_es"] <= R_DOWN,
        "ES_STALE(gap/r1h not valid)": STALE["es"],
    }


def main():
    new = not os.path.exists(CSV)
    prev, last_hb, n = None, 0, 0
    if not new:  # seed the ES/NQ fallback from the last recorded row
        with open(CSV, newline="") as f:
            last = list(csv.DictReader(f))[-1]
        LAST["es"], LAST["nq"] = float(last["es"]), float(last["nq"])
    while True:
        try:
            r = poll()
        except Exception as e:  # transient: say so once per failure, keep going
            print(f"poll failed: {type(e).__name__}", flush=True)
            time.sleep(60)
            continue
        st = states(r)
        with open(CSV, "a", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=list(r) + ["flags"], lineterminator="\n")
            if new:
                w.writeheader(); new = False
            w.writerow({**r, "flags": "|".join(k for k, v in st.items() if v)})
        n += 1
        flips = [(k, v) for k, v in st.items() if prev is None or prev[k] != v]
        if prev is not None:
            for k, v in flips:
                print(f"TRIGGER {r['utc'][11:16]}Z {k} {'ON' if v else 'off'} | BTC {r['btc']:.0f} ({r['btc_pct']:+.2f}%) ES {r['es']:.2f} ({r['es_pct']:+.2f}%) NQ {r['nq']:.0f} ({r['nq_pct']:+.2f}%) gap {r['gap_es_minus_btc']:+.2f} r1h {r['r5m_1h_es']:+.2f}", flush=True)
        if time.time() - last_hb > 600:
            on = [k for k, v in st.items() if v]
            print(f"HB {r['utc'][11:16]}Z BTC {r['btc']:.0f} ({r['btc_pct']:+.2f}%) ES {r['es_pct']:+.2f}% NQ {r['nq_pct']:+.2f}% gap {r['gap_es_minus_btc']:+.2f} r1h {r['r5m_1h_es']:+.2f} on={on} rows={n}", flush=True)
            last_hb = time.time()
        prev = st
        time.sleep(60)


if __name__ == "__main__":
    main()
