# What the operator points at in his chart screenshots

Digest, 2026-10-29. Descriptive only: no edge claim, no advice. No prices, sizes or margins are kept here (public repo).

## 0. Coverage (read this first)

| Source | What was read | Status |
|---|---|---|
| Shot store (`shot.py list`) | 315 shots landed, 197 are charts; every chart classification note read | SOURCED |
| Store date range | 2026-10-02 to 2026-10-29 (about 4 weeks) | the "3 months" ask is NOT_IN_DATA before 10-02 |
| Counts below | keyword hits in the classification note (written by the reading session, not the operator), so a shot counts as "mentioned" only if the note names the pattern | counts are floors |
| `OPERATOR_DECISIONS.md` | keyword search, two operator-voice entries read in full (d-live-trading-dashboard-built-live, d-layer-relations-concepts-first) | SOURCED |
| `tools/live_aid/REQUIREMENTS.md` | R01-R10 quotes (operator voice, 10-28) | SOURCED |
| Session transcripts | 887 .jsonl files scanned for user text; 6,792 candidate user messages, about 1,200 distinct operator-like after dropping templates and pastes; about 15 read in full for quotes | partial, see counts |
| `archive/operator_inbox/2026-10-09_to_2026-10-11.md` | grep only: it is an external-LLM research handoff, not the operator pointing at charts | no pointers taken from it |
| `research/live_market*` | directory does not exist | NOT_IN_DATA |
| `PICTURE_AND_PLAN.md`, `BACKTEST_CANDIDATES.md` | read for context only | SOURCED |
| Image content itself | not re-viewed; only the saved notes | NOT_IN_DATA |
| DOM / order-book pointers | 0 shots mention it; 1 transcript message only mentions "divergences in depth" (unrelated) | NOT_IN_DATA |

Dates with chart shots: 10-02, 10-05, 10-07, 10-09, 10-12, 10-14, 10-15, 10-16, 10-17, 10-18, 10-19, 10-23, 10-26, 10-27, 10-28, 10-29 (16 days). "Dates" counts below are out of these.

## 1. Recurring relationships he points at

Shots = chart shots whose note names the pattern. Dates = distinct days. Quotes are verbatim (his dictation is lightly mangled by voice).

| # | Pattern | Layers involved | Shots / dates | Verbatim operator phrase | What he wanted done |
|---|---|---|---|---|---|
| 1 | Price vs RSI divergence (bull and bear, regular and "hidden"), on 1m to 12h | price, RSI14 (+SMA, 40/60 lines), WT_CROSS_LB, StochRSI | 19 / 6 (notes); about 16 transcript messages on 11 days | "we need divergence checks in each time frames and a way to understand the roll over between timeframes" (10-09); "check divergence everywhere" (10-28) | Detect it on every timeframe, see how it rolls between TFs, test whether MTS finds the same pivots he drew; later he said confirmations will be done in the simulator, not by chat |
| 2 | Price vs CVD: price falls while CVD rises (buying visible) or price makes a new high while CVD falls | price, CVD (Binance and aggregated), volume | 23 / 8 | "price was falling CVD was increasing - verify this" (10-14); "this whole idea of buying at every push on the CVD ... is wrong" (10-15) | Verify the claim, measure how accurately the code reads it. He corrected the reader when it over-generalised |
| 3 | CVD vs net delta disagreement (one visible, the other not; CVD up while net delta and OI fall) | CVD, net delta, OI, volume | in the 23 above; about 11 transcript messages on 9 days | "why we see open interest coming down and net delta going down ... But CVD is going up, right? So what it means" (10-23) | Explain what each layer says about the same candle, then learn "which layer tells us what" |
| 4 | OI direction vs price: OI up into a drop (new positions), OI down into a rally (short covering), OI flat base then step | OI, price, volume, net longs/shorts (new) | 23 / 6 | "is this a squeeze" (note, 10-28); price-up/OI-down divergence marked on 15m (10-18) | Classify squeeze / covering / new positions; backtest pivot and reversal odds per timeframe |
| 5 | Net longs / net shorts (new and open) and top-trader long/short (accounts, positions, ratio) | positioning panes, OI, price | 25 / 6, mostly 10-28 | "how these layers ... combine with the net shorts in account and the top traders ... how they react to each other during a phase of a Bitcoin" (10-28) | Describe co-movement per phase, especially around the US open; facts and concepts first, no edge hunting yet. Also "watch closely 1, 3, 5 min" top-trader data |
| 6 | Liquidation heatmap (cross-timeframe) | liquidation layer, price | 11 / 1 (all 10-28, one timeframe sweep 1h to 1d plus 5m) | "now we have to find out how much of this is actually useful - worth trusting" (R08); "see its diff timeframes to compare what played out at lower time frames since last weeks" (R09) | Judge squeeze and support from it; keep a running trust ledger of what its bands did when price reached them |
| 7 | Bollinger "dance": price walks the lower or upper band, then breaks at a known time (US open); band touch with a cushion | BB(20,2), midline, RSI | 41 / 9 mention BB | "Bollinger band dance, and there is no hard set rule that every candle must touch the band. But if it is close enough, it is fine ... some cushion" (10-14) | Research the dance online, define it with tolerance, backtest it, add BTC 24/7 settings |
| 8 | Midline rejection / engulf and RSI-40/60 range shift (RSI rejected at 60 or at its SMA, held at 40) | BB mid, RSI, SMA of RSI | in the RSI group, 57 RSI-mentioning notes / 8 dates | "RSI 40-60 layer ... specialized with Malkan and it will only calculate divergence based on what Malkan says" (10-27) | Keep the RSI layer to Malkan's rules; hidden divergence is a separate confluence source, not part of that layer |
| 9 | VWAP test: price rejected at, holding below, or not touching VWAP; VWAP plus session volume profile / POC | VWAP, session VP, POC rays | 20 / 6 | "asks VWAP research" (note, 10-19, 1m after US open) | Research how price reacts to VWAP; no operator sentence found beyond the notes |
| 10 | Support, resistance and marked levels (weekly low, round number, swept top, flat white line, pre-open tops) | price, session levels, VP/POC | 28 / 8 | "when will you short! on some good resistance with confluence from other indicators and divergences" (10-15); "help me to take profit here. Based on what kind of support you see" (10-28) | Say where a short/take-profit has confluence; record which level patterns to compare for backtests |
| 11 | Footprint and large-trade bubbles (per-bar delta, absorption) | footprint, large trades, net delta | 18 / 3 (10-07, 10-26, 10-28) | "the new order-flow layers" (note, 10-28, shown after research); "what clarity it brings" (note, 10-26) | Read per-bar delta against the same bar on the standard chart; cross-check 3m vs 5m footprints |
| 12 | WaveTrend (WT_CROSS_LB, "wavefront" by voice): above the red line then down through green = buy; coiling | WaveTrend, RSI, price | 18 / 4 (10-28 and 10-29 mostly) | "when it comes down at green, it is a buy there" (R10, 10-28); "if 15m tells a better story with WaveTrend" (note, 10-29) | Build a WaveTrend module and put it on the live dashboard; settings still an open question |
| 13 | Timeframe stories: the same moment on 1d to 1m, 1m-15m vs 4h-1D agreement, bias per TF, "grandfather / father" ladder | all layers across TFs | 60 / 8 (sets of 5 to 12 images on 10-12, 10-15, 10-18, 10-26, 10-27, 10-28) | "read 15m/30m/1h/2h together" (note, 10-27); "how bias changes per timeframe" (note, 10-18); "whether LTF levels break depends on HTF momentum" (note, 10-15) | One bias per TF and how they agree; consistency check across TFs |
| 14 | Context-dependent behaviour (the same readings differ by regime and session) | OI, CVD, net delta, price | about 4 transcript messages; marked windows 10-18 | "The behavior must be consistent for the context. When the context changes, the behavior changes" (10-18) | Read every candle between his vertical lines; backtest per day, per session, per context |
| 15 | His hand-drawn structure: ABCD swings, pitchforks, falling support line, ladder channel | price only | 6 / 4 (12h 10-15, 1m 10-14 and 10-16, 1w 10-18) | "ABCD arrows" and "stacked pitchforks" (notes) | Read the structure; a pitchfork layer was asked for via Gemini |

