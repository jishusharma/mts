# PRE-REGISTRATION: failed auction at the prior-day value-area edge (FAB-4 / TOM-12 family), BTCUSDT 5m closes, DEV (frozen 2026-10-16)

Session: Fable 5.1 (JIS-NB worktree, claim `pit-levels`), base origin/fast-track 6dfa51eb. Docs, one count script, one card.
The commit that adds this file precedes any result commit; `git log` is the proof (convention of
`gross_effect_screen_2026-10-15/PRE_REG.md:4`). Status: EXPLORATORY TRIAL. Nothing here adopts a rule.

Why this family: it is the one catalogue row whose level (prior-day VAH/VAL) comes from a builder that passed the
point-in-time proof (REPORT.md section 3, family F3 prior_day), whose stop is derivable from the trader's words
(the probe extreme) and whose feasible subset has the most DEV events of the rows that clear the cost floor
(REPORT.md section 5: n = 1,835 at stop >= 0.40 %). Labels: SOURCED = file:line or quote; OURS = our judgement.

## 0. Zero-judgement contract for the executing session (lane SONNET, card `pit-prior-va-failed-auction-dev`)
- Read sections 1-8 and run them as written. A missing number = BLOCKED with the item named; choose nothing.
- Step order: (1) run `count_prior_va.py` and commit its output as `COUNT.txt` (no outcome column); (2) check the freeze
  gate in section 4 against that output; (3) only then compute outcomes (one run of the primary cell); (4) write RESULT.md.
- No bar with open >= 2024-07-01 is read for any column (loader guard in count_prior_va.py:91). No RESULT.md of another study is read for numbers.
- Levels and phases come only from the PIT_CONTRACT.md builders (D-LEVELS via `vp_pivot_probe.build_profile`, D-SESSION 00:00 UTC). No other level, no VWAP, no pivot in this screen.

## 1. Economic target (unchanged from `gross_effect_screen_2026-10-15/PRE_REG.md` section 1 unless stated)
| Item | Value | Label |
|---|---|---|
| Venue, bars | Binance USDT-M BTCUSDT, 1m klines on disk (`F:/MTS/data/tom_raw/klines`), resampled to 5m by UTC epoch buckets (FORMULAS 8); research target only | SOURCED (operator decision, claude-side audit :60) |
| Fees | taker 0.0005, maker 0.0002 per side (`backtest/fees.py:27-28`) | SOURCED |
| Slippage | 2 bps per taker leg; 0 on a maker leg filled only by trade-through | OURS (`PRE_REG_VOLUME_2026-10-09.md:28` convention) |
| Primary cost C | taker in, taker out = 0.14 % of price per round trip | derived |
| Secondary C_m | maker in (limit at the failed-auction close, trade-through fill only), taker out = 0.09 %; reported, never rescues a FAIL | derived |
| Cost in R | C / stop_pct per trade; at the feasible subset's median stop (0.781 %, count-only) = 0.18 R taker, 0.12 R maker-in | derived from the count |
| Size, funding, turnover, drawdown bound, benchmarks | as `gross_effect_screen_2026-10-15/PRE_REG.md` section 1 | OURS (same decisions) |

## 2. Candidates (exact rules)
Level builder: prior UTC day's POC / VAH / VAL from that day's 1m bars, FORMULAS 18.1, w = 10 USD, via
`MyTradingSys/backtest/vp_pivot_probe.py:101-112` (leakage PASS, REPORT.md section 3). A prior day with > 5 missing minutes
gives no levels; a day with > 1 missing 5m bar is skipped (OURS). Levels are static for the whole UTC day (D-SESSION).

**Test arm T (SHORT written; LONG is the mirror with VAL, lows, "below"):** on the day's 5m closes (k = 0..287),
- T1. a 5m close above VAH starts an excursion; the excursion's extreme E = the highest 5m high from that bar on;
- T2. the first later 5m close below VAH in the same UTC day is the trigger t (Fabio: "a clear failed auction",
  9IliXww64uM captions; Tom: "price returns into the old balance after outside prices fail to hold", SETUP_CATALOG.md:888);
- T3. entry = close[t]; stop = E (the probe extreme: Fabio "Stop was likely somewhere above here"; OURS as a level);
  target = VAL (Fabio: "all the way to the other side of the range"); stop_pct = (E - entry) / entry;
- T4. feasibility filter, applied before any outcome: stop_pct >= 0.40 % (D-STOPFLOOR, `TOM_ON_BTC.md:24`). Events below
  the floor are counted and reported, never traded;
- T5. one open trade per side at a time; a trigger while a same-side trade is open is skipped and counted;
- T6. time stop: the last 5m close of the UTC day (Fabio is flat by the close; OURS on BTC).
No open-inside-value condition in the primary cell (DECISION (OURS): the count gives n = 1,017 with it, 1,835 without; the
split is printed as a secondary row, not a cell).

**Control arm C (location only):** the first 5m bar of the UTC day whose high >= VAH (touch), entry = that bar's close,
stop = entry x (1 + 0.40 %) (the floor, OURS), target = VAL, same T5/T6. C asks whether the level alone is paid.

