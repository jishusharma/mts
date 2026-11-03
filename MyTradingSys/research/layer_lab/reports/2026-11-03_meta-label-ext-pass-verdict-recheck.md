# Recheck report: meta-label extension PASS under frozen rule

- Card: `meta-label-ext-pass-verdict-recheck` (CODEX, claimed after fresh READY and no-claim checks).
- Verdict in `RECHECK.md`: `PASS STANDS` under the literal frozen preregistration.
- Method: recomputed from saved outputs and preregistration only; no new backtest, bars, validation/holdout read, or verdict-file edit.

BH detail: `run_ext.py:94` duplicates the only observed p-value for both family entries, producing the saved `q=0.023256`. With the available nonpassing companion `p=0.60` (`RESULT.md:19`), m=2 BH gives `q=0.046512`; absent a second extension p-value this is the conservative correction. The family size and reporting-only role are specified in `PRE_REG_EXT.md:13,18`; algorithm in `analyze.py:98-106`; saved p/adjustments in `numbers.json:47,500-502`.

Power detail: `n_top=139`, `delta_min=0.509289 R`; reversing the delta formula gives `sd=2.143209 R`, and the frozen 0.30 R formula gives `n_need=401` (saved field `numbers.json:10,50,201`; formula `PRE_REG_EXT.md:21`). The prior SD gives 495. The NOT ENOUGH DATA branch requires CI spanning zero in addition to `n_top<n_need`; the 95% interval is `[+0.028402,+0.869065] R` (`PRE_REG_EXT.md:18`; `numbers.json:31-34`). Top mean `+0.429609 R` and spread `+0.644763 R` over placebo p95 `+0.521435 R` complete the frozen PASS criteria (`numbers.json:14,39,45`). The literal verdict therefore stands, while the report's evidence remains an unconfirmed pre-DEV hypothesis and the setup remains parked (`RESULT.md:30-31`).
