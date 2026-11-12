"""Fetch + reduce Binance USD-M BTCUSDT aggTrades monthly zips, DEV window months only (2022-01 warm-up .. 2024-05), to D:.
Resume: python MyTradingSys/research/btc_of_level_auction_1112/fetch_b2.py
Zips: D:/MTS_data/binance_aggtrades/um/BTCUSDT/ (sha256 checked against the .CHECKSUM file). Reduced 15m tables:
D:/MTS_data/binance_aggtrades/reduced/. Log: D:/MTS_data/binance_aggtrades/fetch_b2.log. Nothing is unpacked; one download at a time.
Refuses any month outside 2022-01 .. 2024-05 (VALIDATION/GAP/RESERVE/HOLDOUT are never fetched). Stops if D: free < 150 GB.
"""
import hashlib
import os
import shutil
import sys
import time
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2  # noqa: E402

ROOT = 'D:/MTS_data/binance_aggtrades'
ZIPS = ROOT + '/um/BTCUSDT'
URL = 'https://data.binance.vision/data/futures/um/monthly/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip'
MIN_FREE_GB = 150
LOG = ROOT + '/fetch_b2.log'
MONTHS = ['%d-%02d' % (y, m) for y in (2022, 2023, 2024) for m in range(1, 13) if b2.month_ok('%d-%02d' % (y, m))]


def log(msg):
    line = time.strftime('%Y-%m-%dT%H:%M:%S ') + msg
    print(line, flush=True)
    with open(LOG, 'a') as fh:
        fh.write(line + '\n')


def free_gb():
    return shutil.disk_usage('D:/').free / 1e9


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 22), b''):
            h.update(blk)
    return h.hexdigest()


def get(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'mts-research-fetch/1.0'})
    t = time.time()
    n = 0
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as out:
        while True:
            blk = r.read(1 << 20)
            if not blk:
                break
            out.write(blk)
            n += len(blk)
    return n, time.time() - t


def good(zpath, cpath):
    if not (os.path.exists(zpath) and os.path.exists(cpath)):
        return False
    want = open(cpath).read().split()[0].lower()
    return sha256(zpath) == want


def fetch(tag):
    zpath = '%s/BTCUSDT-aggTrades-%s.zip' % (ZIPS, tag)
    cpath = zpath + '.CHECKSUM'
    if good(zpath, cpath):
        return zpath, 0, 0.0
    for attempt in range(3):
        get(URL % tag + '.CHECKSUM', cpath)
        n, s = get(URL % tag, zpath + '.part')
        os.replace(zpath + '.part', zpath)
        if good(zpath, cpath):
            return zpath, n, s
        log('CHECKSUM MISMATCH %s attempt %d' % (tag, attempt + 1))
        os.remove(zpath)
    raise SystemExit('checksum failed 3x for %s' % tag)


def main():
    os.makedirs(ZIPS, exist_ok=True)
    os.makedirs(ROOT + '/reduced', exist_ok=True)
    os.makedirs('D:/MTS_data/scratch', exist_ok=True)
    for tag in MONTHS:
        if not b2.month_ok(tag):
            raise SystemExit('refused month %s' % tag)
        out = '%s/reduced/BTCUSDT-bars15-%s.csv.gz' % (ROOT, tag)
        log('D: free %.1f GB before %s' % (free_gb(), tag))
        if free_gb() < MIN_FREE_GB:
            raise SystemExit('STOP: D: free below %d GB' % MIN_FREE_GB)
        zpath, n, s = fetch(tag)
        size = os.path.getsize(zpath)
        if n:
            log('%s downloaded %.2f GB in %.0f s = %.1f MB/s, checksum ok' % (tag, size / 1e9, s, n / 1e6 / s))
        else:
            log('%s zip present, checksum ok (%.2f GB)' % (tag, size / 1e9))
        if os.path.exists(out):
            log('%s reduced table present, skipped' % tag)
            continue
        t = time.time()
        df, ntr = b2.reduce_zip(zpath)
        el = time.time() - t
        df.to_csv(out + '.tmp', index=False, compression='gzip')
        os.replace(out + '.tmp', out)
        log('%s reduced: %d trades, %d bars, wall %.0f s, read %.1f MB/s zip (%.2f M trades/s), D: free %.1f GB'
            % (tag, ntr, len(df), el, size / 1e6 / el, ntr / 1e6 / el, free_gb()))
    log('ALL DONE %d months' % len(MONTHS))


if __name__ == '__main__':
    main()
