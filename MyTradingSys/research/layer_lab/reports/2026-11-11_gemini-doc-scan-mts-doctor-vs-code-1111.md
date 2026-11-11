COUNTS: MATCH=9 DIFF=1 NOT_IN_DATA=0

# Audit Report: `MyTradingSys/system/MTS_DOCTOR.md` (AI Health) vs `mts_doctor.py` and Tests

- **Card**: `gemini-doc-scan-mts-doctor-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `MyTradingSys/system/MTS_DOCTOR.md` (read)
  - `scripts/dev/mts_doctor.py` (read)
  - `scripts/dev/test_mts_doctor.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-mts-doctor-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 10 testable claims from `MyTradingSys/system/MTS_DOCTOR.md` focusing on the AI health checks (dead refs, duplicates, cards, skills, boot cost, checklist formatting, and execution flags such as `--no-process` and default `--hours 72`) against `scripts/dev/mts_doctor.py` and `scripts/dev/test_mts_doctor.py`.

Audit outcome across 10 claims:
- **MATCH (9)**: Implementation and test coverage precisely verify 9 documented claims:
  1. Default CLI execution writes `MyTradingSys/research/mts_doctor/REPORT_<utc date>.md` with default `--hours 72`.
  2. `--no-process` flag disables network/process calls and runs AI health and local checks only.
  3. Report Line 1 format strictly outputs `HEALTH: GREEN` or `HEALTH: <n> WARN: <names>`.
  4. DEAD-REF detector inspects guidance files for untracked backticked paths and untracked bare doc names.
  5. DUPLICATE detector flags identical lines >= 80 normalized characters appearing in 2 or more guidance docs.
  6. MEMORY drift detector verifies bidirectional consistency between `MEMORY.md` index links and disk files.
  7. CARD lint detector executes `tasks.py lint` to report card warnings.
  8. SKILL detector inspects `*SKILL.md` files for mandatory YAML frontmatter `name:` and `description:`.
  9. BOOT-COST computes byte sizes of `CLAUDE.md` and largest guidance docs without generating false findings.
- **DIFF (1)**: DUP-CARD claim in `MTS_DOCTOR.md:28-29` asserts that `tasks.py twins` ignores batch siblings created within 30 minutes and silences false pairs via `not_twin_of`. While `tasks.py:162,204` implements `TWIN_BATCH_MIN = 30` and `not_twin_of`, `mts_doctor.py:33` classifies the doctor finding type as `"DUP-CARD"` whereas `tasks.py:692` prints `"TWIN <x> <y>"` and the report output formatter prefix is `[DUP-CARD]` (`mts_doctor.py:322`). More importantly, `MTS_DOCTOR.md:29` claims the finding fix advice is to `silence a false pair with not_twin_of`, while `mts_doctor.py:323` returns `"drop one, or add the other id to not_twin_of"`.
- **NOT_IN_DATA (0)**: None; all 10 evaluated claims have corresponding code in `mts_doctor.py` and/or referenced subsystems.

---

## 2. Clause Comparison Table

