# gx-rsi-lookahead audit

RESULT (2026-10-24): no pivot look-ahead found in regular divergence, long-range divergence, or the live divergence adapter on the tested closed-bar prefixes. One HIGH issue in the public MTF composer's documented open-time interface; one LOW forward-outcome/interface issue in retest rows. No CRITICAL findings. Wilder RSI matches independently evaluated FORMULAS.md section 1.

## Scope and controls

Read CLAUDE.md and the applicable status, announcements, entry/protocol, routing, and lessons documents. The task's explicit restrictions supersede sync/claim/ship and station-cleanup instructions. No git, sync.py, push, deployment, existing-code/test/card edits, or runtime/account data access. Only this report and `audit_truncation.py` were created under the authorized task directory. Python ran with `-B` and the script also disables bytecode writes. Existing test suites were not executed because some create temporary files outside the permitted directory; the new script is read-only and imports production functions without invoking their CLI entry points.

Parsed inventory: 22 Python files in `MyTradingSys/backtest/layers/rsi/` (12 implementation/driver files, 10 test files), plus `MyTradingSys/backtest/layers/alerts/live_rsi_divergence.py`. Inspected all implementation/driver signal paths; test files are supporting context, not independent numerical oracles. Inventory line/function counts are emitted by the script using AST parsing. Counts below come from parsed objects, not visual inspection of truncated terminal output.

Fixture: `MyTradingSys/backtest/layers/wavetrend/fixture_btcusdt_1h_dev_2022-01.csv`, 400 parsed rows, unique ascending hourly open timestamps 1640995200000 through 1642431600000. SHA-256: `17ca496f44cb858b7fa5416140f502aef90bdb6e9ededd35daca24dc89fe0efd`. Reads only open_time/high/low/close; no existing indicator/golden values are used as expectations.

## Findings

### F1 — HIGH: MTF gate accepts an unfinished higher-timeframe state under its documented input contract

Locations: `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:26` describes `times` as bar-open timestamps; `:42` through `:50` select the last time <= the signal timestamp without checking the bar's close; bull `:65` and `:66`, bear `:91` and `:92` use this lookup to admit signals. This contradicts the closed-HTF guarantee at `:14` through `:16` and `:30` through `:31`.

What is wrong: a weekly/monthly RSI regime calculated from that bar's eventual close becomes visible on its open date. This is future information even though the timestamp comparison itself is backward-looking. No pivots are involved.

Reproduce with the command below and inspect `mtf_open_time_repro`. Audit-owned bull RSI inputs [50,40,45], daily regimes BULL, tolerance 1, bullish candles on daily bars 10,11,12 produce a support signal on bar 12. Supply weekly BULL at open 10 (actual close 17) and monthly BULL at open 0 (actual close 30). Full open-labelled inputs produce **1** signal; inputs containing only HTF states actually available at the daily close 13 produce **0**. Mirror RSI [50,60,55], regimes BEAR, and bearish candles produces the same **1 versus 0** short-signal discrepancy. Both outcomes are asserted by the script. These are synthetic time units and independently specified gate availability, not market measurements.

Impact/qualification: unsafe public composer interface and misleading causality promise, not a demonstrated defect in the current backtest driver's gate. `run_rsi_backtest.py:220` through `:234` explicitly converts HTF opens to bucket-end availability times before composing, already compensating for this issue. Its daily query remains the daily OPEN timestamp, which is conservative relative to the close at which the daily signal is known; that can delay newly closed HTF states but does not introduce future data. No live divergence code calls this MTF composer.

Suggested correction for a future authorized fix: make the API explicitly accept availability/close timestamps, or require timeframe information and derive those timestamps internally; test open/close boundary cases for both directions.

### F2 — LOW: retest rows are forward outcomes and fail the reclaim-time prefix invariant

Locations: `MyTradingSys/backtest/layers/rsi/rsi_reclaim.py:92` scans bars after reclaim i, through i+within; `:97` and `:103` derive fail/support from those later bars; `:105` attaches the result to `reclaim_t`/`reclaim_i`. At `:91`, `status="none"` represents both insufficient future history and an expired window with no result. There is no availability timestamp or pending/expired distinction.

