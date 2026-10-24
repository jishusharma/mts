# Krown audit — gx-krown-audit — 2026-10-24

Scope: krown_core.py, krown_events.py, krown_context.py, params JSON, all five test modules, and FIRE_COUNTS_BTC_DEV.md. Read-only production audit; only this directory contains new scripts/report. No git, sync, pushing, code/test/card edits, validation or holdout reads. Python ran with `-B` to avoid bytecode writes.

Reproduce all executable checks from the repo root:

```powershell
python -B MyTradingSys/research/gpt_burn_2026-10-24/gx-krown-audit/audit.py
```

The script prints complete structured summaries, counts before reporting, and runs mutations only in memory. Its fire-count subprocess is exactly `python -B MyTradingSys/backtest/layers/krown/run_fire_counts.py`, with no output-path argument; it captures and parses the entire stdout. Historical counts are a comparison artifact, never the independent mathematical oracle.

## Findings

1. **HIGH — Entire S1/S2/S3/S4/S7 emissions can disappear without failing any test.** `MyTradingSys/backtest/layers/krown/test_krown_events.py:31`, `:36`, `:55`; emission path `MyTradingSys/backtest/layers/krown/krown_events.py:72`. Enabled-mode checks are type/schema, pooled non-emptiness and equality of the implementation against its own prefixes. They do not require a positive or negative hand-derived event fixture for any of these five setups. Reproducer: `audit.py`, `mutations.delete_S1` through `delete_S7` (five named mutations, not S5/S6). Each independently removes that setup from build_events and still returns **72 run, 0 failures, 0 errors, 0 skips**. The independent 320-bar fixture actually has S2=13, S3=10, S4=7; deleting those is non-vacuous. Its S1/S7 counts are zero, highlighting why targeted positive fixtures are needed. Recommendation: per-setup positive, negative and boundary examples with expected event index/side derived from the specification.

2. **HIGH — MACD signal-line failure is invisible to the suite.** `MyTradingSys/backtest/layers/krown/test_krown_core.py:236`, implementation `MyTradingSys/backtest/layers/krown/krown_core.py:323`. The test unpacks `(m, s)` but only checks `m`; no signal-line number, warmup, bearish cross or S9 momentum contribution is pinned. Reproducer: `audit.py`, `mutations.MACD_signal_all_None` replaces the signal with all None, suppressing every MACD cross, while **72/72 tests pass**. For a separate numerical fixture, FORMULAS 21.6 gives EMA SMA seeding; for closes 1..6 with fast=2, slow=3, signal=2, line[2..5]=0.5 and signal[3..5]=0.5. The current test would not reject a missing signal even on that simple case.

3. **LOW — The zone-count test only pins an upper bound.** `MyTradingSys/backtest/layers/krown/test_krown_core.py:71`. It asserts `len(zones) <= 5`, so returning one zone can pass, despite silently losing valid non-overlapping ranked zones. Reproducer: `audit.py`, `mutations.cap_zones_at_one` applies `zones_from(... )[:1]` and **all 72 tests pass**. FORMULAS 21.1 permits up to five ranked zones; add a constructed multi-zone fixture with exact membership/order and overlapping-zone exclusions. This finding concerns missing regression coverage, not a claim that current code always returns one zone.

4. **LOW — Weekly completeness accepts a duplicated day plus a missing day.** `MyTradingSys/backtest/layers/krown/krown_context.py:84`, `:92`. The docstring promises all seven daily bars, but the guard checks only row count. Reproducer: `audit.py`, `weekly_completeness`: Monday-based offsets `[0,0,2,3,4,5,6]`, closes `[100,101,102,103,104,105,106]`. Expected complete weeks **0**; actual **1**. A duplicated Monday can replace Tuesday and generate a false weekly high/low/close context. Check the seven exact timestamps, as aggregate_4h already does for hours. This is malformed-input resilience; the observed clean synthetic tape and current fire-count rerun are not evidence of actual duplicate contamination.

