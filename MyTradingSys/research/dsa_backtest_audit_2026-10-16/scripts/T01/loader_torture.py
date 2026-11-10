import sys, os, tempfile, importlib.util
from pathlib import Path
sys.dont_write_bytecode = True

WT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629")
sys.path.insert(0, str(WT / "MyTradingSys/backtest/bt"))
import bt_data as d

TMP = Path(tempfile.mkdtemp(prefix="dsa_audit_T01_"))
KL = TMP / "klines"; KL.mkdir()

H = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
def r(t,o,h,l,c,v,cnt=10,tbv=7,qv=0.0): return f"{t},{o},{h},{l},{c},{v},{t+59999},{qv},{cnt},{tbv},0,0\n"

# case a: microsecond-stamped row (13 -> 16 digits)
(KL/"a.csv").write_text(H + r(1640995200000000, 100,101,99,100,10))
# case b: duplicate row (same t twice, different price)
(KL/"b.csv").write_text(H + r(1640995260000, 200,201,199,200,10) + r(1640995260000, 300,301,299,300,10))
# case c: missing minute between two rows
(KL/"c.csv").write_text(H + r(0,1,2,0,1,10) + r(120000,3,4,2,3,10))
# case d: header-only file
(KL/"d.csv").write_text(H)
# case e: unsorted pair
(KL/"e.csv").write_text(H + r(240000,5,6,4,5,10) + r(60000,2,3,1,2,10))

try:
    bars = d.load_klines(TMP)
    print("CALL: load_klines(TMP) -> OK")
    print("n_bars:", len(bars))
    for b in bars[:6]:
        print("  bar:", b)
except Exception as e:
    print("CALL: load_klines -> RAISE", type(e).__name__, e)

print()
print("== gap check on result ==")
try:
    gaps = d.check_gaps(bars)
    print("gaps:", gaps)
except Exception as e:
    print("gap check RAISE", e)

print()
print("== headerless file (no header row) ==")
KL2 = TMP / "klines2"; KL2.mkdir()
(KL2/"h.csv").write_text(r(0,1,2,0,1,10) + r(60000,2,3,1,2,10))
try:
    bars2 = d.load_klines(TMP, dataset="klines2")
    print("headerless: n=", len(bars2), bars2)
except Exception as e:
    print("headerless RAISE", e)

print()
print("== funding torture ==")
F = TMP / "fundingRate"; F.mkdir()
(F/"x.csv").write_text("calc_time,funding_interval_hours,last_funding_rate\n1000,8,0.0001\n2000,8,0.0002\n")
try:
    fr = d.load_funding(TMP)
    print("funding n=", len(fr), fr)
    print("funding_rate_at(500):", d.funding_rate_at(fr, 500))
    print("funding_rate_at(1500):", d.funding_rate_at(fr, 1500))
    print("funding_rate_at(99999):", d.funding_rate_at(fr, 99999))
except Exception as e:
    print("funding RAISE", e)

print()
print("TMP used:", TMP)
