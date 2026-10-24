# T10 Missing aspects: failure modes nobody here has checked, and the bridge playbook

Card dsa-audit-10-missing-aspects. Run by a Claude builder session on JIS-NB, 2026-10-24, from origin/fast-track b43de092f. No AIBridge was used. Windows: DEV only (before 2024-07-01). Nothing outside scripts/T10/ and this file was edited; no verdict, ledger or bar was changed.

## 1. Summary

1. Checked: 45 ways an intraday crypto-perpetual backtest can mislead, scored against all 16 studies of brief 1b and all 27 testnet layer keys (1935 cells), plus 5 small DEV demonstrations of the worst gaps.
2. Found: of 1935 cells, 89 are HANDLED, 540 NOT HANDLED, 531 N/A and 775 UNKNOWN. The largest holes are costs that do not scale with volatility, no second instrument (BTC only), no margin or liquidation model, no stability-by-period run, and arms that are not corrected for how many were tried.
3. It changes: no published verdict is shown to flip. Four fix cards are filed (all S2), and four wording changes for the DSA prompt are posted to Claude. The bridge playbook is partial: only T01 used the bridge, and T04-T07 and T09 have no report yet.

## 2. Scope

| Item | Window | Method | Result |
|---|---|---|---|
| Failure-mode list (section 3) | none | model knowledge plus 7 web sources, items mapped to brief section 2 and T01-T03, T08 | 45 modes |
| Matrix (section 4) | none | hand-written rules in scripts/T10/t10_build_matrix.py, evidence per cell, UNKNOWN when unverified | matrix.csv, matrix_summary.csv |
| Demonstrations D1-D5 (section 5) | DEV 2022-01-01..2024-06-30 1m BTCUSDT, 1,313,280 bars | own loader, seed 20261024 | scripts/T10/out/demos_run.txt |
| Bridge playbook (section 8) | none | read of the bridge logs of T01, T02, T03, T08 | scripts/T10/T10_BRIDGE_PLAYBOOK.md |

Not read: any VALIDATION or HOLDOUT return. No footprint data was read, so no exposure-ledger row is due. Reports T04, T05, T06, T07, T09 are not on origin/fast-track and are not waited for.

## 3. Failure modes (45)

Source column: a URL when the item comes from a published list found by web search; otherwise `model knowledge` (DeepSeek-style own knowledge, here the builder model). Covered-by names the brief section 2 item or the T-report that already covers it; NONE means no earlier audit covers it.

