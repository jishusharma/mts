# B204 - Card lint rules are only discovered after the card is written, one error at a time: worker agent is allowed on

Filed: 2026-10-26
Status: OPEN
Priority: MED
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B204 | 2026-10-26 | OPEN | MED | Card lint rules are only discovered after the card is written, one error at a time: worker agent is allowed only for size S with est_turns <= 15, and depends_on a card that is only ready is flagged. Two cards each failed lint once and were rewritten. Fix: print all lint errors at once, and document the rules in TASK_REFINEMENT.md next to the card template. | tasks lint on timeframes-add-2d-3d-4d-5d (worker agent on size M) and lab-verify-mtf-bias-ladder (depends_on a ready card), 10-26 ~20:05Z | |
