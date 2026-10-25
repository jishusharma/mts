# MTS Back Testing with Historical Data

## 1. Data inventory
- Snapshots: `runtime_data\snapshots\BTCUSDT_*.json`; dispatch count 6167, range `2026-09-13T13:20Z` to `2026-09-21T13:23Z`, about 9 days, cadence stated as about 1 file per minute [per dispatch facts]. Coordinator count at read time is 6268 [per discrepancy note]. Arithmetic from range and count implies about 0.48 files per minute, not 1 [inferred].
- Each snapshot embeds `current_price`, `conditions` (`price_vs_va`, `cvd_slope`, `vp_shape`, `fvg_unfilled_count`, `book_imbalance`, `oi_trend`, `funding_extreme`), `weekly_vp`, `daily_vp`, `post_funding_vp`, `intraday_4h_vp`, `structure.{1h,15m,5m}`, `vwap`, `cvd`, `trade_flow`, `funding`, `open_interest`, `oi_breakdown`, `order_flow`, `session`, `session_timing`, `setup_candidates` [per dispatch facts].
- `setup_candidates` is an array; oldest snapshot has 3 entries, newest has 0; no `setup_candidates` means the verdict path returns `NO_TRADE` [per dispatch facts; per excerpt 1].
- Labels: `runtime_data\outcome_labels.json`; dispatch count 6594; coordinator count 6689 stored under `.labels` of a dict whose `.version = 5` [per dispatch facts; per discrepancy note]. Fields include `file`, `ts`, `price`, `vp_shape`, `price_vs_va`, `cvd_slope`, `fwd_return_pct {30m, 60m, 120m}` in percent [per dispatch facts; per excerpt 2].
- Labels do not contain `verdict`, `setup_type`, `zone`, `net_rr`, `proof_count`, `tier`, `mode`, or `direction` [per dispatch facts].
- Labeler `MyTradingSys\runtime\outcome_labeler.py` reads `runtime_data\snapshots\BTCUSDT_*.json`, writes `runtime_data\outcome_labels.json`, runs hourly, skips already-labeled files, and is idempotent [per dispatch facts; per excerpt 4].
- Verdict function: `scripts\core\start-trading-day.ps1` L128-225 per dispatch; L127 per coordinator discrepancy note; body matches disk [per dispatch facts; per discrepancy note].
- Math builder files: `MyTradingSys\runtime\math_object_builder.py` functions `_normalize_snapshot`, `_extract_zones`, `_swing_tf_for_zone`, `_pick_stop_target`, `build_math_object`; CLI wrapper `MyTradingSys\runtime\build_mo_cli.py` takes a snapshot path and writes a math_object JSON [per excerpt 3].
- Schema spec: `MyTradingSys\research\_archive\loose_2026-10\schema_v5.1.0_spec.md`; session fields anchor at US cash open, old fields anchor at 00:00 UTC, two anchors coexist [per dispatch facts].
- Usable: snapshots provide conditions and `setup_candidates` for replay [per dispatch facts; per excerpt 1]; labels provide forward returns [per excerpt 2; per excerpt 4].
- Missing: persisted historical verdicts, label fields for verdict/setup/zone/net_rr/proof/tier/mode/direction, proofDir layout, sample `build_mo_cli.py` output, sample `Compute-Verdict` output [per dispatch facts; per NOT PROVIDED].

## 2. Method options
- Option A: Replay `Compute-Verdict` logic from excerpt 1 against snapshots, then join to labels. Cost: medium-high [inferred]. Evidence quality: high if faithful to excerpt 1 [inferred]. Limits: `proofDir` layout unknown, no sample output, and availability of `top.math` fields inside `setup_candidates` is not specified [per excerpt 1; per NOT PROVIDED; inferred].
- Option B: Label-only conditional analysis using `vp_shape`, `price_vs_va`, `cvd_slope`, and forward returns. Cost: low [inferred]. Evidence quality: medium-low because labels lack verdict/setup/zone/net_rr/proof/tier/mode/direction [per dispatch facts]. Limits: cannot evaluate verdict path, RR gates, tiering, proof thresholds, or flow suppression [per excerpt 1; inferred].
- Option C: Build math objects via `MyTradingSys\runtime\build_mo_cli.py`, then replay. Cost: high [inferred]. Evidence quality: potentially high but unverified; no sample output is provided [per NOT PROVIDED; per excerpt 3]. Limits: extra moving parts, schema alignment unknown, and proofDir still unknown [inferred].
## 3. Chosen method
- Choose Option A: replay the `Compute-Verdict` logic from excerpt 1 over `runtime_data\snapshots\BTCUSDT_*.json`, then join reconstructed verdict records to `runtime_data\outcome_labels.json` by `file` and, if needed, by `ts` [per excerpt 1; per excerpt 2; inferred].
- Why: labels lack verdict and setup fields, so only replay can produce verdict-level buckets such as `NO_TRADE`, `WAIT_RR`, `WAIT_FAR`, `WAIT_TRIGGER`, `WAIT_PROOF`, `WATCH`, and `SETUP_FORMING` [per dispatch facts; per excerpt 1; inferred].
- Reject Option B because it cannot test the verdict path or its gates [per dispatch facts; inferred].
- Reject Option C for the first pass because no sample `build_mo_cli.py` output is provided and the `proofDir` layout is missing; it adds dependencies before the core replay is validated [per NOT PROVIDED; inferred].

