SOUND

Card: imb-filter-audit-1-map
Date: 2026-10-17 UTC. Stage 1 evidence map; C1-C3 PASS under the current card contract. SOUND means the requested evidence map is complete. It does not certify the original loader, reproduce absent candles, or establish a profitable filter.

## Checked material and reproduction

Source paths below are relative to `MyTradingSys/research/imbalance_qriptal_2026-10-16/filter/`. Read PRE_REG.md:1-124, COUNTS.md:1-47 and trials.csv:1-31, and parsed all of events_dev.csv:1-5977 and trades_dev.csv:1-5977 before reading RESULT.md:1-132. Subsequently read the context pack and the prior `MyTradingSys/research/layer_lab/reports/2026-10-16_imb-filter-audit-1-map.md`. The card has no predecessor receipt/report pointer. Its current C2/C3 explicitly accept documented NOT_IN_DATA gaps, unlike the prior report's completion decision.

Recount command (standard library; exactly the six research inputs below; no market loader):

```powershell
python MyTradingSys/research/layer_lab/imb_filter_audit_1_map_2026_10_17.py.txt
```

Exit 0. The command prints hashes, complete schemas, counts, means and outcome rates, with assertions for the headline, primary trial rows, DEV touch dates, unique day/level keys and shared event/trade fields. This is a committed-table recount, not a new market trial. No market archive, VALIDATION data file or HOLDOUT data file was opened. No git or sync command was run; correspondence to the committed snapshot is supported by all six hashes matching the read-only context pack, without independent commit-history verification.

## Criterion evidence

C1: PASS

MATCH: RESULT.md:10,18,21,28-29,59 versus COUNTS.md:5,13-14, trades_dev.csv:2-5977 and trials.csv:2-3. Use `small == 'True'` for IMB and `small == 'False'` for NOIMB (PRE_REG.md:77,83). Sum the decimal `net_1` strings, divide by n, then subtract the unrounded means. The recount command above implements this directly.

| Group | n | Distinct days | Sum net R | Mean net R | Rounded headline |
|---|---:|---:|---:|---:|---:|
| IMB | 3271 | 708 | -1198.7559488776 | -0.3664799599136655457 | -0.366 |
| NOIMB | 2705 | 692 | -1263.1844077572 | -0.4669812967679112754 | -0.467 |
| IMB minus NOIMB | | | | +0.1005013368542457297 | +0.101 |

The n values sum to 5,976. All 21 event fields equal the corresponding trade fields row for row; there are zero duplicate `(day, level)` keys. H1/H2 counts are 1201/2070 IMB and 1274/1431 NOIMB, matching COUNTS.md:13-14. trials.csv:2-3 stores -0.366480 and -0.466981; both means match within 0.0000005 R (OURS numerical tolerance for six-decimal ledger rounding). The same check passes for LARGE/NOLARGE in trials.csv:4-5. Subtracting the displayed three-decimal group means alone would lose the precision needed to reproduce the displayed difference.

Additional MATCH: the ALL mean is -0.4119712778840 R, gross -0.0622786114414 R, cost 0.3496926665847 R (trades_dev.csv:2-5977; RESULT.md:9,39). These support the rounded negative base result. C1 does not certify reported clustered SE, Holm significance, or all secondary cells.

C2: PASS

MATCH for the audit input inventory and observable DEV decision dates; original-loader isolation is NOT_IN_DATA. The complete six-file research input list and byte-level SHA256 are:

| Input | SHA256 |
|---|---|
| PRE_REG.md | `54edb80ddb649fedfc723e5af398d6bd7eddd01dd646c3b73e5859b5512edb61` |
| COUNTS.md | `c86dfa848952f9cf56355a8c5be3a0693c3a9c806fe78499b7e3078476233070` |
| events_dev.csv | `b21c2b8e9007ad62a75a45c3e468e05e61af8e03d23d1f4520a3679d8dc72462` |
| trades_dev.csv | `6ba7ced4f2c6a701f1dee5932ef5be3e291ce4db2bfb18ae37f34d23683e9c27` |
| trials.csv | `537050806bf10598642e673e2bd3a1fc71d5066639c0ceb6a214641502cda55f` |
| RESULT.md | `17bcf3b22c6d89ca39c8c783f89a295ff069c1e4a8cc71e3985c2f6370eab6f2` |

