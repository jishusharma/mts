# Rumers (@the.rumers) backtest harness: written BEFORE any rule is known (Lab_Guy, 2026-11-01)

Status: no captions, no extracts on trunk (`git ls-tree origin/fast-track MyTradingSys/research/rumers_2026-11-01/` empty at
2026-11-01 ~10:30Z; caption guard `BLOCKED until 2026-11-01T12:14Z`). Nothing here is a Rumers rule. Every number in this
file is OURS. Per-rule pre-regs are filled from this skeleton once RUMERS_EXTRACT_1/2.md pass `verify_extract_quotes.py`.

## 1. Fixed for every Rumers rule (not changeable per rule)
| Item | Value | Source |
|---|---|---|
| Data | Binance BTCUSDT 1m klines, `Dumps/backtest/raw_1m_2022/BTCUSDT-1m-YYYY-MM.csv` (local, gitignored); sha256 of each month file recorded in the run output | bigtrade/bigmoves.py `SOURCES` |
| DEV window | 2022-04-01 00:00Z .. 2024-06-30 23:59Z (entries only; exits may run past the end) | coordinator brief, card goal |
| VALIDATION / holdout | untouched; no look, no plot, no count | LESSONS_DIGEST s.2 |
| Bars | 1m resampled with `layers/timeframe/tf_resample.resample`; a signal uses CLOSED bars only; entry = next bar open | bigmoves.py docstring convention |
| Fees | `BINANCE_TAKER * 2` from `backtest/fees.py` (0.10 % round trip); stress readout with `research_kit.TAKER_RT_PCT` (0.14 %) | fees.py:36, research_kit.py:21 |
| Same-bar stop and target | stop counted first | C26_PRE_REG.md convention |
| Stats | per rule: n, hit-rate, mean net R, day-clustered SE (`research_kit.cluster_mean_se`), two-sided p (`norm_p_two`) | research_kit.py |
| Family-wise | Holm over ALL rules run on DEV, m fixed in the pre-reg before the first run (`research_kit.holm(p, m)`) | research_kit.py:127 |
| Trial ledger | `TRIAL_REGISTRY_rumers.csv` in this folder (study,variant,run_utc,split,data_source,description,status), one row per rule BEFORE its run | scripts/dev/trial_ledger.py |
| Look-ahead check | re-run each rule with the signal shifted one bar LATER; a result that gets clearly worse is expected, a result that needs the unshifted bar to exist is not; and a shifted-EARLIER run (uses the future) must look better or the code is suspect | coordinator brief |
| Pass bar (DEV) | Holm-adjusted p < 0.05 AND mean net R > 0 AND n >= the rule's power-gate N. A DEV pass is a hypothesis for ONE pooled VALIDATION trial, never a promotion | LESSONS_DIGEST s.2 |

## 2. Per-rule pre-reg skeleton (copy one block per rule, fill, commit, THEN run)
```
### R<k>: <one-line name>
quote: <caption file>:<line>  (from RUMERS_EXTRACT_x.md, verify_extract_quotes exit 0)   -> SOURCED
timeframe:         <value>  SOURCED <file:line> | OURS (why)
trigger:           <exact closed-bar condition>                     SOURCED | OURS
direction:         long / short / both (mirror)                     SOURCED | OURS
entry:             next bar open (market) | limit at <price> (state fill rule: touch vs trade-through)
stop:              <rule>  -> stop distance in % (median expected)  SOURCED | OURS
target / exit:     <rule> | time stop <h>                           SOURCED | OURS
filters:           <trend / session / volume>                       SOURCED | OURS
claimed by video:  hit-rate <x> / RR <y> / "works best when ..."   (NOT_IN_DATA if the video gives none)
0a cost check:     fee in R at the median stop = 0.10 / stop% ; <= 0.25 R required (PRE_REG_TEMPLATE 0a)
0e power:          expected DEV n (from a count-only pass, no P&L) ; N for 80 % power (s.3) ; GO / BLOCKED
look-ahead plan:   +1 bar shift, -1 bar shift
trial row:         added to TRIAL_REGISTRY_rumers.csv (variant = R<k>_v1)
kill:              one redesign max; a second fail closes the rule
```
A count-only pass (how many triggers, no outcome) is allowed before freezing, to fill 0e; it reads no returns.

