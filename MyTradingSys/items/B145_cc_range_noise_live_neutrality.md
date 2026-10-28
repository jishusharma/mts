# B145 - Stopped-loop neutrality test before classify_msb filter_range_noise goes live

Status: CLOSED. Severity: LOW. Opened 2026-10-08.
Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Follow-up to B128 TC-W1-6. Operator ruling 2026-10-08: the flag stays disabled; no live change this session.

## Defect

classify_msb(filter_range_noise=...) defaults to False and the live CryptoCred layer passes no flag (MyTradingSys/backtest/layers/alerts/live_layers.py:122, `_cc_layer`). Turning it on changes which CryptoCred alerts reach the live runner. There is no evidence that it is neutral or better.

## Required before the flag goes live

File: MyTradingSys/backtest/layers/cryptocred/test_cc_range_noise_live_neutrality.py (new).
Test: `test_filter_range_noise_is_neutral_or_better_on_archive_replay`. It runs the live `_cc_layer` path from live_layers.py over the archive bars (Dumps/backtest/raw_1m_2022 + raw, 1h) twice, flag False and flag True, simulates every resulting alert with the same bt_engine/fees.py settings as run_cc_setups.py, and asserts all of:
1. kept-alert count with the flag on is >= 30 per setup;
2. mean net R with the flag on >= mean net R with the flag off, per setup;
3. no alert present with the flag on is absent from the flag-off set (the filter only removes).
It runs in a stopped-loop window (scripts/core/stop-day.ps1 first) because the one-line change to live_layers.py:122 is the only live-path edit and must be gated before mode.ps1 -M armed. The change is promoted via live_layers.py.new, backup .pre_<tag>, re-gate, commit.

## Provenance note

The filter threshold (25 percent of the 50-bar range, cc_structure.py:62) is NO-SOURCE like the other CryptoCred values (B143). A pass here shows neutrality, not a sourced rule; the flag must not be tuned.

## Related

- MyTradingSys/items/B128_partial_code_partial_no_test.md (TC-W1-6)
- MyTradingSys/tests/test_b128_cc_range_noise_filter.py
- MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md

## Receipt

2026-10-10: MyTradingSys/backtest/layers/cryptocred/test_cc_range_noise_live_neutrality.py written to the spec and run with MTS_CC_NEUTRALITY_DATA=F:/MTS/data/tom_raw (382 s). Failures: setup1_sr_flip mean net R with the flag -1.1351 vs without -1.0707 (n 474 vs 1477); setup3_failed_msb_reversal -0.1504 vs -0.1029 (n 52 vs 167). Passes for setup2_fib_pullback; kept-alert count >= 30 and the subset property hold for all three. Decision: filter_range_noise stays disabled, live_layers.py:122 is not changed. The test is opt-in (skips without the env var) so the quick gate stays fast.

# END
