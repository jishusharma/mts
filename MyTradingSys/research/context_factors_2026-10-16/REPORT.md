# Point-in-time context factors: can our backtests rebuild what a BTC trader sees at the decision moment? (2026-10-16)

Session: JIS-NUC worktree `jis-nuc/context-factors`, claim `context-factors`, Opus 5.5 (the prompt named Fable 5.1).
No VALIDATION or HOLDOUT bar read (loader and both builds refuse bars >= 2024-07-01). No outcome column exists in this
folder. No production or live-path code changed. Files: CONTEXT_FACTORS_SPEC.md (definitions), context_asof.py (two
builds), test_context_asof.py (16 tests), COUNTS.md, trials.csv, PRE_REG.md, ANGLES.md, this file.

## 1. Verdict

**Leakage: the context a trader uses can be rebuilt point in time, and it now is.** Seven factor families (24 factor
columns) are built twice, a replay that is only given bars[0..t] and a vectorised build. On every DEV decision hour
(19,729 hours x 2 sides = 39,458 rows) the two agree exactly. All 8 planted look-ahead leaks (one per factor, two for F7)
are caught by the truncation test. Truncation on real DEV bars at 40 boundary and mid-bucket hours gives 0 mismatches. The checks that
look at the market rather than the code (trader's eye on 12 hours, hand arithmetic, red team) found **5 spec errors**.
None was a leak. Each was a place where the first definition did not match what a trader sees: a stop ladder that widened
a too-tight stop, today's high/low missing as levels, a one-hour-old VWAP and session range counted as levels, and an
engulf rule decided by 0.1-USD tick gaps. All five are fixed in both builds.
**Counts: DEV is too short to test any single factor.** At a plausible filter effect of 0.20 R, a decisive test needs
1,242 independent days per bucket and side; DEV has 821 decision days in total, and 0 of 86 buckets qualify. The PRE_REG
therefore refuses every per-factor cell and reads one powered cell: the operator's whole context as one composite
(1,010 events on 456 days, both sides pooled), against a context-matched baseline. That cell clears the power gate only
if the full context is worth at least about 0.35 R per trade (operator decision D1).

## 2. Factors kept and dropped

| family | kept (PIT-proven: replay == vectorised, leak caught) | dropped and why |
|---|---|---|
| F1 side-aware levels | 8 layers: prior D/W high-low, developing session high-low, prior-day VA (Tom + Fabio), prior-week VA (Tom + VP), Krown 4h pivot zones (>= 2 turns), session/weekly VWAP, round 1,000s, 4h BB mid (operator) | Malkan: no price-level rule in his transcripts (his 40/60 are RSI) |
| F2 confluence and quality | distinct layers in +-0.5 ATR(1h); age; touches; first touch vs retest | counting trader names (double-counts the shared VA computation) is kept only as a variant |
| F3 daily-candle stop ladder | armed flag, D/12h/8h widths, stop timeframe, cost in R | - |
| F4 candle patterns (D/12h/8h/4h) | engulf (operator rule), outside, inside, pin, three in a line, doji; alignment with the side | classic engulf kept only as a variant (tick noise) |
| F5 Bollinger state (1h, 4h) | walk / break / re-enter / inside; confidence; veto | - |
| F6 phase | A weekly SMA10 + slope (chosen), B 30 d trend + 90 d range (variant), intraday ER | - |
| F7 additions | volatility regime, 4h squeeze, session, weekend, approach speed, sweep-and-reclaim, HTF alignment, funding | open interest (archive starts 2025-09), liquidations and news (no DEV data), footprint at the level (klines only) |

## 3. Top findings (counts and definitions only)

1. **Levels are everywhere.** With eight layers, 90 % of DEV hours (17,802 of 19,729 long, 17,851 short) have a same-side
   level within 1 ATR(1h). "At support" selects nothing on its own. Only confluence, quality or the stop rule narrow it.
2. **The daily-candle stop is wide and cheap.** In the tradeable ledger the stop is the prior D candle in 86-87 % of events
   (median 1.66-1.69 %, cost 0.083-0.085 R). 26-27 % of cooled-down events get no valid stop: mostly price is already
   beyond yesterday's extreme or every candidate is under the 0.56 % cost floor. A minority are wider than a day's
   ATR at every rung (COUNTS.md ladder table).
3. **"Phase" is not one thing.** The weekly definition and the daily one agree on 45.8 % of events. 607 events are weekly
   markdown but daily accumulation, and 582 are weekly markup but daily distribution. The phase is also confounded with the
   year: weekly markdown has 1,440 events in 2022 (Apr-Dec) and 50 in 2024H1. A phase factor cannot meet a per-year sign rule.
4. **The operator's band "dance" is not a band walk.** In his own words the price "takes support at this lower band ...
   bounces between the lower and the center line" (MAL-BB-RSI-4060.md:106). His warning is about shorting into that
   bounce, not into a walk. The prompt's walk veto touches 126 decision events; his reading would touch 701.
5. **The classic engulf is noise on 24/7 BTC.** Half of all daily candles open 0.1-4.4 USD away from the previous close,
   so "opens at or below the previous close" is a coin flip. The operator's close-past-open rule is used instead.
6. **Same-day overlap.** Many events share one candle: the D candle is the same for every hour of the day, and
   one wick shows as a pin on 12h, 8h and 4h at once. The counts therefore use distinct days, not events, as units.
7. **pit_levels shipped while this ran** (`research/pit_levels_2026-10-16/`, not edited here). Overlap: both builds use
   the same delays (pivot after i+n closes, period levels from the next period, closed buckets) and agree with its
   PIT_CONTRACT. Differences:
   - its profiles use 1m bars, mine 5m;
   - its stop floor is 0.40 % (TOM_ON_BTC.md:24), mine 0.56 % (cost <= 0.25 R, OURS);
   - its PRE_REG's power gate counts events (n = 1,835) at z = 2.8 against zero; mine counts days with a Holm-adjusted z
     against a matched baseline. Its inventory and leakage tests were not reused because they were not on fast-track at the start.
8. **eur_low_us_sweep_2026-10-14 read the HOLDOUT, for real.** The VERDICTS.csv row is not a parse error. RESULT.md:8 and
   :21 report HOLDOUT 2026 side by side, and its "VAL 2025" second half is also holdout under the project split
   (2025-07-01 ..). Any later study that uses 2025-07 .. 2026-09 must log that exposure.

## 4. Operator decisions (default applies until you overrule it)

| # | decision | default |
|---|---|---|
| D1 | The composite cell is powered only if your whole context (levels + confluence + daily candle + no band walk + phase) is worth >= ~0.35 R per trade before any trigger. Run card `context-composite-dev-read`? | **Yes, run it as frozen.** If you think the context is worth less, park the card; nothing else is lost |
| D2 | Band veto: walk only (prompt) or any close at/below the lower band in the last 2 bars (your "dance")? | Keep the walk veto in the frozen composite; your reading is the first variant for the next PRE_REG |
| D3 | Single factors cannot be tested on 821 DEV days. Extend DEV backwards with Binance USD-M BTCUSDT 1m klines 2019-09 .. 2021-12 (free public data, about 850 more days)? | **Yes**: one HAIKU card to fetch and checksum them, then per-factor PRE_REGs. Even then only the largest buckets reach 1,242 days |
| D4 | One power convention for every PRE_REG: units = distinct UTC days, z adjusted by Holm for the verdict-ledger count. The pit_levels PRE_REG uses events at z = 2.8 | **Days + Holm** from now on; the pit_levels card runs as frozen, but its RESULT should print the day count and day-unit MDE beside its own |
| D5 | A completed candle pattern can be undone by the partial candle (2024-05-10: yesterday's bull engulf, given back by 15:00). Add an "invalidated by the partial candle" flag? | No change now; revisit only if a candle factor gets a powered test |

## 5. Next step
Card `context-composite-dev-read` (lane SONNET, READY): one outcome read of the composite under PRE_REG.md, then
`verdicts.py add`. If D3 is accepted, add a HAIKU card for the 2019-2021 data first. Every per-factor question waits for
that data.

## 6. After the run and the second engine (2026-10-17, session context-compare-close)

What happened since: the card ran (RESULT.md: INCONCLUSIVE, 241 of 1,010 C events matched, 164 days < 387); a V2 PRE_REG
widened the control pool (974 events / 452 days); an independent audit said FIX-FIRST (stop comparability, realised-MDE
rule); D3 added DEV_EXT 2020-2021. The same prompt also ran on Fable 5.1 (`research/context_factors_pit_2026-10-16/`,
COMPARISON.md there). I checked its Opus-side numbers against this folder (1,010 / 456, 241 / 164, -0.137 R,
974 / 452, 63 vetoed per side); they match. Its Fable-side counts (e.g. 4 of 14 cells powered) were not recounted here.

**What both engines agree on (robust):** the context rebuilds point in time; "at a level" alone selects nothing (90 % /
94.5 % of hours); no single factor is testable on DEV in day units; candle patterns at a level are rare; the
eur_low_us_sweep HOLDOUT read is real.

**What depends on the definition:** band-walk veto (2 % of my events, 26 % of Fable short episodes), the phase object
(weekly SMA slope vs daily pivots), the ladder width (1 x ATR(D) vs 2.5 % of price). One correction to COMPARISON.md s.3:
its "D in 86-87 % (Opus) vs 59 % (Fable)" compares ledger events with all grid rows; on comparable rows my D share is
82-83 % for C and 87-88 % for the at-level pool (fix-1 draft counts), so the gap is smaller than that line suggests.

**The composite cannot get a decisive DEV verdict (counts only, `counts_v3.py`):**

| design | matched events / days | median stop C vs controls (long, short) | reachable verdicts |
|---|---|---|---|
| V2 pool (as frozen) | 974 / 452 (reproduced) | 2.086 vs 1.560 %, 2.165 vs 1.670 % (gap 25.2 %, 22.9 %) | INCONCLUSIVE only: PASS needs mean net_R of C > 0 (V1 printed -0.137 R on the same trades); FAIL is forbidden by the >25 % stop-gap rule |
| V2 pool + stop caliper (control stop within 1/1.25 .. 1.25 x the C stop, OURS) | 241 / 165 | 1.561 vs 1.487 %, 1.759 vs 1.645 % (4.7 %, 6.5 %) | INCONCLUSIVE only: 165 < 393 days |

With DEV_EXT the caliper design would reach about 310 days (estimate at the same rate, not counted), still under 393.
So card `context-composite-v2-dev-read` is on hold (OPERATOR_DECISIONS D8); D1-D5 are logged as D7. The descriptive
fact stays: the whole composite averaged -0.137 R per trade all-taker on DEV (1,010 trades), so nothing here argues for
more composite work.

**What changes going forward:**
1. `sync.py start <slug>` now prints the trunk's study folders and task cards whose names hold every slug word, so a
   second session on the same task sees the first one at boot, not at ship time (test_sync.py).
2. Every PRE_REG counts power in UTC days with Holm (D4, logged); a factor that the two engines define differently gets a
   cross-engine agreement count before any verdict (Fable card `context-factors-one-run`, step 1).
3. A PRE_REG must check that the verdict it can reach is not fixed in advance (PASS blocked by an already-read gate, FAIL
   blocked by a comparability rule) before a card is spent on it.
4. Next context work is the Fable chain (Q87 audit, then Q88 one run, 4 of 14 cells powered); this folder's composite
   chain is closed on DEV.