| ID | Class | Failure mode | How it shows | Test | Source | Covered by |
|---|---|---|---|---|---|---|
| F01 | data | Duplicate or missing bars | event counts and returns change after de-duplication | count unique open_time and gaps per loader | model knowledge | T01 |
| F02 | data | Time unit mix (microseconds read as milliseconds) | bars land in year 50000 or are dropped | assert stamp range per file | model knowledge | T01 |
| F03 | data | Trade-price bars used where mark/index price decides stops or liquidation | stop hit on a print the exchange would not use | rerun stop logic on mark bars | model knowledge | T03 (bt_engine mark bars), section 1e L5 |
| F04 | data | Spot data standing in for perp data | basis and funding ignored; session volume differs | compare spot vs perp close on overlap | model knowledge | T01 L10 |
| F05 | data | Single-instrument universe (BTC only): result may be an instrument accident | no cross-asset check; edge vanishes on ETH | rerun the frozen rule on ETHUSDT DEV | https://www.columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf | NONE |
| F06 | data | Point-in-time errors: OI, depth, funding or revised data used before it was published | signal uses a field stamped earlier than it was knowable | check publish lag of each derived column | https://arxiv.org/html/2512.22476v1 | T02 partly (bar stamps) |
| F07 | data | Bad prints and flash wicks drive extremes | extreme-based signals fire on one-tick wicks | re-run with wicks > k ATR clipped | model knowledge | NONE |
| F08 | data | Data venue differs from trading venue (Binance bars, Deribit fills) | backtest on one venue, trade on another | compare bar close Binance vs Deribit on the same minutes | model knowledge | section 2 G8 (Deribit parity) |
| T01 | time | Look-ahead through resample labels, centred windows or pivot confirmation | signals differ when the future is cut off | truncation and poison test | https://arxiv.org/html/2512.22476v1 | T02 |
| T02 | time | Session clocks without DST or with fixed UTC | US open label shifts one hour for half the year | count events whose label flips under DST rule | model knowledge | T02 L6 |
| T03 | time | Funding settlement window and sign mishandled | funding charged on wrong side or boundary | planted funding canary | https://arxiv.org/html/2512.22476v1 | T03, T06 L1 |
| T04 | time | Signal-to-fill latency: fill at the signal bar close | result worsens with a 1-2 bar delay | rerun with next-open and +1 bar fills (D1) | https://arxiv.org/html/2512.22476v1 | section 2 partly; demonstrated here D1 |
| T05 | time | Weekend and holiday liquidity seasonality ignored | edge lives only in thin hours | split events by hour/weekday; count per cell | model knowledge | NONE |
| T06 | time | Higher-timeframe join keyed on bar open | daily/weekly level known before it closed | merge_asof direction audit | model knowledge | T02 |
| C01 | costs/fills | Flat cost where spread and slippage scale with volatility | cost under-charged in fast minutes | vol-scaled slippage rerun (D5) | https://www.binance.com/en/academy/articles/what-is-backtesting | section 2 G7 partly; demonstrated D5 |
| C02 | costs/fills | Maker orders filled on touch | fill rate and adverse selection overstated | require trade-through by k ticks | model knowledge | section 2 G4 (through_ticks flag) |
| C03 | costs/fills | Gap through the stop booked at the stop price | stop loss smaller than live | book stop at next open when gapped | model knowledge | section 2 N2/G7, T03 |
| C04 | costs/fills | Funding charged flat or on the wrong side | shorts pay where they receive | real per-settlement funding | https://arxiv.org/html/2512.22476v1 | T06 L1, T03 |
| C05 | costs/fills | Intrabar order ambiguity: stop and target both inside one bar | optimistic ordering inflates win rate | count bars where both are reachable (D2) | model knowledge | T03 convention only; demonstrated D2 |
| C06 | costs/fills | Market impact and queue position ignored | size larger than top-of-book depth | compare clip size to bookDepth | model knowledge | NONE |
| C07 | costs/fills | Tick size, lot size and minimum notional ignored | orders rejected or rounded live | round to instrument grid | model knowledge | NONE (grep tick_size in backtest: 0 hits) |
| C08 | costs/fills | Fee tier, maker rebate and venue fee mismatch | net sign depends on 2 bp | single fee module | model knowledge | T06 L3, section 1a fees.py |
| C09 | costs/fills | Liquidation, margin and auto-deleveraging not simulated | leveraged path ends early live | simulate maintenance margin on worst bars | model knowledge | NONE (grep liquidat in backtest: 1 unrelated hit) |
| S01 | statistics | Multiple testing across arms, horizons and variants (family-wise error) | some arm passes by chance (D3) | placebo null across K arms | https://www.cxoadvisory.com/big-ideas/seven-habits-of-highly-ineffective-quants/ | T05 L7; section 2 E1/E4; demonstrated D3 |
| S02 | statistics | Overlapping holds and autocorrelated events inflate n | naive SE too small | cluster or block bootstrap | model knowledge | T05 L7 |
| S03 | statistics | Trial count not recorded (garden of forking paths) | DSR cannot be computed | trial ledger completeness | https://bookdown.org/palomar/portfoliooptimizationbook/8.2-seven-sins.html | section 2 E1, T08 |
| S04 | statistics | Fat tails and skew break the t-test | t=2 on a handful of outliers | trimmed mean and bootstrap CI | https://mathinvestor.org/2014/04/faqs-on-backtest-overfitting/ | NONE |
| S05 | statistics | Low power: MDE bigger than the effect asked about | INCONCLUSIVE read as no effect | report MDE next to every null | model knowledge | section 2 G1 |
| S06 | statistics | Control group that contains the signal | DIFF vs control is biased to zero | control purity check | model knowledge | T05 L8 |
| S07 | statistics | Out-of-sample reuse and split leakage | validation read twice | exposure ledger per read | https://www.columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf | T08 L2 |
| R01 | regime | Regime drift: a long-biased arm rides the trend | per-year mean flips sign (D4) | per-year and long/short split | model knowledge | NONE; demonstrated D4 |
| R02 | regime | Structural breaks: listing, halving, ETF flows, fee-schedule changes | rule works before a date only | rolling-window stability by quarter | model knowledge | NONE |
| R03 | regime | Exchange outages and extreme days (e.g. 2022-11 FTX, 2023-03 USDC depeg) | a few days carry the P&L | drop the top-5 days and rerun | model knowledge | NONE |
| R04 | regime | Liquidation cascades make stops unfillable | fills far from stop in cascade minutes | stress the 20 worst minutes | model knowledge | section 2 G7 partly |
| E01 | selection | Storytelling: rule invented after seeing the chart | parameters tuned to anecdotes | pre-registration with SOURCED/OURS labels | https://www.columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf | CLAUDE.md numbers rule; PRE_REG files |
| E02 | selection | Selecting the timeframe, symbol or window after looking | only the best cell is reported | count cells examined vs reported | https://gainium.io/blog/common-backtesting-problems | section 2 E2, T08 |
| I01 | implementation | Backtest code and live code are different implementations | live fires on different bars | run backtest function on the live log | https://arxiv.org/html/2512.22476v1 | T09 (missing); section 1c parity.py |
| I02 | implementation | Cost in percent but risk in R: cost in R-units ignored | stop 0.044% vs cost 0.14% = 3.2R | cost-in-R gate | model knowledge | section 2 E3 |
| I03 | implementation | Duplicate loaders and split schemes (25+ loaders, 8 splits) | same study differs by loader | single-source import test | model knowledge | T01, T08 |
| O01 | operations | Exit reason misclassified in the ledger | target exits are really stops | re-derive exit class from prices | model knowledge | section 2 LEDGER_EXIT_AUDIT |
| O02 | operations | Stale feed: writer behind klines | signals on old window | staleness guard | model knowledge | NONE verified |
| O03 | operations | Restart or state loss mid-trade | position unknown after crash | restart test with open position | model knowledge | CLAUDE.md live-path rule |
| O04 | operations | API errors and rate limits | orders dropped, retries double-send | fault-injection test | model knowledge | CLAUDE.md live-path rule |
| O05 | operations | Testnet fills are synthetic and thin | testnet P&L not a cost estimate | compare testnet slippage to mainnet book | model knowledge | section 2 G3 |
| O06 | operations | Tests not in the CI gate | a regression ships green | gate coverage diff | model knowledge | T07 L9 (missing) |