5. **LOW — Provenance coverage stops at JSON labels and misses additional defaults.** `MyTradingSys/backtest/layers/krown/test_krown_core.py:15`, `MyTradingSys/backtest/layers/krown/params/krown_params.json:2`, `MyTradingSys/backtest/layers/krown/krown_context.py:34`, `:281`, `:292`, `:302`. JSON has **47 entries = 22 SOURCED + 25 OURS; 0 missing/invalid labels and 0 blank sources**. However, no JSON SOURCED entry itself supplies a literal trader quote plus file:line; it supplies a ledger id and paraphrase. The table below resolves these pointers independently. Outside JSON, middle-third thresholds, significance alpha, multiplicity default and power quantile lack an explicit SOURCED/OURS label. The JSON-only test would not detect their absence and verifies no quote. Reproduce by parsing all 47 JSON entries and inspecting the cited lines (the table generation script checks each quote location). Label these extra research choices OURS with exact references. Numeric selections 5 from 3–5 zones and 3 from a 3–5-bar horizon are supported endpoints, but selecting an endpoint remains an implementation choice; record it explicitly, as already done for bbwp_low=30.

No CRITICAL findings. HIGH findings above are demonstrated test blind spots, not observed production formula failures or live-trading failures. Layer remains descriptive/default OFF.

## Parameter inventory

All JSON entries appear below with exact declaration line. `P` means `MyTradingSys/backtest/layers/krown/params/krown_params.json`. `E` means `MyTradingSys/research/krown_ta101_2026-10-13/extracts/`. Quotes are excerpts from the checked-in trader extracts, not fetched external material. Leash count 3 is available only in that extract's **analyst stated-mechanics summary** at line 190; it is not a literal trader quote there. Its ledger source KR-M06 repeats the claim, so literal-word provenance remains incomplete for that count.

