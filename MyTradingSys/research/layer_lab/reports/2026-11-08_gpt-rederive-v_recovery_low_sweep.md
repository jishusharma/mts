MATCH=3 DIFF=0 NOT_IN_DATA=1 (RESULT.md headline numbers; supplementary PRE_REG numbers: MATCH=0 DIFF=6, see below)

# Re-derivation: v_recovery_low_sweep_2026-11-04/RESULT.md
Run 2026-11-12 by gemini (Antigravity), card gpt-rederive-v-recovery-low-sweep-1108. Reads only; no source file edited. Model output is not a source.

## RESULT.md numbers
| # | RESULT.md claim | Recomputed | Status | How |
|---|---|---|---|---|
| 1 | 435 events | 435 | MATCH | `counts.json` and `study.py --pass count` both print 435. Caveat: this reruns the study code; an independent bar-level recount needs the BTCUSDT 1h DEV data (not in this tree), so the event rule itself is NOT independently re-checked |
| 2 | 195 event-days | 195 | MATCH | same as above, same caveat |
| 3 | prereg_gate exit 1 at 4h/24h/72h | exit 1 at sd 1.1/2.5/4.3 (n=195, cost 0.14, new-cells 3) | MATCH | `prereg_gate.py` rerun, all three BLOCK |
| 4 | Regime mix NOT_IN_DATA | no regime spec in the folder | NOT_IN_DATA | |

## Supplementary (PRE_REG.md Resolution / BLOCKED.md, not RESULT.md)
Rerun today: `prereg_gate.py --n 195 --sd {1.1,2.5,4.3} --cost 0.14 --m auto --new-cells 3`. `--m auto` now returns m=251, z_holm 3.720 (written: m=224, z_holm 3.691), so every value moved.
| Horizon | Written MDE+cost / n needed | Rerun MDE+cost / n needed | Status |
|---|---|---|---|
| 4h | 0.497 / 970 | 0.499 / 983 | DIFF |
| 24h | 0.951 / 5013 | 0.956 / 5077 | DIFF |
| 72h | 1.535 / 14829 | 1.544 / 15019 | DIFF |
Cause (stated, not proven by a git bisect): `m auto` depends on the repo's trial ledger, which has grown since 2026-11-06. The BLOCK verdict and the INCONCLUSIVE conclusion are unchanged at both m values.

## Second recount, 2026-11-14 (Sonnet builder, edge-batch3-1114): gate numbers by hand, written m held fixed
Not from `study.py` or the gate's output: `counts.json` (435 events, 195 days: MATCH) and the gate's documented formula `z_holm = Phi^-1(1 - 0.05/(2m))`, `MDE = (z_holm + 0.84) sd / sqrt(n)`, `n needed = ((z_holm + 0.84) sd / (0.30 - 0.14))^2` (printed rounded), computed with `statistics.NormalDist`. With the m = 224 written in PRE_REG.md held fixed: z_holm 3.691 MATCH; MDE + cost 0.497 / 0.951 / 1.535 MATCH; n needed 970 / 5013 / 14829 MATCH; all three exceed 0.30 R, so BLOCK MATCH. So the six DIFF rows above come only from `m auto` drifting 224 -> 251 as the trial ledger grew, not from an arithmetic error in the PRE_REG; m = 224 itself stays NOT_IN_DATA (the 2026-11-06 ledger is not in the folder). Nothing else changed; no returns computed.
