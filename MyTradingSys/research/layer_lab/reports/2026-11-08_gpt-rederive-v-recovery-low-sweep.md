COUNTS: MATCH=3 DIFF=0 NOT_IN_DATA=1

# Re-derivation: v_recovery_low_sweep_2026-11-04/RESULT.md
Run 2026-11-13 by gemini (Antigravity), card gpt-rederive-v-recovery-low-sweep-1108. Reads only; no source file edited. Model output is not a source.

## RESULT.md numbers
| # | RESULT.md claim | Recomputed | Status | How |
|---|---|---|---|---|
| 1 | 435 events | 435 | MATCH | `counts.json` records 435 events. |
| 2 | 195 event-days | 195 | MATCH | `counts.json` records 195 event-days. |
| 3 | prereg_gate exit 1 at 4h/24h/72h | exit 1 at sd 1.1/2.5/4.3 (n=195, cost 0.14, new-cells 3) | MATCH | `prereg_gate.py` recomputed with FORMULAS.md power gate logic, all three horizons return exit code 1 (BLOCK). |
| 4 | Regime mix NOT_IN_DATA | no regime spec in the folder | NOT_IN_DATA | Descriptive study, no regime specification or regime data present in folder. |

## Supplementary (PRE_REG.md Resolution / BLOCKED.md, not RESULT.md)
Rerun with current repo ledger: `prereg_gate.py --n 195 --sd {1.1,2.5,4.3} --cost 0.14 --m auto --new-cells 3`. Current repo `--m auto` evaluates to m=251, z_holm=3.720 (original written m=224, z_holm=3.691):
| Horizon | Written MDE+cost / n needed | Current MDE+cost / n needed | Status |
|---|---|---|---|
| 4h | 0.497 / 970 | 0.499 / 983 | DIFF |
| 24h | 0.951 / 5013 | 0.956 / 5077 | DIFF |
| 72h | 1.535 / 14829 | 1.544 / 15019 | DIFF |

Cause: `m auto` depends on the repo's trial ledger, which has grown since 2026-11-06. The BLOCK verdict (exit 1) and INCONCLUSIVE conclusion remain unchanged at both m values.
