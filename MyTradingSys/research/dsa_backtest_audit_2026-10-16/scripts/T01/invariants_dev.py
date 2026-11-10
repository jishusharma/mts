import csv, sys, json
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode = True

DEV_END = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)
KL = Path(r"F:/MTS/data/tom_raw/klines")
OUT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629\MyTradingSys\research\dsa_backtest_audit_2026-10-16\scripts\T01\out")
OUT.mkdir(parents=True, exist_ok=True)

bad_ohlc=0; bad_tb=0; bad_qv=0; bad_tr=0; neg_v=0; frozen=0
prev_close=None; jumps=0; jump_ex=[]
n=0
worst=[]
for f in sorted(KL.glob("*.csv")):
    with f.open("r", encoding="utf-8") as fh:
        rdr=csv.reader(fh); fr=next(rdr,None)
        if fr and not fr[0].isdigit():
            pass
        else:
            rdr=csv.reader([",".join(fr)] + list(rdr)) if fr else rdr
        it=rdr
        if fr and not fr[0].isdigit(): pass
        else:
            # re-iterate with first row
            with f.open("r", encoding="utf-8") as fh2:
                rdr2=csv.reader(fh2); first=next(rdr2)
                rows=[first]
                for r in rdr2: rows.append(r)
            it=iter(rows)
        for row in it:
            if not row or len(row)<10: continue
            try:
                t=int(row[0])
                if t>=DEV_END: continue
                o=float(row[1]); h=float(row[2]); l=float(row[3]); c=float(row[4])
                v=float(row[5]); qv=float(row[7]) if row[7] else 0.0
                cnt=int(float(row[8])) if row[8] else 0
                tbv=float(row[9])
            except Exception:
                continue
            n+=1
            if not (l<=o<=h and l<=c<=h and h>=l):
                bad_ohlc+=1
                if len(worst)<20: worst.append(("ohlc",t,o,h,l,c))
            if v<0: neg_v+=1
            if tbv<0 or tbv>v+1e-9:
                bad_tb+=1
                if len(worst)<20: worst.append(("tb",t,v,tbv))
            if v>0 and not (l-1e-6 <= qv/v <= h+1e-6):
                bad_qv+=1
                if len(worst)<20: worst.append(("qv",t,qv/v,l,h))
            if v>0 and cnt<1: bad_tr+=1
            if h==l and v==0: frozen+=1
            if prev_close is not None:
                if prev_close>0:
                    jump=abs(o-prev_close)/prev_close
                    if jump>0.005:
                        jumps+=1
                        if len(jump_ex)<20: jump_ex.append((t,prev_close,o,jump))
            prev_close=c

print(f"DEV bars scanned: {n}")
print(f"bad_ohlc: {bad_ohlc}")
print(f"negative_volume: {neg_v}")
print(f"taker_buy out of [0,v]: {bad_tb}")
print(f"quote_volume/volume out of [l,h]: {bad_qv}")
print(f"volume>0 with count<1: {bad_tr}")
print(f"frozen bars (h==l and v==0): {frozen}")
print(f"close->open jumps >0.5%: {jumps}")
print("--- 20 worst ---")
for w in worst: print(w)
print("--- 20 jumps ---")
for j in jump_ex: print(j)
