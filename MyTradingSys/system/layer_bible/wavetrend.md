# Layer Bible: WaveTrend (family `wavetrend`) | v0 2026-11-04: design ACCEPT (Gemini 3.8 Flash re-check, research/layer_bible/RECHECK_GEMINI_1104.md); numbers not yet re-derived by Haiku; operator confirmation of "cycle ends at the last valid top" pending
One source of truth for WaveTrend. Every other WaveTrend file is secondary and points here. Runtime: `python scripts/dev/layer_state.py wavetrend`.
Answer rule: state questions quote the `layer_state.py` output and its STAMP line; no stamp = "not computed".

## Definition
- Formula (SOURCED, LazyBear "WaveTrend with Crosses", `research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:14-21`): `ap=(h+l+c)/3; esa=EMA(ap,10); d=EMA(|ap-esa|,10); ci=(ap-esa)/(0.015*d); wt1=EMA(ci,21); wt2=SMA(wt1,4)`. Detail and worked numbers: `backtest/layers/FORMULAS.md` s20; code `backtest/layers/wavetrend/wavetrend.py`.
- Bands (SOURCED, Pine :9-12): ob1 53, ob2 60, os1 -53, os2 -60; centre 0 (:23).
- Cross (OURS, FORMULAS s20.2): an event at the first bar strictly on the other side of wt1-wt2; ties skipped.
- Valid dot (OURS, from FORMULAS s20 zones and `research/wt30_sequence_2026-10-30/study.py` dot definition): a cross whose wt1 on the bar BEFORE the cross is at or beyond the band (the study definition: `study.py` T1/T2 use wt1[t-1]). Up-cross with prior-bar wt1 <= -53 = valid bottom dot; down-cross with prior-bar wt1 >= 53 = valid top dot. Any other cross is NOT a valid dot.
- Cycle (operator words below; the +-53 requirement on the turning dot is OURS): starts at a valid bottom dot (up-cross from the lower zone). It is COMPLETED once a valid top dot (down-cross at the top) prints; no new cycle starts until the next valid bottom dot.
- Closed bars only; warm-up 200 bars (OURS, PARITY_CONTRACT s3).

## Parameters (read by the runtime; edit here, nowhere else)
```json layer_state
{"family": "wavetrend", "symbol": "BTCUSDT", "source": "data-api.binance.vision",
 "tfs": ["1m", "3m", "5m", "15m", "30m", "1h", "4h"], "bars": 1000, "dot_band": 53, "dot_basis": "prev_bar"}
```
Labels: formula, 10/21/4, 0.015 and the +-53/+-60 bands SOURCED; dot_band use as the dot filter, 1000-bar window, the TF list OURS.

## Operator rules
- 2026-11-04 ~13:30Z, voice (relayed by the coordinator, d-layer-bible-runtime-1104): "the wave[trend] has crossed from down and it has reached up. So that's why I'm calling it a start of a cycle. And it continues all the way, and on the second arrow that I have drawn down, that's where I'm calling it that it ends there."
- 2026-11-04 ~13:50Z, voice (30m Bitstamp shots 445d03cb17c0 and dd97b217eee8; relayed by the coordinator), verbatim: "after it has gone up from the lower band, and it touches the red bands and it tries to come down to the center but does not come down, and then after making 3 waves and finally when it comes down the zero line and goes up again ... the price is so high compared to the previous high. So you can see the divergence in the wavetrend. That signals a clear shot, and the confirmation is the green line coming down. So that is the only trade which is the best trade in this whole setup, and that's what we have to anticipate." Example: the 11-02 ~03:00-04:30 short. Then: "understand how to apply different time frames context together ... use the historical data ... design tasks that really make sense ... for backtesting." Designs: `research/wt_bible_studies_2026-11-04/SPEC.md`.
- 2026-10-17 (`research/wavetrend_2026-10-17/OPERATOR_DIRECTION.md`): do not apply WaveTrend to everything; context and confluence decide; generic crosses are controls.
- 2026-10-22 (wt30 trigger shots): "buying in a downtrend is invalid" (tested as the trend gate, see Findings).

