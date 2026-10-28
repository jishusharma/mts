"""V2: volume STATE family on daily bars, DEV only (PRE_REG_ADDENDUM_A_2026-10-09.md A2) + placebo.
Run: python MyTradingSys/research/volume_2026-10-09/run_v2.py [--placebo 20]
Writes V2_DEV_RESULTS.md, v2_dev_results.json, appends TRIAL_REGISTRY.csv (run_id V2-2026-10-09).
"""
import sys
sys.dont_write_bytecode = True
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vdata as D  # noqa: E402
import vstate as T  # noqa: E402
import vstats as S  # noqa: E402

RUN_ID = "V2-2026-10-09"
COST = 2 * (0.0005 + 0.0002)
HS = (5, 10, 20)
BLOCK = 40
MIN_N = 100
REPS = 1000
SEED = 12345
ALPHA = 0.10
NAMES = T.STATE_EVENTS


def prepare(d1, h1, funding, shift_days=0, lo_ms=None, hi_ms=None):
    """Compute states/events on the full given arrays (so warm-up is filled), then select bars with lo_ms <= open < hi_ms whose forward
    window stays inside the arrays. shift_days>0 = placebo: volume/tbv of both series circularly shifted (days, and days*24 hours)."""
    if shift_days:
        d1 = dict(d1)
        h1 = dict(h1)
        d1["v"], d1["tbv"] = np.roll(d1["v"], shift_days), np.roll(d1["tbv"], shift_days)
        h1["v"], h1["tbv"] = np.roll(h1["v"], shift_days * 24), np.roll(h1["tbv"], shift_days * 24)
    s = T.states(d1, h1)
    ev = T.events2(s, len(d1["c"]))
    n = len(d1["c"])
    hmax = max(HS)
    idx = np.arange(T.W2, n - 1 - hmax)
    if lo_ms is not None:
        idx = idx[d1["t"][idx] >= lo_ms]
    if hi_ms is not None:
        idx = idx[d1["t"][idx] < hi_ms]
    fwd, fund = {}, {}
    for h in HS:
        fwd[h] = np.log(d1["o"][idx + 1 + h] / d1["o"][idx + 1])
        fund[h] = funding.window(d1["t"], idx + 1, idx + 1 + h)
    return d1, s, ev, idx, fwd, fund


def family(ev, idx, fwd, reps=REPS, seed=SEED):
    EV = np.array([ev[k][idx] for k in NAMES])
    dirs = np.array([T.DIRS2[k] for k in NAMES], dtype=float)
    VAL = np.stack([np.stack([dirs[e] * fwd[h] for h in HS]) for e in range(len(NAMES))])
    rc = S.rc_family(EV, VAL, BLOCK, MIN_N, reps=reps, seed=seed)
    return EV, dirs, rc


def rows_from(EV, dirs, rc, fwd, fund):
    rows = []
    for e, nm in enumerate(NAMES):
        for hi, h in enumerate(HS):
            for orient, osign in (("follow", 1), ("fade", -1)):
                sgn = dirs[e] * osign
                n = int(rc["n"][e])
                live = bool(rc["live"][e])
                r = {"event": nm, "tf": "1d", "h": h, "orient": orient, "sign": int(sgn), "n": n, "live": live}
                if n:
                    nets = sgn * fwd[h] - COST - sgn * fund[h]
                    r["gross_bps"] = float(1e4 * (sgn * fwd[h][EV[e]]).mean())
                    r["net_bps"] = float(1e4 * nets[EV[e]].mean())
                    r["win"] = float((nets[EV[e]] > 0).mean())
                    r["excess_bps"] = float(1e4 * osign * rc["stat"][e, hi])
                    if live:
                        _, lo, hi_ = S.mean_ci(EV[e], nets, BLOCK, reps=REPS, seed=SEED)
                        r["ci_lo_bps"], r["ci_hi_bps"] = 1e4 * lo, 1e4 * hi_
                        r["t"] = float(osign * rc["t"][e, hi])
                        r["p_raw"] = float(rc["p_raw_cont"][e, hi] if osign == 1 else rc["p_raw_rev"][e, hi])
                        r["p_adj"] = float(rc["p_adj_cont"][e, hi] if osign == 1 else rc["p_adj_rev"][e, hi])
                        r["mde_bps"] = float(1e4 * S.mde(float(np.std(fwd[h])), n))
                r["pass"] = bool(live and n and r.get("net_bps", -1) > 0 and r.get("ci_lo_bps", -1) > 0 and r.get("p_adj", 1) < ALPHA and r.get("excess_bps", -1) > 0)
                rows.append(r)
    ps = [r.get("p_raw", 1.0) if r["live"] else 1.0 for r in rows]
    for r, q in zip(rows, S.bh_qvalues(ps)):
        r["q_bh"] = float(q) if r["live"] else None
    return rows


