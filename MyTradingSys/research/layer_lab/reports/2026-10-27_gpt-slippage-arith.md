# GPT slippage arithmetic recheck

Verdict: SOUND

## Checked

- `MyTradingSys/research/gemini_burn_2026-10-25/slippage_sources.md:17-19,23-28` (requested arithmetic and adjacent friction/depth claims).
- Binance USD-M perpetual trading parameters, BTCUSDT row: https://www.binance.com/en/futures/trading-parameters/perpetual (current page lists minimum price movement 0.10 USDT; min notional 50 USDT).
- Independent calculations below. No market data arrays or backtests were used; the cited Binance page was checked directly.
- Excluded per task instruction: `REVIEW_FABLE` and `desk.py` slippage.

## Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `slippage_sources.md:17-19` | No arithmetic error. | MATCH: 0.10 / 50,000 * 100 = 0.0002%; 0.10 / 100,000 * 100 = 0.0001%. Since 1 bp = 0.01%, these equal 0.02 bp and 0.01 bp. 0.02% = 2 bp. At $50k-$100k, 0.02% is $10-$20 per BTC; divided by $0.10/tick gives 100-200 ticks. Binance row supports the $0.10 price movement. | None. Consider stating the tick values in ascending price order (0.0002% at $50k, 0.0001% at $100k) to make the relationship clearer; current range is still correct. |
| LOW | `slippage_sources.md:23` | The $500k+ within-one-tick depth assertion is NOT_IN_DATA in the repository. | NOT_IN_DATA: no repository book-depth observations or supporting evidence for this numerical claim were cited in the scoped lines. | Cite a reproducible order-book dataset and its measurement method, or label the estimate OURS and remove the empirical certainty (“never”). |
| LOW | `slippage_sources.md:25-27` | The stated spread, latency-drift, and stop-momentum ranges are NOT_IN_DATA in the repository. | NOT_IN_DATA: the file attributes spread broadly to Amberdata/Glassnode, while the latency and stop-momentum ranges have no traceable repository evidence in the scoped lines. | Add source-specific evidence and conditions for each range, or label these as OURS assumptions. |
| LOW | `slippage_sources.md:28` | 2.0 bp is a valid selected-point sum, but not a result implied by the component ranges. | MATCH for the displayed example: 0.10 + 0.50 + 1.40 = 2.00 bp = 0.02%. NOT_IN_DATA as an empirically supported total. The ranges at lines 25-27 span 1.55-2.45 bp when summed. | Say “illustrative selected values total 2.0 bp”; retain the OURS label and source or label each component estimate. |

## Conclusion

The requested tick/bp/percent/dollar/tick-count arithmetic is SOUND. The 2.0 bp bundle is arithmetically sound for its selected component values. Adjacent market-depth and component estimates lack repository evidence and are marked NOT_IN_DATA; this does not change the arithmetic verdict.

Follow-up cards created: none (no HIGH findings).
