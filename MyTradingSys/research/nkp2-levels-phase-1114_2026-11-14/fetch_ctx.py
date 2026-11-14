"""Fetch context data from data.binance.vision into F:/MTS/data_cache/binance/nkp2-levels-phase-1114 (public market data only).
 klines_1h_<SYM>.npz  : ts(ms open), o,h,l,c,v,tbv   (spot 1h incl. taker-buy base volume, for C6)
 funding_<SYM>.npz    : ts(ms), rate                  (futures/um fundingRate, for C5)
 oi_<SYM>.npz         : ts(ms, hourly), oi_value      (futures/um metrics sum_open_interest_value, last 5m record of each hour, for C4)
Each file has a .meta.json sidecar (source, fetch UTC, rows, first/last ts, sha256, key 'ts' in ms). Prints first available date per coin/series.
Usage: python fetch_ctx.py"""
import io, os, sys, json, time, zipfile, hashlib, datetime as dt, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np

OUT = Path(r"F:\MTS\data_cache") / "binance" / "nkp2-levels-phase-1114"
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
BASE = "https://data.binance.vision/data/"
TODAY = dt.datetime.now(dt.timezone.utc).date()


def get(url):
    for i in range(4):
        try:
            return urllib.request.urlopen(url, timeout=40).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1 + i)
        except Exception:
            time.sleep(1 + i)
    return None


def rows_of(blob):
    z = zipfile.ZipFile(io.BytesIO(blob))
    txt = z.read(z.namelist()[0]).decode()
    out = []
    for ln in txt.splitlines():
        p = ln.split(",")
        if not p or not p[0] or not p[0][0].isdigit() and not p[0][0] == "2":
            continue
        out.append(p)
    return out


def months(a, b):
    y, m = a
    while (y, m) <= b:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def kl_month(sym, y, m):
    b = get(f"{BASE}spot/monthly/klines/{sym}USDT/1h/{sym}USDT-1h-{y}-{m:02d}.zip")
    return [] if b is None else rows_of(b)


def kl_day(sym, d):
    b = get(f"{BASE}spot/daily/klines/{sym}USDT/1h/{sym}USDT-1h-{d.isoformat()}.zip")
    return [] if b is None else rows_of(b)


def ts_ms(x):
    x = int(x)
    return x // 1000 if x > 10**14 else x  # spot 2025+ files carry microseconds


def fetch_klines(sym):
    rows = []
    cur = (TODAY.year, TODAY.month)
    for y, m in months((2019, 1), (cur[0], cur[1] - 1) if cur[1] > 1 else (cur[0] - 1, 12)):
        rows += kl_month(sym, y, m)
    d = dt.date(cur[0], cur[1], 1)
    while d < TODAY:
        rows += kl_day(sym, d)
        d += dt.timedelta(days=1)
    a = np.array([[ts_ms(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])] for r in rows])
    _, i = np.unique(a[:, 0], return_index=True)
    a = a[i]
    return dict(ts=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5], tbv=a[:, 6])


def fetch_funding(sym):
    rows = []
    for y, m in months((2019, 9), (TODAY.year, TODAY.month)):
        b = get(f"{BASE}futures/um/monthly/fundingRate/{sym}USDT/{sym}USDT-fundingRate-{y}-{m:02d}.zip")
        if b is None:
            continue
        for p in rows_of(b):
            rows.append([int(p[0]), float(p[2])])
    if not rows:
        return None
    a = np.array(rows)
    _, i = np.unique(a[:, 0], return_index=True)
    a = a[i]
    return dict(ts=a[:, 0].astype(np.int64), rate=a[:, 1])


def oi_day(args):
    sym, d = args
    b = get(f"{BASE}futures/um/daily/metrics/{sym}USDT/{sym}USDT-metrics-{d.isoformat()}.zip")
    if b is None:
        return []
    out = {}
    z = zipfile.ZipFile(io.BytesIO(b))
    for ln in z.read(z.namelist()[0]).decode().splitlines()[1:]:
        p = ln.split(",")
        try:
            t = dt.datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
            out[int(t.timestamp() * 1000) // 3600000 * 3600000] = float(p[3])  # last record of the hour wins
        except Exception:
            continue
    return sorted(out.items())


def fetch_oi(sym):
    days = [dt.date(2020, 9, 1) + dt.timedelta(days=k) for k in range((TODAY - dt.date(2020, 9, 1)).days)]
    rows = []
    with ThreadPoolExecutor(16) as ex:
        for r in ex.map(oi_day, [(sym, d) for d in days]):
            rows += r
    if not rows:
        return None
    a = np.array(rows)
    _, i = np.unique(a[:, 0], return_index=True)
    a = a[i]
    return dict(ts=a[:, 0].astype(np.int64), oi_value=a[:, 1])


def save(name, d, source):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    tmp = OUT / (name + ".tmp.npz")
    np.savez_compressed(tmp, **d)
    os.replace(tmp, p)
    meta = dict(source=source, fetch_utc=dt.datetime.now(dt.timezone.utc).isoformat(), rows=int(len(d["ts"])),
                first_ts=int(d["ts"][0]), last_ts=int(d["ts"][-1]), first_utc=str(np.datetime64(int(d["ts"][0]), "ms")),
                last_utc=str(np.datetime64(int(d["ts"][-1]), "ms")), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), key="ts (ms)")
    (OUT / (name + ".meta.json")).write_text(json.dumps(meta, indent=1))
    return meta


def main():
    which = sys.argv[1:] or ["klines", "funding", "oi"]
    OUT.mkdir(parents=True, exist_ok=True)
    for kind in which:
        for s in SYMS:
            name = {"klines": f"klines_1h_{s}.npz", "funding": f"funding_{s}.npz", "oi": f"oi_{s}.npz"}[kind]
            if (OUT / (name + ".meta.json")).exists():
                print(kind, s, "cached", flush=True)
                continue
            d = {"klines": fetch_klines, "funding": fetch_funding, "oi": fetch_oi}[kind](s)
            if d is None:
                print(kind, s, "NO-DATA", flush=True)
                continue
            m = save(name, d, BASE + {"klines": "spot/(monthly|daily)/klines", "funding": "futures/um/monthly/fundingRate", "oi": "futures/um/daily/metrics"}[kind])
            print(kind, s, m["rows"], "first", m["first_utc"], "last", m["last_utc"], flush=True)


if __name__ == "__main__":
    main()
