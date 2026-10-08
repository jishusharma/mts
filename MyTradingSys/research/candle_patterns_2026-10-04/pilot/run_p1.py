"""P1 run: classical candle-pattern scan on DEV data (PRE_REG_CANDLE_PILOT.md sections 4-6). Definitions frozen.
Run: python MyTradingSys/research/candle_patterns_2026-10-04/pilot/run_p1.py
Writes P1_RESULTS.md, p1_results.json, appends TRIAL_REGISTRY.csv (run_id P1-2026-10-07).
Implementation choices not spelled out in the pre-reg (documented in P1_RESULTS.md):
 - common bar range i in [0, n-7] for every h so one family shares one bootstrap index set;
 - BH over all 54 trials per timeframe, INSUFFICIENT-N entries enter with p=1 (still counted as trials);
 - net-per-trade CI = circular block bootstrap (same block length) of sum(ev*net)/sum(ev), 1000 resamples, seed 12345;
 - volatility ratio denominator = mean range of the 14 bars ending at the signal bar (prior to the measured next bar).
"""
import sys
sys.dont_write_bytecode = True
import csv
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candles  # noqa: E402
import cdata  # noqa: E402
import stats_lite  # noqa: E402

OUT = HERE.parent
RUN_ID = "P1-2026-10-07"
DATE = "2026-10-07"
COST = 2 * (0.0005 + 0.0002)          # 14 bps round trip
HS = (1, 3, 5)
MIN_N = {"1d": 20, "1h": 100}
BLOCK = {"1d": 10, "1h": 24}
REPS = 1000
SEED = 12345
RC_ALPHA = 0.10


def forward_return(bars, i, h):
    return math.log(bars[i + 1 + h]["o"] / bars[i + 1]["o"])


def window_funding(bars, i, h, funding):
    return funding.sum(bars[i + 1]["t"], bars[i + 1 + h]["t"])


def net_trade(sign, fwd, fund):
    return sign * fwd - COST - sign * fund


def is_insufficient(n, tf):
    return n < MIN_N[tf]


def bh_over_trials(p_list):
    """BH q-values over all trials; None (INSUFFICIENT-N) enters as p=1 and returns None."""
    q = stats_lite.bh_qvalues([1.0 if p is None else p for p in p_list])
    return [None if p is None else qq for p, qq in zip(p_list, q)]


def triage(r, tf):
    """Section 5, all four conditions."""
    if is_insufficient(r["n"], tf):
        return "INSUFFICIENT-N"
    if (r["mean_net"] > 0 and r["ci_lo"] > 0 and r["p_adj"] is not None and r["p_adj"] < RC_ALPHA and r["stat"] > 0):
        return "PASS"
    return "FAIL"


def block_ci_mean(ev, net, block, reps=REPS, seed=SEED):
    """Circular block bootstrap 95 percent CI of mean(net | ev) over the bar index."""
    m = len(ev)
    evd = ev + ev
    pc, ps = [0.0], [0.0]
    for e, v in zip(evd, net + net):
        pc.append(pc[-1] + e)
        ps.append(ps[-1] + e * v)
    nb = int(math.ceil(m / float(block)))
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        c = s = 0.0
        for _b in range(nb):
            a = rng.randrange(m)
            c += pc[a + block] - pc[a]
            s += ps[a + block] - ps[a]
        if c > 0:
            out.append(s / c)
    out.sort()
    return out[int(0.025 * len(out))], out[min(len(out) - 1, int(0.975 * len(out)))]


