# OURS definitions, fixed before run: P0=13:00Z open, US window 13:00-16:59Z, H/L=window high/low,
# rally: H/P0-1 >= 1.5%; at 20:00Z (X = open of 20:00 bar) giveback (H-X)/(H-P0) >= 0.5.
# Outcomes over 20:00Z..+24h: trades below L, trades above H, which first, close-to-close return. No fees, descriptive.
import glob,csv,collections,statistics as st
bars={}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t  # us vs ms
        bars[t//1000*1000 if False else t]=(float(r[1]),float(r[2]),float(r[3]),float(r[4]))
ts=sorted(bars); m={t//1000:bars[t] for t in ts}
days=sorted({t//86400 for t in m})
def rng(a,b): return [m[t] for t in range(a,b,60) if t in m]
ev=[];base=[]
for d in days:
    s=d*86400; w=rng(s+13*3600,s+17*3600); after=rng(s+20*3600,s+44*3600)
    if len(w)<200 or len(after)<1300 or (s+20*3600) not in m: continue
    P0=w[0][0];H=max(b[1] for b in w);L=min(b[2] for b in w);X=m[s+20*3600][0];Y=after[-1][3]
    base.append(Y/X-1)
    if H/P0-1<0.015 or (H-X)/(H-P0)<0.5: continue
    first=None
    for b in after:
        if b[2]<L: first='L';break
        if b[1]>H: first='H';break
    ev.append(dict(d=d,dn=any(b[2]<L for b in after),up=any(b[1]>H for b in after),first=first,ret=Y/X-1,g=(H-X)/(H-P0)))
n=len(ev);print('n',n,'of',len(base),'days')
print('below US-window low within 24h',sum(e['dn'] for e in ev),'above US high',sum(e['up'] for e in ev))
print('first hit',collections.Counter(e['first'] for e in ev))
print('24h ret median %.2f%% mean %.2f%% up-share %d/%d'%(100*st.median([e['ret'] for e in ev]),100*st.mean([e['ret'] for e in ev]),sum(e['ret']>0 for e in ev),n))
print('baseline all days 24h median %.2f%% up-share %.0f%%'%(100*st.median(base),100*sum(x>0 for x in base)/len(base)))
import datetime as dt
for e in ev[-6:]: print(dt.date.fromordinal(dt.date(1970,1,1).toordinal()+e['d']),e['first'],'%.2f'%(100*e['ret']))
