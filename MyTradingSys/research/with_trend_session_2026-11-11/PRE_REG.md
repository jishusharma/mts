# PRE-REGISTRATION: with-trend session trades (card with-trend-session-census-1111), frozen 2026-11-11 before any return is computed

Edge lead (Sonnet). Operator ask: "naked" Tom/Fabio trades on the everyday chart by session, directional, built on what happened before; the fades all lost (CENSUS_5M15M_1109.md: -0.106 R, n 1,484), so test the two with-trend shapes they never covered. Method: phase-first (d-phase-first-method-1106): a diagnostic census here, the proof is testnet-forward. Labels: SOURCED = cited, OURS = chosen here, frozen. Changing any parameter after a result = a new trial.

## Context
- Regime: 7 years pooled (2019-11-08 .. 2026-11-10), ladder D/W/M as census_session_ladder.ladder_maps; the headline split is by year and by ladder regime (bull/range/bear, D close vs SMA20 +-2 %, OURS). Printed as `Regime mix:` with window days per regime.
- Phase: two buckets, `range_1024` (days from 2026-10-24, Bible range) and `rest`; the range bucket is reported, never judged.
- Session: UTC blocks of the entry bar, OURS, as C59: Asia 00-07, London 07-13, NY 13-21 (late 21-24 is reported as a fourth row, never judged).
- Entry: a closed-bar signal, MARKET entry at that bar's close = taker (honest); the Deribit maker-entry arm is the optimistic bound, reported second.
- Data: Binance BTCUSDT 5m rebuilt from data.binance.vision (futures/um 2020+, spot 2019), 15m built from three closed 5m bars; closed bars only. No order flow used.

## Size rule (EDGE_PLAN a, OURS)
Planned move >= 500 USD per BTC and stop >= 40 bp. Price moved 4k..126k in 7 years, so a fixed USD amount is a different cost in bp: the 500 USD floor is carried as 62 bp (500 / 80,000, OURS conversion) of entry. An event whose structural stop is under 40 bp is SKIPPED and counted (never widened: widening would be tuning).

## Shape A: acceptance continuation in the bias direction
| Item | Frozen value | Label |
|---|---|---|
| Levels | prior UTC day VAH/VAL/POC from auction_census.build_levels (as the 1h/15m census) | OURS (as census) |
| Bias | long needs D = +1 AND W = +1; short needs D = -1 AND W = -1 (census_session_ladder.ladder_maps; M reported, not required) | idea SOURCED Tom TOM-053; lengths OURS |
| Event | FIRST time in a UTC day that 4 consecutive CLOSED 15m bars all close above prior-day VAH (long) or below VAL (short), starting on a bar that opens inside the day's session block (Asia/London/NY); acceptance over 1 h | OURS (acceptance 12x5m is SOURCED in kind, PM:107) |
| Entry | close of the 4th bar, market | OURS |
| Stop | long: the lower of VAH and the lowest low of the 4 acceptance bars; short: mirror; no buffer. Skip if distance < 40 bp of entry | structural OURS; 40 bp = EDGE_PLAN size rule |
| Target | entry +- 2 x risk (so target >= 80 bp >= the 62 bp floor); skip if target would be < 62 bp (cannot happen at stop >= 40 bp, asserted in code) | OURS |
| Management | none; same-bar stop and target: stop first; time stop at close of bar 96 (24 h) | OURS |
| Cooldown | one event per direction per UTC day | OURS |
| Fees | model T = fees.FEES_ALL_TAKER (5 bp/side) + fees.SLIPPAGE_RT_S13 (2 bp RT) = HEADLINE; model D = fees.FEES_DERIBIT + same slippage = optimistic. No cost literal in code | SOURCED fees.py |
| Net R | (gross return - cost) / (stop distance as a fraction of entry) | OURS |
| Random-entry control | for every event, 200 random draws: same UTC day, a random closed 15m bar inside the SAME session block, same direction, same stop distance and 2R target taken from the entry (no level information); control mean = mean over draws; fraction of draws with mean net R >= the event mean reported (seed 1111) | OURS |

## Shape B: Opus "trend pullback to value", exactly as written (OPUS.md section D1, four_model_review_2026-11-11/OPUS.md)
Copied verbatim, all on closed bars, long only (shorts reported only, none traded):
1. 4h ADX14 >= 20 and DI+ > DI-. 2. ADX 5-bar slope >= 0. 3. PHASE_LABEL not BEAR or PEAK_WINDOW (eh-o2-phase-lens/phase_label.py). 4. The signal bar's low inside [prior-day VAL, prior-day POC] (UTC-day 70 % profile). 5. Trigger: the C30 H2 rule unchanged (15m WT buy dot <= -53 + RSI bull divergence, PRE_REG_C30.md frozen, including the 2h-trend condition of H2). 6. Entry: maker limit at the trigger close; no fill within 3 bars = no trade. 7. Stop: the lower of the divergence second pivot low and VAL, no fixed % floor. 8. Arm A: C30 X1 exit unchanged. Arm B: target prior-day VAH, BE at +1R, skip if VAH < 1.5R away.
Sample per OPUS.md: BTC 15m, DEV 2022-01-01 .. 2024-06-30 ONLY (HOLDOUT from 2025-07 and VALIDATION 2024-07..2025-06 never loaded). STEP 1 count pass with no returns (events by phase, ADX state, session); if n < 30 on DEV: stop, Shape B goes to the testnet-forward slot with no return computed, and the result says INSUFFICIENT n. If n >= 30: arms A and B net R under fees.FEES_DERIBIT + slippage, taker arm, C30 trigger alone on the same bars for the "beats the trigger alone by 1 SE" test, 30 random entries under the same gates. Holm m = 2. Size rule: Shape B stops under 40 bp are NOT skipped here (exactly as written; reported in a separate column as BELOW-SIZE-RULE).
Refuted if any: arm A or B net R <= 0 maker; taker net R <= 0; not beating the trigger alone by 1 SE; not beating the random entries; (testnet: net R <= 0 after 30 trades).
Known curve-fit flags (OPUS.md): the H2 trigger was best of ~250 cells, so its +0.22 % is inflated; ADX 20, 4h, slope window, lower-half VA fixed and never swept.

## Kill line (Shape A, per session and pooled)
EDGE only if headline (taker) mean net R > 0 AND > 2 SE AND the Deribit arm > 0 AND the event mean beats at least 95 % of random draws. n < 100 in a cell = INCONCLUSIVE, never a pass. Nothing is promoted by this census; a pass would only earn a forward slot. A FAIL is reported plainly as FAIL.

## Run
`with_trend_census.py` (this folder) reads the 5m cache built by census_fetch_mirror.py (F:/MTS/data/edge_1111_5m, not committed), writes `RESULT.md` and `result.json`. Tests in this folder; each fails on a stub. This file's commit precedes every result file.
