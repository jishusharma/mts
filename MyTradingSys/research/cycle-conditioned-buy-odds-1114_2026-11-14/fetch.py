import urllib.request,json,os,csv
C='F:/MTS/data_cache/'
def get(u):return json.load(urllib.request.urlopen(u,timeout=60))
d=get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=CapMVRVCur&frequency=1d&start_time=2011-01-01&page_size=10000")['data']
tmp=C+'coinmetrics/btc_mvrv.csv.tmp'
with open(tmp,'w') as f:
    f.write('date,mvrv\n')
    for x in d:f.write(f"{x['time'][:10]},{x['CapMVRVCur']}\n")
os.replace(tmp,C+'coinmetrics/btc_mvrv.csv')
k=get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime=1793750400000&limit=60")
import datetime
tmp=C+'binance_1d/BTCUSDT_1d_tail.csv.tmp'
with open(tmp,'w') as f:
    f.write('date,high,low,close\n')
    for r in k:
        dt=datetime.datetime.fromtimestamp(r[0]/1000,datetime.UTC).strftime('%Y-%m-%d')
        f.write(f"{dt},{r[2]},{r[3]},{r[4]},{r[6]}\n".replace(f",{r[6]}\n","\n"))
os.replace(tmp,C+'binance_1d/BTCUSDT_1d_tail.csv')
print(len(d),len(k),k[-1][0],k[-1][6])
