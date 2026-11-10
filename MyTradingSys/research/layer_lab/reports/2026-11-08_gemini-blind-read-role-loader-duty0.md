COVERED: 3 | NOT_COVERED: 4

# Gemini Blind Read Report: `test_role_loader.py` session_planner Duty 0 Case

- **Card**: `gemini-blind-read-of-mytradingsys-tests-`
- **Date**: 2026-11-08 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target Files Audited**:
  - `MyTradingSys/system/roles/session_planner.md` (lines 19-23) [SOURCED: `MyTradingSys/system/roles/session_planner.md:19-23`]
  - `MyTradingSys/tests/test_role_loader.py` (`test_session_planner_has_duty_0_and_fits_the_cap`, lines 311-324) [SOURCED: `MyTradingSys/tests/test_role_loader.py:311-324`]
- **Scope In / Out**:
  - In: `MyTradingSys/tests/test_role_loader.py` (read); `MyTradingSys/system/roles/session_planner.md` (Duty 0) (read); `MyTradingSys/research/layer_lab/reports/2026-11-08_gemini-blind-read-role-loader-duty0.md` (new)
  - Out: no edit to the source files; no live-tree edit, no deploy, no `.secrets` or `.env` read

---

## 1. Specification (Session Planner Duty 0 Text)

From `MyTradingSys/system/roles/session_planner.md:19-23` [SOURCED: `MyTradingSys/system/roles/session_planner.md:19-23`]:
- **Sentence 1 (Heading & Announcement)**: `## Duty 0 (CODE RED, first step): lane floors CODEX >= 8 and GEMINI >= 4 ready cards (A-20261104-1)`
- **Sentence 2 (Trigger condition)**: `Before refining any SONNET card, count ready cards in CODEX (GPT) and GEMINI ([GEMINI] title, lane: CODEX).`
- **Sentence 3 (Floor check)**: `Below a floor:`
- **Sentence 4 (Feeder step 1 - study blind reads)**: `1. Feeder: every study shipped on origin/fast-track (RESULT/REPORT/DEV_CHECK.md) without a [GEMINI] blind read of ... card gets one;`
- **Sentence 5 (Feeder step 2 - gpt spec tests & re-derivation)**: `every shipped .py without spec tests or re-derivation gets gpt-spec-tests-<name> or gpt-rederive-<name> (lane: CODEX, kind: audit, weight: ROUTINE); promote each to ready at once.`
- **Sentence 6 (Seeding fallback)**: `2. Still short: seed ready cards from MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md section 6 until both floors hold.`
- **Sentence 7 (Role hook limit constraint)**: Hook emission length constraint under the 9500 character ceiling (`test_session_planner_has_duty_0_and_fits_the_cap` docstring & assertion).

---

## 2. Test Implementation in `test_role_loader.py`

From `MyTradingSys/tests/test_role_loader.py:311-324` [SOURCED: `MyTradingSys/tests/test_role_loader.py:311-324`]:
```python
    def test_session_planner_has_duty_0_and_fits_the_cap(self):
        """Code Red lane floors (CODEX >= 8, GEMINI >= 4) are Duty 0 of the planner and the emit stays <= 9500 chars."""
        def local_show(repo, rel):
            p = REPO / rel
            return p.read_bytes().decode("utf-8") if p.exists() else None
        f = REPO / rl.ROLES_REL / "session_planner.md"
        body = f.read_bytes().decode("utf-8").replace("\r\n", "\n")
        self.assertIn("## Duty 0", body)
        self.assertIn("CODEX >= 8", body)
        self.assertIn("GEMINI >= 4", body)
        with mock.patch.object(rl, "git_show", local_show), mock.patch.object(rl, "git_sha8", lambda r: "abcd1234"), \
                mock.patch.object(rl, "lease_suffix", lambda n, r: ""):
            n = len(rl.build_text("Session_Planner", REPO, True))
        self.assertLessEqual(n, 9500, f"session_planner emits {n} chars")
```

---

## 3. Sentence-by-Sentence Audit Matrix

| # | Duty 0 Text Item / Clause | Source Reference | Pinned in `test_role_loader.py` | Status | Audit Notes |
|---|---|---|---|:---:|---|
| 1 | `## Duty 0` section presence | `session_planner.md:19` | `self.assertIn("## Duty 0", body)` (`line 318`) | COVERED | Pins that Duty 0 header exists in `session_planner.md`. |
| 2 | `CODEX >= 8` floor requirement | `session_planner.md:19` | `self.assertIn("CODEX >= 8", body)` (`line 319`) | COVERED | Pins literal presence of the string `CODEX >= 8`. |
| 3 | `GEMINI >= 4` floor requirement | `session_planner.md:19` | `self.assertIn("GEMINI >= 4", body)` (`line 320`) | COVERED | Pins literal presence of the string `GEMINI >= 4`. |
| 4 | Count ready cards before refining SONNET cards (`Before refining any SONNET card, count ready cards...`) | `session_planner.md:20` | None | NOT_COVERED | Test only checks string presence in markdown role file; does not assert or simulate planner execution behavior. |
| 5 | Feeder step 1: study shipped on `origin/fast-track` gets `[GEMINI] blind read of ...` card | `session_planner.md:21` | None | NOT_COVERED | Unchecked by test suite in `test_role_loader.py`. |
| 6 | Feeder step 2: shipped `.py` without spec tests gets `gpt-spec-tests-<name>` / `gpt-rederive-<name>` (`lane: CODEX`, `kind: audit`, `weight: ROUTINE`) promoted to `ready` | `session_planner.md:21` | None | NOT_COVERED | Unchecked by test suite in `test_role_loader.py`. |
| 7 | Seeding fallback from `D11_PROGRAMME.md` section 6 if floors still short | `session_planner.md:22` | None | NOT_COVERED | Unchecked by test suite in `test_role_loader.py`. |

### Summary of Counts
- **Total sentences / requirements evaluated**: 7 [OURS]
- **COVERED**: 3 [OURS] (Header presence `## Duty 0`, literal floor tokens `CODEX >= 8` and `GEMINI >= 4`, plus emit cap `<= 9500` chars verified)
- **NOT_COVERED**: 4 [OURS] (Procedural feeder mechanisms, seeding logic from `D11_PROGRAMME.md`, and execution ordering before SONNET card refinement)

### Conclusion
`test_role_loader.py` is a role loader hook test. It pins that the `Session_Planner` role definition contains the Duty 0 section with the Code Red floor numbers (`CODEX >= 8`, `GEMINI >= 4`) and that including Duty 0 preserves the `< 9500` character cap required for Claude prompt injection. The procedural rules within Duty 0 (how the feeder finds studies, seeds cards, and prioritizes queues) are role prompt instructions for human/LLM planner sessions, not executed or mocked by `test_role_loader.py`.
