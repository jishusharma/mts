"""Download Binance USD-M BTCUSDT daily metrics (5m open interest, top-trader and taker long/short ratios)
from the public archive data.binance.vision into F:/MTS/data/binance_metrics (local only, never committed).
Usage: python fetch_metrics.py 2022-01-01 2025-12-31"""
import datetime as dt, io, sys, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OUT = Path('F:/MTS/data/binance_metrics'); OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-{}.zip'

def get(d):
    f = OUT / f'BTCUSDT-metrics-{d}.csv'
    if f.exists(): return 'have'
    try:
        z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL.format(d), timeout=30).read()))
        f.write_bytes(z.read(z.namelist()[0])); return 'ok'
    except Exception as e:
        return f'miss {d} {e}'

a, b = (dt.date.fromisoformat(x) for x in sys.argv[1:3])
days = [str(a + dt.timedelta(i)) for i in range((b - a).days + 1)]
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, days))
print({k: sum(r.startswith(k) for r in res) for k in ('ok', 'have', 'miss')})
print([r for r in res if r.startswith('miss')][:10])
