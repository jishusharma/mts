# PRE-REGISTRATION: gross-effect screen, conditional location + flow vs plain location, BTCUSDT 1m (frozen 2026-10-15)

Session: Fable 5.1 pilot (JIS-NB worktree, claim `fable-pilot-pre-reg`), base origin/fast-track ffd9768d. Docs and one card only.
The commit that adds this file precedes the commit that adds any result; `git log` is the proof (same convention as
`research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:4`). Status: EXPLORATORY TRIAL. Nothing here adopts a rule.

Why: the three 2026-10-15 audits (`research/layer_lab/reports/2026-10-15_claude-side-audit.md:29-34`, `..._revalidate-strategy-audit-with-counterev.md:107`,
`..._strategy-direction-audit.md:64`) agree that no tested configuration has a net edge and that the next step is a gross-effect
screen with costs declared before any outcome is read. Operator decision 2026-10-15 (claude-side audit :60): the Binance tape is
the research target; a separate Deribit execution check gates any fill or profit claim. This screen makes no fill or profit claim.

Labels: SOURCED = file:line in this repo (a trader's words or a verified exchange number). OURS = our judgement or a default.
Every DECISION (OURS) below was taken because the repo had no answer; the most conservative reading was chosen.

## 0. Zero-judgement contract for the executing session (lane SONNET)
- Read sections 1-7 and run them as written. If a number is missing, the screen is BLOCKED with the missing item named; do not choose one.
- One run of the primary cell. No parameter is changed after the first outcome is read. Every cell that is computed is printed.
- Do not open bars dated 2024-07-01 or later for any outcome column (section 6). Do not read `RESULT.md` files of other studies for numbers.
- CI RED on STATUS.md at the time of writing was stale: the last three `gh run list --branch fast-track` runs (15:41Z-15:59Z) are success. DECISION (OURS): no CI fix in this session.

## 1. Economic target
| Item | Value | Label |
|---|---|---|
| Venue, instrument | Binance USD-M BTCUSDT perpetual, the tape on disk (`research/orderflow_views_2026-10-14/study.py:8-9`); research target only | SOURCED (operator decision, claude-side audit :60) |
| Execution venue for any later claim | Deribit BTC-PERPETUAL testnet, separate check, not part of this screen | SOURCED (same) |
| Bars | 1m klines, fields open_time, open, high, low, close, volume, taker_buy_volume; UTC | SOURCED (study.py:8, :69-70) |
| Size | 1,000 USDT notional per entry, one open position per side at a time, 1x (no leverage) | DECISION (OURS): the repo names no research size (GO_LIVE_BAR.md counts trades, not notional). Smallest round clip; participation reported (section 3.5) |
| Fee tier, taker | 0.0005 per side (5 bps), Binance USDT-M default tier | SOURCED (`backtest/fees.py:27`, via T055b L22-23) |
| Fee tier, maker | 0.0002 per side (2 bps) | SOURCED (`backtest/fees.py:28`) |
| Deribit fees (for the later execution check only) | taker 0.0005, maker 0.0 | SOURCED (`backtest/fees.py:23-24`, API-verified 2026-09-26) |
| Slippage bound | 2 bps per side on every taker leg; 0 on a maker leg that is counted filled only by trade-through | OURS, adopted from `PRE_REG_VOLUME_2026-10-09.md:28` (the repo's standing research convention) |
| Primary round-trip cost C | taker in, taker out: 5+5 fee + 2+2 slippage = **14 bps = 0.14 %** | derived from the rows above |
| Secondary cost readout C_m | maker in (2 bps, trade-through fill only), taker out (5 + 2): **9 bps = 0.09 %**; reported beside C, can never rescue a FAIL (`TOM_LAYER_V2_SPEC.md:331-332` rule) | derived |
| Funding | horizons up to 240 min can straddle a settlement (00/08/16 UTC). If `F:/MTS/Dumps/backtest/raw_fund/` has the fundingRate archive for the window, add the realised rate (long pays a positive rate) to the cost of straddling encounters; else add a flat 1 bp per straddling encounter and print `funding NOT_IN_DATA` | DECISION (OURS) |
| Turnover bound | ledger cooldown 60 min per side (section 5) => at most 24 encounters per side per UTC day; realised encounters per day are printed | DECISION (OURS) |
| Drawdown tolerance | max peak-to-trough drawdown of the cumulative net (cost C) return of the arm at the primary cell, in % of one clip, must not exceed the buy-and-hold BTC max drawdown over DEV computed from 1m closes. Exceeding it is FAIL whatever the mean says | DECISION (OURS): a relative bound derived from the data, not an invented operator risk number (revalidate audit :101 "do not invent operator risk numbers") |
| Calendar-time benchmarks | (a) cash = 0; (b) buy-and-hold BTC over DEV scaled by the arm's time in market f = n x h / minutes in DEV. Both printed next to the arm's total net; report only, not a pass criterion (the arm is two-sided, the benchmark one-sided) | DECISION (OURS) |

## 2. Candidates (exact rules on data already on disk)
Data: `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv` (archive 2022-01..2026-09-26, 89 files on JIS-NB, loader `study.py:87-109`).
delta_i = 2 x taker_buy_volume_i - volume_i (`FORMULAS.md` section 14, as `bt_data.cvd_delta`, study.py:8). No OI: the metrics
archive starts 2025-09-01 (study.py:10), after DEV; an OI arm would repeat the untestable-arm error (revalidate audit N1).

Session anchor: the UTC day, first bar s = 00:00 UTC. DECISION (OURS): `TOM_ON_BTC.md:107-109` lists 00:00 UTC, the US cash
open, London and the CME week open as candidates and says the choice is OURS to test. 00:00 UTC is the only one with no
DST shift (`MARKET_ANALYSIS_2026-10-05.md:80`, the 13:30/14:30 trap) and needs no extra table. One anchor only in this screen.

**Location rule L** (evaluated at the close of 1m bar t; SHORT form, LONG is the mirror with high<->low, max<->min):
- L1. t - s >= 60 (at least 60 closed bars into the session).
- L2. H(t) = max(high[s..t]) and the bar that set it is one of t-2, t-1, t (new session high within the last 3 bars; study.py:15 condition b, no hindsight pivot).
- L3. Up-leg: the bar of min(low[s..t]) comes before the bar of H(t).
- L4. Oversized: leg(t) = (H(t) - min(low[s..t])) / open[s] >= the 80th percentile of {leg_k(m)} over the previous 20 UTC days k, where m is t's minute of day and leg_k(m) is the same quantity on day k at minute m (days with a missing bar at m are skipped; fewer than 15 reference days => L4 is false). DECISION (OURS): top quintile; `TOM_LAYER_V2_SPEC` A-C1 "rank vs prior sessions" gives no number.
- LONG mirror: new session low within the last 3 bars, down-leg (the high came first), same leg size test.
Trade direction = fade (SHORT at the session high, LONG at the session low). sgn = -1 for SHORT, +1 for LONG.

**Flow flag F** (closed bars only): D5(t) = sum of delta over bars t-4..t. SHORT: F true iff D5(t) < 0 (sellers net aggressive
into the new high = Tom's "selling surplus in delta", `TOM_ON_BTC.md:65`, A-P6). LONG: F true iff D5(t) > 0. D5 = 0 => F false.
DECISION (OURS): a 5-bar window and a zero threshold; the spec gives no number. The window length is the only arbitrary choice and it is not varied.

**Test arm T** = eligible encounters (section 5) with F true. **Complement notF** = eligible encounters with F false.
**Control C (plain price/context rule)** = all eligible encounters (location alone, no flow). C uses the same screen, costs and
cells as T. There is no other control.

## 3. Effect measure: the decay curve
- 3.1 Decision time = close of bar t (open_time + 60 s). Features use bars <= t only. No label is taken at a bar open (revalidate audit N3).
- 3.2 Arrival latency: stated as one full bar. The Binance 1m kline is final only at its close and the live loop polls it; DECISION (OURS): 60 s is the conservative round number. Executable delay d = 1 bar.
- 3.3 Fill reference after delay d bars: p_in = open[t+1+d]. Exit reference after horizon h bars: p_out = open[t+1+d+h]. Gross effect G(d,h) = sgn x (p_out / p_in - 1) x 100, in % of notional, no fee, no slippage, no funding.
- 3.4 Grid, fixed: d in {0, 1, 2, 5, 15} bars; h in {5, 15, 30, 60, 120, 240} bars. d = 0 is the no-latency upper bound and is never tradeable; it is printed only to show the decay. Primary cell: **d = 1, h = 60**. DECISION (OURS): 60 min matches the only prior pre-registered horizon on this tape (study.py:25).
- 3.5 Participation: median 1m quote_volume over DEV is printed with the clip's share of it; a share above 1 % marks the arm `size-limited` (report only).
- 3.6 An encounter whose window [s-20 days .. t+1+15+240] has any missing bar in the bars it actually uses is dropped and counted in a `dropped_missing_bars` line.
- 3.7 Net at a cell = G - C (all-taker) and G - C_m (maker readout), funding per section 1. Printed for every cell; only the primary cell decides.

## 4. Pass/fail rule (fixed now; DEV only; primary cell d = 1, h = 60; cost C = 0.14 %)
Statistics: mean G per arm; SE cluster-robust by UTC day (Var(mean) = sum over days of S_day^2 / n^2, S_day = sum over the day's
encounters of (G_i - mean)); t_cost = (mean - C) / SE. DIFF = mean_T - mean_notF with its SE from OLS of G on [1, F] with
day-clustered sandwich variance; t_DIFF = DIFF / SE_DIFF. Sides pooled after the sgn adjustment; per-side rows printed. MDE at 80 % power = 2.8 x SE printed before any outcome column is read (n and SE need no outcome: SE uses outcomes; so MDE is printed with the result, n before it).
- N_min = 200 encounters in the arm on DEV. DECISION (OURS). n_T and n_C are printed and committed before the outcome run (step order in the card).
- **PASS_FLOW** iff n_T >= 200 and mean_T >= 0.14 % and t_cost_T >= 2.0 and DIFF >= +0.05 % and t_DIFF >= 2.0 and MDD_T <= MDD_BH.
- **PASS_CONTROL** iff not PASS_FLOW and n_C >= 200 and mean_C >= 0.14 % and t_cost_C >= 2.0 and MDD_C <= MDD_BH (the plain rule pays and flow adds nothing measurable: the next step is a validation read of C, no detector work).
- **INCONCLUSIVE** iff the arm under test has n < 200 (power), with MDE printed; never relabelled NEGATIVE.
- **FAIL** otherwise. FAIL means stop: no detector, chart, layer or management work on this hypothesis family (session-extreme fade with delta flow on 1m BTC). Krown Q66-Q69 and Tom T5 (`TOM_ON_BTC.md:136`) stay parked for it.
- The +0.05 % / t >= 2 incremental bar is the one already used on this tape (study.py:25). The t >= 2 on cost is OURS. Secondary cells and the maker readout carry no verdict.
- A PASS is a gross-effect finding on the Binance tape, nothing more. Fill or profit claims need the separate Deribit execution check (card written only after a PASS).

## 5. Eligible-event ledger (shared by T, notF and C) and the exposure row (G6)
- 5.1 Ledger = every bar t in DEV where L holds (either side), then cooldown: an encounter is eligible only if no eligible encounter on the same side exists in bars t-60..t-1. The cooldown is applied once, to the ledger, before the F partition (fixes the per-arm cooldown of study.py:224-237, revalidate audit R1). Estimand: conditional gross return for flow vs non-flow encounters on identical eligibility (DIFF), plus the unconditional encounter return (C).
- 5.2 Ledger file `research/gross_effect_screen_2026-10-15/ledger.csv`: t_open_time, side, F, D5, leg, p_in per d, G per (d,h), dropped flag. Overlap counts (T, notF, C) and encounters per day are printed.
- 5.3 Exposure row (G6): `research/TRIAL_LEDGER.csv` does not exist yet (card gap-g6-trial-ledger is parked). This study writes `research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv` with columns study, run_utc, data_source, window_read, split, rule_sha256 (of this file at the run commit), verdict, decision_informed. The first run appends three rows: (i) this screen on DEV; (ii) prior known exposure: `orderflow_views_2026-10-14/study.py` read DEV 2022-2024, VAL 2025, HOLDOUT 2026 and published all three (RESULT.md:37-42); (iii) `tom_btc_2026-10-13/chart_lab.py` drew 80 charts (window per `charts/index.csv`, not read here). The G6 builder merges this file later.

## 6. Data split (fixed; DEV only in this screen)
- DEV: bar open 2022-01-01 .. 2024-06-30 (the project's standard split, `PRE_REG_VOLUME_2026-10-09.md:23`; the 1m archive starts 2022-01). The L4 reference window makes the first 20 days of 2022 ineligible.
- VALIDATION: 2024-07-01 .. 2025-06-30, read once, later, by a separate card, only after PASS_FLOW or PASS_CONTROL, with this file unchanged.
- HOLDOUT: 2025-07-01 .. 2026-09-30, sealed; opening it needs the operator (A7, `TOM_ON_BTC.md:124`, still open per claude-side audit :60).
- DECISION (OURS): the standard split, not the TOM_ON_BTC footprint DEV (2024-12..2025-03, `TOM_ON_BTC.md:121`), because this screen uses klines only and the footprint DEV lies inside the standard VALIDATION window. Known contamination: study.py already published numbers on 2024-07..2024-12 (inside VALIDATION) and 2026 (HOLDOUT) for a different rule; recorded in 5.3, not undone.
- Loader guard: the script refuses any bar with open >= 2024-07-01 unless called with `--split validation` by the later card; no such flag exists in this screen.

## 7. Known traps (each one is a check in the script or the test)
1. Gap-stop booking: `orderflow_views_2026-10-14/study.py:195-210` books a stop at the stop price without checking the bar open (claude-side audit :11, revalidate N2). This screen has no stops. If a stop simulation is ever added, fill = min(open, stop) for longs, max(open, stop) for shorts (`backtest/tom_bt.py:203-204`).
2. Bar-open labels: features at close of t, fills at open[t+1+d]; `chart_lab.py:138` minute-open labels are not reused (revalidate N3).
3. Per-arm cooldown and subset-vs-all: cooldown on the shared ledger, DIFF against the complement (revalidate R1 witness 1.0 vs 2.0).
4. OI in DEV: NOT_IN_DATA (metrics from 2025-09); no OI arm (N1).
5. CVD level depends on the series start (`RESULT.md:18-19`): only windowed sums (D5) are used, never a CVD level.
6. Overlapping outcomes: day-clustered SE; no i.i.d. t.
7. DST anchor (`MARKET_ANALYSIS_2026-10-05.md:80`): 00:00 UTC anchor; no 13:30/14:30 table.
8. Archive revisions: SHA256 of every input file in `DATA_MANIFEST.csv`; bar count and gap list per month printed; the archive ends 2026-09-26 and no top-up is needed for DEV.
9. Delta sign: taker_buy_volume is buyer-taker volume; buyer-maker trades are sells (strategy-direction audit :51); delta = 2 x tbv - v, tested on a fixture.
10. Power: n before outcomes; INCONCLUSIVE is a separate verdict from FAIL (N1 lesson).
11. Maker fill on touch is not a fill: maker readout counts an entry only when a later bar trades through open[t+1+d] by at least one tick (0.1 USDT) in the entry's favour (`TOM_LAYER_V2_SPEC.md:331`).
12. Venue: a PASS here says nothing about Deribit fills (Deribit testnet liquidity differs from production, revalidate R5).

## 8. Outputs of the executing session
`screen.py`, `test_screen.py`, `DATA_MANIFEST.csv`, `ledger.csv`, `decay.csv` (arm x d x h: n, mean G, SE, net C, net C_m), `EXPOSURE_LEDGER.csv`,
`RESULT.md` (verdict line first, then the primary-cell table, decay table, per-side rows, drawdown vs buy-and-hold, benchmarks, participation,
dropped counts, funding availability). Verdict words: PASS_FLOW | PASS_CONTROL | INCONCLUSIVE | FAIL. The result commit must come after this file's commit.

## 9. Pilot bookkeeping (this session)
Budget and other sessions: `PILOT_USAGE.md` in this folder. Operator instruction for this pilot: zero operator input, conservative defaults, written as DECISION (OURS) above.