## 3. Power gate (from `power_table.py`, fees.py costs; win p / RR shapes are OURS until the videos give theirs)
| stop % | cost R (fees.py) | cost R (stress 0.14 %) | win p | RR | gross R | net R | N for 80 % power | power at n=30 / 100 / 300 / 1000 | MDE net R at n=30 / 100 / 300 / 1000 |
|---|---|---|---|---|---|---|---|---|---|
| 0.3 | 0.33 | 0.47 | 0.40 | 2.0 | +0.20 | -0.13 | never (net <= 0) | n/a | 0.75 / 0.41 / 0.24 / 0.13 |
| 0.3 | 0.33 | 0.47 | 0.55 | 1.0 | +0.10 | -0.23 | never (net <= 0) | n/a | 0.51 / 0.28 / 0.16 / 0.09 |
| 0.3 | 0.33 | 0.47 | 0.33 | 3.0 | +0.32 | -0.01 | never (net <= 0) | n/a | 0.96 / 0.53 / 0.30 / 0.17 |
| 0.5 | 0.20 | 0.28 | 0.40 | 2.0 | +0.20 | +0.00 | never (net <= 0) | n/a | 0.75 / 0.41 / 0.24 / 0.13 |
| 0.5 | 0.20 | 0.28 | 0.55 | 1.0 | +0.10 | -0.10 | never (net <= 0) | n/a | 0.51 / 0.28 / 0.16 / 0.09 |
| 0.5 | 0.20 | 0.28 | 0.33 | 3.0 | +0.32 | +0.12 | 1928 | 6% / 10% / 20% / 52% | 0.96 / 0.53 / 0.30 / 0.17 |
| 1.0 | 0.10 | 0.14 | 0.40 | 2.0 | +0.20 | +0.10 | 1695 | 7% / 10% / 22% / 58% | 0.75 / 0.41 / 0.24 / 0.13 |
| 1.0 | 0.10 | 0.14 | 0.55 | 1.0 | +0.10 | +0.00 | never (net <= 0) | n/a | 0.51 / 0.28 / 0.16 / 0.09 |
| 1.0 | 0.10 | 0.14 | 0.33 | 3.0 | +0.32 | +0.22 | 574 | 10% / 22% / 53% / 96% | 0.96 / 0.53 / 0.30 / 0.17 |
| 2.0 | 0.05 | 0.07 | 0.40 | 2.0 | +0.20 | +0.15 | 753 | 9% / 18% / 42% / 90% | 0.75 / 0.41 / 0.24 / 0.13 |
| 2.0 | 0.05 | 0.07 | 0.55 | 1.0 | +0.10 | +0.05 | 3108 | 6% / 8% / 14% / 36% | 0.51 / 0.28 / 0.16 / 0.09 |
| 2.0 | 0.05 | 0.07 | 0.33 | 3.0 | +0.32 | +0.27 | 381 | 12% / 30% / 70% / 100% | 0.96 / 0.53 / 0.30 / 0.17 |

What it means (power for ONE test at 5 %; with Holm over m rules the first critical z rises from 1.96 to about 2.81 at
m = 10, so the N column grows about 1.7x):
- Stops at or under 0.5 % on BTC die on fees unless the video's real edge is above about 0.3 R gross; a scalp rule there is BLOCKED
  before running unless the claimed hit-rate x RR says otherwise.
- A 27-month DEV window gives a 1h/4h swing rule perhaps 50-300 fills: that only detects net edges of about 0.3-0.5 R. Such
  rules will mostly read "underpowered", never "no edge" (PRE_REG_TEMPLATE item 10).
- Only frequent rules (15m and below, ~1000 fills) with a stop of 1-2 % can detect the +0.1-0.2 R edges that are plausible.