| Parameter | Value | Declared label | Declaration | Quote or declared judgement |
|---|---|---|---|---|
| `enabled` | false | OURS | P:4 | flag-gated default OFF (KROWN_LAYER_SPEC s5) |
| `zone_k` | 3 | OURS | P:5 | bars each side of a swing; KR-L01 gives no number, grid {2,3,5} |
| `zone_min_turns` | 2 | SOURCED | P:6 | “price turned at least twice” — E`extract_qEfES84jwwo.md:65` |
| `zone_lookback` | 250 | OURS | P:7 | pivots older than this many bars are not ranked (KR-Z18 'recent' is not defined) |
| `zone_max` | 5 | SOURCED | P:8 | “three to five zones maximum” — E`extract_qEfES84jwwo.md:74` |
| `zone_mature_tests` | 3 | SOURCED | P:9 | “more than three times” — E`extract_qEfES84jwwo.md:196` |
| `swing_tol` | 0.01 | OURS | P:10 | 'about the same' range tolerance (KR-L10 gives no number) |
| `vol_sma` | 20 | SOURCED | P:11 | “A 20 period simple moving average” — E`extract_UqAvU1loT_k.md:68` |
| `vol_mult` | 2 | SOURCED | P:12 | “two or more times the average” — E`extract_UqAvU1loT_k.md:86` |
| `vol_half` | 0.5 | SOURCED | P:13 | “50% of the average” — E`extract_6aA-P4Gvhrc.md:130` |
| `vol_slots` | 7 | OURS | P:14 | same-slot baseline arm: weekday slot for 1d (spec C5/C10) |
| `vol_slot_prev` | 8 | OURS | P:15 | same-slot baseline arm: previous weeks averaged |
| `tops_vol_sma` | 30 | SOURCED | P:16 | “average of the past 30 days” — E`extract_7IxfsuD2wCM.md:64` |
| `bbwp_basis` | 7 | SOURCED | P:17 | “basis moving average length seven” — E`extract_kcMnnQr1VFg.md:100` |
| `bbwp_lookback` | 100 | SOURCED | P:18 | “look back period 100” — E`extract_kcMnnQr1VFg.md:100` |
| `bbwp_mult` | 2.0 | OURS | P:19 | band multiplier not stated (KR-Q01); percentile formula defined in FORMULAS.md 21.5 |
| `bbwp_high` | 85 | SOURCED | P:20 | “above 85% higher or more” — E`extract_kcMnnQr1VFg.md:109` |
| `bbwp_low` | 30 | OURS | P:21 | KR-Q02 gives 25-35; 30 picked, grid {25,30,35} |
| `bbwp_confirm` | 50 | SOURCED | P:22 | “back above 50th percentile” — E`extract_kcMnnQr1VFg.md:540` |
| `hammer_wick` | 0.6 | OURS | P:23 | wick-to-range ratio for a big wick (KR-C03 gives none) |
| `hammer_close_pos` | 0.7 | OURS | P:24 | close in the top (hammer) or bottom (star) 30 % of the range (KR-C03 'closes strong') |
| `doji_body` | 0.1 | OURS | P:25 | body ratio for a doji (not stated) |
| `confirm_horizon` | 3 | SOURCED | P:26 | “over the next three to five candles” — E`extract_8MvxK_nxO-0.md:94` |
| `crows_bars` | 3 | SOURCED | P:27 | “three down bars from the high” — E`extract_7IxfsuD2wCM.md:222` |
| `ma_fast` | 21 | SOURCED | P:28 | “a 21 and a 55 EMA” — E`extract_-NXzJs5JRks.md:92` |
| `ma_slow` | 55 | SOURCED | P:29 | “a 21 and a 55 EMA” — E`extract_-NXzJs5JRks.md:92` |
| `ma_long` | 200 | SOURCED | P:30 | “a 200 simple moving average” — E`extract_-NXzJs5JRks.md:92` |
| `ma_leash` | 5 | SOURCED | P:31 | “your five EMA” — E`extract_-NXzJs5JRks.md:194` |
| `leash_n` | 3 | SOURCED | P:32 | “about three closes not connecting” — E`extract_-NXzJs5JRks.md:190` (analyst summary, not trader quote) |
| `rsi_period` | 14 | OURS | P:33 | KR-S02 does not state the period |
| `rsi_bull` | 60 | SOURCED | P:34 | “below the 60 read” — E`extract_INOCBmqQupc.md:153` |
| `rsi_bear` | 40 | SOURCED | P:35 | “above a 40 read” — E`extract_INOCBmqQupc.md:151` |
| `macd_fast` | 12 | OURS | P:36 | MACD periods not stated (KR-P01 names the cross only) |
| `macd_slow` | 26 | OURS | P:37 | MACD periods not stated (KR-P01) |
| `macd_signal` | 9 | OURS | P:38 | MACD periods not stated (KR-P01) |
| `range_n` | 20 | OURS | P:39 | range lookback not stated (KR-R01) |
| `range_width_max` | 0.25 | OURS | P:40 | max (top-bottom)/mid for a range; compression thresholds not stated |
| `range_edge` | 0.2 | OURS | P:41 | edge band share of the range; KR-R01 says edges only, no width |
| `coil_recent` | 5 | OURS | P:42 | bars in the coil window (not stated) |
| `coil_max` | 0.7 | OURS | P:43 | coil score below this = compression (not stated) |
| `tops_window` | 3 | OURS | P:44 | 'a few bars' (KR-P01), grid {2,3,4} |
| `tops_need` | 3 | SOURCED | P:45 | “three of the four align” — E`extract_7IxfsuD2wCM.md:20` |
| `s1_vol_mult` | 2 | SOURCED | P:46 | “two or more times the average” — E`extract_UqAvU1loT_k.md:86` |
| `s2_vol_mult` | 1.0 | OURS | P:47 | S2 volume above average (spec); 'discernible' threshold grid {1.0,1.25,1.5} |
| `s8_recent` | 5 | OURS | P:48 | bars to look back for BBWP <= low (S8) |
| `s8_break_n` | 10 | OURS | P:49 | bars of range the S8 candle must break (not stated) |
| `s7_vol_lookback` | 100 | OURS | P:50 | 'biggest volume bar' window for S7 (KR-V07 gives none) |

