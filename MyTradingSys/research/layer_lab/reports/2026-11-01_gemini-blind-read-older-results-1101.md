FOUND: 844, NOT_IN_DATA: 31, DIFF: 1 (counts are numeric tokens in the result files)

# Blind re-read: five older result files (independent, DSA direct 2026-11-02)

Method: script (chk.py in session scratchpad) extracts every numeric token from each RESULT/REPORT .md (skipping code spans, dates, hashes, clock times) and tests it against all numbers in the cited json/txt, allowing x1, x100, /100 scaling and tolerance of half the last printed decimal. Unmatched tokens were then opened by hand. Weakness stated: this is a value-level match (a token passes if any number in the source rounds to it), not a cell-by-cell join; small integers (<10) match trivially. DIFF and NOT_IN_DATA lines were verified by hand with the commands noted. Earlier Gemini file older_results_blind_read.md was not used.

| file | cited sources | FOUND | NOT_IN_DATA | DIFF | notes |
|---|---|---|---|---|---|
| setup_alpha_beta_v2_2026-10/RESULT.md | result_numbers.json; PRE_REG.md; setup_alpha_beta_2026-10-10/BETA_RESULTS.md:9 | 131 | 4 | 1 | DIFF: RESULT.md:11 prints Alpha DEV mean R 6.178 but result_numbers.json alpha.DEV.alpha.mean_R = 6.178972980370181 (rounds 6.179; the same file's table at line 25 prints 6.18). NOT_IN_DATA (4, design parameters from PRE_REG.md, not result data): `8` Beta cells at :5, `90` min bracket at :18, `8`-bar window and `90` min stop at :49. FOUND includes 708,240 = BETA_RESULTS.md:9 (v1 Beta n 708240). |
| us_open_levels_2026-10-30/RESULT.md | results.json | 240 | 0 | 0 | all 240 numeric tokens matched a value in results.json. |
| us_open_oos_2026-10-30/REPORT.md | results_oos_2020_2021.json + session_sweeps/results_2026-10-04.json (the 2022-26 'orig' columns) | 93 | 0 | 0 | the 2022-26 columns (0.498, 0.494, 1.92x, 1,178 days ...) are in session_sweeps/results_2026-10-04.json, not in the OOS json; 1,052,640 bars = 731 days x 1440 (computed) for the 24 monthly files 2020-01..2021-12. |
| wt30_sequence_2026-10-30/RESULT.md | output.txt | 201 | 19 | 0 | FOUND includes 'about 2.3 points at n=465' = sqrt(.25/465)=2.32 pts (computed). NOT_IN_DATA (19): date ranges (10-22 to 10-30), live price/oscillator readings from the operator screenshots (77,436; 81,089; -55.7; -26.9; -37.9 ...), design labels (<= 16 bars, 1,100, 2.5 years); output.txt holds none of them. |
| tom_transfer_2026-10-11/vp_return/RESULT.md | results.json | 179 | 8 | 0 | NOT_IN_DATA (8): labels not results: CI level 95, shift label 18.6 (placebo definition), table-year 2023, band headers -3.0/+3.0, TOM-281, column ids. |
