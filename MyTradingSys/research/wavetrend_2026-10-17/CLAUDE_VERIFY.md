# Claude verification of the GPT WaveTrend research (2026-10-17, card wavetrend-verify)

Method: re-opened the cited pages with WebFetch on 2026-10-17 (summaries by a small model, so figures were checked as printed strings, not from raw HTML), read the repo files, grepped the repo. No backtest was run; REPORT.md contains no number computed by GPT itself, so there is nothing to recompute from repo data (all numbers are publisher figures, re-read at the source). Labels: VERIFIED / WRONG / OVERSTATED / UNSUPPORTED / NOT RE-CHECKED (budget; not a doubt).

## VERDICT: FIX-FIRST (small). The research is a sound hypothesis list, no edge claim is made. Five documentation fixes and four plan corrections (section D) go into the next cards before any code.

## A. Sources and quotes

| Claim | Label | Evidence |
|---|---|---|
| LazyBear 2014 page: sell = oscillator above overbought crosses down the signal; buy = crosses up below oversold; page gives no defaults | VERIFIED | page text: "above the overbought band (red lines) and crosses down the signal"; "crosses above the signal when below the Oversold band"; published May 27, 2014; no parameter values on the page |
| Defaults 10 / 21, OB 60 / 53, OS -60 / -53, source hlc3, wt2 = sma(wt1, 4), created 2015-01-12, 2 stars, 1 fork, header credits LazyBear | VERIFIED | gist marketcalls/f9c795c7d5ba0f988761 (inputs quoted). The 0.015 coefficient and `d = EMA(abs(ap-esa), n1)` were not echoed by the fetch; they match T061 and the report, so SOURCED only by the gist file, to be confirmed at file:line by the parity card |
| Formiq: 30 combos, 10/21 H1 +3,283.4 pips (867 trades, 2025), +1,076.6 (2024), 30/30 profitable 2025, 24 both years, none on M15, 0.3 pip spread, published 2026-08-24 / updated 08-30 | VERIFIED | all strings match. Report's "won" = "profitable": fine. Gross-of-slippage FX result; report rightly says no BTC transfer |
| Freqle: 33 pairs, futures, 20220101-20250101, 7,893 trades, -90.18 %, PF 0.75, 81.1 % wins, 0.05 % per side, 9/12, SMA 3, entry WT2 beyond -/+80, exit beyond +/-60 | VERIFIED | page table + code. "Trading ends July 2023" PARTLY: last ledger entries 2023-06-30 / 07-01. "5m from sandbox default": VERIFIED (page says so). Page also flags "edge below fee" |
| Quantroduction: audited 2026-09-12, window to 2026-09-14, 7 markets, 15m, from 2023-07-15, median -24.9 %, B&H +49.6 %, 0 of 7, 3,562 orders | VERIFIED | page ("7 markets x 3.2 years ... 111,044 bars of 15m"); page says correctness, not profitability. The date oddity (audit before window end) is real and unexplained |
| TrendCrypto2022 BTC strategy: long when WT1 crosses over WT2 below a limit, stop at lowest of previous 3 bars, R:R 1:1.5, no backtest on page | VERIFIED | quotes "Long when Wavetrend1 crossover Wavetrend2 and they are less than a limit value", "Stoploss at lowest 3 bar previous", "R:R = 1:1,5". Page date May 5, 2022. The limit has no numeric default on the page, so "configurable limit" is right and any number is OURS |
| Maydo Market Sniper 9/12, volume multiplier 2, lookback 60 minutes | VERIFIED | quotes match; date 2023-06-07 (report says date not visible: harmless). "Protected script" not re-checked |
| jadamcraig VWMA: size multipliers 1/2/4, session limit | VERIFIED | page opens, May 6 2021. **EVIDENCE_REVIEW.md lists this URL under "direct page retrieval failed" while EXTERNAL_SETUPS.md lists it as opened (S09): internal contradiction, EVIDENCE_REVIEW entry is the wrong one** |
| ClassicScott: lookback 55 and default 6, 14 suggested, "bias / pullback to centerline" family C | **OVERSTATED** | author says "one plot with a lookback period of 55, and another with the default set to 6"; coloured bar on centerline cross; 14 as slower option; divergence added 2021-12 / 2025-04. The "55 = momentum bias, 6 = entry, dip toward centre in bias direction" rule is the report's reading, not the author's. Mark family C entry logic OURS |
| "Above the long oscillator's zero line" | WRONG wording | the author says "centerline"; WT has no zero-line statement |
| S03 thomcam, S06-S08 (christofferka/Adonis details), S10-S15, S16 binhna gist, S17-S19 platform docs, S20 Reddit, two extra Reddit threads, Deribit funding page, Bailey et al. PBO paper, TradingView repainting doc | NOT RE-CHECKED | no reason to doubt; all are T3 definitions or platform docs and none carries a number the plan depends on |
| "20 distinct pages opened, 14 TradingView" | UNSUPPORTED as a count that matters | row list has S01-S20; S01-S15 are 15 rows of which 14 TradingView + 1 gist, consistent. The count has no decision value |
| Raw TradingView counters (e.g. "60.8K 301 301") | OK as labelled | report refuses to call them reviews; keep that |
| Zero T1/T2 WaveTrend efficacy evidence | VERIFIED as a scoped claim | the three efficacy sources (Formiq, Freqle, Quantroduction) are publisher T3 and conflict (positive FX H1, negative crypto) |