## Findings (as reported in the source file; trust UNCHECKED by Lab_Guy unless a re-derivation is named)
| claim | n / stat | window | source |
|---|---|---|---|
| 30m top dot (>=53): +1% first 53% vs -1% first 42%; with 4h WT up 56% | 465 | DEV 2022-01..2024-06 | `research/wt30_sequence_2026-10-30/RESULT.md` |
| 30m bottom dot (<=-53): up 4h 57%, then -1% first 48% vs +1% 43% | 422 | same | same |
| rejection at 0 from above (T8): up after 12h 40% (about 2.5 SE below base); from below (T7) 59% up but -1% first 50% | 163 / 152 | same | same |
| centre crosses carry no information | ~1,100 each | same | same |
| bare dots lose fee-net everywhere (15m/30m/1h, buy and sell); 126 of 509 cells with n>=30 have a net CI wholly below 0, none wholly above | 509 cells | DEV, fee 0.14% | `research/wavetrend_c30_retest_2026-11-04/RESULT.md` |
| trend gate helps SELL dots, hardly BUY dots; part of it is bear-window drift | see source | DEV | same |
| C30 retest + confluence: 0 survivors of 24 pooled + 96 session cells; INCONCLUSIVE (underpowered), VALIDATION unread | m=24/96 | DEV | same (BLOCKED.md) |
| frozen atlas: 4 FAIL, 5 INCONCLUSIVE; W07/W08 invalid (pre-correction) | 9 cells | DEV | `research/wavetrend_2026-10-17/RESULT.md`, `LIVE_NOTE_2026-10-27.md` s2 |
No validated edge, no live integration, never a core gate (PROJECT_VISION s2/s4).

## Candidates (not Findings: unregistered, scratch, overlapping events; one Haiku recount queued: card wt30-div-blind-recount-haiku-1104)
- 30m lower-high divergence short (OURS rule in SPEC.md Card 1), coordinator scratch 2026-11-04 on 2020-01..now BTCUSDT 30m: n=1219 net -6.1 bp at 12 h; operator-context subset n=975 -3.4 bp; 2020-22 +8.9 bp, 2023-26 -12.0 bp. CAUTION: the window runs past DEV_END (2024-06-30), into VALIDATION and sealed HOLDOUT bars; unusable as evidence until re-run on splits.py windows.
- Cycle frequency per week (full cycle bottom-zone up-cross to top-zone down-cross): 5m 6.1, 15m 2.1, 30m 1.1, 1h 0.6, 4h 0.1; median length 4.9 h, 17.8 h, 29.5 h, 57 h, 240 h; only 13-15 % of crosses are zone dots. Same window caveat.
- Example for the runtime: the 30m up cycle from 2026-11-02 19:30 (wt1 -71) has no valid top dot yet (the 11-03 cross printed +52.1): second `layer_state.py` test case.

## Corrections
- 2026-11-04: an answer gave "new cycle at 12:21" on 3m. 12:21 is an up-cross at wt1 -49.3 (prior bar -50.9): not a valid dot (OURS, band rule; the cross-bar basis gives the same answer), so no new cycle. Cause: no runtime applied the rule; answered from memory.

## Open (OURS defaults, the operator can overrule)
- Which top dot ends the cycle: on 3m, BTCUSDT 2026-11-04, bottom 03:12 (-74.0) has valid tops at 05:03, 05:54, 07:33 and 11:39; he drew the end at 11:39. The runtime reports the full list and the LAST valid top before the next bottom; it does not pick "first". Needs his confirmation.
- Dot basis: prior-bar wt1 (as the studies) versus the cross-bar wt1 (what the chart dot sits on); same result on the 11-04 case, may differ elsewhere; param `dot_basis`.
- Intermediate crosses inside a cycle (e.g. 04:21 down at 44) do not end it.

## Status
Family row: `system/layer_index.json` (`wavetrend`); layer map LAYERS.md. Secondary files (to archive after review, never deleted): see `research/layer_bible/ARCHIVE_PLAN_wavetrend.md` (phase 3).
