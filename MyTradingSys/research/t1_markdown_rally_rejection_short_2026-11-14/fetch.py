"""Fetch 15m spot klines from data.binance.vision (public) for the T1 primary coins -> F:/MTS/data_cache/binance/t1-markdown-rally-rejection/
<SYM>USDT_15m.npz (keys t,o,h,l,c,v; t = open time ms) + .meta.json sidecar. Coins with < 730 days of history are recorded in dropped.json, not kept for the study."""
import io, os, sys, json, time, zipfile, hashlib, datetime as dt, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np

OUT = Path(r"F:\MTS\data_cache") / "binance" / "t1-markdown-rally-rejection"
SYMS = "EOS NEO IOTA ZEC DASH ZIL VET BAT ICX QTUM ONT ENJ MANA SAND THETA XTZ HBAR AAVE GRT CHZ".split()
BASE = "https://data.binance.vision/data/spot/"
TODAY = dt.datetime.now(dt.timezone.utc).date()
START = (2018, 10)


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
    out = []
    for ln in z.read(z.namelist()[0]).decode().splitlines():
        p = ln.split(",")
        if p and p[0][:1].isdigit():
            out.append(p)
    return out


def ts_ms(x):
    x = int(x)
    return x // 1000 if x > 10**14 else x  # 2025+ spot files carry microseconds


def months():
    y, m = START
    ey, em = (TODAY.year, TODAY.month - 1) if TODAY.month > 1 else (TODAY.year - 1, 12)
    while (y, m) <= (ey, em):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def fetch(sym):
    jobs = [f"{BASE}monthly/klines/{sym}USDT/15m/{sym}USDT-15m-{y}-{m:02d}.zip" for y, m in months()]
    d = dt.date(TODAY.year, TODAY.month, 1)
    while d < TODAY:
        jobs.append(f"{BASE}daily/klines/{sym}USDT/15m/{sym}USDT-15m-{d.isoformat()}.zip")
        d += dt.timedelta(days=1)
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for b in ex.map(get, jobs):
            if b is not None:
                rows += rows_of(b)
    if not rows:
        return None
    a = np.array([[ts_ms(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in rows])
    _, i = np.unique(a[:, 0], return_index=True)
    a = a[i]
    return dict(t=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dropped = {}
    for s in SYMS:
        p = OUT / f"{s}USDT_15m.npz"
        if (OUT / (p.name + ".meta.json")).exists():
            print(s, "cached", flush=True)
            continue
        d = fetch(s)
        if d is None:
            dropped[s] = "no data"
            print(s, "NO-DATA", flush=True)
            continue
        tmp = OUT / (p.name + ".tmp.npz")
        np.savez_compressed(tmp, **d)
        os.replace(tmp, p)
        days = (int(d["t"][-1]) - int(d["t"][0])) / 86400000
        meta = dict(source=BASE + "(monthly|daily)/klines/<SYM>USDT/15m", fetch_utc=dt.datetime.now(dt.timezone.utc).isoformat(), rows=int(len(d["t"])),
                    first_utc=str(np.datetime64(int(d["t"][0]), "ms")), last_utc=str(np.datetime64(int(d["t"][-1]), "ms")), history_days=round(days, 1),
                    sha256=hashlib.sha256(p.read_bytes()).hexdigest(), key="t (ms open time)")
        (OUT / (p.name + ".meta.json")).write_text(json.dumps(meta, indent=1))
        print(s, meta["rows"], meta["first_utc"], meta["last_utc"], meta["history_days"], flush=True)
    # dropped list (history < 730 d), from sidecars
    for s in SYMS:
        mp = OUT / f"{s}USDT_15m.npz.meta.json"
        if mp.exists() and json.loads(mp.read_text())["history_days"] < 730:
            dropped[s] = f"history {json.loads(mp.read_text())['history_days']} d < 730"
    (OUT / "dropped.json").write_text(json.dumps(dropped, indent=1))
    print("dropped", dropped)


if __name__ == "__main__":
    main()
