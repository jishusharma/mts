# PRE_REG: T12 funding extreme reversal (1d, two cells A long / B short, OI descriptive), 2026-11-14, frozen before any outcome

Design: `EDGE_WAVE3_DESIGN_1114.md` (side-session notes folder), section "T12 FUNDING EXTREME REVERSAL" plus SHARED RULES T7-T12. The design is frozen and implemented as written; every forced difference is listed under Deviations. Frozen BEFORE any trade return, exit, P&L or placebo number is computed: only the counting step (signal and unit counts, stop distance as % of entry, which depends on the entry open and ATR but on no later bar) was run. Research, not advice; nothing is an edge until a fee-net out-of-sample result passes. SOURCED = named file or doc; OURS = our choice.

## Context

Question: when funding prints an extreme (one side crowded) and price then prints a reversal bar in a BTC phase where that crowd is wrong, does the crowd unwind over about 10 days as a price effect (not carry), net of 12 bp?
Regime: phase-specific gate per cell on the BTC phase label (SOURCED labels, MTS_BRAINS_SPEC lines 24-29; mapping to funding OURS). Cell A (long): MARKDOWN, CAPITULATION, RELIEF, ACCUM-RANGE. Cell B (short): MARKUP, DISTRIBUTION. BTC cycle state BULL/BASE/BEAR (smoothed, below) is a descriptive row on every cell, not a gate.
Phase: the label of the signal day d from `F:\MTS\data_cache\mts_brains\phase_daily.csv` (BTC only; the brain builds the row of day d from closes through d-1, so it is usable on day d; checked by the `close_used` column in the audit stage). Labels are empty before about 2014-2018 rows in the file and such days never qualify.
Session: none, because daily bars on a 24/7 market; funding prints at 00:00, 08:00, 16:00 UTC are used at their print time only.
Entry: signal on completed daily bar d (funding extreme through d, reversal bar on d); entry at the open of bar d+1; per coin and cell a 10-day cooldown; hold to the close of day 10 or the stop.
Regime mix: reported in RESULT from the data (share of DEV and VAL trades in BTC cycle BULL / BASE / BEAR, and in each phase label, for each cell). Expected from the design: VAL is one bull (2024 to 2025) then one bear (late 2025 to 2026), so a sign flip between years and cycle states is likely.

## Rules

