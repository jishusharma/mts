# PRE-REGISTRATION: pre-US failed-break short build, BTC 1m (frozen 2026-10-28)

Card `backtest-the-operator-s-pre-us-failed-br`. Docs only. The commit that adds this file precedes any commit that adds a result;
`git log` is the proof (convention of `research/gross_effect_screen_2026-10-15/PRE_REG.md`, the template). Status: EXPLORATORY TRIAL.
Nothing here adopts a rule. The run is a separate card (`backtest-pre-us-failed-break-dev-run`), raw, executing sections 1-7 as written.

Labels: SOURCED = file:line or operator shot id. OURS = our judgement (DECISION (OURS), most conservative reading). Operator shots are the
only source for the behaviour; they give no numeric rule, so every number below is OURS unless a SOURCED tag is shown.

## 0. Contract for the executing session
- Zero judgement: if a number is missing the run is BLOCKED with the item named. One run of the primary cell; every cell computed is printed.
- No bar dated 2024-07-01 or later is opened (section 6). No VALIDATION or HOLDOUT read. No live or testnet order.
- The 2026-10-28 day is an anecdote (shots bf4be625432d, 3ca8df9aca33, `research/live_reads/2026-10-17_live_market_1017/READ.md:174`), never a test row; 2026 is outside DEV.

## 1. The behaviour being tested (what the operator did, SOURCED, descriptive only)
Deribit testnet 2026-10-28: short, 17 sells between 08:46 and 12:14 UTC, 8,280 USD average 81,414.42, closed 12:03-12:14Z,
net +0.00041079 BTC (READ.md:174). Context: day high 81,800 from the 08:30Z spike (READ.md:175). Reading (OURS): shorts scaled in above a
failed break of a high before the US open, no stop, exit by limit at lower levels. The net figure is testnet, one day, selected after the fact;
it is not evidence of an edge.

## 2. Rule (SHORT only; the LONG mirror is out of scope, DECISION (OURS): the operator's build is short only)
Data: Binance USD-M BTCUSDT 1m klines (`F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv`, fields open_time, open, high, low, close, volume; UTC). Research tape only, no fill claim.
All features use bars closed at or before t. Entry fills at open[t+1].

| Item | Definition | Label |
|---|---|---|
| Pre-US window W | 07:00-13:00 UTC every day, fixed in UTC (no DST table: the US cash open is 13:30 or 14:30 UTC, so 13:00 is before it all year). Trade day = UTC day. Signals only with t+1 inside W. | OURS (shots span 08:46-12:14Z, SOURCED READ.md:174; the window pads them) |
| ATR | ATR14 on 1h bars (Wilder, true range), last CLOSED hour before t. Needs 14 prior hourly bars, else no signal. | OURS |
| Resistance levels S_up (the break targets) | (a) prior UTC day high PDH; (b) early-session high ASH = max(high) of 00:00..t UTC of the current day, valid only if set at least 60 bars before t; (c) the highest 1h swing high (high above both neighbours, usable only 2 hours after it formed) of the last 5 UTC days. A level is used only if it is at least 0.5 ATR above the day's 00:00 open. | OURS (operator named S/R levels, gave no numbers) |
| Support levels S_dn (exit targets) | prior UTC day low PDL; session low SL = min(low) of 00:00..t; lowest 1h swing low (mirror of (c)) of the last 5 UTC days. | OURS |
| Break | A bar in W has high > L + 0.10 ATR for L in S_up. Excursion E = max(high) after the first crossing, in ATR above L. | OURS |
| Failure | Within 3 bars after the break bar (inclusive) a bar CLOSES back below L. That bar is t (signal bar). If E exceeds 1.5 ATR first, the level is dead for the day. | OURS |
| Signal limits | One signal per level per day; at most 3 signals per day; one position per day (a later signal while a position is open adds nothing). | OURS |

## 3. Position build (fixed capital scale-in, no stop)
- Capital K = 1.0 unit of notional per day (returns in % of K and bps). No leverage. DECISION (OURS): unit notional so days are comparable; the operator's 8,280 USD is not copied.
- 4 equal tranches of 0.25 K. Tranche 1 fills at open[t+1] (taker). Tranche j (j = 2..4) is a resting sell limit at entry_1 + (j-1) x 0.5 ATR (average-up), filled only when a later bar's high trades THROUGH the price by at least one tick (0.1 USDT) (maker rule of the template, trap 11). Unfilled limits are cancelled at 13:00 UTC. OURS.
- No stop. Risk is not capped by the rule, only by the window end (section 4), and is REPORTED, never hidden: per-day maximum adverse excursion (MAE, % of K) and the forced-flat loss.

## 4. Exits (S/R limits, no stop)
- Target T1 = the nearest S_dn level at least 1.0 ATR below entry_1: a buy limit for the whole open size, filled on trade-through of one tick. If none exists, target = entry_1 - 1.5 ATR. OURS.
- Time cap (labelled as such, not a stop): any open size is closed at the open of the 13:00 UTC bar (market, taker, 2 bps slippage). Count of such days and their summed return are printed. OURS (a window must end; the operator closed by 12:14Z, SOURCED READ.md:174).

