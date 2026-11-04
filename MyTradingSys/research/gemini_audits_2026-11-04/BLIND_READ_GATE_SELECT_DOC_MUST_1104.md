# Blind Read Audit: `scripts/dev/gate_select.py` `DOC_MUST`

- **Card**: `gemini-blind-read-of-scripts-dev-gate-se`
- **Target File**: `scripts/dev/gate_select.py` (lines 50-80)
- **Test File**: `scripts/dev/test_gate_select.py`
- **Date**: 2026-11-04 UTC
- **Reviewer**: Gemini (Worker on lane CODEX)

---

## 1. Context and Scope

In `scripts/dev/gate_select.py:58-62`, `DOC_MUST` maps specific document and data file path patterns to the gating step required to validate them before shipping:

```python
DOC_MUST = {
    "3tl": CARD_RE,                                                                 # dsabr-c1..c8 promoted to ready: red at 3tl
    "3af": re.compile(r"^MyTradingSys/system/OPERATOR_DECISIONS\.md$"),            # Home hub excerpt over its 30000 B cap
    "4d": re.compile(r"^MyTradingSys/system/handover/[^/]+\.md$"),                 # test_integrity forbidden refs
}
```

Where `CARD_RE` is defined at line 55:
```python
CARD_RE = re.compile(r"^MyTradingSys/system/tasks/[^/]+\.json$")   # a card in the diff brings step 3tl (task-card lint) with it
```

---

## 2. DOC_MUST Pattern Routing & Sample Paths

For each entry in `DOC_MUST`, matching paths trigger the designated step, while non-matching paths route according to standard doc rules (or escape to `[]` when changes are doc-only).

### Key 1: `"3tl"` (Task-Card Lint)
- **Target Step**: `3tl` (`python scripts/dev/tasks.py lint`)
- **Regex**: `^MyTradingSys/system/tasks/[^/]+\.json$` (`scripts/dev/gate_select.py:55`)
- **Intended Trip**: Catches malformed or unlinted task cards (e.g. invalid JSON, missing required fields, schema violations) when promoting cards to `ready`.
- **Matching Path**: `MyTradingSys/system/tasks/task-gemini-blind-read.json`
  - Routes to: `('docs', ['3tl'])`
- **Non-Matching Path**: `MyTradingSys/system/tasks/archive/task-old.json` (or `MyTradingSys/system/claims/claim.json`)
  - Subdirectories under `tasks/` fail `[^/]+` and route to `('docs', [])` without running `3tl`.
  - Non-task json files (e.g. `MyTradingSys/system/groups.json`) do not match and run no `3tl` lint.

### Key 2: `"3af"` (Artifact Hub Tests)
- **Target Step**: `3af` (`python scripts/dev/test_artifacts.py`)
- **Regex**: `^MyTradingSys/system/OPERATOR_DECISIONS\.md$` (`scripts/dev/gate_select.py:60`)
- **Intended Trip**: Ensures edits to `OPERATOR_DECISIONS.md` do not push the MTS Home hub artifact over its 30,000 byte limit.
- **Matching Path**: `MyTradingSys/system/OPERATOR_DECISIONS.md`
  - Routes to: `('docs', ['3af'])`
- **Non-Matching Path**: `MyTradingSys/system/OPERATOR_INBOX.md` (or `MyTradingSys/system/COMPILED_DECISIONS.md`)
  - Routes to: `('docs', [])`.

### Key 3: `"4d"` (Doc Integrity Shard)
- **Target Step**: `4d` (`pytest MyTradingSys/tests/docs` or `test_integrity`)
- **Regex**: `^MyTradingSys/system/handover/[^/]+\.md$` (`scripts/dev/gate_select.py:61`)
- **Intended Trip**: Prevents forbidden cross-references, stale links, or format breaches in supervisor handover files.
- **Matching Path**: `MyTradingSys/system/handover/SUPERVISOR_B.md`
  - Routes to: `('docs', ['4d'])`
- **Non-Matching Path**: `MyTradingSys/system/handover/archive/SUPERVISOR_A_202610.md` (or `MyTradingSys/system/SUPERVISOR.md`)
  - Subdirectories under `handover/` fail `[^/]+` and route to `('docs', [])`.
  - Root markdown files like `MyTradingSys/system/RELAY.md` do not match and run no `4d`.

---

## 3. Analysis: Escaping to "No Gate"

1. **Intended Design**:
   - By policy (`DOC_STEPS = ()`, line 54), pure documentation ships (`mode == "docs"`) bypass full local regression test suites (`steps = []`), relying on CI behind the gate unless explicitly trapped by `DOC_MUST`.
   - `DOC_MUST` selectively pulls in cheap targeted gates (`3tl`, `3af`, `4d`) for known high-risk document types that caused reverts in past commits (`gate_gap_2026-11-03`).

2. **Observed Boundary Escapes**:
   - **Nested Directories**: Neither `tasks/` nor `handover/` regex supports nested paths (they use `[^/]+`), meaning files placed in subfolders (e.g. `MyTradingSys/system/tasks/sub/task.json`) escape the check. Currently all active cards and handovers live flat in those directories.
   - **Other System Docs**: Docs such as `MyTradingSys/system/PLAN_24H_2026-11-04.md` or `MyTradingSys/system/ANNOUNCEMENTS.md` have no `DOC_MUST` entry and route to `('docs', [])` (zero gates).
   - **Research Notes**: Files in `MyTradingSys/research/**` that are markdown or data (except trial ledger csvs handled via `must_extras`) route to `('docs', [])`.

3. **Routing Correctness**:
   - Each defined regex correctly targets exactly the intended path and triggers the exact corresponding test step without triggering false-positive smoke runs.

---

## VERDICT: SOUND

## Claude spot-check (Builder gem-review-chain-1104)

- Checked 5 claims against trunk `scripts/dev/gate_select.py`: DOC_STEPS = () at line 54 AGREE; CARD_RE at line 55 AGREE; DOC_MUST spanning lines 58-61 AGREE; "3af" regex at line 60 AGREE; "4d" regex at line 61 AGREE.
- Not checked: the routing outputs `('docs', [...])` were not executed, and the nested-directory escape claims were not tested.
- Outcome: 5 of 5 AGREE, 0 DISAGREE. Card closed.
