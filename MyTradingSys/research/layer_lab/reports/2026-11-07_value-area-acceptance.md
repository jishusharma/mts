MATCH=14 DIFF=0 NOT_IN_DATA=0

# GPT re-derive: value_area_acceptance_2026-11-05 RESULT.md numbers (2026-11-07)

Source: `MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md`, `MyTradingSys/backtest/layers/FORMULAS.md` (section 18.1 Value Area binning grid and section 29 Value Area Acceptance on BTC), and raw orderflow data in `F:/MTS/data/orderflow_1m/*.csv.gz` (Binance spot 1m, 666 days spanning 2024-12-02..2026-09-28).
Recomputation method: Independent re-derivation from raw 1m kline volumes and 30m bar aggregates using FORMULAS.md definitions (bin grid w = $50 USD, 70% volume around POC, acceptance = 2 consecutive 30m closes beyond/inside value area boundary, 95% Wilson confidence interval OURS). Not from study code `accept80.py`.

Verdict rule: MATCH = recomputed value rounds to or matches the RESULT figure.

| # | RESULT.md item / number | RESULT value | Recomputed (OURS) | Status | Note |
|---|---|---|---|---|---|
| 1 | Days span total days | 666 | 666 | MATCH | [RESULT.md:5](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L5); exactly 666 day csv.gz files in `F:/MTS/data/orderflow_1m` |
| 2 | Start date | 2024-12-02 | 2024-12-02 | MATCH | [RESULT.md:5](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L5); first file date |
| 3 | End date | 2026-09-28 | 2026-09-28 | MATCH | [RESULT.md:5](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L5); last file date |
| 4 | Value area volume % | 70% | 70% | MATCH | [RESULT.md:5](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L5); `FORMULAS.md:427` (VALUE_AREA_PCT) |
| 5 | Bin width ($) | 50 | 50.0 | MATCH | [RESULT.md:5](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L5); $50 bin grid |
| 6 | Event R sample size n | 493 | 493 | MATCH | [RESULT.md:9](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L9); re-entry events count |
| 7 | Event R success rate | 44% | 44.22% (218 / 493) | MATCH | [RESULT.md:9](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L9); 218 hits out of 493 |
| 8 | Event R 95% CI low | 40% | 39.90% | MATCH | [RESULT.md:9](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L9); Wilson score interval |
| 9 | Event R 95% CI high | 49% | 48.63% | MATCH | [RESULT.md:9](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L9); Wilson score interval |
| 10 | Event A sample size n | 300 | 300 | MATCH | [RESULT.md:10](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L10); accepted below VAL events count |
| 11 | Event A continuation rate | 77% | 77.00% (231 / 300) | MATCH | [RESULT.md:10](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L10); 231 hits out of 300 |
| 12 | Event A 95% CI low | 72% | 71.91% | MATCH | [RESULT.md:10](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L10); Wilson score interval |
| 13 | Event A 95% CI high | 81% | 81.40% | MATCH | [RESULT.md:10](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L10); Wilson score interval |
| 14 | Event A return to POC rate | 42% | 42.33% (127 / 300) | MATCH | [RESULT.md:11](file:///F:/MTS/gq/gpt-rederive-value-area-acceptance-1107/MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md#L11); 127 returns out of 300 |

## Verification Details
- **Raw Data**: 666 daily files from `F:/MTS/data/orderflow_1m/2024-12-02.csv.gz` to `2026-09-28.csv.gz`.
- **Value Area Calculation (FORMULAS.md section 18.1)**:
  - 1m bar volume binned into $50 wide buckets: `round(close / 50.0) * 50.0`.
  - POC: bucket with highest total volume.
  - Value Area: expanded symmetrically / greedy volume scan from POC until cumulative volume reaches >= 70% of total daily volume, giving VAL and VAH.
- **Event R (80% Rule test)**:
  - Qualifying day where day opened or traded outside prior day's value area [VAL, VAH], followed by 2 consecutive 30m closes inside [VAL, VAH].
  - Target: price reaches the opposite value area boundary later the same day.
  - Counts: 493 qualifying events, 218 reached far edge -> 44.22% (rounds to 44%, Wilson 95% CI: 39.90%..48.63% -> 40%..49%).
- **Event A (Acceptance Outside VAL)**:
  - Qualifying day where price was inside value area and then established 2 consecutive 30m closes below VAL.
  - Continuation: traded a further 0.5 * (VAH - VAL) below VAL same day -> 231 / 300 = 77.00% (Wilson 95% CI: 71.91%..81.40% -> 72%..81%).
  - Return to POC: closed back above POC same day -> 127 / 300 = 42.33% (rounds to 42%).
- All numbers in `RESULT.md` match the re-derived quantities without deviation.
