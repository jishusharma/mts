r"""fetch_1m.py - Binance spot USDT 1m klines from data.binance.vision monthly (+ daily for the open month)
into F:\MTS\data_cache\binance_1m\<SYM>_1m.npz  (keys t_ms,o,h,l,c all float64, sorted, unique).
Idempotent/resumable: per-month parts cached in <out>/_parts/<SYM>/. Timestamps from 2025 are microseconds -> normalised to ms.
Also writes <out>/_coverage.json (first/last, rows, gap count, missing minutes per symbol).
Usage: python fetch_1m.py [--symbols BTC,ETH,...] [--start 2019-01] [--end 2026-11-13] [--workers 2] [--slot]
"""
import argparse, ctypes, io, json, os, sys, time, urllib.request, urllib.error, zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
import numpy as np

OUT = Path(r"F:\MTS\data_cache\binance_1m")
BASE = "https://data.binance.vision/data/spot"
NK20 = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()


def _lower_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def _get(url, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mts-maker-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == retries - 1:
                raise
        except Exception:
            if i == retries - 1:
                raise
        time.sleep(2 ** i)


def parse_zip(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        raw = z.read(z.namelist()[0])
    rows = []
    for ln in raw.decode().splitlines():
        p = ln.split(",")
        if not p or not p[0].strip().isdigit():
            continue  # header
        rows.append((float(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[4])))
    a = np.array(rows, dtype=np.float64).reshape(-1, 5)
    if len(a) and a[0, 0] > 1e14:  # microseconds
        a[:, 0] = np.floor(a[:, 0] / 1000.0)
    return a


def get_part(sym, kind, stamp, d: Path):
    f = d / f"{stamp}.npy"
    none = d / f"{stamp}.none"
    if f.exists():
        return np.load(f)
    if none.exists():
        return None
    url = f"{BASE}/{kind}/klines/{sym}/1m/{sym}-1m-{stamp}.zip"
    blob = _get(url)
    if blob is None:
        none.write_text("404")
        return None
    a = parse_zip(blob)
    np.save(f, a)
    return a


def months(start, end):
    y, m = start
    while (y, m) <= end:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def fetch_symbol(coin, start_ym, end_d):
    sym = coin + "USDT"
    d = OUT / "_parts" / sym
    d.mkdir(parents=True, exist_ok=True)
    parts = []
    last_full = (end_d.year, end_d.month)
    # month is complete only if end_d is its last day
    nxt = end_d + timedelta(days=1)
    if nxt.month == end_d.month:
        last_full = (end_d.year, end_d.month - 1) if end_d.month > 1 else (end_d.year - 1, 12)
    for y, m in months(start_ym, last_full):
        a = get_part(sym, "monthly", f"{y}-{m:02d}", d)
        if a is not None and len(a):
            parts.append(a)
    if last_full != (end_d.year, end_d.month):
        day = date(end_d.year, end_d.month, 1)
        while day <= end_d:
            a = get_part(sym, "daily", day.isoformat(), d)
            if a is not None and len(a):
                parts.append(a)
            day += timedelta(days=1)
    if not parts:
        return sym, None
    a = np.concatenate(parts)
    a = a[np.argsort(a[:, 0], kind="stable")]
    a = a[np.concatenate(([True], np.diff(a[:, 0]) > 0))]
    t = a[:, 0]
    dt = np.diff(t)
    gaps = dt[dt > 60000]
    cov = dict(sym=sym, first=int(t[0]), last=int(t[-1]), rows=int(len(t)),
               first_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(t[0] / 1000)),
               last_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(t[-1] / 1000)),
               gap_count=int(len(gaps)), missing_minutes=int(((gaps / 60000) - 1).sum()),
               max_gap_min=int(gaps.max() / 60000) if len(gaps) else 1)
    tmp = OUT / f"{sym}_1m.tmp.npz"
    np.savez_compressed(tmp, t_ms=a[:, 0], o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4])
    os.replace(tmp, OUT / f"{sym}_1m.npz")
    return sym, cov


def acquire_slot():
    base = Path(r"F:\MTS\maker_slots")
    base.mkdir(parents=True, exist_ok=True)
    while True:
        for i in range(4):
            p = base / f"slot{i}"
            try:
                p.mkdir()
                return p
            except FileExistsError:
                pass
        time.sleep(20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default=",".join(NK20))
    ap.add_argument("--start", default="2019-01")
    ap.add_argument("--end", default="2026-11-13")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--slot", action="store_true")
    a = ap.parse_args()
    _lower_priority()
    OUT.mkdir(parents=True, exist_ok=True)
    slot = acquire_slot() if a.slot else None
    try:
        sy, sm = map(int, a.start.split("-"))
        end_d = date.fromisoformat(a.end)
        covf = OUT / "_coverage.json"
        cov = json.loads(covf.read_text()) if covf.exists() else {}
        coins = [c.strip().upper().replace("USDT", "") for c in a.symbols.split(",") if c.strip()]
        with ThreadPoolExecutor(a.workers) as ex:
            for sym, c in ex.map(lambda c: fetch_symbol(c, (sy, sm), end_d), coins):
                cov[sym] = c
                covf.write_text(json.dumps(cov, indent=1))
                print(sym, c, flush=True)
    finally:
        if slot:
            try:
                slot.rmdir()
            except OSError:
                pass


if __name__ == "__main__":
    main()
