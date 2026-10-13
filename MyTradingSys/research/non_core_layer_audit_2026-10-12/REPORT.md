# Independent layer audit: RSI, WaveTrend and the other non-core layers

Prepared 12 October 2026, Asia/Kolkata. Scope: analysis and evidence preservation; no strategy or execution changes. TOM and FABIO strategy audits are excluded because parallel sessions own them. Shared adapters were inspected where they affect the other layers.

## Decision for the operator

Keep the working calculation and observation infrastructure. Do not interpret it as a proven trading system. The immediate priorities are to define exactly which RSI system is being evaluated, reconcile source rules with code and execution, and preserve event-level evidence before another profitability run. WaveTrend is an unbuilt, parked indicator proposal in the inspected repository, not a failed backtest or an implemented layer.

The strongest positive finding is engineering progress: 505 existing tests passed in this audit, four Malkan extract files passed their quote checks, and both saved RSI divergence tables were reproduced exactly from their committed JSON summaries. The strongest negative finding is that no inspected non-core result establishes the project's current S3 standard: walk-forward out-of-sample positive net expectancy with an interval above zero. This is an evidence verdict, not a claim that every possible version of these systems cannot work.

Several earlier conclusions were too broad. Negative generic-bracket RSI tests do not reject Malkan's complete strategy. A small positive live sample does not establish edge. A low probability-of-backtest-overfitting score does not establish profitability. A number found in a transcript is not sourced for every role in which code uses it.

## What was actually verified

Evidence classes used throughout:

- **REPRODUCED:** a local check executed in this session. The script, outputs and logs are attached.
- **CODE:** inspected implementation; proves behavior or wiring in this checkout, not deployment on the live machine.
- **RECORDED:** a committed historical report was read; its underlying full market-data run was not repeated here.
- **UNKNOWN:** the evidence needed to decide is unavailable or incomplete.

The evidence files include source excerpts with line numbers and SHA-256 hashes. Use those hashes when comparing with later parallel changes. The checkout advanced during the session; the reproducibility receipt records its own Git HEAD, and the source manifest records the exact files used. This is not a claim that every observation came from one immutable commit.

Local default 1m input roots `Dumps/backtest/raw_1m_2022` and `Dumps/backtest/raw`, and the local `Dumps/backtest/runs` folder, were absent. `F:/MTS/data` exists, but equivalent full 1m coverage was not established. Therefore this audit did not rerun years of market outcomes. Re-rendering saved summaries verifies report arithmetic/presentation, not raw-data correctness.

The runtime evidence is **mirror@2026-10-11T20:09:30.734919+00:00**, producer Git `927665a`. The mirror tool explicitly marked it stale. It is not current live status. The connected private Control Room database could not be read with the available tools; committed page configuration and relevant recorded instructions were inspected instead.

## Layer-by-layer assessment

