# SPEC: how the favourite indicators are used, then grouped with the analysts' layers (cards tvfav-usage-*, indicator-map-1107)

Operator 2026-11-07 (voice): "understand what is common in these indicators and what exactly people say, how to use them, what
LazyBear says, what articles have been written ... then apply the filter for crypto and Bitcoin ... then have these indicators
properly grouped together so that we understand where they are applied and what the context is ... volume is a layer, price is a
layer, time analysis is a layer ... a structured way of using the connected indicators is the key."

Builds on `research/tv_favorites_2026-11/FAVORITES_2026-11-07.md` (formulas SOURCED, proposed use OURS) and the engines
(adx, wavetrend, squeeze, vfi). Phase-first rule (11-06) stays: every indicator is a CONTEXT column, never a signal alone.

## Step 1: usage research, one Gemini card per indicator (lane CODEX, Gemini queue on the NUC, effort low)
Cards: tvfav-usage-wavetrend-1107, tvfav-usage-squeeze-1107, tvfav-usage-vfi-1107, tvfav-usage-adx-1107.
Output: `research/tv_favorites_2026-11/USAGE_<indicator>.md`, one screen, sections in this order:
1. Author's intent: WaveTrend = LazyBear's script notes + the original WT idea; Squeeze = LazyBear's notes + John Carter's TTM
   Squeeze (Mastering the Trade; "squeeze fires" = first grey/off dot after >= 6 on dots, trade in the histogram's direction, exit
   when momentum fades, the $1M claim is Carter's own); VFI = Markos Katsanos, "Using Money Flow to Stay with the Trend" (TASC
   June 2004: sign crossing 0, divergence vs price, 50-day smoothing for daily); ADX/DI = Wilder 1978 (20/25 thresholds, DI cross).
2. How people use it: 3 to 5 sources per indicator (TradingView script page comments count as one), each with a verified quote
   (`scripts/dev/verify_extract_quotes.py` exit 0; YouTube only through captions). State the timeframe and market each source used.
3. Crypto/Bitcoin filter: which uses survive 24/7 markets, funding-driven volume, and BTC's volatility; what the sources say fails.
4. Common pitfalls and the parameters people change (label SOURCED values; anything we would change is OURS).
5. One line "What it measures": momentum, volatility/compression, participation (volume), trend strength, or position in swing.
No verdict, no backtest, no code. Each file under 6000 bytes.

## Step 2: the map (card indicator-map-1107, lane SONNET, login B after its 11-08 reset or login A)
`MyTradingSys/system/INDICATOR_MAP.md`, built from the four USAGE files, FAVORITES, LAYERS.md and the analyst notes
(Tom: levels, LVN/POC, balance; Habib; Fabio sessions; CBP calls; Steve/CCU DI cross; the mts_bible cycle clock). Content:
1. Dimension table, rows = what is measured: price action, levels/volume profile, volume/participation, momentum, volatility/
   compression, trend strength, time/cycles/sessions. Columns: indicators that measure it (engine path or "none"), analysts who
   read it, the MTS layer id if one exists, TradingView favourite yes/no.
2. Role table per dimension: context (phase), setup (where), confirmation (go/no-go), with the current phase-first gate column
   it feeds (CENSUS M4, wick W2, volume M5, scenario_ledger).
3. Connected sets: for each setup family we run (cycle-bottom long, session trade, level test, range-to-range) the ordered read:
   context -> setup -> confirmation, naming the indicator or analyst for each slot, and what disagreement means.
4. Gaps: dimensions with no indicator or no analyst; indicators with no consumer (wiring_registry rule: producer needs a consumer).
5. Mechanism: every "X confirms Y" sentence in the map is also a `scenario_ledger.py add` row or a wiring_registry entry the same
   ship (feedback 11-04: a rule in a doc is not a mechanism). Test: `test_indicator_map.py` checks each engine in layers/ has a
   row and each row's engine path exists; fails on the pre-change tree.
Ship with `Result: <rows, gaps>` and `Next: END: operator reads the map; the first connected set goes to testnet-forward`.

## Never
No new trading rule, threshold or signal is invented here; thresholds stay the sources' (SOURCED) or are marked OURS and untested.
