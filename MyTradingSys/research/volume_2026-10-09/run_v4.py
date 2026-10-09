"""V4: pooled volume-confirmation premium (PRE_REG_ADDENDUM_B_2026-10-09.md). DEV = descriptive prior; VALIDATION = the test (once);
HOLDOUT is opened ONLY if VALIDATION supports the hypothesis (p < 0.025, VCP > 0) for that timeframe.
Run: python MyTradingSys/research/volume_2026-10-09/run_v4.py -> V4_RESULTS.md, appends TRIAL_REGISTRY.csv
"""
import sys
sys.dont_write_bytecode = True
import csv
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vdata as D  # noqa: E402
import vfeat as F  # noqa: E402
import vstats as S  # noqa: E402

RUN_ID = "V4-2026-10-09"
COST = 2 * (0.0005 + 0.0002)
PAIRS = [("BBSQ_UP_V", "BBSQ_UP_N", 1), ("BBSQ_DN_V", "BBSQ_DN_N", -1), ("DON_UP_V", "DON_UP_N", 1),
         ("DON_DN_V", "DON_DN_N", -1), ("R60U_V", "R60U_N", 1), ("R40D_V", "R40D_N", -1)]
CFG = {"4h": {"h": 18, "block": 60, "alpha": 0.025}, "1d": {"h": 10, "block": 25, "alpha": 0.025}}
LOADERS = {"4h": D.load_4h, "1d": D.load_1d}


def vcp(tf, b, lo_ms, hi_ms=None):
    """Pooled VCP on bars with lo_ms <= open (< hi_ms); features computed on all of b (warm-up)."""
    h = CFG[tf]["h"]
    f = F.features(b, tf)
    ev = F.events(b, f)
    n = len(b["c"])
    idx = np.arange(F.W, n - 1 - h)
    idx = idx[b["t"][idx] >= lo_ms]
    if hi_ms is not None:
        idx = idx[b["t"][idx] < hi_ms]
    fwd = np.log(b["o"][idx + 1 + h] / b["o"][idx + 1])
    m = len(idx)
    cA, sA, cB, sB = np.zeros(m), np.zeros(m), np.zeros(m), np.zeros(m)
    per = []
    for v_nm, n_nm, dr in PAIRS:
        ev_v, ev_n = ev[v_nm][idx], ev[n_nm][idx]
        cA += ev_v; sA += ev_v * dr * fwd
        cB += ev_n; sB += ev_n * dr * fwd
        if ev_v.sum() and ev_n.sum():
            per.append((v_nm, int(ev_v.sum()), int(ev_n.sum()), float(1e4 * ((dr * fwd)[ev_v].mean() - (dr * fwd)[ev_n].mean()))))
        else:
            per.append((v_nm, int(ev_v.sum()), int(ev_n.sum()), None))
    c = S.pooled_contrast(cA, sA, cB, sB, CFG[tf]["block"], reps=1000, seed=12345)
    c["per_pair"] = per
    c["pos_pairs"] = sum(1 for x in per if x[3] is not None and x[3] > 0)
    c["n_pairs"] = sum(1 for x in per if x[3] is not None)
    # exploratory session split (4h)
    if tf == "4h":
        sg = F.slot_keys(b, tf)["sg"][idx]
        sess = []
        for g, lab in ((0, "A 00-08"), (1, "B 08-16"), (2, "C 16-24")):
            mk = (sg == g)
            cc = S.pooled_contrast(cA * mk, sA * mk, cB * mk, sB * mk, CFG[tf]["block"], reps=500, seed=12345)
            sess.append((lab, cc["nA"], cc["nB"], cc["diff"], cc["lo"], cc["hi"]))
        c["sessions"] = sess
    c["window_bars"] = m
    return c


def fmt(c):
    if c["diff"] != c["diff"]:
        return "n/a"
    return "VCP %+.0f bp [%+.0f, %+.0f], confirmed n=%d mean %+.0f bp (net of 14 bp: %+.0f), unconfirmed n=%d mean %+.0f bp, one-sided p=%.3f, pairs positive %d/%d" % (
        1e4 * c["diff"], 1e4 * c["lo"], 1e4 * c["hi"], c["nA"], 1e4 * c["meanA"], 1e4 * c["meanA"] - 1e4 * COST, c["nB"], 1e4 * c["meanB"], c["p_one"], c["pos_pairs"], c["n_pairs"])


def descriptive_insufficient(L):
    """B2: INSUFFICIENT-N events on DEV, descriptive only."""
    MINN = {"4h": 100, "1d": 30}
    HSS = {"4h": (6, 18, 42), "1d": (3, 10, 20)}
    BL = {"4h": 60, "1d": 25}
    L.append("## Descriptive appendix (B2): events too rare for the registered test - DEV, oriented gross forward return, NO inference, NO pass/fail")
    L.append("")
    L.append("| event | tf | n | " + " | ".join("h index %d" % i for i in range(1, 4)) + " |")
    L.append("|---|---|---|---|---|---|")
    for tf in ("4h", "1d"):
        b = LOADERS[tf]()
        f = F.features(b, tf)
        ev = F.events(b, f)
        n = len(b["c"])
        hmax = max(HSS[tf])
        idx = np.arange(F.W, n - 1 - hmax)
        for nm in F.EVENT_NAMES:
            e = ev[nm][idx]
            k = int(e.sum())
            if k >= MINN[tf] or k < 20:
                continue
            cells = []
            for h in HSS[tf]:
                fw = np.log(b["o"][idx + 1 + h] / b["o"][idx + 1]) * F.DIRS[nm]
                mu, lo, hi = S.mean_ci(e, fw, BL[tf], reps=500, seed=12345)
                cells.append("h=%d: %+.0f bp [%+.0f, %+.0f] (all bars %+.0f)" % (h, 1e4 * mu, 1e4 * lo, 1e4 * hi, 1e4 * fw.mean()))
            L.append("| %s (dir %+d) | %s | %d | %s |" % (nm, F.DIRS[nm], tf, k, " | ".join(cells)))
    L.append("")


