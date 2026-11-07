# Multi-Stage Revalidation Log: Tom & Fabio Course Correction (2026-11-07)

This document records the 4-stage revalidation pipeline mandated by the operator:
1. **Stage A — Self-Revalidation #1 (Argon / Gemini Pro)**
2. **Stage B — Independent Revalidation by Flash Model (`06542add-72ec-4698-8b1b-4d7cdaec47ff`)**
3. **Stage C — Self-Revalidation #2 Incorporating Flash Suggestions (Argon / Gemini Pro)**
4. **Stage D — Independent Pre-Trunk Review by Claude (`claude -p --model sonnet`)**

---

## Stage A: Self-Revalidation #1 (Initial Audit & Code Verification)
- Verified `AUDIT_AND_COURSE_CORRECTION.md` against `FORMULAS.md`, `OPERATOR_DECISIONS.md`, `RESCORE.md`, `value_area_acceptance_2026-11-05/RESULT.md`, `CENSUS_5m_2026-10-03_11-07.md`, and `SetupCandidatesBuilder.java`.
- Fixed `test_auction_context.py` touch-index detection when pre-touch bars pass near a level before the actual probing bar (`probed` scan prioritized over `zone_tol_pct`).
- Verified `test_run_v3_l3.py`, `test_models_engine.py`, `test_spec_tf_strip.py`, and `test_auction_context.py` all pass.

---

## Stage B: Independent Flash Model Revalidation (`06542add-72ec-4698-8b1b-4d7cdaec47ff`)

### Summary of Flash Model Critique & Findings
1. **Factual & Numerical Cross-Check**:
   - Confirmed accuracy of `vp_pivot_probe.py` (`0/48`), `tom_vp.py` (`0/20`, `-0.399 R`), `tom_fabio_guidance` (`0/186`), `TOM_CORE_BT_RERUN` (`2,880` fills, gross `-0.145 R`, fee `2.76 R`, net `-2.912 R`, median stop `8.2 bps`; `>=5` proofs: `13-17` trades in 4.7y, `0/7` DAX recall), `SpikeFadeDetector` (`1/10` recall), `Fabio v3` (`12` IS / `0` OOS for Model A, `8` IS / `0` OOS for Model D, `3.1%` S1 balance rate `B141`), and `value_area_acceptance` (`77%` continuation on Event A, `n=300`; `44%` on Event R, `n=493`).
   - **Caught `0.001 R` rounding in `RESCORE.md`**: `RESCORE.md` line 12 reports `-1.423 R` (`all mkt PLAN tight`, fee `1.502 R`, gross `+0.079 R`), whereas the draft cited `-1.422 R`.
   - **Caught exact Bybit 5m OHLCV values in `CENSUS_5m_2026-10-03_11-07.md` (lines 119–123)**: Recommended updating Trade 4's 5m bar table and `test_auction_context.py` to use the exact printed numbers from `CENSUS_5m` lines 119–123 (`15:00 O 75511 H 75568 L 74929 C 75046 V 2702`, `15:05 O 75046 H 75378 L 74810 C 75290 V 3005`).
   - **Uncovered deeper structural asymmetry in `SetupCandidatesBuilder.java:313-332, 476-482`**:
     - At `above_vah`, line `307` sets `trend_healthy`, line `317` adds `"short"` and `"long"`, line `477` kills `"short"` (`if ("trend_healthy".equals(state)) return null;`), and line `478` kills `"long"` (`return isShort ? "ct_short" : null;`) -> **0 setups possible at VAH**.
     - At `below_val`, line `320` only adds `"long"` (omitting `"short"`, so breakdown continuation below VAL is impossible), while line `480` (`val`) omits the `trend_healthy` check that line `477` (`vah`) enforces!
2. **Code Logic & Edge-Case Critique on `auction_context.py`**:
   - **Unimplemented `LVN_FAST_TRAVERSE` verdict**: Mentioned in docstrings, but `classify_level_interaction` fell through to `PROBING_UNCONFIRMED` when an impulse candle sliced across an LVN without reclaiming.
   - **Stale `reclaim_idx` on double probes / deeper sweep**: If Bar 0 pierced support and closed above, and Bar 1 either closed back below support or swept to a deeper low (`74,810` after `74,929`) and closed back above (`75,290`), `reclaim_idx` stayed stuck at Bar 0 instead of advancing to Bar 1 (`V2_sweep`).
   - **Contiguous Multi-Bin LVNs in `compute_volume_profile`**: Strict single-bin inequality (`vk < v_prev and vk < v_next`) missed 2+ adjacent low-volume bins.
   - **`is_knife_approach` lookback guard**: Returned `False` unconditionally when `touch_idx < 12` even if `6` pre-touch bars formed a `-2.8%` vertical cliff.
   - **Substring matching on `htf_bias`**: `"bear" in htf_bias` matched `"counter_trend_bounce_in_macro_bear"`.

---

## Stage C: Self-Revalidation #2 (Incorporating Flash Model Suggestions)

