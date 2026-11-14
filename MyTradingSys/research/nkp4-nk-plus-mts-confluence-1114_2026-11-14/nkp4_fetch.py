"""Fetch futures OI (hourly from 5m metrics), funding, and spot 1h taker klines for the 20 NK coins.
Raw outputs: F:\MTS\data_cache\<venue>\<slug>\ with .meta.json sidecars (key ts, ms). Public archive only."""
import io, json, time, zipfile, hashlib, datetime as dt, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
SLUG = "nkp4-nk-plus-mts-confluence-1114"
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI NEAR FIL ALGO".split()
ROOT = Path(r"F:\MTS\data_cache")
FUT = ROOT / "binance" / SLUG
SPOT = ROOT / "binance_spot" / SLUG
BASE = "https://data.binance.vision/data"


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MTS-research/1.0"}), timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1 + i)
        except Exception:
            time.sleep(1 + i)
    return None


def rows_of(b):
    z = zipfile.ZipFile(io.BytesIO(b))
    return z.read(z.namelist()[0]).decode().splitlines()


def meta(path, source, n, ts):
    h = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    Path(str(path) + ".meta.json").write_text(json.dumps(dict(
        source=source, fetched_utc=dt.datetime.utcnow().isoformat(), rows=int(n), first_ts=int(ts[0]) if n else None,
        last_ts=int(ts[-1]) if n else None, sha256=h, key="ts")))


def oi_day(sym, d):
    b = get(f"{BASE}/futures/um/daily/metrics/{sym}/{sym}-metrics-{d.isoformat()}.zip")
    if b is None:
        return None
    out = []
    for ln in rows_of(b)[1:]:
        p = ln.split(",")
        t = dt.datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
        if t.minute == 0 and p[2]:
            out.append((int(t.timestamp() * 1000), float(p[2])))
    return out


def do_oi(base):
    sym = base + "USDT"; path = FUT / f"{sym}_oi_1h.npz"
    if path.exists():
        return base, "cached"
    d0 = dt.date(2020, 9, 1); today = dt.datetime.utcnow().date()
    # probe first month with data (first of month +/- a few days)
    first = None
    m = d0
    while m < today and first is None:
        for k in (1, 8, 15, 22):
            if oi_day(sym, m.replace(day=k)):
                first = m; break
        m = (m.replace(day=28) + dt.timedelta(days=5)).replace(day=1)
    if first is None:
        return base, "no-data"
    days = [first + dt.timedelta(days=i) for i in range((today - first).days)]
    rows = []
    for d in days:
        r = oi_day(sym, d)
        if r: rows += r
    a = np.array(sorted(set(rows)), dtype=np.float64)
    np.savez_compressed(path, ts=a[:, 0].astype(np.int64), oi=a[:, 1])
    meta(path, f"{BASE}/futures/um/daily/metrics/{sym}", len(a), a[:, 0].astype(np.int64))
    return base, f"{len(a)} rows first {dt.datetime.utcfromtimestamp(a[0,0]/1000):%Y-%m-%d}"


def do_fund(base):
    sym = base + "USDT"; path = FUT / f"{sym}_funding.npz"
    if path.exists():
        return base, "cached"
    today = dt.datetime.utcnow().date(); rows = []
    y, mo = 2019, 9
    while (y, mo) < (today.year, today.month):
        b = get(f"{BASE}/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{y}-{mo:02d}.zip")
        if b:
            for ln in rows_of(b)[1:]:
                p = ln.split(",")
                rows.append((int(p[0]), float(p[2])))
        mo += 1
        if mo > 12: y, mo = y + 1, 1
    if not rows:
        return base, "no-data"
    a = np.array(sorted(set(rows)), dtype=np.float64)
    np.savez_compressed(path, ts=a[:, 0].astype(np.int64), fr=a[:, 1])
    meta(path, f"{BASE}/futures/um/monthly/fundingRate/{sym}", len(a), a[:, 0].astype(np.int64))
    return base, f"{len(a)} rows first {dt.datetime.utcfromtimestamp(a[0,0]/1000):%Y-%m-%d}"


def do_taker(base):
    sym = base + "USDT"; path = SPOT / f"{sym}_1h.npz"
    if path.exists():
        return base, "cached"
    today = dt.datetime.utcnow().date(); rows = []
    y, mo = 2019, 1
    while (y, mo) < (today.year, today.month):
        b = get(f"{BASE}/spot/monthly/klines/{sym}/1h/{sym}-1h-{y}-{mo:02d}.zip")
        if b:
            for ln in rows_of(b):
                p = ln.split(",")
                if not p[0].isdigit(): continue
                t = int(p[0]); t = t // 1000 if t > 10**14 else t
                rows.append((t, float(p[4]), float(p[5]), float(p[9])))
        mo += 1
        if mo > 12: y, mo = y + 1, 1
    # tail of current month via API
    last = (rows[-1][0] + 3600000) if rows else 0
    while last:
        b = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1h&limit=1000&startTime={last}")
        if not b: break
        k = json.loads(b)
        if not k: break
        rows += [(x[0], float(x[4]), float(x[5]), float(x[9])) for x in k]
        last = k[-1][0] + 3600000
        if len(k) < 1000: break
    a = np.array(sorted(set(rows)), dtype=np.float64)
    np.savez_compressed(path, ts=a[:, 0].astype(np.int64), c=a[:, 1], v=a[:, 2], tb=a[:, 3])
    meta(path, f"{BASE}/spot/monthly/klines/{sym}/1h", len(a), a[:, 0].astype(np.int64))
    return base, f"{len(a)} rows"


if __name__ == "__main__":
    FUT.mkdir(parents=True, exist_ok=True); SPOT.mkdir(parents=True, exist_ok=True)
    for name, fn, w in (("taker", do_taker, 6), ("funding", do_fund, 6), ("oi", do_oi, 20)):
        with ThreadPoolExecutor(w) as ex:
            for r in ex.map(fn, SYMS): print(name, *r, flush=True)
