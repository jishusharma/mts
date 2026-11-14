"""Download context data for nkp1 (public data.binance.vision only). Raw outputs go to F:\\MTS\\data_cache only.
spot 1d klines (taker buy volume) -> binance_spot\\nkp1\\<SYM>USDT_1d_tbv.csv      cols ts,o,h,l,c,v,tbv   (ts = bar open ms)
futures funding                   -> binance_futures\\nkp1\\<SYM>USDT_funding.csv  cols ts,rate
futures OI (metrics daily files)  -> binance_futures\\nkp1\\<SYM>USDT_oi_daily.csv cols ts,oi   (ts = day end ms, last 5m row of that UTC day)
Each with a .meta.json sidecar (source, rows, sha256, key ts, first_ts)."""
import io, os, sys, json, hashlib, zipfile, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests

ROOT = r"F:\MTS\data_cache"
BASE = "https://data.binance.vision/data"
SYMS = "BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC BCH SOL DOT AVAX ATOM UNI VET NEO ZEC EOS DASH IOTA".split()
S = requests.Session()
S.mount("https://", requests.adapters.HTTPAdapter(pool_connections=48, pool_maxsize=48))


def get(url):
    for k in range(3):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 404:
                return None
            if r.status_code == 200:
                return r.content
        except Exception:
            pass
    return None


def rows(zbytes):
    z = zipfile.ZipFile(io.BytesIO(zbytes))
    return z.read(z.namelist()[0]).decode().strip().splitlines()


def months(y0=2019, m0=1):
    t = dt.date.today()
    y, m = y0, m0
    while (y, m) <= (t.year, t.month):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def write(path, header, lines, src):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    txt = header + "\n" + "\n".join(lines) + "\n"
    with open(path, "w", newline="") as f:
        f.write(txt)
    meta = dict(source=src, rows=len(lines), sha256=hashlib.sha256(txt.encode()).hexdigest(), key="ts",
                first_ts=int(lines[0].split(",")[0]) if lines else None, fetched=dt.datetime.utcnow().isoformat() + "Z")
    json.dump(meta, open(path + ".meta.json", "w"))


def ms(x):
    x = int(float(x))
    return x // 1000 if x > 10 ** 14 else x


def spot(sym):
    out = os.path.join(ROOT, "binance_spot", "nkp1", f"{sym}USDT_1d_tbv.csv")
    if os.path.exists(out):
        return
    L = []
    for y, m in months():
        b = get(f"{BASE}/spot/monthly/klines/{sym}USDT/1d/{sym}USDT-1d-{y}-{m:02d}.zip")
        if b is None and (y, m) >= (dt.date.today().year, dt.date.today().month):
            continue
        if b is None:
            continue
        for ln in rows(b):
            p = ln.split(",")
            if not p[0].isdigit():
                continue
            L.append(f"{ms(p[0])},{p[1]},{p[2]},{p[3]},{p[4]},{p[5]},{p[9]}")
    if L:
        write(out, "ts,o,h,l,c,v,tbv", L, f"{BASE}/spot/monthly/klines/{sym}USDT/1d")


def funding(sym):
    out = os.path.join(ROOT, "binance_futures", "nkp1", f"{sym}USDT_funding.csv")
    if os.path.exists(out):
        return
    L = []
    for y, m in months():
        b = get(f"{BASE}/futures/um/monthly/fundingRate/{sym}USDT/{sym}USDT-fundingRate-{y}-{m:02d}.zip")
        if b is None:
            continue
        for ln in rows(b):
            p = ln.split(",")
            if not p[0].isdigit():
                continue
            L.append(f"{ms(p[0])},{p[-1] if len(p) < 4 else p[2]}")
    if L:
        write(out, "ts,rate", L, f"{BASE}/futures/um/monthly/fundingRate/{sym}USDT")


def oi_day(args):
    sym, d = args
    b = get(f"{BASE}/futures/um/daily/metrics/{sym}USDT/{sym}USDT-metrics-{d.isoformat()}.zip")
    if b is None:
        return None
    last = None
    for ln in rows(b):
        p = ln.split(",")
        if p[0] == "create_time":
            continue
        last = p
    if last is None:
        return None
    end = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000) + 86400000 - 1
    return f"{end},{last[2]}"


def oi(sym, ex):
    out = os.path.join(ROOT, "binance_futures", "nkp1", f"{sym}USDT_oi_daily.csv")
    if os.path.exists(out):
        return
    # futures listing date from funding file (first funding settlement), metrics start no earlier than 2020-09-01
    fp = os.path.join(ROOT, "binance_futures", "nkp1", f"{sym}USDT_funding.csv")
    if not os.path.exists(fp):
        return
    first = int(open(fp).read().splitlines()[1].split(",")[0])
    d0 = max(dt.date(2020, 9, 1), dt.datetime.fromtimestamp(first / 1000, dt.timezone.utc).date())
    days = []
    d = d0
    end = dt.date.today() - dt.timedelta(days=1)
    while d <= end:
        days.append((sym, d))
        d += dt.timedelta(days=1)
    res = list(ex.map(oi_day, days))
    L = [r for r in res if r]
    if L:
        write(out, "ts,oi", L, f"{BASE}/futures/um/daily/metrics/{sym}USDT (last 5m row per UTC day)")
    print(sym, "oi days", len(L), "of", len(days), flush=True)


if __name__ == "__main__":
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(spot, SYMS))
        print("spot done", flush=True)
        list(ex.map(funding, SYMS))
        print("funding done", flush=True)
    with ThreadPoolExecutor(40) as ex:
        for s in SYMS:
            oi(s, ex)
    print("ALL DONE", flush=True)
