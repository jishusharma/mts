# Industry survey: how traders use simulators, and what we build from what we have (Thinker, 2026-11-03)

Why: the operator found the simulator "useless to verify anything". Files read: REQUIREMENTS_2026-11-02.md, ROADMAP.md, SIM_DESIGN_RESEARCH.md (top 60), api_review/SIM_VISUALS_REVIEW.md, desk.py, page.html, results/*.json (all in sim_desk/). Searches: 7, standard mode; most sources are vendor or blog pages, so thresholds are rules of thumb, not standards.

Facts on disk (counted this turn): results/ holds 338 files = 337 results + _catalogue.json. Example kinds across the 337: none 255, table 62, curve 50, charts 27 (desk candle charts, all desk-* ids), replay 12, trade_chart 1 (eagle-c30-wt-rsi-div), sides 2, stack 2. BTCUSDT 1m: 119 files in F:/MTS/data/tom_raw/klines (ROADMAP: 2022-01..2026-09; order flow from Dec 2024; desk DEV window 2022-04-01..2024-06-30; VALIDATION 2024-07..2025-06 and HOLDOUT 2025-07+ sealed). Verdict labels in results/*.json: NOT ENOUGH DATA 39, FAILED 15 (the two largest groups).

## A) What pros and smart retail do (2024-2026)
| # | Practice | Source |
|---|---|---|
| 1 | Bar Replay: step forward bar by bar, watch the tester update | https://www.tradingview.com/chart/ETHUSD/f7EbFMfu-How-To-Backtest-Further-In-The-Past-On-Low-Timeframes/ |
| 2 | Visual mode: dotted line entry to exit, stop/target lines, speed slider | https://www.mql5.com/en/blogs/post/774731 |
| 3 | List of trades next to one continuous chart, click a row to jump (our Opus review, section 1) | api_review/SIM_VISUALS_REVIEW.md |
| 4 | Equity curve plus drawdown under a KPI banner | https://quantconnect.com/docs/v2/our-platform/backtesting/results |
| 5 | Out-of-sample: tune on one window, judge on an unseen one | https://futurevocation.pages.dev/skills/backtesting-methodology-with-rigorous-out-of-sample-testing-walk-forward-analysis-and-overfitting-detection |
| 6 | Walk-forward: roll in-sample/out-of-sample windows, at least 5 cycles, compare the two | https://getpineforge.com/blog/walk-forward-analysis-trading-bots |
| 7 | Monte Carlo: reshuffle the same trades thousands of times, read the 95th-percentile drawdown | https://www.mql5.com/en/blogs/post/774072 |
| 8 | Parameter plateau: neighbours of the chosen setting must also work; a lone peak is fragile | https://www.luxalgo.com/library/concept/parameter-stability/ |
| 9 | Count every try; deflate the result by the number of trials (DSR, PBO) | https://papers.ssrn.com/abstract=2460551 |
| 10 | Costs and slippage inside the test; stability must be paired with realistic costs | https://www.luxalgo.com/library/concept/parameter-stability/ |

Caveats from the same searches: shuffling cannot detect overfitting (a curve-fit trade list shuffles into a good-looking list); walk-forward run on 50 variants and then picking the best re-introduces overfitting.

## B) Do we have it?
| # | Status | Proof |
|---|---|---|
| 1 Bar replay | PARTIAL: 12 results have a replay example, 1 has the per-trade candle chart with indicator panes; 255 of 337 show nothing | results/*.json example kinds; REQUIREMENTS rows P1, 5 |
| 2 Entry/exit/stop markers | PARTIAL: desk draws candles, entry, stop, target, exit (27 results, all desk runs); hosted page has none for most | charts.py line 4; REQUIREMENTS P3 |
| 3 Trade list, click to chart | HAVE on desk (filled trades, click a row for its candle chart); MISSING on hosted page | page.html line 87; REQUIREMENTS row 4 |
| 4 Equity + drawdown | PARTIAL: scrubbable equity curve on desk, max drawdown in stats; 50 results carry a curve; no drawdown line drawn | page.html line 85; desk.py line 96 |
| 5 Sealed out-of-sample | HAVE: desk offers DEV only, cached results refuse trades past the cut; VALIDATION read once per finished idea | desk.py lines 6, 257; ROADMAP R4 |
| 6 Walk-forward | MISSING: only a by-year breakdown table (n, mean R, "too few trades" under 30) | desk.py line 140 |
| 7 Monte Carlo | HAVE on desk (1000 reshuffles, seed 7, 5-95% band and drawdown range); not on the hosted page | desk.py line 108 |
| 8 Stability heatmap | PARTIAL: export_grid.py runs a fixed grid of settings per study; no heatmap view; I did not read its output | export_grid.py docstring |
| 9 Try counter | HAVE: ledger row before result, "Trial #N logged" on every run; no deflation maths | desk.py lines 244, 311, 315 |
| 10 Fee break-even | HAVE as a script: fee x0/0.5/1/2 and break-even multiple per study; on no page | fee_sweep.py docstring |

## C) Build from what we have (max 6, nothing new to fetch)
| # | Build | Value to the operator | Size | Data on disk | Test that must fail first |
|---|---|---|---|---|---|
| 1 | Hosted page: trade list plus candle chart for the 27 desk-* results that already carry charts, then other desk runs | He can open a test and see each trade, the thing he said was missing | M | yes (1m klines, desk results) | Export check: a result with filled trades but no list rows must fail |
| 2 | One fixed verdict banner on every result: verdict, filled trades n, net R after fees, try number, fee break-even multiple | One glance says pass, fail or too few, and why | S | yes (desk.py output, fee_sweep.py) | A run with n under 30 must not read as a pass; fails if banner shows mean R alone |
| 3 | Equity curve with drawdown shading and the Monte Carlo band on the hosted page for the 50 curve results | Shows whether the profit is order luck | S | yes (curve in results, monte_carlo in desk.py) | A curve result without a band field must fail the export |
| 4 | Year-by-year strip from breakdown(), flag when signs disagree | Cheap split-sample check on DEV; not called walk-forward | S | yes (DEV 27 months) | A run positive in one year, negative in others must show "not stable" |
| 5 | Neighbour heatmap from export_grid.py runs (two parameters, colour = mean net R, n on hover) | Plateau vs lone peak, the main overfit check | M | yes for studies with grids (needs a read of export_grid output) | A grid with one positive cell among negatives must label "lone peak" |
| 6 | Candle-by-candle replay with status line for desk runs, reusing the C30 replay code | Answers "when do I get in, when out" | M | yes | Status goes Waiting, Signal, In trade, Exited on a fixture trade; fails before the code exists |

## D) How backtesting is viewed on a simulator page
Top: a verdict banner (pass, fail, not enough data; trade count; net result after fees; try number). Under it one continuous chart with every trade marked entry to exit, the stop line or "no stop" stated, indicator panes sharing the time axis (SIM_VISUALS_REVIEW section 3). Beside it the trade list; a click jumps the chart; optional bar replay of the chosen trade. Below, the equity curve with drawdown, then robustness: a by-period table and a settings heatmap. We already show: verdict and try number (desk), trade list and candle chart (desk only), scrubbable equity curve (desk, 50 hosted results), Monte Carlo (desk only), breakdown by year (desk). Missing on the hosted page: trade list, any chart for 255 of 337 results, drawdown line, heatmap, fee break-even.

## E) Cut
- Quiz, badges, streaks, five-tab layout: already cut by the operator override in SIM_DESIGN_RESEARCH.md (2026-10-25); keep cut.
- Full walk-forward and PBO/CSCV: too few trades (39 results say NOT ENOUGH DATA) and one 27-month DEV window; not worth building until more assets or months exist.
- Rolling Sharpe, return histograms, multi-chart replay, order placing while replaying: noise at this trade count.
- A separate box for each of 35 trades: replace with one strip (REQUIREMENTS row 6).

Noticed:
- 255 of 337 result files have example kind "none": the page shows nothing for them.
- Monte Carlo, fee break-even and breakdown live only in desk.py / fee_sweep.py; I did not check that export_results.py carries them.
- REQUIREMENTS P1 and the Opus review: no file records exit reason per trade, so the trade list needs the exporter extended first.
- ROADMAP says 89 files of 1m data; disk shows 119 (more months fetched since); ROADMAP is stale there.
- export_grid.py names only tom_vp and fabio_v3, so heatmap coverage is narrow.
- I did not open the hosted page itself, only result files and local code.
