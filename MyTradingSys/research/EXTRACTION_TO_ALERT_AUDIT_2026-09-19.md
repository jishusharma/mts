# EXTRACTION-TO-ALERT AUDIT
# Date: 2026-09-19
# Session: MTS-2026-09-19-0823Z
# Scope: verify the claim in cross_trader_integration_plan.md Phase 4 that 33 entries were integrated.
# Method: grep 19 unique CT ids + 38 C-entries across four code surfaces.
# ---

## FINDING

Phase 4 landed in the engine document only. Zero traceability links exist from
the engine document to Java, to Python runtime, to the watch script, or to the
verdict script.

This does not prove the behavior is absent. It proves the tag is absent.
Behavior-level verification is out of scope for this pass.

## WIRE STATUS

| Wire | Status | Evidence |
|---|---|---|
| Transcript to extract | DONE | 7 extracts under MyTradingSys/extracts/ |
| Extract to C-entries | DONE | Phase 2, 80 entries in cross_trader_consolidated.md |
| C-entries to engine doc | DONE | compiled_engine.md L772-849 traceability matrix |
| Engine doc to Java | NOT TAGGED | 19 CT ids + 38 C-entries, 0 hits |
| Engine doc to Python | NOT TAGGED | 0 hits |
| Engine doc to watch script | NOT TAGGED | 0 hits |
| Engine doc to verdict script | NOT TAGGED | 0 hits |

## SECTION 12 EXCEPTION

Section 12 (Post-Entry Management, subsections 12.1-12.10) cannot be code-wired
by construction. The MTS verdict function is a screener. It emits WATCH, WAIT_RR,
SETUP_FORMING, SETUP_CONFIRMED. It does not read position state, entry price, or
management signals. No code path exists that could consume Section 12.

Classification: gauge by design. Same class as B021 and B022.

## CT IDS IN ENGINE DOC (19)

CT-006, CT-029, CT-033, CT-035, CT-047, CT-048, CT-049, CT-050, CT-051,
CT-052, CT-053, CT-054, CT-055, CT-057, CT-066, CT-069, CT-075, CT-082, CT-083

## TAG SCHEME (PROPOSED, PENDING USER CONFIRMATION)

Six families, intuitive names:

| Family | Tag | Source |
|---|---|---|
| Tom core | [TOM-NNN] | raw_transcripts_canonical (213 ids, existing) |
| Cross-trader rules | [CT-NNN] | other analyst extracts (existing, 19 ids in engine) |
| Verdict tracking | [VERDICT-NNN] | future analyst opinion pipeline |
| MalkanView RSI | [MALKAN-NNN] | RSI 40-60 layer |
| Event probability | [PROB-NNN] | probability distribution layer |
| Session frame | [SESSION-NNN] | session-aware frame |
| Our invention | [SCREENER] | no number (existing) |

Source of layer names: MyTradingSys/PROJECT_VISION.md INTEGRATIONS TRACKED table.

## NEXT STEPS

1. Confirm tag count (6 families or 4 layers plus existing).
2. Write tag scheme into MTS_DICTIONARY.md.
3. Refresh indicator_audit_table.md (2026-08-31, stale 19 days).
4. Decide whether to tag existing code with CT-NNN where behavior is present.
5. Section 12: mark as gauge by design, no code consumer intended.

# END