Web sources used: arXiv 2512.22476 (perpetual-futures backtest fragility: next-bar execution, funding look-ahead, reused evaluation windows); Luo et al., Seven Sins of Quantitative Investing (Deutsche Bank 2014); Palomar portfolio-optimization book section 8.2; CXO Advisory summary of Lopez de Prado on why ML funds fail; Math Investor FAQ on backtest overfitting; Gainium common backtesting problems; Binance Academy what-is-backtesting. A search for the Bailey/Lopez de Prado PBO paper itself returned no direct hit; DSR/PBO are in B/bt/bt_stats.py:57-69 (psr, expected_max_sr, dsr, pbo_cscv) and are called only by the Fabio v3 and ref_pbo runners (run_v3_l3.py:262-266, run_backtest.py:118).

## 4. Matrix

Full matrix: scripts/T10/matrix.csv (45 rows x 43 columns: 16 studies S01-S16 in brief 1b order, 27 registry keys of build_default_registry as `L layer|sub|tf`). Cell = status plus evidence in brackets. Row and column counts: scripts/T10/matrix_summary.csv.

Totals: HANDLED 89, NOT HANDLED 540, N/A 531, UNKNOWN 775. UNKNOWN is large on purpose: a cell is HANDLED or NOT HANDLED only where a file line, a grep of the whole backtest tree, a brief statement or a T-report shows it. Chasing the UNKNOWN cells is the next audit, not a defect.

### 4a. By failure mode (sorted by NOT HANDLED)

