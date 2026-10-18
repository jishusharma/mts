# Causal bottom/top extension: design and feasibility, not a result

2026-10-14. Every number here is OURS. No additional outcome prices were read for this design. This is a preregistration candidate requiring independent audit, not permission to read existing sealed periods.

## What can be known at the alert

Retain all candidate alerts, failed alerts and late confirmations. Candidate support is a previously available daily/weekly low or a confirmed 4h pivot. A five-bar 4h low pivot at index j requires low[j] strictly below lows[j-2:j] and lows[j+1:j+3]; it becomes usable only at j+2 close. Ties are not pivots. Its availability timestamp, not the pivot's original timestamp, controls access. Mirror highs for tops.

The first candidate reclaim is the completed close returning above the known support after a below-support close. The candidate extreme is the minimum traded price between the initial break and reclaim, all already observed. Freeze its value at alert time. An optional structure confirmation is a completed 1h close above the latest previously confirmed 1h swing high (same five-bar rule). A higher-low sequence requires a second confirmed pivot low above the first; two extra bars of confirmation delay are real and must appear in the ledger. Never move an earlier alert timestamp to the final low after seeing the chart.

Compare candidate reclaim alone, reclaim plus structure confirmation, and reclaim plus higher-low plus structure confirmation. Each costs another counted arm. The exact family/TF grid must be reduced and frozen by the audit card before implementation; no performance look is authorised by this draft. The existing six-pattern DEV results cannot be reused as confirmation of these new structure sequences.

## Three different outcome questions

For each alert use the next minute open E and its frozen candidate low B (top T for shorts). Normaliser A is the simple mean true range of the 20 last fully completed 4h candles at the alert; TR=max(high-low, abs(high-prev_close), abs(low-prev_close)). Incomplete history means NOT_IN_DATA. This definition must be added to canonical FORMULAS.md before coding.

| Outcome family | Forward horizon | Bullish success | Invalidation | Interpretation |
|---|---|---|---|---|
| Local reaction | 24 hours | E+1A traded before B-0.25A | B-0.25A traded first | Did it produce a tradable-size local reaction? |
| Swing low | 30 days | E+3A reached, and no low below B-0.25A for the full window | Any lower breach inside window | Was this low retained through a swing? |
| Persistent low | 180 days | E+5A reached, and no low below B-0.25A for the full window | Any lower breach inside window | A measurable persistence proxy; not proof of a halving-cycle bottom |

For shorts reverse price inequalities. Report success, failure, timeout/no target and right-censored separately; never count incomplete horizons as failures. For local barriers, if both are touched inside one minute, report lower/upper success bounds and resolve with trades before a strategy claim. For persistence outcomes, a later invalidation is failure even if the target was touched earlier. This prevents calling a rally before a deeper low the final bottom. Entry-to-extreme distance and confirmation lag are mandatory readouts; late confirmation may improve precision while making trading economics worse.

## Independent units and power

Cluster alerts around the same candidate extreme, then embargo each test episode through its outcome end. Train/test purging uses the longest 180-day label, not the 1m trigger spacing. Separate descriptive episode recall from event precision; do not let one successful bottom generate thousands of independent successes. Top and bottom episodes remain separate directional questions.

The available frozen candle DEV window is 912 days. Even ignoring warmup and boundary censoring, floor(912/180)=5 disjoint 180-day blocks. Thus the existing window cannot support a precise cycle-bottom probability across bull/bear/trend/range cells. For illustration, even 5 independent successes out of 5 have a two-sided 95% Wilson interval about [56.6%,100%], before selection bias and regime splitting. A 5pp lift above a known 50% baseline needs roughly 784 independent events at 80% power under an optimistic iid normal calculation. This is not achieved by resampling five cycles.

Decision: macro precision claims are INCONCLUSIVE/UNDERPOWERED by design. Use a dated case ledger and forward collection; a cycle detector can be assessed as a hypothesis with wide intervals, not sold as a high-confidence probability. Extend historical data only after a lineage audit defines genuinely eligible development history; do not call previously inspected historical periods OOS. Cross-asset pooling, if proposed, is a separate transfer assumption, not extra BTC cycles.

## Validation and calibration

For each event output alert_time, available_at, trigger_TF, level_TF, parent_phase, local_direction, signature, B/T, A, E, target_time, invalidation_time, label_end, censor_reason and episode_id. Store the untouched raw event features separately from later outcome labels.

Baseline: all first eligible level encounters in the same predeclared phase/session/volatility band, with identical eligibility and entry/exit timing. Add random levels at matched distances as a separate placebo. Compare nested confirmations on common encounter IDs, counting untriggered/missed trades; conditioning only on fills would hide missed opportunities.

Report precision, recall against all retrospectively labelled episodes, confirmation delay, false alerts per month, Brier/log loss relative to the phase base rate and calibration bins with episode-bootstrap uncertainty. Probability fitting must be trained only inside rolling DEV folds, with frozen features, regularisation and label embargo; no full-sample phase percentile thresholds. Fee-net execution with historical funding and both intraminute-order bounds is a later separate strategy step.

## Twelve-slot readiness decision

1. Home: OURS BTC perpetual; local/swing/persistence questions above, no sourced strategy attribution.
2. Source check ledger: NOT_IN_DATA for anonymous YouTube trader; mechanical OURS hypothesis only.
3. Recall/fire rate: NOT_RUN; exact-signal synthetic tests and all-episode ledger required before P&L.
4. Inputs: OHLC available for DEV; trade resolution, historical costs and funding not assembled for this extension.
5. Levels: causal prior-period and delayed-pivot rules specified; independent parity tests required.
6. Economics: normalised outcomes do not establish net P&L; costs and stop distance must be measured.
7. Fills: next-open reference only; passive-order touch/through tests deferred until an order model exists.
8. Management: local bracket versus persistence label deliberately separate; neither is trader-faithful management.
9. Null: first-encounter/episode-matched and random-level comparisons specified above.
10. Power: 180-day proxy has at most five disjoint blocks in current DEV; macro probability claim underpowered.
11. Holdout: no read authorised. Full search lineage and clean forward window needed before validation.
12. Stratification: daily causal phase, trend/range and 4h direction; sparse cells shown, not hidden or promoted.

Verdict: **NOT READY for cycle-probability validation or a P&L backtest.** A local/swing extension is technically feasible after independent design audit; macro inference is sample-limited, not a coding problem. This is the concrete next decision produced by the current research, not a promise that running more minute bars will solve it.
