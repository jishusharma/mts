"""T03 part 2: independent rebuild of the published verdict statistics and exact-boundary tests of the pass bars.
Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T03/t03_stats.py
Reads only the committed DEV ledgers of the gross screen (ledger.csv) and mal_bb (ledger.csv): no bars, no VALIDATION/HOLDOUT.
The statistics here are pure Python (no numpy): mean, day-clustered SE sqrt(sum_d (sum_i in d (g-m))^2)/n, t=(mean-0.14)/SE,
MDE=2.8 SE, DIFF via the influence-function form of the dummy regression. Nothing is imported from the code under test
except in the boundary section, where the verdict functions are the object under test.
"""
import csv
import datetime as dt
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "MyTradingSys").is_dir())
RES = ROOT / "MyTradingSys" / "research"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE))
TS0 = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
MS, PER8 = 60_000, 8 * 3600 * 1000
C = 0.14
out = {}


def mean_se(g, day):
    n = len(g)
    m = sum(g) / n
    s = {}
    for x, d in zip(g, day):
        s[d] = s.get(d, 0.0) + (x - m)
    se0 = math.sqrt(sum(v * v for v in s.values())) / n
    G = len(s)
    se1 = se0 * math.sqrt(G / (G - 1) * (n - 1) / (n - 1)) if G > 1 else float("nan")      # CR1 with k=1 regressor: G/(G-1)*(n-1)/(n-1)
    return m, se0, se1, G


def diff_se(g, f, day):
    """T minus not-T. diff = mT - mN. Influence of obs i: F_i (g_i - mT)/nT - (1-F_i)(g_i - mN)/nN. SE = sqrt(sum_d (sum_i in d infl)^2)."""
    gt = [x for x, k in zip(g, f) if k]
    gn = [x for x, k in zip(g, f) if not k]
    mt, mn = sum(gt) / len(gt), sum(gn) / len(gn)
    s = {}
    for x, k, d in zip(g, f, day):
        s[d] = s.get(d, 0.0) + ((x - mt) / len(gt) if k else -(x - mn) / len(gn))
    return mt - mn, math.sqrt(sum(v * v for v in s.values()))


def maxdd(x):
    c = pk = dd = 0.0
    for v in x:
        c += v
        pk = max(pk, c)
        dd = max(dd, pk - c)
    return dd


def close(a, b, tol):
    return abs(a - b) <= tol


