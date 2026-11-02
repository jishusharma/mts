# Simulator visuals review (Opus 5.5 via Console API batch msgbatch_01PpdaZ2N43Pzfc9NHxyErqQ, 2026-11-03)

# Backtest simulator page: design review

## 1. What established tools show

| Tool | Views and panes | Trade markers | Interactions | Notes |
|---|---|---|---|---|
| **TradingView Strategy Tester** | One continuous price chart with indicator panes below. Tester panel with Overview (equity curve, drawdown), Performance Summary, and List of Trades. | Entry and exit arrows on the candles, labelled with the order name and size. | Scroll and zoom the chart. The trade list shows entry/exit times, profit, and run-up/drawdown per trade. | Standard. All trades sit on one chart. |
| **TradingView Bar Replay** | The same chart with everything to the right of a chosen point hidden. | Your own drawings or the strategy's markers as bars appear. | Step one bar, Play with speed control, jump back. | Standard for "live it again" checking. |
| **MT5 Strategy Tester, visual mode** | Chart that builds bar by bar (or tick by tick) with indicators drawing live. Report tabs: balance/equity graph, statistics, deals list. | Buy/sell arrows joined by a dotted line from entry to exit. Stop-loss and take-profit lines show while a trade is open. | Speed slider, pause, single step. | Standard. The closest match to "show me entering and getting stopped". |
| **NinjaTrader Strategy Analyzer** | Tabs: Summary, Analysis (graphs), Trades, Executions, Orders, Chart. | Execution markers on the Chart tab with entry→exit lines. | Sort the trade list. Market Replay is a separate playback mode. | Standard. |
| **QuantConnect** | Equity, drawdown, and benchmark charts. Orders table. Custom charts where you plot price and indicators. | Order markers on the asset plot. | Zoom. Download orders. | Candle-level detail is weak; you plot it yourself. |
| **backtesting.py** | One interactive page: equity pane, profit/loss-per-trade pane, candles, volume, indicator panes. All panes share the time axis. | Each trade is a dashed line from entry to exit, green for a win and red for a loss. Triangles mark per-trade results. | Linked zoom and pan, hover tooltips. | Static HTML output, the nearest model for our page. |
| **Backtrader `plot()`** | Value pane, trade-result pane (win/loss dots), price with buy/sell triangles, indicator subpanes. | Buy/sell triangles. | Static image. | Standard but crude. |
| **FX Replay** | Bar replay across several synced timeframes. | Orders you place by hand, with stop and target lines. | Step, play, place trades, journal, stats. | Built for manual practice, not rule testing. |

**Standard everywhere:** all trades marked on one continuous chart, an equity curve, a trade list, and indicator panes under the price.

**Rare in testers:** a separate small chart for each trade. That view comes from trade journals (Tradervue, TraderSync, Edgewonk), not from strategy testers.

## 2. The basic idea of a simulation, in plain words

1. The computer walks through the history **one candle at a time**, in order, never peeking ahead.
2. On **every** candle it asks the rule: "Is the entry condition true now?" Almost always the answer is no, and nothing happens. That is why you do not see something on every candle.
3. When the answer is yes, that candle is the **signal**. The trade is **entered at the open of the next candle**, because you only know the signal once the candle has closed.
4. While the trade is open, it asks on every candle: "Is the exit condition true?"
   - For C30 H1, the exit is WaveTrend crossing back above 0, or a time cap of 60 candles (30 hours).
   - **This rule has no stop loss**, so no trade can be "stopped out". The page must say this plainly.
5. After the exit, it goes back to waiting for the next signal.

**How tools show this:**
- **Standard:** one long chart, every trade marked, and you scroll or jump between them.
- **Also standard:** a replay that builds the chart candle by candle so you watch each phase happen (waiting → signal → in trade → exit).
- **Rare:** one trade at a time in its own box.

## 3. Minimum visuals, in priority order

