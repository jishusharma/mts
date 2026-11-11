counts MATCH=8 DIFF=0 NOT_IN_DATA=0

# Blind Read Report: `scripts/dev/role_loader.py` against its Docstring

- **Date**: 2026-11-12
- **Auditor**: Gemini 3.8 Flash (Low)
- **Target**: `scripts/dev/role_loader.py`
- **Scope In**:
  - `scripts/dev/role_loader.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-role-loader-docstring-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## Clause Verification Table

| # | Docstring Clause (Quote & file:line) | Implementation Citation & Verification (Quote & file:line) | Status | Notes |
|:---|:---|:---|:---|:---|
| 1 | "loads a role's workflow deterministically when the operator opens a session with \"You are Eagle_Eyes\" (or \"I need a pipeliner\" ...), and lets the operator verify it in one glance." (`scripts/dev/role_loader.py:1-2`) | SOURCED (`scripts/dev/role_loader.py:81,223-252,506-554`): `PREFIX = r"(?:you are\|you're\|act as\|be the\|be\|role:\|i need(?: an\| a\| the)?\|start(?: an\| a\| the)?)"`; `match_roles(prompt, roles)` scans prefixes and triggers; `handle()` builds and returns injection JSON. | MATCH | Role trigger phrases like "You are Eagle_Eyes" and "I need a pipeliner" match registered roles deterministically and inject the workflow banner. |
| 2 | "Header = line 1 of every MyTradingSys/system/roles/*.md: `<!-- role: <Name> \| version: v<N> \| token: <word>-<word> \| triggers: a, b, c -->`" (`scripts/dev/role_loader.py:4-5`) | SOURCED (`scripts/dev/role_loader.py:79-80,85-105`): `HEADER_RE = re.compile(r"^<!--\s*role:\s*(?P<name>[^\|]+?)\s*\|\s*version:\s*(?P<version>v\d+(?:\.\d+)*)\s*\|\s*token:\s*(?P<token>PENDING\|[a-z]+-[a-z]+)\s*\|\s*triggers:\s*(?P<triggers>[^>]*?)\s*-->\s*$")`; `parse_header(text)` parses line 1 matching this regex. | MATCH | Exact format verified and enforced by regex `HEADER_RE` and `parse_header()`. |
| 3 | "The token is DERIVED from the file body (every line after line 1): sha256 -> two 16-bit chunks -> two words of WORDS. Any body edit changes the token, so a stale token is detectable (`check`). `token: PENDING` is a placeholder." (`scripts/dev/role_loader.py:6-7`) | SOURCED (`scripts/dev/role_loader.py:64-77,85-97,720-728`): `WORDS` is 256-word tuple; `compute_token(text)` splits line 1, computes sha256 of body, maps chunks `d[0:2]` and `d[2:4]` modulo `len(WORDS)`; `_check_one()` detects stale tokens and allows `PENDING`. | MATCH | Implementation derives token from SHA256 of lines after line 1 mapped to `WORDS`, detects staleness in `check`, and accepts `token: PENDING`. |
| 4 | "Which roles exist, their files and how each starts: roles/ROSTER.json (the single source; KNOWN_ROLES and ALIASES come from it)." (`scripts/dev/role_loader.py:9`) | SOURCED (`scripts/dev/role_loader.py:36,40-60`): `ROSTER_REL = f"{ROLES_REL}/ROSTER.json"`; `load_roster()` reads `roles/ROSTER.json` (local or trunk fallback); `KNOWN_ROLES = [r["name"] for r in load_roster()]`; `ALIASES = {r["name"]: ...}`. | MATCH | Roster JSON is the primary authority defining roles, file associations, starts, `KNOWN_ROLES`, and `ALIASES`. |
| 5 | "hook UserPromptSubmit hook: on a role trigger, inject the role file from origin/fast-track + a banner instruction; a session's first prompt with no role line gets the best-fitting operator role (`pick`), banner `(fallback: <why>)`." (`scripts/dev/role_loader.py:11-12`) | SOURCED (`scripts/dev/role_loader.py:112-115,446-481,506-554`): `handle()` checks `UserPromptSubmit`, matches triggers or runs `pick_role()` on first prompt; fetches role file from `TRUNK` (`origin/fast-track`); outputs banner with `(fallback: <why>)`. | MATCH | Injects role file fetched from `origin/fast-track` with the banner instruction, or uses `pick_role` with fallback explanation on first prompt without role line. |
| 6 | "list print the roster (name, file, start, model, lane, job) and the aliases." (`scripts/dev/role_loader.py:13`) | SOURCED (`scripts/dev/role_loader.py:604-617,988-990`): `list_lines()` formats header `'Role  File  Start  Model  Lane  Job'`, appends entries for each role in `load_roster()`, lists alias mappings, and prints count. | MATCH | `list` sub-command formats and prints roster columns (name, file, start, model, lane, job) along with alias lines. |
| 7 | "pick --text <task text \| -> the role the fallback would load for that text, and why (never an embedded role)." (`scripts/dev/role_loader.py:14`) | SOURCED (`scripts/dev/role_loader.py:282-302,996-1006`): `pick_role()` checks keywords, skips `r.get("start") != "operator"` (excluding embedded roles), prints `"{name}: {reason}"` or `NONE`. CLI accepts `--text <task text | ->`. | MATCH | Implements role keyword matching for operator roles only, excludes embedded roles, accepts `--text` argument or stdin (`-`), and outputs the selected role and reason. |
| 8 | "check roster vs files, rows of ROLES.md vs files vs header validity vs token freshness, rendered blocks current (exit 1 on malformed, stale or mismatched)." (`scripts/dev/role_loader.py:17-18`) | SOURCED (`scripts/dev/role_loader.py:670-729,986-987`): `check()` calls `check_roster()` and `_check_one()`; validates `ROSTER.json` vs role files, `ROLES.md` rows vs files, header regex validity, token freshness vs body SHA256, and render freshness; exits with 1 on any defect. | MATCH | Complete multi-level validation checking roster, header validity, token staleness, rendered blocks, and ROLES.md consistency with exit code 1 on defects. |

---

## Summary of Findings

1. **Role Loading & Trigger Dispatch**:
   - `scripts/dev/role_loader.py` listens as a `UserPromptSubmit` (and `SessionStart`) hook.
   - It matches explicit role invocations using regex patterns (`PREFIX` + role trigger phrases) and pulls authoritative markdown definitions directly from `origin/fast-track`.
2. **Deterministic Token Derivation**:
   - Headers strictly follow `<!-- role: <Name> | version: v<N> | token: <word>-<word> | triggers: ... -->`.
   - The token is computed via SHA256 on the body (all lines following line 1), sliced into two 16-bit integers, each indexed modulo 256 into a static 256-word dictionary `WORDS`.
3. **Fallback & Roster Authority**:
   - `roles/ROSTER.json` is the sole source of truth for role cataloging.
   - Sessions lacking a role header on prompt 1 are evaluated through `pick_role()`, which scores strong (1.0) and weak (0.5) keyword matches across operator roles (embedded roles are excluded).
4. **Verification & Audit Integrity**:
   - All 8 evaluated docstring clauses match the underlying implementation in `scripts/dev/role_loader.py`.