| Layer / component | What went right | What went wrong or remains unproven | Proof / confidence | Needed next / input required |
|---|---|---|---|---|
| RSI calculation and smoothing | Central Wilder implementation, explicit seed and flat-series convention; 134 RSI tests pass, including event and research modules. Independent period-3 arithmetic matched. | Calculation correctness is not source fidelity or profitability. Generic params specify tolerance 0 although the level-event function rejects nonpositive tolerance. | E01-E03; REPRODUCED/CODE, high | Validate public parameter files against their consumers; retain a documented flat-series convention and independent numerical fixtures. |
| RSI level events | Support, rejection, failure and cross are separately represented; live registry includes 5m, 15m and 1h. | Historical D3 tested 40-support long and 60-rejection short. Current live detector uses level 40, and execution additionally maps failure/cross events. The research and traded event populations differ. | E04-E06; CODE/RECORDED, high | A versioned event-to-side-to-exit identity shared by research and calibration; event-specific outcome rows. |
| Malkan single-timeframe 40/60 | Regime and candle-color mechanics are implemented and tested. | Uses a 20-value regime proxy and same-timeframe gate. That is not the complete daily entry with higher-timeframe conditions. Historical generic bracket result cannot reject the full strategy. | E07-E09; CODE/RECORDED, high | Own-source rule ledger, primary-frame examples, complete entry/stop/target specification and home-market check set. |
| Malkan multi-timeframe composer | Exists; backtest driver supplies higher-timeframe close timestamps, mitigating look-ahead. | Gates on regime strings rather than current weekly/monthly RSI thresholds. No equivalent complete-strategy run was established here. `state_asof` documentation invites open-time misuse. | E07-E09; REPRODUCED/CODE, high | Make availability timestamps explicit; source-faithful threshold gates; audited run receipt after readiness is complete. |
| RSI divergence: sourced-window detector | Close-to-close, decimals retained, confirmation delayed to the next bar; four extract quote gates pass. | Consecutive strict local pivots are an implementation choice. Raw divergence study omits candle confirmation, price trigger, source target and management. | E10-E12; REPRODUCED/CODE, high | Label it a raw event study; annotated chart cases for detection precision/recall and complete strategy exits. |
| RSI operator reclaim / 2a / long-range ideas | Reclaim module logs dwell, depth and retest outcomes; caller supplies window/clearance explicitly. Long-range study is separately labelled. | Full BB, CVD/OI, RSI-MA confluence and speed-trigger strategy not demonstrated. Small higher-timeframe leads are unstable under anchor changes. | E12-E14; CODE/RECORDED, medium-high | Separate operator hypothesis from Malkan rules; freeze confluence definitions before testing and retain unseen data. |
| WaveTrend | Formula and defaults recorded in T061 and the LazyBear survey; independent, read-only layer contract is clear. | No named implementation found across inspected refs; no live registration or performance output found. Planned module paths disagree. Current board parks it. | E15-E16; CODE/RECORDED, high for repo status | Pin exact Pine version and attribution, save source/fixture values, define edge cases, then build observation-only parity implementation. |
| Other LazyBear indicators: Squeeze, Better Volume, VFI | Survey records corrected defaults and known source quirks. | These are shortlisted designs, not delivered layers. Squeeze displayed-source BB multiplier differs from proposed corrected behavior; updated author source was not verified in that report. | E16; RECORDED, medium | Source-version decisions and chart parity before coding; VFI must not be represented as measured aggressor CVD. |
| CryptoCred | Three setup families, structure/retest adapters and 69 passing tests; historical fill-bias corrections were recorded. | Fixed 0.1% buffers and 1.5R/2R targets do not follow from the quoted minimum-R:R requirement. Live execution uses its generic bracket rather than the setup's native geometry. | E17-E19; CODE/RECORDED, high | Correct role-level provenance; define sourced context/selection and management; reconcile fills and live-vs-backtest contract. |
| Positioning / funding-CVD fade | Costs/funding accounting tested; corrected full-funding rerun remains negative. | Research variant selection and live defaults differ; source concept does not validate percentile/window defaults. | E20-E21; CODE/RECORDED, medium-high | Freeze variant identity and raw CVD/funding coverage; only reopen with a materially different, sourced hypothesis. |
| Session momentum | Independent implementation and named session/DST support exist; funding-window rerun corrected an earlier invalid run. | Positive aggregate net is tiny and inconsistent by year; selected NY/60-minute research variant differs from live UTC/30-minute default. | E20-E21; CODE/RECORDED, high | Test exactly the intended sourced/adapted session contract; report per-year and session risk-adjusted results. |
| Turn of candle | Operational sampling is explicitly tagged; 36 tests pass. | High trade frequency is not edge. Existing BTC proxies fail; live minute-14 timing differs from opening-window research entries. | E21-E22; CODE/RECORDED, high | Keep calibration results separate from strategy evidence; reconcile exact timing before making comparisons. |
| Session levels / failed first break | Conservative same-bar stop precedence and explicit assumptions; 13 tests pass. | Historical sampled cells with sufficient n are negative; clocks, failure window and target choices are placeholders. | E23; RECORDED/CODE, medium-high | Event rows, justified session boundaries and like-for-like null; no parameter search to rescue the existing result. |
| Tick/extreme flags | Ranking, cooldown and tier tables built; 49 tests pass; metadata records actual coverage. | Not wired in inspected default registry. Recorded delta cross-check has a nonzero maximum discrepancy, despite an identity claim in the builder description. Rare flags and top-20 extremes do not prove predictiveness. | E24; CODE/RECORDED, high | Reconcile mismatched raw bars, OI resolution and historical coverage; validate context utility and future flag rate. |
| Timeframe infrastructure | 18 tests pass; weekly/monthly and alternative anchors supported; trailing unclosed buckets excluded. | Gapped but closed buckets are returned. RSI divergence consumer does not reject them or report their impact. Day-reset 7h includes a shorter end-of-day bucket. | E25; REPRODUCED/CODE, high | Explicit missing-bar policy and duration field; anchor provenance; prohibit calling variable-duration buckets uniform 7h exposure. |
| Consensus / RSI observation | Hook is wired; 52 tests pass; missing fields remain null. | README status is stale; RSI values are from the latest RSI event, not necessarily current. Hook writes one row per firing poll, not one per every core alert. | E26; CODE, high | Freshness tags, per-event linkage and delivery/failure accounting; separate this from strategy consensus or voting. |
| MA/candle/volume research and market guide | Observation-only guide and explicit validation/triage reports exist; volume validation did not silently promote the DEV lead. | No inspected validated standalone entry system. RSI-volume validation is insufficient-n, not a definitive rejection; candle results are DEV triage. | E27-E28; RECORDED, medium | Preserve stage labels; test only frozen candidates after readiness; require event-level rows and multiplicity control. |
| Kurisko candidate | Repository research distinguishes four stochastics from four RSIs and lists conflicts. | No faithful implemented strategy demonstrated; oscillator definition, third setting, trigger and market translation remain unresolved. | E29; RECORDED, medium | Primary chart/source confirmation, not another invented RSI parameter set. |

