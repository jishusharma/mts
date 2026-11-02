# OURS: weekdays where at 13:15Z price sits within 0.15% of the day low (00Z..13:15Z). How much lower does the low go by 14:30Z (pre-open) and by 16:30Z (first 2h US)? 2022-01-01..2025-06-30.
import glob,csv,statistics as st,datetime as dt,collections
END=dt.date(2025,7,1); days=collections.defaultdict(dict)
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        d=dt.datetime.fromtimestamp(t,dt.timezone.utc)
        if d.date()>=END: break
        if d.weekday()>4: continue
        days[d.date()][d.hour*60+d.minute]=(float(r[3]),float(r[4]))
pre=[];us=[];reb=[]
for d,m in days.items():
    if len(m)<1400: continue
    L=min(m[i][0] for i in m if i<=795); px=m.get(795)
    if not px or px[1]/L-1>0.0015: continue
    L2=min(m[i][0] for i in m if 795<i<=870); L3=min(m[i][0] for i in m if 795<i<=990)
    pre.append(L2/L-1); us.append(L3/L-1); reb.append(m[990][1]/px[1]-1)
n=len(pre); q=lambda xs,p: sorted(xs)[int(p*len(xs))]
print('days n=%d (weekday, px at 13:15Z within 0.15%% of day low)'%n)
print('low extended by 14:30Z: %2.0f%% of days; median ext %+.2f%%  p25 %+.2f%%'%(100*sum(x<-0.0005 for x in pre)/n,100*st.median(pre),100*q(pre,0.25)))
print('low extended by 16:30Z: %2.0f%% of days; median ext %+.2f%%  p25 %+.2f%%  p10 %+.2f%%'%(100*sum(x<-0.0005 for x in us)/n,100*st.median(us),100*q(us,0.25),100*q(us,0.10)))
print('px 16:30Z vs 13:15Z: up %2.0f%%  median %+.2f%%'%(100*sum(x>0 for x in reb)/n,100*st.median(reb)))
