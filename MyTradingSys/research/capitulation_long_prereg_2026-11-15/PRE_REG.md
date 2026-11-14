# PRE_REG: capitulation long (forced-liquidation wash-out), capitulation-long-prereg-1115

Written before any event outcome is computed. Only signal counts and the unconditional 5-day return SD (all days, no event conditioning) were computed, to run the power gate (power_gate.json, cap_core.py).

## Context
Operator wording: a forced-liquidation wash-out after several red days (flush day, volume spike, OI drop), then a long. Lead: nkp4 (d77c8c8f8) found CAPITULATION-phase long positive in DEV and VAL on only 52 and 6 BTC days (UNDERPOWERED). Prior work read first: edge2_capitulation_long_2026-11 (bar-shape capitulation + confirm, 0/6 cells, VAL +0.65% n340 CI incl. 0; a different, price-shape definition), capitulation_breadth_2026-11-13 (breadth event FAIL), t11 (FAIL), t2 (BULL+BASE FAIL, BEAR control passes only with CI low +0.03 R, power BLOCK), t6 (KILLED, drift + survivorship). OI/funding positioning is edge-brief-funding-oi's lane; here OI is only a descriptive BTC-only column, not a gate.
Phase: the rule is itself the CAPITULATION phase read per coin; no other phase traded. Session: daily bars, 24/7.

Regime mix: BTC days 2019-2023 (DEV): CAPITULATION 3%, VAL 2024-2026-11: 1% (nkp4 RESULT.md). Signal days found here (10 coins): DEV 16 distinct days (44 coin-signals), VAL 5 distinct days (14 coin-signals): all within the same few market-wide crashes, so coin-signals are one cluster per day.

## Hypothesis
After a coin's flush day (down >= 2 ATR, volume >= 3x its 20-day median, >= 3 red of the last 4 days), buying the next UTC open and holding 5 days earns a gross effect above the 0.14% round-trip cost.

## Rule (exact)
Daily bars built from the shared F:\MTS\data_cache\binance_spot 15m caches (complete 96-bar days only; 1m caches in binance_1m carry no volume, so volume is read from 15m). 10 symbols: BTC ETH BNB SOL XRP ADA DOGE LINK LTC AVAX (the 10 with complete 15m and 1m history; a coin contributes from its first bar).
| param | value | label |
|---|---|---|
| ATR period | 14, Wilder | SOURCED (standard default) |
| flush: day return <= -k x ATR%(prior day) | k = 2.0 | OURS |
| volume >= m x median(prior 20 days) | m = 3.0, 20 | OURS |
| red days (close < open) among last 4 incl. flush day | >= 3 | OURS (operator "several red days") |
| entry | open of the next UTC day | OURS |
| stop | 2 x ATR% below entry, daily lows | OURS |
| exit | close of day d+5 | OURS |
| cost | research_kit.TAKER_RT_PCT = 0.14% | SOURCED |
OI drop: Binance metrics OI exists only for BTC 2022-2025 (F:\MTS\data\binance_metrics), so OI is a BTC-only descriptive column and cannot gate a 10-symbol rule. Nothing here is fitted: all values fixed now, DEV 2019-01..2023-12-31 descriptive, VAL 2024-01-01..now is the verdict split.

## Counts and power (research_kit.power_check, MDE = 2.8 x SD / sqrt(n), n = distinct signal days)
| split | coin-signals | independent days |
|---|---|---|
| DEV | 44 | 16 |
| VAL | 14 | 5 |
| ALL | 58 | 21 |
Unconditional 5d SD = 13.0% (event-day SD is likely higher). MDE at n=21 days: 7.95% gross; at n=5: 16.3%. A realistic gross effect is 1-3% (OURS), so needed 8.09% > 3%: **power gate = BLOCK**. Days needed to detect a 2% gross effect net of 0.14%: 384 (about 18x the 21 days available).

## Kill criterion (if ever run with enough n)
KILL if VAL fee-net mean <= 0 with >= 30 independent days, or day-clustered 95% CI lower bound <= 0. PASS needs DEV mean > 0, VAL CI low > 0, placebo (random non-event days, same coins, same hold) below the real mean, ex-best-3 days still > 0.

## Decision
Study NOT run. BLOCKED.md states the data needed. The reading remains an unproven lead, not a rejection.