The broader project also names probability, options and analyst/caller feeds. These are adjacent integrations, not all in `backtest/layers`. `backtest/prob_table.py`, its tests, the probability design and `queue/cbp_adapter.py` exist, but their calibration, feed integrity and execution readiness were not deeply audited in this pass. Treat those as **inventory-only / UNKNOWN**, not passed. A blanket claim that this report certifies every MTS subsystem would be false.

## RSI findings in detail

### 1. The maths is a useful foundation

The independent worked case is closes `[10,12,11,14,13]`, period 3. The seed gains average 5/3, losses 1/3, giving RSI 83.333333. On the next loss, averages become 10/9 and 5/9, giving RSI 66.666667. Current code matches both. A flat series returns 50 by an explicitly documented project convention. This is not proof of unconditional parity with every chart platform.

### 2. Regime is not the same as an RSI threshold

The reproduced series `[65]*19 + [45]` produces `BULL` under `malkan_regime`, although current RSI is only 45. Therefore `weekly_regime == BULL` cannot be substituted for `weekly_RSI > 60`. The reverse problem also occurs conceptually: an earlier low in the lookback can reject a currently qualifying RSI. This affects which trades enter the sample before any profitability calculation.

The MTF driver correctly supplies `bucket_end` availability times. The helper itself merely chooses the latest timestamp not after the query; it cannot tell whether supplied timestamps are bar opens or closes. This is a contract hazard, not evidence that the current driver leaks future information.

### 3. The old RSI verdicts apply to specific proxies

| Historical test | Recorded result | Valid interpretation | Still needed |
|---|---|---|---|
| D3 1h, 40-support, tolerance 0.5, five-bar return | OOS n=89; gross +0.043%, PBO 0.030 | 4.3 bp gross is below even the study family's 10 bp taker round trip. Low PBO does not make it profitable. | Raw event outcomes and current-rule parity; do not call this full Malkan. |
| Single-TF Malkan, generic 1% stop / 2% target | 1h n=43, net -0.092%, PBO .760; 4h n=17; 1d n=5 | Negative or thin evidence for this implementation and bracket. | Complete sourced setup with home-market examples and matching exits. |
| RSI-MA event grid | 1h n=357, net -0.199%; 4h n=69, net -0.216% | No demonstrated edge for tested grid/exit; 15m run was dropped after timeout. | Identify desired standalone observation vs trade strategy; do not silently fill the missing 15m result. |
| RSI down-cross plus volume, validation | n=50; net -2 bp, interval [-68,+64] bp | Original validation label is INSUFFICIENT-N against registered minimum 100; unvalidated hypothesis. | Preserve validation status; do not select new thresholds from this validation set. |

