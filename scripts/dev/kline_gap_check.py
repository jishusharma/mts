"""Gap check and top-up for public Binance USD-M 1m klines on disk.

python scripts/dev/kline_gap_check.py ETHUSDT 2022-01 2026-09 [--fetch]
Months up to DEV_LAST are parsed bar by bar. VALIDATION/HOLDOUT months (after DEV_LAST) are never parsed:
they are fetched checksum-verified, written unread and checked by row count only.
"""
import calendar
import hashlib
import io
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(os.environ.get('SIM_DESK_KLINES', 'F:/MTS/data/tom_raw/klines'))
BASE = 'https://data.binance.vision/data/futures/um/monthly/klines'
DEV_LAST = '2024-06'
MIN_MS = 60_000


def months(first, last):
    y, m = map(int, first.split('-'))
    while f'{y:04d}-{m:02d}' <= last:
        yield f'{y:04d}-{m:02d}'
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def expected_rows(month):
    y, m = map(int, month.split('-'))
    return calendar.monthrange(y, m)[1] * 1440


def month_start_ms(month):
    y, m = map(int, month.split('-'))
    return calendar.timegm((y, m, 1, 0, 0, 0)) * 1000


def missing_minutes(open_times_ms, first_ms, last_ms):
    have = set(open_times_ms)
    return [t for t in range(first_ms, last_ms + 1, MIN_MS) if t not in have]


def check_month(path, month, sealed=False):
    """sealed: count rows only, never parse a price or timestamp."""
    path = Path(path)
    if not path.exists():
        return {'month': month, 'missing': expected_rows(month), 'mode': 'absent'}
    if sealed:
        n = sum(1 for ln in path.read_bytes().splitlines() if ln[:1].isdigit() or ln == b'x')
        return {'month': month, 'missing': expected_rows(month) - n, 'mode': 'rows'}
    ts = [int(ln.split(',')[0]) for ln in path.read_text(encoding='utf-8').splitlines() if ln[:1].isdigit()]
    start = month_start_ms(month)
    return {'month': month, 'missing': len(missing_minutes(ts, start, start + (expected_rows(month) - 1) * MIN_MS)),
            'mode': 'bars'}


def _get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def fetch_month(symbol, month, root=ROOT):
    out = Path(root) / f'{symbol}-1m-{month}.csv'
    if out.exists():
        return False
    url = f'{BASE}/{symbol}/1m/{symbol}-1m-{month}.zip'
    z = _get(url)
    want = _get(url + '.CHECKSUM').split()[0].decode()
    if hashlib.sha256(z).hexdigest() != want:
        raise RuntimeError(f'checksum mismatch {url}')
    with zipfile.ZipFile(io.BytesIO(z)) as zf:
        out.write_bytes(zf.read(zf.namelist()[0]))
    return True


def run(symbol, first, last, fetch=False, root=ROOT):
    bad = []
    for m in months(first, last):
        if fetch and fetch_month(symbol, m, root):
            print('fetched', symbol, m, flush=True)
        r = check_month(Path(root) / f'{symbol}-1m-{m}.csv', m, sealed=m > DEV_LAST)
        if r['missing']:
            bad.append(r)
    total = sum(r['missing'] for r in bad)
    print(f'{symbol} {first}..{last}: months={len(list(months(first, last)))} months_with_gaps={len(bad)} missing_1m_bars={total}')
    for r in bad:
        print('  ', r)
    return total


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    sys.exit(1 if run(a[0], a[1], a[2], fetch='--fetch' in sys.argv) else 0)
