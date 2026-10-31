# Plugging a layer into the simulator desk

One layer = one file in `studies/`. The desk finds it at start. No edit to `desk.py` and no edit to the page.
`studies/levels.py`, `studies/rsi.py`, `studies/wavetrend.py`, `studies/krown.py` and `studies/pitchfork.py` are the working examples. Bar-based layers share `studies/_bars.py`, which loads the 1m bars, builds the higher timeframes and runs one trade on 1m bars (stop, target, signal exit, time limit, fees). `test_plugin.py` shows how small a file can be: it uses a 30-line dummy study.

## What the layer file must provide

| Name | What it is |
|---|---|
| `ID`, `TITLE` | A short id (used in the trial ledger) and a plain title for the page. |
| `params()` | The settings boxes. Each box has a plain label. A box is a list of choices, a number with min/max, or a date. |
| `normalize(p)` | Fills in defaults and checks the typed values. Bad input gives a plain error such as "please type a number". It must keep `start`/`end` inside the development window. |
| `label(q)`, `describe(q)` | A short ledger label, and one plain sentence saying what this setting does. |
| `run(q, progress)` | Runs the backtest and returns one row per trade idea. The rows hold `day`, `touch_t`, `net` (R after fees), `gross`, `fees` and `filled` (did it actually trade). They also hold `all_days` and `refs`, where `refs` is a handle used to redraw one trade. |
| `chart_trade(ref, q)` (optional) | The 1m bars of that day, side, level, entries (time and price), stop, target, exits (time, price and reason) and net R. Without this function the desk shows no charts. |
| `PRIOR_TAG`, `build_cache()` (optional) | The ledger tag of earlier tries made outside the desk, and a one-off data cache build (`desk.py --build`). |

## What the desk does for every layer

- **Date lock:** only the development window (2022-04-01 to 2024-06-30) can be run. The validation and held-back data are never offered.
- **Verdict:** counts filled trades only, and states the 95 % range of the average. Under 30 filled trades it always reads NOT ENOUGH DATA:
  - PASSED when the whole range is above zero.
  - FAILED when the whole range is below zero, or when even the top of the range is below +0.10 R and the sample was big enough to see +0.10 R.
  - Otherwise NOT ENOUGH DATA.
- **Trial ledger:** each new setting writes one row to `layer_lab/TRIALS.md` before the result shows. A repeat writes nothing. The page shows how many tries were made.
- **Charts:** the 3 winners and 3 losers closest to the typical winner and loser, with date and time in UTC.
- **Questions panel:** the open decisions are shown on the page, and answers are saved to `cache/answers.jsonl`, which is local and never committed. New questions go in `questions.json`.

## Which layers fit (survey 2026-10-21, updated 2026-10-28)

"Fits now" means a layer already returns timestamped trades. **No layer does that today**, so every layer below needs a small adapter or does not fit yet.

