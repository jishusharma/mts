"""Fetch public 4h spot klines from data-api.binance.vision for candidate coins into runtime_data/edge6-capitulation-breadth-1113/ (ignored cache)."""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge6-capitulation-breadth-1113"))
CANDS = ("BTC ETH BNB XRP ADA SOL DOGE DOT LTC LINK BCH TRX AVAX ATOM ETC XLM NEAR UNI FIL ALGO VET ICP AAVE EOS XTZ THETA SAND MANA AXS GRT CHZ ENJ "
         "BAT ZEC DASH NEO IOTA ONT QTUM ZIL HBAR CRV SNX COMP SUSHI YFI 1INCH RUNE KSM EGLD FLOW KAVA CHR ANKR CELR HOT ONE RVN WAVES GALA ENS LRC ICX ZRX "
         "STORJ SXP MKR DYDX IMX SHIB AR FTM CAKE CHZ XEM OMG BAND OCEAN RLC SKL CTK ALPHA REEF TFUEL CVC").split()
START = 1606780800000  # 2020-12-01
def get(u):
    for k in range(6):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if k == 5: return None
            time.sleep(1 + k)
def one(c):
    rows, st = [], START
    while True:
        d = get("https://data-api.binance.vision/api/v3/klines?symbol=%sUSDT&interval=4h&limit=1000&startTime=%d" % (c, st))
        if not d: break
        rows += [[r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[7])] for r in d]  # t,o,h,l,c,quote vol
        if len(d) < 1000: break
        st = d[-1][0] + 1
    if rows: json.dump(rows, open(os.path.join(OUT, c + "_4h.json"), "w"))
    return c, len(rows), (time.strftime("%Y-%m-%d", time.gmtime(rows[0][0] / 1000)) if rows else None)
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        for c, n, f in ex.map(one, list(dict.fromkeys(CANDS))): print(c, n, f, flush=True)
