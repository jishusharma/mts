import json, urllib.request, datetime as dt, time, pandas as pd, sys
sys.path.insert(0,'.')
from fetch_hourly import days
OUT='F:/MTS/data_cache/bigtrades/premium_1h.csv'
def get(u):
    for a in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'mts-research'}),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    raise err
ds=days(); rows_cb=[]; rows_bn=[]
# group into contiguous ranges
rng=[]; s=ds[0]; p=ds[0]
for d in ds[1:]:
    if (d-p).days>1: rng.append((s,p)); s=d
    p=d
rng.append((s,p))
for a,b in rng:
    t0=dt.datetime(a.year,a.month,a.day,tzinfo=dt.timezone.utc); t1=dt.datetime(b.year,b.month,b.day,tzinfo=dt.timezone.utc)+dt.timedelta(days=1)
    t=t0
    while t<t1:
        e=min(t+dt.timedelta(hours=299),t1)
        c=get('https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600&start=%s&end=%s'%(t.strftime('%Y-%m-%dT%H:%M:%SZ'),e.strftime('%Y-%m-%dT%H:%M:%SZ')))
        for r in c: rows_cb.append(r)  # time,low,high,open,close,volume
        t=e+dt.timedelta(hours=1); time.sleep(0.2)
    t=int(t0.timestamp()*1000)
    while t<int(t1.timestamp()*1000):
        k=get('https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1000&startTime=%d&endTime=%d'%(t,int(t1.timestamp()*1000)))
        if not k: break
        rows_bn+=k; t=k[-1][0]+3600000
    print(a,b,len(rows_cb),len(rows_bn),flush=True)
cb=pd.DataFrame(rows_cb,columns=['t','lo','hi','op','cb_close','cb_vol']).drop_duplicates('t'); cb['hour_utc']=pd.to_datetime(cb.t,unit='s')
bn=pd.DataFrame(rows_bn).iloc[:,[0,4,5]]; bn.columns=['t','bn_close','bn_vol']; bn=bn.drop_duplicates('t'); bn['hour_utc']=pd.to_datetime(bn.t,unit='ms')
m=cb[['hour_utc','cb_close','cb_vol']].merge(bn[['hour_utc','bn_close','bn_vol']],on='hour_utc').astype({'bn_close':float,'bn_vol':float})
m['prem_bp']=(m.cb_close/m.bn_close-1)*1e4
m.sort_values('hour_utc').to_csv(OUT,index=False); print(len(m))
