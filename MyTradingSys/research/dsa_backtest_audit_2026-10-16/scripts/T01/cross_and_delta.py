import sys, csv, gzip
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode = True

WT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629")
OUT = WT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)

DEV_END = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)
KL = Path(r"F:/MTS/data/tom_raw/klines")

# 1) delta sign convention across loaders
print("== delta sign convention ==")
print("bt_data.cvd_delta = 2*taker_buy_volume - volume")
# orderflow file has explicit 'delta' column. Take a row and compare.
of = Path(r"F:/MTS/data/orderflow_1m/2024-12-02.csv.gz")
with gzip.open(of, "rt", encoding="utf-8") as fh:
    rdr = csv.reader(fh); hdr = next(rdr); cols = {n:i for i,n in enumerate(hdr)}
    n = 0
    for r in rdr:
        v = float(r[cols["buy_vol"]]) + float(r[cols["sell_vol"]])
        delta_calc = float(r[cols["buy_vol"]]) - float(r[cols["sell_vol"]])
        delta_file = float(r[cols["delta"]])
        cvd_kline = 2*float(r[cols["buy_vol"]]) - v  # by convention kline tbv=buy_vol
        if n < 3:
            print(f"  buy={r[cols['buy_vol']]} sell={r[cols['sell_vol']]} delta_file={delta_file:.4f} delta_buy_minus_sell={delta_calc:.4f} 2*tb-v={cvd_kline:.4f}")
        n += 1
        if n >= 3: break

# 2) close->open jump worst
print()
print("== close->open jumps >0.5% in DEV ==")
prev_c = None
for f in sorted(KL.glob("*.csv")):
    with f.open("r", encoding="utf-8") as fh:
        rdr = csv.reader(fh); fr = next(rdr, None)
        rows = []
        if fr and not fr[0].isdigit():
            for r in rdr: rows.append(r)
        else:
            if fr: rows.append(fr)
            for r in rdr: rows.append(r)
    for row in rows:
        try:
            t=int(row[0])
            if t >= DEV_END: continue
            o=float(row[1]); c=float(row[4])
        except Exception: continue
        if prev_c and prev_c>0:
            jump = abs(o-prev_c)/prev_c
            if jump>0.005:
                print(f"  {datetime.fromtimestamp(t/1000,timezone.utc).isoformat()} prev_close={prev_c} open={o} jump={jump:.4f}")
        prev_c = c

# 3) frozen bars list
print()
print("== frozen bars (h==l and v==0) sample ==")
cnt = 0
for f in sorted(KL.glob("*.csv")):
    with f.open("r", encoding="utf-8") as fh:
        rdr = csv.reader(fh); fr = next(rdr, None)
        rows = []
        if fr and not fr[0].isdigit():
            for r in rdr: rows.append(r)
        else:
            if fr: rows.append(fr)
            for r in rdr: rows.append(r)
    for row in rows:
        try:
            t=int(row[0])
            if t >= DEV_END: continue
            h=float(row[2]); l=float(row[3]); v=float(row[5])
        except Exception: continue
        if h==l and v==0:
            cnt += 1
            if cnt <= 10:
                print(f"  {datetime.fromtimestamp(t/1000,timezone.utc).isoformat()}")
print("total frozen DEV:", cnt)
