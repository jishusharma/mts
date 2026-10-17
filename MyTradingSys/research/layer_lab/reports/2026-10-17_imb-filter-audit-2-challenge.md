SOUND

Card: imb-filter-audit-2-challenge
Date: 2026-10-17 UTC. Independent challenge, C1-C3 PASS under the stated contract. This accepts the audit deliverable, not the original loader or a causal/profitable trading claim.

## Material checked and command

All source paths below are relative to `MyTradingSys/research/imbalance_qriptal_2026-10-16/filter/`. Read PRE_REG.md:1-124, COUNTS.md:1-47, RESULT.md:1-132, trials.csv:1-31 and parsed every row of events_dev.csv:1-5977 and trades_dev.csv:1-5977. Original sources and independent calculations preceded reading the predecessor report identified by `MyTradingSys/system/tasks/imb-filter-audit-1-map.json`: `MyTradingSys/research/layer_lab/reports/2026-10-17_imb-filter-audit-1-map.md`. Subsequently read the context pack as reference.

```powershell
python MyTradingSys/research/layer_lab/imb_filter_challenge.py.txt
```

Exit 0; all headline assertions passed. This standard-library recount opens exactly the six research files listed below, no market data. No VALIDATION/HOLDOUT data, loader code, git or sync commands were used. It is table verification, not a new market trial. The independent challenge additionally reconstructs net R from price/side/width rather than merely averaging saved net returns.

## Criteria

C1: PASS

MATCH: COUNTS.md:5,13-14; PRE_REG.md:46-48,77,83; RESULT.md:10,18,28-29,59; trades_dev.csv:2-5977; trials.csv:2-3. Select IMB with `small == 'True'` and NOIMB with `small == 'False'`, average `net_1`, subtract unrounded means.

| Group | n | Days | Mean stored net R | Independently recomputed from prices | Headline |
|---|---:|---:|---:|---:|---:|
| IMB | 3271 | 708 | -0.366479959913666 | -0.366479920955719 | -0.366 |
| NOIMB | 2705 | 692 | -0.466981296767911 | -0.466981382150356 | -0.467 |
| Difference | | | +0.100501336854246 | +0.100501461194637 | +0.101 |
| ALL | 5976 | 818 | -0.411971277884003 | -0.411971295207977 | -0.412 |

The price calculation is `(side*(exit_1-level) - 0.0007*(level+exit_1))/width`, directly from PRE_REG.md:46-47. The maximum row discrepancy is 0.000006384054 R; the price columns are rounded, so their reconstruction is not bit-identical. Both methods reproduce every requested headline. Ledger means match within 0.0000005 R (OURS tolerance for six-decimal rounding). All 21 shared event/trade fields match across all 5976 rows; duplicate `(day, level)` keys: zero. This challenges duplicated/changed membership and simple fee/arithmetic errors; it does not validate how exit prices were obtained.

C2: PASS

MATCH: audit input inventory and recorded decision dates. Full research input list, prefixed by the source directory above, with byte SHA256:

| File | SHA256 |
|---|---|
| RESULT.md | `17bcf3b22c6d89ca39c8c783f89a295ff069c1e4a8cc71e3985c2f6370eab6f2` |
| PRE_REG.md | `54edb80ddb649fedfc723e5af398d6bd7eddd01dd646c3b73e5859b5512edb61` |
| COUNTS.md | `c86dfa848952f9cf56355a8c5be3a0693c3a9c806fe78499b7e3078476233070` |
| trades_dev.csv | `6ba7ced4f2c6a701f1dee5932ef5be3e291ce4db2bfb18ae37f34d23683e9c27` |
| events_dev.csv | `b21c2b8e9007ad62a75a45c3e468e05e61af8e03d23d1f4520a3679d8dc72462` |
| trials.csv | `537050806bf10598642e673e2bd3a1fc71d5066639c0ceb6a214641502cda55f` |

All match the context-pack and predecessor receipt hashes. Commit history was not independently inspected. No VALIDATION or HOLDOUT data file is among these inputs; references to those windows in prose are not input data reads.

The command verifies all touch times in events_dev.csv:2-5977 and trades_dev.csv:2-5977 lie in 2022-04-01..2024-06-30: minimum 2022-04-01 01:27 UTC, maximum 2024-06-30 22:26 UTC, 818 days. Every `day` equals `t // 86400000`; zero timestamps at/after 2024-07-01. MATCH to COUNTS.md:3,5 and the decision-date portion of RESULT.md:5.

**Original-loader isolation: NOT_IN_DATA.** PRE_REG.md:12-16 prescribes the guard and RESULT.md:5 asserts compliance, but the six files contain neither loader implementation nor historical file-access manifest, flag-candle availability timestamps or exit timestamps. Output touch dates cannot establish historical read isolation. The inherited KEEP selection from 2024-12..2025-03 is explicitly disclosed in PRE_REG.md:20-22 and RESULT.md:110; therefore DEV decision dates do not imply research independence from VALIDATION-derived selection information. This documented gap is accepted by C2.

C3: PASS

MATCH as documentation only: PRE_REG.md:27-28 and RESULT.md:109 give the old side formula `1 if touch_bar_close >= level else -1`. A touch-bar close is not available when a resting order fills during that bar. PRE_REG.md:38 replaces it with previous-close direction (equal skipped); :43 denies target credit on the touch bar because a favourable extreme could precede entry. The six files document these mechanisms but cannot independently demonstrate their execution on an observed bar.

Complete present columns, from events_dev.csv:1, trades_dev.csv:1 and trials.csv:1:

