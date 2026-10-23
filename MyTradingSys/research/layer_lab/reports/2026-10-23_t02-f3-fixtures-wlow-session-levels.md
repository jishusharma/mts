# T02-F3 part b: Event-Forcing Look-Ahead Fixtures for Wlow Bounce and Session Levels

**Date:** 2026-10-23  
**Runner:** Gemini Flash (Antigravity, JIS-NUC)  
**Card:** `t02-f3-fixtures-wlow-session-levels`  
**Scope:** T02 backtest causality audit — wlow_bounce and session_levels lookahead verification  
**Artifact:** `MyTradingSys/backtest/layers/alerts/test_lookahead_forcing_wlow_session.py`

---

## 1. Problem Statement & Motivation

During the T02 backtest truncation audit (`MyTradingSys/research/dsa_backtest_audit_2026-10-16/T02_lookahead_time.md`, table 3a), two layers produced 0 events on synthetic random walk bars:
- `wlow_bounce|bbrsi60|1h`: requires a complete prior ISO week to establish a weekly low, followed by a break below that low, a bounce back above it, and a Bollinger/RSI hold condition.
- `session_levels|session_levels|1m`: requires a complete prior UTC day (>= 1400 bars) to calculate prior-day high/low, followed by an Asia/EU session poke outside the range and a failed break back inside within the 60-minute window.

Comparing full vs truncated series was therefore vacuous for both layers. Card `t02-f3-fixtures-wlow-session-levels` mandates hand-building event-forcing fixtures for each layer and verifying them under the shared `assert_causal` harness with planted peek detection.

---

## 2. Fixture Design & Implementation

### A. Weekly-Low Bounce (`wlow_bounce|bbrsi60|1h`)
- **Week 0:** 168 1h bars flat at 95.80 with a dip to 95.0 on bar 50, establishing prior ISO weekly low $W = 95.0$.
- **Week 1:**
  - Bar 170: dips below $W$ ($l = 94.0, c = 94.5$), opening a bounce episode (`BROKEN`).
  - Bar 171: closes back above $W$ ($c = 95.9, h = 96.0$), entering `BOUNCED` status.
  - Bars 172..189: rise steadily by $+0.05$/bar. On bar 175, Bollinger upper band condition ($c \ge \text{upper} \times 0.995$), RSI range ($52 \le \text{RSI} < 60$), and slope limit ($|\Delta\text{RSI}| \le 3.0$) are satisfied simultaneously.
  - Bar 175 triggers active event `wlow_bounce_bbrsi60_active` ($t = 1704697200000$, side `long`).

### B. Session Levels (`session_levels|session_levels|1m`)
- **Day 0:** 1440 1m bars ($h = 100.0, l = 90.0, c = 95.0$) establishing prior-day high $PDH = 100.0$.
- **Day 1:**
  - Bar 100 (Asia session, minute 100): pokes above PDH ($h = 105.0$).
  - Bar 101 (minute 101): closes back below PDH ($c = 99.0$), completing failed breakout.
  - Triggers failed break event `sess_pdh_failed_break` at timestamp $1728092460000$ (side `short`, level `100.0`).

---

## 3. Test Results & Verification

Ran test suite `MyTradingSys.backtest.layers.alerts.test_lookahead_forcing_wlow_session`:

- `TestWlowBounceCausal`:
  - `test_fixture_forces_the_expected_event`: exactly 1 event on bar 175 ($t = 1704697200000$), event `wlow_bounce_bbrsi60_active`, prior weekly low 95.0, side long. Pass.
  - `test_no_look_ahead_with_events`: `assert_causal` across 15 cuts (170..184) yields `events_full = 1`, `compared = 10`, 0 late, 0 repaint, 0 NaN diffs, 0 x10 diffs. Pass.
  - `test_planted_peek_is_detected`: `fwd_peek_next_bar_layer` and leaky scanner fail `assert_causal` with `AssertionError`; empty fixture raises `AssertionError`. Pass.
- `TestSessionLevelsCausal`:
  - `test_fixture_forces_the_expected_event`: exactly 1 event at Day 1 + 101 min ($t = 1728092460000$), event `sess_pdh_failed_break`, side short, level 100.0. Pass.
  - `test_no_look_ahead_with_events`: `assert_causal` across 20 cuts (1535..1554) yields `events_full = 1`, `compared = 20`, 0 late, 0 repaint, 0 NaN diffs, 0 x10 diffs. Pass.
  - `test_planted_peek_is_detected`: `fwd_peek_next_bar_layer` and leaky adapter fail `assert_causal` with `AssertionError`; empty fixture raises `AssertionError`. Pass.

All 6 tests run in 24.62s with 0 errors or failures.