| Mode | HANDLED | NOT HANDLED | N/A | UNKNOWN |
|---|---|---|---|---|
| F05 Single-instrument universe (BTC only): result may be an instrument accident | 0 | 43 | 0 | 0 |
| F08 Data venue differs from trading venue (Binance bars, Deribit fills) | 0 | 43 | 0 | 0 |
| C01 Flat cost where spread and slippage scale with volatility | 0 | 40 | 3 | 0 |
| C06 Market impact and queue position ignored | 0 | 40 | 3 | 0 |
| C07 Tick size, lot size and minimum notional ignored | 0 | 40 | 3 | 0 |
| C09 Liquidation, margin and auto-deleveraging not simulated | 0 | 40 | 3 | 0 |
| R04 Liquidation cascades make stops unfillable | 0 | 40 | 3 | 0 |
| R02 Structural breaks: listing, halving, ETF flows, fee-schedule changes | 0 | 38 | 0 | 5 |
| T04 Signal-to-fill latency: fill at the signal bar close | 1 | 27 | 3 | 12 |
| C05 Intrabar order ambiguity: stop and target both inside one bar | 0 | 27 | 3 | 13 |
| I01 Backtest code and live code are different implementations | 0 | 27 | 0 | 16 |
| I02 Cost in percent but risk in R: cost in R-units ignored | 0 | 27 | 3 | 13 |
| O05 Testnet fills are synthetic and thin | 0 | 27 | 16 | 0 |
| R03 Exchange outages and extreme days (e.g. 2022-11 FTX, 2023-03 USDC depeg) | 0 | 16 | 0 | 27 |

Rows with zero NOT HANDLED and zero HANDLED are all-UNKNOWN or all-N/A and are in matrix_summary.csv.

### 4b. By study and layer (columns)

| Column | HANDLED | NOT HANDLED | N/A | UNKNOWN |
|---|---|---|---|---|
| S01 session_extreme_fade | 6 | 17 | 6 | 16 |
| S02 preopen_tops | 1 | 11 | 6 | 27 |
| S03 mal_bb_mid_engulf | 2 | 14 | 6 | 23 |
| S04 bb_mtf_center | 1 | 11 | 6 | 27 |
| S05 weekly_low_round_sweep | 1 | 11 | 6 | 27 |
| S06 wlow_bounce_bbrsi60 | 2 | 14 | 6 | 23 |
| S07 krown_malkan_counts | 1 | 6 | 25 | 13 |
| S08 qriptal_calls | 0 | 5 | 26 | 14 |
| S09 candle_close | 0 | 13 | 6 | 26 |
| S10 levels_sizing | 0 | 14 | 6 | 25 |
| S11 level_hold_lc1 | 0 | 6 | 24 | 15 |
| S12 orderflow_views | 0 | 15 | 6 | 24 |
| S13 eur_low_us_sweep | 0 | 12 | 6 | 27 |
| S14 mfe_exits | 2 | 14 | 6 | 23 |
| S15 published_strats | 1 | 13 | 6 | 25 |
| S16 tom_fabio_matrix | 1 | 13 | 6 | 25 |
| 27 testnet layer keys (sum) | 71 | 351 | 378 | 415 |

Study S01 (the gross-effect screen) has the most HANDLED cells because its code was read line by line (screen.py:30, :55, :183, :193, :422, :430, :451). That is a reading effect, not proof the others are worse. Layer columns are nearly identical because the same registry and the same executor serve all of them; only the T02 look-ahead row differs (22 PASS, 5 NOT DECISIVE).

## 5. Demonstrations (DEV, seed 20261024)

Script: scripts/T10/t10_demos.py. These show effect size on a plain 60-bar breakout rule that is NOT one of the 16 studies. They are not study results and change no verdict.