def contrasts(ev, idx, fwd):
    h = 10
    e = {k: v[idx] for k, v in ev.items()}
    r = fwd[h]
    out = []

    def add(label, A, B, val, note):
        c = S.contrast(A, B, val, BLOCK, reps=REPS, seed=SEED)
        c.update({"label": label, "note": note, "h": h})
        out.append(c)

    add("K1", e["MOM_HI"] & e["D20_HI"], e["MOM_HI"] & ~e["D20_HI"], r, "momentum HI: buy-delta HI minus not (long)")
    add("K2", e["MOM_LO"] & e["D20_LO"], e["MOM_LO"] & ~e["D20_LO"], -r, "momentum LO: sell-delta LO minus not (short)")
    add("K3", e["DUS_HI"], e["DAS_HI"], r, "US-hours buy-delta HI minus Asia-hours buy-delta HI (long)")
    qs = S.bh_qvalues([c["p_two"] if c["p_two"] == c["p_two"] else 1.0 for c in out])
    for c, q in zip(out, qs):
        c["q_bh"] = float(q)
        c["supported"] = bool((c["lo"] > 0 or c["hi"] < 0) and q < 0.10) if c["diff"] == c["diff"] else False
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--placebo", type=int, default=20)
    a = ap.parse_args()
    funding = D.Funding()
    d1 = D.load_1d()
    h1 = D.load_1h()
    d1, s, ev, idx, fwd, fund = prepare(d1, h1, funding)
    EV, dirs, rc = family(ev, idx, fwd)
    rows = rows_from(EV, dirs, rc, fwd, fund)
    cs = contrasts(ev, idx, fwd)
    L = []

    def P(x=""):
        L.append(x)

    npass = sum(r["pass"] for r in rows)
    nlive = sum(1 for r in rows if r["live"])
    P("# V2 DEV RESULTS - BTC volume STATE family on daily bars (run %s, DEV)" % RUN_ID)
    P()
    P("Registered in PRE_REG_ADDENDUM_A_2026-10-09.md (commit 6e6227b) before any V2 outcome. %d bars in range (first valid state bar index %d), %d trials (%d live, %d INSUFFICIENT-N), **%d pass triage**." % (
        len(idx), T.W2, len(rows), nlive, len(rows) - nlive, npass))
    P("Entry open(i+1), exit open(i+1+h), net of 14 bp and funding in (entry, exit]. 'follow' = trade in the label direction (HI long / LO short), 'fade' = opposite. Excess = oriented mean fwd | state minus mean fwd | all bars. "
      "Overlap warning: a state lasts many days and a 20-day holding window overlaps its neighbours, so the effective number of independent observations is far below n; block = 40 days handles the inference, MDE below is the naive i.i.d. figure and is optimistic.")
    sdv = {h: float(np.std(fwd[h])) for h in HS}
    P("sd of h-day fwd return: " + ", ".join("h=%d %.0f bp" % (h, 1e4 * sdv[h]) for h in HS) + ". Naive MDE at n=400: " + ", ".join("h=%d %.0f bp" % (h, 1e4 * S.mde(sdv[h], 400)) for h in HS))
    P()
    P("| state | n | " + " | ".join("h=%d follow / fade (excess bp, p_adj)" % h for h in HS) + " |")
    P("|---|---|" + "---|" * len(HS))
    for nm in NAMES:
        cells = []
        n = next(r["n"] for r in rows if r["event"] == nm)
        for h in HS:
            f_ = next(r for r in rows if r["event"] == nm and r["h"] == h and r["orient"] == "follow")
            d_ = next(r for r in rows if r["event"] == nm and r["h"] == h and r["orient"] == "fade")
            if not f_["live"]:
                cells.append("INSUFF")
            else:
                cells.append("%+.0f (%.2f) / %+.0f (%.2f)" % (f_["excess_bps"], f_["p_adj"], d_["excess_bps"], d_["p_adj"]))
        P("| %s | %d | %s |" % (nm, n, " | ".join(cells)))
    P()
    live = sorted([r for r in rows if r["live"]], key=lambda r: r["p_adj"])
    P("### 10 best trials by RC p_adj")
    P()
    P("| state | h | orient | n | gross bp | net bp [95% CI] | win | excess bp | t | p_raw | p_adj | q_BH | triage |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in live[:10]:
        P("| %s | %d | %s | %d | %+.0f | %+.0f [%+.0f, %+.0f] | %.0f%% | %+.0f | %.2f | %.3f | %.3f | %.2f | %s |" % (
            r["event"], r["h"], r["orient"], r["n"], r["gross_bps"], r["net_bps"], r["ci_lo_bps"], r["ci_hi_bps"], 100 * r["win"], r["excess_bps"], r["t"], r["p_raw"], r["p_adj"], r["q_bh"], "PASS" if r["pass"] else "FAIL"))
    P()
    P("### Registered contrasts (h=10, follow-oriented; own BH family of 3)")
    P()
    P("| id | what | nA | nB | mean A bp | mean B bp | diff bp | 95% CI bp | p | q_BH | supported |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cs:
        P("| %s | %s | %d | %d | %+.0f | %+.0f | %+.0f | [%+.0f, %+.0f] | %.3f | %.3f | %s |" % (
            c["label"], c["note"], c["nA"], c["nB"], 1e4 * c["meanA"], 1e4 * c["meanB"], 1e4 * c["diff"], 1e4 * c["lo"], 1e4 * c["hi"], c["p_two"], c["q_bh"], "YES" if c["supported"] else "no"))
    P()
    registry = []
    for r in rows:
        registry.append([RUN_ID, "2026-10-09", "V2-state", r["event"], "1d", r["h"], r["sign"], "DEV", r["n"], "" if "net_bps" not in r else "%.1f" % r["net_bps"],
                         "" if "p_adj" not in r else "%.4f" % r["p_adj"], "PASS" if r["pass"] else ("INSUFFICIENT-N" if not r["live"] else "FAIL")])
    for c in cs:
        registry.append([RUN_ID, "2026-10-09", "V2-contrast", c["label"], "1d", c["h"], 0, "DEV", min(c["nA"], c["nB"]), "%.1f" % (1e4 * c["diff"]), "%.4f" % c["p_two"], "SUPPORTED" if c["supported"] else "NOT-SUPPORTED"])

    if a.placebo:
        P("### Placebo calibration (volume and taker-buy shifted by 42*k days, k distinct in 1..38; family-wise pass = any trial with p_adj < 0.10)")
        P()
        rng = np.random.default_rng(2027)
        hits, trig, lags = [], {}, []
        d1b, h1b = D.load_1d(), D.load_1h()
        ks = rng.choice(np.arange(1, 39), size=a.placebo, replace=False)    # distinct lags (first draft sampled with replacement: 9 values for 20 runs)
        for k, kk in enumerate(ks, start=1):
            lag = int(42 * kk)
            lags.append(lag)
            _, sp, evp, idxp, fwdp, fundp = prepare(d1b, h1b, funding, shift_days=lag)
            EVp, dirsp, rcp = family(evp, idxp, fwdp, reps=500, seed=k)
            live_ = rcp["live"][:, None] & np.ones((1, len(HS)), dtype=bool)
            pmin = np.minimum(np.where(live_, rcp["p_adj_cont"], 1.0), np.where(live_, rcp["p_adj_rev"], 1.0))
            hit = bool((pmin < 0.10).any())
            hits.append(hit)
            if hit:
                e_, _h = np.unravel_index(np.argmin(pmin), pmin.shape)
                trig[NAMES[e_]] = trig.get(NAMES[e_], 0) + 1
            registry.append([RUN_ID, "2026-10-09", "V2-placebo", "family", "1d", 0, 0, "DEV", k, "", "%.4f" % pmin.min(), "HIT" if hit else "clean"])
        rate = float(np.mean(hits))
        P("- %d placebo runs, family-wise pass rate %.2f (expected <= 0.10; miscalibrated if > 0.20) -> **%s**. Triggers: %s. Lags (days): %s" % (a.placebo, rate, "CALIBRATED" if rate <= 0.20 else "MISCALIBRATED", trig or "none", lags))
        P("- Revision note: the first V2 run drew lags WITH replacement from only 9 values (20 runs, pass rate 0.20, all 4 hits on VT_HI, so partly duplicated lags); this is the corrected draw of 20 distinct lags. The 96 trials and every non-placebo number are unchanged.")
        P()
    cands = [r for r in rows if r["pass"]]
    P("### V2 candidates frozen for VALIDATION")
    P()
    if not cands:
        P("**None.** No state x horizon x orientation passes the registered triage on DEV.")
    else:
        P("| state | h | orient | n | net bp [CI] | excess bp | p_adj |")
        P("|---|---|---|---|---|---|---|")
        for r in cands:
            P("| %s | %d | %s | %d | %+.0f [%+.0f, %+.0f] | %+.0f | %.3f |" % (r["event"], r["h"], r["orient"], r["n"], r["net_bps"], r["ci_lo_bps"], r["ci_hi_bps"], r["excess_bps"], r["p_adj"]))
    P()
    (HERE / "V2_DEV_RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    (HERE / "v2_dev_results.json").write_text(json.dumps({"run_id": RUN_ID, "candidates": [{k: (v.item() if isinstance(v, np.generic) else v) for k, v in c.items()} for c in cands],
                                                       "contrasts_supported": [c["label"] for c in cs if c["supported"]]}, indent=1), encoding="utf-8", newline="\n")
    reg = HERE / "TRIAL_REGISTRY.csv"
    with open(reg, "a", newline="", encoding="utf-8") as fh:
        csv.writer(fh, lineterminator="\n").writerows(registry)
    print("wrote V2_DEV_RESULTS.md; candidates", len(cands), "contrasts supported", [c["label"] for c in cs if c["supported"]])


if __name__ == "__main__":
    main()