| # | Documented Claim in `MTS_DOCTOR.md` | Code & Test Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `MTS_DOCTOR.md:8`: `python scripts/dev/mts_doctor.py [--hours 72]` writes `MyTradingSys/research/mts_doctor/REPORT_<utc date>.md` | `scripts/dev/mts_doctor.py:29,1008-1009,1043-1044,1059`: `OUT_REL = "MyTradingSys/research/mts_doctor"`; `ap.add_argument("--hours", type=int, default=72)`; writes `REPORT_<day>.md`; `scripts/dev/test_mts_doctor.py:53` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:8`, `scripts/dev/mts_doctor.py:29,1008-1009,1043-1044,1059`, `scripts/dev/test_mts_doctor.py:53`). Default CLI argument `--hours` defaults to 72, target directory is `MyTradingSys/research/mts_doctor`, and report filename is `REPORT_<day>.md`. |
| 2 | `MTS_DOCTOR.md:9`: `--no-process = AI health only (no network)` | `scripts/dev/mts_doctor.py:861-862,870-877,1012-1019,1062,1075`: `if not process: return "unavailable", "skipped (--no-process, no network)"`; skips `health_audit.build` and network-bound checks; `scripts/dev/test_mts_doctor.py:36,51` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:9`, `scripts/dev/mts_doctor.py:861-862,870-877,1012-1019,1062,1075`, `scripts/dev/test_mts_doctor.py:36,51`). `--no-process` sets `process=False`, skipping external network API queries (`ci_fetch`, `broadcast_check`, `stale_claims`, `supervisor_idle`, `health_audit`). |
| 3 | `MTS_DOCTOR.md:13`: `Line 1 is HEALTH: GREEN or HEALTH: <n> WARN: <names>. Each check is OK / WARN / unavailable: <why>; none fails or edits.` | `scripts/dev/mts_doctor.py:881-884,887-890,1026`: `def health_line(results): warns = [n for n, s, _ in results if s == "WARN"]; return "HEALTH: GREEN" if not warns else f"HEALTH: {len(warns)} WARN: {', '.join(warns)}"`; `scripts/dev/test_mts_doctor.py:274-281` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:13`, `scripts/dev/mts_doctor.py:881-884,887-890,1026`, `scripts/dev/test_mts_doctor.py:274-281`). Status values are constrained to OK / WARN / unavailable, and line 1 strictly outputs the specified format. |
| 4 | `MTS_DOCTOR.md:27,59`: `DEAD-REF (a path or doc name in guidance that is not tracked)` ... `skips runtime-generated paths ('runtime/sched', 'orderflow')` | `scripts/dev/mts_doctor.py:30-31,265-280`: `PATH_RE` matches paths in backticks; `BARE_DOC_RE` matches uppercase docs in `CLAUDE.md`; skips `re.search(r"/runtime/(sched|orderflow\w*|state)/", ref)`; `scripts/dev/test_mts_doctor.py:38-40` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:27,59`, `scripts/dev/mts_doctor.py:30-31,265-280`, `scripts/dev/test_mts_doctor.py:38-40`). Untracked paths matched by `PATH_RE` and non-existent `*.md` files in `CLAUDE.md` matched by `BARE_DOC_RE` produce `DEAD-REF`. |
| 5 | `MTS_DOCTOR.md:27`: `DUPLICATE (same 80+ char line in 2+ guidance files)` | `scripts/dev/mts_doctor.py:32,283-293`: `DUP_MIN = 80`; checks lines with `len(norm) >= DUP_MIN` across docs; excludes tables/code blocks; `scripts/dev/test_mts_doctor.py:41,103-110` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:27`, `scripts/dev/mts_doctor.py:32,283-293`, `scripts/dev/test_mts_doctor.py:41,103-110`). Normalizes whitespace and strips list prefixes; lines >= 80 chars appearing in >1 file trigger `DUPLICATE` findings (skipping `.SKILL.md` shared rules). |
| 6 | `MTS_DOCTOR.md:27-28`: `MEMORY (index line without file, file without index line)` | `scripts/dev/mts_doctor.py:296-305`: checks `MEMORY.md` index links `](...md)` vs files in `memory_dir`; returns `lists {n} which does not exist` or `{n} is not in MEMORY.md`; `scripts/dev/test_mts_doctor.py:42-43` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:27-28`, `scripts/dev/mts_doctor.py:296-305`, `scripts/dev/test_mts_doctor.py:42-43`). Detects broken index links (`listed - files`) and unindexed orphan files (`files - listed`). |
| 7 | `MTS_DOCTOR.md:28`: `CARD (tasks.py lint warnings)` | `scripts/dev/mts_doctor.py:308-312`: executes `subprocess.run([sys.executable, str(Path(repo) / "scripts" / "dev" / "tasks.py"), "lint"])`; parses warning lines into `("CARD", card_id, ln, fix)`; `scripts/dev/test_mts_doctor.py:45` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:28`, `scripts/dev/mts_doctor.py:308-312`, `scripts/dev/test_mts_doctor.py:45`). Invokes `tasks.py lint` and packages each non-header output line as a `CARD` finding. |
| 8 | `MTS_DOCTOR.md:28-29`: `DUP-CARD (tasks.py twins: two open cards for one job; tasks.py new warns at filing; cards created within 30 min of each other are one batch and never paired; silence a false pair with not_twin_of)` | `scripts/dev/mts_doctor.py:315-325`: runs `tasks.py twins` and maps output to `("DUP-CARD", ...)`; `scripts/dev/tasks.py:162,204,683-686`: `TWIN_BATCH_MIN = 30`; excludes pairs where `abs((ta - tb).total_seconds()) <= TWIN_BATCH_MIN * 60` or in `not_twin_of`; `scripts/dev/test_mts_doctor.py:132-140` | DIFF | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:28-29`, `scripts/dev/mts_doctor.py:315-325`, `scripts/dev/tasks.py:162,204,683-686`, `scripts/dev/test_mts_doctor.py:132-140`). Core twin-batch (30m) and `not_twin_of` suppression match `tasks.py`, but `mts_doctor.py:323` formats suggested fix as `"drop one, or add the other id to not_twin_of"` whereas `MTS_DOCTOR.md:28-29` suggests only `"silence a false pair with not_twin_of"`, and `tasks.py` stdout uses the prefix `TWIN` while `mts_doctor.py` labels the finding `DUP-CARD`. |
| 9 | `MTS_DOCTOR.md:29`: `SKILL (no name/description frontmatter)` | `scripts/dev/mts_doctor.py:327-334`: reads first 600 bytes of `*SKILL.md` files; flags if not `head.startswith("---")` or missing `name:` or `description:`; `scripts/dev/test_mts_doctor.py:44` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:29`, `scripts/dev/mts_doctor.py:327-334`, `scripts/dev/test_mts_doctor.py:44`). Verifies presence of YAML frontmatter `name:` and `description:` in skill definitions. |
| 10 | `MTS_DOCTOR.md:29-30`: `BOOT-COST (CLAUDE.md bytes and the biggest guidance files). Each finding: file:line, what, suggested fix. The script never edits.` | `scripts/dev/mts_doctor.py:360-365,1029`: `boot_cost(repo, docs)` computes CLAUDE.md byte length and top 5 guidance files; formatted in report header outside findings list; `scripts/dev/test_mts_doctor.py:48-56` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:29-30`, `scripts/dev/mts_doctor.py:360-365,1029`, `scripts/dev/test_mts_doctor.py:48-56`). `boot_cost` prints byte breakdown in Part 1 header; `test_writes_only_the_report_and_names_boot_cost_apart_from_findings` verifies it is reported informatively apart from actionable `findings`. |
