# PASS: Explicitly empty quoted evidence fails closed

## Scope checked

- `scripts/dev/verify_extract_quotes.py`: `QUOTE` at line 17, `CBP_EVIDENCE` at line 21, `check_cbp_evidence` at line 85, and `check` at line 114.
- Contract: the checker documents a quoted extract plus source GPS and promises missing or mis-positioned quotes fail. The CBP guide requires quote checking for claims; the shipped `cbp-quote-empty-fragment-word-boundary` card specifically requires evidence that normalizes to no spoken words to fail.
- No production CBP rows, transcripts, stores, or external sources were read.

## Reproduction and repair

In temporary directories, called the real `verify_extract_quotes.check()` entry point on two cases with ordinary speech transcripts: a valid CBP header followed by `evidence: ""`, and a generic `> ""` quote followed by a valid Source GPS tag.

Before the fix, both cases returned `0` with no diagnostic output. The same checker already reports `MISSING` for `evidence: "..."` and punctuation-only evidence. The CLI maps zero problems to PASS, so explicit empty quotes silently bypassed the check.

Cause: both `QUOTE` and `CBP_EVIDENCE` used `(.+)`, which requires at least one character inside the quotes. Empty quoted values were not recognized and never reached the existing fail-closed empty-normalization branch.

Repair: changed only those captures to `(.*)`, so the empty value reaches the existing normalization check and is reported as `MISSING`. Records with no evidence line remain unchanged; a temporary no-caption record still returns zero problems.

Regressions: `scripts/dev/test_verify_extract_quotes.py::test_cbp_empty_quoted_evidence_fails` and `::test_empty_gps_quote_fails`. Both failed against the original implementation (`bad == 0`, expected one problem).

Verification after the fix:

- `python -m pytest scripts/dev/test_verify_extract_quotes.py -q` — **16 passed**.
- `python -m pytest MyTradingSys/tests -k quote -q --basetemp F:/MTS/scratch/codex-cbp-empty-evidence-pytest` — **4 passed, 1032 deselected**.
- Temporary no-evidence/no-caption record — **0 problems**, unchanged behavior.

## Findings

| Severity | Evidence | Finding |
|---|---|---|
| MED | `scripts/dev/verify_extract_quotes.py:17-21,114-119` | Empty generic GPS quotes and empty CBP evidence were skipped and returned zero problems. Fixed by allowing empty captures to reach the existing rejection branch. |

No other verifier behavior was changed or certified here. Lab_Guy ACCEPTed the scoped fix; the card is ready for closure and ship.
