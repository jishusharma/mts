# RESEARCH SOURCE - OI/CVD PATTERN QUESTION
# Two models asked 2026-09-16. Prompt was identical. Responses saved as
# primary source in case the summary in SESSION_LEARNINGS is questioned.

## GROK RESPONSE

1. No established name for this multi-phase pattern in literature.
   Phase 1 alone = new short openings. The full two-phase sequence has
   no recognized name in peer-reviewed work, exchange research, or major
   practitioner sources.

2. Phase 2 = new long openings per standard frameworks:
   - CVD up + OI up = new longs being opened.
   - CVD up + OI down = shorts covering.
   OI did not drop, so read as fresh long entry, not short covering.

3. Resolution requires: OI change in contract units, CVD/taker volume
   delta, funding rate sign and trend, long/short account ratio,
   estimated long/short open interest, liquidation data.
   Glassnode LPOC metrics formalize this but still need CVD overlay.

4. No documented base rate. Practitioner sources describe Phase 1 as
   building short-squeeze fuel if price stalls and CVD shows absorption.
   No forward statistics for the recovery leg on 1-3 hour horizon.

5. No clean answer. The components are standard and widely repeated.
   The multi-phase convergence is not catalogued as a distinct setup
   with predictive rules.

Sources: Glassnode 2025, Buildix 2026, Investopedia standard OI
interpretation, MarketTrace order-flow blogs. All Tier 3 except
Glassnode Tier 2.

## CLAUDE RESPONSE

1. No named pattern in peer-reviewed or exchange research. Closest is
   classical futures price/OI matrix which is Tier 3 and covers one
   variable pair, not a two-phase sequence.

2. Neither option (a) nor (b) is determinable from the three series.
   OI is symmetric. Every open contract is one long and one short.
   "Old shorts holding" is a category error. Option (b) is mechanically
   impossible while OI rises.

3. Fully resolving requires per-account position-change data. Only on
   transparent DEXs. Hyperliquid API exposes userFills -> dir with
   values Open Long / Close Long / Open Short / Close Short.
   Binance USD-M has partial fields:
   - /futures/runtime_data/openInterestHist (5m minimum, no 1m)
   - /futures/runtime_data/takerlongshortRatio
   - /futures/runtime_data/topLongShortPositionRatio
   - /futures/runtime_data/topLongShortAccountRatio
   - /futures/runtime_data/globalLongShortAccountRatio
   - <symbol>@forceOrder (liquidation stream)
   - /fapi/v1/fundingRate, /fapi/v1/premiumIndex
   - /fapi/v1/aggTrades

4. No sourced answer. No study or backtest conditions BTC 1-3 hour
   forward returns on a two-phase price/OI/CVD sequence. The one
   rigorously quantified intraday conditional effect found is return
   reversals around option expirations. Different pattern.

5. Literature does not answer question 4.

Key mechanical point: OI is symmetric. "Shorts holding" is not a state.
Only OI total. When OI rises both sides added. When OI falls both sides
closed. Price/OI/CVD cannot separate which side rotated.

Data integrity check: Giagkiozis and Said 2023/2024, arXiv:2310.14973,
Reconciling Open Interest with Traded Volume in Perpetual Swaps.
Defines minimum traded volume implied by observed OI change. Some venues
fail reconciliation. A 1200-contract OI rise the trade tape cannot
support is a data artefact.

Unit check: 107.5K in BTC or contracts or USD? Price fell 1.8 percent
in Phase 1. If OI is USD, a 1.1 percent USD change is 2.9 percent in BTC.
Changes the conclusion materially.