What is wrong: these rows cannot be treated as stable signals/features at reclaim time. This is an interface risk, not proof of a leaking trading caller: the module describes forward retest classification, exposes resolve_i, and the scoped signal drivers/live adapter do not consume this helper. A caller that uses resolve_i correctly can remain causal.

Reproduction on the actual fixture, with RSI(14), level 40 up / 60 down, clearance 1, within 5 (OURS audit settings):

* Down reclaim i=21, t=1641070800000: prefix through 21 returns status none, touch_i/resolve_i/bars_after all null. Full data returns fail, touch_i=22, resolve_i=23, bars_after=2 for the same reclaim.
* Up reclaim i=71, t=1641250800000: prefix through 71 returns none with null touch/resolve; full data returns fail, touch_i=72, resolve_i=73, bars_after=2.
* Reclaim-keyed rows differ in 26 up and 14 down channel/cut comparisons out of 400 each. The symmetric differences contain 52 and 28 row versions, respectively; these are not counts of independent signals.

The script deliberately adds `t=reclaim_t` only in the `retest_raw_*` test views, to test the unsafe interpretation; the actual helper has no `t` field. When treated as outcomes available at resolve_i, or i+within for final none, **both retest streams have zero prefix mismatches**. Fix/interface recommendation: distinguish pending from expired and expose available_i/available_t; never use the resolved status to select an entry at the earlier reclaim.

## Availability of every signal/value family

Notation: i is the current closed bar, A/B are pivot indices, p the RSI period, L an MA length, W the retest window. Input `t` is generally a bar OPEN label; a close-derived value is known at that bar's CLOSE. A timestamp label is not permission to execute at the bar's open. For hourly fixture bars availability is t+3,600,000 ms.

| Family and source location | First bar/time at which the output is knowable | Later-confirmed pivots / audit conclusion |
|---|---|---|
| Wilder RSI, `rsi_core.py:23`, `:29`, `:42` | Seed at close of bar p using the first p changes; subsequent value at close i | No pivots, only closes <=i. |
| SMA/WMA/EMA/RMA on RSI, `rsi_ma.py:30`, `:36`, `:49` | First valid full window at p+L-1 for uninterrupted data, then close i; recursive state uses prior output | No pivots or future windows. |
| Level support/rejection/failure, `rsi_events.py:64`, `:82` | Close i that exits/resolves the band run; not the earlier touch/run-start bar | No pivots; unresolved trailing runs emit nothing. |
| Direct level cross, `rsi_events.py:89` | Close i that changes side without an intervening band run | No pivots. |
| MA support/rejection/failure/cross, `rsi_ma_events.py:22`, `:25`, `:37` | Close i resolving/crossing RSI minus its MA; same-bar MA value | No pivots; warm-up follows both RSI and MA. |
| Regime, `malkan_40_60.py:42` | Close i after lookback non-None RSI observations exist | No pivots. It walks backward across None gaps, retaining old observations; a separate gap-policy matter, not future use. |
| Single-TF MLK-S1/MLK-S2, `malkan_40_60.py:85`, `:91`, `:94`, `:119`, `:125`, `:128` | Close of resolving support/rejection bar i; same-bar regime and candle color must be known | No pivots; no signal at the initial touch. |
| MTF MLK-S1-MTF/MLK-S2-MTF, `malkan_mtf.py:65`, `:91` | Daily resolving close AND selected weekly/monthly regime bars' closes | No pivots. F1: only causal with correctly supplied HTF availability times; open labels alone are insufficient. |
| Regular bullish/bearish divergence, `rsi_divergence.py:23`, `:26`, `:47`, `:54` | B+1 CLOSE confirms strict close pivot B with neighbors B-1 and B+1; A confirmed earlier | YES, one right-side bar, but output i=B+1 and t=ts[B+1] correctly defer it. Consecutive same-kind pivot ordering and chain depend only on pivots confirmed by then. |
| Operator long-range bullish/bearish divergence, `run_divergence_mtf.py:81`, `:87`, `:97` | B+1 CLOSE; A and all intermediate pivots are earlier than B and already confirmed | YES, same one-bar pivot confirmation. Search walks only earlier pivot-list positions, never later B candidates. No leaking pivot back-stamp found. |
| Live rsi_div_bull/rsi_div_bear, `alerts/live_rsi_divergence.py:41`, `:49`, `:50` | Close of B+1 in the cleaned finite-OHLC sequence | YES, inherited B+1 confirmation. `_clean` can skip bars, so B+1 means next retained bar, possibly later in wall-clock time. Output t explicitly labels confirming bar OPEN (`:11`), not real availability. Requires closed-bar inputs. |
| Reclaim up/down, `rsi_reclaim.py:47`, `:59` | Close i that returns beyond the reclaim threshold after an armed run | No pivots; dwell/depth/band counts use only earlier/current RSI. |
| Retest support/fail, `rsi_reclaim.py:92`, `:97`, `:103` | Close resolve_i, strictly after reclaim i | No pivots, but forward scanning relative to reclaim. F2 applies if joined back to the reclaim as a contemporaneous feature. |
| Retest final none, `rsi_reclaim.py:91`, `:105` | Close i+W with no earlier resolution; before then outcome is pending | No pivots. Current returned none does not distinguish pending. |
| Backtest malkan/MA wrappers, `run_rsi_backtest.py:211`, `:225`, `:256` | Inherit the resolving close and closed HTF inputs; entry model is signal bar close (`:97`, `:107`) | No new pivots; full-series indicator computation alone is not a leak when prefixes remain unchanged. |
| Forward returns/trade scores, `run_divergence_mtf.py:108`, `:145`; `run_rsi_backtest.py:95`, `:158` | Forward horizon/exit must complete, later than the event/entry | Deliberate ex-post scoring, not real-time signals. Do not demand unchanged forward outcomes on a truncated history. |
| Anchor probe, `run_t090_anchor_probe.py:24` | Shifted/resampled complete bucket, then inherited B+1 confirmation and later scoring horizon | Creates no new detector; constant timestamp offset does not move information from later bars into earlier indices. |
| Observation reader, `observation.py:121`, `:137` | Only after an alert line has been persisted/read | No RSI/pivot computation. Reads latest record, exposes t_close/t_confirm, has no historical as-of argument; a current observation is not a historical feature snapshot. |