These figures are RECORDED, not fresh full-history reproductions. The old reports' source descriptions and status lines sometimes predate later work. For example, four Malkan extracts now exist and pass quote matching, superseding the older claim that extraction had never been done.

### 4. Recount of the newer divergence evidence

The main JSON contains 19 timeframes x two columns x two sides = **76 cells**: 32 labelled no edge, 44 insufficient n. Of the 32 cells with at least 300 events, **31 are net negative**. The only positive one is 1h operator bearish: n=332, net +0.0383977%, t=0.3882, insufficient evidence for an edge.

The T088 extension adds four timeframe/anchor configurations and **16 cells**: four no edge, twelve insufficient n. Combined: **92 cells, 36 no edge, 56 insufficient n, zero edge candidates**. All four eligible extension cells are negative. This recount and exact report regeneration are REPRODUCED from saved summaries.

The outcome is a fixed ten-bar forward return minus 0.10% round-trip taker fee. It is not realized strategy profit: no source-faithful entry trigger, stops, partial exits, funding or slippage. Events may overlap. The naive t-stat therefore overstates independence. Calendar-year tables do not constitute an untouched chronological holdout. The whole historical period has now been inspected for these hypotheses.

The 6h operator bullish lead had only 54 events, +1.57% and t=2.99. The subsequent anchor probe reported 18 cells, only three with t>2; the favored cell moved with the anchor, and all counts were 35-55. This undermines a specific 6h/7h advantage, but does not mathematically prove that all common positive drift was caused by data mining. The appropriate decision is **unvalidated, underpowered, no promotion**.

### 5. Source fidelity remains the central missing proof

The extracts establish that the source discusses close-to-close divergence, short separation, confirmation, targets and higher-timeframe context. They also explicitly flag auto-caption and translation noise. Quote-gate success proves matching to the stored transcript, not the correctness of captions or of a chart interpretation.

Target C is described as a point between A and B; the extract says its exact geometry needs the video frame. Partial-exit wording is garbled. These cannot be filled by convention and called Malkan. Build a minute-timestamped source ledger with screenshots, design/check separation, missed examples and false positives. Only then evaluate the complete encoded strategy.

## WaveTrend and the indicator collection

T061 records channel 10, average 21, WT signal SMA 4, normalization constant .015, and threshold annotations +60/+53/-60/-53. The intended computation is typical price, EMA deviation normalization, smoothed WT1 and four-bar SMA WT2. These describe an oscillator; they do not supply a profitable trading policy or sourced exits.

The survey says the linked page is a lonestar108 republication whose header attributes LazyBear. A current web fetch of both the regional and main TradingView URL failed as restricted. Therefore this session relies on the saved survey for that attribution and formula and **does not claim fresh Pine-source verification**. Do not repeat the item's public-domain licensing assertion without checking actual source terms.

The current branch/ref filename inventory found no Python/Java/Pine file named for WaveTrend, Squeeze Momentum, Better Volume, VFI/volume_flow or Kurisko. Current layer/source/script text searches and the default registry also found no WaveTrend implementation. This cannot rule out differently named untracked work on another machine.

There are two proposed WaveTrend paths (`layers/wavetrend/` and `layers/momentum/wavetrend.py`), which should be reconciled into one owner and API before building. Existing board policy parks new layers while Tom/Fabio are redefined. The user's present request authorizes this audit and roadmap; it is not necessary to change that build policy to deliver the report.

Recommended sequence: WaveTrend first among new indicator ports because it is explicitly requested and compact; then Squeeze if volatility context is still a gap; Better Volume after verifying its long formula and precedence; VFI only for a clearly defined candle-volume observation need. This is an audit recommendation, not evidence of relative returns or a change to the existing queue.

For WaveTrend, freeze Pine version, EMA initialization, missing values, zero-deviation behavior, cross equality rules, warm-up and timestamp semantics. Obtain golden chart/export fixtures for flat, trending and alternating input plus a real chart. Implement continuous values and crossover tags independently of trade direction. A profitable-strategy study is a separate deliverable after readiness, source policy and exits are resolved.

