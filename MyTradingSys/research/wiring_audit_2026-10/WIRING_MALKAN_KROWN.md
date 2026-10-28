# Wiring audit: Malkan, Krown (every sourced rule vs layer code, params, tests)

Card `extracted-rules-wiring-audit`, 2026-10-28, MTS_Doctor (Sonnet). Read-only: no layer code, params or backtests changed. Sibling: `WIRING_TOM_FABIO_HABIB.md`.
Table: `WIRING_MALKAN_KROWN.csv`. Rebuild: `build_wiring_malkan_krown.py` (verdicts are its hand-made tables; quotes, file:line and counts are computed). Quotes checked with `scripts/dev/verify_extract_quotes.py` on `QUOTES_USED_MALKAN_KROWN.md`.

## 1. What a row is
- Krown: one row per rule of the ledger `KROWN_RULES.csv` (131 rules, KR-T01..KR-LQC04); the 16 setups KR-S1..KR-S16 of `KROWN_SETUP_CATALOG.md` are built from these rules and cite them by id, so every catalog rule is counted once. Quote = the first quote under the rule's first source concept id in the extracts (`extracts/extract_<video>.md:<line>`). 22 of 131 rules are REJECT (16) or BLOCKED (6) in the ledger; they get not-worth-wiring or, where the block is only missing code, unwired, with the reason.
- Malkan: one row per rule bullet of `MALKAN_DIVERGENCE_GLOSSARY.md` section 2 (2.1 to 2.9), 36 rows. Only his sourced PRD/NRD counts; generic hidden divergence is a Krown rule (operator 2026-10-28), kept in `rsi/krown_hidden_divergence.py`. Quote = the glossary quote block (its extract cite is in the note). Hindi originals are not separate rows. `SETUP_CATALOG.md` itself holds no Malkan rule (0 mentions); it covers Tom and Fabio (sibling card).
- Malkan rules outside these three documents (the 40/60 regime and bounce setups `rsi/malkan_40_60.py`, `rsi/malkan_mtf.py`, from `malkan_rsi_2026-09-28/WEB_RESEARCH.md`) are wired and tested but not rows here; listed in section 5.
- Verdict: `wired` (extent `full` = the rule as he states it is coded; `partial` = a stated part is missing, see note); `unwired-worth-wiring` = mechanical, data we hold, not coded; `not-worth-wiring` = philosophy, sizing, execution, needs L2/option data we do not hold, or no mechanic. Wiring means a pre-registered test first, never a live change.
- Param labels: SOURCED = his number; OURS = our choice (never his). Krown thresholds in `krown/params/krown_params.json` carry their label per key. Layer flag `enabled=false`: alert-only, no live wiring.
- Priority of unwired rows: Krown H/M/L = rule stated in 4+ / 2-3 / 1 videos (`n_videos`, how strongly he stresses it); Malkan rows are M (the glossary marks most as one video, UNVERIFIED).

## 2. Counts by verdict

| Trader | wired (full) | wired (partial) | unwired-worth-wiring | not-worth-wiring | rows |
|---|---|---|---|---|---|
| Malkan | 8 | 13 | 11 | 4 | 36 |
| Krown | 32 | 28 | 32 | 39 | 131 |
| **all** | 40 | 41 | 43 | 43 | 167 |

Reading: Krown's v0 layer codes zones, trend state, volume, candles, averages, BBWP, ranges and the four-signal top; it has no trend-line code, no exits and no weekly 200 SMA, which is where most unwired rows sit. Malkan's divergence core (regular, PRD, NRD with the 60/40 regime, bar window, chain) is coded and tested; his confirmation, stop and target are not (the backtest uses a flat 1%/2% bracket).

## 3. Top 10 unwired-worth-wiring (by how strongly he stresses it)

| rank | id | videos | rule | what is missing |
|---|---|---|---|---|
| H1 | KR-T07 | 6 | Range tell: flat tangled averages plus shrinking volume | flat tangled averages plus shrinking volume as a range tell: not coded (range_state uses highs/lows only) |
| H2 | KR-Z09 | 5 | Role flip | role flip (broken support becomes resistance): no detector; S2 stops at the break |
| H3 | KR-Z10 | 4 | Break, wait, retest routine | break, wait, retest routine: S2 fires on the break close only; retest leg not coded |
| M4 | KR-L12 | 3 | In a sideways range favour the previous trend | in a sideways range favour the previous trend: not coded |
| M5 | KR-M05 | 3 | 21 and 55 EMA as dynamic support | 21/55 EMA band as dynamic support (KR-S5 variant): not coded |
| M6 | KR-R05 | 3 | Bias from the structure inside the range | bias from the structure inside the range: not coded |
| M7 | KR-Z16 | 3 | Confluence: static zone plus rising average | confluence of a static zone with a rising average: no code joins zones and averages |
| M8 | KR-M03 | 2 | The 200 SMA reacts on first contact | first contact with the 200 after a long absence (KR-S5 variant): not coded |
| M9 | KR-M11 | 2 | Slope of an average = strength of the trend | slope of an average as trend strength: not coded |
| M10 | KR-Q06 | 2 | Volatility-based profit taking | volatility-based profit taking: no exit logic in the layer |

Malkan unwired, in order of fit with the existing layer: D05/D11 candle confirmation, D06 stop above the high incl. shadow, D07 target at point C, then D15 RSI level near 40/60 on regular divergence, G02/G03 monthly-60 gate on divergence.

## 4. NO_QUOTE
Rules whose source ids (LQC, liquidation episode) have no quote block in the extracts (kept, verdict from the ledger text and the code):

- KR-LQC01 Anatomy of a liquidation cascade and domino effect: liquidation cascade anatomy: not coded; needs liquidation feed (check data availability first)
- KR-LQC02 Liquidation weather: funding rate and open interest: funding rate and open interest as liquidation weather: not coded; funding history exists for backtests, OI history not checked
- KR-LQC03 Deleveraging flush and V-shaped recovery pattern: deleveraging flush recovery pattern: discretionary description
- KR-LQC04 Liquidation risk defense and distance: liquidation risk defence and distance: sizing / leverage advice

## 5. Findings for the operator
- Every wired Krown core function and PRD/NRD (`test_div_flags_chart.py`) has a unit test; a test that pins a number to his quote exists only for the Malkan bar window (`test_params_file_matches_sourced_values`).
- Wired but unused: `mature` zone flag (KR-Z13), `vol_half` (KR-V10), doji (KR-C07): computed, consumed by no setup.
- A conflict between the layer and his words: zones expire after 250 bars in code (OURS) while KR-Z06 says they do not.
- Outside the three documents: `rsi/malkan_40_60.py` (MLK-R1, S1, S2) and `rsi/malkan_mtf.py` (MLK-GAP1) are wired with tests `test_malkan_40_60.py`, `test_malkan_mtf.py`.

ROWS: 167
