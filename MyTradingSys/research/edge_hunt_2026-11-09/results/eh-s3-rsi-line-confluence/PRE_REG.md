# PRE_REG: eh-s3-rsi-line-confluence (RSI 40/60 line bounce with other-timeframe confluence)

Frozen before any return is computed. Trials T11 and T12 from TRIALS.md (frozen 2026-11-09 by edge-hunt-plan-opus-1109, wave 2, lens L1). No trial added, split or re-cut. Labels: S = SOURCED (file:line), O = OURS.

## Hypothesis
The RSI 40/60 line-behaviour study (research/rsi_40_60_line_behaviour_2026-11-04/RESULT.md, PRE_REG.md) found one consistent effect: when another timeframe's RSI sits at the same line the hold rate rises (1h +7, 4h +12, 12h +18, 1d +17 points), and when the higher-TF bias agrees with the bounce the bounce holds 10-14 points LESS. It was never traded.
- **T11**: the confluence bounce (all confluent bounces, 1h + 4h, BTC + ETH spot, both lines pooled) has mean fee-net R > 0.
- **T12**: the T11 subset whose bounce goes against the higher-TF bias has mean fee-net R > 0.

Known overlap (TRIALS.md reading rule): the confluence effect was found on the same DEV span (2017-08..2024-06) by that study, so the DEV screen here is not independent evidence; only the single VALIDATION read is. Both the study and this file use the same RSI events and lines, but the cushion here is fixed at 2 points (OURS) and the study's DEV-picked cushions (picks_dev.json) are not used, so no selection on DEV is repeated.

