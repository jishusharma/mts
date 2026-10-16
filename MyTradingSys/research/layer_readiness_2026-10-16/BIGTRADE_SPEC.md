# BIGTRADE_SPEC - row 13 bigtrade_fires / volume_candles_ma

STATUS: **NO-SOURCE**. No trader-sourced, causal detector exists, so nothing was built (no detector, adapter, registry or config change).
Date 2026-10-16, task bigtrade-spec-build. Follows HANDOFF_W2b.md (W2b: fires_kline.py is a replay harness, bigmoves.py is look-ahead).

## What "bigtrade" is in this repo
- `bigtrade` is our own analysis project name (research/bigtrade_2026-10-09/PLAN.md): a hindsight "big leg" ground truth (bigmoves.py) plus a replay of
  already-live layers (fires_kline.py). Neither is a trader's setup, so it has no trader words to quote. Per the Numbers rule it cannot be called SOURCED.
- "volume_candles_ma" is a family label in LAYERS.md (volume, candle patterns, daily MA). Its members: volume (no validated edge, HOLDOUT sealed),
  candle_patterns (pilot, no edge vs null), ma_daily (NO-SOURCE), candle_close (0 of 126 arms), bb_top_reversal (unrun).

## Search done (all negative for a causal volume-candle/MA rule)
| Place | Result |
|---|---|
| research/bigtrade_2026-10-09/* | our own backtest plan/reports; hindsight labels |
| setup_catalog_2026-10-15/SETUP_CATALOG.md, ANGLE_TRADE_CATALOG.md | "big trades" = Fabio/Tom order-flow bubbles (aggTrades size filter; Fabio's own words are "30 contracts", London 20, DyS79Eb92Ug_raw.txt:681-683; the gLHd "30 to 40 on NQ" slide is secondary, H6); BTC size is OURS (99th pct, V3); not a volume candle + MA rule, and "big trade" is undefined for BTC (CATALOGUE_AUDIT.md:19) |
| volume_2026-10-09/VOLUME_RESEARCH_REPORT | traders give no numeric volume rule; every threshold NO-SOURCE-TRADER; 0 pass triage |
| krown_ta101 catalog | KR-S7 capitulation hammer on biggest-volume bar (weekly/daily, provisional, lookback OURS, no stop given; Krown is deferred); "heavy volume = double or more the recent volume bars" is a trend-line rule, not an entry |
| F:/MTS/data/bigtrade | data/fires from our own replays, no transcripts |
| MA rules | ma_daily = NO-SOURCE (chatbot handoff numbers) |

## Parameter table
| Parameter | Label | Note |
|---|---|---|
| "heavy volume" = >= 2x recent volume bars | SOURCED (Krown, KROWN_SETUP_CATALOG.md:760 "double or more the recent volume bars around those lows or highs") | defines a trend-line touch, not an entry; lookback not stated |
| biggest volume bar + hammer (KR-S7) | SOURCED text, lookback OURS | 1w/1d, provisional; belongs to the Krown lane, deferred |
| volume-spike 2.0x of 240 bars (P06) | OURS | NO-SOURCE, Java SetupCandidatesBuilder:804-816 |
| any MA length/type for an entry | none | NO-SOURCE |
| entry, stop, target for a bigtrade layer | none | not stated anywhere |

## What is missing (to unblock)
1. A trader quote giving an entry trigger from volume candles (what makes a candle "big", the lookback, the side, the confirmation) with stop and target; or an operator decision to run it as an OURS layer (chosen on DEV, checked once on VALIDATION, holdout once, ledgered).
2. For the MA part: a quoted MA length/type and how it gates the entry.
3. For order-flow "big trades": a BTC size definition and aggTrades in the live path (Fabio lane, excluded from this task).
Until then an OURS volume layer already tested negative (VOL-V1..V4), so building one would put an unvalidated rule on testnet.

## Causal rules (for any future build)
Closed bars only; entry at next bar open; no fill at a level after the bar that proves it; no bigmoves/forward labels.
