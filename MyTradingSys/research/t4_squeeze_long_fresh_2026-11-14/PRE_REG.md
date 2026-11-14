# PRE_REG: T4 trapped-shorts squeeze long on FRESH coins, 4h, frozen before any outcome (2026-11-14)

Source: `EDGE_WAVE2_DESIGN_1114.md` (side-session notes), pick T4. Source cell = named combo "T3 trapped-shorts squeeze long" of `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/` (`PRE_REG.md` + `miner.py`, read from trunk). Frozen BEFORE any signal, trade, return or placebo number is computed; only file-availability counts were looked at. SOURCED = copied unchanged from a named repo file; OURS = our choice, stated here. No parameter below is a trader's number. One cell, no grid, no second pass.

## Context

Question: does the miner's one surviving lead (4h, same-bar AND of low funding, spot net taker buying and a 5-day breakout, long only, ridden until a 10-day-low break) hold on coins it was never fitted on? Every miner lead failed only on CI width or multiplicity, never on sign or fees; the lever here is coin independence and count. Not a trade instruction; nothing is an edge until a fee-net out-of-sample result passes the bars below and a blind review.
Regime: BTC structure UP / MIX / DOWN (BTC daily close vs its SMA200d and the 20-day change of that SMA), the miner's label, reported as bull = UP, range = MIX, bear = DOWN per window. Hypothesis cell = non-bear (UP_E, UP_L, MIX_E, MIX_L); control row = DOWN_E, DOWN_L (descriptive only, never pooled into the verdict).
Phase: miner 6-label phase = structure x halving clock (E = under 540 days since the last halving, L = 540 or more), keyed to the ENTRY bar's UTC day from BTC closes of days <= D-1. Today (2026-11-14) by that rule, from `F:\MTS\data_cache\binance\combo-edge-miner-1114\spot_1d\BTCUSDT.csv` (last closed bar 2026-11-13: close 68420 below SMA200d 73092, SMA200d 20-day change +150, 938 days since the 2024-04-20 halving): MIX_L, i.e. active for this cell. The MTS brain label in `F:\MTS\data_cache\mts_brains\phase_daily.csv` for the same day is MARKDOWN / BEAR (RSI14 25.5, provisional); it is reported descriptively as a second column in RESULT and gates nothing. The two labels disagree today: the miner label is the frozen gate, the brain label is a descriptive cut.
Session: none, because the timeframe is 4h with holds of days to 60 days; intraday session timing is not the mechanism.
Entry: onset 4h bar where FUND_LO, NB_ABS and BRK5 are all true (and not all true on the previous bar of that coin), fill at the next 4h open (taker, 12 bp round trip plus actual funding charged), stop max(2.5 x ATR14, 2% of entry), primary exit RIDE.
Regime mix: filled in RESULT from the data: share of calendar days and of trades in UP / MIX / DOWN for DEV and for VAL, fresh basket and old-20 pooled row. Expected from the miner study: DEV 2020-2023 holds the 2020-21 bull and the 2022 bear (DOWN_E/DOWN_L days are control only), VAL 2024-2026 holds the 2024-25 bull and the 2026 bear, so VAL has DOWN days that the hypothesis cell excludes.

## Source cell and rule table