## Rules (frozen)
| Item | Rule | Label |
|---|---|---|
| Lines | RSI14 (Wilder, `layers/rsi/rsi_core.py`) lines 40 and 60 | S (MLK-R1; study PRE_REG "Event"); |
| Approach | Line 40 from above: RSI enters the band 38..42 (edges inside) at bar k while bar k-1 > 42. Line 60 from below: RSI enters 58..62 at bar k while bar k-1 < 58 | lines S; cushion 2 RSI points O (fixed, not tuned); band-entry definition copied from study.py `find_entries` (zone above/inside/below), restricted to the origin side the brief names |
| Bounce (entry) | Line 40: first close at bar j, k < j <= k+6, with RSI > 42, with no close RSI < 38 on bars k+1..j-1 first. Line 60: first close j with RSI < 58 and no close RSI > 62 first. Enter at the close of bar j (taker). 40 = long, 60 = short | study.py event logic adapted (the study's hold = leaves the band on the origin side); 6 bars O |
| Data continuity | bars k-1..j must be consecutive (no missing bar); otherwise the event is skipped and counted | O |
| Confluence | at the entry-bar close time T, for each OTHER TF in {1h, 4h, 12h, 1d} take its last bar whose close time <= T (no lookahead) and a value no older than 2 bar lengths (else missing); confluent if RSI14 within +-2 of the same line (|RSI - line| <= 2). T11 = at least 1 confluent TF | study "Confluence" (PRE_REG: other TFs inside the same band [L-c, L+c]); +-2 O |
| HTF bias | trade TF 1h -> 4h, trade TF 4h -> 1d; RSI14 of that TF's last closed bar > 50 = up, < 50 = down (exactly 50 or missing = no bias: never "against"); against = long while down, short while up | rule form S from the study PRE_REG ("RSI14 of the next TF up above/below 50"); the map 4h -> 1d is OURS (the study mapped 4h -> 12h) |
| Stop | long: lowest low of bars k..j; short: highest high of bars k..j; exactly at the extreme, no buffer, no floor | structural (d-stops-follow-trade-1106) |
| Target / time | target 2.5R; time stop at the close of the 48th bar after entry (bars j+1..j+48) | O |
| Fills | Entry at the close of bar j. Stop: bar low <= stop (long) -> fill min(open, stop), stop wins a same-bar tie with the target. Target: bar high >= target -> fill max(open, target). Time: close of bar j+48. A trade whose exit would need a bar past the data end is censored and counted (not traded). An entry with stop on the wrong side of, or equal to, the entry is invalid and counted | O (same convention as the shipped eh-h2 worker) |
| Overlap | one trade at a time per symbol x TF x population: an entry bar before the prior trade's exit bar is skipped and counted. T11 population = confluent bounces; the no-confluence contrast is its own chain; T12 is the HTF-against subset of the T11 trades (so T12 is contained in T11) | O |
| T11 | all confluent bounces, 1h + 4h, BTCUSDT + ETHUSDT spot, both lines pooled | TRIALS.md |
| T12 | the T11 trades with HTF bias "against" | TRIALS.md |
| Exploratory (cannot promote) | no-confluence bounces (the contrast), per TF, per line, number of confluent TFs 1/2/3, per regime tag, HTF "with" bias | - |

## Data and splits
- Spot klines BTCUSDT and ETHUSDT 1h and 4h from the existing public cache (data.binance.vision, fetched earlier by `fetch_binance_archive.py --spot-history`, F:/MTS/Dumps/backtest/spot_2017; kept outside the repo; it holds later months, which the loader never opens). **12h and 1d are resampled from closed 1h bars** (UTC buckets, complete buckets only; a bucket with a missing hour is dropped). 4h is the archive's own 4h file. 1w and 1M (regime tag only) are resampled from those 1d bars (weeks Monday 00:00 UTC).
- DEV = 2017-08..2024-06-30; signals counted from 2017-10-01 (O: 1d RSI14 needs about a month to settle). VALIDATION = 2024-07-01..2025-06-30, read once, only if a trial passed the DEV screen (the script refuses a second run). HOLDOUT (2025-07-01+) is never loaded; the loader raises on any bar at or after 2025-07-01 and a test shows it.
- Funding: perp fundingRate archive (futures um monthly, data.binance.vision) cached outside the repo in F:/MTS/Dumps/backtest/eh_s3_conf/fund. The archive starts 2020-01 (2019-09..2019-12 files are not published: 404), so funding is 0 before 2020-01; trades before that carry spot-history cost only and RESULT says so.

## Fees, R, statistics
- Regime A: taker 0.0005 per side (fees.py DERIBIT_TAKER = BINANCE_TAKER) = 10 bps round trip + 2 bps round-trip slippage (FORMULAS.md s13) = 12 bps. fee_r = 12 bps / stop distance in bps. Funding R = side_sign x sum(rate over records with t_in < calc_time <= t_out) x entry / risk (FORMULAS s13); t_in = entry close time, t_out = exit bar close time. Net R = gross R - fee_r - funding R.
- SE clustered by UTC day for sets made only of 1h trades, by ISO week for any set that contains 4h trades (so T11 and T12 cluster by ISO week, which also absorbs the BTC/ETH and 1h/4h correlation: conservative; O). DEV screen: n >= 30, mean net R > 0, 95 % CI lower bound > 0. MDE = 2.8 x SE (80 % power, two-sided 5 %).
- VALIDATION (once): one-sided p for mean net R > 0, Holm at m = 15 across the wave (smaller of the two p x15, larger x14, monotone; trials not read count as p = 1).
- Verdict: PASS = DEV screen passed and VALIDATION Holm-significant with mean > 0. FAIL = DEV mean net R <= 0 with the CI upper bound below the MDE. INCONCLUSIVE otherwise. A PASS files one raw testnet-forward card; next step is testnet forward, never a longer backtest.
- Reported: n, hit, mean gross R, mean fee_r, mean funding R, mean net R, SE, CI, MDE, per-year DEV table, counts per year and side (count pass), invalid/censored/overlap-skipped counts.

## Order of work
1. This file committed first. 2. `test_line_confluence.py` run failing before the code exists. 3. Count pass (events per year and side, regime mix, no returns). 4. DEV. 5. VALIDATION once if screened in. 6. RESULT.md.

## Trial ids
T11, T12. Everything else exploratory.

## Context
- Regime: research_kit regime_tag logic (weekly + monthly RSI 60/40 band with daily SMA side, `research_kit.ma_side` / `rsi_band`); DEV weeks reported on the `Regime mix:` line (BTC). The study is ungated (the question is the line behaviour in all contexts); trades are also tagged bull/range/bear for an exploratory split. The bear label is expected empty.
- Phase: DEV 2017-08..2024-06 pooled; not split by cycle phase (eh-o2's question).
- Session: none (24h, trade TF bars).
- Entry: at the close of the bounce bar (taker), long off 40 from above, short off 60 from below.