Additional configurable defaults and hardcoded research choices:

| Location | Parameter/value | Label audit |
|---|---|---|
| `MyTradingSys/backtest/layers/krown/krown_core.py:110` | bbwp mult=2.0 | OURS via bbwp_mult / FORMULAS 21.5 |
| `MyTradingSys/backtest/layers/krown/krown_core.py:313` | RSI bull=60, bear=40 | SOURCED via rsi_bull/rsi_bear quotes above |
| `MyTradingSys/backtest/layers/krown/krown_events.py:67` | fire ceiling=1.0 per 10 bars | OURS preregistration criterion (docstring names PRE_REG_KROWN item 3); not a trader number |
| `MyTradingSys/backtest/layers/krown/krown_context.py:25` | LATENCY_MS=60000 | explicitly OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:26` | ATR_N=14 | explicitly OURS; plain SMA definition is separately sourced to FORMULAS 12 |
| `MyTradingSys/backtest/layers/krown/krown_context.py:27` | SMA_LONG=200 | explicitly OURS naive baseline; distinct from sourced MA indicator |
| `MyTradingSys/backtest/layers/krown/krown_context.py:28` | RET_N=20 | explicitly OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:29` | FRESH_LOOKBACK=6 | explicitly OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:30` | FRESH_FROM=30 | explicitly OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:31` | FRESH_TO=50 | SOURCED via BBWP confirm quote above |
| `MyTradingSys/backtest/layers/krown/krown_context.py:32` | Z_NEAR_ATR=0.5 | explicitly OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:33` | EDGE_FRAC=0.2 | explicitly OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:34` | MID_LO=1/3, MID_HI=2/3 | **unlabelled**; design reference without OURS/SOURCED; audit classification OURS |
| `MyTradingSys/backtest/layers/krown/krown_context.py:239` | d2 bbwp_high=85 | SOURCED inherited from bbwp_high quote above |
| `MyTradingSys/backtest/layers/krown/krown_context.py:281` | alpha=0.05 | **unlabelled**; audit classification OURS statistical design choice |
| `MyTradingSys/backtest/layers/krown/krown_context.py:292`, `:302` | sd_r=1.5, rho=0.1 | explicitly OURS in mde_slope docstring; mde_mean inherits conventions |
| `MyTradingSys/backtest/layers/krown/krown_context.py:292`, `:302` | m=1, power_z=0.84 | **unlabelled defaults**; audit classification OURS multiplicity/power design |
| `MyTradingSys/backtest/layers/krown/krown_core.py:365`, `:367`; `MyTradingSys/backtest/layers/krown/krown_context.py:270` | edge epsilon=1e-9 | **unlabelled numerical tolerance**, audit classification OURS; shifts exact edge boundaries |

Units (milliseconds per day/hour/week), category codes, EMA alpha algebra, loop indices and bisection precision are implementation constants rather than separately tuned trading parameters. API inputs such as `n`, `period`, `tol`, `near_atr`, `edge`, `horizon`, `window`, `need` inherit their caller's documented JSON/constants; externally supplied overrides need their own provenance. This inventory covers the three requested modules, not every runner-script setting.

Usage caveat: `confirm_horizon` and `crows_bars` are labelled in JSON but build_events never reads either key. Confirmation exists as the standalone confirm_index helper; events use pattern bars directly. Three-crows detection is fixed at three bars. Do not interpret these configuration entries as event-engine controls. This is an API/documentation limitation; no assumption that every pattern must await confirmation was added to FORMULAS 21.

## Independent numbers and look-ahead checks

The numerical checks are calculated from FORMULAS sections 12 and 21, not copied from production output:

