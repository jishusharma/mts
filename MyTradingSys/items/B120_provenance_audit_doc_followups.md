# B120 - Tom provenance audit doc follow-ups from W3 and revalidation not delivered

Status: OPEN (receipt written 2026-10-07; W3-5 parked on an operator ruling). Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. Group (c) from MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md.

## Defect

Tom provenance audit doc follow-ups from W3 and revalidation not delivered.

## Findings

- RA-W3-RECLASS | audit source MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md:174-176 | C1 verdict NOT | Not reclassified in MyTradingSys/research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md; reader-biased finding.
- RA-W5-FIELDS | audit source MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md:231 | C1 verdict NOT | Fields not added to provenance audit; no thresholds sourced.
- W3-2 | audit source MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_REPORT_2026-10-01.md:69 | C1 verdict NOT | Re-extraction of 22 both-reader NO-SOURCE rows not delivered; no output file; headline 36 still in OPUS_PLAN:20.
- W3-4 | audit source MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_REPORT_2026-10-01.md:63-64 | C1 verdict NOT | 17 rows split NO-SOURCE vs CONCEPT-ONLY; PROVENANCE_AUDIT_TOM.md:5 definition unchanged since the report.
- W3-5 | audit source MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_REPORT_2026-10-01.md:65 | C1 verdict NOT | DATA-PLUMBING 'no trading meaning' vs 'no Tom idea' unresolved; fast_track_2026-09-27/W3_BLIND_PACKET_2026-10-01.md:14 unchanged.
- W3-6 | audit source MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_REPORT_2026-10-01.md:66 | C1 verdict NOT | No re-adjudication of A05/A07 on disk; packet gives no long/short split.
- W3-LIM | audit source MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_REPORT_2026-10-01.md:13 | C1 verdict NOT | Search-based reading, speaker identification and packet-without-code limits not remediated; no full transcript read exists.

## Evidence

- RA-W3-RECLASS: B03/V04 veto rows not reclassified in PROVENANCE_AUDIT_TOM.md.
- RA-W5-FIELDS: 9 unaudited section-10 fields not added to the provenance audit; no thresholds sourced.
- W3-2: re-extraction of 22 both-reader NO-SOURCE rows not delivered; headline 36 still in OPUS_PLAN_2026-10-02.md:20.
- W3-4: 17 rows split NO-SOURCE vs CONCEPT-ONLY; PROVENANCE_AUDIT_TOM.md:5 definition unchanged.
- W3-5: DATA-PLUMBING definition gap awaiting operator pick (W3_BLIND_PACKET_2026-10-01.md:14).
- W3-6: A05/A07 SOURCED vs CONCEPT-ONLY not re-adjudicated; no long/short split.
- W3-LIM: search-based reading, speaker identification and packet-without-code limits not remediated.

## Fix shape

Doc work on the provenance audit. W3-5 needs an operator ruling first. Claude-side re-extraction (W3-2) must pass verify_extract_quotes.py.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

Session MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Doc-only item. No audit document was edited this session.

- W3-5: awaiting operator definition of DATA-PLUMBING per W3_BLIND_PACKET_2026-10-01.md:14. PARKED.
- RA-W3-RECLASS, RA-W5-FIELDS, W3-4, W3-6, W3-LIM: CONFIRMED still undelivered (PROVENANCE_AUDIT_TOM.md:5 definition unchanged). Next action: Sonnet doc pass with verify_extract_quotes.py. Not run this session.
- W3-2: CONFIRMED undelivered; headline 36 still in OPUS_PLAN_2026-10-02.md:20. Re-extraction of the 22 both-reader rows needs a transcript read and passes verify_extract_quotes.py. Not run this session.

Item stays OPEN. W3-5 is the only operator-blocked sub-item; the rest are unblocked doc work.
