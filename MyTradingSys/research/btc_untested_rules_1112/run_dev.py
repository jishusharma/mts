import sys
sys.dont_write_bytecode = True
import datetime as dt
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules as R
import trade_sanity as TS


def ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


START, END = ms("2022-02-01 00:00"), ms("2024-05-31 23:59")
mid = (START + END) // 2
b = R.load()
assert b["t"][-1] < ms("2024-06-01 00:00"), "VALIDATION must not be loaded"
print("15m bars", len(b["t"]), "first", b["t"][0], "last", b["t"][-1], "gaps", int((np.diff(b["t"]) != R.M15).sum()))
di = R.day_info(b)
wi = R.week_info(b)
kfiles = [f for f in sorted(glob.glob("F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv")) if f[-11:-4] <= "2024-06"]
kl = TS.load_klines(kfiles) if kfiles else {}
print("days", len(di), "weeks", len(wi), "1m kline files", len(kfiles))


def tstat(x):
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 and x.std(ddof=1) > 0 else float("nan")


def share(x):
    return "n %d, share %.3f" % (len(x), np.mean(x)) if len(x) else "n 0"


TOL = 0.002  # percent: the reduced 15m open is the first aggtrade, the 1m kline open can differ by a tick (about 0.1 USD)


def sanity(tr, exit_leg=None):
    if not kl or not tr:
        return
    if exit_leg == "close":   # A: exit at the close of its 15m bar = 1m close of the last minute
        chk = [dict(x, exit_ms=x["exit_ms"] + 14 * 60_000) for x in tr]
        TS.log_sanity(chk, kl, n=5, entry_leg="open", exit_leg="close", tol_pct=TOL)
    else:
        TS.log_sanity([dict(x, exit_ms=x["entry_ms"], exit_px=x["entry_px"]) for x in tr], kl, n=5, tol_pct=TOL)


def report(name, tr, pm, desc):
    r = np.array([x["ret"] for x in tr])
    n = len(r)
    out = ["## " + name]
    if n == 0:
        return out + ["n 0", "VERDICT_MECH: FAIL"] + desc
    h1 = np.array([x["ret"] for x in tr if x["entry_ms"] < mid])
    h2 = np.array([x["ret"] for x in tr if x["entry_ms"] >= mid])
    cum = np.cumsum(r)
    dd = float((np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max())
    out.append("n %d, win rate %.1f %%, mean net bp %.2f, t %.2f, max drawdown %.1f bp (sum, peak to trough)" % (n, 100 * (r > 0).mean(), r.mean(), tstat(r), dd))
    out += desc
    out.append("half 1 (before 2023-04-02): n %d mean %.2f | half 2: n %d mean %.2f" % (len(h1), h1.mean() if len(h1) else float("nan"), len(h2), h2.mean() if len(h2) else float("nan")))
    out += TS.year_side_lines(tr)
    out.append("placebo (500 draws, seed 1): mean net bp %.2f, sd %.2f, share of draws >= real mean %.3f" % (pm.mean(), pm.std(), (pm >= r.mean()).mean()))
    ok = r.mean() > 0 and tstat(r) >= 2 and len(h1) and len(h2) and h1.mean() > 0 and h2.mean() > 0
    dec = "PASS" if ok else ("FAIL" if r.mean() <= 0 else "INCONCLUSIVE")
    if n < 30 and dec != "FAIL":
        dec = "INCONCLUSIVE"
    return out + ["VERDICT_MECH: " + dec]


out = []
ta, acc, non = R.run_a(b, di, START, END)
sanity(ta, "close")
out += report("A acceptance then edge retest (BB3c8visnkI R4)", ta, R.placebo(b, ta, START, END, "hold"),
              ["hold share accepted events: %s; non-accepted events: %s" % (share(acc), share(non))])
tb, rev = R.run_b(b, di, START, END)
sanity(tb)
out += report("B return to liquidity, fade to prior POC (BB3c8visnkI R5)", tb, R.placebo(b, tb, START, END, "stop"),
              ["revisit share within 24 bars: %s; exits: %s" % (share(rev), ", ".join("%s %d" % (k, sum(x["kind"] == k for x in tb)) for k in ("stop", "tp", "cap")))])
tc, thin_t, oth_t = R.run_c(b, di, START, END)
sanity(tc)
out += report("C thin close pulls to POC (YkclL6xgu-s R5)", tc, R.placebo(b, tc, START, END, "stop"),
              ["touch share next day, THIN days: %s; other days: %s; exits: %s" % (share(thin_t), share(oth_t), ", ".join("%s %d" % (k, sum(x["kind"] == k for x in tc)) for k in ("stop", "tp", "cap")))])
td, tou, mir, mfe = R.run_d(b, wi, START, END)
out += report("D naked weekly POC (ODdF0Bn_KSc R6)", td, R.placebo(b, td, START, END, "hold"),
              ["touch rate within 4 weeks: %s; mirror-level touch rate: %s; median MFE over 96 bars %.1f bp (descriptive); log sanity skipped: fill is a limit at the POC, not a bar open" % (share(tou), share(mir), np.median(mfe) if mfe else float("nan"))])
print("\n".join(out))
open(os.path.join(HERE, "dev_output.txt"), "w").write("\n".join(out) + "\n")
