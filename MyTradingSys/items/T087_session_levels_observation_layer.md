# T087 Session-levels observation layer: does MTS see a failed first break of the prior high, and what comes next?

Opened 2026-10-09 from the operator's ask (MTS project thread, 14:22 UTC): "now the question is if MTS understands this and anticipates this? And then - is MTS able to see the probabality of the next event - price breaking the local hight before US session start? ... will it break the last local low of the asian/eur session!"

## The day, from Binance USD-M BTCUSDT klines (fetched 2026-10-09 ~14:25 UTC)
| Level | Price | Time (UTC) |
|---|---|---|
| Previous day (10-08) high | 83,487.1 | 10-08 |
| Asia 00:00-08:00 low / high | 81,571.5 / 82,627.9 | 01:15 / 06:45 |
| EU morning low (last local low before the spike) | 82,365.1 | 10:30 (15m bar) |
| Spike high: took the 10-08 high by 12.8 on the first touch, then sold | 83,499.9 | 11:45 (15m bar) |
| Drop low at the US cash open | 82,426.3 (61 above the 10:30 low, not broken) | 14:00 (15m bar) |
| Now | 83,099.4, bounce high 83,196.9 | 14:15 |
Indicator confluence at the 13:40-14:01 low: 1m RSI double bullish divergence (13:41, 13:43; screenshots/2026-10-09_BTCUSDT_90e55256ec34.md); 5m OI 91,821 -> 92,130 with buying delta from 13:45 (screenshots/2026-10-09_BTCUSDT_850745dc9d8d.md).

## What MTS did (live_runner.log, polls 10:00-14:22 UTC)
- Fired: turn_of_candle 1m every 15 min (time-based), rsi_events 5m at 10:35, 11:00, 13:35, 14:05, cryptocred sr_flip 15m at 10:45, fabio v3_grid 1m 72 alerts at 14:20.
- Not fired: nothing for the 11:45 failed break of the prior-day high, nothing for the short.
- htf_context (research/htf_context/2026-10-09.jsonl): 4H rows only; bal_4h and bal_1d null all day, so failed_breakout is null (unknown) for the 08-12 window that holds the spike.
- No live layer tracks prior-day high/low, Asia or EU session high/low, first-touch break vs fail, or gives a probability of the next level being taken. rsi_divergence.py is a backtest module, not wired live.

## What a layer would need (sources first, provenance rule)
- Tom: big participants "usually have a readiness to act up here when a market shoots past the previous day's highs" (Of_wlv3xaZo:7); a breakout to the previous day high with a fair value gap is "a great idea to make a long trade" (Of_wlv3xaZo:7); the market "likes to run from liquidity to liquidity" (QClPWDJ-BrU:7). Fabio: check extracts before adding anything.
- NO-SOURCE today: the Asia / EU session clock for BTC, "first go" definition (close beyond vs wick beyond), the break threshold, and any probability. A probability must come from a backtest table on 2022-2026 1m klines (counts of: prior-high first touch fails -> next session low taken before / after a new high), stratified by session as B154 requires.
- Output is an observation row, not a Tom filter and not an order (separate layer, CLAUDE.md hard rule).

## Status
OPEN. Not started: budget hold until the weekly reset (Sun 2026-10-11 22:30 IST). Related: B154 (no session-stratified verdict), T082 (Tom core re-run).
