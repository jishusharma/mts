"""V1: event study on DEV (PRE_REG_VOLUME_2026-10-09.md sections 4-8) + placebo calibration (section 5).
Run: python MyTradingSys/research/volume_2026-10-09/run_v1.py [--placebo 20] [--tf 1d,4h]
Writes V1_DEV_RESULTS.md, v1_dev_results.json (frozen candidate list), appends TRIAL_REGISTRY.csv. DEV window only (no unseal).
Funding is charged on settlements in (entry, exit]. Entry open(i+1), exit open(i+1+h).
"""
import sys
sys.dont_write_bytecode = True
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vdata as D  # noqa: E402
import vfeat as F  # noqa: E402
import vstats as S  # noqa: E402

RUN_ID = "V1-2026-10-09"
COST = 2 * (0.0005 + 0.0002)
HS = {"1d": (3, 10, 20), "4h": (6, 18, 42)}
MIN_N = {"1d": 30, "4h": 100}
BLOCK = {"1d": 25, "4h": 60}
MEDH = {"1d": 10, "4h": 18}
REPS = 1000
SEED = 12345
ALPHA = 0.10


def build(b, tf, funding, shift=0):
    """Features/events on bars b (optionally with volume/tbv circularly shifted = placebo) and the common-range arrays."""
    if shift:
        b = dict(b)
        b["v"] = np.roll(b["v"], shift)
        b["tbv"] = np.roll(b["tbv"], shift)
    f = F.features(b, tf)
    ev = F.events(b, f)
    n = len(b["c"])
    hmax = max(HS[tf])
    idx = np.arange(F.W, n - 1 - hmax)              # i + 1 + hmax <= n - 1
    fwd, fund = {}, {}
    for h in HS[tf]:
        fwd[h] = np.log(b["o"][idx + 1 + h] / b["o"][idx + 1])
        fund[h] = funding.window(b["t"], idx + 1, idx + 1 + h)
    return b, f, ev, idx, fwd, fund


def run_family(tf, b, f, ev, idx, fwd, fund, reps=REPS, seed=SEED):
    names = F.EVENT_NAMES
    hs = HS[tf]
    EV = np.array([ev[k][idx] for k in names])
    dirs = np.array([F.DIRS[k] for k in names], dtype=float)
    VAL = np.stack([np.stack([dirs[e] * fwd[h] for h in hs]) for e in range(len(names))])      # (E,H,m)
    rc = S.rc_family(EV, VAL, BLOCK[tf], MIN_N[tf], reps=reps, seed=seed)
    return names, hs, EV, dirs, VAL, rc


def triage_table(tf, names, hs, EV, dirs, rc, fwd, fund, with_ci=True):
    rows = []
    for e, nm in enumerate(names):
        for hi, h in enumerate(hs):
            for orient, osign in (("cont", 1), ("rev", -1)):
                sgn = dirs[e] * osign
                n = int(rc["n"][e])
                live = bool(rc["live"][e])
                row = {"event": nm, "tf": tf, "h": h, "orient": orient, "sign": int(sgn), "n": n, "live": live}
                if n:
                    nets = sgn * fwd[h] - COST - sgn * fund[h]
                    row["gross_bps"] = float(1e4 * (sgn * fwd[h][EV[e]]).mean())
                    row["net_bps"] = float(1e4 * nets[EV[e]].mean())
                    row["win"] = float((nets[EV[e]] > 0).mean())
                    row["excess_bps"] = float(1e4 * osign * rc["stat"][e, hi])
                    if live:
                        m_, lo, hi_ = S.mean_ci(EV[e], nets, BLOCK[tf], reps=REPS, seed=SEED)
                        row["ci_lo_bps"], row["ci_hi_bps"] = 1e4 * lo, 1e4 * hi_
                        row["t"] = float(osign * rc["t"][e, hi])
                        row["p_adj"] = float(rc["p_adj_cont"][e, hi] if osign == 1 else rc["p_adj_rev"][e, hi])
                        row["p_raw"] = float(rc["p_raw_cont"][e, hi] if osign == 1 else rc["p_raw_rev"][e, hi])
                        sdv = float(np.std(fwd[h]))
                        row["mde_bps"] = float(1e4 * S.mde(sdv, n))
                row["pass"] = bool(live and n and row.get("net_bps", -1) > 0 and row.get("ci_lo_bps", -1) > 0
                                   and row.get("p_adj", 1) < ALPHA and row.get("excess_bps", -1) > 0)
                rows.append(row)
    # BH q over all trials in this tf (insufficient enters as p=1)
    ps = [r.get("p_raw", 1.0) if r["live"] else 1.0 for r in rows]
    qs = S.bh_qvalues(ps)
    for r, qv in zip(rows, qs):
        r["q_bh"] = float(qv) if r["live"] else None
    return rows