| Item | Rule | Label |
|---|---|---|
| Timeframe, side | 4h spot bars (UTC-aligned), long only; spot price is the perp proxy, funding charged on top | SOURCED miner PRE_REG "Data" and "Trade management" |
| FUND_LO | 3-day mean of the daily mean funding, <= 10th percentile of the PRIOR 90 daily values (`pct_rank(fd3, 90)`: share of the prior 90 values <= current, excludes current; condition `<= 0.10`). Daily value = mean of the 8h prints of that UTC day. A 4h bar on day D reads the PREVIOUS completed day (D-1). Missing funding or fewer than 90 prior values = False | SOURCED miner.py `daily_flow`, `tf_features`; thresholds OURS (miner) |
| NB_ABS long | spot de-biased net taker ratio over 3 bars >= +0.08. nt = (2 tbv - v)/v; bias = mean of nt over the prior 30 days (180 bars, shifted one bar); deb = (2 tbv - v) - bias x v; ratio = sum(deb over 3 bars) / sum(v over 3 bars) | SOURCED miner.py `tf_features`; 0.08 OURS (miner) |
| BRK5 long | close > highest high of the prior 5 days (30 bars, prior bars only) | SOURCED miner.py `tf_features`; 5d OURS (miner) |
| Combination, onset | same-bar AND of the three; signal on the ONSET bar (true now, false on the coin's previous bar; first bar of a coin never an onset) | SOURCED miner.py `onsets` |
| Phase gate | entry day (UTC day of the next-bar open) phase in {UP_E, UP_L, MIX_E, MIX_L}; BTC SMA200d = plain 200-day mean of daily closes, slope = SMA minus SMA 20 days earlier, UP = close > SMA and slope > 0, DOWN = close < SMA and slope < 0, else MIX; label from the close of day d keyed to day d+1, valid if the latest key is within 3 days | SOURCED miner.py `phase_table`, `phase_for_days`; 540-day split and halvings 2016-07-09, 2020-05-11, 2024-04-20 OURS (miner) |
| Entry | open of the 4h bar after the signal bar | SOURCED miner.py `simulate` |
| ATR14 | plain SMA of true range on 4h bars (not Wilder), FORMULAS s12 | SOURCED `MyTradingSys/backtest/layers/FORMULAS.md` s12 |
| Stop | S = max(2.5 x ATR14 at the signal bar, 2.0% of entry); stop = entry - S; a gap fills at the worse of stop and the bar open; stop checked from the entry bar | SOURCED miner.py; 2.5 and 2% OURS (miner) |
| PRIMARY exit RIDE | exit at the next bar's open after a 4h close <= the lowest low of the prior 10 days (60 bars, prior bars only); time exit at the close of day 60 (360 bars) | SOURCED miner.py `simulate` kind RIDE; 10d and 60d OURS (miner) |
| SECONDARY exit T3R | stop S, target entry + 3 x S filled at the target, same-bar stop and target = stop, time exit at the close of day 30 (180 bars). Carries bar 5 (ex-best-5) | SOURCED miner.py `simulate` kind T3R; 3R and 30d OURS (miner) |
| TRAIL exit | not run (it was a miner exit, seen DEV -0.017 R; the design note names only RIDE and T3R) | OURS |
| Overlap | no overlapping trades per coin: take the first signal, skip signals before that trade's exit-time bar index, repeat | SOURCED miner.py `greedy` |
| Unresolved | a trade not resolved by the last closed bar is dropped; data ends with the last 4h bar closed by 2026-11-13 20:00Z | SOURCED miner.py `DATA_END_MS` |
| Entry window | entries only on or after 2020-01-01 and only when the entry bar open is at or after the coin's first funding print; earlier bars are indicator warm-up | SOURCED miner.py `build_frame` |
| Net R | (gross return - cost - funding paid) / (S / entry), FORMULAS s13. cost = 2 x `fees.BINANCE_TAKER` + `fees.SLIPPAGE_RT_S13` imported from `MyTradingSys/backtest/fees.py` (12 bp; never retyped in code). Funding = sum of actual 8h prints after the entry open up to and including the exit open, as the miner's `cum_funding` computes it; longs pay positive prints and receive negative ones | SOURCED fees.py, miner.py `cum_funding`, `net_r` |
| Splits | DEV = signal bar UTC day <= 2023-12-31; VAL = signal bar UTC day >= 2024-01-01. A DEV trade may exit in 2024 (at most 60 days); stated, not removed | task (the miner split by entry day; the two differ only for the 20:00Z bar whose entry is the next 00:00Z, see ambiguities) |
| Week unit | ISO week (Monday start, UTC) of the ENTRY bar open, over all coins | OURS (task) |
| Seed | 1114 for every resample and draw | OURS |

## Data and fresh universe

Public Binance spot USDT klines (4h and 1d, taker-buy base volume column 9) and USDT-M futures funding from `data.binance.vision`, in `F:\MTS\data_cache\binance\wave2-1114\{spot_4h,spot_1d,funding}` (one CSV per symbol plus `.meta.json`). Nothing from there is committed; no raw klines in git. The research script reads it, committed tests use synthetic bars only. BTC daily closes for the phase label come from `F:\MTS\data_cache\binance\combo-edge-miner-1114\spot_1d\BTCUSDT.csv` (the miner's own cache, so the label is the miner's byte for byte).

Frozen candidate list (49, none is in the miner's 20): NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN.
Drop rule (OURS, outcome-free): keep a coin only if it has 4h spot data AND funding prints in the wave cache; a coin with fewer than 90 funding days before a bar simply cannot fire FUND_LO there (no special case). Every dropped coin is listed in RESULT with the reason (no 4h spot file, no funding file, too short). No coin is dropped for performance or for having few signals. At the time of this freeze the funding folder holds files for the 49 and the 4h spot folder is still being fetched, so the kept list is fixed by the rule at step A, not chosen here.
Survivorship: delisted coins are kept where the archive has them (LUNA, FTT, OMG, WAVES, OCEAN may end early); a coin whose archive is absent is dropped and listed. The list is not point-in-time by volume, so coins that listed after 2020 enter late. The bias direction is unknown and stated.
Out of sample by coin, NOT by calendar time: the fresh coins share the same weeks as the 20 coins on which the rule was found. That is why the DEV / VAL split by time stays.
Old-20 pooled row (miner list, same code, same rules): descriptive only, never in a verdict.

## Pass bars (OURS from the design note; all at 12 bp plus actual funding)

Verdict cell = fresh coins, non-bear phases, RIDE exit unless stated. Weeks = ISO entry weeks over all fresh coins.
1. VAL n >= 30 trades AND >= 20 distinct entry weeks, else UNDERPOWERED (cannot PASS).
2. VAL mean net R > 0 AND the week-cluster bootstrap 95% CI low > 0. Statistic = mean net R per trade; resample the VAL entry weeks with replacement (2000 resamples, seed 1114), each resample takes all trades of the drawn weeks, mean over those trades; CI = 2.5th and 97.5th percentiles; one-sided p = (1 + number of resampled means <= 0) / (2000 + 1).
3. DEV mean net R > 0 (sign agreement).
4. Excess over random entries: 1000 draws. One draw = for every real VAL trade, one random 4h bar of the SAME coin, same phase flag (non-bear), same split, resolved, and entry-eligible by the entry-window rule, with the real trade's stop distance in percent of entry (S / entry) and the RIDE exit rules, 12 bp and the actual funding of its own window; draw statistic = mean net R over the matched set. The real mean must exceed the 97.5th percentile of the 1000 draw means (and excess = real minus placebo mean > 0); placebo percentile = share of draws below the real mean. Placebo trades are not overlap-filtered (stated).
5. Ex-best-5 weeks on the T3R row: VAL T3R trades of the same signals, rank entry weeks by the sum of net R, drop the 5 best weeks, the mean net R of the remaining trades must be > 0. Also reported on the RIDE row (not a gate).
6. Buy-and-hold baseline: strategy mean net daily return while in a position >= equal-weight fresh basket mean daily return over the same eligible days. Strategy = for each RIDE trade, net fractional return (gross return - 12 bp - funding paid) divided by its held calendar days (bars / 6), averaged over all position-days of the split, trades pooled. Basket = for each UTC day D in the split with a non-bear phase label, the mean over coins having closes on D and D-1 (and past their entry-window start) of close(D)/close(D-1) - 1, averaged over those days. Compared on VAL.
7. Top-coin removal: remove each fresh coin in turn from VAL; the VAL RIDE mean net R must stay > 0 for every removal, else FRAGILE (reported and blocks PASS).
Holm: the VAL one-sided p of this cell (bar 2) is reported next to the verdict together with its rank among the three wave-2 p-values (T4, T5, T6, m = 3, assembled by the coordinator); a PASS that fails Holm at 0.05 over m = 3 is labelled MULTIPLICITY-FLAGGED.
Verdict vocabulary: PASS (bars 1-7 all met) / FAIL (a bar failed, reason per bar) / UNDERPOWERED (bar 1 not met). FRAGILE and MULTIPLICITY-FLAGGED are labels on top; a FRAGILE result is not a PASS.
Reported, not gates: gross R, sd of R, by coin, by year, by miner phase label and brain label, trade counts and entry weeks per split, time in market, 6 bp row (informational; no fill model), control row (same signal in DOWN_E / DOWN_L, descriptive, never pooled), old-20 + fresh pooled row, TRAIL not run.

## Kill criteria (copied from the design note, made exact)

KILL the line ("squeeze long was a tail of 20 old coins") if ANY of:
- fresh VAL mean net R <= 0 on RIDE; or
- VAL T3R row ex-best-5 weeks mean net R <= 0; or
- the real VAL RIDE mean is at or below the 97.5th percentile of the same-phase random-entry draws AND n >= 60.
A kill needs its own n condition to be met and bar 1 to hold; with VAL n < 30 or fewer than 20 weeks the verdict is UNDERPOWERED, never "no edge".
Registered prediction (CONFIRMED / REFUTED): fresh VAL RIDE mean > 0 with the T3R row smaller than the RIDE row. Seen on the old coins: RIDE DEV +2.675 R (n 45), VAL +2.420 R (n 72), CI [0.217, 5.887], placebo p 0.047; T3R DEV +0.399, VAL +0.220; TRAIL DEV -0.017. These are not tuned against.

## Power gate

Inputs, each with its source:
- `--n 72`: the VAL trade count of this exact cell on the 20 old coins (`combo-edge-miner-1114_2026-11-14/RESULT.md` line 78). Conservative for the fresh 49: more coins, but alts list later and have fewer funding days, so no scaling is assumed. A second run at n 150 (about 2x) is pasted too.
- `--sd 12.3`: two-point value backed out of the same row's published day-cluster CI [0.217, 5.887] around mean 2.420: half-width 2.835 / 1.96 = SE 1.45, times sqrt(72) = 12.3 R. Clustering inflates the SE, so this is a rough figure for the per-trade sd, not a measurement; the measured sd is reported in RESULT.
- `--cost 0.03`: 12 bp over a typical 4% stop (design note: 0.02-0.03 R).
- `--m 3`: Holm family T4-T6.

```
python scripts/dev/prereg_gate.py --n 72 --sd 12.3 --cost 0.03 --m 3 --sd-source MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:78
n 72 sd 12.3 m 3 z_holm 2.394 MDE 4.688 R + cost 0.03 = 4.718 vs max plausible gross 0.3; n needed 21705
BLOCK: do not freeze (write BLOCKED.md with these numbers)   [exit 1]

python scripts/dev/prereg_gate.py --n 150 --sd 12.3 --cost 0.03 --m 3 --sd-source MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:78
n 150 sd 12.3 m 3 z_holm 2.394 MDE 3.248 R + cost 0.03 = 3.278 vs max plausible gross 0.3; n needed 21705
BLOCK: do not freeze (write BLOCKED.md with these numbers)   [exit 1]
```

Decision (OURS): BLOCK, stated. The run goes ahead because the operator ordered the wave (2026-11-14). The gate's 0.30 R plausible-gross ceiling is built for ordinary-R cells; this cell is tail-shaped by design (seen gross about +2.4 R), so an MDE of about 3-5 R means only a result of the seen size can register. A FAIL or a CI spanning 0 is therefore read as UNDERPOWERED or UNTESTED, never as proof of no edge; a PASS still needs the blind review and the operator's go before any testnet-forward card.

## Known weaknesses (before the run)

- Tail-shaped profit: RIDE pays on a few long trends; the seen TRAIL row was -0.017 R. Bar 5 on the T3R row, the ex-best-5 cut and top-coin removal exist for that reason.
- Power gate BLOCK (above); independent episodes (weeks with a squeeze across many alts) are far fewer than trades, since altcoins squeeze together.
- The rule was found on the old 20 coins in the same calendar weeks; fresh coins are independent by coin, not by time. The 4h frame, FUND_LO, 0.08 and 2.5 ATR numbers were chosen by the miner on those 20 coins (OURS, seen).
- One BTC-based phase label for every coin; it disagrees with the MTS brain label today (MIX_L vs MARKDOWN / BEAR).
- Spot price stands in for the perp: no basis, no liquidation, no fill model, 12 bp flat. Real alt spreads can be wider than 12 bp (stated, not modelled).
- Survivorship: the candidate list is fixed and not point-in-time; delisted coins absent from the archive are missing (bias unknown). Collapsing coins (LUNA, FTT) are held by a long-only ride only until the stop fills at the gap open, which the stop-fill rule handles.
- Funding history of these perps starts 2020-09 or later for many coins, so DEV may be thin (bar 3 is sign only).
- Coins in one week are correlated: the week-cluster bootstrap is the minimum honest unit.

## Protocol

1. Code (`t4_lib.py`, `t4_trades.py`, `t4_stats.py`, `test_t4_*.py`, mutation check; module names carry the `t4_` prefix) and synthetic-bar tests are committed in the next stage. Tests use synthetic bars only (no cache paths, no `scripts/sched`), cover look-ahead, stop-wins-ties, gap fill, fee arithmetic from `fees.py`, funding sign, overlap and a planted edge, and must fail on a planted bug at least once.
2. Step A: `t4_trades.py` writes the trade list (fresh coins, plus the old-20 and control rows as separate files), with NO pooled statistic.
3. Step B: an independent recompute of 3 dated trades from raw klines and FORMULAS.md, and an adversarial look-ahead / fee audit, run on that list.
4. Step C: only if both are clean, `t4_stats.py` computes the statistics and RESULT.md; a checker re-derives the verdict from the summary numbers against the bars above.
5. A found mechanical bug is fixed and logged in RESULT; rules are never changed after step A.

## Ambiguities in the source text and the reading frozen

- Split unit: the design note says DEV / VAL "by signal bar", the miner used the entry day. Frozen: signal bar UTC day (task text); the phase label still keys to the entry day as the miner does. Only the 20:00Z bar can differ.
- "Exit next open after a close below the prior-10-day low" is read as close <= prior 10-day lowest low (the miner's `d * (exit_lvl - close) >= 0`, so equality exits).
- Funding window: prints after the entry open up to and including the exit open (miner `cum_funding`, `side="right"`).
- Ex-best-5 weeks ranks weeks by the sum of net R and is gated on the T3R row (design note); the miner used UTC days, here the unit is the ISO entry week (task text).
- Basket day return and strategy daily return are defined above because the note gives no formula; both are on VAL for bar 6.
- Placebo "same stop distance" is read as the real trade's S / entry; "same phase flag" as non-bear (not the same one of the four labels).