Concrete original-fixture divergence: A=123, B=129, event i=130, t=1641463200000. Closes 42817.38 -> 42591.58, RSI 19.824539404224836 -> 23.505213307442233. Pivot B needs bar 130's close, so the event is absent on prefix ending 129 and present on prefix ending 130. Its hourly availability is 1641466800000. The other original-fixture regular event indices are 135,151,160, each exactly B+1.

The live adapter's OPEN-time stamp is explicit repo convention, not a separate defect here. Prefix equality over closed bars cannot establish correct behavior if a caller supplies an actively forming bar or trades at the event's open. This audit establishes detector behavior under closed-bar inputs; it does not certify the external runner/execution pipeline.

## Reproducible truncation test

```powershell
python -B MyTradingSys/research/gpt_burn_2026-10-24/gx-rsi-lookahead/audit_truncation.py
```

RESULT: exit 0. Script emits complete JSON with parsed counts, first changed rows, independent numerical comparisons, file inventory, MTF counterexamples, and original divergence details. No output files are written. It asserts zero unexpected causal mismatches; expected forward-retargeting failures are explicitly reported separately, not silently discarded as passes.

For every cutoff t=bar index 0..399, recompute all upstream RSI/MA/regime/event inputs on bars[:t+1] and compare full event dictionaries with full-series events whose output label is <=t. All 9 aligned value series are compared to their exact full-series prefixes, giving 3,600 checks on the original fixture with zero failures; mirrored-price data gives another 3,600. Each of the 27 event streams is tested at 400 cutoffs; 25 streams use actual availability interpretation and pass, while the two raw reclaim-keyed retest streams expose F2. Count = 10,000 passing causal event-stream/cut comparisons per original/mirrored dataset, not 10,000 independent signals.

| Original-fixture stream | Full events | Mismatching cutoffs / 400 |
|---|---:|---:|
| MA SMA / EMA / RMA / WMA | 70 / 78 / 64 / 82 | 0 / 0 / 0 / 0 |
| Levels 30 / 40 / 50 / 60 / 70 | 12 / 36 / 56 / 28 / 4 | 0 / 0 / 0 / 0 / 0 |
| Regular bull / bear | 4 / 0 | 0 / 0 |
| Long-range bull / bear | 3 / 4 | 0 / 0 |
| Reclaim up / down | 14 / 10 | 0 / 0 |
| Raw retest rows keyed to reclaim, up / down | 14 / 10 | 26 / 14 |
| Retests keyed to actual resolution/expiry, up / down | 14 / 10 | 0 / 0 |
| Live divergence | 4 | 0 |
| Driver MA touch / cross | 21 / 17 | 0 / 0 |