def contrasts(tf, b, f, ev, idx, fwd):
    """C1-C8 and (4h) TH1, TH3. Orientation: sign * fwd with sign = event direction (continuation positive)."""
    h = MEDH[tf]
    r = fwd[h]
    keys = F.slot_keys(b, tf)
    sg, wkend = keys["sg"][idx], keys["weekend"][idx]
    e = {k: v[idx] for k, v in ev.items()}
    d = F.DIRS
    pl = {k: v[idx] for k, v in F.plain_rv_spikes(b, f).items()}

    def pool(names, evs=e):
        """pooled event indicator and per-bar orientation value dir*fwd (bars with two events cannot occur: up/down are exclusive)."""
        ind = np.zeros(len(r), dtype=bool)
        val = np.zeros(len(r))
        for nm in names:
            ind |= evs[nm]
            val = np.where(evs[nm], d[nm] * r, val)
        return ind, val

    out = []

    def add(label, A, B, val, note):
        c = S.contrast(A, B, val, BLOCK[tf], reps=REPS, seed=SEED)
        c.update({"label": label, "note": note, "tf": tf, "h": h})
        out.append(c)

    for lab, a, bn, sgn, note in (("C1", "BBSQ_UP_V", "BBSQ_UP_N", 1, "squeeze up-break: vol-confirmed minus not"),
                                  ("C2", "BBSQ_DN_V", "BBSQ_DN_N", -1, "squeeze down-break (short oriented)"),
                                  ("C3", "DON_UP_V", "DON_UP_N", 1, "Donchian up: vol-confirmed minus not"),
                                  ("C4", "DON_DN_V", "DON_DN_N", -1, "Donchian down (short oriented)"),
                                  ("C5", "R60U_V", "R60U_N", 1, "RSI up-cross 60: vol minus not"),
                                  ("C6", "R40D_V", "R40D_N", -1, "RSI down-cross 40 (short oriented)")):
        add(lab, e[a], e[bn], sgn * r, note)
    sp_ind, sp_val = pool(["SP3_UP", "SP3_DN"])
    spp_ind, spp_val = pool(["SP3_UP", "SP3_DN"], pl)
    add("C7", sp_ind, spp_ind, np.where(sp_ind, sp_val, spp_val), "SP3 defined with RVadj minus defined with plain RV (overlapping sets; signed cont return)")
    add("C8/TH2", sp_ind & wkend, sp_ind & ~wkend, sp_val, "SP3 weekend minus weekday (signed cont return)")
    if tf == "4h":
        add("TH1", sp_ind & (sg == 2), sp_ind & (sg == 0), sp_val, "SP3 session C (16-24 UTC) minus A (00-08 UTC)")
        bv_ind, bv_val = pool(["BBSQ_UP_V", "BBSQ_DN_V"])
        add("TH3", bv_ind & (sg == 1), bv_ind & (sg == 0), bv_val, "BBSQ_*_V session B (08-16) minus A (00-08)")
    for c in out:
        c["supported_ci"] = bool(c["lo"] > 0 or c["hi"] < 0) if c["diff"] == c["diff"] else False
    cs = [c for c in out if c["label"].startswith("C")]
    qs = S.bh_qvalues([c["p_two"] if c["p_two"] == c["p_two"] else 1.0 for c in cs])
    for c, qv in zip(cs, qs):
        c["q_bh"] = float(qv)
    ths = [c for c in out if c["label"] in ("TH1", "C8/TH2", "TH3")]
    qs = S.bh_qvalues([c["p_two"] if c["p_two"] == c["p_two"] else 1.0 for c in ths])
    for c, qv in zip(ths, qs):
        c["q_th"] = float(qv)
    return out


