"""wt30_div_short: WaveTrend 30m lower-high divergence short, SPEC.md Card 1. See PRE_REG.md.

Passes: --pass count (event counts + regime mix, NO returns), --pass dev (DEV only). VALIDATION/HOLDOUT are never loaded:
the loader end is DEV_END. WT = layers/wavetrend/wavetrend.py only. Times UTC ms.
"""
import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest.layers.wavetrend import wavetrend as wtm  # noqa: E402

DAY = 86400000
BAR = 1800000
COST = rk.TAKER_RT_PCT          # 0.14 % RT, SOURCED
BAND = 53.0                     # SOURCED
SKIP = 48                       # dedup bars, OURS
WIN48H = 96                     # earlier cross within 48 h, OURS
K = 3                           # +-k bars around the earlier cross, OURS
HOLD = 24                       # exit after 24 bars, OURS
CTX_DAYS_BARS = 8 * 48          # 8 days
RSI_P = 14
SEED = 20261106
DATA = [("F:/MTS/data/dev_ext_2019_2021", "klines"), ("F:/MTS/data/bigtrade", "spot_raw")]
MIN_N = 30                      # minimum n for a cell to be able to pass, OURS


def load_1m(end_ms, start_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = {}
    for root, ds in DATA:
        for b in load_klines(root, ds, start_ms=start_ms, end_ms=end_ms):
            bars[b["t"]] = b
    return [bars[k] for k in sorted(bars)]


def ms(s):
    import pandas as pd
    return int(pd.Timestamp(s).tz_localize("UTC").timestamp() * 1000)


def c30_module():
    p = REPO / "MyTradingSys/research/wavetrend_c30_retest_2026-11-04/study.py"
    spec = importlib.util.spec_from_file_location("c30study", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def find_events(bars30, rows30, rsi30, rows4h, t4h):
    """Returns list of dicts, one per confirming cross c that satisfies the SPEC Card 1 event, before dedup flag."""
    n = len(bars30)
    wt1 = [r.wt1 for r in rows30]
    wt2 = [r.wt2 for r in rows30]
    ev = [r.event for r in rows30]
    down = [i for i in range(n) if ev[i] == -1]
    up_deep = [i for i in range(n) if ev[i] == 1 and wt1[i] <= -BAND]
    dots_top = [i for i in down if i > 0 and wt1[i - 1] >= BAND]      # valid top dots (prior-bar wt1 beyond +53)
    hi = [b["h"] for b in bars30]
    out = []
    for c in down:
        if not (0 < wt1[c] <= BAND):
            continue
        p_ok = None
        for p in reversed([d for d in down if c - WIN48H <= d < c]):
            if wt1[p] >= 45 and wt1[p] - wt1[c] >= 10:
                seg = wt1[p + 1:c]
                if len(seg) and min(seg) < 0:
                    d_ix = p + 1 + int(np.argmin(seg))
                    if max(hi[d_ix:c + 1]) > max(hi[max(0, p - K):p + K + 1]):
                        p_ok = (p, d_ix)
                        break
        if p_ok is None:
            continue
        p, d_ix = p_ok
        # his-context subset
        ctx = False
        ups = [u for u in up_deep if c - CTX_DAYS_BARS <= u < c]
        if ups:
            u = ups[-1]
            waves = sum(1 for d in down if u < d <= c and min(wt1[d], wt2[d]) > 0)
            ctx = waves >= 3
        # features
        drop = min(wt1[p + 1:c])
        tops = [t for t in dots_top if t < c]
        hrs = (c - tops[-1]) * 0.5 if tops else float("inf")
        t_close = bars30[c]["t"] + BAR
        sess = rk.session_tag(t_close // 1000)
        i1 = max(range(max(0, p - K), p + K + 1), key=lambda j: hi[j])
        i2 = max(range(d_ix, c + 1), key=lambda j: hi[j])
        r1, r2 = rsi30[i1], rsi30[i2]
        rsi_lower = (r1 is not None and r2 is not None and r2 < r1)
        # last closed 4h bar at t_close
        k4 = None
        for j in range(len(t4h) - 1, -1, -1):
            if t4h[j] + 4 * 3600000 <= t_close:
                k4 = j
                break
        slope = None
        if k4 is not None and k4 >= 3:
            a, b = rows4h[k4].wt1, rows4h[k4 - 3].wt1
            if not (math.isnan(a) or math.isnan(b)):
                slope = "up" if a > b else "down"
        out.append({"c": c, "p": p, "t_close": t_close, "ctx": ctx, "drop": drop, "hrs": hrs, "sess": sess,
                    "rsi_lower": rsi_lower, "slope": slope})
    # dedup: skip 48 bars after an event
    kept, last = [], None
    for e in out:
        if last is None or e["c"] - last >= SKIP:
            kept.append(e)
            last = e["c"]
    return kept


def trade(bars30, c):
    """short at close of c; fixed 24-bar and first-touch +-1 % (stop first if both in a bar). Returns (gross24, gross_ft) in %."""
    if c + HOLD >= len(bars30):
        return None
    px = bars30[c]["c"]
    g24 = -(bars30[c + HOLD]["c"] - px) / px * 100.0
    gft = g24
    for j in range(c + 1, c + HOLD + 1):
        if bars30[j]["h"] >= px * 1.01:
            gft = -1.0
            break
        if bars30[j]["l"] <= px * 0.99:
            gft = 1.0
            break
    return g24, gft


def stats(gs, days):
    g = np.array(gs)
    if len(g) == 0:
        return {"n": 0, "days": 0}
    net = g - COST
    m, se = rk.cluster_mean_se(net, days)
    t = rk.t_stat(m, se)
    return {"n": len(g), "days": len(set(days)), "gross": float(g.mean()), "net": m, "se": se, "t": t,
            "p": rk.norm_p_two(t), "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev"))
    a = ap.parse_args()
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    lo, hi_ = ms(splits.DEV_START), ms(splits.DEV_END)
    bars_1m = load_1m(hi_, ms("2020-01-01"))        # 2020-01..2021-12 = warm-up history only (PRE_DEV, no returns scored)
    assert bars_1m[-1]["t"] < hi_                    # HOLDOUT/VALIDATION never loaded
    b30 = resample(bars_1m, "30m", registry)
    b4 = resample(bars_1m, "4h", registry)
    rows30 = wtm.compute([(b["t"], b["h"], b["l"], b["c"]) for b in b30], BAR)
    rows4 = wtm.compute([(b["t"], b["h"], b["l"], b["c"]) for b in b4], 4 * 3600000)
    rsi30 = rsi_core([b["c"] for b in b30], RSI_P)
    t4 = [b["t"] for b in b4]
    evs = [e for e in find_events(b30, rows30, rsi30, rows4, t4) if lo <= e["t_close"] < hi_]
    c30 = c30_module()
    daily, wk, mo = c30.build_context(bars_1m, registry)
    ctx_at = c30.make_ctx_at(daily, wk, mo)
    mix = rk.regime_mix_line([ctx_at(t)["regime"] for t in c30.week_starts(lo, hi_)])
    (HERE / ("regime_mix_" + a.pass_ + ".txt")).write_text(mix + "\n", encoding="utf-8", newline="\n")
    tr = []
    for e in evs:
        r = trade(b30, e["c"])
        if r is not None:
            e["g24"], e["gft"] = r
            e["day"] = int(b30[e["c"]]["t"] // DAY)
            tr.append(e)
    # frozen bins: tercile edges of the DEV events' wt1 minimum between the crosses (computed on DEV only)
    q1, q2 = np.percentile([e["drop"] for e in tr], [100 / 3, 200 / 3]) if tr else (0, 0)

    def cells(e):
        out = []
        out.append("drop_deep" if e["drop"] <= q1 else "drop_mid" if e["drop"] <= q2 else "drop_shallow")
        out.append("top_0_12h" if e["hrs"] <= 12 else "top_12_24h" if e["hrs"] <= 24 else "top_gt24h")
        out.append({"late": "sess_21_08", "asia": "sess_21_08", "london": "sess_08_13", "ny": "sess_13_21"}[e["sess"]])
        out.append("rsi_lower" if e["rsi_lower"] else "rsi_not_lower")
        if e["slope"]:
            out.append("slope4h_" + e["slope"])
        if e["ctx"]:
            out.append("his_context")
        return out
    names = ["drop_deep", "drop_mid", "drop_shallow", "top_0_12h", "top_12_24h", "top_gt24h", "sess_21_08", "sess_08_13",
             "sess_13_21", "rsi_lower", "rsi_not_lower", "slope4h_up", "slope4h_down", "his_context"]
    if a.pass_ == "count":
        rows = [{"cell": "unconditional", "n": len(tr), "days": len({e["day"] for e in tr})}]
        for nm in names:
            sel = [e for e in tr if nm in cells(e)]
            rows.append({"cell": nm, "n": len(sel), "days": len({e["day"] for e in sel})})
        fname = "counts.csv"
    else:
        rows = []
        allr = dict(cell="unconditional", **stats([e["g24"] for e in tr], [e["day"] for e in tr]))
        allr["ft_net"] = float(np.mean([e["gft"] for e in tr]) - COST) if tr else float("nan")
        rows.append(allr)
        rng = np.random.default_rng(SEED)           # placebo: random 30m bars in DEV, same count, short, 24 bars
        valid = [i for i in range(len(b30) - HOLD) if lo <= b30[i]["t"] + BAR < hi_]
        pick = rng.choice(valid, size=len(tr), replace=False) if tr else []
        pg = [trade(b30, int(i)) for i in pick]
        pr = dict(cell="placebo", **stats([x[0] for x in pg], [int(b30[int(i)]["t"] // DAY) for i in pick]))
        pr["ft_net"] = float(np.mean([x[1] for x in pg]) - COST) if pg else float("nan")
        rows.append(pr)
        fam = []
        for nm in names:
            sel = [e for e in tr if nm in cells(e)]
            r = dict(cell=nm, **stats([e["g24"] for e in sel], [e["day"] for e in sel]))
            r["ft_net"] = float(np.mean([e["gft"] for e in sel]) - COST) if sel else float("nan")
            rows.append(r)
            fam.append(r)
        adj = rk.holm([r["p"] if r.get("n", 0) > 0 and r["p"] == r["p"] else 1.0 for r in fam], m=14)
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            r["pass_dev"] = bool(r.get("n", 0) >= MIN_N and r["net"] > 0 and q < 0.05 and r["ci_lo"] > 0)
        (HERE / "dev_edges.json").write_text(json.dumps({"q1": float(q1), "q2": float(q2)}), encoding="utf-8")
        fname = "dev_cells.csv"
    cols = sorted({k for r in rows for k in r}, key=lambda k: (k != "cell", k))
    with open(HERE / fname, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(mix)
    for r in rows:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
