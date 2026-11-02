# BLOCKED — independent Pitchfork EXACT replay could not be reproduced from the specified description

## Checked

- Read `MyTradingSys/research/mts_audit_2026-11-03/AUDIT.md` (sections 1–7), the Pitchfork section of `MyTradingSys/system/LAYERS.md`, `PHASE2_4H_POC_STUDY.md`, `RESEARCH_PITCHFORK_LAYER.md`, the Pitchfork 4H trial ledger, `layer_map.json`, `VERDICTS.csv`, and the audit's JSON/test artifacts. The reference Python implementation was not read or imported.
- Confirmed the requested DEV minute files exist: 2020–2021 in `F:/MTS/data/dev_ext_2019_2021/klines`, 2022 onward in `F:/MTS/data/tom_raw/klines`. No bars after 2024-06-30 were read.
- Ran `python MyTradingSys/research/layer_lab/mts_audit_recheck_1103/recheck.py`.

## Findings

| Severity | Evidence | Result | Detail |
|---|---|---|---|
| HIGH | `AUDIT.md:17-28`; `PHASE2_4H_POC_STUDY.md:39-60`; `RESEARCH_PITCHFORK_LAYER.md:26-45` | BLOCKED | The audited summary specifies causal pivots, next-bar order, 1m walk, stop-first, 4H zigzag 4 / 3%, 1.5% stop and ML target. That does not define enough to reproduce the arm exactly: fork variant coordinate equations, VA construction for this filtered sample, limit fill cancellation/expiry, target evaluation/update timing and placebo sampling mechanics are absent from the audited description. A recreation that supplies those choices would be a new encoding; importing the reference recheck would no longer be independent. Thus the reported n/mean/CI/PF/placebo were not independently confirmed. |
| MED | `VERDICTS.csv`; `recheck.py` output | DISAGREE | The audit reports 117 rows with 54 FAIL; the current file contains 118 data rows: FAIL 55, INCONCLUSIVE 40, UNPARSED 13, BLOCKED 8, PASS 2. |
| MED | `layer_map.json` Pitchfork 4H record; `PHASE2_4H_POC_STUDY.md` Modified Schiff + VA row | AGREE | Stale layer-map figures n=734 and 64.85% conflict with the study row's n=279 and 39.07%; the audit correctly calls out this register/report inconsistency (`AUDIT.md:29`). |
| LOW | `MyTradingSys/system/LAYERS.md:249-268`; `AUDIT.md:41` | AGREE | Layer index records the withdrawn 4H result and lists the independent recheck and operator-fork work as separate cards. Live-bar-count statement is recorded by the audit but not independently measured here. |
| LOW | `AUDIT.md:3-6, 31-77` | PARTIAL | Sections 1 and 3–7 mostly quote registers and opinions. The evidence register is identified in the audit, but this pass did not inspect every underlying research result named in those rows; their numerical claims are not upgraded to independently verified facts. The partial evidence inventory is in `RECHECK.md`. |

## Rerun table

| Arm | n | mean net % | 95% CI | PF |
|---|---:|---:|---|---:|
| STUDY rules | Not independently reproduced | — | — | — |
| CAUSAL pivots | Not independently reproduced | — | — | — |
| EXACT | Not independently reproduced | — | — | — |
| Random-entry placebo | Not independently reproduced | — | — | — |

The data are present; this is a specification/reproducibility block, not a missing-data claim. No later-than-2024-06-30 candles were accessed. The audit's main qualitative conclusion that the prior PASS is unsupported by a causal recheck is consistent with the cited source inconsistency, but its exact replacement statistics remain unverified here.

Files created: `MyTradingSys/research/layer_lab/mts_audit_recheck_1103/recheck.py`, `RECHECK.md`.
Follow-up cards: none created.
