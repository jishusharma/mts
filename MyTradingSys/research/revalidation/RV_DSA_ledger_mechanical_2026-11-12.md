# RV-DSA ledger mechanical check + layer index path audit (host=JIS-NUC)

Card: rv-dsa-ledger-mechanical (state was `refined`; `tasks.py take` refused: only a ready card can be taken, so the card was NOT claimed and NOT moved to done).
Run by: haiku-nuc-dsa-runner (no DSA chat, no AIBridge), checkout origin/fast-track 4066be7a8. Read-only: no code or ledger edits.
Checker: scratchpad `ledger_check.py` (output `ledger_check_out.txt`).

## RV01 check 1 (mechanical) - TOM_TRADE_LEDGER.csv
- rows 39, canonical groups 12 (CSV n_rows agree with ledger rows for all 12)
- 1a date not ISO-parseable (prose or invalid): 0
- 1b ISO date while trade_date_status is NOT_IN_DATA / ASSUMED / UNRESOLVED: 0
- 1c canonical groups with more than one distinct ISO date: 0
- 1d ENTRY geometry (short: target < entry < stop; long: stop < entry < target): 10 checked, 0 violations, 1 unparseable (T6: stop and target `n/s`, entry 25344)
- 1e group n_rows mismatches: 0
- 1f frame pointers: 70 checked, 0 real misses. The checker flagged 6, but on inspection: 3 are bare filenames that resolve in the frames folder (n7ZSkjb7JXs_0680.jpg, ujedEcmvBMk_0168.jpg, zQTbdEweG3c_0465.jpg), 1 sheet exists (ujedEcmvBMk_02.jpg), and 2 are non-path text (NOT_IN_DATA, a `(cells t=...)` note).

Note: the check passes on structural rules only. It does not settle RV01 checks 2-4 (chart provenance, repair fidelity, counts text), which need frame reading.

## Path audit
- system/layer_index.json: 93 path strings, 0 missing.
- system/layer_map.json: 58 path strings, 14 missing (not in this repo):
  backtest/layers/cryptocred/, backtest/layers/fabio/fabio_cvd_absorption.py, backtest/layers/fabio/fabio_escalation.py,
  backtest/layers/fabio/fabio_volume_fvg.py, backtest/layers/positioning/funding_cvd_fade.py, backtest/layers/rsi/run_divergence_mtf.py,
  backtest/layers/session/session_momentum.py, backtest/layers/turn_of_candle/, research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md,
  research/candle_patterns_2026-10-04, research/setup_alpha_beta_2026-10-10/alpha_backtest.py, research/t087_session_levels_2026-10-09,
  research/tom_fabio_guidance_2026-10-12/matrix_q33.py, research/volume_2026-10-09
  Check whether these are moved, renamed or only exist in another repo before trusting layer_map rows that cite them.
