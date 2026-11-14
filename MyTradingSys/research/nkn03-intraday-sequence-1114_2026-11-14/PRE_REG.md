# PRE_REG nkn03-intraday-sequence-1114 (committed together with study.py and test_study.py, before any real-data run)

Operator order 2026-11-14 06:12Z: NK rules must not be tested blindly; context applied correctly; think from phases / context / crypto context / layers / levels. A mechanical all-bars test is not acceptable. This study implements the frozen design `nkn_design/NKN-03.md` (side-session notes, local_62e478d7) exactly. Rule NKN-03 = the full NK intraday sequence of video 3KnEiKNh1pc (rules file `nk_stocktalk_1113/extract55/NK55_RULES_1114.md`, section 1.2 and the NKN-03 draft). Labels: SOURCED = a verified NK caption quote (video id + time), OURS = our choice, one value, no grid, never called NK's.

## Context
- Regime: BTC cycle label for the day from `F:\MTS\data_cache\mts_brains\phase_daily.csv` (column `label`, built from closes through d-1, same label for every coin, `provisional=True` rows excluded). PRIMARY phase cell = MARKUP, LONG only. Control phases (never pooled): ACCUM-RANGE longs, DISTRIBUTION longs, MARKDOWN mirror shorts (the mirror is OURS). RELIEF (34 days) and CAPITULATION (6) are descriptive only and not run. MARKUP already implies an up trend, so no second coin-level phase gate is stacked; the coin's own trend phase (MA20 slope over 5 days plus ADX14 >= 20 with DI direction, else RANGE) is a report column only.
- Phase: MARKUP (cycle-state half: c > SMA50, S50 >= +1%, c > SMA200 or BULL; thresholds OURS, spec s1 of MTS_BRAINS_SPEC_1114). Counts on disk 2024-01-01..2026-11-13: MARKUP 321 of 1048 days (31%), DISTRIBUTION 333, MARKDOWN 199, ACCUM-RANGE 156, RELIEF 34, CAPITULATION 6. If MARKUP is under 5% of DEV days every primary cell is UNDERPOWERED.
- Session: NY row = open 13:30 UTC (OURS: crypto has no open; NK5's only positive row was NY), exit 20:00 UTC (NY cash close, OURS). CONTROL C5 = UTC-day row (open 00:00, exit 08:00 UTC, descriptive). London and Asia are dropped. NK's "first hour" is the session-anchored first 60 minutes after the open (built from 1m, anchor OURS).
- Entry: first 1m bar from open + 60 min (14:30 UTC, SOURCED patience 3KnEiKNh1pc 00:15:10) whose low touches the session VWAP through the previous bar; fill at that VWAP, or at the open if the bar opens below it. No touch before the last session bar = no trade. All conditions before it (scanner, trap, confirm, skip, index tag, HM) are read from bars closed before 14:30; V1/V2 layer reads use the last closed 4h / daily bar at 14:30.
- Regime mix (plan): reported in RESULT.md as cycle-label share of session days, DEV and VAL, from the labels alone before any trade outcome.

## Hypothesis
The complete NK sequence (mover scanner, prior-close dip then reclaim, 1h close above the prior window high, VWAP pullback entry, session-low stop, 1h-close-below-VWAP stop) has positive fee-net expectancy as a LONG in MARKUP only. Earlier NK studies (NK1..NK6, about 100 rows) had gross R near 0; this is a new combination (NK1: different trigger; NK5: no trap or scanner), not a re-run. The trap is a plain level sweep-and-reclaim, a WEAK crypto port (earlier sweep-reclaim studies had gross about 0). Expect FAIL or UNDERPOWERED; the DEV gross >= 2 x fee gate may end the rule before VAL.

## Frozen design copied in

### Context conditions (closed bars only; window = NY session row unless stated)
1. Cycle label MARKUP for the day. OURS (label thresholds OURS), one value.
2. Index filter: BTC daily close d-1 > SMA20 and > SMA50 (SOURCED 3KnEiKNh1pc 00:15:29; BTC as the Nifty proxy OURS). Implied by MARKUP; REPORTED as a redundancy check (share of P1 trades where it holds), not an extra gate. NK says "otherwise cut size"; a hard skip would be OURS.
3. Session open 13:30 UTC. OURS.
4. Prior reference: prior window = 13:30 of d-1 to 13:29 of d (the 24 h ending just before the open). Prior close = close of the 13:29 minute (day invalid if that bar is missing); prior high / low from that window. OURS (no gap exists; idea SOURCED 00:07:24).
5. Scanner: first-hour return (close of the 14:29 minute / open of 13:30 - 1) >= +2% (SOURCED 00:09:15). Second primary row at >= +1% (SOURCED alternate). No rank row.
6. Trap: within minutes 0-9 after 13:30 some 1m low is below the prior close (SOURCED 00:07:24; 10 min SOURCED, 1m bars OURS); then a 1m CLOSE above the prior close at or after the dip bar and before 14:30 (close-not-wick OURS).
7. Confirmation: the first session-anchored 1h candle (13:30-14:29) closes above the prior window high (SOURCED 00:08:07, 00:08:58). 60 min primary; the 90 min variant is dropped.
8. Skip: first 1h range (high-low)/open > 4% (OURS cap; NK said only "big", 00:12:01). Skip count and share reported.
9. HM filter: HM(9,3,21) on the last closed epoch-aligned 1h bar at 14:30 must favour a long (SOURCED "agree" 00:18:24; formula and line colour OURS and unverified): EMA3 of RSI9 above WMA21 of RSI9 AND RSI9 > 50. The cut and weights follow the formula in the class video, not verified against his chart.
10. Entry: as in Context above; VWAP = session VWAP from 13:30, typical price (h+l+c)/3 x volume, 1m (place SOURCED 00:10:08, definition OURS). The VWAP used for the touch is the value through the previous bar.
11. Stop: session low since 13:30 through the bar before the entry bar (SOURCED "day low" 00:10:48), widened to the common floor R = max(structural, 0.5% of entry, 0.6 x ATR14 daily Wilder through d-1) (floor OURS). Also the VWAP stop: a close of an epoch-aligned 1h bar below the session VWAP exits at that close (SOURCED 00:25:50). Stop is checked from the entry bar on, stop first; a gap through the stop fills at the bar open. Both stops are part of the one rule version, not separate rows.
12. Exit (one only): 20:00 UTC (close of the 19:59 bar), OURS. The 2R target, the 8 h hold and the 24 h hold are not run.
13. Funding/OI: see "Design items not implemented".
14. Tags only, never gates: coin trend phase, cycle clock / BIBLE reading, CBP lean (coin trend phase is produced; the other two are not, see below).

### Crypto translation
Session open: NY 13:30 UTC primary; UTC day 00:00 control. Gap replacement: dip below the prior-window close then a 1m close back above (a plain level sweep, WEAK port). BTC market filter: item 2. Does NOT translate: overnight gap psychology; weekly expiry and option-chart confirmation; options strike/delta; a stock-style mover scanner on a small universe. Dropped as not computable here: volume-profile / order-flow layers (need aggTrades), taker-delta divergence (already negative), BUY_ZONE_MAP (hand-built BTC snapshot, would look ahead), value area / POC, hourly OI, liquidations, the funding 80th-percentile gate.

### Layer agreement (max 3 variants, all reads on bars closed before the 14:30 read)
| Variant | Definition | Labels |
|---|---|---|
| V0 | rule alone (items 1-12, which already carry the BTC index tag and the 1h HM) | reference |
| V1 | V0 AND 4h Wilder RSI14 >= 50 on the last closed epoch-aligned 4h bar (`rsi_core`, period 14) | RSI14 SOURCED (FORMULAS s1); the 50 cut OURS |
| V2 | V1 AND daily ADX14 >= 20 AND +DI > -DI on the last closed daily bar (`adx_di`) | ADX SOURCED (FORMULAS s30); 20 SOURCED (NK55 common block) |
Shorts mirror (RSI <= 50, -DI > +DI, HM mirrored) in the MARKDOWN control only; C4 uses V0 only. Disagree controls: C7 = V0 AND NOT V1, C8 = V0 AND V1 AND NOT V2. RESULT reports the gross-R lift of V1 over V0 and V2 over V1, not net R alone. Layers module use: `rsi_core` and `adx_di` imported from `backtest/layers`; `tf_resample.py` takes lists of 1m bars and is used only as a cross-check of the epoch alignment in the tests; the study builds 1h / 4h / 1d from the dense series of the same source with the same epoch grid.

### Level type
Classic daily pivot ladder from the prior closed window (13:30 d-1 to 13:29 d for NY; prior UTC day for C5): P = (H+L+C)/3, S1 = 2P - H, R1 = 2P - L. Family SOURCED (NK2; Part 1 pivot table), window basis OURS. At-level (one test): entry price E; a long is at-level if min(|E-P|, |E-S1|) <= 0.25 x ATR14(daily Wilder, through d-1) (band OURS, one value; set {P, S1} for longs, {P, R1} for shorts, OURS). Away = complement. The level is a TAG on the V0 entry, not a trigger. Ladder frozen at window start (tested). Circularity guard: P contains the prior close and the trap is a dip/reclaim of that close; the at-level share of P1 trades is reported; above 90% P5 is declared REDUNDANT (same sample as P1) and C1 UNDERPOWERED.

### Cell table (15 cells total, 5 PRIMARY; no cell may be added)
| # | Phase cell | Variant | Scanner | Level | TF read | Side | Role |
|---|---|---|---|---|---|---|---|
| P1 | MARKUP | V0 | +2% | all | NY 1m/1h | long | PRIMARY |
| P2 | MARKUP | V0 | +1% | all | NY 1m/1h | long | PRIMARY |
| P3 | MARKUP | V1 | +2% | all | NY 1m/1h/4h | long | PRIMARY |
| P4 | MARKUP | V2 | +2% | all | NY 1m/1h/4h/1d | long | PRIMARY |
| P5 | MARKUP | V0 | +2% | at-level | NY 1m/1h | long | PRIMARY |
| C1 | MARKUP | V0 | +2% | away | NY 1m/1h | long | CONTROL |
| C2 | ACCUM-RANGE | V0 | +2% | all | NY 1m/1h | long | CONTROL |
| C3 | DISTRIBUTION | V0 | +2% | all | NY 1m/1h | long | CONTROL |
| C4 | MARKDOWN | V0 mirror | -2% | all | NY 1m/1h | short | CONTROL |
| C5 | MARKUP | V0, UTC-day row (00:00 open, exit 08:00) | +2% | all | UTC 1m/1h | long | CONTROL |
| C6 | MARKUP | V0, 15m trap, 20-coin 15m spot universe | +2% | all | NY 15m/1h | long | CONTROL |
| C7 | MARKUP | V0 AND NOT V1 | +2% | all | NY 1m/1h/4h | long | CONTROL |
| C8 | MARKUP | V0 AND V1 AND NOT V2 | +2% | all | NY 1m/1h/4h/1d | long | CONTROL |
| C9 | MARKUP | random same-phase placebo for P1 | n/a | all | NY 1m | long | CONTROL |
| C10 | MARKUP | random placebo for P5, same at-level split | n/a | at-level | NY 1m | long | CONTROL |
**Total cells tried: 15. Primary cells: 5.** Each cell is one row; its timeframe column lists the timeframes it reads. A separate 4h or daily or weekly signal row is not expressible: the rule's trigger is a 1m / 1h session sequence and the frozen design fixes the cell list (no cell may be added). 4h and daily enter only as layer reads inside P3/P4/C7/C8; weekly context enters only through the cycle label. The 15m row is C6.

## Universe (fixed here, before any run)
- 1m rows (P*, C1-C5, C7-C10): 13 coins with public spot 1m history on both sides of 2024-01-01 and in the funding cache: BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM (ALGO excluded: 1m history only from 2026-09). Source: public Binance spot 1m klines WITH volume, fetched by `fetch_1m.py` from data.binance.vision into `F:\MTS\data_cache\nkn_1114\nkn03-intraday-sequence\` (the shared `binance_1m` cache has no volume column, which the VWAP needs). One source per coin: 1h, 4h, daily bars and every indicator are built from that one 1m series on the UTC epoch grid. Row counts match the shared cache (BTC 4,134,471).
- C6: the 20 cached spot coins of `F:\MTS\data_cache\binance_spot` (15m, with volume): BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO; all timeframes of a C6 coin come from its own 15m series. A file that fails the time-key / strictly-increasing / constant-step assertion is excluded and named in RESULT.
- Loader asserts the time key (`t_ms`, `ts` or `t`), strictly increasing timestamps and a constant bar step; per-file first / last timestamp, rows and gaps go into the RESULT provenance block. Missing bars stay NaN (a gap is never filled for highs, lows or the VWAP; closes are forward-filled for the 1h / 4h / daily resample only). A session day needs the prior 13:29 bar and >= 90% of first-hour bars, else it is skipped.

## Splits
DEV = signal time before 2024-01-01 00:00 UTC, VALIDATION = on/after it. Signal time = session open + 60 min of the session day (the read time of every condition), so split is by the SIGNAL bar, never entry or exit (a session never crosses midnight, tested). DEV = 2019-2023 (selection of nothing: no grid, no tuning); VAL gives the verdict.

## Fees, R, fills
- R = stop distance in price units dist = max(structural, 0.5% x E, 0.6 x ATR14 daily through d-1). Gross R = side x (X - E) / dist.
- Fee R at 12 bp taker (primary verdict) = (12 / 2e4) x (E + X) / dist, i.e. 6 bp of the entry notional plus 6 bp of the exit notional (nkp2 convention: the bp number is the ROUND TRIP, charged on both legs). Maker 6 bp (secondary) = (6 / 2e4) x (E + X) / dist; the maker row keeps the same fills (a sensitivity row, not PASS-bearing).
- Funding (design header): a hold that crosses a 00/08/16 UTC stamp pays side x rate x E / dist in R, with the rate of that stamp from `F:\MTS\data_cache\binance_futures\nkp1\<COIN>USDT_funding.csv`; no file or no stamp row = 0 and counted ("trades without funding data"). NET R = gross - fee - funding. Funding applies to every net figure (12 bp, 6 bp); RESULT also shows net 12 bp without funding.
- Fills: the entry is a VWAP limit touched by the bar, or the bar open if it opens beyond VWAP (never a better price); stop first when stop and a VWAP-hour close fall in one bar; a gap through the stop fills at the bar open; VWAP-stop exits at the 1h bar close; session-end exit at the last bar close.

## Placebo (like-for-like)
For every real VAL trade of a primary cell: a random entry in the SAME coin, same side (long), same phase (a MARKUP VAL day), same entry clock (rounded to the 10-minute grid from 14:30), the same layer flags (P3: V1 true, P4: V1 and V2 true, P5: at-level true at the placebo fill price), entry at the bar OPEN (no VWAP touch), the same session-low stop with floor, the same VWAP-hour stop, the same exit and the same fee and funding. 2000 draws; p = (1 + #(placebo mean >= real mean)) / 2001. The pool is every MARKUP VAL coin-day x 10-minute grid entry (not only armed days). "Beats placebo" (p < 0.05) is reported separately from "profitable". C9 / C10 rows report the pool means.

## Parameters
| Parameter | Value | Label |
|---|---|---|
| Scanner threshold | +2%, alternate +1% | SOURCED 3KnEiKNh1pc 00:09:15 |
| Trap window | 10 min, 1m bars | 10 min SOURCED 00:07:24; 1m OURS |
| Trap reclaim | 1m close above prior close | idea SOURCED, close-not-wick OURS |
| Confirmation | first 1h candle (60 min) closes above the prior window high | SOURCED 00:08:07 / 00:08:58; anchor OURS |
| Skip | first-hour range > 4% | OURS |
| Index filter | BTC close > SMA20 and SMA50 (tag) | SOURCED 00:15:29; BTC proxy OURS |
| HM | EMA3(RSI9) > WMA21(RSI9) and RSI9 > 50 on the last closed 1h | agree SOURCED 00:18:24; formula, colour, reading OURS (unverified) |
| Entry | VWAP touch from open + 60 min | place SOURCED 00:10:08; patience SOURCED 00:15:10; definition OURS |
| Stop | session low, floor max(0.5%, 0.6 ATR14d) | session low SOURCED 00:10:48; floor OURS |
| VWAP stop | epoch 1h close beyond VWAP | SOURCED 00:25:50 |
| Exit | 20:00 UTC | OURS |
| Session open | 13:30 UTC (NY) | OURS |
| Phase label | MARKUP etc. | OURS (spec s1) |
| Pivot ladder | P, S1, R1 | family SOURCED (NK2); window OURS |
| At-level band | 0.25 x ATR14 daily | OURS |
| V1 | 4h RSI14 >= 50 | RSI14 SOURCED; 50 OURS |
| V2 | daily ADX14 >= 20, DI direction | SOURCED (FORMULAS s30, NK55) |
| Fees | 12 bp taker, 6 bp maker, both legs | OURS (nkp2 convention) |
| Funding | stamp rate x notional | OURS |
| Placebo grid | 10 min | OURS |

## Gates (VALIDATION primary cells; all needed for PASS)
Mean net R > 0 at 12 bp; trade-level bootstrap 95% CI low > 0 (5000 draws); day-cluster bootstrap CI low > 0 (cluster = session date, all coins; 5000 draws); ex-best-5 mean > 0 (the 5 best days removed); placebo beaten (p < 0.05); Benjamini-Hochberg q <= 0.10 over ALL 5 primary cells with the one-sided day-cluster bootstrap p (net R <= 0); n VAL >= 100 per cell, else UNDERPOWERED (not FAIL, not PASS); DEV gross R >= 2 x DEV fee R (12 bp), computed and printed before the VAL statistics, a failing cell is FAIL. An UNDERPOWERED cell is never pooled with another and no condition is loosened afterwards. Rule verdict: PASS if any primary cell PASSes, FAIL if none passes and at least one is powered, UNDERPOWERED if all are underpowered.

## Kill rules and protocol
One run, no re-runs with changed values; `python study.py run` refuses to run while study.py / PRE_REG.md / test_study.py are uncommitted. A BUG fix after seeing results is allowed only as a separate commit and is listed under "Deviations" in RESULT.md. No parameter or cell is changed after seeing a result. DEV gross vs 2 x fee ends a cell before VAL is read. Controls are reported in their own table and never pooled with primary.

## Design items not implemented (declared before any run)
1. Item 13 funding/OI descriptive columns (prior-day funding sum vs its own 90-day percentile, 5-day OI change): not produced (never a gate). Funding enters only as the stamp cost above. OI files exist for 23 coins but no column is built.
2. Item 14 tags: the coin trend phase tag is produced (P1 mix reported); the cycle-clock / BIBLE reading and the CBP lean tags are not produced.
3. Separate 4h / daily / weekly signal rows (see cell table note): not expressible and no cell may be added.
4. The 1m universe is 13 coins, not the 4 named in the design's data note (the fetch of public 1m with volume found 13 coins with history on both sides of 2024-01-01). The design's rule that a coin enters a split with >= 95% minute coverage is replaced by a per-day rule (prior 13:29 bar present, >= 90% first-hour bars); the per-coin valid-day counts are reported.
5. `tf_resample.py` is a cross-check only (see Layers module use).
6. Funding for C6 coins without a funding file (NEAR, FIL, ALGO) and for early history before a coin's funding file starts counts as 0 and is reported as the share of trades without funding data.

## Tests (test_study.py, synthetic data, no cache access)
Look-ahead (truncate all data at the read time of day t: every scanner / trap / confirm / skip / HM / V1 / V2 / ATR / pivot value for day t and earlier is unchanged; MUST FAIL under `NKN_BUG=1`, which reads the daily context from the same day), ladder frozen at window start, entry and stop causal (data cut after the entry bar leaves the entry unchanged), fee on both legs with a hand-computed number (E=100, X=102, R=2 -> 0.0606 R at 12 bp), split by signal bar, gap-through-stop fill at the open, stop beats a VWAP-hour exit in one bar, entry-bar stop, R floor, funding hand case, a control-phase / short / UTC / 15m trade never lands in a primary cell, trap / scanner / confirm / skip hand cases, session-anchored first hour, pivot and at-level hand case, VWAP hand case, entry fill rules, HM WMA vs manual and causal, epoch alignment vs `tf_resample`, BH hand example, ex-best-5, loader assertions, file-size check.

## Weaknesses stated up front
Power is the main risk: +2% mover AND trap AND confirm AND HM in MARKUP may give few events per coin, so P-cells may be UNDERPOWERED; P2 (+1%) exists for that reason, pre-registered. NY 13:30 as the primary session is OURS, not NK's. HM formula and the line reading are unverified. The 4% skip overlaps the +2% scanner. The pivot level is probably circular with the trap (NK2's best pivot row was -0.009 R). VAL is one bull-then-bear cycle: a pass would be a regime result, not a cycle law. Coins are correlated; day clusters are the honest unit. Spot prices stand in for the futures price; funding is applied from the futures files.
