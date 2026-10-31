# Testnet co-trade: operator calls, Claude places and records (design, 2026-10-31)

Ask (operator, 2026-10-31, condensed by the Super Session): trade on the Deribit TESTNET together; he watches the chart and says
"short 100 here / buy here with a double", Claude places it and RECORDS his exact words and what he is watching; scale-in
ladders that double the total (X, 2X, 3X, 6X ...); orders resting before the wick, exits ready at once; US open hours.
Status: design only, nothing built. Testnet only. Numbers: SOURCED = exchange/clock facts, OURS = our runs or choices.

## 1. Capabilities: what exists vs what is missing

| Need | Exists today | Missing |
|---|---|---|
| Place limit/market on testnet | `execution/deribit_orders.py:487` `place()` (testnet-only, refuses bad input offline) | A command that takes his words -> one structured order, shows it, places it, journals it |
| Reduce-only, cancel, amend, flatten | `deribit_orders.py:396` cancel, `:400` cancel_by_label, `:507` amend, `:408` close_position | Nothing for v1 |
| Protective stop per fill | `executor.py:322` ensure_stop: server-side `stop_market` reduce-only over the FULL filled size (`deribit_orders.py:377`) | Reuse it for manual orders |
| Ladder of resting limits | Plan type `ladder` (`trade_plan_validator.py:117`, `plan_compiler.py:144`), even spacing, any size_multipliers; executor places all rungs up front (`executor.py:425`) | Size rule "add = current total" (1,2,3,6,12...) as a generator; spacing in % or points; cancel the rest on stop |
| Exit order ready the moment a rung fills | Targets are placed only AFTER the entry phase ends (`executor.py:508`, `:535`) | Per-fill take-profit: each rung fill places its own reduce-only limit TP at once (needed for "wick, sold immediately") |
| Size caps that fail closed | Account cap $10,000 (`risk_guard.py:22`), plan ceiling $10,000 and max loss -$500 (`trade_plan_validator.py:35-36`), max 10 rungs (`:38`), daily loss -$500 (`daily_loss_guard.py:8`) | A ladder preflight that sums ALL rungs (worst case) against the caps before the first order |
| Kill switch / HALT | `kill_switch.py` (cancel all + flatten + writes `execution/HALT`); executor re-checks HALT before every order (`executor.py:205`, `:239`) | Co-trade command must call the same HALT check; "flat" / "kill" as his spoken words |
| Restart safety | Journal replay `journal.py:91` reconstruct_belief; position_manager respawn (`auto_trader.py:702`) | Co-trade restart: read open orders + position from the exchange, compare to journal, refuse new orders on mismatch |
| One position per account | Deribit nets one position per account (`TESTNET_SUBACCOUNTS.md`); R8 refuses if the account is busy | Operator decision d-cotrade-use-existing-account: no new account; use the spare slot jishu_22, else main. While he holds a position the auto-trader on that slot is refused by R8 (safe); an account-wide kill flattens his trade too |

## 2. The doubling ladder: worst case (OURS, `ladder_math.py`, computed independently of repo code)

Example: X = $100 short, P0 = 100,000, one rung every +0.4 %, one stop 0.4 % above the last rung. Adds 1,2,3,6,12,24,48 X.

| Rungs filled | Total size | Price moved against | Loss at stop | Margin at 10x / 20x |
|---|---|---|---|---|
| 1 | $100 (1X) | 0.40 % | $0.40 | $10 / $5 |
| 3 | $600 (6X) | 1.20 % | $4.00 | $60 / $30 |
| 5 | $2,400 (24X) | 2.01 % | $18.38 | $240 / $120 |
| 7 | $9,600 (96X) | 2.81 % | $75.67 | $960 / $480 |

- Size grows 96x over 7 rungs; rung 8 would be $19,200 and the existing $10,000 account cap refuses it. Hard cap (OURS): 7 rungs at X=$100;
  generally sum of all rungs <= $10,000 and loss-at-stop <= $500, checked before the first order, else nothing is placed.
- Price must come back ~0.78 % from the last rung just to break even. A 2.8 % one-way run in 4 h is common (section 4: 35 % of US days move >= 2 % one way).
- Repo already tested this shape: `eur_low_us_sweep_2026-10-14/RESULT.md` finding 6: 1-1-2-3 ladder wins 64 % of trades, mean -0.02 % (t -0.32): "a martingale: many small wins, a few 7-unit losses".

## 3. Recording: every co-trade becomes research data