None is a VALIDATION or HOLDOUT data file. References to those windows inside PRE_REG/RESULT are prose, not files opened by this recount. The command shows identical bounds in events_dev.csv:2-5977 and trades_dev.csv:2-5977: `t = 1648776420000..1719786360000`, or 2022-04-01 01:27 through 2024-06-30 22:26 UTC. There are zero rows at/after 2024-07-01 00:00 UTC and zero discrepancies between `day` and `t // 86400000`; 818 distinct event days. MATCH to COUNTS.md:3,5 and RESULT.md:5 for decision dates.

PRE_REG.md:12-16 prescribes a DEV-only loader and explicitly excludes the lc event table. RESULT.md:5 asserts the original run did not read VALIDATION/HOLDOUT. Neither loader source nor an original-run opened-file manifest, source-candle availability records or exit timestamps is in these six files. DEV touch dates cannot establish that flags and exits used only DEV observations. Thus original-loader isolation and historical file-access compliance remain NOT_IN_DATA, as permitted by C2; they are not inferred from filenames or output dates.

MATCH disclosure: PRE_REG.md:20-22 and RESULT.md:110 acknowledge that KEEP-family selection came from 2024-12..2025-03, within standard VALIDATION. This is inherited selection information, distinct from reading a VALIDATION file during this run. The scope cannot certify selection independence.

C3: PASS

MATCH as documentary evidence: PRE_REG.md:27-28 records the old direction formula `side = 1 if touch_bar_close >= level else -1`; PRE_REG.md:38 chooses previous-close direction instead, and :43 disallows touch-bar target credit. RESULT.md:109 alleges that LC1/LC2 used touch-close direction and credited favourable touch-bar movement. The touch close is unavailable at a resting touch entry; a favourable touch-bar extreme may precede the fill. These are the stated mechanisms, not an independent inspection of the cited out-of-scope source code.

Complete columns present (headers at events_dev.csv:1, trades_dev.csv:1 and trials.csv:1):

```text
events_dev.csv:
day, t, family, level, side, width, w_pct, small, large, ctrl,
small_1h, small_4h, small_12h, small_1d, small_k3, large_k3, ctrl_k3,
small_k3_1h, small_k3_4h, small_k3_12h, small_k3_1d

trades_dev.csv: all 21 event columns above, followed by:
exit_1, kind_1, gross_1, cost_1, net_1, net_m_1,
exit_2, kind_2, gross_2, cost_2, net_2, net_m_2

trials.csv:
cell, block, rr, n, net_R, se
```

NOT_IN_DATA: previous close, all four touch OHLC values, and exit time are absent. `t` is the touch timestamp, and `exit_1`/`exit_2` are summarized exit prices, not timestamps (PRE_REG.md:37,46 and the trade rows). Side alone cannot recover previous close or touch close. No chronological post-touch bars or observed intrabar path is supplied. Consequently these files cannot reproduce direction flips or pre-fill target credit on observed rows.

MATCH: the following rates are supported by the saved `kind_1`/`kind_2` outcomes across trades_dev.csv:2-5977. Each percentage uses all trades in that group, including time exits. The command recomputes the integer counts and rates.

| Group / rr | n | Target count (%) | Stop count (%) | Time count (%) |
|---|---:|---:|---:|---:|
| ALL / 1 | 5976 | 2761 (46.2015) | 3144 (52.6104) | 71 (1.1881) |
| IMB / 1 | 3271 | 1578 (48.2421) | 1643 (50.2293) | 50 (1.5286) |
| NOIMB / 1 | 2705 | 1183 (43.7338) | 1501 (55.4898) | 21 (0.7763) |
| LARGE / 1 | 2702 | 1252 (46.3360) | 1413 (52.2946) | 37 (1.3694) |
| NOLARGE / 1 | 3274 | 1509 (46.0904) | 1731 (52.8711) | 34 (1.0385) |
| CTRLONLY / 1 | 1771 | 783 (44.2123) | 969 (54.7149) | 19 (1.0728) |
| ALL / 2 | 5976 | 1705 (28.5308) | 4025 (67.3527) | 246 (4.1165) |