## 4. Validation gates
- Snapshot-label join: at least 95% of snapshot files must match a label by `file`; secondary check at least 95% match by `ts` within 1 second [inferred].
- Horizon completeness: at least 99% of joined rows must have non-null `fwd_return_pct` for 30m, 60m, and 120m [per excerpt 2; inferred].
- No-candidate rule: 100% of snapshots with `setup_candidates` length 0 or null must produce `NO_TRADE` [per excerpt 1].
- Verdict reconstruction spot check: 20 out of 20 hand-checked snapshots must match excerpt-1 logic across oldest, newest, and no-candidate cases [inferred].
- Cadence: median inter-snapshot gap <= 150 seconds and 95th percentile gap <= 600 seconds [per dispatch facts; per discrepancy note; inferred].
- Unlabeled after 120m: <= 5% of eligible snapshots [per excerpt 4; inferred].
- Bucket minimum: each primary verdict bucket (`NO_TRADE`, `WAIT_RR`, `WAIT_FAR`, `WAIT_TRIGGER`, `WAIT_PROOF`, `WATCH`, `SETUP_FORMING`) should have n >= 30 for reporting; sparse buckets must be flagged [per excerpt 1; inferred].
- Drift check: rerun on same inputs must produce >= 99% verdict agreement [inferred].
- Multiple testing: pre-register <= 5 hypotheses and report FDR at q = 0.10 [UNVERIFIED-WEB].
- These are proposed gates, not executed results [inferred].
## 5. Known traps
- Label leakage: `fwd_return_pct` at 30m, 60m, and 120m is future information relative to snapshot time; features at time t must not use labels from t+30m or later [per excerpt 2; per excerpt 4; inferred].
- Verdict drift: dispatch says L128, coordinator says L127; the B058 mode classifier, broken-value override, and flow contradiction suppression can change verdicts across versions [per excerpt 1; per discrepancy note].
- Snapshot cadence: stated as about 1 file per minute, but counts over about 9 days imply about 0.48 files per minute; uneven sampling can bias buckets [per dispatch facts; per discrepancy note; inferred].
- Missing labels: labels count exceeds snapshots; excerpt 2 shows a label dated `2026-09-12`, outside the snapshot range start `2026-09-13`; labels also lack verdict fields [per dispatch facts; per excerpt 2; per discrepancy note].
- Multiple testing: many verdict buckets, horizons, filters, and mode overrides increase false-discovery risk [inferred; UNVERIFIED-WEB].
- Two time anchors: session fields anchor at US cash open; old fields anchor at 00:00 UTC [per dispatch facts].
- Unknown proofDir layout and no sample outputs: `proofDir` only appears as a parameter name, and no sample `build_mo_cli.py` or `Compute-Verdict` output is provided [per excerpt 1; per NOT PROVIDED].

## 6. Code spec
- Inputs: `runtime_data\snapshots\BTCUSDT_*.json`; `runtime_data\outcome_labels.json`; `scripts\core\start-trading-day.ps1` L128-225, or L127 per discrepancy note; `MyTradingSys\research\_archive\loose_2026-10\schema_v5.1.0_spec.md`; optional `MyTradingSys\runtime\math_object_builder.py`, `MyTradingSys\runtime\build_mo_cli.py`, and `MyTradingSys\runtime\outcome_labeler.py` [per dispatch paths; per discrepancy note].
- Outputs: a per-snapshot reconstructed verdict record with `file`, `ts`, `price`, `verdict`, `reason`, `setup`, `zone`, `net_rr`, `proof`, `mode`, `direction`, joined to label fields `vp_shape`, `price_vs_va`, `cvd_slope`, and `fwd_return_pct` for 30m, 60m, 120m [per excerpt 1; per excerpt 2]. Output path is not assigned in dispatch; operator must provide it [inferred].
- Files: use only the paths listed above; no new paths are invented here [per dispatch paths; inferred].
- Dry-run command: no command text is provided in dispatch, and this worker cannot run commands; operator should supply a single-snapshot dry-run invocation for the replay harness or for `MyTradingSys\runtime\build_mo_cli.py`, writing to stdout only [per NOT PROVIDED; inferred].
## 7. Open questions for the operator
1. What is the `proofDir` file layout and default value `"aligned"`? [per excerpt 1]
2. Do `setup_candidates` entries always include `top.math.net_rr`, `top.math.net_rr_sanity`, `top.math.tier`, `top.score.proof_count`, `top.zone.name`, `top.zone.price`, and `top.direction`? [per excerpt 1; inferred]
3. Which count set is authoritative: dispatch 6167 snapshots / 6594 labels, or coordinator 6268 snapshots / 6689 labels? [per discrepancy note]
4. Why does one label file reference `BTCUSDT_2026-09-12_1789227015940.json` with `ts` `2026-09-12`, outside the snapshot range `2026-09-13` to `2026-09-21`? [per excerpt 2; per dispatch facts]
5. Does `Compute-Verdict` start at L127 or L128? [per discrepancy note]
6. What output path and schema should the backtest table use? [inferred]
7. How should the two schema time anchors be handled in the backtest? [per dispatch facts]
8. Are multiple-testing corrections desired, and at what q value? [UNVERIFIED-WEB; inferred]
9. Should `WAIT_*` buckets be reported separately or merged? [per excerpt 1; inferred]
10. Can sample `build_mo_cli.py` output and sample `Compute-Verdict` output be provided? [per NOT PROVIDED]

TASK: Produce planning document titled MTS Back Testing with Historical Data. [inferred]
STATUS: Draft written from dispatch excerpts only; no commands run. [inferred]
SUMMARY: First pass is replay of `Compute-Verdict` logic over snapshots joined to forward-return labels. [inferred]
FINDINGS: Main blockers are missing historical verdicts, label-field gaps, count/line discrepancies, and unknown proofDir layout. [inferred]
NEXT: Operator to answer open questions and provide output path plus dry-run invocation. [inferred]