| Item | Rule | Label |
|---|---|---|
| Universe | the union of the file lists of `binance/wave2-1114/funding` and `binance/combo-edge-miner-1114/funding` under `F:/MTS/data_cache`, read at run time; counted at freeze: 68 coins (BTC and ETH once; wave2 file wins for a coin in both). Listed below. Delisted coins kept | SOURCED (design SHARED RULES) |
| Daily bars | Binance spot `<COIN>USDT` 1d from `wave2-1114/spot_1d` or `combo-edge-miner-1114/spot_1d`. Each coin is split into contiguous segments at missing days (LUNA hole 2022-05-13..05-31 = 18 days; FTT hole 2022-11-15..2023-09-22 = 311 days; no other coin showed a gap in the checked files). History, ATR and every trade window live inside one segment, so no trade spans a hole | SOURCED hole dates (design); segmenting OURS |
| Alive | a coin-day is alive with >= 260 daily bars of history in its current segment. Dates with fewer than 30 alive coins (spot-based count) are excluded from verdicts and counted separately | SOURCED (design) |
| Funding feature F3(d) | sum of the funding `rate` prints with UTC day in d-2..d divided by 9, i.e. the mean per-8h rate over the last 3 days through d. Valid only if each of the 3 days holds >= 3 prints. Prints are rounded to the second. Equals the mean of the nine 8h prints when the coin pays 8-hourly, and stays a per-8h equivalent if a coin's interval is shorter | OURS (smoothing); per-8h equivalent is a clarification, see Deviations |
| Extreme, cell A | F3(d) <= the 5th percentile of the F3 values of days d-180..d-1 (linear-interpolated percentile, >= 150 valid values in that window, F3(d) itself excluded from the window) AND F3(d) <= -0.0001 (-0.01% per 8h) | percentile and window OURS; floor SOURCED baseline (Binance interest-rate component 0.01% per 8h), used as floor OURS |
| Extreme, cell B | F3(d) >= the 95th percentile of the same window AND F3(d) >= +0.0001 | same |
| Reversal bar | A: close > open and close > prior day's high. B: close < open and close < prior day's low | OURS |
| Phase gate | A: label in {MARKDOWN, CAPITULATION, RELIEF, ACCUM-RANGE}; B: label in {MARKUP, DISTRIBUTION} | SOURCED labels, mapping OURS |
| Cooldown | per coin and cell, a signal fires only if its bar index is >= 10 bars after the previous fired signal; the clock moves when a signal fires (flag + reversal + gate), even if the trade is later skipped | OURS |
| Entry | open of bar d+1, which must be the next calendar day inside the same segment | SOURCED (design: entry at t+1 open) |
| Stop | entry -/+ max(2.5 x ATR14[d], 6% of entry). ATR14 = Wilder per FORMULAS.md on the segment (first TR uses its own close as previous close, seed = simple mean of the first 14 TR), taken at the signal bar d. R = stop distance / entry. Stop >= 1.5% of entry always holds (floor 6%) | OURS (2.5, 6%); ATR period SOURCED (Wilder 14) |
| Stop fill | checked on daily bars from the entry day through the exit day. Stop wins ties: any bar whose range touches the stop exits there, even if its close was favourable. A bar that opens beyond the stop fills at the open (gap) | OURS (design: stop wins ties) |
| Exit | first of the stop or the close of the 10th bar (entry bar = day 1). 10 days in market | OURS |
| Funding charged | real signed funding: sum of the cached `rate` prints with entry_open < print <= UTC midnight at the end of the exit day (or stop day). Long pays +rate; short receives +rate (cost = side x sum). No funding is imputed: the trade is skipped unless the planned window holds >= 3 prints per day and the cache covers it | SOURCED (design: real signed funding) |
| Fee | 12 bp round trip = `2*BINANCE_TAKER + SLIPPAGE_RT_S13` imported from `MyTradingSys/backtest/fees.py` (0.0012). Fee in R = 0.0012 / stop%. No private cost constants | SOURCED (fees.py) |
| ENDED | if the segment ends inside the window and it is the coin's last segment and the coin stopped trading >= 30 days before the data end: close at the last bar, flagged ENDED. Otherwise the trade is skipped (window past segment) | OURS (design: close at last bar, flag ENDED) |
| Data end | signal bars before 2026-11-01 only (VAL ends 2026-10-31, the funding end) | SOURCED (design) |
| BTC cycle state | the `cycle` column of the phase table, smoothed: a new state counts only after 10 consecutive days; until then the prior state holds | OURS (design) |
| Seed | 1114 | OURS |

Trade outcome definitions: gross = side x (exit/entry - 1); price-only net = gross - fee; total net = gross - fee - side x funding sum. All in R by dividing by the stop fraction. Primary metric: mean R per trade, price-only net R for bars 2, 3, 5, 6, 7, 8 (design: a pass needs price-only excess > 0); total net R is reported next to it.

## Data