def decay_profile(tf, b, ev, idx, nm, sgn, hmax):
    """mean sign*fwd path h=1..hmax after the event (T2)."""
    n = len(b["c"])
    ii = idx[ev[nm][idx]]
    ii = ii[ii + 1 + hmax <= n - 1]
    out = []
    for h in range(1, hmax + 1):
        out.append(float(1e4 * np.mean(sgn * np.log(b["o"][ii + 1 + h] / b["o"][ii + 1]))))
    return out


def strat_T3(tf, b, ev, idx, nm, sgn, h, fwd_h):
    keys = F.slot_keys(b, tf)
    sg, wk = keys["sg"][idx], keys["weekend"][idx]
    c = b["c"]
    d1 = D.load_1d()
    sma = np.full(len(d1["c"]), np.nan)
    w = np.lib.stride_tricks.sliding_window_view(d1["c"], 200).mean(axis=1)
    sma[199:] = w
    daymap = dict(zip(d1["t"] // D.DAY, np.concatenate([[np.nan], sma[:-1]])))      # SMA200 as of the previous day close
    pday = dict(zip(d1["t"] // D.DAY, np.concatenate([[np.nan], d1["c"][:-1]])))
    regime = np.array([1.0 if (pday.get(t // D.DAY, np.nan) > daymap.get(t // D.DAY, np.nan)) else (0.0 if daymap.get(t // D.DAY, np.nan) == daymap.get(t // D.DAY, np.nan) else np.nan) for t in b["t"][idx]])
    e = ev[nm][idx]
    allm = fwd_h.mean()
    rows = []
    for lab, mk in (("session A 00-08", sg == 0), ("session B 08-16", sg == 1), ("session C 16-24", sg == 2), ("weekend", wk), ("weekday", ~wk),
                    ("bull (prev close > SMA200)", regime == 1.0), ("bear (prev close < SMA200)", regime == 0.0)):
        mm = e & mk
        if mm.sum() >= 5:
            rows.append((lab, int(mm.sum()), float(1e4 * (sgn * (fwd_h[mm].mean() - allm)))))
    return rows


def fmt_cell(r):
    if not r["live"]:
        return "n=%d INSUFF" % r["n"]
    return "n=%d, exc %+.0f bp, p=%.2f" % (r["n"], r["excess_bps"], r["p_adj"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--placebo", type=int, default=20)
    ap.add_argument("--tf", default="1d,4h")
    a = ap.parse_args()
    funding = D.Funding()
    base = {"1d": D.load_1d(), "4h": D.load_4h()}
    L = []

    def P(s=""):
        L.append(s)

    P("# V1 DEV RESULTS - BTC volume event study (run %s, DEV 2020-01-01 .. 2024-06-30)" % RUN_ID)
    P()
    P("Definitions and decision rule: PRE_REG_VOLUME_2026-10-09.md (frozen in commit ec18096 before any outcome). Net = sign*fwd - 14 bps - sign*funding in (entry, exit]. "
      "Excess = sign*(mean fwd | event - mean fwd | all bars), BTC drift cancels. p_adj = White Reality-Check max-T over all 216 trials of the timeframe (both orientations). "
      "Triage PASS needs n >= min, net mean > 0 with block-bootstrap CI lower bound > 0, p_adj < 0.10, excess > 0.")
    P()
    registry = []
    candidates = []
    T = {}
    for tf in a.tf.split(","):
        b, f, ev, idx, fwd, fund = build(base[tf], tf, funding)
        names, hs, EV, dirs, VAL, rc = run_family(tf, b, f, ev, idx, fwd, fund)
        rows = triage_table(tf, names, hs, EV, dirs, rc, fwd, fund)
        T[tf] = (b, f, ev, idx, fwd, fund, rows)
        npass = sum(r["pass"] for r in rows)
        nlive = sum(1 for r in rows if r["live"])
        P("## %s: %d bars in range, %d trials (%d live, %d INSUFFICIENT-N), **%d pass triage**" % (tf, len(idx), len(rows), nlive, len(rows) - nlive, npass))
        P()
        sdv = {h: float(np.std(fwd[h])) for h in hs}
        P("Analytic minimum detectable excess (80 pct power, one-sided .05) per event size n at each horizon: " +
          "; ".join("h=%d: n=50 -> %.0f bp, n=200 -> %.0f bp, n=1000 -> %.0f bp" % (h, 1e4 * S.mde(sdv[h], 50), 1e4 * S.mde(sdv[h], 200), 1e4 * S.mde(sdv[h], 1000)) for h in hs))
        P("(sd of the h-bar forward return: " + ", ".join("h=%d: %.0f bp" % (h, 1e4 * sdv[h]) for h in hs) + ")")
        P()
        P("### %s: continuation-oriented excess return per event and horizon (cell: n, continuation excess bp with its RC p_adj, and the RC p_adj of the reversal orientation)" % tf)
        P()
        P("| event | dir | " + " | ".join("h=%d" % h for h in hs) + " |")
        P("|---|---|" + "---|" * len(hs))
        for nm in names:
            cells = []
            for h in hs:
                rc_ = next(r for r in rows if r["event"] == nm and r["h"] == h and r["orient"] == "cont")
                rr_ = next(r for r in rows if r["event"] == nm and r["h"] == h and r["orient"] == "rev")
                if not rc_["live"]:
                    cells.append("n=%d INSUFF" % rc_["n"])
                else:
                    cells.append("n=%d, cont %+.0f bp (p %.2f) / rev p %.2f" % (rc_["n"], rc_["excess_bps"], rc_["p_adj"], rr_["p_adj"]))
            P("| %s | %+d | %s |" % (nm, F.DIRS[nm], " | ".join(cells)))
        P()
        live = [r for r in rows if r["live"]]
        live.sort(key=lambda r: r["p_adj"])
        P("### %s: 12 best trials by RC p_adj" % tf)
        P()
        P("| event | h | orient | n | gross bp | net bp [95% CI] | win | excess bp | t | p_raw | p_adj | q_BH | MDE bp | triage |")
        P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in live[:12]:
            P("| %s | %d | %s | %d | %+.0f | %+.0f [%+.0f, %+.0f] | %.0f%% | %+.0f | %.2f | %.3f | %.3f | %.2f | %.0f | %s |" % (
                r["event"], r["h"], r["orient"], r["n"], r["gross_bps"], r["net_bps"], r["ci_lo_bps"], r["ci_hi_bps"], 100 * r["win"], r["excess_bps"],
                r["t"], r["p_raw"], r["p_adj"], r["q_bh"], r["mde_bps"], "PASS" if r["pass"] else "FAIL"))
        P()
        for r in rows:
            registry.append([RUN_ID, "2026-10-09", "V1", r["event"], tf, r["h"], r["sign"], "DEV", r["n"],
                             "" if "net_bps" not in r else "%.1f" % r["net_bps"], "" if "p_adj" not in r else "%.4f" % r["p_adj"], "PASS" if r["pass"] else ("INSUFFICIENT-N" if not r["live"] else "FAIL")])
            if r["pass"]:
                candidates.append(r)
        cs = contrasts(tf, b, f, ev, idx, fwd)
        P("### %s: registered contrasts at h=%d (does volume add information? time hypotheses)" % (tf, MEDH[tf]))
        P()
        P("| id | what | nA | nB | mean A bp | mean B bp | diff bp | 95% CI bp | p | q_BH (C-family) | q (TH-family) | CI excludes 0 |")
        P("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for c in cs:
            P("| %s | %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                c["label"], c["note"], c["nA"], c["nB"],
                "n/a" if c["diff"] != c["diff"] else "%+.0f" % (1e4 * c["meanA"]), "n/a" if c["diff"] != c["diff"] else "%+.0f" % (1e4 * c["meanB"]),
                "n/a" if c["diff"] != c["diff"] else "%+.0f" % (1e4 * c["diff"]),
                "n/a" if c["diff"] != c["diff"] else "[%+.0f, %+.0f]" % (1e4 * c["lo"], 1e4 * c["hi"]),
                "n/a" if c["p_two"] != c["p_two"] else "%.3f" % c["p_two"],
                "%.3f" % c["q_bh"] if "q_bh" in c else "-", "%.3f" % c["q_th"] if "q_th" in c else "-", "yes" if c["supported_ci"] else "no"))
            registry.append([RUN_ID, "2026-10-09", "contrast", c["label"], tf, c["h"], 0, "DEV", min(c["nA"], c["nB"]),
                             "" if c["diff"] != c["diff"] else "%.1f" % (1e4 * c["diff"]), "" if c["p_two"] != c["p_two"] else "%.4f" % c["p_two"], "SUPPORTED" if (c["supported_ci"] and c.get("q_bh", c.get("q_th", 1)) < 0.10) else "NOT-SUPPORTED"])
        P()
        T[tf] = T[tf] + (cs,)

    # placebo calibration
    if a.placebo:
        P("## Placebo calibration (volume and taker-buy columns circularly shifted by a multiple of 42 bars, lag >= 504; family-wise RC pass = any trial with p_adj < 0.10)")
        P()
        for tf in a.tf.split(","):
            rng = np.random.default_rng(2026)
            hits = []
            trig = {}
            for k in range(1, a.placebo + 1):
                lag = int(42 * rng.integers(12, 200))
                bp, fp, evp, idxp, fwdp, fundp = build(base[tf], tf, funding, shift=lag)
                namesp, hsp, EVp, dirsp, VALp, rcp = run_family(tf, bp, fp, evp, idxp, fwdp, fundp, reps=500, seed=k)
                live = rcp["live"][:, None] & np.ones((1, len(hsp)), dtype=bool)
                pmin = np.minimum(np.where(live, rcp["p_adj_cont"], 1.0), np.where(live, rcp["p_adj_rev"], 1.0))
                hit = bool((pmin < 0.10).any())
                hits.append(hit)
                if hit:
                    e_, h_ = np.unravel_index(np.argmin(pmin), pmin.shape)
                    trig[namesp[e_]] = trig.get(namesp[e_], 0) + 1
                registry.append([RUN_ID, "2026-10-09", "placebo", "family", tf, 0, 0, "DEV", k, "", "%.4f" % pmin.min(), "HIT" if hit else "clean"])
            rate = float(np.mean(hits))
            P("- %s: %d placebo runs, family-wise pass rate %.2f (expected <= 0.10; miscalibrated if > 0.20) -> **%s**. Events that triggered: %s" % (
                tf, a.placebo, rate, "CALIBRATED" if rate <= 0.20 else "MISCALIBRATED", trig or "none"))
        P()

    # T2/T3 for any candidate
    P("## Candidates frozen for VALIDATION (triage PASS on DEV)")
    P()
    if not candidates:
        P("**None.** No event x horizon x orientation passes the registered triage on DEV in either timeframe. Nothing is sent to VALIDATION; HOLDOUT stays sealed.")
    else:
        P("| event | tf | h | orient | n | net bp [CI] | excess bp | p_adj |")
        P("|---|---|---|---|---|---|---|---|")
        for r in candidates:
            P("| %s | %s | %d | %s | %d | %+.0f [%+.0f, %+.0f] | %+.0f | %.3f |" % (r["event"], r["tf"], r["h"], r["orient"], r["n"], r["net_bps"], r["ci_lo_bps"], r["ci_hi_bps"], r["excess_bps"], r["p_adj"]))
        P()
        for r in candidates:
            tf = r["tf"]
            b, f, ev, idx, fwd, fund = T[tf][:6]
            hm = max(HS[tf])
            prof = decay_profile(tf, b, ev, idx, r["event"], r["sign"], hm)
            P("T2 decay (%s %s %s): mean signed fwd bp by bar after entry: %s" % (r["event"], tf, r["orient"], ", ".join("%d:%+.0f" % (i + 1, x) for i, x in enumerate(prof) if (i + 1) % (6 if tf == "4h" else 3) == 0 or i == 0)))
            P("T3 EXPLORATORY strata (%s %s %s, h=%d, excess bp vs all bars): %s" % (r["event"], tf, r["orient"], r["h"], "; ".join("%s n=%d %+.0f" % x for x in strat_T3(tf, b, ev, idx, r["event"], r["sign"], r["h"], fwd[r["h"]]))))
        P()
    OUTMD = HERE / "V1_DEV_RESULTS.md"
    OUTMD.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    (HERE / "v1_dev_results.json").write_text(json.dumps({"run_id": RUN_ID, "candidates": [{k: (v if not isinstance(v, np.generic) else v.item()) for k, v in c.items()} for c in candidates]}, indent=1), encoding="utf-8", newline="\n")
    reg = HERE / "TRIAL_REGISTRY.csv"
    new = not reg.exists()
    with open(reg, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if new:
            w.writerow(["run_id", "date", "family", "event", "tf", "h", "sign", "window", "n", "mean_net_bps", "p_adj", "note"])
        w.writerows(registry)
    print("wrote", OUTMD, "registry rows", len(registry), "candidates", len(candidates))


if __name__ == "__main__":
    main()
