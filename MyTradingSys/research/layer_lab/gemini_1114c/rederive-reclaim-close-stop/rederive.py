"""Blind re-derivation of reclaim_close_stop_2026-11 headline verdict and summary stats
from PRE_REG.md rules and results_DEV.csv (without reading RESULT.md).
"""
import csv
import os

STUDY_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'reclaim_close_stop_2026-11')
)
CSV_PATH = os.path.join(STUDY_DIR, 'results_DEV.csv')

FEE_RT_PCT = 0.10  # SOURCED: PRE_REG.md:15 (BINANCE_TAKER 0.0005 per side, round trip 0.10 %)


def prereg_verdict(n, ci_lo, ci_hi):
    """Apply PRE_REG.md:21 rule: n < 100 -> INCONCLUSIVE; else CI upper < 0 FAIL; CI lower > 0 PASS; else INCONCLUSIVE."""
    if n < 100:
        return 'INCONCLUSIVE'
    if ci_hi < 0:
        return 'FAIL'
    if ci_lo > 0:
        return 'PASS'
    return 'INCONCLUSIVE'


def main():
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    by_key = {(r['tf'], r['arm']): r for r in rows}

    for tf in ('4h', '1D'):
        r_all = by_key[(tf, 'all')]
        r_low = by_key[(tf, 'low')]
        r_high = by_key[(tf, 'high')]

        n_low = int(r_low['n'])
        n_high = int(r_high['n'])
        n_all_calc = n_low + n_high
        n_all_csv = int(r_all['n'])

        gross_calc = (n_low * float(r_low['gross_pct']) + n_high * float(r_high['gross_pct'])) / n_all_calc
        net_calc = (n_low * float(r_low['net_pct']) + n_high * float(r_high['net_pct'])) / n_all_calc
        net_from_fee = float(r_all['gross_pct']) - FEE_RT_PCT
        win_calc = (n_low * float(r_low['win_pct']) + n_high * float(r_high['win_pct'])) / n_all_calc
        stop_calc = (n_low * float(r_low['stop_share']) + n_high * float(r_high['stop_share'])) / n_all_calc
        hold_calc = (n_low * float(r_low['mean_hold']) + n_high * float(r_high['mean_hold'])) / n_all_calc

        ci_lo = float(r_all['ci_lo'])
        ci_hi = float(r_all['ci_hi'])
        verdict_calc = prereg_verdict(n_all_calc, ci_lo, ci_hi)

        print(f"=== {tf} (all) ===")
        print(f"  n:          recomputed={n_all_calc} (low={n_low} + high={n_high}), csv={n_all_csv}")
        print(f"  gross_pct:  recomputed={gross_calc:.4f}%, csv={float(r_all['gross_pct']):.4f}%")
        print(f"  net_pct:    recomputed={net_calc:.4f}% (gross-fee={net_from_fee:.4f}%), csv={float(r_all['net_pct']):.4f}%")
        print(f"  ci_95:      [{ci_lo:.4f}%, {ci_hi:.4f}%]")
        print(f"  win_pct:    recomputed={win_calc:.4f}%, csv={float(r_all['win_pct']):.4f}%")
        print(f"  stop_share: recomputed={stop_calc:.4f}, csv={float(r_all['stop_share']):.4f}")
        print(f"  mean_hold:  recomputed={hold_calc:.4f}, csv={float(r_all['mean_hold']):.4f}")
        print(f"  verdict:    recomputed={verdict_calc}, csv={r_all['verdict']}")


if __name__ == '__main__':
    main()
