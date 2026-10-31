"""Fetch public Binance spot daily klines (data.binance.vision), months 2017-08 .. 2024-06 only, into event_study/data/ (gitignored)."""
import io
import urllib.request
import zipfile
from pathlib import Path

import run_event_study as es

URL = 'https://data.binance.vision/data/spot/monthly/klines/{s}/1d/{s}-1d-{m}.zip'


def main():
    es.DATA.mkdir(exist_ok=True)
    for s in ('BTCUSDT', 'ETHUSDT'):
        for m in es.months():
            out = es.DATA / f'{s}-1d-{m}.csv'
            if out.exists():
                continue
            raw = urllib.request.urlopen(URL.format(s=s, m=m), timeout=60).read()
            z = zipfile.ZipFile(io.BytesIO(raw))
            out.write_bytes(z.read(z.namelist()[0]))
    print('ok', len(list(es.DATA.glob('*.csv'))), 'files')


if __name__ == '__main__':
    main()
