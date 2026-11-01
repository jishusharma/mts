# Brief: co-trade P5 hedge leg (planner refresh 2026-11-01)

Card: cotrade-p5-hedge-leg (CRITICAL). Testnet only. Files: `MyTradingSys/execution/cotrade.py`, `test_cotrade.py`, DESIGN.md s7.

## State to build on (0711c65f5, P1 review fixes done, 33 tests)
pick_account (spare slot jishu_22 else main), _validate, ensure_stop (a stop counts only if amount and trigger match; correct stop placed before wrong ones are cancelled), place_order (resting limits are REFUSED: no polling), _refuse_resting, _flatten_and_halt, kill (HALT first, one account today), unknown-state scan over the journal.

## Decisions (OURS)
- A hedge `--at P` that would rest is refused like P1; only marketable hedges are placed.
- Hedge size = pct of the parent filled size, rounded to AMOUNT_STEP_USD (10).
- Hedge goes on a second existing slot (jishu_1..4 / jishu_22 / main), never a new key, never the parent account.

## Tests (write first; each must fail on 0711c65f5)
1. refuses same-account hedge; refuses a slot with no key file (existence check only)
2. testnet env asserted before any call
3. hedge has its own stop via ensure_stop (amount and trigger match)
4. refused while HALT is set
5. sum of both slots max loss at stops <= MAX_LOSS_AT_STOP_USD (500)
6. hedge place fails after parent filled: parent keeps its stop, journal state hedge_failed, no naked leg
7. journal child record carries the parent order id
8. kill flattens BOTH slots even if the first flatten raises; HALT exists before the first cancel; journal records per-slot errors
9. restart rebuilds the pair from exchange positions on both accounts, not only the journal
10. unknown-state scan treats a half-placed hedge as unknown
11. --dry-run prints both legs and net exposure, makes no call
12. live aid = a `net` view printed by cotrade.py itself (DECISION OURS, no other file): net size across both slots from exchange positions; test with two fake positions (+30 and -10 USD gives net +20)
13. hedge --at P that would rest is refused (no order placed)
14. size = pct of the parent filled size rounded to 10 USD (parent 70, 50 pct -> 30 by floor to step; state the rounding rule in the test); hedge side is opposite to the parent

## Process
CRITICAL protocol: post `REVIEW cotrade-p5-hedge-leg PLAN <branch>` once plan and tests exist, build, post `REVIEW ... DIFF <sha>`. Builder never deploys or touches HALT files outside tests.
Verify line: content sha, `git cherry origin/fast-track <sha>` empty, `git ls-tree -r origin/fast-track --name-only` shows the files.