All 8 recommendations from the Flash model audit were implemented and verified:
1. Updated `AUDIT_AND_COURSE_CORRECTION.md` with `-1.423 R` (`RESCORE.md` line 12), the exact Bybit 5m bars from `CENSUS_5m` lines 119–123 (`15:00 V 2,702`, `15:05 V 3,005`), and the full forensic breakdown of `SetupCandidatesBuilder.java:307, 317-322, 476-482`.
2. Implemented `LVN_FAST_TRAVERSE` in `classify_level_interaction()` and `lvn_fast_traverse` trade construction in `build_auction_trade_plan()`.
3. Fixed `reclaim_idx` tracking in `classify_level_interaction()` so that (a) closing back beyond the level resets `reclaim_idx = None`, and (b) making a deeper sweep extreme (`l < sweep_extreme` on support or `h > sweep_extreme` on resistance) while closing inside updates `reclaim_idx` to the true final sweep-reclaim bar (`V2_sweep` on the Nov 6 `15:00–15:05` bars).
4. Upgraded `compute_volume_profile()` to detect contiguous multi-bin LVN vacuums (`lvn_zones` + `lvns`).
5. Updated `is_knife_approach()` to evaluate `bars[max(0, touch_idx - lookback):touch_idx]` whenever `touch_idx >= 3`.
6. Replaced substring matching with `BEARISH_HTF_BIASES` / `BULLISH_HTF_BIASES` frozensets in `build_auction_trade_plan()`.
7. Added unit tests in `test_auction_context.py` covering `LVN_FAST_TRAVERSE`, double-probe reclaim reset, multi-bin LVN vacuums, short-window knife detection, and `counter_trend_bounce_in_macro_bear` sizing (`10 passed in 0.30s`).


---

## Stage D: Independent Pre-Trunk Review by Claude (`claude -p --model sonnet`)

Before shipping to trunk (`origin/fast-track`), we ran an independent review using Claude (`claude -p --model sonnet`, task `1094`) directly against the worktree diff and files.

### Summary of Claude's Findings & Recommendations
1. **Verified All 3 Deliverables**:
   - Confirmed the `engine.py` / `models.py` fix for Fabio v3 Model A `confirm` mode is surgical and prevents silent `0.0 R` (`"unmanaged"`) scoring.
   - Confirmed the `'1M'` addition to `tf_strip.js`, `live_aid.html`, and `test_spec_tf_strip.py` is clean (`TFS` length `8`, `ALL_TFS` length `9`) and matches Binance `'1M'` kline intervals.
   - Confirmed the root-cause diagnoses in `AUDIT_AND_COURSE_CORRECTION.md` (fee-to-stop geometry collapse, over-gating vs. blind level touches, missing `1M`/`1w` context ladder, `SetupCandidatesBuilder.java` VAH/VAL asymmetry, and location-blind order flow).
2. **Code Refinements Requested on `auction_context.py` (All Implemented)**:
   - **Pre-Touch Volume Baseline (`med_vol`)**: Changed `vols[:look_vol]` (which took the first 48 bars of the array rather than the 48 bars immediately preceding `touch_idx` when `len(bars) > 60`) to `vols[max(0, touch_idx - 48):touch_idx]`.
   - **Macro-Bear Bounce Short Sizing (`BEARISH_HTF_BIASES`)**: Renamed the green-month-below-20M-SMA bias to `"rally_in_macro_bear"` and included it in `BEARISH_HTF_BIASES` so that shorting at resistance during a counter-trend bounce inside a macro bear receives `"full_with_htf"`, symmetric with `"pullback_in_macro_bull"` for longs. Also incorporated `elapsed_pct` and `p_keep_colour` to flag nascent monthly candles (`<10%` elapsed and `P_keep < 60%`).
   - **Consecutive Acceptance Tracking & Provenance (`OUR` vs `SOURCED`)**: Added `consec_beyond` and `max_consec_beyond` tracking in `classify_level_interaction()` so `ACCEPTED` requires consecutive closes beyond the level (`max_consec_beyond >= 6` or `not currently_inside and consec_beyond >= 4`), and explicitly documented the provenance (`OURS` on 5m, `SOURCED` to `accept80.py` on `2x 30m`).
   - **Recency Guard on Fast Rejection (`STALE_REJECTION`)**: Added `max_bars_since_reclaim: int = 3` to `classify_level_interaction()` so a reclaim that happened `> 3` bars ago returns `verdict = "STALE_REJECTION"` (`trade_bias = "skip_stale"`) instead of firing late.
   - **Exact Fee-Inclusive R:R (`effective_rr`)**: Added `"effective_rr": round((gross_rr - fee_r) / (1.0 + fee_r), 2)` alongside `net_rr` in `build_auction_trade_plan()`.
   - **Optional Bar-Range Volume Spreading (`spread_range`) & `poc_mid`**: Added `spread_range: bool = False` and `"poc_mid"` to `compute_volume_profile()`.
   - **Fail-Closed Short Pre-Touch Window in `is_knife_approach`, `LEVEL_SIDE_ALIASES`, and Causality Guard**: `is_knife_approach()` now returns `True` (fail closed) when `touch_idx < 3`; `LEVEL_SIDE_ALIASES` maps `'val'`/`'low'` -> `'support'` and `'vah'`/`'high'` -> `'resistance'`; `evaluate_forming_candle()` raises `ValueError` if `bars[-1]["t"] > now_ms`.
3. **Report Refinements & Follow-Up Companion Cards**:
   - Clarified in `AUDIT_AND_COURSE_CORRECTION.md` that `SetupCandidatesBuilder.java:303-307` sets `trend_healthy` in `14/18` outside-VA slope combinations and `trend_unhealthy` in the `4/18` opposing-CVD combinations, labeled the four Oct–Nov 2026 trades as illustrative diagnostic case studies, and filed two companion follow-up cards on the queue: (1) Pre-registered multi-month OOS backtest of `auction_context.py` on BTC 5m/15m data, and (2) Patching `SetupCandidatesBuilder.java:320, 477-480` VAH/VAL asymmetry.
