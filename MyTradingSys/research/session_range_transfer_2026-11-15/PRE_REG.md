# PRE-REGISTRATION BRIEF: session range transfer (card edge-brief-session-levels, Sonnet builder, 2026-11-15), NOT YET FROZEN

Status: brief with counts only. No return, R, win rate or outcome column was computed or read; no bar at or after 2024-07-01 was loaded (`counts_only.py` drops them at load and asserts). Labels: SOURCED = cited file:line; OURS = chosen here. Changing any parameter after the first outcome = a new trial. Hand-off: a Sonnet session copies this into a frozen PRE_REG (one run), adds `fwd_*` window names in its own code, then runs it.

## Hypothesis (3 lines)
1. After a quiet Asia session, the Asia high/low is a stored-order boundary: the first 15m CLOSE beyond it inside London (07-10 UTC) starts a one-way move (range expansion), so the break is traded WITH the break, not faded.
2. Same transfer one session later: the London range (07-13 UTC) broken at the first 15m close inside NY (13-16 UTC).
3. A narrow prior session (width in the lowest third of the last 20) means compressed inventory, so expansion should be larger relative to the stop (the stop is the opposite range extreme, so a narrow range is also a small risk).

## Mechanism (why it could pay after cost)
Liquidity thins in Asia, so its extremes hold unfilled stops and breakout orders; London and NY opens bring the volume that sweeps them. A close beyond the boundary (not a wick) with a structural stop at the other side of the range gives a defined risk and a 2R target. The edge, if any, is range expansion at a session handover, a different object from the level fades and the sweep-reclaim that already failed.

## Why this is NOT a repeat (verdicts.py check matched only on words)
| Prior | Result | Difference |
|---|---|---|
| T04 first-touch sweep-reclaim fade PDH/PDL/PWH/PWL (edge_hunt EDGE_TABLE.md) | FAIL n 1150, -0.221 R | that FADES a wick through a previous-day/week level and waits for the reclaim; here the CLOSE beyond a session range is traded WITH the break, level = session range |
| T05 / T14 / T09 / T10 level fades | FAIL | all counter-trend fades |
| with_trend_session Shape A (prior-day VAH/VAL acceptance, 4 closes) | FAIL n 717, -0.088 R taker, control beat event 100 % | level = prior-day value area, 4-bar acceptance, bias D+W; here level = the previous SESSION's own range, first close, no acceptance wait, no VA |
| layer_lab session_levels_event_table | 445 failed-break events, event table only, no rule | counter-trend failed break, BTC only to 2024-06 |
| opr_weekly_low_round_sweep, opr_preopen_tops | FAIL / INCONCLUSIVE | prior-week low and round numbers, 60-min horizon |
| bb_range_to_range, bb_range_retest | FAIL / INCONCLUSIVE | Bollinger band logic, BTC only |
Verdict lines for `verdicts.py check`: all 4 BLOCK rows are word overlaps (opr_*, bb_*), none has the same entry object; the frozen PRE_REG must restate this table.
Honest prior: the with-trend control (random same-session entries) beat the events in Shape A, so the random-entry control below is a hard kill gate.

## Context / regime (Context-before-backtest gate)
- Regime: by day, bull/range/bear = D close vs SMA20 +-2 % (OURS, as with_trend_session), reported as `Regime mix:` plus by year; the verdict is on pooled DEV, regime rows are reported, never selected after the fact.
- Phase: none, because this is a first-pass diagnostic on 2020-2023 pooled; phase-first testing is the testnet-forward stage (phase-first method), and the compress arm is the only context filter (Asia/London width in the lowest third of the last 20).
- Session: UTC blocks, OURS: Asia 00-07 range transfers into London 07-10 (H1); London 07-13 range transfers into NY 13-16 (H2); late 21-24 not used.
- Entry: first closed 15m bar whose CLOSE is beyond the prior session range, market entry at that close (taker, honest); no maker arm.
- Window: DEV_EXT 2020-01-01..2021-12-31 and DEV 2022-01-01..2023-12-31 pooled (OPERATOR_DECISIONS D3-dev-ext); VAL 2024-01-01..2024-06-30 sealed until DEV passes; 2024-07+ never read here (holdout; the forward stage is testnet-forward).
- Symbols (10, OURS, all in `F:/MTS/data_cache/binance/<SYM>USDT_15m.npz`): BTC ETH SOL BNB XRP ADA DOGE LINK LTC AVAX. SOL/AVAX/DOGE start late (cache starts 2020-08, 2020-09, 2019-07); NOT_IN_DATA is counted, never filled.
- Data: 15m closed bars only, UTC.

