"""Fetch Bybit v5 public 5m linear klines (all history from 2020 or listing) into runtime_data (ignored)."""
import sys, os, time, json, urllib.request, concurrent.futures as cf
OUT = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'runtime_data', 'edge-nk-rsi-hilega-1113')
SYMS = ['BTCUSDT','ETHUSDT','SOLUSDT','XRPUSDT','DOGEUSDT','BNBUSDT','ADAUSDT','LINKUSDT','LTCUSDT','AVAXUSDT']
import calendar
START = calendar.timegm((2020,1,1,0,0,0)) * 1000
def get(url):
    for k in range(12):
        try:
            j = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'mts-research'}), timeout=20))
            if j.get('retCode') == 0: return j
            time.sleep(2+2*k)
        except Exception:
            time.sleep(1+k)
    raise RuntimeError(url)
def fetch(sym):
    fn = os.path.join(OUT, sym + '_5m.csv')
    rows = {}
    end = int(time.time()*1000)
    while True:
        j = get(f'https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval=5&start={START}&end={end}&limit=1000')
        L = j['result']['list']
        if not L: break
        for r in L: rows[int(r[0])] = r
        mn = min(int(r[0]) for r in L)
        if mn <= START or len(L) < 2: break
        end = mn - 1
    with open(fn,'w') as f:
        f.write('t,o,h,l,c,v\n')
        for t in sorted(rows):
            r = rows[t]; f.write(','.join([str(t)]+r[1:6])+'\n')
    return sym, len(rows)
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(3) as ex:
        for s, n in ex.map(fetch, SYMS): print(s, n, flush=True)
