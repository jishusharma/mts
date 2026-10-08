# B143 - CryptoCred 0.1 percent stop buffer and 1.5R target are NO-SOURCE

Status: OPEN. Severity: MED. Opened 2026-10-07.
Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Also carries the CryptoCred fill-bias UNVERIFIED state (see Receipt of the rerun). Operator ruling 2026-10-07: stays flagged this session; remove-or-replace review is a separate session. Same shape as B116/B117/B118.

## Defect

CryptoCred 0.1 percent stop buffer and 1.5R target are NO-SOURCE.

## Findings

- C14 | cryptocred/cc_setups.py:34,45 | setup 1 stop = level x (1 -/+ 0.1%) | NO-SOURCE (LAYER_PROVENANCE_AUDIT.md:99)
- C15 | cc_setups.py:34,64 | setups 1-2 fixed 1.5R target | NO-SOURCE as a fixed value; BH:82 is a minimum, not a target (LAYER_PROVENANCE_AUDIT.md:100, :200)
- C19 / C23 | cc_setups.py:104,131,183,206 | setup 2 and 3 stops use the same 0.1% buffer | NO-SOURCE (LAYER_PROVENANCE_AUDIT.md:104,108)

## Evidence

- cc_setups.py:53 setup1_sr_flip(stop_buffer_pct=0.001, target_r=1.5); :89 setup2_fib_pullback(... stop_buffer_pct=0.001, target_r=1.5).
- The 0.1% stop makes the fee per R large (AUDIT_RERUNS_2026-10-06.md), so any CryptoCred verdict depends on an unsourced number.

## Fix shape

Separate session: remove or replace with a trader-sourced rule. Do not grid these values. The rerun results are evidence about the unsourced values, not a basis to select them.

## Scope of this filing

Filing only. No code or doc edit was made for this item.

## Related

- MyTradingSys/research/AUDIT_RERUNS_2026-10-06.md (step 3)
- MyTradingSys/system/sessions/MTS-2026-10-07-1002Z-APP-BLD-research-closeout.md

## Receipt

# END