- BBWP basis=2/lookback=3, closes `[10,10,12,11,15,15,14]`: pair widths = `4*abs(b-a)/(a+b)`; counting prior widths strictly below current gives `[None,None,None,None,100,0,100/3]`. Production matches.
- RSI period 2, `[10,11,10,12]`: seed gain/loss `0.5/0.5` gives 50; next `1.25/0.25` gives `100-100/6 = 83.3333333333`. Production matches.
- EMA(5), `[1,2,3,4,5,6]`: SMA seed 3, alpha 1/3, next 4. Production matches.
- SMA ATR(3), highs `[10,11,12,11]`, lows `[9,9,10,9]`, closes `[9.5,10.5,11.5,10]`: true ranges `2,2,2.5`, average `13/6 = 2.1666666667`. Production matches.

Fixture-style truncation (audit.py `prefixes`):

| Output | Fixture | Comparisons | Mismatches |
|---|---|---|---|
| Complete event list through each cutoff | 320 OHLCV bars, deterministic walk seed 71 | 320 | 0 |
| All daily rows through each cutoff, including weekly trend and zones | 240 daily bars, seed 17 | 240 | 0 |
| All 4h rows through each cutoff | Same 240-price tape at 4h opens | 240 | 0 |

Every prefix from length 1 through full length was tested, comparing **all** prefix rows/events, including tags. Swing confirmation and weekly completion boundaries are included. A deliberately next-close-peeking row is detected at **239/239** eligible cutoffs. Existing join tests also pass the strict `available_at < decision_ts` boundary and planted open-key/forward-row leak controls. No look-ahead was found on these fixtures; finite prefix tests are not a universal proof, and no actual-data context truncation was run.

The full existing suite reports **72 tests, 0 failures, 0 errors, 0 skips**, including artifact/recall-document checks. All seven independent in-memory mutations also report 72/0/0/0; no mutations persist on disk. Artifact checks test schemas/timestamps/arithmetic and required prose; recall-table checks test citation syntax and internal row/summary consistency. Neither substitutes for recomputing indicator values or true recall from raw examples. These distinctions explain how the passing suite coexists with the demonstrated blind spots.

## Fire-count reproduction

All **54/54** requested DEV month files are present: 24 CSV months (2020–2021) and 30 ZIP months (2022–2024-06). `run_fire_counts.py` exited 0 and rebuilt **1643 full daily bars** from 2020-01-01 through 2024-06-30 and **234 full Monday-start weekly bars**. Parsed **65 fields = 1 coverage header + 46 detector rows + 18 setup rows** from both complete outputs, comparing every cell in each detector/setup row. **0 differing fields**, including events, rates and long/short splits. Original report: `MyTradingSys/backtest/layers/krown/FIRE_COUNTS_BTC_DEV.md:3`; daily setup table starts at :34 and weekly table at :75. A match establishes reproducibility of the current implementation, not independent validity of every historical detector count.

| Setup | Daily events | Daily long/short | Weekly events | Weekly long/short |
|---|---|---|---|---|
| S1 | 0 | 0/0 | 0 | 0/0 |
| S2 | 61 | 32/29 | 11 | 6/5 |
| S3 | 23 | 8/15 | 0 | 0/0 |
| S4 | 24 | 15/9 | 0 | 0/0 |
| S5 | 12 | 7/5 | 0 | 0/0 |
| S6 | 41 | 25/16 | 8 | 5/3 |
| S7 | 2 | 2/0 | 0 | 0/0 |
| S8 | 51 | 32/19 | 3 | 3/0 |
| S9 | 29 | 0/29 | 1 | 0/1 |

Counts sum to **243 daily events** and **23 weekly events**. Independent rate arithmetic: daily S2 `61*10/1643 = 0.371272`, weekly S2 `11*10/234 = 0.470085`; both match rounded output. Neither timeframe exceeds 1 event per 10 bars per setup. Daily S1=0 is reproducible; it does not establish correct recall. The historical report explicitly discloses Binance volume/venue ambiguity and limited DEV years; this audit makes no edge or P&L claim.

Result: Fire counts reproduce exactly (65/65 fields); 800 prefix checks pass; 72 tests pass but seven broken-code mutations survive; provenance/default and weekly-completeness gaps remain.
