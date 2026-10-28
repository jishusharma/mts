# R6 PRE-REGISTRATION: Krown S8 squeeze break on 4h, BTC+ETH+SOL pooled, DEV stage 2020-01..2024-06 (Fable 5.1, 2026-10-28)

**Verdict of the counts screen: ONE family is POWERED. Krown S8 (BBWP squeeze then break) on 4h bars, pooled over BTCUSDT, ETHUSDT and SOLUSDT with DEV_EXT (2020-2021) and DEV (2022-01..2024-06), has 807 events on 539 distinct UTC days against 439 days needed (m = 65, z_holm 3.364, cost 0.025 R). Nothing else comes close: Krown S5 229 of 435, pitchfork 1d 476 of 763 (its 1.5 % stop makes cost 0.093 R), Malkan RSI 40/60 1d 20 of 451, 1w 5 of 396. On DEV alone (2022-24H1) even S8 is not powered (274 of 444 days): the test exists only because the operator-approved DEV_EXT (D3-dev-ext) and two more symbols are pooled.**

No outcome column was read; no bar at or after 2024-07-01 00:00Z was loaded (`counts_only.py` drops them at load and asserts on every frame, then again before computation). No backtest ran. Labels: SOURCED = file:line; OURS = this session's choice. Question answered as asked; R1's verdict table is not re-argued.

## 1. Counts (`counts_only.py --m-base 56`; `COUNTS.csv` = 45 rows: 30 cells + 15 pooled, rendered row for row in `COUNTS.md`; the table below condenses them)

Data: public Binance USD-M futures monthly kline zips (data.binance.vision), 4h and 1d, cached outside the repo at `F:/MTS/data/fable_run6_klines/`; 1w resampled from 1d (Monday 00:00 UTC). The archive starts 2020-01 (2019-09..12 NOT_IN_DATA: no warm-up before DEV_EXT, so January 2020 4h signals and the first 34 weeks of 1w are structurally missing); SOLUSDT lists 2020-09-14 (partial DEV_EXT, 12 months NOT_IN_DATA). The repo's own 1m DEV_EXT files (`F:/MTS/data/dev_ext_2019_2021`) are missing on this machine (B187 item 4): the fetched 4h/1d klines are real data for the same venue and window, not an estimate. Event rules = the repo's layer code unchanged (docstring of `counts_only.py`). Stop per event: Krown far side of the last 10 bars (`sim_desk/studies/krown.py` STOP_BARS, OURS); Malkan the signal candle (trader, `studies/rsi.py`); pitchfork 1.5 % (`run_pitchfork_event_study.py:238`, OURS there).

| family | tf | window | BTC ev/days | ETH ev/days | SOL ev/days | pooled days | mean stop % | cost R | n_needed days | POWERED |
|---|---|---|---|---|---|---|---|---|---|---|
| Krown S5 | 4h | DEV | 55/55 | 51/50 | 58/55 | 129 | 7.20 | 0.029 | 443 | no |
| Krown S5 | 4h | DEV_EXT | 46/46 | 41/41 | 26/26 p | 100 | 9.35 | 0.022 | 424 | no |
| Krown S5 | 4h | DEV+DEV_EXT | | | | 229 | 8.08 | 0.026 | 435 | no |
| **Krown S8** | 4h | DEV | 135/135 | 142/141 | 156/156 | 274 | 6.48 | 0.029 | 444 | no |
| **Krown S8** | 4h | DEV_EXT | 142/142 | 146/144 | 86/85 p | 265 | 8.63 | 0.021 | 419 | no |
| **Krown S8** | 4h | **DEV+DEV_EXT** | | | | **539** | 7.48 | 0.025 | 432 (m 58) / **439 (m 65)** | **YES** |
| Malkan RSI 40/60 | 1d | DEV+DEV_EXT | 6/6 | 6/6 | 8/8 p | 20 | 6.90 | 0.031 | 451 | no |
| Malkan RSI 40/60 | 1w | DEV+DEV_EXT | 3/3 | 1/1 | 1/1 p | 5 | 12.8 | 0.013 | 396 | no |
| pitchfork triplet | 1d | DEV+DEV_EXT | 242/242 | 255/255 | 202/202 p | 476 | 1.50 | 0.093 | 763 | no |

