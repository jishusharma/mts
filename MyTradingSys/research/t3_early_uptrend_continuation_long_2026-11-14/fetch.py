"""Fetch inputs for the T3 early-uptrend study into F:\MTS\data_cache\binance\t3-early-uptrend-1114 (public data.binance.vision only).
spot_1d/<SYM>USDT.csv  cols ts,o,h,l,c,v,tbv (ts = bar open ms; tbv = taker-buy base volume)
funding/<SYM>USDT.csv  cols ts,rate: copied from the nkp1 cache where present, else downloaded from the public monthly
                       futures fundingRate archive (calc_time,last_funding_rate). No print for a coin = flat assumption in t3_study.py.
Run: python fetch.py   (idempotent, skips cached files). Writes fetch_report.json beside this file."""
import io, os, json, time, shutil, zipfile, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"F:\MTS\data_cache\binance\t3-early-uptrend-1114"
NKP1 = r"F:\MTS\data_cache\binance_futures\nkp1"
CANDS = ("NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT "
         "AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN").split()
SYMS = ["BTC"] + CANDS
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


def months(y0, m0):
    today = dt.date.today()
    y, m = y0, m0
    while (y, m) < (today.year, today.month):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def fetch_spot(sym):
    out = os.path.join(ROOT, "spot_1d", f"{sym}USDT.csv")
    if os.path.exists(out):
        return sym, "cached"
    rows = {}
    for y, m in months(2017, 8):
        b = get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}USDT/1d/{sym}USDT-1d-{y}-{m:02d}.zip")
        if b:
            z = zipfile.ZipFile(io.BytesIO(b))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                p = ln.split(",")
                if p[0].isdigit():
                    rows[ms(p[0])] = (p[1], p[2], p[3], p[4], p[5], p[9])
    today = dt.date.today()
    start = int(dt.datetime(today.year, today.month, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    while True:
        b = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}USDT&interval=1d&limit=1000&startTime={start}")
        if not b:
            break
        k = json.loads(b)
        if not k:
            break
        for x in k:
            rows[int(x[0])] = (x[1], x[2], x[3], x[4], x[5], x[9])
        start = int(k[-1][0]) + 86400000
        if len(k) < 1000:
            break
    if not rows:
        return sym, "none"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ts = sorted(rows)
    with open(out + ".tmp", "w", newline="") as f:
        f.write("ts,o,h,l,c,v,tbv\n")
        for t in ts:
            f.write(f"{t}," + ",".join(rows[t]) + "\n")
    os.replace(out + ".tmp", out)
    f0 = dt.datetime.fromtimestamp(ts[0] / 1000, dt.timezone.utc)
    f1 = dt.datetime.fromtimestamp(ts[-1] / 1000, dt.timezone.utc)
    return sym, f"{len(ts)} bars {f0:%Y-%m-%d}..{f1:%Y-%m-%d}"


def fetch_funding(sym):
    out = os.path.join(ROOT, "funding", f"{sym}USDT.csv")
    if os.path.exists(out):
        return sym, "cached"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    src = os.path.join(NKP1, f"{sym}USDT_funding.csv")
    if os.path.exists(src):
        shutil.copyfile(src, out)
        return sym, "nkp1 copy"
    rows = {}
    for y, m in months(2019, 9):
        b = get(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}USDT/{sym}USDT-fundingRate-{y}-{m:02d}.zip")
        if b:
            z = zipfile.ZipFile(io.BytesIO(b))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                p = ln.split(",")
                if p[0].isdigit():
                    rows[ms(p[0])] = p[2]
    if not rows:
        return sym, "none"
    with open(out + ".tmp", "w", newline="") as f:
        f.write("ts,rate\n")
        for t in sorted(rows):
            f.write(f"{t},{rows[t]}\n")
    os.replace(out + ".tmp", out)
    return sym, f"{len(rows)} prints (archive months only; the running month is not covered, flat fill)"


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    rep = {"spot": {}, "funding": {}}
    with ThreadPoolExecutor(12) as ex:
        for s, r in ex.map(fetch_spot, SYMS):
            rep["spot"][s] = r
            print("spot", s, r, flush=True)
        for s, r in ex.map(fetch_funding, SYMS):
            rep["funding"][s] = r
            print("funding", s, r, flush=True)
    with open(os.path.join(HERE, "fetch_report.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print("ALL DONE", flush=True)