## 4. What our existing code can already express (by module; verify the exact function on first use)
| Rule family (typical YouTube-TA wording) | Existing code | Can test |
|---|---|---|
| Swing high/low, "liquidity above the high", sweep and reclaim | `eagle_eyes_picture_2026-10-28/failed_retest_takeout.py` (pivot +-W, retest, take-out), `layers/cryptocred/cc_stop_sweep.py`, `bigtrade/bigmoves.py` (pivots, legs) | YES, once W and the near-band are fixed |
| Support/resistance flip, retest of a broken level | `layers/cryptocred/cc_retest.py`, `cc_structure.py` | YES for mechanical levels (pivots, session/weekly highs-lows); NO for hand-drawn zones |
| Session / day / week highs-lows, opens | `layers/session_levels/session_levels.py`, `layers/wlow_bounce/detector.py` | YES |
| Market structure HH/HL, break of structure, change of character | `layers/cryptocred/cc_structure.py`, `cc_htf_count.py` | YES with a pivot width fixed as OURS; the video's own swing choice is a chart read |
| Trend via moving averages, "above the 200" | `layers/timeframe/tf_resample.py` + `layers/krown/krown_core.py` | YES |
| Trendline break | `layers/trendlines/trendline_core.py` | PARTIAL: our auto-trendline is not the analyst's drawn line (class C9) |
| Pitchfork / fib-style channels | `layers/pitchfork/pitchfork_detector.py` | PARTIAL (anchor choice is a chart read) |
| Candle patterns (engulfing, pin bar, candle close beyond level) | `layers/turn_of_candle/turn_of_candle.py`; lab brief `layer_lab/briefs/gptb-candle-pattern-event-table.md` | YES for closed-form patterns; size thresholds are OURS unless quoted |
| RSI levels, divergence, RSI-MA | `layers/rsi/*` (rsi_core, rsi_divergence, malkan_40_60, rsi_ma) | YES |
| WaveTrend, stochastic, Bollinger | `layers/wavetrend/wavetrend.py`, `layers/kurisko/stoch_core.py`, `layers/krown/krown_core.py` | YES |
| Volume / CVD / absorption, volume profile | `layers/fabio/*`, `layers/tick/*`; aggTrades only for the months on disk | PARTIAL: 1m klines give volume, not aggressor side for all of DEV (NOT_IN_DATA where missing) |
| Open interest, long/short ratio | `layers/positioning/funding_cvd_fade.py`; `F:/MTS/data/binance_metrics/BTCUSDT-metrics-2022-01-01..2025-12-31.csv` (1461 daily files, 5m rows, local) | YES for OI on DEV; liquidations NOT_IN_DATA |

## 5. What I cannot test without the operator's own chart reads (say it plainly)
- Hand-drawn supply/demand or order-block zones: which candle "is" the zone is a judgment; our encoding is OURS and needs
  PRE_REG_TEMPLATE 0g (fires where he would mark it, checked on >= 3 of his dated charts) before any P&L.
- "Confluence", "clean structure", "strong rejection", "when it looks weak": no closed-form trigger; NOT TESTABLE until the
  video gives a measurable rule or the operator marks examples.
- Exits by discretion ("I'd trail it", "take some off"): a fixed bracket is a lower bound only (PRE_REG_TEMPLATE item 8).
- Anything on altcoins or other markets the video uses: tested on BTC only; transfer is stated as an assumption.
- A Gemini direct-view (no caption) rule: candidate only; it cannot be SOURCED (no verified quote), so its result is OURS end to end.

## 6. Testability verdict rubric (applied to each extracted rule)
- TESTABLE: trigger, direction, entry, stop and exit all closed-form from quotes or a stated OURS default; data on disk for DEV.
- NOT TESTABLE (missing: <piece>): a piece has no quote and no defensible OURS default, or the input is NOT_IN_DATA.
- NEEDS OPERATOR CHART: closed form exists only after a human marks levels/zones (0g).
