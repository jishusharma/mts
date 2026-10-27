# BLOCKED: context_factors V2 power gate fails (2026-10-28, card fable-run2-regate-c-ctx-v2-blocked-pit-v3-m89)

Verdict word: BLOCKED. The V2 run is not frozen (a power result, not a layer decision). No outcome was computed or read; no outcome file was written; no VALIDATION or HOLDOUT bar was read.

## Check command output

`python scripts/dev/prereg_gate.py --n 452 --sd 1.5 --cost 0.066 --m 76`
```
n 452 sd 1.5 m 76 z_holm 3.407 MDE 0.300 R + cost 0.066 = 0.366 vs max plausible gross 0.3; n needed 741
BLOCK: do not freeze (write BLOCKED.md with these numbers)
```

## Power gate arithmetic

- Matched days available in DEV: $n = 452$
- Standard deviation: $\text{sd} = 1.5\text{ R}$ (DECISION OURS)
- Multiple-testing Holm pool: $m = 76$
- Critical value: $z_{\text{holm}} = 3.407$
- MDE at 80% power: $\text{MDE} = \frac{(3.407 + 0.8416) \times 1.5}{\sqrt{452}} = 0.300\text{ R}$
- Incremental fee / slippage cost: $\text{cost} = 0.066\text{ R}$
- Total hurdle: $\text{MDE} + \text{cost} = 0.300 + 0.066 = 0.366\text{ R}$
- Plausible gross effect gate: $0.30\text{ R}$
- Days needed: $n_{\text{needed}} = \left\lceil \left( \frac{(3.407 + 0.8416) \times 1.5}{0.30 - 0.066} \right)^2 \right\rceil = 741\text{ days}$

Because $n_{\text{needed}} = 741 > 452$ available matched days (and $\text{MDE} + \text{cost} = 0.366\text{ R} > 0.30\text{ R}$), the power gate refuses freeze.
BLOCKED means the V2 run is not frozen: this is a power result under the pre-registered decision rules, not a layer decision.

## Dependent task cards

Task card `context-composite-v2-dev-read` (stamped: read-only, never edited) waits on this power result, so the session planner can set its state accordingly.
(Task card `context-factors-one-run` addresses the pit V3 study).

## DECISION log
- DECISION (OURS, conservative default): BLOCKED on power gate. No outcome run, no VALIDATION/HOLDOUT reads.
