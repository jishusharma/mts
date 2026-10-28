# FIX-FIRST: Explicitly empty quoted evidence bypasses the quote verifier

## Scope checked

- `scripts/dev/verify_extract_quotes.py`: `QUOTE` at line 17, `CBP_EVIDENCE` at line 21, `check_cbp_evidence` at line 85, and `check` at line 114.
- Contract: the checker documents a quoted extract plus source GPS and promises missing or mis-positioned quotes fail. The CBP guide requires quote checking for claims; the shipped `cbp-quote-empty-fragment-word-boundary` card specifically requires evidence that normalizes to no spoken words to fail.
- No production CBP rows, transcripts, stores, or external sources were read.

## Reproduction

In temporary directories, called the real `verify_extract_quotes.check()` entry point on two cases with ordinary speech transcripts: a valid CBP header followed by `evidence: ""`, and a generic `> ""` quote followed by a valid Source GPS tag.

Observed result for both cases: return value `0`, no diagnostic output. The same checker reports `MISSING` for `evidence: "..."` and punctuation-only evidence. The CLI maps zero problems to PASS, so explicit empty quotes silently bypass the check.

Cause: both `QUOTE` and `CBP_EVIDENCE` use `(.+)`, which requires at least one character inside the quotes. Empty quoted values are therefore not recognized and never reach the existing fail-closed empty-normalization branch.

## Proposed scope

Allow both quoted captures to be empty so the existing normalization check rejects them. Preserve behavior for a record with no evidence line, since no-caption outcomes are intentionally represented without a quote. Regressions: `scripts/dev/test_verify_extract_quotes.py::test_cbp_empty_quoted_evidence_fails` and `::test_empty_gps_quote_fails`.

Both regressions were run against the current verifier before the fix and failed because `bad == 0`, expected one problem. A CBP-only prototype passed the focused verifier and quote-integration suites, but the generic-format case exposed the same parser gap and is now included in the scoped card. No source fix is included in this report commit pending the required Lab_Guy review stamp.

## Findings

| Severity | Evidence | Finding |
|---|---|---|
| MED | `scripts/dev/verify_extract_quotes.py:17-21,114-119` | Empty generic GPS quotes and empty CBP evidence are skipped and the checker returns zero problems. Any explicitly quoted empty value must fail closed. |

No other verifier behavior was changed or certified here. `cbp-empty-quoted-evidence` remains pending Lab_Guy review; this report does not claim the fix is shipped.