Public Binance data only, cache `F:\MTS\data_cache`: `binance/wave2-1114/spot_1d` + `funding`, `binance/combo-edge-miner-1114/spot_1d` + `funding` + `oi`, `mts_brains/phase_daily.csv`. Tests never read the cache. Funding prints are jittered by a few ms around the 8 h grid and are rounded to the second.
Universe (68): 1INCH AAVE ADA ALGO ANKR ATOM AVAX AXS BAND BAT BCH BNB BTC CELR CHZ COMP CRV DASH DOGE DOT EGLD ENJ EOS ETC ETH FIL FTM FTT GRT HBAR ICX IOST IOTA KAVA KNC LINK LTC LUNA MANA MATIC MKR NEAR NEO OCEAN OMG ONE ONT QTUM RUNE RVN SAND SNX SOL STORJ SUSHI THETA TRX UNI VET WAVES XLM XMR XRP XTZ YFI ZEC ZIL ZRX (all with USDT).
Survivorship: the list is a hindsight list; delisted and collapsed coins that were not listed are absent and the list holds coins large enough to be listed. This biases longs UP and shorts DOWN. The RESULT carries an ex-ENDED row and an ex-LUNA/FTT row (drop trades on LUNA and FTT) and states this direction.
OI (descriptive only): 20 coins in `combo-edge-miner-1114/oi` (daily `ts, oi`, ts = end of the UTC day minus 1 ms); 7-day OI change = oi[d] / oi[d-7] - 1 at the signal day d.

## Splits

DEV = signal bar <= 2023-12-31; VAL = signal bar >= 2024-01-01 (ends 2026-10-31). 12 bp. Unit of statistics: ISO entry week over all coins (Monday-start; a Sunday belongs to the week of its Monday; weekly bars are NOT used for any signal, only for clustering).

## Pass bars (each cell separately; numbered as the design: wave-2 bars 1-7, wave-3 additions 8-9)

