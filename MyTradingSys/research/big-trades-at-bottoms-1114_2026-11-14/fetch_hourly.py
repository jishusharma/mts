"""Download daily public trade dumps, aggregate to hourly large-trade buy/sell USD volume, delete the zip.
Venues: binance spot, binance usdm futures (aggTrades), bybit linear perp (trades). Output F:/MTS/data_cache/bigtrades/<venue>/<date>.csv"""
import os, sys, io, zipfile, gzip, datetime as dt, urllib.request, time
import pandas as pd, numpy as np
from concurrent.futures import ThreadPoolExecutor
OUT='F:/MTS/data_cache/bigtrades'; TMP=OUT+'/tmp'
LOWS=['2022-06-18','2022-11-21','2024-08-05','2025-04-07','2026-02-06','2026-07-01']
def days():
    s=set()
    for l in LOWS:
        d=dt.date.fromisoformat(l)
        for k in range(-4,5): s.add(d+dt.timedelta(days=k))
    d=dt.date(2026,10,24)
    while d<=dt.date(2026,11,13): s.add(d); d+=dt.timedelta(days=1)
    return sorted(s)
URL={'spot':'https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip',
     'fut':'https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip',
     'bybit':'https://public.bybit.com/trading/BTCUSDT/BTCUSDT%s.csv.gz'}
def agg(df,tcol,usd,sell,unit):
    h=(df[tcol].values//unit)*unit//1000 if unit else None
    return h
def process(venue,day):
    ds=day.isoformat(); outd=f'{OUT}/{venue}'; os.makedirs(outd,exist_ok=True); fo=f'{outd}/{ds}.csv'
    if os.path.exists(fo): return
    tmp=f'{TMP}/{venue}_{ds}.dl'
    for a in range(4):
        try:
            urllib.request.urlretrieve(URL[venue]%ds,tmp); break
        except Exception as e:
            err=e; time.sleep(3)
    else:
        open(fo+'.missing','w').write(str(err)); print('MISSING',venue,ds,err,flush=True); return
    z=None
    if venue=='bybit':
        f=gzip.open(tmp,'rt')
    else:
        z=zipfile.ZipFile(tmp); f=z.open(z.namelist()[0])
    first=f.readline(); f.seek(0) if hasattr(f,'seek') and venue!='bybit' else None
    # re-open for cleanliness
    if venue=='bybit':
        f.close(); f=gzip.open(tmp,'rt'); rd=pd.read_csv(f,chunksize=3_000_000,usecols=['timestamp','side','size','price'])
    else:
        f.close(); z=zipfile.ZipFile(tmp); f=z.open(z.namelist()[0])
        hdr=first.decode()[:1].isalpha()
        rd=pd.read_csv(f,chunksize=3_000_000,header=0 if hdr else None,names=None if hdr else ['id','price','qty','f','l','t','m','b'][:first.decode().count(',')+1],usecols=None if hdr else ['price','qty','t','m'])
    parts=[]
    for ch in rd:
        if venue=='bybit':
            t=(ch['timestamp'].values*1000).astype('int64'); sell=(ch['side'].values=='Sell'); qty=ch['size'].values; usd=qty*ch['price'].values
        else:
            tc='transact_time' if 'transact_time' in ch else 't'; mc='is_buyer_maker' if 'is_buyer_maker' in ch else 'm'
            t=ch[tc].values.astype('int64'); 
            if t.max()>1e14: t=t//1000
            sell=ch[mc].astype(str).str.lower().values=='true'; qty=(ch['quantity'] if 'quantity' in ch else ch['qty']).values; usd=ch['price'].values*qty
        hr=t//3600000
        g=pd.DataFrame({'hr':hr,'usd':usd,'qty':qty,'sell':sell})
        r=[]
        for col,thr,nm in (('usd',0,'all'),('usd',1e6,'1m'),('usd',5e6,'5m'),('qty',10,'b10'),('qty',50,'b50')):
            x=g[g[col]>=thr]
            p=x.pivot_table(index='hr',columns='sell',values='usd',aggfunc=['sum','count'],fill_value=0)
            p.columns=[f'{a}_{"sell" if b else "buy"}_{nm}' for a,b in p.columns]
            r.append(p)
        parts.append(pd.concat(r,axis=1))
    cols=[f'{a}_{b}_{n}' for a in ('sum','count') for b in ('buy','sell') for n in ('all','1m','5m','b10','b50')]
    o=pd.concat(parts).groupby(level=0).sum().reindex(columns=cols,fill_value=0.0).fillna(0.0)
    o.index=pd.to_datetime(o.index*3600,unit='s'); o.index.name='hour_utc'
    o.to_csv(fo); f.close()
    try: z.close()
    except Exception: pass
    os.remove(tmp)
    print('ok',venue,ds,len(o),flush=True)
def safe(j):
    try: process(*j)
    except Exception as e: print('ERR',j,repr(e),flush=True)
if __name__=='__main__':
    jobs=[(v,d) for d in days() for v in ('spot','fut','bybit')]
    if len(sys.argv)>1: jobs=jobs[:int(sys.argv[1])]
    with ThreadPoolExecutor(4) as ex: list(ex.map(safe,jobs))
