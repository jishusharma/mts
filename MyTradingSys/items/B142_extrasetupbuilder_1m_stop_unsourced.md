# B142 - ExtraSetupBuilder stop is the previous 1m bar high/low, with no trader source

Status: CLOSED (code 2026-10-11; live after the Java window). Severity: MED. Opened 2026-10-07.
Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Operator ruling 2026-10-07: stays flagged this session; remove-or-replace review is a separate session. Same shape as B116/B117/B118.

## Defect

ExtraSetupBuilder stop is the previous 1m bar high/low, with no trader source.

## Findings

- ESB-STOP | src/main/java/datafeed/ExtraSetupBuilder.java:39 | stop = previousHigh(klines1m) for short, previousLow(klines1m) for long | no row in PROVENANCE_AUDIT_TOM.md (grep ESB/ExtraSetup returns nothing); AUDIT_RERUNS_2026-10-06.md step 3 lists it NO-SOURCE.

## Evidence

- ExtraSetupBuilder.java:39-46: stop, gross_rr and net_rr all derive from the previous 1m bar extreme.
- Only FVG is tested (src/test/java/datafeed/ExtraSetupBuilderFvgTest.java); the stop rule has no test and no transcript quote.

## Fix shape

Separate session: remove, or replace with a trader-sourced stop (transcript quote plus file:line). Never tune. Java under the live tree: stage and re-gate before promotion.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RERUNS_2026-10-06.md (step 3)
- MyTradingSys/system/sessions/MTS-2026-10-07-1002Z-APP-BLD-research-closeout.md

## Receipt

# END

## Fix 2026-10-11 (relay A)
ExtraSetupBuilder.build returns an empty ArrayNode (D15). ExtraSetupBuilderDisabledTest: red on old code (expected 0, was 1 at price 99 and 101), green after. Full `mvn test` green. Reaches the feed only at the next JVM restart (JIS-NB desk task).