1. VAL fresh: n >= 30 trades and >= 20 distinct entry weeks, else UNDERPOWERED (never FAIL, never KILL).
2. VAL mean price-only net R > 0 and the moving-block bootstrap 95% CI low > 0 (blocks of 2 consecutive calendar ISO entry weeks over the span first to last trade week of the cell and split, empty weeks kept, 2000 resamples, seed 1114; resampled mean = sum of R in drawn weeks / trades in drawn weeks). One-sided p = (resamples with mean <= 0, plus 1) / (resamples + 1).
3. DEV mean price-only net R > 0 (sign agreement).
4. Excess over the like-for-like placebo: for each real VAL trade draw one day of the SAME coin, same side, same VAL split, same BTC phase label as the real signal day, within +/-8 ISO weeks (56 days) of the real signal day, carrying the same extreme-funding flag (same gate, percentile and floor) but NO reversal bar, not the real day itself, same stop % as the real trade (the placebo trade uses the real trade's stop fraction), same 10-day exit rule, same real funding (so carry cancels), same planned-window and funding-coverage rules. One draw = mean over the matched trades; 1000 draws, seed 1114. Real mean (over the matched trades) must be >= the 97.5th percentile of the draw means and excess = real mean - mean of the draws > 0. A real trade with no candidate is dropped from both sides and counted. Global variant also reported: candidates = any flagged no-reversal day of the coin in VAL with the same label, any distance. Bar 4 is judged on price-only net R and the same-window variant; total net R and the global variant are reported.
5. Ex-best-5 entry weeks (VAL, price-only): drop the 5 entry weeks with the largest summed net R; mean of the rest > 0. When the cell has fewer than 30 weeks, ex-best-2 is used instead (stated in RESULT). The 3R-capped row is not applicable (fixed stop, fixed time exit); stated, not run.
6. Baseline: mean net return per day in position of the VAL trades (price-only net % per trade / days held, averaged over trades, fee included) >= the equal-weight basket of the same side over flagged-state days (each VAL day with the cell's phase gate and extreme-funding flag on at least one coin: equal-weight mean over the flagged coins of the signed open-to-close return of the next bar; then mean over those days; no fee charged to the basket, which favours the basket). The mean funding carry in bp per trade (VAL) and the basket's carry per day are printed next to it. Judged on price-only; total net also shown.
7. Top-3 coin removal (VAL, price-only): remove the coin with the largest summed net R, then the next, then the next; the mean after the third removal must stay > 0 else FRAGILE (reported, blocks PASS).
8. Leave-one-year-out (VAL calendar years of the signal bar, price-only): every leave-one-year mean > 0, else FRAGILE (reported, blocks PASS).
9. Rows by BTC cycle state (BEAR/BASE/BULL) and by year always printed (DEV and VAL). SIGN-FLIP = positive price-only mean only in the cycle state opposite to the gate (cell A long: BULL; cell B short: BEAR) and <= 0 in the gate-aligned states (A: BEAR + BASE; B: BULL + BASE); a SIGN-FLIP is not a PASS.
Holm: over the two cells (their bar-2 one-sided p-values) reported next to each verdict; over the 9-cell wave-3 family the worst case min(1, 9 p) is reported (the other 7 cells' p-values are not available to this study; the coordinator completes the family Holm). A PASS whose Holm-adjusted p exceeds 0.05 is labelled MULTIPLICITY-FLAGGED.
Also reported (descriptive, no verdict): DEV and VAL separately gross R, price-only net R, total net R, fee in R, funding in R; price-only versus total (carry); ex-ENDED and ex-LUNA/FTT rows; the per-reason counts (TIME, STOP, STOP-GAP, ENDED); OI tercile rows.

## Kill criteria

KILL the funding-extreme-reversal line at the daily level if: (a) both cells have bar 1 true and both VAL price-only net means <= 0; or (b) both cells' real means are <= the placebo 97.5th percentile and the two cells together hold >= 100 VAL trades. An UNDERPOWERED cell is never KILL. Meaning: dead at the daily level; the OI conclusion stays open (only 20 coins). A killed line cannot be labelled PASS.

## Verdict vocabulary

Per cell: UNDERPOWERED (bar 1 fails; read as UNTESTED, never as proof of no edge), PASS (bars 1-8 hold, not SIGN-FLIP), FRAGILE (bars 1-6 hold, bar 7 or 8 fails), SIGN-FLIP (bars 1-6 hold but positive only opposite to the gate), CARRY-ONLY (total net VAL mean > 0 with bootstrap CI low > 0 but bar 2 on price-only fails), FAIL (bar 1 holds and a bar among 2-6 fails and not CARRY-ONLY; the first failing bar is named). NOT-A-PASS = descriptive rows. A pass on one cell with the other failing is reported as partial. Overall line states both cells.

## Seen results

None. Only inventory counts were read (file lists, meta sidecars, row counts, the counting step below). The design's expected counts (Cell A 25-50 weeks, Cell B 25-40 weeks) came from the power designer, not from outcomes.

## Known weaknesses

- Extreme funding persists in a bull, so shorts can keep losing; a long at negative funding collects carry, so total net can beat zero with no price edge (the reason for the price-only/total split and CARRY-ONLY).
- VAL is one bull then one bear, so a sign flip is likely; OI covers 20 coins only.
- Weeks, not trades, are the sample: coins move together; the gate below counts weeks.
- Spot prices stand in for the perp (basis not modelled); no fill or liquidity model for small coins; collapsed coins' last-bar exits are optimistic.
- The 180-day percentile, 3-day smoothing, reversal bar, 2.5 ATR / 6% stop, 10-day hold and cooldown, phase mapping and the smoothing of the cycle state are OURS. BIBLE.md has no line on funding; these are OURS and never the trader's.
- Measured at the counting step: the stop is far wider than the design expected (median stop 18% to 25% of entry, not 6% to 12%; 2.5 x ATR14 on altcoins is large), so fee in R is about 0.005 to 0.007 R, below the 0.010-0.020 R quoted in the design. No parameter is changed because of this.

## Power gate

n = VAL distinct entry weeks per cell from the counting step (below): Cell A 43, Cell B 69. m = 2 (the two cells). sd = 1.0 R, the floor, because the design asks for the DEV week-level sd but the counting step may not compute outcomes (Deviation 1). cost = median fee in R at the counting step (A 0.006, B 0.007).

    python scripts/dev/prereg_gate.py --n 43 --sd 1.0 --cost 0.006 --m 2 --sd-source "T12 PRE_REG: floor 1.0 R (no DEV outcome computed before freeze); counts.json"
    n 43 sd 1 m 2 z_holm 2.241 MDE 0.470 R + cost 0.006 = 0.476 vs max plausible gross 0.3; n needed 110
    BLOCK: do not freeze (write BLOCKED.md with these numbers)

    python scripts/dev/prereg_gate.py --n 69 --sd 1.0 --cost 0.007 --m 2 --sd-source "T12 PRE_REG: floor 1.0 R (no DEV outcome computed before freeze); counts.json"
    n 69 sd 1 m 2 z_holm 2.241 MDE 0.371 R + cost 0.007 = 0.378 vs max plausible gross 0.3; n needed 111
    BLOCK: do not freeze (write BLOCKED.md with these numbers)

Decision (OURS): BLOCK stated for both cells. The run goes ahead because the design orders it ("gate expected BLOCK at sd 1 R", a BLOCK is reported, not hidden, and the run is still ordered). No BLOCKED.md is written for that reason. A FAIL or UNDERPOWERED result reads as UNTESTED at this power (MDE about 0.4-0.5 R against a plausible gross below 0.3 R), never as proof of no edge. A PASS would still need the blind review.

## Counting step (signals and units only, no outcomes; `t12_count.py`, output `counts.json`)

Universe 68 coins loaded; dates with fewer than 30 alive coins (excluded from verdicts): 618 calendar days.

| Cell | Split | flag days (alive, gate, extreme) | flag + reversal bar | fired after cooldown | trades planned | distinct entry weeks | ENDED | skipped (no funding) | median stop % |
|---|---|---|---|---|---|---|---|---|---|
| A long | DEV | 2346 | 456 | 296 | 296 | 72 | 0 | 0 | 25.5 |
| A long | VAL | 996 | 190 | 126 | 125 | 43 | 0 | 1 | 20.4 |
| B short | DEV | 5949 | 908 | 608 | 608 | 55 | 0 | 0 | 18.3 |
| B short | VAL | 6098 | 1079 | 613 | 611 | 69 | 3 | 2 | 17.6 |

Both cells clear bar 1 on counts (VAL n >= 30 and weeks >= 20) before any outcome. 67 coins carry trades in each cell. The design's expected 25-50 and 25-40 weeks were met or exceeded for cell A (43) and exceeded for cell B (69).

## Deviations

1. Power gate sd: design says sd from the DEV week-level sd of the counting step. The counting step may not compute outcomes, so the floor 1.0 R is used with `--sd-source` naming this section. The measured sd goes into RESULT.
2. F3 formula: "mean of the 8h prints over the last 3 days" is implemented as (sum of all prints with UTC day d-2..d) / 9, valid only with >= 3 prints on each of the 3 days. Identical for 8-hourly coins; for any coin whose funding interval is shorter it stays a per-8h equivalent instead of an average of shorter-interval rates.
3. Unit of the bootstrap: design says "block 2 weeks"; implemented as a moving block over consecutive calendar ISO weeks including empty weeks (a ratio mean per resample as in T6).
4. Baseline and SIGN-FLIP, leave-one-year-out and ex-LUNA/FTT definitions are not spelled out in the design; the readings above are frozen here before any outcome.
5. The expected stop (6-12%) and fee in R (0.010-0.020) in the design differ from the measured stop distribution (above). Rules unchanged.

## Protocol

1. This PRE_REG, `t12_core.py`, `t12_stats.py`, `t12_count.py`, `t12_run.py`, `test_t12_core.py` (synthetic bars: look-ahead, stop wins ties, fee arithmetic, funding sign, ISO-week Sunday test, cooldown, hole and ENDED handling, planted edge, no-edge, placebo) and `mutation_check.txt` are committed together BEFORE any outcome is computed.
2. `t12_run.py` (also committed before any outcome; smoke-tested only on synthetic bars) builds the trade list, then statistics, RESULT.md and results.json. A mechanical bug found later is fixed and logged in RESULT; rules and parameters are never changed after seeing outcomes. No extra cells.
