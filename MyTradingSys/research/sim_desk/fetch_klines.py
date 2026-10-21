"""Fetch public Binance USD-M 1m klines (data.binance.vision, free, checksum-verified) for the desk's DEV months.

python MyTradingSys/research/sim_desk/fetch_klines.py ETHUSDT
Writes <klines folder>/<SYMBOL>-1m-YYYY-MM.csv for 2022-01..2024-06 only (warm-up + DEV; never later). Skips files that exist.
"""
import hashlib
import io
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(os.environ.get('SIM_DESK_KLINES', 'F:/MTS/data/tom_raw/klines'))
BASE = 'https://data.binance.vision/data/futures/um/monthly/klines'


def months(first='2022-01', last='2024-06'):
    y, m = map(int, first.split('-'))
    while f'{y:04d}-{m:02d}' <= last:
        yield f'{y:04d}-{m:02d}'
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def fetch(symbol, root=ROOT):
    for m in months():
        out = Path(root) / f'{symbol}-1m-{m}.csv'
        if out.exists():
            continue
        url = f'{BASE}/{symbol}/1m/{symbol}-1m-{m}.zip'
        z = get(url)
        want = get(url + '.CHECKSUM').split()[0].decode()
        if hashlib.sha256(z).hexdigest() != want:
            raise RuntimeError(f'checksum mismatch {url}')
        with zipfile.ZipFile(io.BytesIO(z)) as zf:
            data = zf.read(zf.namelist()[0])
        out.write_bytes(data)
        print('ok', out.name, flush=True)


if __name__ == '__main__':
    fetch(sys.argv[1] if len(sys.argv) > 1 else 'ETHUSDT')
