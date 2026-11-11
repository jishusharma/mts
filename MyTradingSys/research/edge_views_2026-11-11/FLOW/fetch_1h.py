"""Download public Binance USD-M BTCUSDT 1h klines (monthly zips) to F:/MTS/edge_views_data/k1h."""
import io, os, urllib.request, urllib.error, zipfile
OUT = "F:/MTS/edge_views_data/k1h"
os.makedirs(OUT, exist_ok=True)
for y in range(2020, 2027):
    for m in range(1, 13):
        f = f"BTCUSDT-1h-{y}-{m:02d}"
        if os.path.exists(f"{OUT}/{f}.csv"):
            continue
        url = f"https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1h/{f}.zip"
        try:
            b = urllib.request.urlopen(url, timeout=30).read()
        except urllib.error.HTTPError as e:
            print(f, e.code); continue
        zipfile.ZipFile(io.BytesIO(b)).extractall(OUT)
print(len(os.listdir(OUT)))