def run_tf(bars, tf, funding):
    n = len(bars)
    m = n - 6                                  # i in 0..n-7 so that i+1+5 <= n-1
    sig = candles.signals(bars)
    fwd = {h: [forward_return(bars, i, h) for i in range(m)] for h in HS}
    fund = {h: [window_funding(bars, i, h, funding) for i in range(m)] for h in HS}
    items, meta = [], []
    for name, sign in candles.DIRECTIONAL.items():
        evs = [0] * m
        for i in sig[name]:
            if i < m:
                evs[i] = 1
        for h in HS:
            items.append({"name": "%s|h%d" % (name, h), "ev": evs, "val": fwd[h], "sign": sign, "min_n": MIN_N[tf]})
            meta.append((name, sign, h))
    rc = stats_lite.block_boot_family(items, m, BLOCK[tf], reps=REPS, seed=SEED)
    rows = []
    for it, r, (name, sign, h) in zip(items, rc, meta):
        ev = it["ev"]
        nn = r["n"]
        row = {"pattern": name, "h": h, "sign": sign, "tf": tf, "n": nn, "insufficient": r["insufficient"]}
        if nn:
            idx = [i for i in range(m) if ev[i]]
            nets = [net_trade(sign, fwd[h][i], fund[h][i]) for i in idx]
            wins = sum(1 for x in nets if x > 0)
            row["mean_gross"] = sum(sign * fwd[h][i] for i in idx) / nn
            row["mean_net"] = sum(nets) / nn
            row["win_rate"] = wins / float(nn)
            row["mean_all_fwd"] = sum(fwd[h]) / m
        if not r["insufficient"]:
            netall = [net_trade(sign, fwd[h][i], fund[h][i]) for i in range(m)]
            row["ci_lo"], row["ci_hi"] = block_ci_mean(ev, netall, BLOCK[tf])
            row.update({"stat": r["stat"], "t": r["t"], "p_raw": r["p_raw"], "p_two": r["p_two"], "p_adj": r["p_adj"]})
        rows.append(row)
    qs = bh_over_trials([r.get("p_two") for r in rows])
    for r, q in zip(rows, qs):
        r["q_bh"] = q
        r["triage"] = triage(r, tf) if not r["insufficient"] else "INSUFFICIENT-N"
    # volatility-state family: next-bar range ratio and next-bar |return|
    f = [(b["h"] - b["l"]) for b in bars]
    mv = n - 1 - 14
    ratio, absret = [], []
    for j in range(mv):
        i = j + 14
        mean_prior = sum(f[i - 13:i + 1]) / 14.0
        ratio.append(f[i + 1] / mean_prior if mean_prior > 0 else 1.0)
        absret.append(abs(math.log(bars[i + 1]["c"] / bars[i + 1]["o"])))
    vitems, vmeta = [], []
    for st in candles.VOL_STATES:
        evs = [0] * mv
        for i in sig[st]:
            if 14 <= i <= n - 2:
                evs[i - 14] = 1
        for metric, val in (("range_ratio", ratio), ("abs_return", absret)):
            vitems.append({"name": "%s|%s" % (st, metric), "ev": evs, "val": val, "sign": 1, "min_n": MIN_N[tf]})
            vmeta.append((st, metric, val, evs))
    vrc = stats_lite.block_boot_family(vitems, mv, BLOCK[tf], reps=REPS, seed=SEED)
    vrows = []
    for r, (st, metric, val, evs) in zip(vrc, vmeta):
        row = {"state": st, "metric": metric, "tf": tf, "n": r["n"], "insufficient": r["insufficient"]}
        if r["n"]:
            row["mean_event"] = sum(v for v, e in zip(val, evs) if e) / r["n"]
            row["mean_all"] = sum(val) / mv
        if not r["insufficient"]:
            row.update({"stat": r["stat"], "t": r["t"], "p_raw": r["p_raw"], "p_two": r["p_two"], "p_adj": r["p_adj"]})
        vrows.append(row)
    vq = bh_over_trials([r.get("p_two") for r in vrows])
    for r, q in zip(vrows, vq):
        r["q_bh"] = q
    return {"rows": rows, "vol": vrows, "n_bars": n, "m": m}


def g(x, fmt="%.1f", mult=1e4):
    return "-" if x is None else fmt % (mult * x)


def p(x):
    return "-" if x is None else "%.3f" % x


