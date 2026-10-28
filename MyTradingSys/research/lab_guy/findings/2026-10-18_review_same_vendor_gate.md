# Review: same-vendor gate, lab commit 3bc336e6 (rule 11, report only)

Scope: `scripts/dev/lab_flow.py`, `scripts/dev/test_lab_flow.py` as of 3bc336e6, read via `git show`/`git archive` into a scratch dir; lab tree untouched.
Baseline in scratch: 28 passed.

## Blind-first: what the gate must do (lab_guy.md:25, 33)
"producer vendor recorded and different from the reviewer's"; routing: GPT producer -> Gemini reviews, Gemini -> GPT, Claude -> either. So: vendor must be derived from something trustworthy, compared case/whitespace-insensitively, fail closed on unknown/empty vendor, and any override must be narrow and tested.
Result: the comparison itself (`vendor == producer_vendor`) is right for the happy path; it relies entirely on a free-text label.

| # | Severity | file:line | Finding | Evidence |
|---|---|---|---|---|
| 1 | MED | lab_flow.py:167-180 | Vendor is a free-form recipe label, never validated against an allowlist or the model id. Not a prefix derivation, so no prefix bug, but also no cross-check: a recipe row `("gemini", ..., "gpt-6-astra")` passes as cross-vendor; `"openai"` vs `"codex"` (same vendor) passes. Unknown/new vendors are accepted rather than failing closed. | Probe via `F.launch` with monkeypatched RECIPES: gemini-label+gpt model => ACCEPTED; codex vs openai => ACCEPTED. Not exploitable by a card author today (RECIPES is code), but any new recipe row or alias (argon, gemini-3.8-flash-low, claude-sonnet-5-5 under label "claude") depends on hand-typed labels. |
| 2 | MED | lab_flow.py:178 | No normalisation: `"Codex"` vs `"codex"` and `"codex "` vs `"codex"` are treated as different vendors. | Probe: both ACCEPTED at launch. |
| 3 | MED | lab_flow.py:178 | Empty-string vendor is accepted as a distinct vendor; only `None` on both sides happens to be rejected (equal). `("", ...)` reviewer vs codex producer => ACCEPTED. Should fail closed. | Probe: empty vendor reviewer => ACCEPTED. |
| 4 | MED | test_lab_flow.py:67-88 | C0-only restriction is untested: mutation M2 (override allowed for any risk class, C0 check removed) leaves all 28 tests green. Likewise the bool-type and risk_class-enum checks have no test. The code does reject C1 override and "true"/"c0" (probe), so behaviour is correct but unguarded. | M2 mutation => 28 passed. Probe: override C1 => REJECT, 'true' => REJECT. |
| 5 | LOW | lab_flow.py:178 | Compares only against stage 1; for 3+ stage recipes a stage that matches an intermediate reviewer's vendor is unchecked (allowed by spec text, noted for completeness). | code read |
| 6 | LOW | lab_flow.py:17-21,222 | Recipe change silently weakens critical-audit/run-review: `crucial=model=="gpt-6-astra"` (line ~242) no longer fires because astra was dropped from critical-audit, and run-review verify went from gpt-6.1-sol/medium to gemini-2.5-pro/low. Report discloses the vendor switch but not the lost crucial flag/effort drop. | diff hunk @@ -15; launch crucial= expression |
| 7 | INFO | test_lab_flow.py:67 | Tests are NOT vacuous for the main gate. M1 (vendor check stubbed off) => 2 failed. M3 (revert to model-id compare) => 1 failed. | scratch mutation runs |

Verdict: the stated defect (gpt-6-luna vs gpt-6-astra passing) is fixed and tests bite. Gaps are fail-closed hardening (1-3) and a missing test for the C0 restriction (4). Suggested follow-up card: vendor allowlist + `.strip().lower()` + model-prefix consistency check (codex<->gpt-*, gemini<->gemini-*, claude<->claude-*; unknown prefix => reject), plus tests for C1 override, non-bool override, empty/case vendor.
