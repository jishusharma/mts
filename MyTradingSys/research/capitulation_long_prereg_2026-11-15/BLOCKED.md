# BLOCKED: capitulation-long study (power gate BLOCK)

n available: 21 independent flush days (16 DEV, 5 VAL) over 10 coins, 2019-2026; needed for a 2% gross effect at 0.14% cost: about 384 days (MDE = 2.8 x 13.0% / sqrt(n)). Gap: roughly 18x.

What is missing:
1. History before 2019 and 2020+ perp contracts: the real forced-liquidation wave (2020-03-12, 2021-05-19, 2022-05/06, 2022-11, 2024-08-05) is the only source of independent days; coins add almost no days because every coin flushes on the same market day.
2. Open interest per symbol: Binance metrics cached for BTC only (2022-2025); OI drop and liquidation volume cannot be tested on altcoins. Needs fetch of OI history (5m metrics dumps) for the other 9 coins, or liquidation-feed data (allLiquidation snapshots, not cached).
3. More days by loosening the rule (k, volume multiple) is a fitting step; only allowed as a pre-registered ladder, and the count at 1 ATR / 2x volume should be reported before any outcome. Even 10x more days (about 200) still falls short of 384 unless the effect is >= 3%.
Next action if the operator wants this reading tested: run it as a testnet-forward collector (phase-first method) on the 10 symbols and log each flush, rather than a backtest.
