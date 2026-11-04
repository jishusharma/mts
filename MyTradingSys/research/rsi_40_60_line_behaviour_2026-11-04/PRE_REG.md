# PRE_REG: how RSI14 behaves around the 40 and 60 lines (hold / break / range), the cushion, what changes the odds, and two plays (frozen 2026-11-04, before any outcome was read)

Order: `d-rsi-40-60-line-behaviour-1104` in `MyTradingSys/system/OPERATOR_DECISIONS.md` (operator, voice): when RSI comes from above and rests on 60 does it bounce, break or chop into a range; what do the other timeframes do at that moment; what is the higher-timeframe bias and the BTC phase; "wait for the break" or "take the bounce"; how big a cushion (clearance band) around the line.
Code: `study.py`; tests `test_wiring.py`. Folder checked new on `origin/fast-track` (nearest: `bear_proxy_context_tuning_2026-11-04`, whose per-cell threshold tuning this replaces as the answer to the question).
Counts (events and distinct days only, no outcome) are in `count_dev.csv`. Every tuned parameter in this file is **OURS**; the 40 and 60 lines themselves are the SOURCED Malkan levels.

## Data and split (same as `bear_proxy_context_tuning_2026-11-04/PRE_REG.md`)

- Binance SPOT klines (not futures, no splice), BTCUSDT + ETHUSDT, read from `F:/MTS/Dumps/backtest/spot_2017` at 1h / 4h / 1d. **12h = built from 1h**: bucket = floor(t / 12 h), kept only when all 12 hourly bars are present (closed, complete; a bucket with a missing hour is dropped). **1w = `tf_resample.resample(1d, "1w")`** (closed weeks only). Pooled across both symbols, clustered by UTC day.
- DEV = event-bar closes 2017-08-01..<2024-07-01. VALIDATION = 2024-07-01..<2025-07-01, read once, picks only (the script refuses a second run). HOLDOUT (2025-07-01+) is never loaded (loader end = window end). Events whose outcome window does not fit before the window end are dropped.
- RSI = Wilder RSI14 of the bar closes (`rsi_core`; FORMULAS.md s1, checked against an independent implementation in `test_wiring.py`). A bar's RSI is known at its close = bar open + bar length. Every cross-timeframe read is as-of: the latest bar whose close time is <= the event close time.
- Cost 0.14 % round trip (`research_kit`, SOURCED). Gaps in the spot archive are not filled ("N bars" = bars present).

## Event (OURS)

For TF in {1h, 4h, 12h, 1d}, line L in {40, 60}, cushion c in {1, 2, 3, 5} RSI points: band = [L - c, L + c] (edges inside). Zone of a bar = above (RSI > L + c), inside, below (RSI < L - c).
**Event** = bar k whose RSI is inside the band while bar k-1 was outside it. **Side (origin)** = the zone of bar k-1 (above / below) = where the last close outside the band was. A bar that jumps across the whole band never enters it and is not an event.

## Outcome (OURS)

Window N bars per TF (also the holding period of the plays): **1h 24, 4h 18, 12h 14, 1d 10**. Scan bars k..k+N; `crossings` = number of changes of the side of RSI vs the line L itself (above/below L, counting from bar k-1 whose side is the origin; RSI exactly on L keeps the previous side), up to the exit bar. The exit bar = the first bar j > k outside the band.

| Outcome | Rule |
|---|---|
| RANGE (chop) | an exit bar exists and crossings >= 2 (the line was crossed back and forth) |
| HOLD | exit bar on the origin side and crossings < 2 (= 0): RSI left the band back where it came from |
| BREAK | exit bar on the far side (closes beyond L by more than c) and crossings < 2 (= 1) |
| RANGE (inside) | no exit bar within N bars: RSI stayed inside the band |

