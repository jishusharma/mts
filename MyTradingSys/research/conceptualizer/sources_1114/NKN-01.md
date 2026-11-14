# NKN-01 context design (frozen before results)

Rule: convergence breakout long (video 5GZIshXnxW8), draft in `MyTradingSys/research/nk_stocktalk_1113/extract55/NK55_RULES_1114.md` Part 2. No backtest, no outcome data was read for this design. Only metadata and file lists were checked.
Labels: SOURCED = NK video id + time. OURS = one fixed value, no grid. NK never mentions WaveTrend, funding, ATR depth or weekly levels: those are OURS and come from the operator order of 2026-11-14, not from NK.

## Verified inputs (checked on disk 2026-11-14)
| Item | Exists? | Where / note |
|---|---|---|
| Coin bars, 20 coins | YES | `<local-path>` (keys t,o,h,l,c,v). Resample to 4h and 1d (UTC). Earliest start 2020-08-11 (SOL). Only 5 coins have 4h/1d/1w json in `binance_spot_htf` |
| Cycle label (BTC) | YES | `<local-path>`, column `label`, already lagged 1 day (label for date d uses closes through d-1). Code: `MyTradingSys/research/nkp2-levels-phase-1114_2026-11-14/mts_phase.py` (`labels_from_features`, row `t4` = ACCUM-RANGE: M != BULL, RNG40 <= 0.30, abs(c/SMA50-1) <= 0.07, NL15 == 0). The last row is provisional: drop the final day |
| Fresh coins | PARTLY | `<local-path>`: 8 not in the 20 (AAVE ENJ GRT HBAR MANA SAND THETA XTZ), not 10. Key names are mixed (`t` vs `ts`): check keys per file. Two more must be fetched (public data) or the shortfall reported |
| Funding | YES for 17 of the 20 coins | `<local-path>` (ts,rate, 8h, from 2020-01). Missing for ALGO, FIL, NEAR and all 8 fresh coins: V2 is NO-DATA there |
| Open interest | EXISTS (daily from 2020-09) but NOT USED | `<SYM>_oi_daily.csv` |
| WaveTrend | YES | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`: `compute(bars, tf_ms)`, `htf_index(t, htf_ms, opens)`. Golden fixtures exist; LAYERS.md status "no validated edge", so used as a causal reader only |
| Coin phase (20d SMA slope, 5-day lag, ADX14 < 20) | NO single function found | Nearest ADX code: `MyTradingSys/research/adx_1d_through25_2026-11-13/run_1113.py`. Worker implements the Part 2 text and adds a future-bar poke test |
| Shared simulator / stats (nkp4 `simulate()`, `stats.py`) | NOT in this tree or in the F: cache | Worker builds the simulator inside the study folder with the fee/R rules below and commits code WITH the PRE_REG |
| Weekly and daily bars for levels | Derive | From the resampled bars (week ends Sunday 23:59 UTC) |

## Phase tested
- **Primary:** LONG only, DAILY timeframe, coin-day phase RANGE (read at the prior daily close, before the first close above the stack) x BTC cycle state ACCUM-RANGE (same prior close). Why: a tight 20-to-200 stack can only form after a base; NK says long only after a fall (5GZIshXnxW8 00:13:58) and a thin stack in sideways (00:06:03). The draft's "UP and RANGE" pooled two situations, so UP is a control. The cycle label is BTC-only and used as a label, never as a coin's own trend.
- **Controls, each reported alone and never pooled (descriptive, not gated):** see the Cells table.
- Regime-mix block per split (DEV, VAL): share of days in each coin phase and each BTC cycle state, and the share with BTC above SMA200. DEV (holds the 2022 bear) and VAL (mostly bull-dip) are reported separately, by BTC state, not pooled.
- CBP lean is bearish and BTC is MARKDOWN today: the primary cell is out of phase right now. Say so in the PRE_REG header. No live or forward trading on this.

## Context conditions (all from closed bars, computed at the signal bar's prior close)
1. Stack: EMA20, EMA50, EMA100, EMA200 on the signal timeframe. OURS (NK says 20 to 200, lengths between not stated).
2. Tight stack: (max EMA - min EMA)/close <= 3% daily, <= 1.5% 4h at the trigger bar. OURS. Idea SOURCED: thin when sideways, spread out is unreliable (5GZIshXnxW8 00:06:03 and 00:14:52). No "tight for 10 bars" condition (dropped: it clashes with the fall precondition; RANGE phase already supplies the sideways context).
3. Prior fall, shape: the close 10 bars before the first close above the stack is under the stack. OURS (10). Idea SOURCED: 5GZIshXnxW8 00:13:58.
4. Prior fall, depth: (highest high of the prior 50 bars - F) >= 1.5 x ATR14, where F = lowest low of the 10 bars before the first close above the stack. OURS (50, 1.5). Without it a 1-tick dip passes.
5. Trigger: second consecutive close above the highest EMA of the stack. Two-close idea SOURCED at a8RP5ftOfGo 00:08:50 and IjU9PpqvrI8 00:14:58 (the 5GZIshXnxW8 spans 00:07:20 and 00:12:14 are UNQUOTED); the count of two for convergence is OURS-informed.
6. De-overlap: per coin, a new episode needs the stack to have broken (a close back inside) since the last signal. n counts coin-episodes, not trades.
7. Coin phase RANGE at the prior daily close (Part 2 rule: 20-day MA slope with 5-day lag, ADX14 < 20; thresholds copied verbatim from the 11-14 studies into the PRE_REG). OURS.
8. BTC cycle state ACCUM-RANGE at the prior close, from `phase_daily.csv`. OURS (MTS_BRAINS_SPEC thresholds).
9. Entry: next bar open. Stop: under the lowest EMA of the stack (SOURCED). R = max(stop distance, 0.5% of price, 0.6 x ATR14) per the common block. Fee 12 bp round trip taker, 6 bp maker reported non-gating. Exit: half at 2R (OURS), trail the rest under the lowest EMA, exit all on two closes back inside the stack (SOURCED two-close).
10. Level condition (below).

Considered and moved out of the gate:
- BTC index filter (NK: Nifty above SMA20/SMA50, 3KnEiKNh1pc 00:15:29; 4SPDtbJVDr4 00:06:54). It contradicts a base-then-turn setup where BTC sits in ACCUM-RANGE, so it is control C8 (BTC close > its SMA20 and SMA50 at the prior close). For BTC itself it is self-referential: BTC is reported without it.
- HM gate and HM overheat > 86 (3KnEiKNh1pc 00:18:24, MLrMJ7rlL4U 00:16:38): the HM formula is OURS and unverified (NK4 failed), the 86 caption is UNCONFIRMED. NOT RUN.
- "No entry at first-touch support" (fZvp72BBmRI 00:18:39): no level definition. NOT RUN.
- Sideways-run condition, BTC SMA200 and slope leg: dropped (redundant with cycle state, extra OURS parameters).

## Crypto translation
- Session open: not used. The daily bar opens 00:00 UTC; the 4h grid is 00/04/08/12/16/20 UTC.
- Gap: DROPPED, no substitute invented. Expiry: DROPPED (perps have none).
- "Price fell first": kept (price structure only).
- Market filter: BTC cycle label as a label (primary) and BTC SMA20/SMA50 as control C8. Not the coin's own phase.
- Funding: V2 only. Mean of the last 3 settled 8h prints with timestamp <= signal bar close. A crowding check, NOT an expiry analogue.
- OI: not used (no gate, no split). It starts 2020-09, is daily only, and earlier studies found no OI-class separation.
- Does NOT translate: gap, expiry, weekly options, value area/POC on daily bars.
- Prices: spot bars (longest history for all 20 coins). Spot vs perp is an open doubt.

## Layer agreement (max 3 variants, each its own row)
- **V0: rule alone** with context conditions 1 to 9 and the level condition. Reference row.
- **V1: V0 + WaveTrend agreement.** Daily WT1 at the last closed daily bar before the signal: WT1 < +53 AND WT1 > WT2. Code: `backtest/layers/wavetrend/wavetrend.py` `compute()` on daily bars, `htf_index()` for the 4h control (last closed daily bar only). +53 is the LazyBear default (verify the constant in the param file before the PRE_REG); WT1 > WT2 is OURS. Report how many V0 signals V1 removes. Poke test: changing any bar after the signal must not change V1.
- **V2: V1 + funding not crowded.** Mean of the last 3 settled funding rates <= 0.03% per 8h. 0.03% is OURS (the 0.01% Binance baseline is not the cutoff). No existing layer module: the worker writes a causal reader over the funding CSVs with a future-row poke test. Coins without funding data are NO-DATA and removed from V2 only (count shown). If V2 VAL n < 100 it is UNDERPOWERED; do not loosen.
- Rejected: C7 volatility compression and C3 Bollinger width (restate the stack), 4h RSI >= 60 (redundant with two closes above EMA200), taker delta, session, OI, divergence, `ma_daily`, `funding_cvd_fade` and `oi_delta` (no usable implementation).

## Level type
- **One primary level: L = lowest low of the 12 weekly bars fully closed before the signal bar** (weeks end Sunday 23:59 UTC, built from closed daily bars; for 4h rows, weeks closed before the 4h bar's open). OURS (12). Not NK's: no NK quote ties this rule to prior-low support, so the PRE_REG must say so.
- **At-level:** |F - L| <= 1.0 x ATR_D, ATR_D = daily ATR14 at the prior daily close. OURS (1.0). Includes a sweep below L of up to 1 ATR_D.
- **Away-from-level (complement):** |F - L| > 1.0 x ATR_D.
- Pre-registered prediction: at-level mean net R > away-from-level mean net R. If away is equal or better, the level adds nothing and the rule fails the level step.
- Rejected levels: moving averages (circular with the trigger), daily and weekly pivots (NK2 levels, failed), value area/POC (session profiles, meaningless on daily bars), prior-day high/low (too near), the BTC buy-zone map (BTC-today only, cannot be rebuilt without look-ahead; descriptive overlay only).
- Before any outcome is read: report the at-level share and cell counts per split (counts only). No tuning of 12 or 1.0.

## Timeframes
- **Daily: primary, the only gated rows.**
- **4h: control C6 only**, same primary cell, width 1.5%, at-level, V0. R floor 1.2% (OURS; deviates from the common block's 0.5% because a 1.5% stack with a 0.5% floor leaves fee/R near 0.2 R; reported as a deviation). Phase, cycle and level are read from daily bars at the prior close.
- 15m and 1h: NOT run (NK says same timeframe; a 1h/15m EMA200 stack is a different rule with no source; a later PRE_REG). Native weekly and monthly rows: NOT run (too few events on 20 coins from 2020-08; stated, not hidden).
- Data limit: daily EMA200 needs about 200 days and the weekly level 12 weeks, so first signals appear about 2021-03. Effective DEV is 2021-03 to 2023-12 (includes the 2022 bear). VAL = 2024-01-01 onward.

## Cells
Splits: DEV <= 2023-12-31, VAL >= 2024-01-01. Universe: the 20 coins (gated). The fresh holdout and the days since 2026-11-13 run once as a separate confirmatory column, never pooled into VAL.

| ID | Coin phase | BTC cycle | Level | Variant | TF | Side | Status |
|---|---|---|---|---|---|---|---|
| P1 | RANGE | ACCUM-RANGE | at-level | V0 | 1d | long | PRIMARY |
| P2 | RANGE | ACCUM-RANGE | at-level | V1 | 1d | long | PRIMARY |
| P3 | RANGE | ACCUM-RANGE | at-level | V2 | 1d | long | PRIMARY |
| C1 | RANGE | ACCUM-RANGE | away | V0 | 1d | long | CONTROL (level comparison) |
| C2 | RANGE | MARKUP | at-level | V0 | 1d | long | CONTROL (a pause, not a turn) |
| C3 | DOWN | MARKDOWN | at-level | V0 | 1d | long | CONTROL (falling knife) |
| C4 | UP | any (reported by label) | at-level | V0 | 1d | long | CONTROL (continuation) |
| C5 | RANGE | CAPITULATION or RELIEF | at-level | V0 | 1d | long | CONTROL (episodes only) |
| C6 | RANGE | ACCUM-RANGE | at-level | V0 | 4h | long | CONTROL (timeframe) |
| C7 | DOWN | MARKDOWN | mirrored at-level | V0 | 1d | short (stack above price) | CONTROL (NK forbids shorts) |
| C8 | RANGE | ACCUM-RANGE + BTC close > SMA20 and SMA50 | at-level | V0 | 1d | long | CONTROL (NK index filter) |
| C9 | RANGE | ACCUM-RANGE | at-level | V0, limit at SMA20 within 5 bars | 1d | long | CONTROL (entry variant, ungated) |
| C10 | RANGE | ACCUM-RANGE | at-level | V0, stack width 5% | 1d | long | CONTROL (power check; one pre-declared value, run regardless of counts) |

Each row also gets a placebo (random same-cell entries, same stop and exit, matched on at-level/away) and a 6 bp maker line; these are references, not extra cells.

**Total cells tried: 13. Primary cells: 3.**
Multiple testing: BH q <= 0.10 across the 3 primary cells only. Controls are descriptive and cannot make anything PASS. All 13 are listed in the PRE_REG.

## Gates and underpowered rule
- A primary cell PASSES only if all hold on VAL: mean net R > 0 at 12 bp; trade-level and 72h cross-coin-cluster CI low > 0; ex-best-5 > 0; placebo beaten; BH q <= 0.10; n >= 200 coin-episodes (common block).
- **Underpowered rule: any cell with n VAL < 100 is UNDERPOWERED, not FAIL. n 100 to 199 is reported with its CI but cannot PASS (common-block 200 rule).** Count signals per cell before reading any outcome; do not loosen any parameter to reach n.
- Expectation only, not evidence: 0 of 17 earlier phase-chosen cells and 0 of about 100 NK rows passed, gross R about zero, fee 0.2 to 0.3 R at the 0.5% floor. A filter cannot rescue a rule with no gross R; UNDERPOWERED on daily is the likely verdict.

## Open doubts
- Power: a 3% daily stack x RANGE x ACCUM-RANGE x at-level on 20 coins from 2021-03 is probably under 100 VAL episodes. C10 (5%) and the fresh coins are the only fixes allowed. The fresh set is 8 coins, not 10.
- At-level with 1.0 ATR_D may be true for most signals on volatile alts; its share is reported (count only), not tuned.
- Coin RANGE definition: no reusable function found; thresholds must be copied from the 11-14 studies and checked by the worker. If they cannot be recovered, the PRE_REG must say so before any run.
- The BTC-only cycle label may not describe a coin's own base; coin-own markdown is a later PRE_REG.
- "Fall" in NK's words may be longer than 10 bars (transcript not rechecked); the 50-bar and 1.5 ATR depth are OURS.
- V1 may be a near no-op; V2 is NO-DATA for 3 of 20 coins and all fresh coins.
- WT +53 constant to be verified in the parameter file; HM rows excluded because the formula is unverified.
- Spot vs perp prices; funding starts 2020-01 but spot bars start 2020-08.
- OI dropped to hold the cell count down; a later PRE_REG if wanted.
- The nkp4 simulator named by one angle is absent here; a new simulator needs its own look-ahead and fee tests (new tests must fail on pre-change code once).
