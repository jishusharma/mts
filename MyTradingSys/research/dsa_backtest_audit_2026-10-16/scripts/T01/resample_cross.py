import csv, sys
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode = True
WT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629")
OUT = WT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)

DEV_END = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)
KL = Path(r"F:/MTS/data/tom_raw/klines")

# resample 1m -> 1d per UTC day
def load_1m(d):
    rows = []
    for f in sorted(d.glob("*.csv")):
        with f.open("r", encoding="utf-8") as fh:
            rdr = csv.reader(fh); fr = next(rdr, None)
            it = rdr
            if fr and not fr[0].isdigit():
                pass
            else:
                if fr: rows.append(fr)
                for r in rdr: rows.append(r)
                continue
            for r in rdr: rows.append(r)
    return rows

days = {}
for f in sorted(KL.glob("*.csv")):
    with f.open("r", encoding="utf-8") as fh:
        rdr = csv.reader(fh); fr = next(rdr, None)
        it = rdr
        if fr and not fr[0].isdigit():
            pass
        else:
            if fr:
                try: t = int(fr[0])
                except: t = None
                if t is not None and t < DEV_END:
                    day = t // 86400000
                    days.setdefault(day, []).append(fr)
            it = rdr
        for row in it:
            try:
                t = int(row[0])
                if t >= DEV_END: continue
            except: continue
            day = t // 86400000
            days.setdefault(day, []).append(row)

print("days resampled:", len(days))

# read raw_1d
RAWD = Path(r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1d/klines")
daily = {}
for f in sorted(RAWD.glob("*.csv")):
    with f.open("r", encoding="utf-8") as fh:
        rdr = csv.reader(fh); fr = next(rdr, None)
        it = rdr
        if fr and not fr[0].isdigit():
            pass
        else:
            if fr:
                try:
                    t = int(fr[0]); daily[t // 86400000] = fr
                except: pass
            it = rdr
        for row in it:
            try: t = int(row[0]); daily[t // 86400000] = row
            except: continue

print("raw_1d days in DEV:", sum(1 for d in daily if d*86400000 < DEV_END))

# compare OHLCV
fields = {1:"open",2:"high",3:"low",4:"close",5:"volume"}
mism = {v:0 for v in fields.values()}
ex = []
for day, rows in days.items():
    if day not in daily: continue
    rows_sorted = sorted(rows, key=lambda r: int(r[0]))
    o = float(rows_sorted[0][1]); c = float(rows_sorted[-1][4])
    h = max(float(r[2]) for r in rows_sorted); l = min(float(r[3]) for r in rows_sorted)
    v = sum(float(r[5]) for r in rows_sorted)
    got = {"open":o,"high":h,"low":l,"close":c,"volume":v}
    d = daily[day]
    exp = {"open":float(d[1]),"high":float(d[2]),"low":float(d[3]),"close":float(d[4]),"volume":float(d[5])}
    for k in fields.values():
        if abs(got[k]-exp[k]) > max(1e-6, abs(exp[k])*1e-9):
            mism[k] += 1
            if len(ex) < 10:
                ex.append((day, k, got[k], exp[k]))

print("mismatches per field:", mism)
print("examples (day_index, field, resampled, raw_1d):")
for e in ex: print("  ", e)