The fixture lacks open prices. The base audit explicitly sets open=close, so candle-filtered Malkan/MTF/driver signals are zero and those base tests alone are vacuous. Additional explicitly synthetic open=close-1 and open=close+1 variants keep the original close/high/low observations, generate respectively 1 bull and 4 bear Malkan events, and each is reproduced by the matching MTF closed-input and driver wrappers with zero mismatches over 400 cutoffs. These opens are branch-coverage inputs, not reconstructed real candle data. Constant known-at-bar HTF states here test composition stability, not true weekly/monthly RSI histories; F1's separate availability counterexample covers that clock distinction.

For bearish coverage, mirror prices as C'=100000-C, H'=100000-L, L'=100000-H, O'=100000-O (OURS test transform): 4 regular bearish events, long-range bull/bear 4/3, and 4 live events; all causal prefixes pass. On original data replace bar 100 close with NaN and bar 200 high with infinity: live adapter still has 4 events, 400 comparisons, zero mismatches. This checks cleaning consistency without changing production behavior.

## Independent Wilder derivation and comparison

Expected numbers are calculated by the script's `independent_wilder`, directly from `MyTradingSys/backtest/layers/FORMULAS.md:13` through `:28`: decimal arithmetic with precision 50, delta gains/losses divided by the full period, recursive Wilder smoothing, RSI = 100G/(G+L), and 50 on a completely flat seed. This expression is algebraically identical to 100-100/(1+G/L) and handles G=0 or L=0 without dividing by L. No production RSI helper, existing tests, CSV indicator columns, or golden values generate expectations. Production RSI is imported solely for actual values and signal inputs.

For [10,12,11,14], p=3: changes +2,-1,+3; G=(2+0+3)/3=5/3 and L=(0+1+0)/3=1/3; RS=5; RSI[3]=100-100/6=83.33333333333333. Actual=83.33333333333334. Prefix indices 0..2 are None.

For [10,11,10,12,11,13], p=2: seed G=L=0.5 gives RSI[2]=50. Next G=1.25,L=0.25 gives RSI[3]=83.33333333333333. Next G=L=0.625 gives RSI[4]=50. Next G=1.3125,L=0.3125 gives RSI[5]=80.76923076923077. Production agrees within floating arithmetic. Flat/increasing/decreasing p=14 fixtures independently give 50/100/0 once seeded, and pass.

| Fixture period | Compared non-None values | Maximum absolute error |
|---|---:|---:|
| 1 | 399 | 0 |
| 2 | 398 | 2.2879476091475226e-12 |
| 3 | 397 | 1.4068746168049984e-12 |
| 5 | 395 | 5.755396159656812e-13 |
| 9 | 391 | 2.7000623958883807e-13 |
| 14 | 386 | 2.1316282072803006e-13 |
| 21 | 379 | 1.4210854715202004e-13 |

Total 2,745 numerical comparisons; all None prefixes match. OURS numerical tolerance is 1e-10 RSI points, allowing binary-price subtraction/recursive rounding versus decimal-price arithmetic. Initial trial used 1e-12: 14 period-2 and 3 period-3 values exceeded that threshold (max 2.29e-12), causing the audit script's initial assertion to fail. The numerical method was retained, tolerance made explicit at 1e-10, and the entire script rerun successfully. This is rounding-scale disagreement, not a seed/smoothing defect.

Selected RSI(14) decimal expectations versus actual: index 14 = 56.16276802655418 versus 56.16276802655401; index 123 = 19.82453940422478 versus 19.824539404224836; index 129 = 23.505213307442133 versus 23.505213307442233; index 399 = 37.62173981446867 versus 37.62173981446863.

Result: 1 HIGH MTF open-time contract leak and 1 LOW retest outcome-timing hazard; tested divergence/live signals are causal at B+1 close, and independently derived Wilder RSI matches within 1e-10.