p = partial (SOL from 2020-09-14). Formulas: cost_R = mean over events of 14 bp / stop_i (C = 14 bp, SOURCED `gross_effect_screen_2026-10-15/PRE_REG.md:28-32` via R1 sec. 3); n_needed = ((z_holm(m) + 0.84) x sd / (0.30 - cost_R))^2 with sd 1.37 R (R1 sec. 3, `R1_EDGE_OR_STOP.md:60`, OURS there from the Krown S5 CI), plausible 0.30 R and 0.84 = `prereg_gate.py` constants (OURS); m = `verdicts.py count --split DEV` = 56 (run 2026-10-28, 19 studies) + new cells per family (Krown 2 for the screen, 9 for the frozen pre-reg; Malkan 2; pitchfork 1); units = distinct UTC days across symbols (one cluster per day, R1 E1). Cross-check: BTC S5 4h DEV counts 55 signal bars here vs 35 filled trades in the desk row (`TRIALS.md:280`), which starts 2022-04-01, holds one position at a time and runs on 1m fills; the difference is the busy rule and window, not the detector (OURS reading, no outcome read).

Gates (`verdicts.py check`, 2026-10-28): "Krown S5 S8 4h" exit 0 (5 rows match the word krown only inside other families' kill scopes: context composite, gross screen, opr_bb; none is a Krown row); "Malkan RSI 40/60" exit 0, no prior row; "pitchfork" exit 0, no prior row (the 2020-2026 pitchfork event study `PHASE1_EVENT_STUDY.md` read sealed bars and carries no RESULT.md row; it is not the test proposed here and is not freezable: its cost 0.093 R blocks it anyway).

`prereg_gate.py --sd 1.37 --sd-source R1_EDGE_OR_STOP.md:71 --m auto`:

| cell | args | output | exit |
|---|---|---|---|
| Krown S8 pooled DEV+DEV_EXT, 9 frozen cells | `--n 539 --cost 0.0250 --new-cells 9` | m 65 z_holm 3.364 MDE 0.248 + 0.025 = 0.273 <= 0.30; n needed 439 | **0 PASS: may freeze** |
| Krown S8 pooled, screen m | `--n 539 --cost 0.0250 --new-cells 2` | m 58 z 3.332 MDE 0.246 + 0.025 = 0.271; n needed 432 | 0 PASS |
| Krown S8 DEV only | `--n 274 --cost 0.0287 --new-cells 2` | MDE 0.345 + 0.029 = 0.374 > 0.30; n needed 444 | 1 BLOCK |
| Krown S5 pooled | `--n 229 --cost 0.0260 --new-cells 2` | MDE 0.378 + 0.026 = 0.404; n needed 435 | 1 BLOCK |
| Malkan 1d / 1w pooled | `--n 20` / `--n 5` | MDE 1.278 / 2.556 R | 1 BLOCK |
| pitchfork 1d pooled | `--n 476 --cost 0.0933 --new-cells 1` | MDE 0.262 + 0.093 = 0.355; n needed 763 | 1 BLOCK |

Stop floor check (OURS, 4 x 14 bp = 0.56 %): 0 of 807 S8 events have a stop under 0.56 % (minimum 0.85 % BTC, 1.19 % ETH, 3.04 % SOL; medians 4.9 / 6.3 / 9.9 %), so the fee-stop rule (`FABLE_FEE_STOP_RULE.md`) removes nothing.

## 2. Frozen pre-registration: E2, Krown S8 4h pooled (one run; nothing below changes after the first outcome)

**Hypothesis.** After a volatility squeeze (BBWP <= 30 within the last 5 bars) the first 4h close above the 50th BBWP percentile that also closes beyond the prior 10-bar range continues far enough, before the far side of those 10 bars is hit, to earn more than fees (KR-Q02/KR-Q05, `krown_ta101_2026-10-13/KROWN_RULES.csv`; entry, stop, target OURS as in `sim_desk/studies/krown.py`).

### Items 0a-0f (pre-build gate)
- 0a Cost: stop = far side of the last 10 4h bars incl. the signal bar; floor 0.56 % (4 x 14 bp, OURS; `FABLE_FEE_STOP_RULE.md` floors 0.40 % taker / 0.20 % maker are both below it). Events under the floor are skipped and counted; today 0 of 807. Median stops 4.9-9.9 %: fee share 0.015-0.03 R, under the 0.25 R cap.
- 0b Gross: not checked on outcomes (this run is counts-only by design; the 2x-cost check is the DEV run's own pass rule: mean gross R >= 4 x mean fee R).
- 0c Record: Krown has no dated BTC ledger; detector recall 3 of 12 (RECALL FAIL, `krown_ta101_2026-10-13/RECALL.md`): hypothesis, never a core; every result carries NO-RECALL-CLEARANCE (planner DECISION 2026-10-18, card krown-dev-event-study).
- 0d Data: OHLC 4h only; no volume, OI, funding or aggressor side needed. SOL DEV_EXT partial from 2020-09-14 (NOT_IN_DATA before), January 2020 no warm-up (NOT_IN_DATA, never 0).
- 0e Power: 539 UTC days available vs 439 needed at m = 65 (section 1); MDE 0.248 R + cost 0.025 R = 0.273 R <= 0.30 R plausible. Runs.
- 0f Kill: PASS_DEV fails with days >= 439 -> Krown S8 4h is DEAD on BTC/ETH/SOL, zero redesigns, and because it is the only powered family of R1 E1 the R1 section 5 STOP list applies to the whole BTC trading-edge program (new backtests on trader sources stop until new data exists). A VALIDATION fail after a DEV pass has the same effect.

### Items 1-12
1. **Source home:** Krown, BTC, 4h/daily charts, swing holds of days (KR-Q01..Q05, `KROWN_RULES.csv`; `KROWN_SETUP_CATALOG.md` S8). Evidence: `krown_ta101_2026-10-13/KROWN_RULES.csv` rows KR-Q01, KR-Q02, KR-Q05.
2. **Ground truth:** NOT_IN_DATA (no dated trade ledger; RECALL.md 3 of 12 examples verify). Hypothesis status stated in 0c.
3. **Recall / fire rate:** recall waived with the NO-RECALL-CLEARANCE label (0c). Fire rate: 807 signals on 539 days in 4.5 years across 3 symbols = 0.49 per calendar day pooled, 0.16 per symbol-day (`COUNTS.csv`). Not everywhere: 539 of 1,643 days.
4. **Data inputs:** open/high/low/close 4h; `counts_only.load` keeps only those five columns and asserts no outcome-like name. Volume-based Krown setups (S1, S2, S7, S9) are out of scope (desk SKIPPED note).
5. **Parity:** raw-bar check only: the E2 run must reproduce 807 events / 539 days within 1 % from the same cached klines before any outcome is computed (freeze bar, as `PRE_REG_V2.md` keeps `n_T within 1 %`); otherwise the run stops with BLOCKED.md.
6. **Cost per instrument:** taker 0.05 % per market leg + 0.02 % slippage on market and stop fills (SOURCED `backtest/fees.py:27-28`; slippage OURS `sim_desk/studies/_bars.py` SLIP_DEFAULT); maker 0.02 % on a target fill. Same three numbers for all symbols (Binance USD-M). Fee share of R at the median stop 0.015-0.03 R < 0.25 R.
7. **Fills:** market entry at the open of the bar after the signal bar (taker + slip). Stop: filled at the stop, or at the open when the bar opens beyond it. Target: limit at the target (maker), touch = fill. Same-bar stop and target: stop wins (conservative). Mismatch stated: fills on 4h OHLC, not 1m (1m is not on disk for SOL and 2020-21); a 4h-bar fill is the lower bound the desk's 1m fills would refine, never the other way.
8. **Exits:** target 2 x risk from the fill price (OURS; the desk measures from the signal close), stop (item 7), time stop at the close of the 100th bar after entry (taker). Trader's management (KR-X01, KR-Z14 give no exit): mismatch stated; a fixed bracket is a lower bound.
9. **Null like-for-like:** none needed for the verdict (one-sample t against zero net R; the cost model already removes the free-money null). Descriptive comparator, no verdict: the same bracket placed at the open of every 4h bar that is NOT a signal bar, same symbols and windows, reported as n and mean only.
10. **Power:** section 1; pass rule below uses the same m = 65 (z_holm 3.364) that set n_needed.
11. **Holdout:** DEV stage = 2020-01-01..2024-06-30 (DEV_EXT + DEV, D3-dev-ext allows DEV-stage reads). VALIDATION 2024-07-01..2025-06-30 read ONCE by a separate card after a DEV PASS and after the operator is told in one line; HOLDOUT 2025-07-01+ sealed. Trial count: this pre-reg adds 9 cells to the ledger (m = 65); the desk's S5 row and the three krown-dev-event-study cards are other hypotheses and stay in the ledger as they are.
12. **Stratified readout:** the 8 strata cells below (symbol, side, window = the two market regimes 2020-21 and 2022-24H1, BTC-on-DEV) next to the pooled number; session is not a stratum on 4h bars. A year table (2020..2024H1: n, mean net R, no t, no verdict) is descriptive.

### Frozen cells (9; Holm m = 56 + 9 = 65, z_holm = 3.364 two-sided)
| cell | definition | role |
|---|---|---|
| C0 | pooled BTC+ETH+SOL, both sides, 2020-01..2024-06 | **verdict cell** |
| C1-C3 | BTCUSDT / ETHUSDT / SOLUSDT | stratum |
| C4-C5 | long / short | stratum |
| C6-C7 | DEV_EXT 2020-01..2021-12 / DEV 2022-01..2024-06 | stratum (regime) |
| C8 | BTCUSDT x DEV 2022-01..2024-06 (comparable to the desk's BTC rows) | stratum |

Strata report n, days, mean gross R, mean fee R, mean net R, t; they carry no verdict word and can neither rescue nor kill C0.

### Statistic and pass rules
- Unit = UTC day of the entry fill; pooled across symbols (one cluster per day). mean net R over filled trades; SE by day-block bootstrap, 2,000 resamples, seed 20261028 (FORMULAS 18.7 as `PRE_REG_V2.md` item 1); t = mean / SE.
- One position at a time per symbol (desk busy rule); signals during a position are skipped and counted (539 is signal days; the busy rule can push entry days under 439, which is INCONCLUSIVE, never FAIL); a trade open at 2024-06-30 24:00Z is closed at that bar's close (taker) and reported.
- Freeze bar: events 807 +- 1 %, days 539 +- 1 %, else BLOCKED.md, no outcome.
- **PASS_DEV** iff entry days >= 439 AND mean net R > 0 AND t >= 3.364 AND mean gross R >= 4 x mean fee R. **INCONCLUSIVE** iff entry days < 439 (never FAIL). **FAIL** otherwise. FAIL means stop: no detector, chart, layer or management work on the Krown S8 squeeze-break family on 4h BTC, ETH or SOL with this 10-bar stop; and, this being the last powered family of R1 E1, the R1 section 5 STOP list applies to the BTC trading-edge program.
- **VALIDATION** (one read, separate card): same code, 2024-07-01..2025-06-30, PASS iff mean net R > 0 AND t >= 2.0 (same sign as DEV). HOLDOUT untouched.
- RESULT.md carries a `Verdict arms` table (arm | n | mean | se | verdict) and the exact kill sentence above so `verdicts.py backfill` parses it; the 9 cells go to `research/layer_lab/TRIALS.md` and `research/TRIAL_LEDGER.csv`.

## 3. Decisions (all OURS, conservative defaults; no operator question asked)
- DEV stage for the verdict = DEV_EXT + DEV pooled with three symbols, because that is the only configuration the power gate passes; the same pooling is frozen for VALIDATION.
- 4h-bar fills instead of 1m (data), target from the fill price, stop floor 0.56 %, 9 cells with one verdict cell, descriptive null, bootstrap seed 20261028.
- Pitchfork is BLOCKED on cost (its 1.5 % stop is the study's own number; a wider stop is a new hypothesis, not tried here). Malkan 1d/1w are BLOCKED on counts at any cost (20 and 5 days). Krown S5 is BLOCKED (229 of 435).
- Cards: E2 DEV run (SONNET), VALIDATION read (blocked until the operator says go), carry executability memo E3 (SONNET). The three `krown-dev-event-study*` cards test other Krown hypotheses (H-V1..H-T1 on BTC 2017+); they are not twins of E2 and are left as they are.