## 2. Patterns by how often he returns to them (shots, not messages)

Biggest recurring: multi-timeframe sets (60), RSI (57), BB (41), in-trade/short context (41), levels/POC/VP (28), positioning panes (25), OI (23), CVD (23), VWAP (20), divergence (19), WaveTrend (18), footprint (18), heatmap (11). INFERRED: the weight moved from RSI and divergence (10-09 to 10-19) to positioning panes, heatmap, footprint and WaveTrend (10-26 to 10-29) as he started trading live.

## 3. What he says he needs while IN a trade

All from 10-28 unless dated. Direct quotes first, then the dashboard reading.

- "enjoyment of small trade when should I get out of this position or when should I add to it? What are the term layers saying right now?" (10-28; "term" is voice for Tom's layers, INFERRED). Needs: exit-or-add call per layer.
- "help me to take profit here. Based on what kind of support you see." Needs: support levels near his take-profit, with the factors behind them (he said the first answer "did not come out right").
- "i need like a trading aid now when i am into positions" (R01). Needs: one screen while holding.
- "so now when us opens we can look into getting into positions based on each layer" (R02). Needs: per-layer entry look at the US open.
- "all latest inputs" (R03): all layer readings current on one page.
- "strict narrow dashboard that suits my style - we will add functions step by step" (R05); "highly performance oriented" (R06).
- Liquidation context kept building so he can trust it (R08); timeframe heatmap of what played out lower (R09).
- Watch top-trader and net longs/shorts closely at 1, 3, 5 minutes (shot note, 10-28 13:49Z).
- Is it a squeeze, where is the liquidation map, where is price relative to VWAP and the band (10-28 notes).
- INFERRED from the image-only stream on 10-28 (about 35 one-minute shots in about 6 hours with no text): he wants a repeated live read of the same stack (price/BB, OI/CVD/net delta/RSI, positioning panes, footprint) after each spike, and a note when CVD diverges from a new price high or low.
- Mode he asked for: observation only, no signals (decision 10-28, the dashboard decision).

## 4. Things he said NOT to do

- No candle-only TAKE/SKIP marking; ask him only to confirm indicator readings (memory, 10-28).
- Do not hunt for an edge yet; first the simple facts and correlations as concepts (10-28).
- He will verify divergence and confirmations in the simulator with clear parameters, not on screenshots (10-28).
- Do not repeat questions he already answered (10-28).

## 5. Gaps

- NOT_IN_DATA: shots before 2026-10-02; the images themselves; a standing log of live reads (`research/live_market*`); any DOM/order-book pointer.
- Counts come from reader notes, not from his own words, so single messages may mention more patterns than the table shows.
- Operator transcript text is dictated; terms are mangled ("Crown" = Krown, "Mercon" = Malkan, "wavefront" = WaveTrend, "term" = Tom).
