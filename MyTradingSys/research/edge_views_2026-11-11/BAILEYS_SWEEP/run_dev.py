import sys
sys.dont_write_bytecode = True
import glob
import os
import datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "MyTradingSys", "backtest"))
import baileys_sweep as B
import trade_sanity as TS


def ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


START, END = ms("2022-02-01 00:00"), ms("2024-05-31 23:59")
LOAD_END = ms("2024-06-08 00:00")  # exit runoff only; VALIDATION (2024-07-01 on) untouched
files = [f for f in sorted(glob.glob("F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv")) if f[-11:-4] <= "2024-06"]
kl = TS.load_klines(files)
ks = sorted(k for k in kl if k < LOAD_END)
t = np.array(ks, dtype=np.int64)
a = np.array([kl[k] for k in ks])
b15 = B.resample(t, a[:, 0], a[:, 1], a[:, 2], a[:, 3], B.M15)
h1 = B.resample(t, a[:, 0], a[:, 1], a[:, 2], a[:, 3], B.H1)
d1 = B.resample(t, a[:, 0], a[:, 1], a[:, 2], a[:, 3], B.D1)
print("1m rows", len(t), "15m", len(b15["t"]), "1h", len(h1["t"]), "1d", len(d1["t"]))
tr = B.run(b15, h1, d1, START, END)
# sanity: entry fills vs 1m klines; the exit is a stop/target price, so it is checked against its 15m bar range instead
chk = [dict(x, exit_ms=x["entry_ms"], exit_px=x["entry_px"]) for x in tr]
TS.log_sanity(chk, kl, n=5)
bad = sum(1 for x in tr if not (b15["l"][x["exit_i"]] - 1e-9 <= x["exit_px"] <= b15["h"][x["exit_i"]] + 1e-9))
print("exit price outside its 15m bar range: %d of %d" % (bad, len(tr)))
r = np.array([x["ret"] for x in tr])
n = len(r)
mid = (START + END) // 2
h1r = np.array([x["ret"] for x in tr if x["entry_ms"] < mid])
h2r = np.array([x["ret"] for x in tr if x["entry_ms"] >= mid])


def tstat(v):
    return v.mean() / (v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 and v.std(ddof=1) > 0 else float("nan")


cum = np.cumsum(r)
dd = float((np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max()) if n else 0.0
out = []
out.append("n %d, win rate %.1f %%, mean net R %.4f, mean net bp %.1f, t %.2f, max drawdown %.2f R (sum of R, peak to trough)" % (
    n, 100 * (r > 0).mean(), r.mean(), np.mean([x["net_bp"] for x in tr]), tstat(r), dd))
out.append("gross mean R %.4f; exits: " % np.mean([x["gross_r"] for x in tr])
           + ", ".join("%s %d" % (k, sum(x["kind"] == k for x in tr)) for k in ("stop", "tp", "cap")))
out.append("median risk %.3f %% of price" % (100 * np.median([x["r_pct"] for x in tr])))
out.append("half 1 (before %s): n %d mean %.4f | half 2: n %d mean %.4f" % (
    dt.datetime.fromtimestamp(mid / 1000, dt.timezone.utc).strftime("%Y-%m-%d"), len(h1r), h1r.mean(), len(h2r), h2r.mean()))
out += TS.year_side_lines(tr)
pm = B.placebo(b15, tr, START, END)
out.append("placebo (500 draws, seed 1): mean net R %.4f, sd %.4f, share of draws >= real mean %.3f" % (
    pm.mean(), pm.std(), (pm >= r.mean()).mean()))
dec = "PASS" if (r.mean() > 0 and tstat(r) >= 2 and h1r.mean() > 0 and h2r.mean() > 0) else ("FAIL" if r.mean() <= 0 else "INCONCLUSIVE")
if n < 30 and dec == "PASS":
    dec = "INCONCLUSIVE"
out.append("VERDICT_MECH: " + dec)
print("\n".join(out))
open(os.path.join(HERE, "dev_output.txt"), "w").write("\n".join(out) + "\n")