# ------------------------------------------------------------------ A. gross screen, T arm, primary cell d=1 h=60
rows = list(csv.DictReader(open(RES / "gross_effect_screen_2026-10-15" / "ledger.csv", newline="")))
ev = []
for r in rows:
    if r["dropped"] not in ("0", "", "0.0") or r["G_d1_h60"] in ("", "nan", "NaN"):
        continue
    idx = (int(r["t_open_time"]) - TS0) // MS
    e = idx + 1 + 1
    x = e + 60
    cross = ((TS0 + x * MS) // PER8) - ((TS0 + e * MS) // PER8)
    ev.append(dict(g=float(r["G_d1_h60"]) - 0.01 * cross, F=int(r["F"]), day=idx // 1440, t=idx))
ev.sort(key=lambda z: z["t"])
A = {}
for name, sel in (("T", lambda z: z["F"] == 1), ("notF", lambda z: z["F"] == 0), ("C", lambda z: True)):
    s = [z for z in ev if sel(z)]
    g = [z["g"] for z in s]
    m, se0, se1, G = mean_se(g, [z["day"] for z in s])
    A[name] = dict(n=len(g), mean=m, se=se0, se_cr1=se1, clusters=G, t_cost=(m - C) / se0, t_cost_cr1=(m - C) / se1, mdd=maxdd([x - C for x in g]), mde=2.8 * se0)
d, dse = diff_se([z["g"] for z in ev], [z["F"] for z in ev], [z["day"] for z in ev])
A["diff"], A["diff_se"], A["t_diff"] = d, dse, d / dse
pub = dict(T=dict(n=40, mean=-0.0568, se=0.1304, t_cost=-1.51, mdd=8.47), notF=dict(n=1399, mean=-0.0067, se=0.0253, t_cost=-5.79),
           C=dict(n=1439, mean=-0.0081, se=0.0246, t_cost=-6.03, mdd=214.21), diff=-0.0500, diff_se=0.1350, t_diff=-0.37, mde_T=0.3650)
chk = []
for arm in ("T", "notF", "C"):
    for k, v in pub[arm].items():
        got = A[arm][k]
        tol = {"n": 0, "mean": 6e-5, "se": 6e-5, "t_cost": 6e-3, "mdd": 6e-3}[k]
        chk.append((f"screen {arm} {k}", v, got, "MATCH" if close(v, got, tol) else "DIFFERENT"))
for k in ("diff", "diff_se", "t_diff"):
    chk.append((f"screen {k}", pub[k], A[k], "MATCH" if close(pub[k], A[k], {"diff": 6e-5, "diff_se": 6e-5, "t_diff": 6e-3}[k]) else "DIFFERENT"))
chk.append(("screen MDE T = 2.8 SE", pub["mde_T"], A["T"]["mde"], "MATCH" if close(pub["mde_T"], A["T"]["mde"], 6e-4) else "DIFFERENT"))
out["screen_T_rebuild"] = dict(mine=A, compared=chk)

# ------------------------------------------------------------------ B. mal_bb A1 from its ledger
rows = list(csv.DictReader(open(RES / "mal_bb_mid_engulf_2026-10-16" / "ledger.csv", newline="")))
g, day = [], []
for r in rows:
    idx5 = (int(r["engulf_bar_open_utc_ms"]) - TS0) // (5 * MS)
    e = (idx5 + 1) * 5 - 1 + 2                      # last 1m bar of the 5m bar, +1 +DELAY(1)
    g.append(float(r["G_short_h60"]))
    day.append(e // 1440)
m, se0, se1, G = mean_se(g, day)
B = dict(n=len(g), mean=m, se=se0, se_cr1=se1, clusters=G, net=m - C, t_net=(m - C) / se0, t_net_cr1=(m - C) / se1, mde=2.8 * se0)
pubB = dict(n=1179, mean=0.0124, se=0.0212, net=-0.1276, t_net=-6.02, mde=0.0593)
out["mal_bb_A1_rebuild"] = dict(mine=B, compared=[(k, v, B[k], "MATCH" if close(v, B[k], {"n": 0, "mean": 6e-5, "se": 6e-5, "net": 6e-5, "t_net": 6e-3, "mde": 6e-5}[k]) else "DIFFERENT") for k, v in pubB.items()]
                                                  + [("DIFF vs control", "0.0111 t 0.61", None, "BLOCKED-DATA: control events (n 2486) are not in any committed file; rebuilding them needs F:/MTS/data 1m bars")])

# ------------------------------------------------------------------ C. boundary tests (the verdict code is the object under test)
import numpy as np
from t03_canaries import load_src, RES as _RES
K = load_src("chart_common_stats", _RES / "chart_read_g5_2026-10-16/common.py")
S = K.S


def arm(n, mean, sd):
    z = np.array([1.0 if i % 2 == 0 else -1.0 for i in range(n)])
    if n % 2:
        z[-1] = 0.0
    return mean + sd * z


def run(g, gc, mdd_bh=1e9, n_min=200):
    d = np.arange(len(g))
    dc = np.arange(len(gc)) + 10 ** 6
    return K.verdict_arm(g, d, gc, dc, d, mdd_bh, n_min=n_min)


bt = []


def rec(name, expect, r):
    bt.append(dict(test=name, expect=expect, got=r["verdict"], n=r["n"], mean=r["mean"], t_net=r["t_net"], diff=r["diff"], t_diff=r["t_diff"], mdd=r["mdd"],
                   ok=(r["verdict"] == expect)))


gc = arm(300, 0.30, 0.3)
rec("base pass (n300, mean .40, t_net>>2, diff .10)", "PASS", run(arm(300, 0.40, 0.3), gc))
rec("n = 200 exactly", "PASS", run(arm(200, 0.40, 0.3), gc))
rec("n = 199", "INCONCLUSIVE", run(arm(199, 0.40, 0.3), gc))
# t_net exactly 2.0 in dyadic arithmetic: C_PCT patched to 0, n_min 4, g = [2,0,2,0], SE = sqrt(4)/4 = .5
Cold = K.C_PCT
K.C_PCT = 0.0
r = run(np.array([2.0, 0.0, 2.0, 0.0]), np.array([-2.0, -4.0, -2.0, -4.0]), n_min=4)
rec("t_net exactly 2.0 (C patched to 0; dyadic)", "PASS", r)
r = run(np.array([2.0 - 1e-9, -1e-9, 2.0 - 1e-9, -1e-9]), np.array([-2.0, -4.0, -2.0, -4.0]), n_min=4)
rec("t_net 2.0 minus 2e-9 (all values shifted -1e-9)", "FAIL", r)
K.C_PCT = Cold
# DIFF at +0.05 (decimal), +-1e-9
for dlt, exp in ((-1e-9, "FAIL"), (0.0, "PASS"), (1e-9, "PASS")):
    mc = 0.40 - (0.05 + dlt)
    rec(f"DIFF = 0.05 {dlt:+.0e} (mT .40, mC {mc:.10f})", exp, run(arm(300, 0.40, 0.05), arm(300, mc, 0.05)))
rec("DIFF = 0.5 - 0.45 (decimal 0.05, float 0.04999999999999999?)", "PASS", run(arm(300, 0.5, 0.05), arm(300, 0.45, 0.05)))
# t_diff bisection to the 2.0 boundary
lo, hi = 1e-6, 5.0
for _ in range(200):
    mid = (lo + hi) / 2
    rr = run(arm(300, 0.40, 0.05), arm(300, 0.30, mid))
    if rr["t_diff"] >= 2.0:
        lo = mid
    else:
        hi = mid
rl, rh = run(arm(300, 0.40, 0.05), arm(300, 0.30, lo)), run(arm(300, 0.40, 0.05), arm(300, 0.30, hi))
rec(f"t_diff just >= 2.0 ({rl['t_diff']!r})", "PASS", rl)
rec(f"t_diff just < 2.0 ({rh['t_diff']!r})", "FAIL", rh)
# MDD at the buy-and-hold value
base = run(arm(300, 0.40, 0.3), gc)
rec("MDD == BH MDD", "PASS", run(arm(300, 0.40, 0.3), gc, mdd_bh=base["mdd"]))
rec("MDD slightly above BH MDD", "FAIL", run(arm(300, 0.40, 0.3), gc, mdd_bh=base["mdd"] - 1e-9))
# screen.evaluate: n bar and verdict word
def cells_for(nT, nN, mT=0.40, mN=0.30, sd=0.3):
    g = np.concatenate((arm(nT, mT, sd), arm(nN, mN, sd)))
    F = np.concatenate((np.ones(nT, bool), np.zeros(nN, bool)))
    t = np.arange(len(g))
    led = dict(t=t, side=np.ones(len(g), np.int64), F=F, day=t, D5=np.zeros(len(g)), leg=np.zeros(len(g)))
    cells = dict(G={(1, 60): g}, FUND={(1, 60): np.zeros(len(g))}, FILL={}, PIN={}, led=led)
    A_ = dict(C=np.linspace(1000.0, 1.0, 2000))
    return S.evaluate(cells, A_, 1)


for nT, exp in ((200, "PASS_FLOW"), (199, "PASS_CONTROL")):
    ev_ = cells_for(nT, 800)
    bt.append(dict(test=f"screen.evaluate nT={nT}", expect=exp, got=ev_["verdict"], n=ev_["T"]["n"], mean=ev_["T"]["mean"], t_net=ev_["T"]["t_cost"],
                   diff=ev_["diff"], t_diff=ev_["t_diff"], mdd=ev_["T"]["mdd"], ok=(ev_["verdict"] == exp)))
ev_ = cells_for(199, 800, mN=0.0)
bt.append(dict(test="screen.evaluate nT=199, control arm C (all events) mean .08 < .14", expect="INCONCLUSIVE", got=ev_["verdict"], n=ev_["T"]["n"], mean=ev_["T"]["mean"],
               t_net=ev_["T"]["t_cost"], diff=ev_["diff"], t_diff=ev_["t_diff"], mdd=ev_["T"]["mdd"], ok=(ev_["verdict"] == "INCONCLUSIVE")))
out["boundary"] = bt
(OUT / "stats_rebuild.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8", newline="\n")

print("=== screen T arm / C / DIFF vs published")
for c in out["screen_T_rebuild"]["compared"]:
    print(c)
print("screen small-sample check: T clusters", A["T"]["clusters"], "SE0", A["T"]["se"], "SE CR1", A["T"]["se_cr1"], "t_cost", A["T"]["t_cost"], "-> CR1", A["T"]["t_cost_cr1"])
print("=== mal_bb A1")
for c in out["mal_bb_A1_rebuild"]["compared"]:
    print(c)
print("A1 clusters", B["clusters"], "t_net CR0", B["t_net"], "CR1", B["t_net_cr1"])
print("=== boundary")
for b in bt:
    print("OK " if b["ok"] else "BAD", b["test"], "| expect", b["expect"], "got", b["got"], "| t_net", None if b["t_net"] is None else round(float(b["t_net"]), 6), "diff", None if b["diff"] is None else round(float(b["diff"]), 9), "t_diff", None if b["t_diff"] is None else round(float(b["t_diff"]), 6))