RANGE = chop + inside; both parts are reported. Classification bar e = the exit bar (RANGE-inside: bar k+N).
**Forward price return** (recorded for every event, gross %): entry = OPEN of bar e+1 (the bar after the classification), exit = CLOSE of bar e+N; fee-net = signed gross - 0.14.
**Plays** (real-time executable: the exit bar's close is known before the entry):
- **take the bounce** = enter at the first HOLD confirmation (bar e), in the direction RSI left the band: came from above -> long, from below -> short.
- **wait for the break** = enter at the BREAK confirmation (bar e), in the break direction: came from above -> short, from below -> long.
Chop and inside-range events have no play. Both plays trade the direction in which RSI leaves the band; they differ only by whether it leaves on the origin or the far side.

## Event context columns (all as-of the event bar close)

- **Higher-TF bias** = RSI14 of the next TF up above / below 50 (1h->4h, 4h->12h, 12h->1d, 1d->1w); exactly 50 or missing = no bias (excluded from that context only).
- **Confluence** = how many of the other three TFs have their last closed RSI14 inside the same band [L - c, L + c] (0 to 3). Context values: 0, 1plus.
- **Regime** = `research_kit.regime_tag` primary (Malkan weekly+monthly 60/40 with daily SMA200 side, SOURCED) bull / range / bear, as of 00:00 UTC of the event day. **Phase** = age of the SMA200 side in daily closes at that instant: `fresh` <= 60, `mature` > 60 (OURS, as the sibling; `research_kit.phase_tag` classes W1/H/R belong to tf_break events and do not exist here). Events with no regime (first ~15 months) are kept in ALL and dropped from regime/phase contexts. The bear regime is expected empty (the Malkan bear gate fires 0 weeks on BTC); it is reported and capped, not dropped.
- Context values used for plays: ALL, htf_up, htf_down, confl_0, confl_1plus, reg_bull, reg_range, reg_bear, ph_fresh, ph_mature (10).

## Cushion pick (OURS, DEV only, no return used)

Per TF x line x side, over c in {1, 2, 3, 5}: **separation(c) = |hold share - break share|**, shares of all events (so a cushion that mostly makes RANGE scores low). Pickable only with n >= 100 events and >= 40 distinct days; highest separation wins, ties go to the smaller c; none pickable = null. The picked cushion is also labelled hold-dominant or break-dominant by the sign of hold - break.
**Random-walk benchmark** (not a trial; for reading only): the same event/outcome rules on one synthetic iid-normal-return series of 200 000 bars per TF (seeds fixed in `study.py`), reported beside every real base rate, because an event starts at the band edge nearest its origin and a pure random walk therefore already "holds" more than it breaks.

## Reports on DEV

1. Table 1: hold / break / range (chop, inside) rates and n per TF x line x side x c, with the benchmark, and the picked cushion.
2. At the picked cushion: the same rates per context value; Table 2: **hold-rate difference with a day-clustered 95 % CI** (percentage points, pooled per TF over its picked line x side cells): HTF bias aligned with the bounce direction vs opposed (aligned = bias sign equals the origin side), confluence >= 1 vs 0, fresh vs mature, bull vs range.
3. Plays: per picked TF x line x side x context (10) x play (2): n, days, fee-net mean, day-clustered 95 % CI.
**Play pick (DEV only):** best fee-net mean among cells with n >= 30 and >= 20 days, at most one cell per TF x line x side, **at most 6 cells**. Only those are tested, once, on VALIDATION.

## Trial count (stated up front)

DEV evaluations: behaviour rates 4 TF x 2 L x 2 side x 4 c = **64**; context splits at the picked cushion 16 cells x 9 non-ALL values = **144**; Table 2 contrasts 4 TF x 4 = **16**; plays 16 cells x 10 contexts x 2 plays = **320**; total **544**. The cushion pick (64 rows) and the benchmark add no evaluations. VALIDATION: at most **6** play tests (Holm family m = 6, unpicked slots count as p = 1); the cushion stability rates on VALIDATION are descriptive.

## Power gate (count-only, `scripts/dev/prereg_gate.py` formula, m = 6, cost 0.14, unit %, n = distinct DEV days, max plausible gross 0.30 %)

sd of the N-bar return (OURS): the sibling's 10-bar sds (1h 1.9, 4h 4.0, 1d 10) scaled to a per-bar sd (1h 0.60, 4h 1.26, 1d 3.16; 12h 2.2 by sqrt-time between 4h and 1d) times sqrt(N): **1h 2.9, 4h 5.4, 12h 8.2, 1d 10.0**.
Result (`count_dev.csv`): the event counts alone already **BLOCK on all 64 cells** (event days 920-1956 on 1h, 328-938 on 4h, 128-376 on 12h, 65-213 on 1d; smallest MDE 0.22 on 1h vs 0.16 allowed). A play cell is a subset of its event cell, so **every play cell is BLOCK**. Consequence, fixed now: the plays are exploratory; the verdict ceiling for every play is **INCONCLUSIVE (underpowered)**, whatever VALIDATION shows. The behaviour tables are descriptive rates (no return, no test) and are not gated; their CIs are reported.

## Verdict rule (fixed now)

A play is DEFAULT only if its DEV power gate is PASS and VALIDATION is fee-net with a day-clustered 95 % CI lower bound > 0 and Holm p < 0.05 (m = 6). Powered but not DEFAULT = FAIL. Blocked = INCONCLUSIVE. `rules.json` holds per TF x line x side: the picked cushion, its hold/break/range rates and `default_play` (null unless DEFAULT). The 40/60 lines and the d-bear-proxy-1104 / Malkan gates are unchanged by this study.

## What the result will say

RESULT.md: plain-words summary (max 5 bullets) first, then `Regime mix:` for the DEV window, Table 1 (base rates at the picked cushion + benchmark), Table 2 (what changes the odds), Table 3 (plays on VALIDATION with the verdict), the trial count and the caveats (spot not futures, overlap with sibling DEV windows, 2 symbols).

## Context
Regime: events are crossed with the Malkan gate (`research_kit.regime_tag`, SOURCED) bull / range / bear as a context column; the study is ungated otherwise because the question is how the line behaves in each context.
Phase: OURS SMA200-side-age phase (fresh <= 60 daily closes / mature) as a context column; `phase_tag` W1/H/R does not apply to RSI-line events.
Session: none, because session tags (OURS) were not requested by this order.
Entry: plays enter at the open of the bar after the exit-bar close that classified the event (HOLD for the bounce, BREAK for the wait), exit at the close N bars later (N per TF, OURS).
