# CBP planted-row gate trial (GPT)

RESULT (2026-10-26 UTC / 2026-10-27 IST, JIS-NUC): five synthetic probes, **two stopped and three reproduced claim-store validation gaps**. No production row, transcript, store, CBP checkout, extraction model or network was read/run. The fixtures live as Python test inputs only; no planted store is committed. Reviewer vendor: OpenAI/Codex (exact serving model variant not exposed). This is a gate audit, not an analyst rating or promotion decision.

## Contract and threat model

`MyTradingSys/research/v1_plan_2026-10-20/D5_CBP_MODULE.md:45-54` defines gates 1 schema (producer then consumer), 2 verbatim quote, 3 expiry plus age, 4 scorecard (56 scored calls before any weight), 5 backtest/promotion before trading. The 56-call rule is SOURCED project policy, not an empirically estimated threshold. `GPT_CBP_GUIDE.md:7-18` limits this card to checking, recounting and gate review. No producer/extraction fix is made here.

Tests use the pre-existing tiny synthetic transcript BODY and GOOD extraction fixture in `MyTradingSys/tests/test_cbp_query.py`, frozen NOW=2026-10-24 10:00 UTC (OURS fixture time). A temporary store path is always supplied. Publication is recent so the expiry-specific tests cannot accidentally pass through the age filter. Each planted input is intentionally inconsistent with the stated contract, not a real analyst claim.

## Five probes

| Planted input | Expected stop | Actual result before any fix | Evidence / test |
|---|---|---|---|
| Trade has no quote | Gate 2 | **STOPPED**: build_row returns None with empty-quote rejection | scripts/dev/cbp_run.py:153-156; test_planted_trade_without_quote_is_rejected |
| direction='SIDEWAYS' while every required trade field and verbatim quote exists | Gate 1 | **GAP**: accepted by build_row; runtime validate_row checks presence, not enum | MyTradingSys/cbp/schema.json defines LONG/SHORT; cbp/__init__.py:49-62 omits enum check; test_planted_wrong_direction_is_rejected |
| Recent publication but expires_at=2026-10-24 09:00 UTC, already past NOW | Gate 3 | **GAP**: query returns the expired row | cbp/__init__.py:71-85 checks publication-date cutoff only; test_planted_expired_row_is_not_returned |
| Existing same (video_id, analyst) encountered again | Ingestion dedupe before gates 1/2 | **STOPPED**: no extractor call, one row remains | scripts/dev/cbp_run.py:173-180,192; test_planted_duplicate_video_id_is_not_extracted_again |
| expires_at missing in a planted store row | Gate 1 at consumer, or fail-closed Gate 3 | **GAP**: validate_row explicitly reports missing expires_at, but query does not invoke it and returns the malformed row | cbp/__init__.py:53,71-85; test_planted_missing_expiry_is_not_returned |

Wrong direction here means an invalid enumerated direction, not a valid LONG/SHORT sign deliberately reversed against an analyst's meaning. That semantic extraction problem requires the independent transcript golden set and is not certified by this enum probe. Likewise duplicate coverage is same video plus same analyst, matching the runtime key; cross-analyst aliases were not tested.

## Fail-first evidence and permanent audit probes

Initial unmarked run: `python -m pytest MyTradingSys/tests/test_cbp_query.py -k planted -q` with a fresh F:/MTS pytest base: **3 failed, 2 passed**. Failures are exactly wrong direction, expired row and missing expiry. Thus each gap has a safety expectation demonstrably red on existing production code.

The audit card asks for findings and a bug card rather than extraction changes. Those three tests are now marked **strict xfail** with bug id cbp-row-schema-expiry-gaps. Entire file: **13 passed, 3 xfailed**. These are three unresolved failures, not three successful checks. `strict=True` makes an unexpected pass fail CI when a repair lands, requiring the repair to convert/remove the marker and assert the intended behavior. No production behavior was changed to make the audit green.

Reproduce the original failures against current code with `pytest --runxfail ... -k planted` in a temporary pytest base. All persistence and transcript fixtures are isolated using tmp_path/monkeypatch. Existing tests still cover fabricated quotes, old publication exclusion and extraction retries.

## Gates 4 and 5: not exercised

No scoring ledger or promoted setup was supplied to these probes. The current cbp.query/is_tradable helpers expose recent claims and field completeness; is_tradable is **not** an order permission, scorecard qualification or promotion receipt (cbp/__init__.py:1-9,65-68). Therefore the three rows passing the query/build boundary are not evidence that they pass every trading gate. The plan's gate 4/5 protections remain requirements outside this test's exercised surface. No trading integration or real orders were attempted.

Repair/review card **cbp-row-schema-expiry-gaps** (SONNET, raw) records the three reachable claim-boundary defects and references this report. It is separate from cbp-quote-gate-review, which checks real verbatim quotes in stored rows. Before changing freshness semantics, a repair must reconcile the age-filter fixture's inclusive calendar cutoff with the producer's published+5-days midnight expiry; do not silently weaken either test to copy the current implementation. Keep explicit expiry boundaries, missing/unparseable expiry and invalid direction fail-closed, with a valid-row control.

Audit complete within its scope. No claim of all-five-gates coverage, analyst reliability, validated edge or deployment safety is made.
