"""Smoke for the Binance DoH path (public data): resolve fapi/fstream, one live 4h kline, fstream TLS reachability.
Exit 0 = OK. Run: python scripts/dev/binance_doh_smoke.py"""
import json
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from MyTradingSys.runtime import binance_doh as bd  # noqa: E402

ok = True
for h in ("fapi.binance.com", "fstream.binance.com"):
    try:
        print("DOH", h, bd.resolve(h))
    except OSError as e:
        ok = False
        print("DOH FAIL", h, e)
try:
    with bd.urlopen("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=4h&limit=1", timeout=10) as r:
        k = json.loads(r.read())[0]
        print("KLINE 4h", r.status, k[0], "close", k[4])
except Exception as e:  # noqa: BLE001
    ok = False
    print("KLINE FAIL", e)
try:
    bd.urlopen("https://fstream.binance.com/", timeout=10).close()
    print("FSTREAM tls ok")
except urllib.error.HTTPError as e:
    print("FSTREAM tls ok (HTTP", e.code, "= server reached)")
except Exception as e:  # noqa: BLE001
    ok = False
    print("FSTREAM FAIL", e)
print("SMOKE", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
