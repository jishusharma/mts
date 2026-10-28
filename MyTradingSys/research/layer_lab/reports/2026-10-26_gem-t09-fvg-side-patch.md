# Lab Report: Review of GPT volume_fvg Side Fix, Patch, Fixture, and Trunk Status (2026-10-28)

**Task**: `gem-t09-fvg-side-patch`  
**Card Title**: `[GEMINI] Review GPT's volume_fvg side fix: patch, red-green fixture, trunk status`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-t09-fvg-side-patch/MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; strict vendor separation satisfied)  
**Files Audited**:
- [`MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/fix.patch`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-t09-fvg-side-patch/MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/fix.patch)
- [`MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/proposed_test_volume_fvg_side.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-t09-fvg-side-patch/MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/proposed_test_volume_fvg_side.py)
- [`MyTradingSys/backtest/layers/alerts/live_layers.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-t09-fvg-side-patch/MyTradingSys/backtest/layers/alerts/live_layers.py) (lines 40–70)
- [`MyTradingSys/backtest/layers/fabio/run_backtest.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-t09-fvg-side-patch/MyTradingSys/backtest/layers/fabio/run_backtest.py) (lines 195–215)
- [`MyTradingSys/backtest/layers/alerts/test_live_runner_layers.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-t09-fvg-side-patch/MyTradingSys/backtest/layers/alerts/test_live_runner_layers.py) (lines 115–165)
- Git commit history for `live_layers.py` (specifically commit `5603ff871d73db7cbcdfcbfc69fbbb26a8ed287e`)

*Constraint adherence*: In strict adherence to the card rules, `T09 section 5` was NOT read. No code or spec modifications were made. `git apply --check` was executed without applying modifications to the worktree.

---

## 1. Executive Summary

1. **Bug Diagnosis Confirmed (`SOUND`)**:
   - GPT's finding T09-F1 is mathematically and logically correct. In the original implementation of `live_layers.py` (prior to commit `5603ff871d`), line 61 mapped `side = "short" if closes[start] > mid else "long"`.
   - Conversely, the backtest implementation in `run_backtest.py:199-203` computes `from_above = closes[start] > mid` and records `ev[(name, "bounce")].append({"i": i, "side": "long" if from_above else "short"})`.
   - When price confirms above the midpoint (`closes[start] > mid`), backtest bounce treats the retest from above as a `long` entry, whereas `live_layers.py` originally emitted a `short` alert, causing an exact 180-degree polarity reversal (0 matches in 24 historical parity events).

2. **Trunk Status (`ALREADY RESOLVED`)**:
   - The inversion was independently resolved in trunk on 2026-10-25 via commit `5603ff871d73db7cbcdfcbfc69fbbb26a8ed287e` (`T09-F1: live volume_fvg takes the backtest bounce side, scan from confirmed_i+1`).
   - Trunk now correctly implements `side = "long" if closes[start] > mid else "short"` at `live_layers.py:64`.
   - In addition, commit `5603ff871d` addressed scan-start latency (`start + 1`), added fail-closed bar length validation (`len(bars) < 2 * n_bins`), added comprehensive unit test suites in `test_live_runner_layers.py:126-165` (all 6 tests passing), and updated `test_layer_signal_parity.py`.

3. **Evaluation of GPT's Patch Proposal (`fix.patch`)**:
   - Running `git apply --check MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/fix.patch` exits with error code 1: `error: No valid patches in input (allow with "--allow-empty")`.
   - The patch file lacks standard unified diff chunk line headers (`@@` without line ranges or closing delimiters) and contains non-standard text trailers (`*** End Patch`).
   - Even if formatted as valid unified diff syntax, the patch is redundant because the targeted line change is already merged into trunk.

4. **Evaluation of GPT's Proposed Test (`proposed_test_volume_fvg_side.py`)**:
   - Running `pytest MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/proposed_test_volume_fvg_side.py` against current trunk fails with `IndexError: list index out of range` at line 12.
   - Root cause: GPT's fixture synthesizes `bars` with length 25 (`len(bars) == 25`). Current trunk `live_layers.py:46-47` contains the guard `if len(bars) < 2 * n_bins: return []` (with default `n_bins=20`, requiring $2 \times 20 = 40$ bars). Because $25 < 40$, `volume_fvg_layer(bars)` returns `[]`, triggering `IndexError` on index `[0]`.
   - Trunk's official unit test `test_volume_fvg_side_matches_backtest` in `test_live_runner_layers.py:134-139` uses `n=40` bars and tests both above (`10.5` -> `long`) and below (`9.5` -> `short`) cleanly.