## Other material failures and successful corrections

**CryptoCred provenance conflict:** the extract's Rule 9 says "greater minimum risk reward requirements". The code uses `target_r=1.5` or `2.0` to compute an exact exit price. The later NO-SOURCE sweep marking 1.5R sourced does not bridge that difference in role. Keep the target attribution unresolved; the concept is sourced, the fixed exit implementation is not established by this passage.

**Testnet comparisons are not like-for-like:** `auto_trader.layer_signal` builds a market-entry plan from configured `stop_pct` and `targets`. Native `entry_price`/`stop` emitted by the CryptoCred adapter are not used for that plan. The generic RSI backtest also omits funding and slippage in its `simulate_trade` call. Testnet brackets, event-study horizons and source-native exits must each have distinct experiment identifiers.

**Positioning and session results:** the corrected full-funding report records positioning n=76, net -0.0453%; session n=299, net +0.0177%, per-trade Sharpe .0084, one of two OOS years positive. These fail their historical gates. Do not silently apply the newest minimum-n rule retroactively and overwrite history; add a current evidence assessment alongside the historical verdict.

**Turn of candle:** the historical calendar test records 49,823 OOS events, almost zero gross return and -0.1201% net. Tested opening-imbalance versions also fail. The live adapter enters at minute 14 using the same quarter's minute-0 imbalance, unlike research entry at the opening-window close. Neither a successful timer nor a large calibration ledger validates the other.

**Tick data integrity:** `tiers_meta.json` records 126,720 compared bars, 2,880 missing in klines and maximum absolute delta difference 68.25 BTC. The builder describes the kline and aggregated-trade delta as identical. The formula may be theoretically equivalent on matched inputs; these recorded inputs are not shown to match. This is a concrete unresolved data reconciliation issue, not grounds to tune severity thresholds.

**Missing-event evidence:** the divergence driver writes summaries and reports but not per-event outcome rows. Existing year/half-day summaries are useful; they do not allow arbitrary session x regime stratification, duplicate removal or independent clustered confidence intervals. The later B154 note identifies this limitation. Do not invent its proposed session boundaries or EMA50 regime as trader-sourced truth.

**Documentation conflicts:** consensus is currently hooked despite the README saying otherwise. T065's item says OPEN while the index says DONE for the survey; survey completion is not implementation completion. The board lists Tom, Fabio, turn-of-candle and parked WaveTrend, leaving RSI and other existing layers unrepresented. Status should have separate fields for sourced, encoded, fidelity-checked, backtested, calibration-only, and live evidence.

## Runtime evidence and its limits

Parsing the complete mirrored auto-trades log gave 3,961 rows: 698 trade_attempt, 682 trade_closed, 680 ledger_row, plus rejection, halt and operational records. These are event counts, not unique reconciled trades. Among trade_closed records: turn-of-candle 548; RSI 5m 48, 15m 13, 1h 4; session 5; CryptoCred SR flip 15m 19 and 1h 2, fib pullback 15m 7, failed MSB 15m 1. No closed records for Malkan or positioning occurred in that parsed set.

The canonical trade ledger was not present in the inspected mirror inventory. `trade_closed` records did not contain a top-level exit_reason; separate ledger_row events have different fields. Do not join merely on plan_id without checking account and duplicate/restart semantics. No fresh P/L ranking or win-rate claim is made here. Zero closed rows cannot distinguish no detector fire, no route, rejection, downtime or open positions.

## Revalidation from different lenses

