PASS STANDS

## Scope

This recheck uses the frozen preregistration and saved outputs only. No backtest or bar data was opened or run, no DEV/VALIDATION/HOLDOUT data was reread, and the original verdict file was not edited.

## Recomputed values

The saved placebo p is `0.023255813953488372 = 7/301` (`MyTradingSys/research/meta_label_dev_ext_2026-10-31/numbers.json:47`; the 300-shuffle rule is in `MyTradingSys/research/meta_label_dev_ext_2026-10-31/PRE_REG_EXT.md:12`). The frozen family size is `m=2` (`PRE_REG_EXT.md:13`). `run_ext.py:94` passes `[p,p]` to BH, so it duplicates the one observed p-value; `analyze.py:98-106` confirms that this returns `q=p`, matching the saved `numbers.json:501-502`.

With the available nonpassing comparison `p=0.60` (`MyTradingSys/research/meta_label_dev_ext_2026-10-31/RESULT.md:19`), BH for the smaller p is `min(2 × 0.023255813953488372, 0.60) = 0.046511627906976744`. This is also the conservative m=2 upper adjustment `2p`; the extension files do not save a separate extension-window second p-value, so `0.046512` is the conservative correction, not a newly observed exact family q. It matches the saved Holm adjustment (`numbers.json:500`). BH is reported beside the frozen rule and is not a pass criterion (`PRE_REG_EXT.md:13,18`).

The saved realized power inputs are `n_top=139` and `delta_min=0.509289099934907 R` (`numbers.json:10,50`). Reversing `delta_min = sd × sqrt(7.849/n_top)` gives `sd=2.143209456617 R`; then `ceil(7.849 × (2.143209456617/0.30)^2)=401`, matching `n_needed_for_0p30R_lift=401` (`numbers.json:201`; formula and 0.30 R target: `PRE_REG_EXT.md:21`). The preregistered prior `sd=2.3817 R` instead gives `ceil(7.849 × (2.3817/0.30)^2)=495` (`PRE_REG_EXT.md:21`). Both floors exceed 139.

## Frozen-rule decision

`PRE_REG_EXT.md:18` defines NOT ENOUGH DATA as fewer than 100 top-tercile trades, **or** a 95% CI spanning zero while `n_top<n_need`. The count is 139 (`numbers.json:10`), so the first condition is false. The saved 95% CI is `[+0.028402,+0.869065] R` (`numbers.json:31-34`), so it does not span zero and the conditional power-floor branch is false despite `139<401`.

All three frozen PASS conditions hold: top mean `+0.429609 R > 0` (`numbers.json:14`); 95% CI lower bound `+0.028402 R > 0` (`numbers.json:31-34`); and spread `+0.644763 R` exceeds placebo p95 `+0.521435 R` (`numbers.json:39,45`). Thus the literal frozen classification is **PASS STANDS** (`PRE_REG_EXT.md:18`; `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/analyze.py:228-231`). The 97.5% interval spans zero and the 0.30 R lift remains unresolved, but neither substitutes for the specified 95% CI test (`numbers.json:35-38`; `RESULT.md:17,23-24`).

This is only the preregistered pre-DEV hypothesis, not confirmation or permission to revive the setup. The existing action keeps it parked and says the evidence is not confirmed (`PRE_REG_EXT.md:18`; `RESULT.md:30-31`). No validation or holdout read was made.