| Layer | Verdict | Why |
|---|---|---|
| Levels study | **Fits (plugged in)** | `studies/levels.py`. |
| RSI 40/60 (Malkan) | **Plugged in 2026-10-21** | `studies/rsi.py` wraps `rsi_core` and `malkan_40_60` unchanged. The trader's setting (daily chart, entry above the signal candle, stop past it, exit at RSI 60/40) finds only 2 trades on DEV. The 4h and 1h charts are ours. |
| WaveTrend (LazyBear) | **Plugged in 2026-10-21** | `studies/wavetrend.py` wraps `wavetrend.py` unchanged. Cross out of the 53/60 band, 3-bar stop and 1.5 x risk target are the traders'. The timeframe and the entry at the next bar are ours. |
| Pitchfork (Andrews / Schiff / Modified Schiff) | **Plugged in 2026-10-28** | `studies/pitchfork.py` wraps `pitchfork_detector.py` (`PitchforkChannel`, `scan_pitchfork_signals`) and `vp_pivot_probe.py` (`build_profile`). Offers Standard Andrews, Schiff, and Modified Schiff channel geometries, tine bounce (80% rule) and Hagopian failure breakouts, and TPO profile Value Area / POC confluence filtering on 4h and daily bars. |
| Tom volume profile (BTC / ETH) | **Plugged in 2026-10-31** | `studies/tom_vp.py` wraps `vp_pivot_probe.build_profile` (FORMULAS 18.1) unchanged and reads volume from the same 1m CSVs. The concepts of his 2026-10-30 video are the settings: prior-day or prior-week value area, three trade ideas (return to value, edge fade, accepted away after N closes), the acceptance exit, the value-migration filter, POC or R target. Source check: `research/tom_transfer_2026-10-11/VP_VIDEO_CONCEPT_CHECK_2026-10-31.md`. First grid (12 settings, DEV): 10 FAILED, 2 weekly NOT ENOUGH DATA. Updated 2026-10-31 (card sim-desk-tom-fabio-studies): each exported run (`results/desk-tom_vp-*.json`, re-exported by `export_grid.py tom_vp`) now carries the desk's 3 winners + 3 losers as candle charts with entry, stop, target, exit, exit reason and net R after fees (example kind `charts`, no prices stored). Tom spike fade and level touch are still not on the desk. |
| Cowen band concepts (BTC / ETH) | **Plugged in 2026-10-31** | `studies/cowen_bmsb.py` builds the bull market support band (20-week SMA and 21-week EMA, completed weeks only) from the same 1m CSVs. Four ideas from his 2026-10-30 video are the settings: bounce off the band, band lost, fake-out below the 50-day, catch-down when the other coin is at its band. The midterm structure, rate-hike lag and IPO analogs are 1 to 3 events and are NOT testable here. Source check: `research/cowen_q4_2026-10-31/COWEN_Q4_CONCEPT_CHECK.md`. First grid (12 settings, DEV): all NOT ENOUGH DATA, 3 to 10 trades each. |
| Tom (BTC, order-flow proofs) | **Small adapter** | `backtest/tom_bt.py` runs on cached rows and 1m bars, with no Java needed. Its trades carry bar numbers, not times, so it needs a time wrapper and a settings list. The current Tom rules are on STOP while v2 is written (LAYERS.md), so wrap v2 only. |
| CryptoCred | **Small adapter** | `layers/cryptocred/cc_bt_adapter.py` already turns signals into trades. Its tested setups failed. |
| Session levels / momentum, funding fade, big-trade fires | **Small adapter, low value** | All closed with no edge, or their held-back data is still unread. |
| Fabio (order flow, v3) | **Does not fit as order flow; price-only parts plugged in 2026-10-31** | The real v3 run needs order-flow bars (delta, big trades, footprint) that start 2024-12-02, after the development window, so it cannot go on the desk. `studies/fabio_v3.py` runs the price-only parts on 1m klines (BTC, New York window): Model C (first-30-minute range breakout) and Model B (failed breakout back into a balance box). It uses `signals.balance`, `models.d_and_stop` and the NY calendar unchanged; Model B is scored with a real stop and target (the v3 runner scores it 0 R). Left out and said on screen: Models A and D (they need delta pressure and absorption), the big-trade push (candle stand-in, ours), absorption in Model B, order-flow exits, break-even moves, the day gate, resting-limit entries. First grid (10 settings, DEV): Model C 4 NOT ENOUGH DATA at n 515-518 and the 2R variant too; Model B 4 of 5 FAILED (n 64-155) and N240 NOT ENOUGH DATA (n 19). Charts: `export_grid.py fabio_v3`. Source: `research/tom_fabio_review_2026-10-31/SETUP_REVIEW.md` section 3. |
| Tom DAX | **Does not fit** | It trades a different market, and no DAX data has been bought. |
| Detectors and studies (volume, candle patterns, guidance matrix, callers) | **Does not fit** | They flag events but are not trading rules, so there are no trades to simulate. |
| Live engine | **Does not fit** | It is execution, not a backtest. |

Every on-screen choice of the RSI, WaveTrend, Krown, Pitchfork, Tom VP and Fabio v3 studies says (trader) or (ours); the file header of each study gives the source file and line.

Which layer goes first is a question on the desk page. Nothing is ported until it is answered.
