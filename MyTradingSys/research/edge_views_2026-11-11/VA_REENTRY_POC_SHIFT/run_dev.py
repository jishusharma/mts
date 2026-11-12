import sys
sys.dont_write_bytecode = True
import glob
import os
import csv
import datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "MyTradingSys", "backtest"))
import va_poc as V
import trade_sanity as TS


def ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


START, END = ms("2022-02-01 00:00"), ms("2024-05-31 23:59")
LOAD_END = ms("2024-06-08 00:00")  # exit runoff only; VALIDATION (2024-07-01 on) untouched
files = [f for f in sorted(glob.glob("F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv")) if f[-11:-4] <= "2024-06"]
rows = {}
for p in files:
    with open(p, newline="", encoding="utf-8") as fh:
        for r in csv.reader(fh):
            if not r or not r[0][:1].isdigit():
                continue
            t = int(float(r[0]))
            if t > 1e14:
                t //= 1000
            if t < LOAD_END:
                rows[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]))
ks = sorted(rows)
t = np.array(ks, dtype=np.int64)
a = np.array([rows[k] for k in ks])
o, h, l, c, v = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
kl = TS.load_klines(files)
prof = V.day_profiles(t, h, l, c, v)
lev = V.levels_for_days(prof)
b15 = V.resample15(t, o, h, l, c)
days, ms0, px0 = V.day_table(t, o)
print("1m rows", len(t), "15m", len(b15["t"]), "days", len(days), "profiles", len(prof))
mid = (START + END) // 2


def tstat(x):
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) > 0 else float("nan")


def report(name, tr, pm, unit, extra=None):
    r = np.array([x["ret"] for x in tr])
    n = len(r)
    h1 = np.array([x["ret"] for x in tr if x["entry_ms"] < mid])
    h2 = np.array([x["ret"] for x in tr if x["entry_ms"] >= mid])
    cum = np.cumsum(r)
    dd = float((np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max()) if n else 0.0
    out = ["## " + name]
    out.append("n %d, win rate %.1f %%, mean net %s %.4f, t %.2f, max drawdown %.2f %s (sum, peak to trough)" % (
        n, 100 * (r > 0).mean(), unit, r.mean(), tstat(r), dd, unit))
    if extra:
        out.append(extra)
    out.append("half 1 (before %s): n %d mean %.4f | half 2: n %d mean %.4f" % (
        dt.datetime.fromtimestamp(mid / 1000, dt.timezone.utc).strftime("%Y-%m-%d"), len(h1), h1.mean() if len(h1) else float("nan"),
        len(h2), h2.mean() if len(h2) else float("nan")))
    out += TS.year_side_lines(tr)
    out.append("placebo (500 draws, seed 1): mean net %s %.4f, sd %.4f, share of draws >= real mean %.3f" % (
        unit, pm.mean(), pm.std(), (pm >= r.mean()).mean()))
    ok = n and r.mean() > 0 and tstat(r) >= 2 and len(h1) and len(h2) and h1.mean() > 0 and h2.mean() > 0
    dec = "PASS" if ok else ("FAIL" if (n == 0 or r.mean() <= 0) else "INCONCLUSIVE")
    if n < 30:
        dec = "INCONCLUSIVE" if n else "FAIL"
    out.append("VERDICT_MECH: " + dec)
    return out


out = []
# ---- R1
tr1 = V.run_r1(b15, lev, START, END)
chk = [dict(x, exit_ms=x["entry_ms"], exit_px=x["entry_px"]) for x in tr1]
TS.log_sanity(chk, kl, n=5)
bad = sum(1 for x in tr1 if not (b15["l"][x["exit_i"]] - 1e-9 <= x["exit_px"] <= b15["h"][x["exit_i"]] + 1e-9))
print("R1 exit price outside its 15m bar range: %d of %d" % (bad, len(tr1)))
ex = "gross mean R %.4f; exits: %s; median risk %.3f %% of price, median target distance %.3f %%" % (
    np.mean([x["gross_r"] for x in tr1]), ", ".join("%s %d" % (k, sum(x["kind"] == k for x in tr1)) for k in ("stop", "tp", "cap")),
    100 * np.median([x["r_pct"] for x in tr1]), 100 * np.median([x["tp_pct"] for x in tr1]))
out += report("R1 value-area re-entry (net R)", tr1, V.placebo_r1(b15, tr1, START, END), "R", ex)
# ---- R2
for hz in (1, 3):
    tr2 = V.run_r2(prof, days, ms0, px0, hz, START, END)
    TS.log_sanity(tr2, kl, n=5)
    out += report("R2 two POC shifts, horizon %d day(s) (net bp)" % hz, tr2, V.placebo_r2(days, ms0, px0, tr2, hz, START, END), "bp")
print("\n".join(out))
open(os.path.join(HERE, "dev_output.txt"), "w").write("\n".join(out) + "\n")