## 3. Effect measure
- 3.1 Decision time = close of 5m bar t. Fill reference: open of bar t+1 (one-bar latency, DECISION (OURS) as before).
- 3.2 Outcome in R: stop and target tested per 5m bar, stop first when a bar holds both; a bar that opens beyond the stop
  fills at the open (`tom_bt.py:203-204` rule). Timeout at T6 exits at that close. gross_R = sgn x (exit - entry) / (stop - entry);
  net_R = gross_R - C / stop_pct (taker) and - C_m / stop_pct (maker readout).
- 3.3 Printed per arm and side: n, hit %, stop %, timeout %, mean gross_R, mean net_R, day-clustered SE (FORMULAS 18.7
  day-block bootstrap, 2000 resamples, seed 20261016), MDD vs buy-and-hold, participation, dropped counts.
- 3.4 Secondary rows (no verdict): open-inside-value split; stop_pct terciles of the feasible subset; maker readout.

## 4. Count-first freeze gate and pass/fail (fixed now; DEV only)
Count-only pass (count_prior_va.py, run 2026-10-16 on JIS-NB, no outcome column):
| arm | n | days | stop % median | geometric R:R median |
|---|---|---|---|---|
| T all | 4,905 | 752 | 0.278 | 4.59 |
| T feasible (stop >= 0.40 %) | **1,835** | 662 | 0.781 | 1.94 |
| C touch | 1,254 | 886 | 0.40 (floor) | n/a |
- Plausible gross effect: +0.75 R per trade = Tom's SOURCED intraday swing metrics (35 % win at 4 R, hQ8sOq67x5o,
  CATALOGUE_AUDIT.md section 3.2 T-3), taken as the family's upper plausible bound on BTC (OURS transfer).
- MDE at 80 % power from the count, two-point payoff at the setup's median R:R 1.94 and the win rate implied by +0.75 R
  (p = 0.596): sd = 1.44 R, MDE = 2.8 x sd / sqrt(1835) = **0.094 R**; cost 0.179 R; MDE + cost = 0.273 R < 0.75 R.
  `power_mde.power_mde(0.596, 1.94, 0.179, 1835)` gives mde_net_r 0.094, trades for 80 % power 50.
- **Freeze rule:** this file is frozen because MDE + C <= plausible gross. The executing session re-runs the count; if its
  n_T differs from 1,835 by more than 1 % or MDE + C > 0.75 R, the screen is BLOCKED and this file is not edited.
- **PASS_T** iff n_T >= 200 and mean net_R_T (taker) > 0 and t = mean_net / SE >= 2.0 and MDD_T <= MDD_BH.
- **PASS_C** iff not PASS_T and n_C >= 200 and mean net_R_C > 0 and t >= 2.0 and MDD_C <= MDD_BH (the level alone pays).
- **INCONCLUSIVE** iff the arm has n < 200 (cannot happen on the count; kept for the executing session's re-count).
- **FAIL** otherwise. One verdict per arm, printed as `T: <verdict>`, `C: <verdict>`.
- Kill scope on FAIL_T: the failed-auction-at-prior-day-value family on BTC 5m with the probe-extreme stop (FAB-4, TOM-12
  as encoded here). It says nothing about other stops, timeframes, Krown, Malkan or Tom's other rows.
- Multiple testing: this is trial 1 of this family in the trial ledger (`EXPOSURE_LEDGER.csv`, section 5); the t >= 2.0 bar
  is Holm-adjusted when the ledger holds k > 1 variants of this family (threshold z for alpha / k).

## 5. Ledger and exposure
- `ledger.csv`: d, side, k, entry, stop, stop_pct, target, feasible, open_inside, skipped_open_trade, then (after step 3) exit, kind, gross_R, net_R.
- `EXPOSURE_LEDGER.csv` row: study pit_levels_2026-10-16, run_utc, data_source, window DEV, split DEV, rule_sha256 of this
  file at the run commit, verdict per arm, decision_informed. Prior exposure of this family: none on BTC in the repo
  (vp_pivots_2026-10-09 touched prior_day levels with +-1R barriers, a different rule and horizon; recorded as prior context).

## 6. Data split
DEV: bar open 2022-01-01 .. 2024-06-30 (912 days). VALIDATION 2024-07-01 .. 2025-06-30, read once, later, by a separate card,
only after PASS_T or PASS_C with this file unchanged. HOLDOUT sealed (operator). Loader guard: count_prior_va.py:91 refuses later bars.

## 7. Known traps (each a check in the script)
1. Level availability: prior-day profile only (static_levels, PASS); never the developing profile at the touch bar.
2. Bucket alignment: 5m buckets by UTC epoch, strict (a 5m bar with any missing minute is NaN and skipped).
3. Stop first on a bar that holds both; gap through the stop fills at the open.
4. One open trade per side; skipped triggers counted.
5. No outcome column before the count is committed (step order in section 0).
6. Day-clustered SE; no i.i.d. t.
7. Venue: a PASS here is a Binance-tape finding; Deribit fills need the separate execution check.
8. The stop floor filter is a count-time filter, declared here; it is not varied.

## 8. Outputs
`COUNT.txt`, `ledger.csv`, `EXPOSURE_LEDGER.csv`, `RESULT.md` (verdict lines first: `T: ...`, `C: ...`; then the tables of 3.3 and 3.4).
