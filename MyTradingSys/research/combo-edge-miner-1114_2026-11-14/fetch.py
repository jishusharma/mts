"""Fetch inputs for the combo edge miner into F:\MTS\data_cache\binance\combo-edge-miner-1114 (public data.binance.vision only).
spot 4h and 1d klines with taker-buy base volume -> spot_<TF>/<SYM>USDT.csv   cols ts,o,h,l,c,v,tbv  (ts = bar open, ms)
futures funding, daily OI: copied from the nkp1 cache (same public source, sha256 sidecars) -> funding/, oi/  (no re-download).
Month files cover every full month; the running month comes from data-api.binance.vision."""
import io, os, sys, json, time, shutil, zipfile, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests

ROOT = r"F:\MTS\data_cache\binance\combo-edge-miner-1114"
NKP1 = r"F:\MTS\data_cache\binance_futures\nkp1"
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI VET ZEC NEO".split()
S = requests.Session()
S.mount("https://", requests.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32))


def get(url):
    for k in range(4):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 404:
                return None
            if r.status_code == 200:
                return r.content
        except Exception:
            time.sleep(1 + k)
    return None


def ms(x):
    x = int(float(x))
    return x // 1000 if x > 10 ** 14 else x


def fetch_tf(args):
    sym, tf = args
    out = os.path.join(ROOT, f"spot_{tf}", f"{sym}USDT.csv")
    if os.path.exists(out):
        return sym, tf, "cached"
    today = dt.date.today()
    rows = {}
    y, m = 2017, 8
    while (y, m) < (today.year, today.month):
        b = get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}USDT/{tf}/{sym}USDT-{tf}-{y}-{m:02d}.zip")
        if b:
            z = zipfile.ZipFile(io.BytesIO(b))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                p = ln.split(",")
                if p[0].isdigit():
                    rows[ms(p[0])] = (p[1], p[2], p[3], p[4], p[5], p[9])
        m += 1
        if m == 13:
            y, m = y + 1, 1
    step = {"4h": 4 * 3600000, "1d": 86400000}[tf]
    start = int(dt.datetime(today.year, today.month, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    while True:
        b = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}USDT&interval={tf}&limit=1000&startTime={start}")
        if not b:
            break
        k = json.loads(b)
        if not k:
            break
        for x in k:
            rows[int(x[0])] = (x[1], x[2], x[3], x[4], x[5], x[9])
        start = int(k[-1][0]) + step
        if len(k) < 1000:
            break
    if not rows:
        return sym, tf, "none"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ts = sorted(rows)
    with open(out + ".tmp", "w", newline="") as f:
        f.write("ts,o,h,l,c,v,tbv\n")
        for t in ts:
            f.write(f"{t}," + ",".join(rows[t]) + "\n")
    os.replace(out + ".tmp", out)
    return sym, tf, f"{len(ts)} bars {dt.datetime.fromtimestamp(ts[0]/1000, dt.timezone.utc):%Y-%m-%d}..{dt.datetime.fromtimestamp(ts[-1]/1000, dt.timezone.utc):%Y-%m-%d %H:%M}"


def copy_futures():
    for kind, sub in (("funding", "funding"), ("oi_daily", "oi")):
        os.makedirs(os.path.join(ROOT, sub), exist_ok=True)
        for s in SYMS:
            for suf in ("", ".meta.json"):
                src = os.path.join(NKP1, f"{s}USDT_{kind}.csv{suf}")
                dst = os.path.join(ROOT, sub, f"{s}USDT.csv{suf}")
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copyfile(src, dst)


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    copy_futures()
    with ThreadPoolExecutor(12) as ex:
        for r in ex.map(fetch_tf, [(s, tf) for s in SYMS for tf in ("1d", "4h")]):
            print(*r, flush=True)
    print("ALL DONE", flush=True)
