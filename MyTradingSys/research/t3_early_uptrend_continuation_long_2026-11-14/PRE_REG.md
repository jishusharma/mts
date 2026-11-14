# PRE_REG: T3 early-uptrend continuation long, fresh coins (t3-early-uptrend-continuation-1114), frozen before any new-coin outcome is computed

Source: `EDGE_POSTMORTEM_1114.md` section 4 T3, order 2026-11-14 ~05:30Z (find an edge; fee-net out-of-sample decides). Nothing here is an edge until a fee-net out-of-sample result passes. Labels: S = SOURCED (named file/layer), O = OURS (our fixed choice, not the trader's). Written before the fresh-coin data was fetched; only the combo miner's DEV table (`dev_cells.csv`, 20 old coins, no VAL column used) was read to pick Cell A. Trunk check: `git ls-tree origin/fast-track MyTradingSys/research/` has no t3 / early-uptrend folder (only `combo-edge-miner-1114_2026-11-14`, whose cells are the source, on a different coin set).

## Context
Regime: the claim is conditional on early-cycle uptrend UP_E only. Entries outside UP_E are not traded; they are used only as the control rows.
Phase: UP_E = BTC close > SMA200 of daily closes AND 20-day slope of that SMA > 0 AND fewer than 540 days since the last halving (FORMULAS s25 clock, halvings 2016-07-09, 2020-05-11, 2024-04-20; S for dates and clock, 540 and the 20-day slope window O), read from closes of days <= D-1, one BTC label for all coins, assigned to the ENTRY day. The MTS brain table `F:\MTS\data_cache\mts_brains\phase_daily.csv` (6 labels + BULL/BASE/BEAR cycle) is joined by date and REPORTED: share of UP_E signals per brain label (MARKUP, DISTRIBUTION, ...) and per cycle state; the row "UP_E and brain MARKUP" is an informational subset, not the claim.
Session: not applicable, daily bars, UTC.
Entry: next daily open after the signal bar closes (taker); stops fill at the worse of stop and open.
Regime mix: reported in RESULT.md per window (DEV, VAL) as the share of calendar days in UP_E / other UP / MIX / DOWN (bull = UP_E + other UP, range = MIX, bear = DOWN, BTC structure as in the miner's PRE_REG) and the share of signal trades in each. A window whose signals are more than 85% from one calendar year is flagged ONE-YEAR and cannot carry a PASS alone (VAL UP_E days run only 2024-04-20..2025-10-12 by construction).

## Data (public data.binance.vision spot klines, no key, no orders; cache outside the repo)
- Daily spot klines with taker-buy volume, fetched with the combo miner's `fetch.py` pattern into `F:\MTS\data_cache\binance\t3-early-uptrend-1114\spot_1d`. Spot is the perp price proxy (stated limit); funding from the perp where a print exists (Binance futures funding via the nkp1 cache or the public endpoint), else the flat assumption 1 bp per 8 h paid by longs (O, conservative; RESULT reports how many trades used it).
- Universe (O): the 20 coins the combo miner used are EXCLUDED (BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI VET ZEC NEO). BTC is read only as the phase source. Candidate list, frozen now: NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN. ALL with data are kept, including delisted ones where the archive has them. No coin is dropped for performance; a coin is dropped only for having under 250 daily bars (reported). Survivorship is a stated limit.
- Entries allowed from the coin's 250th bar (indicator warm-up) and from 2017-09-01. DEV = entry day <= 2023-12-31 (UP_E days: 2017-09..2017-12 and 2020-05..2021-11), VAL = entry day >= 2024-01-01 (UP_E days: 2024-04-20..2025-10-12 only). Split by signal bar. VAL is not looked at before the code, unit tests and the independent 3-trade recompute are frozen and committed.
- Trades that enter on or before 2023-12-31 stay DEV even if they exit later (at most 60 days of 2024 prices; stated).

## Cells (exactly two; no grid, no tuning)
Bank features (daily bars, all from bars <= signal bar): ADX_DI = ADX14 >= 20 and DI+ > DI- (FORMULAS s30, S; 20 O); VOLX = volume >= 2 x median volume of the prior 30 days (O).

| Cell | Signal (onset = true now, false on the previous bar of that coin) | Label |
|---|---|---|
| A | ADX_DI AND VOLX, long | the combo miner's DEV rank-1 cell for 1d, long, UP_E, RIDE exit by day-cluster CI low (`dev_cells.csv`: ADX_DI+VOLX, DEV n 118, CI low +1.21 R; picked by DEV only; definitions unchanged) -> O |
| B | Daily Hilega Milega BUY state (RSI9, EMA3 and WMA21 of that RSI; buy = WMA21 below both lines; FORMULAS s1, s4, s5) AND close above weekly-anchored VWAP (typical price x volume from Monday 00:00 UTC, resets weekly; the signal day's own closed bar included) | HM daily S (NK positional = daily, Qdug_K_TNHg), VWAP leg S, weekly anchor O |

Both: UP_E gate on the entry day; no overlapping trades per coin (next signal at or after the exit bar).

## Trade management (frozen, same for both cells)
Stop distance S = max(2.5 x ATR14, 2.0% of entry) from entry (ATR14 = plain SMA of true range, FORMULAS s12; 2.5 and 2% O, as the miner). Primary exit RIDE: exit at the next open after a close below the prior-10-day low, time exit at the close of day 60; stops fill at the worse of stop and open. A trade not resolved by the last closed bar (2026-11-13) is dropped. Secondary row CAP3R: same entry and stop, target +3R, time exit day 30 (used for the ex-best-5 gate because on a RIDE exit the tail is the design). Net R = (gross return - cost - funding paid) / (S / entry); cost 12 bp primary = 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 from `MyTradingSys/backtest/fees.py` (imported, never retyped); 6 bp row informational.

## Baselines (same simulator, same exit, same costs)
1. Random same-phase entry: 1000 draws of the same n entries from all eligible coin-days in UP_E of the same window (no signal condition, not overlapping an open trade of that coin), each draw with the same exit. The primary metric is EXCESS = mean net R of signal trades minus the mean of the 1000 random means.
2. Buy-and-hold basket: equal-weight basket of the same fresh coins, daily open-to-open return, averaged over all VAL UP_E days; compared with the signal's mean net daily return while in a position (pooled coin-days in trade, costs spread over days held). Reported per window.
3. Ex-best-5: mean net R after dropping the 5 best trades, on the CAP3R row; also reported on RIDE for information.
4. Control: the same cells in all non-UP_E phases (expect no edge).

## Statistics
Clusters = entry ISO week pooled over coins. Mean net R with week-cluster bootstrap (2,000 resamples of weeks, seed 1114), 95% CI and one-sided p; EXCESS CI by the same bootstrap over weeks with the random mean treated as fixed. BH over the 2 cells' one-sided excess p-values (m = 2). `prereg_gate.py` is run before the freeze of the code with the miner's Cell A DEV n and sd (sd source named); its output is pasted in RESULT; a BLOCK does not stop this run (ordered) but is reported next to the verdict.

## Pass / fail bars (fixed now). A cell PASSES only if ALL hold on VAL at 12 bp (RIDE row unless stated)
1. n >= 30 trades AND >= 20 distinct entry weeks (else UNDERPOWERED, reported as NOT PASS).
2. Mean net R > 0.
3. EXCESS over random same-phase entries: week-cluster 95% CI lower bound > 0.
4. BH q < 0.05 over the 2 cells (one-sided excess p).
5. Ex-best-5 mean net R > 0 on the CAP3R row.
6. Beats the buy-and-hold basket: signal mean net daily return in position >= basket mean daily return over VAL UP_E days (point estimate).
7. DEV agreement on the fresh coins: DEV mean net R > 0 at 12 bp (sign check only; failure mode 3 was DEV/VAL sign flips).
8. Both calendar years of VAL trades (2024, 2025) have mean net R > 0, otherwise a pass is labelled single-episode and cannot count as PASS.

Verdict: PASS = a cell meets 1-8. FAIL = any of 2-8 breached with n >= 30. NOT PASS (UNDERPOWERED) = bar 1 not met. A PASS is a testnet-forward candidate after a blind review, never an "edge" (one VAL regime sequence, one cycle).

## Required code checks (committed with the code; each test must fail on a deliberately broken version once)
- Unit tests use synthetic bars only (no read of `F:\MTS\data_cache`, nothing under `scripts/sched`): look-ahead test (changing bars after the signal bar does not change the signal or the phase label), stop-wins-ties, fee/funding arithmetic against a hand number, planted-edge test (a fixed upward drift planted after random UP_E signals is found, a no-drift world reads zero).
- Independent recompute of 3 hand-picked dated trades by a second agent from raw klines and FORMULAS only.
- Adversarial look-ahead and fee audit by a third agent before VAL is read.