def main():
    L = []
    P = L.append
    reg = []
    P("# V4 RESULTS - pooled volume-confirmation premium (VCP)")
    P("")
    P("Registered in PRE_REG_ADDENDUM_B_2026-10-09.md (commit f69f01c) before any V4 outcome. VCP = pooled mean oriented gross forward return of volume-CONFIRMED breakout/cross events (RVadj >= 1.5) minus UNCONFIRMED (< 1.5) over six pairs "
      "(BB-squeeze up/down, Donchian-20 up/down, RSI(14) cross 60 up / 40 down). H1: VCP > 0. Primary 4h h=18, secondary 1d h=10, Bonferroni alpha 0.025 each.")
    P("")
    holdout_open = {}
    for tf in ("4h", "1d"):
        P("## %s (h = %d)" % (tf, CFG[tf]["h"]))
        P("")
        bd = LOADERS[tf](start_ms=D.START_MS, end_ms=D.DEV_END_MS)
        dev = vcp(tf, bd, D.START_MS)
        P("- DEV (descriptive prior, NOT a test, hypothesis was chosen on it): " + fmt(dev))
        bv = LOADERS[tf](start_ms=D.START_MS, end_ms=D.VALID_END_MS)
        val = vcp(tf, bv, D.DEV_END_MS)
        P("- **VALIDATION (the test)**: " + fmt(val))
        sup = bool(val["diff"] == val["diff"] and val["diff"] > 0 and val["p_one"] < CFG[tf]["alpha"])
        P("- VALIDATION verdict: **%s** (support needs one-sided p < %.3f and VCP > 0)" % ("SUPPORTED" if sup else "NOT SUPPORTED", CFG[tf]["alpha"]))
        holdout_open[tf] = sup
        reg.append([RUN_ID, "2026-10-09", "V4-vcp", "VCP", tf, CFG[tf]["h"], 0, "VALID", val["nA"] + val["nB"], "%.1f" % (1e4 * val["diff"]) if val["diff"] == val["diff"] else "", "%.4f" % val["p_one"] if val["p_one"] == val["p_one"] else "", "SUPPORTED" if sup else "NOT-SUPPORTED"])
        P("")
        P("Per-pair difference (confirmed minus unconfirmed, bp, oriented gross), DEV then VALIDATION:")
        P("")
        P("| pair | DEV nV / nN | DEV diff | VALID nV / nN | VALID diff |")
        P("|---|---|---|---|---|")
        for d_, v_ in zip(dev["per_pair"], val["per_pair"]):
            P("| %s | %d / %d | %s | %d / %d | %s |" % (d_[0], d_[1], d_[2], "n/a" if d_[3] is None else "%+.0f" % d_[3], v_[1], v_[2], "n/a" if v_[3] is None else "%+.0f" % v_[3]))
        P("")
        if tf == "4h":
            P("EXPLORATORY session split of the pooled difference (bp; CI; not evidence): DEV: " + "; ".join("%s nV=%d nN=%d %+.0f [%+.0f, %+.0f]" % (s[0], s[1], s[2], 1e4 * s[3], 1e4 * s[4], 1e4 * s[5]) for s in dev["sessions"]))
            P("")
            P("VALIDATION: " + "; ".join("%s nV=%d nN=%d %+.0f [%+.0f, %+.0f]" % (s[0], s[1], s[2], 1e4 * s[3], 1e4 * s[4], 1e4 * s[5]) for s in val["sessions"]))
            P("")
        if sup:
            bh = LOADERS[tf](start_ms=D.START_MS, end_ms=D.ms(2026, 10, 1), unseal=True)      # only reached when VALIDATION supported the hypothesis
            hold = vcp(tf, bh, D.VALID_END_MS)
            hsup = bool(hold["diff"] > 0 and hold["p_one"] < CFG[tf]["alpha"])
            P("- **HOLDOUT (opened once because VALIDATION supported)**: " + fmt(hold))
            P("- HOLDOUT verdict: **%s**" % ("SUPPORTED" if hsup else "NOT SUPPORTED"))
            reg.append([RUN_ID, "2026-10-09", "V4-vcp", "VCP", tf, CFG[tf]["h"], 0, "HOLDOUT", hold["nA"] + hold["nB"], "%.1f" % (1e4 * hold["diff"]), "%.4f" % hold["p_one"], "SUPPORTED" if hsup else "NOT-SUPPORTED"])
        else:
            P("- HOLDOUT: sealed (VALIDATION did not support the hypothesis).")
        P("")
    descriptive_insufficient(L)
    (HERE / "V4_RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "TRIAL_REGISTRY.csv", "a", newline="", encoding="utf-8") as fh:
        csv.writer(fh, lineterminator="\n").writerows(reg)
    print("\n".join(L))


if __name__ == "__main__":
    main()
