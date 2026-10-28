# Liquidation layer: is it worth trusting? (operator 2026-10-28: "find out how much of this is actually useful - worth trusting - so we need a constant context building for this liquidation layer")
Layer = CoinGlass Legend "Liquidation Heatmap (BTCUSDT, Leverage)" and the Hyperliquid liquidation map. It is a MODELLED estimate of where leveraged positions would liquidate, not executed liquidations. Colour scale and units are not shown on the page (NOT_IN_DATA); cream = densest in this palette (OURS reading).
What the 2026-10-28 shots show (no claim of edge): bands end where price traded through them (by construction), e.g. 81.15-81.25k (10-27 ~21:30Z), 81.3-81.8k (10-28 ~08:30Z spike), 79.5-79.6k. Three touches, three reversals = an anecdote chosen in hindsight, no placebo.
Pre-registered test (OURS, to run on forward data only; no historical heatmaps exist in the repo):
1. Each pasted heatmap set adds rows to BANDS_LEDGER.csv at observation time (band lo/hi, density, side, distance from price in ATR(15m)).
2. Score from Binance 1m klines (closed bars): H1 touch within 24 h vs placebo levels at equal distance (random, same count); H2 reversal of >=1 ATR(15m) within 2 h after touch vs placebo; H3 realised liquidation notional near the touch (Binance forceOrder stream, recorded) vs baseline.
3. Count only fee-net or out-of-sample results as evidence; failed H goes in the trial ledger; n below 56 touches = no conclusion (same bar as CBP Gate 4).
4. Until it passes the layer stays DESCRIPTIVE on the dashboard, never an entry rule.
Needs: a recorder for forceOrder + 1m klines (a long-running process, not a scheduled task; owner decision), and the operator pasting heatmap sets (or a CoinGlass API key, operator decision, money).
