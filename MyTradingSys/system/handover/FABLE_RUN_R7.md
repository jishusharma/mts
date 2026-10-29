# Fable run R7: FORWARD TEST DESIGN (start text)

Operator start line, typed into a new Code session on Fable 5.1, effort high, after R6 is on trunk:

    Run FABLE_RUN_R7.md

Design and reasons: `MyTradingSys/research/fable_run_design_2026-10-28/DESIGN_R7.md`. Card: `fable-run7-forward-test`.

---

You are the MTS Fable session R7. Boot per CLAUDE.md steps 1-2 (`python scripts/dev/sync.py start fable-run7-forward-test`, STATUS.md). If `research/fable_run6_powered_prereg/PRE_REG.md` is not on origin/fast-track, stop and reply "R6 not shipped". HOLD (2026-10-28): E2 came back INCONCLUSIVE; if `research/fable_run6_powered_prereg/REVIEW_O2.md` is missing or does not say R7 = run, stop and reply "R7 on hold: O2 first". Usage guard: `get_usage` first and last into `research/fable_runs_2026-10-28/USAGE.md` (`## R7`, UTC, all meters). Stop and ship at weekly Fable +4 pts, 5 h window 85 %, 45 tool turns, or context 60 %.

Hard limits: R6's rule is frozen (never change it; pin the PRE_REG.md commit you read in FORWARD_PREREG.md; an O2 rule change means R7 is re-run); months to power use the signal-day rate 0.33/day, not the 0.49 event rate; no outcome column (E2, VALIDATION, forward fills) and no bar >= 2024-07-01 is read; read the live-path code only, no live-tree edit, no deploy, no process or HALT file touch; testnet only, no mainnet; never read `.secrets/` or `.env`. No questions to the operator: conservative default, log `DECISION (OURS)`.

QUESTION: how does testnet trade the R6 Krown S8 4h rule exactly as frozen, so every day from the first deploy is fresh out-of-sample data, and what forward rule decides it?

READ: the inputs list in DESIGN_R7.md.

DO: write `research/fable_run7_forward_test/FORWARD_PREREG.md` with the 5 parts in DESIGN_R7.md section Output (parity spec with a replay test that reproduces R6's event list exactly, forward sample rule with months to power from COUNTS.csv fire rates, pass/fail rule fixed now, isolation from the other testnet sources, cards). Cards: `tasks.py twins` first, then `tasks.py new` + `fill`: build (SONNET, live path, depends on `fable-r3-stop-gap-early-return`), replay parity test (SONNET), monthly forward readout (SONNET). `tasks.py check`; revert any other card it rewrites. Label every number SOURCED (file:line) or OURS.

Ship: `python scripts/dev/sync.py ship --release fable-run7-forward-test`; commit body `Result: <months to a powered forward read> + <parity rule>`; `sync.py where` clean; `tasks.py done fable-run7-forward-test`.

Reply (6 lines max): bold result line, months to power, cards filed, usage delta.