| Lens / challenge to the initial view | Evidence considered | Revalidated decision | What would change it / still needed |
|---|---|---|---|
| Could RSI simply be broken maths? | Independent seed/update example and passing tests | Basic math is supported; focus on strategy identity and data contracts. | Independent real-series platform fixtures could expose warm-up or missing-value differences. |
| Does no-edge mean reject Malkan? | Generic bracket, proxy regime, raw divergence without source exits | No. Reject promotion of tested versions; full source strategy remains unresolved. | Held-back chart recall/fire-rate and full faithful strategy test. |
| Could fees alone explain everything? | D3 +4.3 bp gross vs 10 bp fees; negative/near-zero gross elsewhere | Fees explain some failure, not all. Maker assumptions cannot create absent gross predictiveness. | Realistic fills and adverse-selection evidence under the same frozen strategy. |
| Does a positive 6h/7h result justify further tuning? | Small n, 18 anchor comparisons, t-stat instability | No promotion or winner selection from these same data. | Preregistered independent symbols/period and clustered uncertainty after readiness. |
| Do green tests prove fidelity? | 505 tests, but source/code role and timing mismatches persist | Tests validate encoded behavior; they do not validate its intended meaning. | Independent source-derived cases, realistic missing-data/fill tests and false-positive controls. |
| Are live wins stronger than historical losses? | Four 1h closed records, different sizes/exits, stale mirror | No. Not a comparable or sufficiently powered experiment. | Canonical ledger, config/deployment hashes, same strategy and normalized risk. |
| Is WaveTrend a promising failed layer? | Design only, no implementation/performance output found | Untested indicator candidate; source and parity work precede edge claims. | Source snapshot, implementation, golden fixture and then valid strategy study. |
| Does a new report supersede old provenance? | CryptoCred minimum-R:R passage vs fixed target code | No; role-level mismatch survives the later note. | Own-source instruction explicitly supporting that exit, or explicit operator-hypothesis label. |
| Does more historical data solve uncertainty? | Sparse daily/weekly events, already inspected period, missing source rules | Only partly. More contaminated observations do not become unseen evidence. | Power plan, data manifest, untouched test set and complete strategy first. |

## Roadmap with acceptance criteria

Priority means dependency order, not an instruction to run unrelated work in the parallel TOM/FABIO sessions. Suggested lanes are ownership recommendations; no work has been dispatched by this report.

| Priority / work package | Concrete output | DONE when / decision gate | Owner lane | Needed / unknown |
|---|---|---|---|---|
| P0-A: layer evidence register | One row per independent system and version; reconcile stale docs/board | Every row distinguishes source, code, fidelity, statistics, calibration and deployment; evidence links resolve | Cloud docs/review | Current page owner for eventual publication; no source-code dependency |
| P0-B: Malkan source and example ledger | Rule-role table plus source frames, minute timestamps, design/check split | Target C, confirmation, partial exit and HTF conditions are resolved or explicitly unknown; caption ambiguity retained | JIS-NB source access, Cloud review | Video frames and reliable chart/instrument/time labels |
| P0-C: identity and clock audit | Exact detector/side/entry/exit/cost/config mapping; timestamp schema | Backtest and calibration identities match or are explicitly separate; causal HTF and gap cases demonstrated | Codex code audit | Event rows, deployed config SHA and canonical ledger from JIS-NB |
| P0-D: data receipts | File hashes, coverage, gaps, funding and event-level schemas | Tick delta discrepancies explained; no absent fields converted to zero; every new result reproducible | Data host + Cloud review | Matched aggTrades/kline source rows and funding coverage |
| P1-A: complete RSI fidelity encoding | Source-faithful strategy alongside labelled operator 2a hypothesis | Held-back examples establish recall and acceptable false-positive/fire rate; no target guessed from captions | Codex build after source specification | P0-B; all 12 readiness items answered |
| P1-B: WaveTrend parity port | Canonical formula entry, one module/API, fixtures, crossover tags | Exact source version and attribution preserved; warm-up/zero denominator/equality/closed-bar tests pass; no execution side inferred | Cloud spec, Codex implementation | Pine source/export and explicit build-policy reconciliation |
| P1-C: observation freshness | Per-TF as-of, available-at, age, missing reasons; consensus event keys | Stale RSI cannot look current; per-poll vs per-event cardinality explicit; failed write cannot silently count as delivered | Codex build, shared-file owner coordination | Observation contract and logged write failures |
| P2-A: one frozen RSI experiment | Readiness document, trial registry, event dump and report | Source-native exits, realistic fees/funding/slippage, clean chronological split, matched null, power and dependence-aware CI; no post-test rescue tuning | Data host execution, Cloud adversarial review | New untouched period/symbol or appropriately reserved data; P0/P1 completion |
| P2-B: indicator utility studies | Separate context usefulness and trade-strategy tests | WaveTrend/Squeeze/BVI evaluated for specified purpose; new combinations count as new trials; not mixed into Tom/Fabio gates | Research lane | Completed ports and preregistered hypotheses |
| P3: calibration reconciliation | Detector -> alert -> accepted plan -> fill -> exit -> ledger funnel per source | Unique reconciled events, deployment/config identity, missing reasons and normalized net returns; only S3-passed configs count as S4 evidence | JIS-NB supervisor/data lane | Canonical ledger and plan/fill artifacts; stale mirror is insufficient |

