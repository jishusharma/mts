import sys
sys.dont_write_bytecode = True
"""Fetch public Binance USD-M BTCUSDT 1m klines 2020-01..2021-12 (DEV_EXT) to a dir outside the repo, SHA256-verified.
Public market data only. Usage: python fetch_dev_ext.py <out_dir>   (writes <out_dir>/klines/BTCUSDT-1m-YYYY-MM.csv)"""
import hashlib, io, urllib.request, zipfile
from pathlib import Path

BASE = "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MTS-dev-ext/1.0"}), timeout=180) as r:
        return r.read()


def main():
    out = Path(sys.argv[1]) / "klines"
    out.mkdir(parents=True, exist_ok=True)
    for y in (2020, 2021):
        for m in range(1, 13):
            name = f"BTCUSDT-1m-{y}-{m:02d}"
            dst = out / f"{name}.csv"
            if dst.exists():
                continue
            z = get(f"{BASE}/{name}.zip")
            want = get(f"{BASE}/{name}.zip.CHECKSUM").decode().split()[0]
            assert hashlib.sha256(z).hexdigest() == want, name
            zf = zipfile.ZipFile(io.BytesIO(z))
            dst.write_bytes(zf.read(zf.namelist()[0]))
            print("ok", name, flush=True)


if __name__ == "__main__":
    main()