| What | Where | Committed? |
|---|---|---|
| Journal line per instruction: `ts_utc`, `seq`, `said` (verbatim), `heard` (Claude's reading), `action` (side, type, size in X and $, price, stop, TP), `market` (mark, bid/ask, 1m/15m close, session minute vs US open), `aid` (live-aid snapshot: verdict, US-open board levels, OI tile sentence), `shots` (shot ids), `result` (order ids, fills, P&L) | `<main checkout>/runtime_data/cotrade/<YYYY-MM-DD>.jsonl`, append-only, gitignored (`.gitignore:235` `runtime_data/`) | NO (has order ids, sizes, P&L) |
| Screenshot he pastes | `scripts/dev/shot.py ingest` store (same runtime_data, gitignored); journal keeps only the shot id | NO |
| Research extract per session: time, said, chart state, outcome in % of price and R, no ids/balances | `research/testnet_cotrade_2026-10-31/SESSIONS.md` | YES |
| Rule-level decisions (e.g. "ladder max 7 rungs") | `system/OPERATOR_DECISIONS.md` | YES; single trade calls never go there |

Live aid snapshot: the page is opened from disk, so v1 copies its state from the same public feeds in `cotrade.py`; v2 adds a
127.0.0.1-only bridge the page POSTs its current board to once per 5 s, so the journal stores exactly what he saw. The page never places orders.

## 4. US open (SOURCED clock, OURS stats from `us_window_stats.py`, BTCUSDT 1m 2022-01..2026-09, 1235 weekdays)

US cash open 09:30 New York (SOURCED). **Until Fri 2026-10-30: 13:30Z. US DST ends Sun 2026-11-01: from Mon 2026-11-02 the open is 14:30Z**
(back to 13:30Z on 2027-03-15). US data slot 08:30 ET = 13:30Z from Monday. India: open 20:00 IST from Monday (was 19:00).

| Measure (OURS unless named) | Value |
|---|---|
| US 4 h range (high-low after the open), p25 / median / p75 / p90 | 1.45 / 2.06 / 2.98 / 4.25 % (winter rows: median 2.37 %) |
| Max move up / down from the open in 4 h, median | 0.79 % up, 0.89 % down; both >= 0.5 % on 40 % of days (the "both ways" day) |
| First 30 min range, median; share of the 4 h range | 0.87 %; 44 % of the 4 h range is set in the first 30 min |
| 60 min before the open: range, median | 0.74 %; its direction matches the US 4 h direction 49.8 % (a coin flip) |
| First 10/15/30 min direction predicts the rest | No (`us_open_oos_2026-10-30/REPORT.md`, 0.475-0.501, both samples) |
| US-open 15 min bucket is a top-2 volatility bucket | Yes (same report; it moves 13:30Z -> 14:30Z with DST) |
| Pre-US squeeze -> US range | 1.54x the 8 h box; first break holds 52 %; 23 % break both sides (`pre_us_squeeze_2026-10-29/RESULT.md`) |
| Levels within 0.25 % of the open reached in 2 h | 80-88 % (`us_open_levels_2026-10-30/RESULT.md`); a break of a nearby low is reclaimed within 2 h 93-95 % (`eur_low_us_sweep_2026-10-14`) |
| "Something happens just before" as a tradable signal | NOT_IN_DATA (no test shows a pre-open pattern that sets direction) |

Ideas (OURS, to test with his recorded sessions, not rules yet):
- Range = the levels the live aid's US-open board already shows (day H/L so far, PDH/PDL, 15-min opening range). Fade sweeps of a level within 0.25-0.5 %, never add after a break that does not reclaim within 30-60 min.
- Ladder width: inside the median first-30-min range (~0.9 %) the ladder is a scalp tool; rungs spaced >= 0.3 % and total width <= ~1.2 % keep it inside a normal US move; beyond p75 (3 %) it is a trend and the stop must take it.
- Side: no data favours a side at the open. Let the level decide (short above a swept high, buy below a swept low), and his call.
- Do NOT trade: first 2 min after 13:30Z data releases and the open (spread/slippage), FOMC/CPI days when the news tile says EVENT, weekends/US holidays, after the daily loss cap.

## 5. Phased plan (each test must fail on the old code first)

| Phase | What he gets | Files | Tests that fail on old code | Worker |
|---|---|---|---|---|
| P1 (this week) | He says "fire: short 100 at 110500 stop 111000" (no extra confirm); Claude shows the reading, places it on the existing testnet slot (jishu_22, else main), server stop on fill, line in the journal | new `execution/cotrade.py`, `execution/test_cotrade.py` | refuses with no stop; refuses off testnet; refuses under HALT; refuses size over cap; journal line has `said` verbatim; restart with an open order reconciles before a new order | Sonnet agent |
| P2 | "Short 100 doubling from 110500 to 111500, 5 steps": rung prices + sizes (1,2,3,6,12) shown with worst-case loss, then placed as resting limits; cancel the rest on stop | `cotrade.py` ladder, `plan_compiler.py` size rule `double_total`, tests | worst case > cap refuses before ANY order; sizes = 1,2,3,6,12 X; spacing in % and points; both directions | Sonnet agent |
| P3 | Each rung fill places its own reduce-only TP at once; one stop over the whole size moves with fills | `cotrade.py`, maybe `executor.py` targets | TP exists within one poll of a fill; partial fill TP = filled size only | Sonnet agent (live-path gates) |
| P4 | Live aid "Co-trade" panel: total size, avg entry, next rung price and size, distance to stop, loss at stop, suggested action from the US-open board; local bridge | `tools/live_aid/live_aid.html`, `cotrade.py serve` | panel reads NOT_IN_DATA when bridge is down; numbers match a hand case | Sonnet agent; layout check Haiku |

## 6. Honest risks and pushback

- The doubling ladder is a martingale. It wins most days and loses big on trend days; the repo already measured no edge for 1-1-2-3 (mean -0.02 %). With caps the loss is bounded ($76 worst case at X=$100); without them it is unbounded.
- Testnet fills, depth and wicks are not real: results show process (speed, discipline, recording), not edge. Fees (the repo's runs assume 0.05 % taker per side, OURS) and slippage are not in testnet P&L; the extract must subtract them.
- "Quick trades" mean market orders in the most volatile 15 min of the day: expect worse prices than he sees.
- To answer "does his entry beat the layers": per call record which layers fired in the same 15 min (from the live aid), the entry, 15/60/240 min outcome, MFE/MAE, fee-net R; compare with (a) the layer's own signal and (b) a random entry at the same minute. Need about 50 calls before reading anything.

## 7. Hedge in profit ("satellite / cluster"), added 2026-10-31

Ask (operator, voice, 2026-10-31): "if I am in a trade and I am in profit, I would like to launch a counter trade, which will be my hedge
... how much hedge we should do should be understood ... depending on how the market is changing ... this should also be built into this."

| What the repo already has | Source |
|---|---|
| The idea, written down: any open position can spawn small, separately-stopped counter positions on a separate subaccount | `items/T048_satellite_framework.md` (OPEN, design only) |
| His two-account hedge ask (hedge after fees+profit are covered; hedge at a Bollinger/divergence extreme) | `items/T053_two_account_hedge_scalping.md` |
| Practitioner research: no external evidence that hedge loops pay; an equal-size hedge is flat, so any profit must come from the un-hedge rule | `research/_archive/loose_2026-10/T053_TWO_ACCOUNT_HEDGE_RESEARCH.md` |
| Backtest of 14 hedge variants, 1m BTC 2022-01..2025-08, 0.05 % taker per side (OURS): EVERY variant was worse than not hedging, by 9 to 250 bp per trade (t -5 to -125) | commit 4a36c8a38, `t053_hedge_variants_2026-10-30/results.txt`; later reverted from trunk (lint), so it is not on trunk now |
| Which outcome class could trigger a hedge (proposal) | `research/fast_track_2026-09-27/T058_BROKEN_EXTREMES.md` |

Corrections to the idea (OURS):
- Deribit nets one BTC-PERPETUAL position per account. A counter order on the SAME account is not a hedge; it just closes part of the
  trade. A real two-sided hedge needs the second leg on ANOTHER existing slot (jishu_1..4 / jishu_22 / main: no new key, per his decision).
- A hedge of equal size locks the profit and pays two more fees plus funding on both legs. Economically that equals taking profit,
  but costs more. A part-size hedge equals a part close. The only thing a hedge buys is keeping the first trade open for a later target.
- So "how much to hedge" is really "how much to take off, and when to put it back". Size rule options to test on his recorded sessions:
  fixed share (25/50/100 % of the open size), share that grows with open profit in R, or full hedge at a named level/extreme.

Build (P5, after P1-P3): `cotrade.py hedge --of <trade> --pct 50 --at <price|now> --stop S` places the opposite leg on a second
existing slot, journals the parent/child link, and the live aid shows net size across both accounts. Caps sum both accounts.
A kill on one slot must flatten BOTH legs (else a half-closed hedge becomes a naked trade).

## 8. Where we are today (2026-10-31)

| Item | State |
|---|---|
| Ready to fire your trades now? | NO. P1 (`cotrade.py`) is a ready card, not built. |
| Rule blocking it | CLEARED 2026-10-31 (d-cotrade-testnet-carveout, operator 'approved'): exception now in CLAUDE.md + MOVED_RULES.md. Wording: "testnet orders the operator calls by name, placed only through cotrade.py, journaled; never mainnet". |
| Showing it in the browser | After P1: you say "fire ...", the reply shows the order, and the same order appears on test.deribit.com (Chrome) under Open orders / Positions. |
| Mainnet afterwards | Separate money gate, your call only. Exists: `--mainnet` + typed confirmation, $50 per order cap (`deribit_orders.py:84-87`), `execution/MAINNET_READINESS_CHECKLIST.md`. Repo goes private at mainnet (CLAUDE.md). |
