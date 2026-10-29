# OPERATOR OVERRIDE 2026-10-25 (read first; it outranks everything below)
Verbatim: "make sure that cool and fun does not mean unnecessary efforts on unwanted/useless stuff - what is need - accuracy + performance + visualization capacity + user friendly + wired for firing back-testing with selectable params for each layer + condition (refer the old design and my verbatim when first model was built)."
First-model verbatim (INPUTS.md 1): "a dashboard ... one page ... where I can click on things and choose, select, run"; "configure whatever layers we want to test and start the runs"; "free-form values ... hit and try ... room for more layers"; "very light ... no cluttering ... the most important and critical things first"; "simple, economical, and very, very powerful".

**The product is the local desk** (`desk.py` + `page.html`, DESIGN.md / PLUGIN.md): it already has Run, per-layer settings, the DEV lock, the trial ledger, the verdict and 6 trade charts, with levels, RSI and WaveTrend on BTC/ETH. The hosted page is only a read-only export of the same result files.
Build, in this order:
1. **Accuracy.** Each study has a reference test that reproduces its known number (levels: 255 filled, -0.119 R). Results are fee-net and count filled trades only. Each new study gets an independent re-derivation. Live-vs-test parity comes from T09.
2. **Selectable params per layer plus conditions.** One shared condition panel applies to any layer before scoring:
   - side (long, short, both);
   - UTC hour window;
   - trend filter (price above or below an EMA, with the timeframe and length typed);
   - volatility band (ATR percentile);
   - day of week;
   - "only when layer B also fired within N bars".
   Values are free-form and labelled (ours). Each new setting adds one TRIALS row.
3. **Performance.** A cached Run takes 10 s or less, with a progress line on the first build. The page shows the run time.
4. **Visualization.** Per-trade candle charts (level, entry, stop, target, exit) and an equity curve in R and as $1,000, which you can scrub. Run A vs run B side by side. A breakdown table by family and condition, with n.
5. **User friendly.** One screen, results first, plain labels marked (trader) or (ours), and plain errors on bad input.
6. Every Run writes `results/<id>.json` in one schema, so the hosted page lists it.
**Cut:** quiz, badges, scoreboard theatrics, play animation (scrub stays), polish of the static mockup, extra tabs. A thought experiment or audit gets one plain card: claim, method, finding, verdict.

# MTS simulator: what to build (Thinker, 2026-10-25, Sonnet lite mode)

Answer in one line: **one static page, five tabs (Tests, Result, Replay, Quiz, Compare), a verdict banner that cannot be hidden, and "if you put 1,000 USD in" as the first number. Clickable mockup: `mockup/index.html` (real numbers: levels ladder, 255 filled trades, -0.119 R, $1,000 -> $715).**
Evidence base: ROADMAP.md, DESIGN.md, REVIEW_FABLE.md, v1 `artifact/index.html` (trade list read from its `D.trades`, filled = `r != 0`: 255, mean -0.1194, win 40.8%, run this session), web searches below. sim-v2 had shipped nothing on trunk under `results/` when read (origin/fast-track @ 0b13455c5); the schema below is proposed, sim-v2 adopts or answers.

## 1. Sources: what people use, what works, what does not, what fits us
Vendor pages are marketing; treat their claims as unverified (the search tool said so for most). Rows marked (vendor) are claims by a seller.