```text
events_dev.csv:
day,t,family,level,side,width,w_pct,small,large,ctrl,small_1h,small_4h,
small_12h,small_1d,small_k3,large_k3,ctrl_k3,small_k3_1h,small_k3_4h,
small_k3_12h,small_k3_1d
trades_dev.csv: all event columns, plus:
exit_1,kind_1,gross_1,cost_1,net_1,net_m_1,exit_2,kind_2,gross_2,cost_2,net_2,net_m_2
trials.csv:
cell,block,rr,n,net_R,se
```

NOT_IN_DATA: previous close, all touch OHLC values and exit time are absent. `exit_1`/`exit_2` are prices (also substantiated by the price-based calculation above), not timestamps; `t` identifies the touch. Side cannot recover the missing closes. There are no ordered post-touch bars or observed intrabar path.

MATCH: saved outcome counts below are independently counted from trades_dev.csv:2-5977 by the command. Percentages include time exits in the denominator, matching RESULT.md:28-29,32,39,41 after rounding where those cells are published.

| Group / rr | n | Target count (%) | Stop count (%) | Time count (%) |
|---|---:|---:|---:|---:|
| IMB / 1 | 3271 | 1578 (48.2421) | 1643 (50.2293) | 50 (1.5286) |
| NOIMB / 1 | 2705 | 1183 (43.7338) | 1501 (55.4898) | 21 (0.7763) |
| ALL / 1 | 5976 | 2761 (46.2015) | 3144 (52.6104) | 71 (1.1881) |
| IMB / 2 | 3271 | 943 (28.8291) | 2147 (65.6374) | 181 (5.5335) |
| NOIMB / 2 | 2705 | 762 (28.1701) | 1878 (69.4270) | 65 (2.4030) |
| ALL / 2 | 5976 | 1705 (28.5308) | 4025 (67.3527) | 246 (4.1165) |

**Effect on the HOLD rates: NOT_IN_DATA.** RESULT.md:109 supplies only an asserted LC1 range of 54-69%, not paired LC1 counts. Subtracting these from the saved 46.2015% target rate would mix periods, trade populations and rules. Neither the size nor net sign of the counterfactual rate change can be reconstructed here. No bars were invented and no market data was read.

Exact fixture fields proposed (OURS evidence schema) for a later Claude-side card:

- Provenance and identity: `event_id, source_file, source_sha256, source_row, day, family, level, width, rr, bar_duration_ms, touch_t_ms, prev_t_ms, prev_close, touch_open, touch_high, touch_low, touch_close`; UTC timestamp semantics and DEV-only input manifest.
- Chronological replay: `bars[{t_ms,open,high,low,close}]` from previous bar through both exits/day end; `entry_price, entry_t_ms, stop_price, target_price, fee_rule, gap_rule, same_bar_order_rule, time_exit_rule, equality_skip_rule`. Mark entry time unknown within minute when appropriate. Any assertion about actual pre/post-fill extremes additionally needs timestamped observed trades/path evidence with provenance; OHLC alone cannot prove that sequence.
- Paired outputs: `variant, side_touch_close, side_prev_close, touch_target_credit, exit_price, exit_t_ms, exit_kind, gross_R, net_R, hold_label, hold_denominator, skipped`. Cross both side rules with target-credit on/off on the same DEV events, preserving skip/censor handling, to isolate each mechanism.
- Frozen original/corrected function excerpts, line references and hashes; expected paired results and count aggregation. Include observed direction disagreement and target excursion if available, explicitly report absent cases. Do not fabricate observed bars to fill the gap.

## Findings and resolution against predecessor

| Severity | Source | Classification / finding | Evidence and proposed action |
|---|---|---|---|
| LOW | RESULT.md:10; PRE_REG.md:46-47; trials.csv:2-3 | MATCH: headline survives independent arithmetic challenge | Stored means and price-based reconstruction above; retain headline. |
| HIGH | RESULT.md:5; PRE_REG.md:12-16; trades_dev.csv:1 | NOT_IN_DATA: original-loader isolation | Dates certify recorded decisions only; obtain historical access manifest and separately scoped loader review. |
| HIGH | RESULT.md:109; PRE_REG.md:27-28,38,43; trades_dev.csv:1 | NOT_IN_DATA: observed defect and HOLD-rate effect | Documentation identifies mechanism; missing bars prevent reproduction. Supply paired fixture above. |
| MED | PRE_REG.md:20-22; RESULT.md:110 | MATCH: inherited selection from standard VALIDATION | Preserve disclosure; do not equate DEV output dates with fully independent selection. |
| MED | RESULT.md:86,100-101 | NOT_IN_DATA: volume as causal source of lift | The report itself acknowledges clustering/confounding and no regime control; retain descriptive association, avoid causal attribution. |

No material numerical disagreement with the predecessor remains: headline, hashes, touch dates and ALL outcome counts independently agree. One wording correction to its C1 discussion: subtracting displayed -0.366 and -0.467 does happen to give +0.101 here; the general need for unrounded values remains valid, but that particular displayed subtraction does not change this headline. Source-based resolution: trials.csv:2-3 and RESULT.md:10,59. Our independent price reconstruction adds evidence against arithmetic/fee mistakes without claiming to validate the absent price path.

Clustered SE, Holm history, commit chronology, original code behavior and secondary-cell significance were not independently certified. SOUND applies to this bounded audit; the empirical study FAIL is unchanged (RESULT.md:18-19).

## Follow-up cards created

None. Later Claude-side fixture requirements are specified above; no source research files were changed.
