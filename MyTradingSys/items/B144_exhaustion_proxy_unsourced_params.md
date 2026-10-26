# B144 - Exhaustion proxy volume spike 2.0x over 240 one-minute bars is NO-SOURCE

Status: BLOCKED. Severity: MED. Opened 2026-10-07.
Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Secondary tag: SCREENER. Operator ruling 2026-10-07: stays flagged this session; remove-or-replace review is a separate session. Same shape as B116/B117/B118.

## Defect

Exhaustion proxy volume spike 2.0x over 240 one-minute bars is NO-SOURCE.

## Findings

- P06 | SetupCandidatesBuilder.java:767-779 | last 1m volume > 2.0x mean of 240 bars, close within 0.1% | PROVENANCE_AUDIT_TOM.md:62 row P06
- P03 | SetupCandidatesBuilder.java:694-718 | absorption volume > 2.0x mean20; strong > 5x (same family)

## Evidence

- SetupCandidatesBuilder.java:775 average(volumes, max(0, n-240), n) // 4h = 240 minutes; :709 volumes[i] > 2.0 * avgVol20.
- StateCodeEmitter.java:53 VOL_RATIO_THRESHOLD = 2.0 is the same unsourced multiple.
- Operator ruling 2026-10-07: carries SCREENER as a secondary tag, since the exhaustion proxy is screener context, not a Tom rule.

## Fix shape

Separate session: remove or replace with a trader-sourced definition of exhaustion. Never tune 2x or 240.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RERUNS_2026-10-06.md (step 3)
- MyTradingSys/system/sessions/MTS-2026-10-07-1002Z-APP-BLD-research-closeout.md

## Receipt

# END

## Receipt - code-line anchors 2026-10-09

- Confirmed on disk: SetupCandidatesBuilder.java:709 `boolean cond1 = volumes[i] > 2.0 * avgVol20;` (absorption); :775 `double avgVol4h = average(volumes, Math.max(0, n - 240), n); // 4h = 240 minutes`; :785 `res.volumeSpikeDetected = magnitude > 2.0;`.
- Confirmed on disk: StateCodeEmitter.java:53 `private static final double VOL_RATIO_THRESHOLD = 2.0;`.
- Both files compile into the running loop. Any edit is a Java live-path change: stopped-loop window required, or the section 6 staged .new path.
- Status stays OPEN per operator ruling 2026-10-07 (remove-or-replace is a separate session).

Receipt by: 2026-10-09 MTS-2026-10-08-2225Z-DSA-COO
