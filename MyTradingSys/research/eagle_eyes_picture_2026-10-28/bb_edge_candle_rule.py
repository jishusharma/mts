# OURS (operator teaching 2026-11-03): Bollinger-band edge candle rule on 1D and 1W.
# SHORT: one of the last 3 closes was above the upper BB(20,2); the next time price trades below the prior close,
#        short at that close; stop = prior candle high (variant: highest high of the last 3 candles); target = BB middle.
# LONG (mirror, Aug 17 case): one of the last 3 closes below the lower BB; price trades above the prior close; stop = prior low.
# BASE: same entry (price crosses prior close) with no BB-edge condition.
# Path ordered on 1m bars (stop vs target first), hold max 20 candles. Split by 50-candle trend. Fee-free, HOLDOUT sealed.
import glob,csv,statistics as st,datetime as dt,collections
END=dt.date(2025,7,1); k=[]
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k.append((t,float(r[1]),float(r[2]),float(r[3]),float(r[4])))
k.sort()
def bars(key):
    out=[];cur=None
    for t,o,h,l,c in k:
        g=key(t)
        if g!=cur: out.append([g,o,h,l,c,[]]); cur=g
        b=out[-1]; b[2]=max(b[2],h); b[3]=min(b[3],l); b[4]=c; b[5].append((t,o,h,l,c))
    return out
def run(name,B,HOLD=20):
    n=len(B); mid=[None]*n; up=[None]*n; lo=[None]*n; sma=[None]*n
    for i in range(19,n):
        w=[b[4] for b in B[i-19:i+1]]; m=sum(w)/20; sd=(sum((x-m)**2 for x in w)/20)**.5
        mid[i]=m; up[i]=m+2*sd; lo[i]=m-2*sd
    for i in range(49,n): sma[i]=sum(b[4] for b in B[i-49:i+1])/50
    res=collections.defaultdict(list)
    for i in range(50,n-HOLD-1):
        prev=B[i-1]; edge_s=any(B[j][4]>up[j] for j in range(i-3,i)); edge_l=any(B[j][4]<lo[j] for j in range(i-3,i))
        trend='up' if prev[4]>sma[i-1] else 'down'
        for side,cond,stop_v,target in (('SHORT',edge_s,{'prev high':prev[2],'3-bar high':max(B[j][2] for j in range(i-3,i))},mid[i-1]),
                                        ('LONG',edge_l,{'prev low':prev[3],'3-bar low':min(B[j][3] for j in range(i-3,i))},mid[i-1])):
            # entry: first 1m bar of candle i trading through the prior close
            m1=[x for b in B[i:i+HOLD] for x in b[5]]; ent=None
            for j,(t,o,h,l,c) in enumerate(B[i][5]):
                if (side=='SHORT' and l<prev[4]) or (side=='LONG' and h>prev[4]): ent=j;break
            if ent is None: continue
            path=m1[ent+1:]
            # confirmed variant: candle i CLOSES through the prior close; enter at that close, stop = candle i extreme
            cur=B[i]; conf=(side=='SHORT' and cur[4]<prev[4]) or (side=='LONG' and cur[4]>prev[4])
            if conf: stop_v=dict(stop_v); stop_v['CLOSE,cur ext']=cur[2] if side=='SHORT' else cur[3]
            for sname,stop in stop_v.items():
                if sname.startswith('CLOSE'):
                    e=cur[4]; path=[x for b in B[i+1:i+1+HOLD] for x in b[5]]; target=mid[i]
                else: e=prev[4]
                dist=abs(stop-e)/e; tdist=abs(target-e)/e
                if dist==0 or (side=='SHORT' and target>=e) or (side=='LONG' and target<=e): continue
                hit=None
                for t,o,h,l,c in path:
                    if side=='SHORT':
                        if h>=stop: hit='STOP';break
                        if l<=target: hit='TGT';break
                    else:
                        if l<=stop: hit='STOP';break
                        if h>=target: hit='TGT';break
                hit=hit or 'none'
                if hit=='TGT': R=tdist/dist
                elif hit=='STOP': R=-1.0
                else: R=((e-path[-1][4]) if side=='SHORT' else (path[-1][4]-e))/e/dist
                tag='edge' if cond else 'base'
                res[(side,tag,sname,trend)].append((hit,tdist/dist,R))
                res[(side,tag,sname,'all')].append((hit,tdist/dist,R))
    print('\n==',name,'candles',n)
    for key in sorted(res):
        xs=res[key]; c=collections.Counter(h for h,_,_ in xs); N=len(xs)
        if N<8 or key[2].startswith('3-bar') and key[3]!='all': continue
        print('%-5s %-4s stop=%-13s trend=%-4s n=%4d  target(mid) first %3.0f%%  stop first %3.0f%%  neither/20 %3.0f%%  target/stop med %.2f  mean R %+.2f'%(
            key[0],key[1],key[2],key[3],N,100*c['TGT']/N,100*c['STOP']/N,100*c['none']/N,st.median(r for _,r,_ in xs),st.mean(R for _,_,R in xs)))
run('1D',bars(lambda t:t//86400))
run('1W',bars(lambda t:(t-345600)//604800))
