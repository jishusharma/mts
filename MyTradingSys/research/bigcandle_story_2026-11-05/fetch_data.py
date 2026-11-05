"""Fetch recent public Binance USD-M BTCUSDT 5m klines + metrics from data.binance.vision into F:/MTS/data/bigcandle_cache.

Public market data only (CLAUDE.md pre-approved). Used for the 2026-11-04 walk-through and the weekly-streak phase label.
Run: python fetch_data.py  (idempotent; skips files already extracted).
"""
import io
import os
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

CACHE = 'F:/MTS/data/bigcandle_cache'
BASE = 'https://data.binance.vision/data/futures/um/daily/'
K_FROM, M_FROM, TO = date(2026, 8, 1), date(2026, 10, 1), date(2026, 11, 4)


def get(job):
    kind, d = job
    s = d.isoformat()
    name = 'BTCUSDT-5m-%s' % s if kind == 'k5' else 'BTCUSDT-metrics-%s' % s
    url = BASE + ('klines/BTCUSDT/5m/' if kind == 'k5' else 'metrics/BTCUSDT/') + name + '.zip'
    out = os.path.join(CACHE, kind)
    if os.path.exists(os.path.join(out, name + '.csv')):
        return None
    os.makedirs(out, exist_ok=True)
    err = ''
    for _ in range(3):
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
            zipfile.ZipFile(io.BytesIO(data)).extractall(out)
            return None
        except Exception as e:  # noqa: BLE001
            err = str(e)
    return url + ' ' + err


def main():
    jobs, d = [], K_FROM
    while d <= TO:
        jobs.append(('k5', d))
        if d >= M_FROM:
            jobs.append(('met', d))
        d += timedelta(1)
    with ThreadPoolExecutor(6) as ex:
        bad = [r for r in ex.map(get, jobs) if r]
    print('jobs', len(jobs), 'failed', bad)


if __name__ == '__main__':
    main()
