import sys
sys.dont_write_bytecode = True
import csv, tempfile, os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1019-0713")
OUT = ROOT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "MyTradingSys"))
TMP = Path(tempfile.mkdtemp(prefix="dsa_t01_"))
KL_DIR = TMP / "klines"; KL_DIR.mkdir()
FUND_DIR = TMP / "fundingRate"; FUND_DIR.mkdir()

# Base clean file: 5 minutes, 2022-01-01 00:00..00:04 UTC, Binance kline CSV column layout
# [open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote,ignore]
T0 = 1640995200000
rows = []
for m in range(5):
    t = T0 + m*60000
    close_t = t + 59999
    rows.append([str(t), "100.0", "101.0", "99.0", "100.5", "10.0", str(close_t), "1005.0", "10", "5.0", "502.5", "0"])
with open(KL_DIR/"clean.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in rows: w.writerow(r)

# (a) microsecond stamps
with open(KL_DIR/"micro.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in rows:
        r2 = list(r); r2[0] = str(int(r[0])*1000); w.writerow(r2)

# (b) duplicate row
with open(KL_DIR/"dup.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in rows: w.writerow(r)
    w.writerow(rows[1])

# (c) missing minute
with open(KL_DIR/"gap.csv","w",newline="") as f:
    w = csv.writer(f)
    for i,r in enumerate(rows):
        if i == 2: continue
        w.writerow(r)

# (d) header row
with open(KL_DIR/"header.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["open_time","open","high","low","close","volume","close_time","quote_volume","count","taker_buy_volume","taker_buy_quote","ignore"])
    for r in rows: w.writerow(r)

# (e) unsorted pair
with open(KL_DIR/"unsorted.csv","w",newline="") as f:
    w = csv.writer(f)
    swapped = [rows[0], rows[2], rows[1], rows[3], rows[4]]
    for r in swapped: w.writerow(r)

# funding variants
# Binance fundingRate CSV: calc_time,funding_interval_hours,last_funding_rate
frows = [[str(T0 + k*8*3600*1000), "8", "0.0001"] for k in range(3)]
with open(FUND_DIR/"clean.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in frows: w.writerow(r)
with open(FUND_DIR/"micro.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in frows:
        r2 = list(r); r2[0] = str(int(r[0])*1000); w.writerow(r2)
with open(FUND_DIR/"dup.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in frows: w.writerow(r)
    w.writerow(frows[1])
with open(FUND_DIR/"gap.csv","w",newline="") as f:
    w = csv.writer(f)
    for i,r in enumerate(frows):
        if i == 1: continue
        w.writerow(r)
with open(FUND_DIR/"header.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["calc_time","funding_interval_hours","last_funding_rate"])
    for r in frows: w.writerow(r)
with open(FUND_DIR/"unsorted.csv","w",newline="") as f:
    w = csv.writer(f)
    for r in [frows[0], frows[2], frows[1]]: w.writerow(r)

sys.path.insert(0, str(ROOT / "MyTradingSys/backtest/bt"))
sys.path.insert(0, str(ROOT / "MyTradingSys/backtest"))
from bt.bt_data import load_klines as bt_load_klines, load_funding as bt_load_funding
sys.path.insert(0, str(ROOT / "MyTradingSys/backtest/bigtrade"))
from bigtrade.bigmoves import load_1m as bm_load_1m

def describe(label, fn):
    try:
        r = fn()
        return (label, "return", str(type(r).__name__), str(len(r) if hasattr(r,'__len__') else r))
    except Exception as e:
        return (label, "raise", type(e).__name__, str(e)[:120])

BT_KL = ["clean.csv","micro.csv","dup.csv","gap.csv","header.csv","unsorted.csv"]
BT_FD = ["clean.csv","micro.csv","dup.csv","gap.csv","header.csv","unsorted.csv"]

results = []
for name in BT_KL:
    results.append(describe(f"bt_data.load_klines[{name}]", lambda n=name: bt_load_klines(TMP, dataset="klines") if n=="clean.csv" else _load_single(TMP, n)))

def _load_single(tmp, filename):
    # load_klines takes a root+dataset, so we swap dataset per file by copying into per-file subdirs
    sub = tmp / ("k_" + filename.replace(".","_"))
    if sub.exists():
        return bt_load_klines(sub, dataset="klines")
    sub.mkdir()
    (sub/"klines").mkdir()
    import shutil
    shutil.copyfile(tmp/"klines"/filename, sub/"klines"/filename)
    return bt_load_klines(sub, dataset="klines")

results = []
for name in BT_KL:
    try:
        r = _load_single(TMP, name)
        results.append((f"bt_data.load_klines[{name}]", "return", "list", len(r)))
    except Exception as e:
        results.append((f"bt_data.load_klines[{name}]", "raise", type(e).__name__, str(e)[:120]))

def _load_fund_single(tmp, filename):
    sub = tmp / ("f_" + filename.replace(".","_"))
    if sub.exists():
        return bt_load_funding(sub)
    sub.mkdir()
    (sub/"fundingRate").mkdir()
    import shutil
    shutil.copyfile(tmp/"fundingRate"/filename, sub/"fundingRate"/filename)
    return bt_load_funding(sub)

for name in BT_FD:
    try:
        r = _load_fund_single(TMP, name)
        results.append((f"bt_data.load_funding[{name}]", "return", "list", len(r)))
    except Exception as e:
        results.append((f"bt_data.load_funding[{name}]", "raise", type(e).__name__, str(e)[:120]))

# bigmoves.load_1m: only merge path
# Its load_klines (from bt) does the per-file scan. Its own guard rejects us vs ms.
for name in BT_KL:
    sub = TMP / ("bm_" + name.replace(".","_"))
    sub.mkdir(exist_ok=True)
    (sub/"klines").mkdir(exist_ok=True)
    import shutil
    shutil.copyfile(TMP/"klines"/name, sub/"klines"/name)
    try:
        r, rep = bm_load_1m(sources=[(sub, "klines")])
        results.append((f"bigmoves.load_1m[{name}]", "return", "list+report", f"bars={len(r)}"))
    except Exception as e:
        results.append((f"bigmoves.load_1m[{name}]", "raise", type(e).__name__, str(e)[:120]))

with open(OUT/"torture_matrix.csv","w",newline="",encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["loader_input","outcome","exception_or_type","detail"])
    for r in results: w.writerow(r)
    for r in results: print(r)
print(f"\nTMP={TMP}")
print(f"wrote {OUT/'torture_matrix.csv'}")
