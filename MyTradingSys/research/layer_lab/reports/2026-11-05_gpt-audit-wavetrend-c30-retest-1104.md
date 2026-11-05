MATCH: 11 | DEVIATES: 2 | NOT_CHECKABLE: 1

# GPT audit: WaveTrend c30 retest study (2026-11-05)

**Verdict: FIX-FIRST.** The implementation largely follows the frozen cell and signal definitions. Two material deviations: its data loader does not point at the available permitted DEV source, and its fee treatment does not implement the fee, slippage, and funding components in FORMULAS.md. One context detail depends on an external helper and is not checkable from the scoped sources.

Checked: `PRE_REG.md` (rules 1–14), `study.py`, and `FORMULAS.md`. Line references below are source lines; each quoted fragment is the implementation or governing formula inspected.

| # | PRE_REG rule | Status | Evidence / finding |
|---|---|---|---|
| 1 | Timeframe and cell grid: 15m/30m/1h; sides, three confluences, six gates, pooled plus four sessions, two entries | MATCH | `study.py:34-40` declares the dimensions; `study.py:275-301` iterates them. `study.py:289` adds `ALL` plus each session. |
| 2 | WaveTrend dot definition, band ±53, closed-bar convention, first 200 bars unused | MATCH | `study.py:28-29`, `study.py:80-95`: `cross_events(..., "le")`, side-specific ±`BAND` test, and `i >= WARMUP`. |
| 3 | RSI(14) same timeframe and dot bar, buy ≤40 / sell ≥60 | MATCH | `study.py:30-31`, `study.py:110-115`, `study.py:281-286`: RSI is computed per resampled TF and filtered at event index. |
| 4 | Regular close-based divergence, swing window 3..12, matching direction, stamped within 3 bars through dot | MATCH | `study.py:32-33`, `study.py:117-119`, `study.py:246-253`; `div_ok` checks indices `i-3` through `i`. |
| 5 | Signal entry at dot close; retest at dot midpoint, first touch over next 6 bars, gap open execution, skip if no touch | MATCH | `study.py:105-108`, `study.py:148-168`; `research_kit.retest_entry` is named at `study.py:161`. Helper contract `research_kit.py:275-283` specifies next bars, first touch, midpoint limit, and gap-open fill. |
| 6 | Exit at close 12 bars after entry; drop if no exit bar | MATCH | `study.py:25`, `study.py:148-167`: `j + h` exit close and boundary drop. |
| 7 | UTC session assignment uses dot-bar close and cutoffs from `session_tag` | MATCH | `study.py:97-102`: passes event `t_close` to `rk.session_tag` and filters by that value. |
| 8 | Trend gate with/against daily SMA200 direction; regime rows via regime_tag | MATCH | `study.py:121-145` maps daily side to with/against and regime tag to the descriptive gates; event context assigned at `study.py:278-279`. The actual daily SMA200/regime calculation is delegated to `research_kit.regime_tag`, not reimplemented in this file. |
| 9 | Daily/weekly/monthly context uses last closed bars with no future context | NOT_CHECKABLE | `study.py:127-137`, `study.py:233-237` delegate to `rk.regime_tag` and resampling. The scoped sources do not establish the helper’s exact lookback/closed-bar timing for all three series, so no stronger match claim. |
| 10 | Net subtracts 0.14% RT; day-clustered mean/SE, 95% CI mean ±1.96 SE | DEVIATES | `study.py:27`, `study.py:171-185` subtract one constant from gross. FORMULAS.md §13 (`:352-358`) specifies fee plus `slip_rt` and funding over `(t_in,t_out]`; this code has no funding input or per-trade funding adjustment. The fixed 0.14% does not implement those components. Cluster aggregation and CI are present in `study.py:176-185`. |
| 11 | Drift control is same-side gross over every bar in matching TF/window/gate/session | MATCH | `study.py:188-214` builds every eligible bar and filters by session/gate; `study.py:179-185` computes the clustered gross difference. |
| 12 | Family A 24 pooled / family B 96 session cells, Holm correction; descriptive cells excluded | MATCH | `study.py:41-44` sets m=24/96; `study.py:303-310` limits families to with-trend RSI/div confirmatory rows and applies `rk.holm` with those m values. |
| 13 | DEV split [2022-01-01, 2024-07-01); validation [2024-07-01, 2025-07-01), DEV survivors only, once; no holdout | DEVIATES | `study.py:53-57` delegates boundaries to `splits`; `study.py:263-270` gates validation to survivors and caps load at the window end. But `study.py:45`, `217-224` load only from `F:/MTS/Dumps/backtest/raw_1m_*`, not the documented available DEV cache under `F:/MTS/data`; no source in the scoped code bridges these roots. Thus the specified permitted DEV source is not wired into the study. `val_guard` at `study.py:60-65` refuses an existing validation output. |
| 14 | Report regime mix before verdict; survivor conditions n≥30, days≥20, net>0, Holm p<.05, excess t≥2; validation n≥15, net>0, raw p<.05 | MATCH | `study.py:68-70` survivor predicate; `303-315` calculates Holm, survivor list and validation predicate; `322-324` writes/prints regime mix. |

## Findings

1. **DEVIATES — data source wiring (`study.py:45`, `217-224`).** The available machine instructions identify the permitted DEV data at `F:/MTS/data/...`; the implementation searches `F:/MTS/Dumps/backtest/raw_1m_*`. The end-time cap (`study.py:270-271`) is a useful boundary guard but does not establish that these configured roots contain the permitted DEV bars. Point the loader to the authorized source and preserve the exclusive split-end bound before relying on any results.
2. **DEVIATES — fee-net formula (`study.py:27`, `171-177`).** The flat subtraction implements the PRE_REG's declared 0.14% constant, but not all terms in FORMULAS.md §13 (`:352-358`): explicit fee, slippage, and funding-record adjustment are absent. Reconcile the preregistered cost convention with the governing formula before treating net results as formula-compliant.
3. The task’s legacy done_when path names `2026-11-04_gpt-audit-wavetrend-c30-retest.md`; this run writes the instructed current-date artifact `2026-11-05_gpt-audit-wavetrend-c30-retest-1104.md`.

No study, source report, script, or market data was modified or run.
