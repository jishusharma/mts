import sys
sys.dont_write_bytecode = True
import csv, gzip, io
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1019-0713")
LIVE = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
F = Path(r"F:/MTS/data")
OUT = ROOT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)

DEV_END = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)
DEV_START = int(datetime(2022,1,1,tzinfo=timezone.utc).timestamp()*1000)

def to_ms(t):
    return t // 1000 if t > 1e14 else t

def scan_1m_dev():
    per_day = {}
    for f in sorted((F/"tom_raw/klines").glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].lstrip("-").isdigit(): continue
                try: t = to_ms(int(row[0]))
                except: continue
                if t < DEV_START or t >= DEV_END: continue
                d = t // 86400000
                o,h,l,c,v = (float(row[i]) for i in (1,2,3,4,5))
                cur = per_day.get(d)
                if cur is None:
                    per_day[d] = dict(o=o,h=h,l=l,c=c,v=v,n=1)
                else:
                    if o < cur["o"]: cur["o"] = o
                    if h > cur["h"]: cur["h"] = h
                    if l < cur["l"]: cur["l"] = l
                    cur["c"] = c
                    cur["v"] += v
                    cur["n"] += 1
    return per_day

def scan_1d():
    rows = {}
    for f in sorted((LIVE/"Dumps/backtest/raw_1d/klines").glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].lstrip("-").isdigit(): continue
                try: t = to_ms(int(row[0]))
                except: continue
                if t < DEV_START or t >= DEV_END: continue
                d = t // 86400000
                rows[d] = dict(o=float(row[1]),h=float(row[2]),l=float(row[3]),c=float(row[4]),v=float(row[5]))
    return rows

print("=== DEV 1m resample vs raw_1d ===")
a = scan_1m_dev()
b = scan_1d()
print(f"1m dev days={len(a)} 1d dev days={len(b)}")
common = sorted(set(a) & set(b))
missing_1d = sorted(set(a) - set(b))
missing_1m = sorted(set(b) - set(a))
print(f"common_days={len(common)} missing_in_1d={len(missing_1d)} missing_in_1m={len(missing_1m)}")

mism = dict(o=0,h=0,l=0,c=0,v=0)
worst = []
rel_v = []
for d in common:
    x = a[d]; y = b[d]
    for k in ("o","h","l","c"):
        if abs(x[k]-y[k]) > 1e-9: mism[k] += 1
    if x["v"] != y["v"]:
        mism["v"] += 1
        if y["v"] > 0: rel_v.append(abs(x["v"]-y["v"])/y["v"])
    if any(abs(x[k]-y[k])>1e-9 for k in ("o","h","l","c")) or x["v"] != y["v"]:
        worst.append((datetime.fromtimestamp(d*86400,timezone.utc).strftime("%Y-%m-%d"), x["v"], y["v"],
                      x["o"],y["o"],x["h"],y["h"],x["l"],y["l"],x["c"],y["c"]))
print(f"OHLC mismatches: o={mism['o']} h={mism['h']} l={mism['l']} c={mism['c']}")
print(f"Volume mismatches: {mism['v']}")
if rel_v:
    print(f"Volume rel-diff max={max(rel_v):.6f} median={sorted(rel_v)[len(rel_v)//2]:.6f}")
with open(OUT/"resample_1d.csv","w",newline="") as fh:
    w = csv.writer(fh); w.writerow(["day","v_1m","v_1d","o_1m","o_1d","h_1m","h_1d","l_1m","l_1d","c_1m","c_1d"])
    for r in worst[:50]: w.writerow(r)
with open(OUT/"resample_summary.txt","w") as fh:
    fh.write(f"common_days {len(common)}\n")
    fh.write(f"mismatch_o {mism['o']}\nmismatch_h {mism['h']}\nmismatch_l {mism['l']}\nmismatch_c {mism['c']}\nmismatch_v {mism['v']}\n")
    if rel_v: fh.write(f"v_rel_max {max(rel_v):.6f}\n")

# === Footprint volume vs kline volume, 2024-12-02..2025-03-31 ===
print("\n=== footprint vs kline volume (Dec24-Mar25) ===")
from datetime import date
start_d = date(2024,12,2); end_d = date(2025,3,31)
fp_dir = F/"orderflow_1m"
kline_dir = F/"tom_raw/klines"
# load kline vol per minute for the window
kvol = {}
for f in sorted(kline_dir.glob("*.csv")):
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if not row or not row[0].lstrip("-").isdigit(): continue
            try: t = to_ms(int(row[0]))
            except: continue
            d = datetime.fromtimestamp(t/1000, timezone.utc).date()
            if d < start_d or d > end_d: continue
            v = float(row[5])
            kvol[t] = v
print(f"kline minutes in window: {len(kvol)}")

# footprint files in window
fp_files = sorted(fp_dir.glob("*.csv.gz"))
in_window = [p for p in fp_files if start_d <= datetime.strptime(p.stem.replace(".csv",""), "%Y-%m-%d").date() <= end_d]
print(f"footprint files in window: {len(in_window)} of {len(fp_files)}")
if in_window:
    # header of one file
    with gzip.open(in_window[0], "rt", encoding="utf-8") as fh:
        head = [next(fh) for _ in range(3)]
    print("--- footprint header ---")
    for h in head: print(repr(h[:200]))