## B. Numbers in REPORT.md

REPORT.md carries only publisher figures (above) and the author parameter set. No event rate, hit rate or fee-net number of GPT's own exists, so there is nothing to recompute. Parameter provenance for the plan: 10/21/4, hlc3, +/-53, +/-60 SOURCED (gist file, third-party mirror of LazyBear's code; the live TradingView source was not read). Everything else numeric (55/6/14, 9/12, 9/12 with SMA 3, +/-80, 2x/60 min, 1:1.5) is another author's value, SOURCED to that author only. All excursion cut-offs, depths, dwell, regime labels in the "atlas" are OURS and not yet defined.

Repo claims re-checked: no WaveTrend implementation exists (git grep of *.py/*.java finds only docs and the audit scripts that cite it) - VERIFIED. `backtest/layers/FORMULAS.md` has no WaveTrend entry - confirmed; T061's "write the FORMULAS.md entry first" is still open. T061 split 70/30 and 0.10 % RT fee are obsolete - VERIFIED against SPLIT_ALIGNMENT_2026-10-17.md (repo split: DEV to 2024-06-30, VALIDATION 2024-07-01..2025-06-30, HOLDOUT from 2025-07-01).

## C. Look-ahead, split, fees

No study was run, so there is no leak in the report. Risks in the proposed plan (not in the data):
1. The atlas says "discover ranges on DEV". Allowed (OURS, DEV, checked once on VALIDATION), but each DEV read must be logged in `research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv` (plan rule 5); the report does not say so.
2. "Full excursion maximum / dwell / later regime label" are named as outcomes, not features: correct and must be enforced in code by a test (feature at bar t uses bars <= t only; HTF value from the last closed bar).
3. Splits: use the repo split only; the bigtrade fire CSVs carried the old 2024-07-01 TRAIN end until relabelled today, so any WaveTrend join with fire CSVs must re-derive the split from timestamps.
4. Fee-net numbers belong to the event-study stage (G5); a gross atlas with MFE/MAE must say "gross".

## D. Against LESSONS / G0-G6 (corrections to the plan)

1. **Atlas scale is not one study.** Six behaviours x 5 timeframes x regimes x 2 sides is hundreds of cells. LESSONS require counts before freezing and MDE/Holm: freeze a short cell list (<= 12) from a count-only pass first; then one pre-registered DEV run. OVERSTATED: "the next empirical deliverable is a behaviour atlas" without that pass.
2. **Control arm.** Every cell needs a random-clock / same-location-without-WT arm, as the gross_effect_screen control (arm C, n = 1,439, mean -0.008 %, t_cost -6.0) showed that a plain location rule can have no gross edge. The report asks for "context alone" but not a random-clock baseline; add it.
3. **Gate mapping.** G0-G4 (extraction, catalogue, eye-read marks) apply to trader-sourced layers. WaveTrend is a T3 mechanical indicator, so: G0/G1 = source snapshot + formula quotes (this verification covers the external part), G2 = written PRE_REG (not an eye-read), G3 and G4 = fixture-tested observation module, G5 = DEV study, G6 = VALIDATION once, HOLDOUT sealed. No encode before the PRE_REG and the count-only pass.
4. **Trial ledger / verdict alias.** `verdicts.py check` matched nothing for "wavetrend wave trend lazybear"; the PRE_REG must add aliases (WT, wave_trend, LazyBear, cipher) and every variant (A, B, C, bands 53 vs 60) goes in the ledger as its own trial.
5. **Overlap / effective n.** Band-region dwell produces clustered events; count independent episodes (days or first-arrival episodes), MDE in realised terms.
6. **Priority vs park.** The control-room park text ("no new layers while Tom/Fabio are redefined") is superseded by the operator's 2026-10-17 priority request. Defaults taken: proceed, but bounded to source + count-only + one DEV study; no Tom/Fabio dependency. Logged here.

## E. Report fixes (to do inside card wavetrend-priority-source-parity, step "Reconcile")
1. EVIDENCE_REVIEW.md: remove jadamcraig from "failed retrieval" list (page opens).
2. EXTERNAL_SETUPS.md family C: relabel entry/bias logic OURS; "zero line" -> "centerline"; family B limit value = no source number.
3. EXTERNAL_SETUPS.md: Freqle "Trading ends July 2023" -> last trades 2023-06-30/07-01.
4. REPORT.md: add the EXPOSURE_LEDGER and random-clock control requirements (D1-D2).
5. Pin 0.015 and the d formula to a gist line number.

## Cards filed (all SONNET, S/M, gate order; none runs a backtest)
1. `wavetrend-priority-source-parity` (existing, d93fef5e, untouched): source/parity contract, report fixes E1-E5.
2. `wavetrend-prereg-counts`: count-only PRE_REG on DEV (event counts, episodes, MDE), freeze <= 12 cells, controls, aliases.
3. `wavetrend-observation-module`: causal module + independent fixtures + look-ahead test. Depends on 1.
4. `wavetrend-dev-atlas`: one DEV run per the PRE_REG (gross, with controls). Depends on 2, 3. VALIDATION/HOLDOUT not read.