Do not spend the next session sweeping more RSI periods, tolerances or anchors. The highest-value next action is the Malkan source/fidelity package and the strategy-identity table. WaveTrend can progress as a bounded read-only port once its source is pinned and the parked-policy dependency is resolved. Existing failed proxies should remain historical negatives; a changed hypothesis must receive a new version and trial identity.

The current 12-item readiness template is the gate for new backtests. One wording caveat should be reviewed: a generic fixed bracket is not mathematically guaranteed to be a lower bound on the source trader's management; it can either help or hurt. Report it as an alternative exit experiment unless a lower-bound relationship is actually proven.

## Explicit unknowns for the next session

| Unknown | Why it matters | Required evidence / request | Can work continue without it? |
|---|---|---|---|
| Exact Malkan target C and partial management | Determines whether a strategy backtest is faithful | Primary chart frames and transcript alignment | Yes: source inventory and contract work; no faithful P/L verdict yet |
| Fidelity on source-home examples | Current BTC null could be encoding failure or market transfer | Minute-level held-back source ledger, recall and false-positive rate | Yes: improve reproducibility first |
| WaveTrend exact Pine version/license/initialization | Avoid attributing a corrected or forked version incorrectly | Saved primary source and golden values | Yes: API/spec draft; final parity acceptance waits |
| Whether full Malkan MTF runs exist on another machine | Local absent runs do not prove global absence | Run manifest and immutable results from data owner | Yes: qualify status as unestablished |
| Current deployment and live layer health | Repo wiring does not prove running process/version | Fresh mirror + deployment SHA + per-layer counters | Yes: offline audit remains valid |
| Why Malkan/positioning have no closed records in mirror | Could be rare events, rejection, mapping or availability | Full funnel logs and canonical ledger, account-aware joins | Yes: do not speculate about causation |
| Tick discrepancy mechanism | Data-equivalence claims presently unsupported by metadata | Exact mismatched timestamps and raw bars | Yes: no threshold promotion |
| Event-level outcomes and regimes | Needed for dependence-aware inference and B154 stratification | Export timestamp, signal/version, side, entry/exit, costs, overlapping exposure and data status | Yes: can design schema now |
| Untouched validation data | Reusing inspected history creates selection bias | Exposure registry and frozen future/independent dataset | Yes: fidelity work first |
| Probability/options/caller readiness | Outside deep coverage of this audit | Dedicated calibration and feed-integrity audit | Yes: keep inventory-only label |
| Latest private page decisions | Committed configuration may lag private database | Page-owner pickup using its connected ArtifactData access | Yes: no page publication or configuration changes made |

## Portable evidence and cloud handoff

Read `REPORT.md` first, `EVIDENCE.md` for source excerpts and hashes, `reproductions.json` for fresh mechanical checks, `test_results.json` and `tests_*.txt` for 505-test results, and `quote_gates.json` for the four extraction checks. `verify_audit.py` reproduces these checks without sending orders or changing strategy code. Source excerpts are included so the package remains readable outside this checkout.

Cloud continuation: revalidate the evidence against current `origin/fast-track`, reserve a non-overlapping claim, and start with P0-A or source-ledger preparation. Preserve TOM/FABIO ownership. Do not reinterpret these recorded results as fresh live data, do not relabel proxies as complete source systems, and do not launch new P/L backtests before the readiness gate. This report supplies the analysis and work queue; it does not claim the roadmap has already been implemented.
