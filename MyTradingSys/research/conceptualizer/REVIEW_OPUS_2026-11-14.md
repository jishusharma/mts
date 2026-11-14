# Conceptualizer wiring review (Opus, 2026-11-14)

Reviewed: commit `1d0c657ba` ("all 16 layers wired") and `11006989b` (republish), at trunk `ff1a589c3`. Read-only review; no code changed.

**What the Conceptualizer is.** A page generator, not a runtime module: `concepts.json` -> `scripts/dev/make_conceptualizer.py` -> `MyTradingSys/system/artifacts/conceptualizer.html`. "Wired" here means every `layer_index.json` family is claimed by a Conceptualizer layer and every test row cites a source file that exists. No layer's trading code calls it, and none should. Brief checks (1) and (5) are therefore judged on that design.

## Verdict: OK with 3 BUGs in data (no generator bug)

| Check | Result | Evidence |
|---|---|---|
| (1) Wiring, no duplicated logic | OK | `make_conceptualizer.py` `wiring_problems()` + `load()` passes `family_ids()`; 18/18 families claimed by 16 layers |
| (2) Producer has a consumer | OK | build reproduces the committed html byte-for-byte; registry `published_sha` updated (`11006989b`); test in `run_all_tests.py:58` |
| (3) Numbers vs sources | OK, 1 verdict BUG | 275/295 rows: every n/net number found in the cited file; the other 20 checked by hand = rounding/format (e.g. T3 `-0.0136R` vs source `-0.014`), except the verdict below |
| (4) Tests fail on pre-change code | OK | old generator: 5 failed / 9 passed; new: 14 passed |
| (5) Look-ahead | N/A | no market computation in the generator; cited studies own their own splits |
| (6) No runtime/order/account data | OK | grep of `sources_1114/` for order ids, balances, keys, holdings: market terms only |
| FORMULAS.md | N/A | generator computes no formula; rows quote study outputs |

## Per layer

| Layer | Verdict | Note |
|---|---|---|
| tom-fabio, cryptocred, krown, positioning, session-timing, volume-ma, callers, wavetrend, pitchfork, pizzino, nk-stocktalk, adx-trend, cycle-context, edge-harness | OK | family claimed, sources exist, numbers match |
| malkan | BUG | `concepts.json:1830` Deep RSI grid row says `INCONCL.`; source `edge3-rsi-deep-extreme-grid-1113_RESULTS.md:3,147` grades the whole grid "FAIL / UNDERPOWERED" and that best cell (4h, T20, tgt3, n 32) `FAIL`. Row softens a FAIL. |
| live-engine | BUG | `concepts.json:14125` "Consensus writer ... not wired; nothing calls it" is false: `alerts/live_runner_cli.py:733` calls `consensus.hook.consensus_after_poll` every poll (observation only). |

## Other findings

- BUG (hand-over): both commits' `Next:` point to `CONCEPTUALIZER_UPDATE_1114.md`; the file is not on trunk. Open items are lost.
- Commit message says 363 test rows; `concepts.json` at `1d0c657ba` has 340 (379 source cells). Claim is off, data is fine.
- Duplication: 93 source files copied into `conceptualizer/sources_1114/`; 2 are byte copies of trunk files (`nk_stocktalk_1113/extract55/NK55_RULES_1114.md`, `layer_lab/gemini_edge_1114/inputs/NK_RSI_RESULTS.md`) and will drift. Point those rows at the originals.
- Verdict words are free text (`UNPROVEN`, `NOT REAL`, `RUNNING`, `UNDERPOWERED` beside FAIL/INCONCL.); `vcls()` (`conceptualizer.tpl.html:135`) styles by first word, so unknown words render unstyled. No closed list is checked.

## Fixes (for the Conceptualizer owner)

1. Malkan Deep RSI row -> `FAIL` (lesson "48 of 60 under 30 trades; best powered cell FAIL").
2. live-engine consensus row -> "called each poll by live_runner_cli.py; observation only, no consumer reads the rows" (verify the reader before writing that half).
3. Write `CONCEPTUALIZER_UPDATE_1114.md` or amend `Next:` in the next ship.
4. Replace the 2 byte copies with the trunk paths; add a closed verdict list to `problems()`.

Next: card for the 4 fixes (owner: conceptualizer-wire session).
