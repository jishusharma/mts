MATCH=43 DIFF=0 NOT_IN_DATA=7

# Re-derive: malkan_window_wide RESULT.md (strength 3, DEV count + power gate)

Source: `MyTradingSys/research/malkan_window_wide_2026-11/{counts.csv,gate_lines.csv,symbols.json,regime_mix_count.txt}`, RESULT.md, PRE_REG.md. Recomputed with an independent script (csv + `statistics.NormalDist`, not wide.py). The MDE formula is OURS (`scripts/dev/prereg_gate.py:5,29-30`, 0.84 = 80 % power OURS); FORMULAS.md has no MDE section (grep MDE/Holm/prereg: no hit). Tolerance for MDE: 0.001 (published sd has 3 decimals).

| Number | RESULT | Recomputed | Status | Note |
|---|---|---|---|---|
| n events 1h S3_10 | 2359 | 2359 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 1h B11_12 | 443 | 443 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 1h C13_18 | 487 | 487 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 1h D19_50 | 140 | 140 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 4h S3_10 | 599 | 599 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 4h B11_12 | 116 | 116 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 4h C13_18 | 158 | 158 | MATCH | sum of bullish+bearish n, counts.csv |
| n events 4h D19_50 | 38 | 38 | MATCH | sum of bullish+bearish n, counts.csv |
| days 1h S3_10 | 2119 | gate_lines 2119; side-sum 2147 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 1h B11_12 | 432 | gate_lines 432; side-sum 433 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 1h C13_18 | 479 | gate_lines 479; side-sum 479 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 1h D19_50 | 140 | gate_lines 140; side-sum 140 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 4h S3_10 | 591 | gate_lines 591; side-sum 591 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 4h B11_12 | 116 | gate_lines 116; side-sum 116 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 4h C13_18 | 158 | gate_lines 158; side-sum 158 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| days 4h D19_50 | 38 | gate_lines 38; side-sum 38 (pooled must be <= side-sum) | MATCH | pooled distinct symbol x day not derivable from counts.csv; only transcription and bound checked |
| sd % (10-bar) 1h | 2.795 | - | NOT_IN_DATA | needs raw 1m/1h bars; only gate_lines.csv holds it |
| sd % (10-bar) 4h | 5.454 | - | NOT_IN_DATA | needs raw 1m/1h bars; only gate_lines.csv holds it |
| MDE+cost 1h S3_10 | 0.416 | 0.4161 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 1h B11_12 | 0.751 | 0.7514 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 1h C13_18 | 0.721 | 0.7206 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 1h D19_50 | 1.214 | 1.214 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 4h S3_10 | 1.16 | 1.16 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 4h B11_12 | 2.443 | 2.4423 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 4h C13_18 | 2.113 | 2.1127 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| MDE+cost 4h D19_50 | 4.163 | 4.1626 | MATCH | (z+0.84)*sd/sqrt(days)+0.14, z=Phi^-1(1-0.05/476)=3.7066, sd as published |
| prereg_gate 1h S3_10 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 1h B11_12 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 1h C13_18 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 1h D19_50 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 4h S3_10 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 4h B11_12 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 4h C13_18 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| prereg_gate 4h D19_50 | BLOCK | BLOCK | MATCH | rule MDE+cost > 0.30 |
| OURS 1h events (1070) | 1070 | 1070 | MATCH | B+C+D sum |
| OURS 4h events (312) | 312 | 312 | MATCH | B+C+D sum |
| prior 4 events (BTC+ETH, strength 1) | 4 | - | NOT_IN_DATA | other study output not in scope |
| Holm m = 222+16 = 238 | 238 | 16 = 4 bands x 2 TF x 2 sides = 16; 222+16 = 238 | MATCH | the 222 repo-wide DEV count is NOT_IN_DATA; the sum is arithmetic only |
| repo-wide DEV count 222 | 222 | - | NOT_IN_DATA | needs verdicts.py |
| cost 0.14 % | 0.14 | - | NOT_IN_DATA | PRE_REG cites research_kit.TAKER_RT_PCT; 0.10 fee part from fees.py not read |
| MDE rule 0.30 % ceiling | 0.3 | PRE_REG: prereg_gate MAX_PLAUSIBLE_GROSS 0.30 | MATCH | OURS threshold, restated |
| exit 10 bars | 10 | PRE_REG: 10 | MATCH | parameter text |
| DEV bars 1h (21888 = 912 d x 24) | 21888 | 21888 | MATCH | 2022-01-01..2024-07-01 = 912 days |
| bars 1h SOL/XRP/LTC 21768 | 21768 | 21888-120 | NOT_IN_DATA | 120-bar gap (5 days) cause needs raw files |
| bars floor 7200; all 10 above | 7200 | min 21768 | MATCH | symbols.json 10 x ok true |
| symbols loaded 10 | 10 | 10 | MATCH | symbols.json |
| weeks 130 | 130 | 912/7=130.29 | MATCH | floor/whole weeks |
| weeks bull 25, bear 0, range 105, n/a 0 | 130 | 130 | MATCH | sum=130; 25/130=19.2 %, 105/130=80.8 % -> 19/81; per-class assignment NOT_IN_DATA |
| verdict BLOCKED | BLOCKED | all 8 cells BLOCK | MATCH |  |
| dev pass not run, no return read | 0 | - | NOT_IN_DATA | no output file to check absence beyond csvs |

**Observation (OURS)**: 4h B11_12 MDE+cost 2.4423 vs published 2.443 (diff 0.0007), beyond sd rounding alone (about 0.0002); accepted as MATCH at the 0.001 tolerance.

No source file edited. No bars read.
