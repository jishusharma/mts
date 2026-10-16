# WaveTrend research method and MTS inspection

Research date: 2026-10-17. Baseline: origin/fast-track 1467c4e8; isolated worktree codex/wavetrend-research.

## Method fixed before external searching

Effectiveness requires reproducible dated samples and trade counts, chronological out-of-sample results, and fees, funding and slippage. Compare net expectancy and uncertainty with simple baselines; account for every tested setting and combination. Definitions, popularity and trader experiences identify hypotheses, not validated profitability; this is a conventional empirical testing problem, not a domain without a validation method.

Apply playbook Part I: T1 scholarly/institutional evidence, T2 disclosed reproducible studies or exchange documentation, T3 practitioner definitions/ideas. Marketing and unsupported profit claims are excluded from evidence of effectiveness. External reports are deliberately blind to MTS; only after collecting them does the synthesis rank applicability. Independent agents use GPT-6-sol and GPT-6-astra; the primary agent inspects MTS and reconciles findings. These are independent model viewpoints, not independent datasets or replications.

## MTS findings (read from current files)

- `items/T061_wavetrend_lazybear.md`: operator requested a separate layer; design records n1=10, n2=21, SMA signal=4, coefficient=0.015 and +/-60, +/-53 levels. Proposed path `backtest/layers/wavetrend/`, timeframes 5m/15m/1h/4h/1d. No strategy's exits, sizing or invalidation are fully specified by an indicator formula.
- `research/T065_LAZYBEAR_SURVEY.md`: prior survey identifies the linked Crosses publication as lonestar108's republication attributing LazyBear. A different proposed path, `layers/momentum/wavetrend.py`, needs reconciliation. Prior survey's popularity numbers are dated historical observations, not current review counts.
- `research/non_core_layer_audit_2026-10-12/REPORT.md`, `REVIEW.md`, ER-07: source snapshot, exact version/attribution, initialization, zero-deviation behavior, warm-up, cross equality and golden fixtures remain acceptance tasks. Neither that audit nor T061 demonstrates an edge.
- `system/control_room.json`: WaveTrend stage is parked; next text is "no new layers while Tom/Fabio are redefined". The present operator explicitly asks to get this layer going on priority; handoff must reconcile the stale park policy with this newer instruction instead of silently retaining an indefinite hold.
- Scoped current implementation searches under `src`, `scripts`, `backtest`, formula registry and verdict registry did not identify WaveTrend calculation or a named WaveTrend performance result. Ref filename inventory is recorded separately. This cannot exclude differently named or untracked remote-machine work.
- Old archive `research/fyi_archive/2026-09-18/02_consolidated_handoff_0456Z_0848Z.md` asserts MTF reduces false signals about 40% without a supporting study in that passage. Do not carry that number into a specification or expected result.

## Additional primary community observations

Verified 2026-10-17 via opened Reddit pages. T3, convenience sample, no OOS/cost disclosure; low confidence on predictive claims.

1. [Daytrading discussion, June 2024](https://www.reddit.com/r/Daytrading/comments/1dhe8ao/): participants favor WT divergence over RSI, mention MACD, and warn that crossover signals produce false signals on lower timeframes. One describes triangle patterns with order blocks/FVGs. This is firsthand testimony about use, not controlled evidence. Search rendering showed +12 for the divergence comment, +4 for the false-signal comment and +3 for the MACD reply; opened rendering hid scores. Record these as search-visible vote scores, never review counts or verified active users.
2. [TradingView community discussion, June 2025 with later replies](https://www.reddit.com/r/TradingView/comments/1lqg6ra/best_tradingview_indicators_3_years_experience/): a March 2026 reply describes WT crosses on 1h/4h/daily and lists VWAP, RSI and EMA 20/50/100 elsewhere on the chart. Search-visible reply score +1. It does not establish that all those indicators form one tested strategy. The discussion mixes trader suggestions and self-promotion; only the firsthand usage observation is retained.

No market-wide total of independent reviews can be inferred from these threads. Votes, script favorites, boosts, views and comment totals have different meanings; comments include questions and author replies. Deleted accounts, survivorship, overlapping forks and search ranking make sentiment unrepresentative.

## Implementation-risk and perp-specific sources

- [TradingView, Repainting](https://www.tradingview.com/pine-script-docs/concepts/repainting/), opened 2026-10-17: official platform documentation, T3 for platform semantics, high confidence. Open-bar crosses can disappear; unconfirmed higher-timeframe data and backward-plotted pivots can mislead historical tests. Use actual availability timestamps, not pivot plot timestamps. This says nothing about WT profitability.
- [Deribit, Funding Specifications](https://support.deribit.com/hc/en-us/articles/31424939178397-Funding-Specifications), opened 2026-10-17: T2 exchange documentation, high confidence for that venue only. Funding is a position-dependent cash flow with time exposure. A BTC perp test needs the actual venue/contract funding mechanism, not a universal eight-hour flat deduction.

For BTC implementation record traded contract, linear/inverse P&L numeraire, mark/index versus trade price, margin/liquidation assumptions, data gaps and funding timestamps. Obtain rules from the selected venue; leverage cannot turn negative unlevered expectancy positive. These are evaluation requirements proposed here, not LazyBear trading rules.
