# Layer Lab Report: Scan of Repo Paths in Done Task Cards Closed Since 2026-10-31

- **Task**: `gemini-scan-done-cards-missing-paths-1101`
- **Lane**: `CODEX`
- **Scanned Cards**: 169 task cards under `MyTradingSys/system/tasks/*.json` marked `done` with `closed` or `refreshed` $\ge$ 2026-10-31
- **Audited Deliverables**:
  - `MyTradingSys/research/gemini_audits_2026-11-01/done_cards_missing_paths.md`
  - `research/gemini_audits_2026-11-01/done_cards_missing_paths.md`
- **Date**: 2026-11-01
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report performs a comprehensive path integrity audit across all 169 task cards completed since 2026-10-31. Every repository path cited in the card `result` or `done_when` criteria was extracted, cleaned, and checked against the tracked files in `git ls-files`.

- **Cards Scanned**: 169
- **Paths Checked**: 300
- **Paths Found**: 271 (90.3%)
- **Paths Missing**: 29 (9.7%)
- **Nearest Existing File**: Identified for each missing path via string distance and directory heuristic.

---

## 2. Taxonomy of Missing Paths

The 29 missing path references cluster cleanly into five operational causes:
1. **Report Date Drift (5 cards)**:
   - Five GPT formula audit cards (`gpt-audit-formulas-vs-positioning-layer`, `trendlines`, `turn_of_candle`, `wavetrend`, `wlow_bounce`) cited deliverable report paths with date prefix `2026-10-30_`, but the actual reports on fast-track carry the `2026-10-31_` prefix.
2. **Runtime Logs and Data Streams (4 cards)**:
   - Dynamic outputs such as `gate_timing.jsonl`, `runtime_data/gate_fail_logs`, and `runtime_data/liq_events/BTCUSDT.jsonl` are local execution artifacts excluded by gitignore.
3. **Pending / Uncommitted Simulator Cards (4 cards)**:
   - `sim_desk/results/<slug>.json` references for exploratory cards that logged trial rows or local figures without committing the JSON descriptor.
4. **Generated HTML Artifacts (1 card)**:
   - `mts_control_room.html` is generated from template `scripts/dev/control_room.tpl.html`.
5. **Subdirectory Relocation / Partial Strings (15 cards)**:
   - Fractal top-level `PRE_REG.md` and `REPORT.md` located within subfolder `p1_split/`; `role/CLAUDE.md` referring to top-level `CLAUDE.md`; test files like `test.js` or `py.txt`.

---

## 3. Epistemic Impact

1. **System Health**: Over 90% of completed card deliverables exist on trunk exactly at their designated paths.
2. **Actionable Clean-up**: Identified report date drift enables subsequent tasks to fix path references in task card metadata or documentation.
