"""Critical test wave 2 item 8: trial count vs Minimum Backtest Length (MinBTL) per layer verdict.

MinBTL (Bailey, Borwein, Lopez de Prado, Zhu 2014, "Pseudo-mathematics and financial charlatanism", eq. for
E[max] of N iid standard normals): E[max_N] ~ (1 - g) Z(1 - 1/N) + g Z(1 - 1/(N e)), g = Euler-Mascheroni;
MinBTL(N) ~ (E[max_N] / SR)^2 years. Budget for a dev window of Y years = largest N with MinBTL(N) <= Y.
For each verdict row in system/layer_map.json: trials read by hand from its n / verdict text (TRIALS below,
None = the row does not record a trial count), the annual Sharpe a best-of-N needs to clear noise on Y years
(E[max_N] / sqrt(Y)), and whether a pass still stands (then a deflated Sharpe >= 0.95 is required).
Run: python MyTradingSys/research/critical_test_wave2_2026-10-30/item8_minbtl.py
"""
import json
import math
import sys
from statistics import NormalDist
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "item8_minbtl.tsv"
GAMMA = 0.5772156649015329
DEV_YEARS = 2.5          # SOURCED: backtest/splits.py DEV 2022-01-01..2024-07-01
SR_REF = 1.0             # SOURCED: CRITICAL_TEST_PLAN.md item 8 ("Sharpe 1")
Z = NormalDist().inv_cdf
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest"))
import fees  # noqa: E402

# trials per row, read from the row's n / verdict text (layer_map.json, read 2026-11-05); None = not recorded
TRIALS = {
    "RSI-DEEP-PRESTUDIES": 662, "Q33": 186, "VOLUME": 553, "RSI-DIV-MTF": 32, "TOM-VP-PHASE2": 48,
    "VOL-V1": 216, "VOL-V2": 96, "VOL-V3": 1, "VOL-V4": 1, "T055-C1": 1, "T055-C2": 1, "T055-C3": 1,
    "PITCHFORK-1D-20261019": None, "PITCHFORK-4H-VP-20261028": 3, "BIGTRADE-EXIT": 54,
    "L1-D3": 80,   # BACKTEST_L1_REPORT.md: 10 tolerances x 4 TF x 2 levels (x 5 horizons not counted)
}
STANDING_PASS = {"L1-D3": "1h support PBO 0.030, GROSS only: OOS +0.043%/trade < Deribit taker round trip"}


def e_max(n):
    if n <= 1:
        return 0.0
    return (1 - GAMMA) * Z(1 - 1 / n) + GAMMA * Z(1 - 1 / (n * math.e))


def min_btl(n, sr=SR_REF):
    return (e_max(n) / sr) ** 2


def budget(years, sr=SR_REF):
    n = 1
    while min_btl(n + 1, sr) <= years:
        n += 1
    return n


def main():
    rows = json.loads((REPO / "MyTradingSys/system/layer_map.json").read_text(encoding="utf-8"))["backtests"]
    b = budget(DEV_YEARS)
    lines = ["id\tlayers\ttrials\tdev_years\tminbtl_budget_sr1\tsr_needed_best_of_n\tover_budget\tstanding_pass\tdsr"]
    over = rec = 0
    for r in rows:
        n = TRIALS.get(r["id"])
        need = e_max(n) / math.sqrt(DEV_YEARS) if n else None
        ob = n is not None and n > b
        over += ob
        rec += n is not None
        sp = STANDING_PASS.get(r["id"], "")
        lines.append("\t".join([r["id"], ",".join(r["layers"] or []), "not recorded" if n is None else str(n),
                                str(DEV_YEARS), str(b), "" if need is None else f"{need:.2f}", "yes" if ob else "",
                                sp, "MISSING" if sp else ""]))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"rows {len(rows)}; trials recorded {rec}; over MinBTL budget {over}; budget N={b} at SR {SR_REF} on "
          f"{DEV_YEARS} y; check N=7 -> {min_btl(7):.2f} y, N=553 needs SR {e_max(553) / math.sqrt(DEV_YEARS):.2f}; "
          f"standing passes {len(STANDING_PASS)} (DSR recorded 0); L1-D3 1h OOS fee-net "
          f"{0.043 - 2 * fees.DERIBIT_TAKER * 100:+.3f}%/trade")


if __name__ == "__main__":
    main()
