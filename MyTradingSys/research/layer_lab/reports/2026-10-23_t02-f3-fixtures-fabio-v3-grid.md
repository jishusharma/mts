# T02-F3 part c: Event-Forcing Look-Ahead Fixtures for Fabio v3 Grid

**Date:** 2026-10-23  
**Runner:** Gemini Flash (Antigravity, JIS-NUC)  
**Card:** `t02-f3-fixtures-fabio-v3-grid`  
**Scope:** T02 backtest causality audit — fabio v3 grid lookahead verification  
**Artifact:** `MyTradingSys/backtest/layers/alerts/test_lookahead_forcing_fabio_v3.py`

---

## 1. Problem Statement & Motivation

During the T02 backtest truncation audit (`MyTradingSys/research/dsa_backtest_audit_2026-10-16/T02_lookahead_time.md`, table 3a), the layer `fabio|v3_grid|1m` produced 0 events on synthetic random walk bars. Consequently, comparing full vs truncated series was vacuous.

Card `t02-f3-fixtures-fabio-v3-grid` mandates:
1. Building a hand-built 1m order-flow fixture (with required columns: `buy_vol`, `sell_vol`, `b99_buy_vol`, `b99_sell_vol`, `thr_days`, `fp`) spanning the NY open window that forces at least one Fabio v3 signal.
2. Executing `assert_causal` across 15+ cuts comparing full, truncated, NaN-tail, and x10-tail series to verify 0 lookahead differences (0 late, 0 repaint, 0 NaN differences, 0 x10 differences).
3. Verifying that planted lookahead peeks (such as next-bar peek and future-dependent emission) fail `assert_causal` cleanly with an `AssertionError`.

---

## 2. Fixture Design & Implementation

- **Session alignment:** Monday 2024-01-08 starting at NY cash open (14:30 UTC = 09:30 EST, $t_0 = 1704724200000$).
- **Initial Balance (IB) bars (0..29):** 30 1m bars flat at 100.0 (high 100.1, low 99.9), `b99_buy_vol = 0.0`.
- **Breakout bar (bar 30):** Close at 100.5 (above IB high 100.1), `b99_buy_vol = 10.0`, triggering Model C IB breakout SIGNAL in confirm entry mode at timestamp $1704726000000$.
- **Subsequent bars (31..34):** Follow-through bars confirming the breakout.
- **Scanning layer:** `make_fabio_v3_layer` operates on discrete 1m bar windows terminating at the current closed bar. The sequential scanner evaluates prefixes `bars[:j+1]` across the window, mirroring live emitter polling.

---

## 3. Test Results & Verification

Ran test suite `MyTradingSys.backtest.layers.alerts.test_lookahead_forcing_fabio_v3`:

- `test_fixture_forces_expected_events`:
  - Full grid emits 72 Model C events on bar 30 ($t = 1704726000000$), all long side. Pass.
- `test_single_cell_fixture_forces_one_event`:
  - Single-cell grid ($N=60, p=0.05, z_{hi}=2.0, m_c=5, f=0.003$) emits exactly 1 event on bar 30.
  - `assert_causal` across cuts 20..34 yields: `events_full = 1`, `compared = 5`, 0 late, 0 repaint, 0 NaN diffs, 0 x10 diffs. Pass.
- `test_assert_causal_passes_full_grid`:
  - Full default grid (72 cells) across cuts 20..34 yields: `events_full = 72`, `compared = 360`, 0 late, 0 repaint, 0 NaN diffs, 0 x10 diffs. Pass.
- `test_planted_peek_is_detected`:
  - `fwd_peek_next_bar_layer`: detects 1 late event and 14 x10 poison diffs; raises `AssertionError`. Pass.
  - `leaky_fabio` (requires next bar to be present): detects 72 late events and 72 x10 poison diffs at cut 30; raises `AssertionError`. Pass.
  - Vacuous fixture (0 events): raises `AssertionError`. Pass.

All 4 tests run in 2.37s with 0 errors or failures.