def main():
    funding = cdata.Funding()
    daily = cdata.load_daily()
    m1 = cdata.load_1m(cdata.HOURLY_START_MS, cdata.DEV_END_MS)
    hourly, dropped = cdata.resample_offset(m1, 60, 0)
    gaps = {"1d": len(cdata.contiguous(daily, cdata.DAY)), "1h": len(cdata.contiguous(hourly, cdata.HOUR))}
    res = {"1d": run_tf(daily, "1d", funding), "1h": run_tf(hourly, "1h", funding)}
    res["meta"] = {"run_id": RUN_ID, "gaps": gaps, "hourly_dropped_partial": dropped, "cost_bps": 1e4 * COST,
                   "reps": REPS, "seed": SEED, "block": BLOCK, "min_n": MIN_N}
    (OUT / "p1_results.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    reg = OUT / "TRIAL_REGISTRY.csv"
    new = not reg.exists()
    wins = {"1d": "2020-01-01..2024-06-30", "1h": "2022-01-01..2024-06-30"}
    with open(reg, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if new:
            w.writerow(["run_id", "date", "family", "variant", "tf", "window", "n", "mean_net_bps", "note"])
        for tf in ("1d", "1h"):
            for r in res[tf]["rows"]:
                w.writerow([RUN_ID, DATE, "P1", "%s|h%d" % (r["pattern"], r["h"]), tf, wins[tf], r["n"],
                            "" if "mean_net" not in r else r["mean_net"] * 1e4, r["triage"]])
            for r in res[tf]["vol"]:
                w.writerow([RUN_ID, DATE, "P1vol", "%s|%s" % (r["state"], r["metric"]), tf, wins[tf], r["n"], "",
                            "INSUFFICIENT-N" if r["insufficient"] else "p_adj=%.3f" % r["p_adj"]])
    md = ["# P1 RESULTS - classical candle patterns on DEV data (generated by run_p1.py, run %s)" % RUN_ID, "",
          "Definitions frozen in PRE_REG_CANDLE_PILOT.md section 4. Net = sign*fwd - 14 bps - sign*realised funding. Entry open(i+1), exit open(i+1+h).",
          "Reality-Check p = single-step max-T over the 54 (18 patterns x 3 h) family per timeframe, one-sided in the textbook direction; "
          "q = two-sided BH over the 54 trials (INSUFFICIENT-N enters with p=1). CI = circular block bootstrap of mean net per trade.",
          "Bars: 1d n=%d (gaps %d); 1h n=%d (gaps %d, dropped partial hours %d). Common range i<=n-7 for all h. Triage = section 5 (N, net>0 with CI lo>0, RC p<0.10, textbook direction)." % (
              res["1d"]["n_bars"], gaps["1d"], res["1h"]["n_bars"], gaps["1h"], dropped), ""]
    for tf in ("1d", "1h"):
        rows = res[tf]["rows"]
        live = [r for r in rows if not r["insufficient"]]
        md += ["## %s directional patterns (%d trials; %d INSUFFICIENT-N)" % (tf, len(rows), len(rows) - len(live)),
               "| pattern | h | n | win | gross bps | net bps [CI] | excess bps | t | RC p | q(BH) | triage |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            ci = "-" if "ci_lo" not in r else "[%.0f, %.0f]" % (1e4 * r["ci_lo"], 1e4 * r["ci_hi"])
            md.append("| %s | %d | %d | %s | %s | %s %s | %s | %s | %s | %s | %s |" % (
                r["pattern"], r["h"], r["n"], "-" if "win_rate" not in r else "%.0f%%" % (100 * r["win_rate"]),
                g(r.get("mean_gross")), g(r.get("mean_net")), ci, g(r.get("stat")),
                "-" if r.get("t") is None else "%.2f" % r["t"], p(r.get("p_adj")), p(r.get("q_bh")), r["triage"]))
        md.append("")
        md += ["## %s volatility-state family (6 trials; one-sided: event mean > all-bar mean)" % tf,
               "| state | metric | n | event mean | all-bar mean | diff | t | RC p | q(BH) |", "|---|---|---|---|---|---|---|---|---|"]
        for r in res[tf]["vol"]:
            fm = "%.3f" if r["metric"] == "range_ratio" else "%.4f"
            md.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (
                r["state"], r["metric"], r["n"], "-" if "mean_event" not in r else fm % r["mean_event"],
                "-" if "mean_all" not in r else fm % r["mean_all"], "-" if "stat" not in r else (fm % r["stat"]),
                "-" if r.get("t") is None else "%.2f" % r["t"], p(r.get("p_adj")), p(r.get("q_bh"))))
        md.append("")
    passed = [(tf, r["pattern"], r["h"]) for tf in ("1d", "1h") for r in res[tf]["rows"] if r["triage"] == "PASS"]
    md += ["## Triage summary", "Pass triage: %s" % (", ".join("%s %s h%d" % x for x in passed) if passed else "NONE"),
           "Trials: 1d %d + %d vol; 1h %d + %d vol (registry rows run_id %s)." % (len(res["1d"]["rows"]), len(res["1d"]["vol"]), len(res["1h"]["rows"]), len(res["1h"]["vol"]), RUN_ID)]
    (OUT / "P1_RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(md[-6:]))


if __name__ == "__main__":
    main()
