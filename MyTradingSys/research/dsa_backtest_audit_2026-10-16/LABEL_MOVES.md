# LABEL_MOVES: family-wise correction before a PASS (T10-F1, card g5-screens-family-wise-correction-across)

## Correction rule (written before any rerun)

- Family = every distinct (study, arm) variant read on DEV. m = 90 (OURS, `python scripts/dev/verdicts.py count --split DEV` on 2026-11-01; 90 variants from 23 studies, a lower bound because secondary cells and variant grids are not counted). Constant `M_FAMILY` in `gross_effect_screen_2026-10-15/screen.py`.
- Method: Holm step-down over the one-sided t tests, family alpha = 0.05 (OURS; the nominal single test is t >= 2, one-sided p = 0.0228). A verdict gates on one arm, so it uses Holm's first step, the Bonferroni bar: `t_bar(m) = max(2.0, q)`, q = z(1 - 0.05/m) + (z^3+z)/(4*199) (Student-t quantile, df = N_MIN-1 = 199, Cornish-Fisher; no scipy). Values: m=1 -> 2.000 (never looser than the pre-registered bar), m=12 -> 2.664, m=40 -> 3.062, m=90 -> 3.308. `holm_reject(pvals)` is provided for a list of arms.
- Both t_cost (`t_net`) and t_DIFF must clear `t_bar(m)`. The other PASS terms (n >= 200, mean >= 0.14 %, DIFF >= +0.05 %, MDD <= BH MDD) are unchanged and are the pre-registered bars; none is edited.
- Label: an arm that clears the nominal bars but not the corrected bar is INCONCLUSIVE (not FAIL: the data cannot separate it from a K-arm null). `verdict_uncorrected` is kept beside `verdict` in screen.evaluate and common.verdict_arm.
- No ledger row, RESULT.md or published verdict is edited.

## Placebo test (no data needed)

`test_screen.py::test_placebo_family`: K=12 and K=40 iid zero-mean arms (n=200, sd=1, 2000 seeds). Old rule (t >= 2): about 24 % and 60 % of seeds pass (T10 D3 reported 23.8 % and 60.5 %). New rule: <= 5 %.

## Past labels that move

Computed from the stored result tables only (no rerun: F:/MTS/data is absent on this host, so NOT MEASURED for any rerun, including T10 D3).

| study | arm | old label | t_net / t_DIFF in RESULT.md | new label |
|---|---|---|---|---|
| gross_effect_screen | T (d=1,h=60) | INCONCLUSIVE | -1.51 / -0.37 | unchanged |
| mal_bb_mid_engulf | A1, A2 | FAIL, FAIL | -6.02 / 0.61, -4.89 / -0.54 | unchanged |
| opr_bb_mtf_center | AU, AD | INCONCLUSIVE, FAIL | -1.46 / 0.04, -2.71 / 1.56 | unchanged |
| opr_preopen_tops | H1, H2 | INCONCLUSIVE, INCONCLUSIVE | -1.63 / 0.57, -1.26 / -0.18 | unchanged |
| opr_weekly_low_round_sweep | RL, AS | FAIL, FAIL | -3.23 / 0.48, -3.87 / -0.19 | unchanged |

No PASS_FLOW, PASS_CONTROL or KEEP exists in these five DEV screens (every t_net < 2), and the correction only raises the PASS bar, so no label moves. PASS or KEEP labels held elsewhere (layer ledgers, other audits) were not enumerated here: NOT MEASURED.