```
seed 20261024; DEV bars 1313280; first 1640995200000 last 1719791940000 (< 1719792000000)

D1 entry timing: 60-bar breakout, hold 30 bars, n=14672, gross % per trade (cost 0.14 not subtracted)
  fill at signal close (same-bar)    mean -0.0090%  se 0.0037
  next bar open                      mean -0.0089%  se 0.0037
  open +1 bar delay                  mean -0.0083%  se 0.0036

D2 intrabar order ambiguity: share of 1m bars where a long entered at the bar open could hit BOTH stop and target inside that one bar
  stop 0.044% target 0.088%: both-in-bar 3.27% of bars; stop-reachable-in-bar 30.61%
  stop 0.1% target 0.2%: both-in-bar 0.37% of bars; stop-reachable-in-bar 10.47%
  stop 0.13% target 0.26%: both-in-bar 0.16% of bars; stop-reachable-in-bar 6.45%

D3 multiple arms under a placebo null (random entry, random sign, hold 390 bars, n=200/arm, 1000 reps, seed 20261024)
  K= 1 arms: P(any arm passes gross>=0.14 & t_gross>=2) = 1.4%;  P(any arm t_net>=2) = 0.00%
  K= 4 arms: P(any arm passes gross>=0.14 & t_gross>=2) = 7.8%;  P(any arm t_net>=2) = 0.10%
  K=12 arms: P(any arm passes gross>=0.14 & t_gross>=2) = 23.8%;  P(any arm t_net>=2) = 0.10%
  K=40 arms: P(any arm passes gross>=0.14 & t_gross>=2) = 60.5%;  P(any arm t_net>=2) = 1.00%

D4 regime drift: mean 390-bar forward return (long-only, %) per calendar year, and a 70/30 long/short random-sign arm
  2022: long-only mean -0.0626%  70/30 arm expected -0.0251%  (pass bar needs +0.14)
  2023: long-only mean +0.0768%  70/30 arm expected +0.0307%  (pass bar needs +0.14)
  2024: long-only mean +0.0665%  70/30 arm expected +0.0266%  (pass bar needs +0.14)
  all DEV: long-only mean +0.0189%  70/30 arm +0.0076%

D5 flat 2 bp slippage vs entry-bar range, breakout entries n=14672
  all-bars median 1m range 5.8 bp; entry-bar median 8.4 bp, mean 12.5 bp
  slippage = 10% of entry-bar range per fill => 1.25 bp per fill vs flat 2.0 bp; round-trip extra -0.0150% on top of the 0.14%
  share of entries whose bar range exceeds the whole 14 bp round-trip cost: 27.7% (all bars 15.0%)
```

What each number means:

- D1 (entry timing, T04). Filling at the signal close, the next open or one bar later moves the mean by under 0.001 percentage point (-0.0090, -0.0089, -0.0083, se 0.0037). For this rule the delay does not matter, so this cell is CLEARED for a 30-bar hold. It is not cleared for the 27 testnet layers, because execution/ records no decision price (brief 1c).
- D2 (intrabar order, C05). At the stop sizes the traders state (0.044%/0.088%), 3.27% of all 1m bars could hit both stop and target, and 30.6% reach the stop inside the entry bar. At 0.10/0.20 it is 0.37% and 10.5%. Any 1m simulator with tight stops must pick an order inside a bar; T03 tested the engine convention but no study reports its sensitivity to it.
- D3 (multiple arms, S01). With a placebo null, the share of runs where at least one arm passes `gross mean >= 0.14% and t_gross >= 2` is 1.4% for 1 arm, 7.8% for 4, 23.8% for 12, 60.5% for 40. The full net bar (`t_net >= 2`) keeps the rate at 0.00%, 0.10%, 0.10%, 1.00%: the cost is a strong guard. The risk is in the gross stage and in the INCONCLUSIVE and exploratory reads, which have no correction (brief L7).
- D4 (regime drift, R01). Mean 390-bar long-only return by year: 2022 -0.0626%, 2023 +0.0768%, 2024H1 +0.0665%; whole DEV +0.0189%. A 70/30 long/short arm carries 0.4 times that drift (+0.0076% on all DEV, up to +0.031% in 2023). Small against the 0.14% bar but of the size of the DIFF bar (+0.05%) in a good year.
- D5 (volatility-scaled cost, C01). Median 1m range is 5.8 bp, but the bar after a breakout signal has median 8.4 bp, mean 12.5 bp, and 27.7% of entries sit in a bar whose range exceeds the whole 14 bp round-trip cost (15.0% of all bars). With slippage = 10% of the bar range the mean slip is 1.25 bp per fill, below the flat 2 bp, so the flat cost is conservative on average and CLEARED in the mean; the tail (27.7% of entries in fast bars) is not measured.

## 6. Findings

