# PRE-REG: Tom return-to-value, near-band placebo as PRIMARY, fresh pre-DEV data (card tom-v2-gross-first-dev-ext)

Written 2026-11-01 BEFORE any run. Source of the test: `research/tom_fabio_review_2026-10-31/SETUP_REVIEW.md:244-248` (section 6 test 2); D7 S3 run list #6.
Everything not listed here is the same as `research/tom_transfer_2026-10-11/vp_return/PRE_REG.md` (definitions, event, RETURN outcome, placebo d cycle (-3,-2,-1,-0.5,0.5,1,2,3) by day index mod 8, ATR14 1h R_ref, bootstrap 2000 day-block seed 20261009, FORMULAS 18.1/18.6/18.7). Labels: SOURCED / OURS / NO-SOURCE as there.
A COUNT of a claim, no trade, no cost, no stop, no target (0a-0b, 6-8 not applicable, as in vp_return). `prereg_gate.py` does not apply (no R, no edge claim). DECISION (OURS): skipped.

## Why this test (the reason, not a new idea)
The DEV vp_return run found real 57.2 % vs pooled placebo 46.8 %, but the post-hoc `|d|<=1` rows showed a band near value behaves like value (51.2 vs 47.8 on those days; descriptive, post-hoc). That was found after seeing the data, so it cannot be a verdict. This card fixes the near-band comparison in advance and runs it on data not yet used.

## Hypothesis and rule (fixed now)
- Data: BTCUSDT USD-M perp 1m klines 2020-01-01..2021-12-31 (`dev_ext_2019_2021`, DEV_EXT, strictly before DEV 2022-01-01; decision D3 in OPERATOR_DECISIONS.md). Perp 1m is public only from 2020-01 (2019 spot is not mixed in: other venue/basis). The folder is absent on this machine, so the same 24 monthly files are fetched from data.binance.vision (public, SHA256-verified) with `fetch_dev_ext.py` into `C:/MTS_data/dev_ext_2019_2021`. No bar at or after 2022-01-01 is read (asserted). DEV, VALIDATION, HOLDOUT unread.
- Primary: real return share minus placebo return share, both over the days whose placebo shift has |d| <= 1 (d in -1, -0.5, +0.5, +1: half of the 8-cycle), same events and RETURN rule, `vp_return_to_value.near_band_primary`.
- H1: diff > 0 AND the lower bound of the 95 % day-block bootstrap CI (2000 resamples, same resampled days for both arms) > 0. PASS if both, FAIL otherwise. No other outcome class and no threshold other than 0.
- If FAIL: the 70/30 claim has no value-specific content on BTC UTC-day value (SETUP_REVIEW). If PASS: the pooled-placebo contrast of the DEV run was driven by far bands being unlike value-specific, and the claim survives one fresh-data test only; no rule is added.
- Not tuned: bin 10 USD, VA 70 %, d set, |d| cut 1.0, N set; nothing is changed after the run. One run.

## Template items (deltas to vp_return)
- 0c Record: a stated frequency, hypothesis only.
- 0d Data: 5m high, low, volume from 1m klines; incomplete UTC days (missing minutes) dropped and counted (NOT_IN_DATA, never zero).
- 0e Power / n: days available ~ 730 (2020-01-02..2021-12-31 need a prior day). Fire rate ~96 % (vp_return RESULT). The |d|<=1 restriction keeps 4 of 8 d values, so expected primary n ~ 350 events per arm, NOT the 870 in the card text (that figure is for all d over 911 days; the card's 2019 start does not exist as perp data). Day-block CI about +-4 pp per arm; detectable diff ~ 6-8 pp at 80 % power. DECISION (OURS): run anyway, report n; if n < 100 the row says UNDERPOWERED, never "no effect".
- 0f Kill: PASS/FAIL as above. FAIL kills nothing beyond the claim's value-specific reading on this window.
- 11 Holdout: DEV_EXT only. Trials: 1 primary. Descriptive and NOT the verdict: pooled all-d diff, far-band rows (|d|>=2), per year (2020, 2021), by side, per-d rows, Part B N=3/6/12, naked-POC, censoring (all from the unchanged `vp_return_to_value.compute`).
- 12 Stratified readout: per year 2020, 2021; up-leave vs down-leave.

## Fail-first test
`test_vp_return_to_value.py::test_near_band_primary_excludes_far_placebo`: hand-computed 3-day table where the |d|=3 day must be excluded (restricted diff +0.5, n 2; unrestricted would be +1/3). It failed (AttributeError) on the code before `near_band_primary` existed.

## Look-ahead guard
Unchanged from vp_return: value of D from D-1 bars, event from bars up to its close, R_ref from 1h bars closed at or before 00:00 of D, outcome bars after the event. `scripts/dev/lookahead_lint.py` before shipping.
