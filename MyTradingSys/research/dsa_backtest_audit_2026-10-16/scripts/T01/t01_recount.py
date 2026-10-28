import sys
sys.dont_write_bytecode = True
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1019-0713")
OUT = ROOT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "MyTradingSys/backtest"))
sys.path.insert(0, str(ROOT / "MyTradingSys/backtest/bt"))
from bt.bt_data import load_klines

F = Path(r"F:/MTS/data")
LIVE = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
DEV_END = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)
DEV_START = int(datetime(2022,1,1,tzinfo=timezone.utc).timestamp()*1000)

bars = load_klines(F/"tom_raw", dataset="klines", start_ms=DEV_START, end_ms=DEV_END)
print(f"loader.tom_raw.DEV: {len(bars)}")
if bars:
    print(f"  first_ms={bars[0]['t']} last_ms={bars[-1]['t']}")

bars2 = load_klines(LIVE/"Dumps/backtest/raw_1m_2022", dataset="klines", start_ms=DEV_START, end_ms=DEV_END)
print(f"loader.raw_1m_2022.DEV: {len(bars2)}")

print("EXPECTED from direct file scan: 1313280")
print(f"MATCH: {len(bars) == 1313280}")

with open(OUT/"recount.txt","w") as fh:
    fh.write(f"loader.tom_raw.DEV {len(bars)}\n")
    fh.write(f"loader.raw_1m_2022.DEV {len(bars2)}\n")
    fh.write("expected_direct_file_scan 1313280\n")
    fh.write(f"match {len(bars) == 1313280}\n")
print(f"wrote {OUT/'recount.txt'}")
