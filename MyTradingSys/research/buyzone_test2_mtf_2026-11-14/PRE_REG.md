# PRE_REG: Test 2, multi-timeframe context rule, both sides (2026-11-14)

Source brief: `MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md` Test 2 plus its Shared rules table. Committed BEFORE any outcome (no trade, R or placebo number has been computed; only phase day-shares below, which use no price outcome). Code (`lib.py`, `run.py`, tests) is committed in the same step, also before any outcome. Labels: SOURCED = stated in the brief; OURS = our choice, conservative default, logged as DECISION (OURS).

## Context

Question: does a daily phase filter + 1W/3D divergence context + 4H break entry show edge pooled across 20 coins, both sides? Nothing here is an edge until a fee-net out-of-sample result passes. Not a trade instruction. Public Binance spot klines (4h, 1d, 3d, 1w, 2017-08 on; fetched with `fetch.py` into a local cache outside the repo, never committed). Machine had no F: drive; DECISION (OURS): fetch public klines from api.binance.com. Funding is not used in this test. Testnet-only repo; no live-tree touches.

Regime mix (share of coin-days per phase, 20 coins, from `regime_mix.py`; n/a warm-up days excluded):
Regime mix: DEV (coin-days, 20 coins, n=39926, n/a excluded from %): UP 23.2%, BASE 8.4%, DOWN 4.6%, BEAR 51.6%, RANGE 12.2%
Regime mix: VAL (coin-days, 20 coins, n=20404, n/a excluded from %): UP 19.2%, BASE 5.4%, DOWN 6.9%, BEAR 49.7%, RANGE 18.8%
Regime mix: RECENT (coin-days, 20 coins, n=9500, n/a excluded from %): UP 14.5%, BASE 4.9%, DOWN 5.1%, BEAR 63.1%, RANGE 12.5%

The sample is dominated by BEAR (alts bled after 2018, 2021). Short-side phases (DOWN+BEAR) carry most days, long-side phases (UP+BASE) about 28% (DEV), 25% (VAL), 19% (RECENT). RANGE is never traded. Expect few long trades in RECENT; report n always.

## Universe (OURS)
BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC DASH ZEC NEO IOTA VET ATOM EOS BCH QTUM (USDT spot, each from its own listing date; 20 coins, pooled). Chosen as liquid, listed before 2020, no outcome look. Survivorship note: all still trade; a coin that was delisted is absent (bias unknown, reported as a caveat).

## Rules

| Item | Rule | Label |
|---|---|---|
| Phase (per coin, daily, from the previous day's bar only: the 4H bar uses the daily bar of the day BEFORE its open day) | UP = close>SMA200, SMA200 higher than 20 days ago, DI+>DI- (Wilder 14). BASE = not UP, close<=0.6 x 540-day high, close>SMA200 on each of the last 20 days. BEAR (post-peak bear) = not UP/BASE, close<=0.6 x 540-day high, close<SMA350 (50w). DOWN = not UP/BASE/BEAR, close<SMA200, DI->DI+. RANGE = rest. n/a until 350 days of history | OURS (shape from the brief and BUY_ZONE_MAP section 3) |
| Sides | Long only in UP and BASE; short only in DOWN and BEAR; RANGE no trades | SOURCED (brief: long in UP/base, short in DOWN/post-peak bear) |
| Context | Bullish divergence (long) or bearish divergence (short) on 1W or 3D, available within the last 28 days (causal: available at the close of the bar that confirms the second pivot). Divergence = two consecutive HTF pivots (half-width 2) 3..30 bars apart, price lower low/higher high while oscillator higher low/lower high. Primary oscillator RSI14 (Wilder); secondary variant WaveTrend (10,21) | SOURCED (brief: 1W or 3D RSI/WT, last 4 weeks, causal); pivot width/gap OURS |
| Entry | 4H close breaks the most recent confirmed 4H pivot (half-width 3, known only from pivot bar + 3): long = close above last pivot high, short = close below last pivot low, first close through that level only; entry at the NEXT 4H open | SOURCED direction; pivot width, next-open OURS |
| Stop | `max(0.6 x ATR14(4H), 0.5% of entry)` beyond the last confirmed 4H pivot on the other side (long: below last pivot low; short: above last pivot high). Setups with stop distance <=0 or >10% of entry are skipped | SOURCED formula; 10% cap OURS |
| Exit | First of: stop (checked from the entry bar, stop first inside a bar, gap fills at the open), opposite raw 4H break (close, exit at next open), 10 days (60 bars, exit at open) | SOURCED |
| Cost | R = (exit-entry)/risk, fee-net = R - fee x entry/risk. 12 bp round trip main row, 6 bp sensitivity row | SOURCED |
| Lockout | 10 days between entries on the same coin | SOURCED |
| Splits | DEV = entry <= 2023-12-31; VAL = entry >= 2024-01-01; RECENT = entry >= 2025-07-01 (reported separately, a subset of VAL, never used to pick a rule) | SOURCED; RECENT start OURS |
| Placebo | Per real trade: a random 4H bar from the SAME side, SAME phase, SAME period (DEV/MID/RECENT, pooled coins), same stop rule, held for that trade's planned hold (bars until its exit signal or 10 days, stop ignored for the hold length, stop still applies); 1000 draws; statistic = mean fee-net R of the matched set; reported as percentile of the real mean inside the draws plus the 2.5/97.5 band. Placebo is on EVERY pooled table | SOURCED (same phase, side, hold, random 4H bars, N>=1000); period stratification OURS |
| Bootstrap | Block bootstrap on calendar blocks of 10 days (= max hold; trades of all coins in the same block stay together), 2000 resamples, 95% CI of mean fee-net R per trade | SOURCED (block = hold length); calendar-block form OURS |
| Top coin | In VAL (both sides) the coin with the largest sum of fee-net 12bp R is removed and the cell recomputed (n, mean, CI); a PASS whose top-removed mean is <=0 or CI low <=0 is labelled FRAGILE | SOURCED report; FRAGILE label OURS |
| Seed | 1114 | OURS |

## Variants
PRIMARY = RSI context (decides the verdict). SEC_WT = WaveTrend context (reported, no verdict claim beyond its own row). CONTROL = same phase and 4H break and exit but NO context (descriptive: tells whether the context adds anything).

## Verdict (SOURCED, shared rule), applied to PRIMARY
PASS only if VAL fee-net 12 bp mean R > 0 with bootstrap CI low > 0 AND the real VAL mean is at or above the 97.5th percentile of the placebo draws (OURS reading of "beats the band") AND DEV fee-net 12 bp mean R > 0 (sign agrees). Otherwise KILL with the number. If VAL pooled n < 30: UNDERPOWERED, no claim. Verdict cells: both sides pooled (primary), long and short separately (secondary, labelled; 3 verdict cells so a lone PASS is multiplicity-flagged). Per phase and per split tables are descriptive.

## Known weaknesses (stated before the run)
- Phase, divergence and pivot parameters are OURS; one specification only, none tuned. No second pass on parameters.
- Alt coin returns are cross-correlated; the 10-day block bootstrap partly handles it, the placebo does not.
- Survivorship (20 coins still listed). Spot only, no funding, no slippage beyond the fee row.
- Test code correctness checks: `test_lib.py` (causality, stop, fee, divergence timing; a mutant with non-causal pivots fails it, see `mutation_check.txt`), `test_run.py` (placebo fast path equals the reference simulator; it failed on the first draft with a broadcast bug).
