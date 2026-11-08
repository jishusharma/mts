import json,urllib.request,datetime as dt
U="https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=1000&startTime="
st=int(dt.datetime(2026,6,1,tzinfo=dt.timezone.utc).timestamp()*1000)
rows=json.load(urllib.request.urlopen(U+str(st),timeout=30))
json.dump(rows,open("k4h.json","w"))
t=[dt.datetime.fromtimestamp(r[0]/1000,dt.timezone.utc) for r in rows]
o=[float(r[1]) for r in rows];h=[float(r[2]) for r in rows];l=[float(r[3]) for r in rows];c=[float(r[4]) for r in rows]
# RSI14 Wilder
n=14;rsi=[None]*len(c);g=[max(c[i]-c[i-1],0) for i in range(1,len(c))];d=[max(c[i-1]-c[i],0) for i in range(1,len(c))]
ag=sum(g[:n])/n;ad=sum(d[:n])/n;rsi[n]=100-100/(1+ag/ad)
for i in range(n+1,len(c)):
    ag=(ag*(n-1)+g[i-1])/n;ad=(ad*(n-1)+d[i-1])/n;rsi[i]=100-100/(1+ag/ad) if ad else 100
ma=[None]*len(c)
for i in range(len(c)):
    w=[x for x in rsi[max(0,i-13):i+1] if x is not None]
    if len(w)==14: ma[i]=sum(w)/14
# WaveTrend LB n1=10 n2=21
ap=[(h[i]+l[i]+c[i])/3 for i in range(len(c))]
def ema(x,p):
    a=2/(p+1);out=[x[0]]
    for v in x[1:]: out.append(a*v+(1-a)*out[-1])
    return out
esa=ema(ap,10);dd=ema([abs(ap[i]-esa[i]) for i in range(len(c))],10)
ci=[(ap[i]-esa[i])/(0.015*dd[i]) if dd[i] else 0 for i in range(len(c))]
wt1=ema(ci,21);wt2=[None]*len(c)
for i in range(3,len(c)): wt2[i]=sum(wt1[i-3:i+1])/4
import csv
with open("ind.csv","w",newline="") as f:
    w=csv.writer(f);w.writerow(["t","o","h","l","c","rsi","rsi_ma","wt1","wt2"])
    for i in range(len(c)): w.writerow([t[i].strftime("%m-%d %H"),o[i],h[i],l[i],c[i],None if rsi[i] is None else round(rsi[i],1),None if ma[i] is None else round(ma[i],1),round(wt1[i],1),None if wt2[i] is None else round(wt2[i],1)])
print(len(rows),t[0],t[-1])
