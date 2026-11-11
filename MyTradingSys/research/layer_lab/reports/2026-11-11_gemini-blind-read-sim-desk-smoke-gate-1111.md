Counts: MATCH: 4, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of Sim Desk Results Smoke-Gate Selection (`70857d4a0`)

- **Card ID**: `gemini-blind-read-sim-desk-smoke-gate-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Commit Audited**: `70857d4a0f8ec132511227944bc78e2528acda19` ("Result: root sim_desk/results/*.json selects the smoke gate, not fail-closed full (test fails on old code)")
- **Scope In Read**:
  - `scripts/dev/gate_select.py` (read; git show `70857d4a0`)
  - `scripts/dev/test_gate_select.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-sim-desk-smoke-gate-1111.md` (new)
- **Scope Out**: No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.

---

## Verification Table

| Clause ID | Clause Description | Target Sources / Functions | Status | File:Line Citations & Detailed Audit Findings |
|---|---|---|---|---|
| C1 | (1) root sim_desk/results/*.json maps to the smoke gate | `scripts/dev/gate_select.py:31,95-96,306-312` | MATCH | **`scripts/dev/gate_select.py:31`** [gate_select.py:31](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/gate_select.py#L31): defines `RESULT_DATA_RE = re.compile(r"^sim_desk/results/[^/]+\.json$")`.<br>**`scripts/dev/gate_select.py:95-96`** [gate_select.py:95-96](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/gate_select.py#L95-L96): in `_is_config(f)`, checks `if RESULT_DATA_RE.match(f) and not FULL_RE.match(f): return True`.<br>**`scripts/dev/gate_select.py:306-312`** [gate_select.py:306-312](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/gate_select.py#L306-L312): in `explain()`, when `_is_config(f)` is True, it adds name-matching and named steps to `picked` and executes `continue` instead of dropping to line 313-314 (`return "full", ... "fail closed"`), resolving to mode `"smoke"` at line 325. |
| C2 | (2) other unknown paths still fail closed to the full gate | `scripts/dev/gate_select.py:31,95-96,313-314` | MATCH | **`scripts/dev/gate_select.py:31`** [gate_select.py:31](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/gate_select.py#L31): `RESULT_DATA_RE` strictly anchors regex `^sim_desk/results/[^/]+\.json$` ensuring non-root files (e.g. `sim_desk/results/sub/x.json`) and non-json files (e.g. `sim_desk/results/run.py`) do not match.<br>**`scripts/dev/gate_select.py:95-96`** [gate_select.py:95-96](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/gate_select.py#L95-L96): `_is_config(f)` requires `not FULL_RE.match(f)`, so any live paths (e.g. `MyTradingSys/execution/x.json`) are excluded.<br>**`scripts/dev/gate_select.py:313-314`** [gate_select.py:313-314](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/gate_select.py#L313-L314): `if not f.endswith(".py") or not f.startswith(CODE_DIRS): return "full", list(all_nums), f"full: {f} matches no rule (fail closed: not a .py under a known code folder)"` ensures unknown paths fail closed to the full gate. |
| C3 | (3) the new test asserts clause 1 | `scripts/dev/test_gate_select.py:263-270` | MATCH | **`scripts/dev/test_gate_select.py:263-270`** [test_gate_select.py:263-270](file:///F:/MTS/gq/gemini-blind-read-sim-desk-smoke-gate-1111/scripts/dev/test_gate_select.py#L263-L270): `FastGateRules.test_sim_desk_result_json_is_smoke_not_full` directly asserts:<br>- `self.assertEqual(self.sel("sim_desk/results/habib-plan-hit-rate-1104.json")[0], "smoke")` (asserts clause 1).<br>- It also asserts clause 2 guardrails:<br>  `self.assertEqual(self.sel("sim_desk/results/run.py")[0], "full")`<br>  `self.assertEqual(self.sel("sim_desk/results/sub/x.json")[0], "full")`<br>  `self.assertEqual(self.sel("MyTradingSys/execution/x.json")[0], "full")`. |
| C4 | (4) the same test would fail on the code before the commit (reason from the diff) | `scripts/dev/gate_select.py:31,95-96,313-314` vs commit diff `70857d4a0` | MATCH | **Diff analysis (`git show 70857d4a0`)**: Prior to commit `70857d4a0`, lines 31 and 95-96 did not exist in `scripts/dev/gate_select.py`. Therefore, for path `"sim_desk/results/habib-plan-hit-rate-1104.json"`:<br>1. `_is_doc(f)` returned `False` (not under `DATA_DIRS` at line 23).<br>2. `_is_config(f)` returned `False` (not in `CONFIG_FILES` or `scripts/dev/`).<br>3. In `explain()`, execution reached line 313: `not f.endswith(".py") or not f.startswith(CODE_DIRS)` was `True`.<br>4. Result returned was `("full", list(all_nums), "full: sim_desk/results/habib-plan-hit-rate-1104.json matches no rule (fail closed: not a .py under a known code folder)")`.<br>5. Therefore `self.assertEqual(self.sel("sim_desk/results/habib-plan-hit-rate-1104.json")[0], "smoke")` in `test_gate_select.py` failed with `AssertionError: 'full' != 'smoke'`. Verified against pre-commit AST/code. |

---

## Summary of Findings

- Total clauses audited: 4
- **MATCH**: 4
- **DIFF**: 0
- **NOT_IN_DATA**: 0
- All 4 clauses are accurately implemented, verified, and substantiated by code and diff evidence.