These reproduce RESULT.md:28-31,38-39,41,89 after rounding. They are saved corrected-rule outcome rates. The 54-69% LC1 HOLD range appears only as a claim in RESULT.md:109, with no supporting original LC1 counts in scope. **Effect on the HOLD rates: NOT_IN_DATA.** Do not subtract 46.2% from 54-69%: the periods, rows and rules are unmatched. Neither magnitude nor net sign of the observed counterfactual rate change is identified here. No invented bars or market data were used.

Exact fixture fields needed by a later Claude-side card (proposed evidence schema, not observations):

- Identity/provenance: `event_id`, `source_file`, `source_sha256`, `source_row`, `day`, `family`, `level`, `width`, `rr`, `touch_t_ms`, `prev_t_ms`, `prev_close`, `touch_open`, `touch_high`, `touch_low`, `touch_close`. Record bar duration and UTC timestamp semantics; every observed bar must open before the DEV cutoff.
- Replay: ordered `bars[{t_ms, open, high, low, close}]` from the prior bar through both exits or the day-end cutoff, plus `entry_price`, `entry_t_ms` (or an explicit unknown-within-minute marker), `stop_price`, `target_price`, `fee_rule`, `gap_rule`, `same_bar_order_rule`, `time_exit_rule`. OHLC cannot reveal the actual intrabar fill/extreme order; if claiming the real order, add timestamped observed trades or lower-resolution path evidence and its provenance. Otherwise report the rule-based ambiguity explicitly.
- Paired calculations: `side_touch_close`, `side_prev_close`, `touch_target_credit`, `exit_price`, `exit_t_ms`, `exit_kind`, `gross_R`, `net_R`, `hold_label`, keyed by `variant` and event. Use four variants crossing previous/touch-close direction with touch-target credit off/on to separate the two changes. Define the HOLD denominator and mapping to outcomes. Include equality/skip handling and day-end censoring.
- Executable evidence: frozen original/corrected function excerpts with source hashes and line references, the expected paired outputs and count aggregation, and a DEV-only input manifest. Observed cases should expose a direction disagreement and a touch-bar target excursion; if absent in the fixture, report that absence rather than fabricate one.

## Findings and assumptions

| Severity | File:line | Classification / finding | Evidence and proposed action |
|---|---|---|---|
| LOW | RESULT.md:10; COUNTS.md:13-14; trials.csv:2-3 | MATCH: headline arithmetic | Independent decimal means and count checks above; retain numbers. |
| HIGH | RESULT.md:5; PRE_REG.md:12-16; events_dev.csv:1; trades_dev.csv:1 | NOT_IN_DATA: original-loader isolation | Obtain a DEV-only access manifest and separately scoped loader review; retain the distinction between observed dates and historical access. Accepted gap for C2. |
| HIGH | RESULT.md:109; PRE_REG.md:27-28,38,43; trades_dev.csv:1 | NOT_IN_DATA: row-level touch defect and HOLD impact | Supply the paired observed DEV fixture above. Documentary mechanism is available; observed counterfactual is absent. Accepted gap for C3. |
| MED | PRE_REG.md:20-22; RESULT.md:110 | MATCH: family choice inherited from standard VALIDATION | Preserve disclosure; do not imply full research independence from that window. |
| MED | RESULT.md:86,100-101 | NOT_IN_DATA: causal attribution to volume alone | The contrast is descriptive; the report itself acknowledges active-period confounding and absent regime control. Treat the phrase about volume carrying the lift as an association pending a separately registered identification design. |
| LOW | PRE_REG.md:39-49,57-70; RESULT.md:80,102,105 | MATCH as disclosed assumptions | Touch-limit fills, numeric thresholds, width, slippage, stop-first and untested wick confirmation are fixed modeling choices, not directly validated fills or the trader's numeric rules. Retain SOURCED/OURS labels. |

Scope limits: commit chronology (PRE_REG.md:5; RESULT.md:127), cited trader quotes/fee sources, upstream builder behavior and earlier trial history behind Holm m=16 were not independently checked. The six files provide references or prescriptions rather than the required external evidence. No market rerun, significance revalidation or change to source research was performed.

## Follow-up cards created

None. The later Claude-side fixture requirements are specified above. Current C1-C3 are PASS because this stage requires an evidence map and explicitly accepts the C2/C3 gaps; the original study's empirical FAIL remains unchanged.
