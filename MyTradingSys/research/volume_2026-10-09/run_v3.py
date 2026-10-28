"""V3: VALIDATION (2024-07-01 .. 2025-06-30), run once, frozen candidates only (PRE_REG_ADDENDUM_A_2026-10-09.md A1).
Candidates: R40D_N 4h h=6 REVERSAL (long); TH1 (SP3 session C minus A, 4h, h=18). HOLDOUT is never loaded.
Run: python MyTradingSys/research/volume_2026-10-09/run_v3.py   -> V3_VALIDATION_RESULTS.md, appends TRIAL_REGISTRY.csv
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

RUN_ID = "V3-2026-10-09"
COST = 2 * (0.0005 + 0.0002)
BLOCK = 60
MIN_N = 100


def window_idx(b, h, lo_ms):
    n = len(b["c"])
    idx = np.arange(F.W, n - 1 - h)
    return idx[b["t"][idx] >= lo_ms]


def main():
    funding = D.Funding()
    b = D.load_4h(start_ms=D.START_MS, end_ms=D.VALID_END_MS)        # DEV + VALIDATION for warm-up; never beyond VALID_END_MS
    f = F.features(b, "4h")
    ev = F.events(b, f)
    L = []
    P = L.append
    reg = []
    P("# V3 VALIDATION RESULTS (2024-07-01 .. 2025-06-30, run once; HOLDOUT never loaded)")
    P("")
    P("Frozen in PRE_REG_ADDENDUM_A_2026-10-09.md (commit 6e6227b). Features computed on DEV+VALIDATION concatenated for warm-up; events and baselines restricted to bars opening on/after 2024-07-01; forward windows end by 2025-06-30.")
    P("")
    # candidate 1
    h = 6
    idx = window_idx(b, h, D.DEV_END_MS)
    fwd = np.log(b["o"][idx + 1 + h] / b["o"][idx + 1])
    fund = funding.window(b["t"], idx + 1, idx + 1 + h)
    e = ev["R40D_N"][idx]
    n = int(e.sum())
    sgn = -F.DIRS["R40D_N"]                                   # reversal orientation = +1 (long)
    nets = sgn * fwd - COST - sgn * fund
    P("## Candidate 1: R40D_N, 4h, h=6, reversal (long after RSI(14) crosses down through 40 on RVadj < 1.5)")
    P("")
    if n:
        m_, lo, hi = S.mean_ci(e, nets, BLOCK, reps=1000, seed=12345)
        EV = e[None, :]
        VAL = (F.DIRS["R40D_N"] * fwd)[None, None, :]
        rc = S.rc_family(EV, VAL, BLOCK, 1, reps=1000, seed=12345)
        excess = float(1e4 * -rc["stat"][0, 0])
        p = float(rc["p_raw_rev"][0, 0])
        gross = float(1e4 * (sgn * fwd[e]).mean())
        win = float((nets[e] > 0).mean())
        P("| n events | gross bp | net bp [95% CI] | win | excess bp vs all bars | one-sided p | min n (registered) |")
        P("|---|---|---|---|---|---|---|")
        P("| %d | %+.0f | %+.0f [%+.0f, %+.0f] | %.0f%% | %+.0f | %.3f | %d |" % (n, gross, 1e4 * m_, 1e4 * lo, 1e4 * hi, 100 * win, excess, p, MIN_N))
        passed = n >= MIN_N and m_ > 0 and lo > 0 and p < 0.10 and excess > 0
        verdict = "PASS" if passed else ("INSUFFICIENT-N (n < %d: registered rule cannot be met; numbers shown for information, candidate stays an unvalidated hypothesis)" % MIN_N if n < MIN_N else "FAIL")
        P("")
        P("Verdict: **%s**" % verdict)
        reg.append([RUN_ID, "2026-10-09", "V3-valid", "R40D_N", "4h", h, int(sgn), "VALID", n, "%.1f" % (1e4 * m_), "%.4f" % p, verdict.split(" ")[0]])
        # descriptive: the same DEV event density
        P("")
        P("DEV had 189 such events in 4.5 years (about 42 per year); VALIDATION has %d in 1 year." % n)
    else:
        P("No events.")
        verdict = "INSUFFICIENT-N"
    P("")
    # candidate 2: TH1
    h2 = 18
    idx = window_idx(b, h2, D.DEV_END_MS)
    fwd2 = np.log(b["o"][idx + 1 + h2] / b["o"][idx + 1])
    keys = F.slot_keys(b, "4h")
    sg = keys["sg"][idx]
    e2 = {k: v[idx] for k, v in ev.items()}
    ind = e2["SP3_UP"] | e2["SP3_DN"]
    val = np.where(e2["SP3_UP"], fwd2, np.where(e2["SP3_DN"], -fwd2, 0.0))
    c = S.contrast(ind & (sg == 2), ind & (sg == 0), val, BLOCK, reps=1000, seed=12345)
    P("## Candidate 2: TH1 replication - SP3 spike continuation return (h=18), session C (16-24 UTC) minus session A (00-08 UTC)")
    P("")
    P("| nC | nA | mean C bp | mean A bp | diff bp | 95% CI bp | p |")
    P("|---|---|---|---|---|---|---|")
    P("| %d | %d | %+.0f | %+.0f | %+.0f | [%+.0f, %+.0f] | %.3f |" % (c["nA"], c["nB"], 1e4 * c["meanA"], 1e4 * c["meanB"], 1e4 * c["diff"], 1e4 * c["lo"], 1e4 * c["hi"], c["p_two"]))
    rep = bool(c["diff"] < 0 and c["hi"] < 0)
    P("")
    P("DEV: diff -178 bp, CI [-344, -20] (C mean -40, A mean +138). Replicated only if the CI excludes 0 with diff < 0: **%s**" % ("REPLICATED" if rep else "NOT REPLICATED"))
    reg.append([RUN_ID, "2026-10-09", "V3-valid-contrast", "TH1", "4h", h2, 0, "VALID", min(c["nA"], c["nB"]), "%.1f" % (1e4 * c["diff"]), "%.4f" % c["p_two"], "REPLICATED" if rep else "NOT-REPLICATED"])
    P("")
    (HERE / "V3_VALIDATION_RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "TRIAL_REGISTRY.csv", "a", newline="", encoding="utf-8") as fh:
        csv.writer(fh, lineterminator="\n").writerows(reg)
    print("\n".join(L))


if __name__ == "__main__":
    main()
