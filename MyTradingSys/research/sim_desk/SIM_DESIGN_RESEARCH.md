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

## 2. What we need

**Light.** One HTML file, inline CSS and JS, no libraries, SVG charts written by hand. Mockup is 27 KB with 255 trades embedded (10 KB of that); budget 150 KB per page, 40 KB per result file. Percent distances and R only, no price files (repo is public). Leave out: candlestick libraries, 600 stats, logins, saved presets, live data, multi-asset, a chart library, any server call.

**Powerful: five views, in this order.**
1. **Tests** (catalogue as cards): name, one-line plain description, status chip (FAILED / NOT ENOUGH DATA / PASSED-DEV-ONLY / NO RESULT), net R, trades, dollars. Top: honest scoreboard (passed / failed / not enough / none yet).
2. **Result**: verdict banner first, then ROI hero, 8 KPIs, equity curve with play and scrub.
3. **Replay**: one trade at a time (date, side, level family, R, money after) plus last-40 bar strip. Local desk adds the real candle SVG for the same trade; the public page cannot.
4. **Quiz** ("would you take this?"): ten real trades, take or skip, reveal, scored against take-all.
5. **Compare**: two results side by side from the same schema (all ideas vs filled; test A vs B; later live vs backtest), before/after fees bar, precomputed-variant slider (stop type K1..K5), level family table with n.
Verdict and why: one sentence the operator can act on ("even +0.10 R is ruled out"), never "power 31%" (REVIEW_FABLE.md section A).

**Fun, kept honest** (rules, not decoration):
- Replay and curve animate; the curve turns red below the start line and the banner is sticky. Animation never smooths or skips losses.
- Quiz scores your picks against "take all ten" on the same trades; end screen states the rule's true average. Streak = rounds played, never wins.
- Badges count tests *closed honestly* (FAILED counts the same as PASSED). The scoreboard shows 0 passed as plain fact.
- Rings/progress only for "validation runs spent" (1 per idea), never for P&L.
- Anything that favours the user (best trade, best family) always sits beside n and the all-trades number.

**ROI shown plainly.** First number on the Result tab: "1,000 USD -> X on DEV after fees". Sizing is OURS: 1% of current money at risk per trade (1R = 1%), compounding. Levels ladder: 1,000 -> **715** (-28.5%), worst drop in money -35%, 255 trades, -0.119 R net per trade, 41% wins, worst losing streak 15 (filled-only, computed this session). Fees shown as their own line (0.111 R). Per-trade money is path-dependent; state the sizing under the number.

**Look and feel.** One design system = v1's tokens (already live): `--bg --card --ink --mute --line --good --bad --acc --warn`, system font, 14 px body, 12 px caps labels, 14 px radius cards, 8/12/16 spacing, dark and light via `:root` variables with `prefers-color-scheme` plus a manual toggle. Phone: single column, bottom tab bar, 16 px gutters, KPI strip 2x4. Desktop: max 980 px, cards in 2 columns. Reference apps to imitate:
- **QuantConnect results banner**: stats strip on top of one equity curve.
- **Apple Fitness / Activity**: one big number, rings, calm colours, one thing per card.
- **Robinhood-style portfolio card**: big money number, one line chart you can scrub, red/green by sign (we keep the colour, drop the confetti).

## 3. Proposed result schema (`results/<id>.json`, sim-v2 adopts or replies)
`{id, title, plain, status: FAILED|NOT_ENOUGH_DATA|PASSED_DEV|NO_RESULT, why, try_no, window:[from,to], fees:{gross_r,fee_r}, n_ideas, n_filled, mean_net_r, ci:[lo,hi], win_rate, max_dd_r, worst_streak, trades:[[date,side,family,r],...], variants:[{label,mean_net_r,n}], families:[{name,n,mean_r}]}`. Dollars are computed in the page from `trades` with the shown sizing rule. The catalogue is `results/index.json` (id, title, status, mean_net_r, n_filled). Counting rule: `n_filled` is the headline trade count; ideas that never filled go in `n_ideas` only.

## 4. Ranked build list (understanding per hour, rough hours for a Sonnet builder)
| # | Item | Hours | Why this rank |
|---|---|---|---|
| 1 | Result tab: banner + dollars hero + KPI strip + equity with scrub/play | 4 | Does the one job: judge a test without text. Prototype done |
| 2 | Standard result JSON + catalogue cards (Tests tab), backfill past tests | 5 | Makes it the home of every test; unlocks all other tabs |
| 3 | Compare tab (two results, fee bars, family table, variant slider) | 4 | Shows why a test failed (fees, no-fills, one bad family) |
| 4 | Replay tab with trade strip; local-only candle SVG per trade (v1 charts.py) | 4 | "See an example"; public page shows R strip only |
| 5 | Quiz | 3 | Fun and teaches that gut picks lose; low risk because scored vs take-all |
| 6 | Dark/light polish, phone pass, scoreboard badges | 2 | Cheap, high feel |
| 7 | Live vs backtest compare (needs live mirror export) | 5 | Valuable later; depends on a data feed that does not exist |
Total 1-6: about 22 h. Do 1 and 2 first; they are the product.

## 5. What NOT to build
Candle chart library; order entry or paper trading; parameter sliders that *run* anything in the page (only precomputed variants); P&L leaderboards; win-streak badges; confetti or sound; rolling Sharpe, Monte Carlo, 600 stats; accounts; a server for the public page; raw price files in the repo; "best family" or "best variant" highlights without n.

## DECISION (OURS) defaults taken
1% risk sizing for dollars; filled trades are the headline count; PASSED only after the one validation run; mockup uses ROADMAP counts for the RSI cards (no decimals invented) and marks WaveTrend "no result yet".

## 6. Operator inputs, one line each (Doctor list 2026-10-25)
| # | Input | Where covered |
|---|---|---|
| 1 | See all this in the simulator, built first | Whole page; build list item 1-2 |
| 2 | Everything tested now is on it | Tests tab catalogue + backfill (item 2); mockup shows 5 cards |
| 3 | Backtests and thought experiments, past and future | Same card shape with a THOUGHT EXPERIMENT chip; mockup card "What if fees were zero?" (real: +0.072 R gross) |
| 4 | Light, powerful, fun, dashboards, app look, ROI | Sections 2 and 4; ROI hero first |
| 5 | Research what people do | Section 1 |
| 6 | "5 layers match exactly" in plain words | Compare tab "same entries / same exits" per layer; mockup shows "not measured yet" (no live export exists, nothing invented); build item 7 |
| 7 | One screen, click a test, settings in plain words | Tests cards -> Result with "How it was set up" table |
| 8 | Visual replay: entry, stop, target, exit, what was considered | Replay tab with 3-step "considered" list; candle chart with stop/target lines only on the local desk (charts.py) because the public repo holds percent distances, not prices; build item 4 |
| 9 | Why it failed, plainly | Verdict banner sentence + fee bars + level-family table |
| 10 | Click and Run later, local, logged, sealed windows | Disabled "Run" button in the mockup; real only in the local JIS-NB desk; hosted page never runs; ledger row per run; VALIDATION/HOLDOUT locked. Left for after items 1-6 |
Standing rules: every setting carries a SOURCED/OURS label (all OURS until a quote is attached; fees SOURCED); failed tests list first and red; fee-net only; percent distances only.