| ID | Sev | Status | Evidence | Size | Fix | Card |
|---|---|---|---|---|---|---|
| T10-F1 | S2 | CONFIRMED | scripts/T10/t10_demos.py D3, screen.py:220-250 and common.py:192-230 (brief L7) | placebo: 23.8% any-arm pass at 12 arms on the gross screen, 60.5% at 40; 0.10% / 1.00% on the net bar | correct for arms, horizons and variants before any PASS or KEEP | g5-screens-family-wise-correction-across |
| T10-F2 | S2 | CONFIRMED (rate), SUSPECTED (effect) | D2; Tom/Fabio stops 0.044-0.13% (brief 1b) | 3.27% of 1m bars hold stop and target at 0.044/0.088; 30.6% reach the stop in the entry bar | report stop-first vs target-first bounds for every 1m sim with stops under 0.15% | intrabar-stop-target-ordering-sensitivit |
| T10-F3 | S2 | CONFIRMED (absence) | grep ETHUSDT in the study.py files: 0 hits; matrix F05 row, 43 of 43 NOT HANDLED | 0 of 16 studies have a second instrument | rerun frozen DEV rules on ETHUSDT DEV | rerun-the-frozen-dev-rules-on-ethusdt-as |
| T10-F4 | S2 | CONFIRMED (absence of grep hits for trimmed/top-days), SUSPECTED for year splits | D4; grep trim_mean/winsor/top_days: 0 hits in studies | drift -0.06..+0.08% per year vs 0.14% bar; no top-days-removed run | per-year, long/short, top-5-days-removed table per study | stability-report-per-study-per-year-long |
| T10-F5 | S3 | CONFIRMED (absence) | grep tick_size/min_notional/lot_size in B/ and R/: 0 files; execution/testnet/t050_phase3.py:33 hard-codes min_trade_amount 10 | none now | add a tick and lot rounding step before any live-size claim | none (S3) |
| T10-F6 | S3 | CONFIRMED (absence) | grep liquidat in B/: 1 unrelated line (tom_bt_report.py:224) | none at current sizes | margin and ADL stress before any leverage above 1x | none (S3) |
| T10-F7 | S3 | SUSPECTED | D5 tail: 27.7% of breakout entries in bars wider than the whole cost | unmeasured | cost by volatility decile on a real study | none (S3) |

Cleared: D1 (entry delay, for the tested rule), D5 mean (flat 2 bp is conservative on average).

Posted to Claude (desk, --target CLAUDE, not shipped by this builder): `20261024-102440-dsa-session-prompt-four-bridge-rules-fro`, four DSA prompt lines from the playbook. No live-path finding is new: the missing decision price and the missing backtest-versus-testnet fill comparison are already in brief 1c and FABLE E5.

## 7. Not checked, decisions, handover

- BLOCKED: web search found no direct text of the Bailey/Lopez de Prado PBO paper; the PBO row rests on bt_stats.py. Mode sources marked `model knowledge` are not cited to a URL (rule: cite only items taken from a list).
- BLOCKED: 775 of 1,935 cells are UNKNOWN because the per-study code was not read for each failure mode (time cap). Highest-value next reads: C03, C05, T04 for S02-S06, S09, S10, S13-S16.
- DECISION (OURS): 43 columns = 16 studies of brief 1b plus the 27 registry keys; not every study ever run (card item 6).
- DECISION (OURS): cells default to UNKNOWN, never to HANDLED. A claim of absence is allowed only with a grep count or a brief/T-report citation in the cell.
- DECISION (OURS): D3 reports both the lax gross screen and the full net bar, because the net bar is the real G5 rule and the gross screen is where uncorrected arms matter.
- DECISION (OURS): the demos use a generic breakout rule, not a published study, so no study number is re-derived.
- DECISION (OURS): the playbook is written from the four shipped reports; T04-T07, T09 are listed as missing.
- Handover. Top fix: T10-F1 (family-wise correction). File: gross_effect_screen_2026-10-15/screen.py:220-250 and chart_read_g5_2026-10-16/common.py:192-230. Test that proves it: a placebo run of K arms must pass at most the nominal rate (D3 numbers become the fail-first case). Risk: past PASS_FLOW and KEEP labels may move to INCONCLUSIVE. Rerun after: scripts/T10/t10_demos.py (D3) and each study's own test.

## 8. Bridge log

No AIBridge was used by this card (Claude builder session, native tools). The merged playbook of the other audits is scripts/T10/T10_BRIDGE_PLAYBOOK.md. One-line rule for the next chat: boot by hand if task=mts-boot fails once, and write files fresh instead of patching them with .Replace in PowerShell 5.1 (T01 #1, #50).

## 9. Reproduce

From the worktree root: `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/t10_build_matrix.py`, `.../t10_demos.py` (needs F:/MTS/data, pandas, about 25 s), `.../t10_build_report.py`, and `python -m pytest MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/test_failure_matrix.py`.
