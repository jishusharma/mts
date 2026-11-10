import csv, gzip, sys
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode = True
ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629")
OUT = ROOT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)

def f_utc(ms):
    if ms is None: return ""
    if ms > 10**14: return "unit>ms:" + str(ms)
    return datetime.fromtimestamp(ms/1000, timezone.utc).isoformat()

def scan(name, dirp, step):
    dirp = Path(dirp)
    if not dirp.exists(): return {"name": name, "dir": str(dirp), "status": "MISSING"}
    files = sorted(dirp.glob("*.csv")) or sorted(dirp.glob("*.csv.gz"))
    rows = 0; uniq = set(); dup = 0; first = None; last = None; units = set()
    for f in files:
        op = gzip.open if f.suffix == ".gz" else open
        with op(f, "rt", encoding="utf-8") as fh:
            rdr = csv.reader(fh)
            for row in rdr:
                if not row: continue
                try: t = int(row[0])
                except ValueError: continue
                rows += 1
                if t in uniq: dup += 1
                else: uniq.add(t)
                if first is None or t < first: first = t
                if last is None or t > last: last = t
                units.add(len(row[0]))
    us = sorted(uniq)
    gaps = 0; ex = []
    for i in range(1, len(us)):
        d = us[i] - us[i-1]
        if d != step:
            gaps += 1
            if len(ex) < 3: ex.append((us[i-1], us[i], d))
    return {"name": name, "dir": str(dirp), "status": "OK", "nfiles": len(files),
            "rows": rows, "uniques": len(uniq), "dup": dup, "first": first, "last": last,
            "units": sorted(units), "gaps": gaps, "gap_examples": ex}

def show(s):
    print(s["name"], "status=" + s["status"],
          "files=" + str(s.get("nfiles","")),
          "rows=" + str(s.get("rows","")),
          "uniq=" + str(s.get("uniques","")),
          "dup=" + str(s.get("dup","")),
          "gaps=" + str(s.get("gaps","")),
          "first=" + f_utc(s.get("first")),
          "last=" + f_utc(s.get("last")),
          "digits=" + str(s.get("units",[])))

rows = []
rows.append(scan("tom_raw_1m",  r"F:/MTS/data/tom_raw/klines", 60000))
rows.append(scan("raw_1m_2022", r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1m_2022/klines", 60000))
rows.append(scan("raw_1d",      r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1d/klines", 86400000))
rows.append(scan("raw_1h",      r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1h/klines", 3600000))
rows.append(scan("raw_15m",     r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_15m/klines", 900000))
rows.append(scan("raw_5m",      r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_5m/klines", 300000))
rows.append(scan("funding",     r"C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_fund/fundingRate", 28800000))
for s in rows: show(s)
with (OUT / "data_inventory.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name","dir","nfiles","rows","uniques","duplicates","first_utc","last_utc","digits","gaps","status"])
    for s in rows:
        w.writerow([s.get("name"), s.get("dir"), s.get("nfiles",""), s.get("rows",""),
                    s.get("uniques",""), s.get("dup",""), f_utc(s.get("first")), f_utc(s.get("last")),
                    ",".join(map(str,s.get("units",[]))), s.get("gaps",""), s.get("status")])
print("WROTE", OUT / "data_inventory.csv")
