import sys, tempfile, traceback
from pathlib import Path
sys.dont_write_bytecode = True
WT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1016-0629")
sys.path.insert(0, str(WT / "MyTradingSys/backtest"))
sys.path.insert(0, str(WT / "MyTradingSys/backtest/bt"))

TMP = Path(tempfile.mkdtemp(prefix="dsa_audit_T01b_"))
KL = TMP / "klines"; KL.mkdir()
H = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
def r(t,o,h,l,c,v,cnt=10,tbv=7): return f"{t},{o},{h},{l},{c},{v},{t+59999},0,{cnt},{tbv},0,0\n"
(KL/"a.csv").write_text(H + r(1640995200000000, 100,101,99,100,10) + r(1640995260000, 200,201,199,200,10) + r(1640995260000, 300,301,299,300,10) + r(1640995320000, 400,401,399,400,10) + r(1640995380000, 500,501,499,500,10))
print("TMP:", TMP)
print()

def try_call(label, fn):
    try:
        out = fn()
        print(f"[{label}] OK -> {out if not hasattr(out,'__len__') else 'len=' + str(len(out))}")
        return out
    except Exception as e:
        print(f"[{label}] RAISE {type(e).__name__}: {e}")
        return None

# fires_kline._read_csv
try:
    import bigtrade.fires_kline as fk
    print("== fires_kline._read_csv ==")
    p = str(KL/"a.csv")
    out = try_call("fires_kline._read_csv", lambda: fk._read_csv(p))
    if out is not None:
        print("  first 3:", out[:3] if hasattr(out,'__getitem__') else out)
except Exception as e:
    print("import fires_kline RAISE", e)
print()

# bigtrade.bigmoves.load_1m — takes sources
try:
    import bigtrade.bigmoves as bm
    print("== bigmoves.load_1m (source=tmp) ==")
    out = try_call("bigmoves.load_1m", lambda: bm.load_1m(sources=[(str(TMP), "klines")]))
    if out is not None:
        try: print("  n:", len(out), "first:", out[:2])
        except Exception: pass
except Exception as e:
    print("import bigmoves RAISE", e)
print()

# tom_bt.load_bars_1m
try:
    sys.path.insert(0, str(WT / "MyTradingSys/backtest"))
    import tom_bt
    print("== tom_bt.load_bars_1m ==")
    out = try_call("tom_bt.load_bars_1m", lambda: tom_bt.load_bars_1m(str(KL)))
    if out is not None:
        try: print("  n:", len(out), "first:", out[:2])
        except Exception: pass
except Exception as e:
    print("import tom_bt RAISE", e)
print()

# timeframe tf_realdata_gate.load_klines_csv
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("tfg", str(WT / "MyTradingSys/backtest/layers/timeframe/tf_realdata_gate.py"))
    tfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(tfg)
    print("== tf_realdata_gate.load_klines_csv ==")
    out = try_call("tf.load_klines_csv", lambda: tfg.load_klines_csv(str(KL/"a.csv")))
    if out is not None:
        try: print("  n:", len(out), "first:", out[:2])
        except Exception: pass
except Exception as e:
    print("import tf RAISE", e)
print()

# vp_pivot_probe._read_csv
try:
    sys.path.insert(0, str(WT / "MyTradingSys/backtest"))
    import vp_pivot_probe as vp
    print("== vp_pivot_probe._read_csv ==")
    out = try_call("vp._read_csv", lambda: vp._read_csv(str(KL/"a.csv")))
    if out is not None:
        try: print("  shape:", out.shape, "first:", out[:2])
        except Exception: pass
except Exception as e:
    print("import vp RAISE", e)
