import gzip, sys, csv, json
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode = True

def f_utc(ms):
    if ms is None: return ""
    return datetime.fromtimestamp(ms/1000, timezone.utc).isoformat()

def scan_gz_daily(name, dirp):
    dirp = Path(dirp)
    if not dirp.exists():
        print(name, "MISSING", dirp); return
    files = sorted(p for p in dirp.iterdir() if p.name.endswith(".csv.gz"))
    first=None; last=None; rows=0; bad_header=0
    for f in files:
        try:
            with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
                rdr = csv.reader(fh)
                fr = next(rdr, None)
                if fr and not fr[0].isdigit(): bad_header += 1
                elif fr:
                    try: t=int(fr[0]); rows+=1
                    except: pass
                for r in rdr:
                    if not r: continue
                    try: t=int(r[0]); rows+=1
                    except: pass
        except Exception as e:
            print("ERR", f.name, e)
    print(f"{name}: files={len(files)} rows={rows}")

def scan_jsonlgz(name, dirp):
    dirp = Path(dirp)
    if not dirp.exists():
        print(name, "MISSING", dirp); return
    files = sorted(p for p in dirp.iterdir() if p.name.endswith(".jsonl.gz"))
    first_ts=None; last_ts=None; total=0
    for f in files:
        try:
            with gzip.open(f, "rt", encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip(): continue
                    total += 1
                    if total <= 1 or total % 100000 == 0:
                        try:
                            d = json.loads(line)
                            ts = d.get("timestamp_utc")
                            if ts:
                                if first_ts is None: first_ts = ts
                                last_ts = ts
                        except: pass
        except Exception as e:
            print("ERR", f.name, e)
    print(f"{name}: files={len(files)} rows_scanned={total} first={first_ts} last={last_ts}")

def scan_dir(name, dirp, pattern="*", sample=3):
    dirp = Path(dirp)
    if not dirp.exists():
        print(name, "MISSING", dirp); return
    files = sorted(dirp.glob(pattern))
    print(f"{name}: dir={dirp} files={len(files)}")
    for p in files[:sample] + files[-sample:]:
        print("   ", p.name, p.stat().st_size)

print("== orderflow_1m gz ==")
scan_gz_daily("orderflow_1m", r"F:/MTS/data/orderflow_1m")
print()
print("== orderflow _qhist ==")
scan_dir("orderflow_qhist", r"F:/MTS/data/orderflow_1m/_qhist", "*.json")
print()
print("== tom_snapshots ==")
scan_jsonlgz("tom_snapshots", r"F:/MTS/data/tom_snapshots")
print()
print("== metrics (OI) ==")
scan_dir("metrics_oi", r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw/metrics", "*.csv")
print()
print("== dax_raw ==")
scan_dir("dax_raw", r"F:/MTS/data/dax_raw")
print()
print("== candles ==")
scan_dir("candles", r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/candles")
