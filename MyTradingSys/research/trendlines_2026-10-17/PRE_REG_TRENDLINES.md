# PRE-REGISTRATION: trend-line behaviour, BTCUSDT perp, DEV (frozen 2026-10-17)

Card `trendline-count-only`. Status: EXPLORATORY, not a strategy test; nothing here adopts a rule. Precedes any outcome read: the commit that adds this file precedes any commit that adds a forward return, MFE/MAE or fee. Detector: `backtest/layers/trendlines/trendline_core.py` (contract `TRENDLINE_CONTRACT.md` v1, parameters fixed there, none re-tuned here).
Labels: SOURCED = quoted from a saved source; OURS = judgement or chosen on DEV counts (allowed; one VALIDATION check later, HOLDOUT sealed, variants in the trial ledger).

## 0. What was read
- Read: Binance USDT-M BTCUSDT 1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01.csv .. -2024-06.csv` (30 files, 1,313,280 bars, DEV only; the loader refuses any bar >= 2024-07-01, test `test_loader_refuses_bar_at_or_after_2024_07_01`). Fields used: open, high, low, close, volume, aggregated to closed 1h, 4h, 1d bars through `tf_resample`.
- Computed: lines, contact episodes, breaks, event-days, MDE. NOT computed anywhere (`count_only.py` and `counts/*.csv` have no such column; `assert_no_outcome_columns` refuses one): any forward return, MFE/MAE, fee, hit rate, retest/reclaim outcome, or any bar after an event. VALIDATION and HOLDOUT: zero reads. Logged in `gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`.
- Reproduce: `python MyTradingSys/research/trendlines_2026-10-17/count_only.py --split DEV` (about 5 minutes). Tests: `test_count_only.py` (7).
- Overlap with earlier S/R studies (`research/VERDICTS.csv`, family text checked): none tests diagonal trend lines. Horizontal-level studies exist (Qriptal filter on lc-levels-hold: DEV FAIL; operator context composite C: DEV INCONCLUSIVE; prior-day VA failed auction: BLOCKED). They bear on the horizontal arm (section 4), not on the line arm.
- Defaults taken without asking: TF set 1h/4h/1d per contract F3 (the card text also named 1m; contract F3 excludes 1m until a power audit, and it was not run); sides pooled by sign (support = long, resistance = short); event-day = UTC date of the event bar's open time; touches and breaks counted only AFTER the line's eligibility bar for that arm (`known_at` strictly later).

## 1. Counting definitions (from the detector's append-only events)
| Item | Definition |
|---|---|
| Line | detector line (anchor pair passing the contract P/L rules), per price arm / transform / age cap |
| Eligible line (arm A/B/V) | contract E2 / E3 / E4: A = 2 anchors + first contact episode closed by reset; B = third anchor; V = two high-volume anchors |
| `touch` event | start of a contact episode (E5/E6) on a line already eligible in that arm, at a bar after the eligibility bar |
| `break` event | first close beyond the line (B1) on a line already eligible in that arm, at a bar after the eligibility bar |
| Event-day | distinct UTC days holding at least one event of the cell (the independence unit; `counts/effective_n_by_day.csv` has the per-day table for the primary family) |
| Slope tercile | terciles of abs(slope_atr) per TF and side over all proposed lines of that family (T1 flattest). Stratum only |

## 2. Power rule (OURS, same as `wavetrend_2026-10-17/PRE_REG.md`)
MDE (SD units of the outcome) = (z(1 - 0.05/(2m)) + 0.84) / sqrt(event-days); a cell stays when MDE <= 0.30 SD. m = the smallest family size with (cells passing at m) <= m, so the Holm correction is never smaller than the number of carried cells. The confirmatory family is the **pooled-tercile primary cells** (TF x arm A/B/V x event touch/break = 18, wick / log / age cap 500); this choice is OURS and was made after seeing that tercile cells split 150-event-day cells three ways. Slope-tercile cells are descriptive strata, not in the family: only 1h arm A T1 reaches the floor (touch 150 event-days, break 140; MDE 0.26 / 0.27 at m=3) and it stays a stratum. MDE is in SD units because no outcome was read; the study converts to bp with the realised SD.

Result: **m = 3, 3 of 18 primary cells carried.**

## 3. Frozen cells (primary family: wick, log price, age cap 500 bars)
| Cell | Eligible lines | Events | Event-days | MDE (SD, Holm m=3, 80 %) | Status |
|---|---|---|---|---|---|
| 1h, arm A, touch | 492 | 464 | 283 | 0.19 | CARRIED |
| 1h, arm A, break | 492 | 464 | 278 | 0.19 | CARRIED |
| 1h, arm B, break | 298 | 281 | 184 | 0.24 | CARRIED |

### Underpowered (dropped from this PRE_REG; counts stay in `counts/CELLS.csv`)
| Cell | Event-days | MDE (SD, m=3) |
|---|---|---|
| 1h arm B touch | 103 | 0.32 |
| 1h arm V break / touch | 76 / 58 | 0.37 / 0.42 |
| 4h arm A touch / break | 80 / 76 | 0.36 / 0.37 |
| 4h arm B break / touch | 62 / 31 | 0.41 / 0.58 |
| 4h arm V break / touch | 17 / 16 | 0.78 / 0.81 |
| 1d arm A touch / break | 18 / 17 | 0.76 / 0.78 |
| 1d arm B break / touch | 7 / 4 | 1.22 / 1.62 |
| 1d arm V touch / break | 0 / 0 | not defined |

`counts/CELLS.csv` (`mde_sd_holm_m`, `underpowered`) is authoritative; this table is a reading aid. 4h and 1d cannot reach the floor on 2.5 years of DEV; their line arms are dropped, not pooled across TFs (contract F3 forbids cross-TF pooling). Arm V (volume lines) is underpowered at every TF.

Sensitivity families (counted only, not powered, not confirmatory; trial-ledger variants of the primary): `wick_log_noage`, `wick_linear_age500`, `close_log_age500`. At 1h the no-age and linear families give counts within about 6 % of the primary (arm A break events 491 and 468 vs 464). The wick penetration rule (L6) rejects almost every close-series line: `close_log_age500` yields 1 line at 1h, 1 at 4h and 0 at 1d, so the close arm is **dead under contract v1**; it needs a contract version (a new L6 for close-price lines) before it can be studied.

## 4. Study design (applies when an outcome card is issued; nothing is run now)
Primary question: after a line is eligible (arm A or B), does the next contact (touch) or break change the sign-adjusted forward move of the line's own TF bar sequence, versus a matched placebo, at 1h on DEV? Sides pooled by sign (support: long on touch, short on break; mirror for resistance); per-side rows printed.

| Arm | Definition | Count status |
|---|---|---|
| line | the carried cells of section 3 | counted |
| context | line event plus one context factor from the factor module (e.g. trend with / against, vol tercile) | NOT_IN_DATA: needs the context-factor card; a context bin splits a line cell, so it is carried only if its own event-days still give MDE <= 0.30 at the final m |
| both | line event AND a horizontal level within 0.25 ATR_b of the line at the event bar | NOT_IN_DATA: horizontal level module not yet joined to this family; n <= line n by construction, same carry rule as context |
| horizontal | flat pairs (contract L7) as horizontal controls: 116 (1d), 2,276 (4h), 16,834 (1h) flat anchor pairs were routed here | candidate pairs counted; contact and break counts NOT_IN_DATA |
| placebo | each carried line event paired with a placebo line of the same slope and ATR_b, anchored at a time-shifted position (seeded random whole shift of 50..500 bars, DEV bars only), same event definition | sized equal to the line arm by construction |

Exact context and horizontal definitions come from their own cards and are added by a dated amendment to this file before any outcome is read. Until then only the `line` and `placebo` arms are runnable.

- Holm family: the carried cells of section 3 (m = 3) plus the line-vs-placebo contrast per cell; alpha 0.05 two-sided, day-clustered, one run.
- Costs: not read in this card. The outcome stage uses round-trip taker 0.14 % and maker 0.09 % (inherited unchanged from `gross_effect_screen_2026-10-15/PRE_REG.md` C_PCT, CM_PCT; OURS) plus 1 bp per straddled funding settlement while funding is NOT_IN_DATA.
- Horizon: forward move over 12 bars of the line's own TF (1h: 12 hours) as the single primary horizon (OURS, fixed now, before any outcome); 4 and 24 bars are descriptive secondary horizons outside the Holm family. Exit policy and MFE/MAE: defined in the outcome card (contract B5), not here.
- Splits: DEV above. One VALIDATION (2024-07-01..2025-06-30) check per carried cell after the DEV result and freeze; HOLDOUT read once and last.
- Kill rule: a cell whose sign-adjusted gross effect is below cost, or not distinguishable from placebo, is dropped for good with a VERDICTS.csv row.
