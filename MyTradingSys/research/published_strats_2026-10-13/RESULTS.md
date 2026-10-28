# Published rule-based strategies on BTCUSDT perp: results (2026-10-13, JIS-NUC)

Design frozen in PRE_REG.md before any outcome. Code `run_pub.py`, every variant in `TRIAL_REGISTRY.csv` (62 at 0.10 %/side, plus the
same 62 at 0.05 %/side as sensitivity). Data: Binance BTCUSDT perp 1h klines 2020-01..2026-09 resampled to 4h/1d, 8h funding.
DEV 2021-01-01..2023-06-30. VAL 2023-07..2024-06 and HOLD 2024-07..2025-06 were only to be opened for DEV advancers.
The project's sealed holdout (2025-07..2026-09) was not touched.

## Answer
**Nothing survives.** 0 of 62 variants cleared DEV (net mean > 0, placebo p corrected by Benjamini-Hochberg q <= 0.10, >= 20 trades), so VAL
and HOLD were never opened. Same at 0.05 %/side. After Holm, the smallest corrected p among directional variants is 1.0.

| Group | Best on DEV (net of 0.10 %/side + funding) | Placebo p (uncorrected) | BH q | Trades | Verdict |
|---|---|---|---|---|---|
| TSMOM, 30 d long-short | 36.6 %/yr, Sharpe 0.53, maxDD -56 % | 0.119 | 0.63 | 79 | not significant |
| Price > SMA100 long-short | 40.6 %/yr, Sharpe 0.59, maxDD -52 % | 0.127 | 0.63 | 33 | not significant |
| Funding contrarian (exploratory) | 30.6 %/yr, Sharpe 0.51 | 0.138 | 0.63 | 95 | not significant |
| Donchian 4h 20/10 long-flat | 20.6 %/yr, Sharpe 0.50 | 0.158 | 0.63 | 68 | not significant |
| Connors RSI(2), Double-7, IBS | -22 to +12 %/yr | 0.18 to 0.84 | >= 0.63 | 12-232 | no edge |
| Williams breakout k=0.5 | -28 to -407 %/yr, gross also <= +24 % | n/a (see note) | - | 374-3881 | fees kill it; gross zero |
| Day-of-week (7), turn-of-month, session blocks (3) | -81 to +11 %/yr | 0.15 to 0.97 | >= 0.63 | 31-911 | no edge; Monday effect absent (net -13 %/yr) |
| Vol targeting cap 1x / 2x | 1.6 / 7.8 %/yr vs buy-and-hold 10.6 % | 0.76 / 0.50 | 0.81 / 0.67 | 1 | no improvement |
| TSMOM 90/180/365 d, Donchian 1d and 55/20, SMA200, golden cross, Bollinger, price > SMA7 | -39 to +30 %/yr (SMA7 worst, 105-210 trades) | 0.12 to 0.77 | >= 0.63 | 3-210 | no edge; 365 d and golden cross have 3-5 trades |

Buy-and-hold in DEV: 10.6 %/yr. 19 variants beat it in raw net return, none beyond what exposure-matched placebo shifts reach.

## Reading
- **Short-lookback trend (30-100 d) leans positive** (TSMOM 30 d, SMA50/100, Donchian 4h 20/10) with uncorrected p about 0.12-0.16 and Sharpe about
  0.5-0.6. It is the same cluster the MA literature already points to (Grobys 2020: strongest at 20 d, fading with length). 62 tests,
  none significant after correction; this is a hypothesis for one pre-registered look, not a result. Long lookbacks (180/200/365 d) show nothing here.
- **Costs decide the short-horizon rules.** Gross annualised return on 4h Donchian long-short is +24 % against +13 % net; 4h RSI(2) and the hourly
  session blocks are about zero gross and -20 to -80 %/yr net. At 0.10 %/side any strategy needing more than a few hundred round trips a year loses.
- **Carry is the only positive, parameter-free number, and it is not alpha.** Delta-neutral funding carry nets 15.4 % (DEV), 12.1 % (VAL), 6.2 % (HOLD
  window) per year with funding alone, decaying; buy-and-hold made 71 % and 59 % in the last two windows. Post-hoc descriptive supplement
  (`supp_carry.txt`, outside the pre-registered gates; it has no parameters). Spot basis, margin calls and borrow are NOT modelled and the
  Sharpe (10-18) is therefore not real. The switched version (funding > 0) is worse than always-on after fees.

## Caveats stated, not hidden
- First Williams run used a "skip if both triggers hit" rule that peeks at the rest of the bar and showed +110 %/yr; replaced by first-touch from
  the 1h bars (worst side if the same hour). Lesson: a bar-level rule must not condition on the bar's later extremes.
- Placebo for intrabar Williams puts entries at trigger offsets that can fall outside the shifted bar, so its p (0.0005, "worse than placebo") is not
  meaningful; it did not matter, the strategy is negative on its own.
- One market. No ETH, NQ or FDAX bars in the repo at these timeframes. Cross-market confirmation needs a fetch.
- Turtle System-1 skip-after-winner rule not implemented; Donchian is close-based; 4h Donchian/RSI/Williams are adaptations, not published settings.
- BTC 2021-2023 contains one bull run and one bear; 2.5 y DEV has few independent trades for slow rules (3-15 for TSMOM 90-365 d), so they
  could only fail to show an effect, not rule one out.
- Long-short results are exposed to perp funding, included; no slippage beyond the fee; liquidations not modelled.

## Follow-ups queued
See cards in the queue (tasks.py list): sealed-holdout look at the pooled 30-100 d trend family (needs operator decision A7), ETH data
fetch for a second market, carry with real spot basis and margin.

## ETH replication of the trend cluster (2026-10-13, same day, coordinator relay)
ETHUSDT perp 1h klines + funding fetched with `fetch_binance_archive.py` (2020-01..2025-06 only; nothing from the sealed window). The 9
cluster variants re-run with identical fees, funding, windows, placebo and BH (over 9). Data outside the repo: Dumps/backtest_eth.

| Variant | Net %/yr | Sharpe | Trades | Placebo p | BH q | ETH buy-and-hold |
|---|---|---|---|---|---|---|
| TSMOM 30 d long-short | 65.9 | 0.73 | 66 | 0.117 | 0.53 | 63.4 %/yr |
| TSMOM 30 d long-flat | 64.7 | 0.93 | 33 | 0.121 | 0.53 | |
| Price > SMA50 long-flat | 45.5 | 0.70 | 28 | 0.295 | 0.53 | |
| Price > SMA100 long-flat | 34.6 | 0.49 | 22 | 0.470 | 0.67 | |
| Donchian 4h 20/10 long-flat / long-short | 5.8 / -18.4 | 0.11 / -0.23 | 84 / 158 | 0.68 / 0.60 | 0.68 / 0.67 | |

**Does not replicate as an edge.** 0 of 9 advance. TSMOM 30 d lands at almost the same placebo p (0.12) as on BTC, but net return only
matches buy-and-hold (it avoids drawdown, not adds return), and the BTC Donchian 4h result flips negative. VAL and HOLD not opened.
Read: the 30 d trend lean is a risk-reduction effect at best; there is no evidence of excess return. The sealed BTC holdout stays sealed.