---

## 2. Independent Audit Details

### A. Side Mapping Logic Comparison

| Implementation | Source File & Lines | Logic / Code | When `closes[start] > mid` |
|---|---|---|---|
| Backtest Bounce | `run_backtest.py:199,202` | `from_above = closes[start] > mid`<br>`side = "long" if from_above else "short"` | `long` |
| Backtest Through | `run_backtest.py:199,203` | `from_above = closes[start] > mid`<br>`side = "short" if from_above else "long"` | `short` |
| Live Layer (Pre-fix) | `live_layers.py:61` (commit `4d1bc360dc`) | `side = "short" if closes[start] > mid else "long"` | `short` (**Inverted** vs bounce) |
| Live Layer (Current trunk) | `live_layers.py:64` (commit `5603ff871d`) | `side = "long" if closes[start] > mid else "short"` | `long` (**MATCH**) |

### B. Patch and Test Verification Results

| Target Artifact | Command | Result Code | Outcome / Observation |
|---|---|:---:|---|
| `fix.patch` | `git apply --check MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/fix.patch` | 1 | `error: No valid patches in input (allow with "--allow-empty")` (Malformed hunk header `@@`, trailer `*** End Patch`). |
| `proposed_test_volume_fvg_side.py` | `python -m pytest MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/proposed_test_volume_fvg_side.py` | 1 | `IndexError: list index out of range` on line 12. Fixture uses 25 bars; fails closed by `len(bars) < 2 * n_bins` (40) check added in commit `5603ff871d`. |
| Trunk volume_fvg unit tests | `python -m pytest MyTradingSys/backtest/layers/alerts/test_live_runner_layers.py -k VolumeFvg` | 0 | 6 passed (including `test_volume_fvg_side_matches_backtest`, `test_volume_fvg_scan_starts_after_confirmation`, `test_volume_fvg_restart_same_bars_same_events`, `test_volume_fvg_degenerate_inputs_return_empty`). |

---

## 3. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/fix.patch:3,6` | Diff syntax invalid for `git apply`; hunk header lacks line range numbers (`@@`), ends with `*** End Patch`. | `git apply --check` exits with error: `No valid patches in input`. | None needed for trunk; commit `5603ff871d` already merged the change. In future burn patches, output standard unified diff headers `@@ -start,len +start,len @@`. |
| LOW | `MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/proposed_test_volume_fvg_side.py:6,12` | Test fixture synthesizes only 25 bars; fails with `IndexError` against current trunk due to the 40-bar fail-closed rule (`2 * n_bins`). | Pytest failure: `IndexError: list index out of range` at line 12 because `volume_fvg_layer(bars)` returns `[]`. | Superseded by trunk's `test_live_runner_layers.py:126-140` which uses 40 bars (`n=40`). If running GPT fixture standalone, set `n=40` or pass `n_bins=12`. |
| SOUND | `MyTradingSys/backtest/layers/alerts/live_layers.py:64` vs `run_backtest.py:199-203` | Pre-fix code inverted live alert side relative to backtest bounce; trunk commit `5603ff871d` already corrected it to `side = "long" if closes[start] > mid else "short"`. | `run_backtest.py:202` emits `long` when `closes[start] > mid`. Trunk `live_layers.py:64` matches. 6 test cases pass. | Resolved in trunk (no further code changes required). |

---

## 4. Verdict

**Verdict: SOUND.**  
The producer's core audit finding (T09-F1 live volume_fvg side inversion) is mathematically and architecturally sound. The fix and regression tests were already independently committed and merged into trunk in commit `5603ff871d73db7cbcdfcbfc69fbbb26a8ed287e`. The proposed standalone artifacts in `gx4-t09-f1-fvg-side/` are fully superseded by trunk's integrated test coverage and code.