## 5. Costs (declared before any outcome)
| Item | Value | Label |
|---|---|---|
| Taker fee per side | 0.0005 | SOURCED `backtest/fees.py:27` |
| Maker fee per side | 0.0002 (Binance research tape); Deribit maker 0.0, for the later execution check only | SOURCED `backtest/fees.py:28`, `:23-24` |
| Slippage | 2 bps per taker leg; 0 on a maker leg counted filled by trade-through only | OURS (repo convention, template section 1) |
| Round-trip cost, booked per episode | tranche 1 taker in (5+2), later tranches and target exit maker (2 each), time-cap exit taker (5+2); all booked per filled tranche | derived |
| Round-trip cost C for the gate | 14 bps all-taker upper bound (template) | OURS |
| Funding | settlement at 08:00 UTC lies inside W: a position held across 08:00 UTC adds the realised rate (short receives a positive rate) from `raw_fund` if present, else a flat 1 bp cost and the line `funding NOT_IN_DATA` | OURS |

## 6. Data split (fixed; DEV only)
- DEV: bars 2022-01-01 .. 2024-06-30 (project standard split, template section 6). The first 5 days are ineligible (swing-level lookback).
- VALIDATION 2024-07-01..2025-06-30: read once, later, by a separate card, only after PASS, this file unchanged. HOLDOUT 2025-07-01..2026-09-30: sealed.
- The loader refuses any bar with open >= 2024-07-01. Contamination to record: the 2026-10-28 day was seen by the author; it is outside DEV and excluded.

## 7. Pass / fail (fixed now; DEV; primary measure = net return per episode after booked costs)
Episode = a day with an entered position (one per day, so day-clustering equals plain). Statistic: mean net, SE over episodes, t = mean / SE.
Also printed: win rate, mean winner, mean loser, MAE distribution, count and sum of time-cap days, max drawdown of the cumulative net (in % of K) vs buy-and-hold BTC max drawdown over DEV (exceeding it is FAIL).
- N_min = 250 episodes on DEV (the gate in section 10). Fewer is INCONCLUSIVE, never NEGATIVE; n is printed and committed BEFORE any outcome column is read.
- **PASS** iff n >= 250 and mean net > 0 and t >= 2.0 and the summed loss of time-cap days is smaller than the summed gain of target-hit days (a no-stop rule that wins small and loses big must not pass on win rate) and MDD <= buy-and-hold MDD.
- **INCONCLUSIVE** iff n < 250. **FAIL** otherwise: stop, no layer or management work on this family (session-high failed-break short with scale-in).
- A PASS is a Binance-tape DEV finding only. Fill or profit claims need VALIDATION and a separate Deribit execution check.

## 8. Known traps
1. No stop: per-trade R is undefined; report % of K and bps, never R. 2. Look-ahead: swing highs are used only after the 2-hour confirmation; levels are fixed at bar close. 3. Maker fill on touch is not a fill (trade-through by a tick). 4. Overlap: one position per day. 5. Selection: the operator's day was chosen after the fact; no row from it. 6. A winning streak without a stop can hide a rare large loss: the time-cap row is the check. 7. Venue: Deribit testnet liquidity differs from the research tape.

## 9. Outputs of the executing session (card `backtest-pre-us-failed-break-dev-run`)
`screen.py`, `test_screen.py` (fixtures: failed-break day, gap-through-limit, no-fill-on-touch), `ledger.csv`, `RESULT.md` (verdict word first: PASS | INCONCLUSIVE | FAIL), `DATA_MANIFEST.csv`. The result commit comes after this file's commit. Forward-index hits (`x[i + 1]`) in the script need reviewed rows in `scripts/dev/lookahead_allowlist.tsv` in the same commit.

## 10. Gate outputs (run 2026-10-28 before the freeze)
Gate call parameters: n = 300 episodes (OURS estimate: about 30 % of the 912 DEV days; the real n is counted before the outcome run and the gate re-run), sd = 60 bps of K per episode (OURS estimate, unmeasured), cost 14 bps, new cells 3 (the primary rule plus two reported variants: window end 12:00, window end 13:00), unit bps, so `--max-gross 30` means 0.30 of a 100 bp unit (OURS mapping). The sd is unmeasured: if the measured sd exceeds about 66 bps the gate flips to BLOCK and the run card parks.
```
$ python scripts/dev/verdicts.py check "pre-US failed break short session high ATR"
check 'pre-US failed break short session high ATR': no prior row matches (need 5 of ['atr', 'break', 'faile', 'high', 'pre', 'sessi', 'short']). Safe to pre-register; append your row after RESULT.
exit 0
$ python scripts/dev/prereg_gate.py --n 300 --sd 60 --sd-source "OURS estimate" --cost 14 --m auto --new-cells 3 --max-gross 30
n 300 sd 60 m 68 z_holm 3.376 MDE 14.605 R + cost 14 = 28.605 vs max plausible gross 30; n needed 250
PASS: may freeze
exit 0
```
