# FIX-FIRST: Explicitly empty CBP evidence bypasses the quote verifier

## Scope checked

- `scripts/dev/verify_extract_quotes.py`: `CBP_EVIDENCE` at line 21, `check_cbp_evidence` at line 85, and `check` at line 114.
- Contract: `MyTradingSys/research/cbp/GPT_CBP_GUIDE.md` requires quote checking for CBP claims; the shipped `cbp-quote-empty-fragment-word-boundary` card specifically requires CBP evidence that normalizes to no spoken words to fail.
- No production CBP rows, transcripts, stores, or external sources were read.

## Reproduction

In a temporary directory, created a valid CBP header and the explicit line `evidence: ""`, with a sibling transcript containing ordinary speech. Called the real `verify_extract_quotes.check()` entry point.

Observed result: return value `0`, no diagnostic output. The same checker reports `MISSING` for `evidence: "..."` and punctuation-only evidence. The CLI maps zero problems to PASS, so the explicit empty evidence silently bypasses the check.

Cause: `CBP_EVIDENCE` uses `(.+)`, which requires at least one character inside the quotes. An empty quoted value is therefore not recognized as an evidence line and never reaches `first_missing()`'s fail-closed empty-normalization branch.

## Proposed scope

Allow the quoted capture to be empty so the existing normalization check rejects it. Preserve behavior for a record with no evidence line, since no-caption outcomes are intentionally represented without a quote. Regression: `scripts/dev/test_verify_extract_quotes.py::test_cbp_empty_quoted_evidence_fails`.

The regression was run against the current verifier before the fix and failed (`bad == 0`, expected a problem). The initial fix and 15 focused / 4 quote-integration test passes are preserved locally pending the required Lab_Guy review stamp; they are not included in this report commit.

## Findings

| Severity | Evidence | Finding |
|---|---|---|
| MED | `scripts/dev/verify_extract_quotes.py:21,119` | Explicit `evidence: ""` is skipped and the checker returns zero problems. Recognized CBP evidence must fail closed when its quoted value is empty. |

No other verifier behavior was changed or certified here. `cbp-empty-quoted-evidence` remains pending Lab_Guy review; this report does not claim the fix is shipped.