| # | Visual | What it shows | Why he needs it | Same as | Size |
|---|---|---|---|---|---|
| 1 | **Trade chart (continuous strip)** | 30m candles around each trade, with neighbouring trades visible. The holding period is shaded green or red. Signal, entry, and exit markers. Y axis is % from the selected trade's entry. | Shows what was traded, when, and the context around it. | backtesting.py, TradingView chart, NinjaTrader Chart tab | M |
| 2 | **Indicator panes** under the chart, sharing the time axis | WaveTrend with the -53 and 0 lines. RSI with the divergence lows joined. | Shows why the rule fired and why it exited. | All of them | S (on top of #1) |
| 3 | **Trade list** (click a row to jump the chart) | Number, entry time (UTC), exit time, candles held, exit reason (WT>0 or 60-candle cap), net %, worst % against, best % for. | One row per trade. Lets him pick any trade. | TradingView List of Trades, NinjaTrader Trades | S |
| 4 | **Step-through replay** of the selected trade | Candles appear one by one. A status line reads "Waiting / Signal / In trade (candle 7 of 60) / Exited: WT crossed 0". | Directly answers "when do you get in, when do you get out". | TradingView Bar Replay, MT5 visual mode | M |
| 5 | **Running-total line** (already built), labelled | Cumulative net % after each trade, with drawdown shading. The dot is the trade currently shown on #1. | Tells him whether the whole rule adds up. | Every tester's equity curve | S (relabel) |
| 6 | **Rule card in plain words** above the chart | Entry, exit, stop ("none"), timeframe, costs. | He must know what to look for before looking. | TradingView strategy Properties/Inputs | S |

The worst/best % figures in #3 come from the 1m data inside each trade. All visuals are percent-only and can be built as static HTML for one test at a time.

## 4. Critique of the per-trade candle panel

**Verdict: keep the content, change the frame.**

The candles, markers, WaveTrend pane, RSI pane, and Prev/Next synced with the dot are the right parts. What to change:

| Change | Why |
|---|---|
| Show it as a window onto a **continuous strip**, not 35 isolated boxes. Prev/Next scrolls to the next trade, and neighbouring trades stay visible. | Isolated boxes hide what happened between trades. They make it look as if the rule only "sees" 45 candles. |
| **Shade the holding period** between entry and exit. | Markers alone do not read as "in a trade". |
| Add the **step-through replay** (#4) inside the panel. | This is the thing he literally asked for. |
| Print **"No stop loss in this rule"** where a stop line would be. | He keeps asking about getting stopped out. |
| Add a **status/caption line** per trade, e.g. "Entered 2023-05-04 14:30 UTC; held 9 candles (4.5 h); exit: WaveTrend crossed 0; net +1.2%". | One sentence explains the whole trade. |

**Things that will confuse a non-developer:**
- **"Signal candle" vs "entry (next open)":** say "signal seen at close → bought at next open".
- **"% from entry price":** say "0% = where we bought". Put a 0% line on the chart.
- **WaveTrend -53 and 0:** label them on the chart: "-53 = oversold trigger", "0 = exit line".
- **"Divergence lows joined":** add a caption: "price made a lower low, RSI made a higher low".
- **Time zone:** state it once (UTC?).
- **"60-candle cap":** say "max 30 hours".
- **Jargon elsewhere on the page:** "VALIDATION", "SOURCED/OURS", "H1/H2" need one-line tooltips.
- **The red dot:** label it "you are here: trade 12 of 35" on the running-total line.

## 5. Requirements file: rows to add or reword

| # | Change |
|---|---|
| 2 (reword "What it means") | "One continuous 30m candle chart per test with all trades marked, holding periods shaded, signal/entry/exit markers, and WaveTrend and RSI panes underneath. Prev/Next jumps between trades. C30 H1 has no stop; state it on the chart." |
| 3 (new, his words from latest dictation) | "Show the basic idea": a plain rule card plus a step-through replay of one trade, candle by candle, with a phase status line. Same as TradingView Bar Replay / MT5 visual mode. Size M. |
| 4 (new) | Clickable trade list with entry/exit time, candles held, exit reason, net %, worst/best % during the trade. Size S. |
| 5 (new) | Label everything on the chart: 0% = entry, WT -53/0 lines, divergence caption, red dot = "trade N of M", time zone. Size S. |
| P3 (reword) | "Published page gets a percent-axis candle chart (no prices) for any test with exported trades. desk.py stays for settings and runs; do not rely on it for review." |
| P4 (new) | Define the reference for the % axis when several trades are visible (the selected trade's entry). Check that the static page stays a reasonable size, one test loaded at a time. Size S. |
| P5 (new) | Every test row states timeframe, entry rule, exit rule, and stop rule (or "none") in plain words. Size M across 337 tests. |
| P1 (extend) | The exporter must save per-trade exit reason and the 1m worst/best % so the trade list can be filled. |
