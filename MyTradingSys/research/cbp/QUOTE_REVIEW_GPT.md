# CBP quote review (2026-10-28, JIS-NUC, OpenAI/Codex)

**BLOCKED for the 13 production rows; FIX-FIRST for synthetic quote-gate gaps.**
The production store and matching transcripts are not available in this checkout or an available quote-review pack. No production row has been certified. The historical 13 accepted / 1 rejected count in CBP_STATUS_2026-10-25.md is a producer claim, not independently recounted here. The existing pending request `20261026-183052-claude-locate-current-cbp-repo-and-store` identifies the missing host/path evidence. No fetch, CBP-repo edit, store access, or transcript publication occurred.

## Reproducible local evidence

Run `python MyTradingSys/research/cbp/quote_review_repro.py`. It uses a temporary synthetic transcript and the actual `check()` entry point. The original verifier is unchanged. All seven current-behavior assertions passed; these are reproductions of gaps, not assertions that acceptance is correct.

| Probe | Machine result | Human disposition |
|---|---|---|
| Exact speech, including negation | OK, 0 problems | PASS control |
| Replace buying with selling | MISSING, 1 problem | FAIL as required; planted alteration caught |
| Evidence is only three dots | OK, 0 problems | FAIL: no spoken content |
| Evidence is only punctuation | OK, 0 problems | FAIL: no spoken content |
| Evidence is `long`; transcript says `belong` | OK, 0 problems | FAIL: partial word is not a quote |
| Ellipsis removes `do not` from a recommendation | OK, 0 problems | FAIL semantically: ordered fragments alone do not preserve meaning |
| File has no recognized evidence lines | PASS, exit 0 | NOT CHECKED, cannot certify a claim |

## Findings

| Severity | Evidence | Finding and proposed action |
|---|---|---|
| HIGH | scripts/dev/verify_extract_quotes.py:66-78 (`first_missing`) | Empty normalized fragments are skipped and no nonempty fragment is required. Reject evidence with no meaningful fragment. Follow-up: `cbp-quote-empty-fragment-word-boundary`. |
| MED | scripts/dev/verify_extract_quotes.py:87 (`body_norm.find`) | Substring matching accepts `long` inside `belong`. Require word boundaries for every fragment. Same follow-up. |
| HIGH | scripts/dev/verify_extract_quotes.py:66-78 | Ordered ellipsis fragments can remove negation. Lexical presence is insufficient for semantic quote approval; retain an independent contextual check. No automated semantic remedy claimed. |
| MED | scripts/dev/verify_extract_quotes.py:178-184 (`main`) | Zero checked quotes yields PASS. Callers must distinguish zero checked from successfully verified evidence. This is a certification limitation, not proof of a production ingestion bypass. |
| BLOCKER | GPT_CBP_GUIDE.md:5,19-21; desk request above | Actual store rows, rejection reason and corresponding transcript bodies are absent. Obtain a host-local review or an authorized noncommitted pack before assigning row-level PASS/FAIL. Do not fabricate 13 table entries. |

Line anchors refer to the reviewed verifier; the repro contains all fixtures and makes no network calls. Tests: `python -m pytest scripts/dev/test_verify_extract_quotes.py -q`: **11 passed**. Card-requested `python -m pytest MyTradingSys/tests -k quote -q --basetemp F:/MTS/scratch/codex-budget-quote-pytest-20261028`: **3 passed, 995 deselected**. Initial default-temp run had a Windows temp-directory PermissionError; the isolated F: base resolved it. The altered synthetic control is not the missing historical rejected row.

## Remaining work

Keep `cbp-quote-gate-review` blocked. Obtain the authoritative 13 accepted rows plus rejected-row evidence and matching transcripts, then check every quote and its context. This report completes only the local gate probes; it does not meet the card's production row-audit done condition. No analyst rating, trading promotion, or VERIFIED trust tag is issued.