| Tool | What works | What does not | Fits us? | Source |
|---|---|---|---|---|
| TradingView Bar Replay + Strategy Tester | Step through bars, play speed, place orders while replaying; low cost | Shallow intraday history, bar-by-bar not tick; automated testing needs Pine code; result screen not linked to live trades (vendor) | Steal: play/pause + speed + scrub. Skip: order placing | [TradingView support](https://www.tradingview.com:443/support/solutions/43000712747-bar-replay-how-and-why-to-test-a-strategy-in-the-past/), [TradeZella comparison (vendor)](https://www.tradezella.com/vs/tradingview) |
| FX Replay | Replay on 16 charts, "Go to" jump, journal tags, P&L trend, drawdown, Monte Carlo | Manual only (no automated strategy tests), reliability complaints, paid | Steal: "jump to trade", tag a trade. Skip: multi-chart | [LuxAlgo overview (vendor)](https://www.luxalgo.com/blog/fx-replay-backtesting-platform-overview/), [Trustpilot](https://ca.trustpilot.com/review/fxreplay.com) |
| TradesViz | Very many charts and stats, replay | Dense, "less guided"; charts can bury a quick review | Counter-example: 5 views, not 600 | [TradesViz vs Tradervue (vendor)](https://www.tradesviz.com/tradesviz-vs-tradervue/), [roundup](https://tradetanto.com/learn/tradesviz-alternative) |
| Tradervue | Simple reporting, sharing | Older look, reporting-first | Steal: clean report layout, shareable link | [Tradervue vs Edgewonk](https://www.tradervue.com/site/edgewonk-alternative) |
| Edgewonk | Discipline and mistake tracking, strategy lab | Dated interface | Steal: "did you follow the rule" as the score, not P&L | [LuxAlgo analysis (vendor)](https://www.luxalgo.com/blog/edgewonk-journal-tool-analysis/) |
| QuantConnect results | Banner of 8 runtime stats on top, equity curve, drawdown, rolling Sharpe, return histogram; PSR (probability the Sharpe beats a benchmark) | Page is large; rolling stats are noise at 255 trades | Steal: KPI banner on top, one equity curve, one drawdown line. Skip: rolling charts | [QC results docs](https://quantconnect.com/docs/v2/our-platform/backtesting/results), [Lean report](https://quantconnect.com/docs/v2/lean-cli/reports) |
| vectorbt + Streamlit apps | Stats, trades, equity and drawdown in a result view; Plotly | Needs Python server, so not a static page | Pattern only; our page reads precomputed JSON | [marketcalls/vectorbt-streamlit](https://github.com/marketcalls/vectorbt-streamlit) |
| Chart Game / SkillCandle / Alpha Chart | Hide future candles, guess next move, drills, friend ranking | Rewards luck on short rounds; ranking by P&L rewards variance | Steal: "reveal" beat. Fix: score against take-all, not by P&L rank | [App list](https://apps.apple.com/app/id6448449756), [SkillCandle](https://www.hunted.space/product/skillcandle) |
| Duolingo / Apple rings / savings apps | Streaks and rings drive return visits; freezes soften resets | Loss aversion pushes people to keep a streak even when stopping is right; harsh reset makes users quit | Steal: rings for "tests honestly closed". Never streak on wins | [RevenueCat guide](https://www.revenuecat.com/blog/growth/gamification-in-apps-complete-guide), [Mind the Product](https://www.mindtheproduct.com/designing-streaks-for-long-term-user-growth/), [Olson Zaltman](https://www.olsonzaltman.com/zfiles/freaky-streaks) |
| Deflated Sharpe (Bailey, Lopez de Prado) | Shows why best-of-N tries inflates results; honest N is the whole trick | Needs trial count to be true | Steal: "try #N" on every verdict (already in v1); full ledger visible | [SSRN 2460551](https://papers.ssrn.com/abstract=2460551), [LuxAlgo explainer](https://www.luxalgo.com/library/concept/deflated-sharpe-ratio/) |

Not found by search (NOT_IN_DATA): independent usability studies of any backtest tool; vectorbt `Portfolio.stats` layout. Command that would find the second: read `vectorbt` docs page `Portfolio.stats`.

## 2-5. Superseded by the OPERATOR OVERRIDE block at the top of this file (2026-10-25): the five-tab plan (Tests/Result/Replay/Quiz/Compare), the proposed result schema, the ranked build list, the cut list and the OURS defaults they rested on are history; what ships is accuracy, selectable params per layer plus conditions, performance, visualization and user friendly, in that order, on the local desk (`desk.py` + `page.html`).

## 6. Operator inputs, one line each (Doctor list 2026-10-25)
| # | Input | Where covered |
|---|---|---|
| 1 | See all this in the simulator, built first | Whole page; build list item 1-2 |
| 2 | Everything tested now is on it | Tests tab catalogue + backfill (item 2); mockup shows 5 cards |
| 3 | Backtests and thought experiments, past and future | Same card shape with a THOUGHT EXPERIMENT chip; mockup card "What if fees were zero?" (real: +0.072 R gross) |
| 4 | Light, powerful, fun, dashboards, app look, ROI | Sections 2 and 4; ROI hero first |
| 5 | Research what people do | Section 1 |
| 6 | "5 layers match exactly" in plain words | Compare tab, real T09 numbers (30 DEV days, live code replayed vs test code): 5 layers exact (turn of candle 2,880/2,880, session momentum 30/30, cvd absorption 99/99, sr flip 130/130, failed msb 17/17); volume_fvg 0 of 24, side flipped; RSI trades events never tested (101 of 240 match); funding_cvd_fade tested on 15m but runs on 1h (0 of 34); escalation misses 68 of 96 (15m); exits differ for every layer (one live 1%/2%/8-bar bracket, 94% timer exits). Source: T09_live_parity.md sections 1, 4, 5 |
| 7 | One screen, click a test, settings in plain words | Tests cards -> Result with "How it was set up" table |
| 8 | Visual replay: entry, stop, target, exit, what was considered | Replay tab with 3-step "considered" list; candle chart with stop/target lines only on the local desk (charts.py) because the public repo holds percent distances, not prices; build item 4 |
| 9 | Why it failed, plainly | Verdict banner sentence + fee bars + level-family table |
| 10 | Click and Run later, local, logged, sealed windows | Disabled "Run" button in the mockup; real only in the local JIS-NB desk; hosted page never runs; ledger row per run; VALIDATION/HOLDOUT locked. Left for after items 1-6 |
Standing rules: every setting carries a SOURCED/OURS label (all OURS until a quote is attached; fees SOURCED); failed tests list first and red; fee-net only; percent distances only.

## 7. Doctor follow-up (a)-(d), 2026-10-25
- (a) **Audit / thought-experiment card kind.** Result JSON `kind: "audit"|"thought_experiment"|"backtest"`; audit fields `{claim, method, finding, verdict, example:{text, figure?}}`; same card, chip AUDIT. Mockup: T09 live-parity audit, opens in place (details tag). Source: `research/dsa_backtest_audit_2026-10-16/T09_live_parity.md`.
- (b) **Parity per layer, plain words, with real T09 numbers** (Compare tab): 5 layers match entry for entry (turn of candle 2,880/2,880; session momentum 30/30; cvd absorption 99/99; sr flip 130/130; failed msb 17/17); fib pullback 108/117; rsi events 101/240; escalation 28/102; funding cvd fade 0/34; volume fvg 0/24 side flipped. Exits differ for all (one live bracket). Counts are sums of T09 section 4 rows. Schema: `parity:[{layer, entries_match:[x,y], exits_same:bool, note}]`.
- (c) **Parameters in plain words with SOURCED/OURS**: Result tab table (done in the previous ship). Schema `settings:[{name, plain_value, label, quote?}]`; all OURS until a quote is attached, fees SOURCED.
- (d) **Replay reasons as text**: entry reason, stop, target, exit reason on every replayed trade (public page, no prices). Schema addition per trade: none needed for levels (derived from family + r); other studies add `why:{entry,stop,target,exit}` text.
Scoreboard now counts T09 audit and the zero-fee experiment as FAILED (3 failed).