## Exact rule (frozen at PRE_REG time)
| Item | Value | Label |
|---|---|---|
| Range (H1) | Asia = 15m bars opening 00:00-06:45 UTC (28 bars required, else skip day); high/low of those bars | OURS (blocks as with_trend_session / C59) |
| Range (H2) | London = bars 07:00-12:45 UTC (24 bars required) | OURS |
| Width | (high - low) / mid | OURS |
| Compression arm | width <= 33.3rd percentile of the previous 20 same-session widths of THAT symbol (prior days only); first 20 days skipped | OURS |
| Event | first closed 15m bar inside the window (H1 07:00-09:45 UTC, H2 13:00-15:45 UTC) whose CLOSE is above the range high (long) or below the range low (short); one event per symbol per day per hypothesis | OURS |
| Entry | that bar's close, market (taker) | OURS |
| Stop | opposite range extreme; no buffer | OURS (structural, as Shape A) |
| Skip | stop < 0.56 % of entry (= 4 x 14 bp, FABLE_FEE_STOP_RULE.md) counted, never widened | SOURCED FABLE_FEE_STOP_RULE.md |
| Target | entry +- 2 x stop distance | OURS |
| Time stop (value) | 16 bars (4 h) after entry; same-bar stop and target: stop first | OURS |
| Cost | `fees.FEES_ALL_TAKER` entry + exit and `fees.SLIPPAGE_RT_S13` each way = 14 bp round trip, imported, no cost literal | SOURCED backtest/fees.py:27-28,49,62; R1_EDGE_OR_STOP.md:37 |
| Net R | (gross return - 14 bp) / stop distance fraction | OURS |
| Forward windows | named `fwd_*` in code (`fwd_exit`, `fwd_mfe`), entry bar index is the event bar, never earlier | gate hint |
| Cluster | one cluster per UTC day across symbols (verdict n = distinct days) | SOURCED R1_EDGE_OR_STOP.md:66 |
| Control | 200 random draws per event: same symbol, same UTC day, a random closed bar in the same window, same direction, same stop distance and 2R target | as Shape A control |

## Cells and Holm
4 frozen cells: {H1, H2} x {all, compress}. New cells for the gate = 4; `prereg_gate.py --m auto --new-cells 4` gives m = 252 (DEV variants already read plus 4). Primary verdict cell: H1 compress (the hypothesis as written); the other three are secondary and carry the same Holm m.

## Power estimate (counts only, `COUNTS.csv`, run `python -I counts_only.py`, pooled DEV_EXT+DEV, stop floor applied)
| Cell | events | skipped < 56 bp | kept | distinct days (n) | mean stop % | cost_R | n needed (m 252) | gate |
|---|---|---|---|---|---|---|---|---|
| H1 all | 6399 | 38 | 6361 | 1314 | 4.13 | 0.054 | 645 | PASS |
| **H1 compress** | 2725 | 38 | 2687 | **885** | 2.57 | 0.0738 | **763** | **PASS** (MDE 0.210 R + cost 0.074 = 0.284 <= 0.30) |
| H2 all | 8232 | 113 | 8119 | 1376 | 3.57 | 0.0612 | 685 | PASS |
| H2 compress | 3536 | 106 | 3430 | 934 | 2.29 | 0.082 | 822 | PASS |
Gate command: `prereg_gate.py --n <days> --cost <cost_R> --sd 1.37 --sd-source MyTradingSys/research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:71 --m auto --new-cells 4` -> exit 0 PASS for all four rows. DEV alone (2022-23) is NOT powered for the compress cells (n 433 / 472 days, needed 888 / 959, BLOCK at m 252); the pass needs the 2020-21 DEV_EXT, so the two must be pooled and the verdict reported pooled. Caveats: sd 1.37 R and plausible 0.30 R are borrowed (R1 sec. 3, OURS), not measured on this rule; stop% is wide (2.6 %) so R-denominated cost is small, which flatters R but not USD edge: report net bp per trade next to net R. Events across 10 symbols on the same day are correlated; n above is days, not events, for that reason. VAL counts (not gated): H1 compress 120 days, H2 compress 119 days; both under the 763 / 822 needed, so VAL is a confirmation read, not a powered test.

## Kill criterion
- KILL H1 compress: pooled DEV net R (taker) mean <= 0 OR 95 % CI upper < +0.05 R OR event net R <= random-entry control net R in >= 50 % of control draws (Shape A had 100 %). Any one kills the family (session range transfer, this entry object, 15m, 10 symbols, 2020-2023, taker 14 bp); it says nothing about other session blocks, other stops, maker entry or 2024+.
- A cell is a candidate only if net R > 0 at Holm-adjusted p < 0.05 (m 252), control beaten, and the sign holds in >= 3 of 4 calendar years of DEV_EXT+DEV. Then VAL once, then testnet-forward (phase-first method), never a longer backtest.
- INCONCLUSIVE (not FAIL) if the realised n falls under the gate row above.

## Gate hints for the builder of the frozen run
- `counts_only.py` is new code (not a copy): lookahead allowlist row added (trailing 20-day percentile, prior days only); costs only via `backtest/fees.py`, so no cost literal needs a costs.csv row; if the ship gate demands a costs.csv inventory row for a copied study, add it.
- Test must fail on pre-change code once (e.g. an event on the same bar as the range close must NOT be counted).
- verdicts.py add after RESULT; TRIAL_LEDGER row for the 4 cells before the first outcome read.

## Next step
`Next: freeze-session-range-transfer`: a Sonnet session writes the frozen PRE_REG from this brief, a `study.py` using this file's `events()`, one run on pooled DEV_EXT+DEV, honest FAIL. No other action here.
