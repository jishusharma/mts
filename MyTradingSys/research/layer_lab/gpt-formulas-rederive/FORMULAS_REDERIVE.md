# GPT re-derivation of FORMULAS.md sections 7, 12, 13, 17 (2026-10-17)

Method: expected numbers computed from the FORMULAS.md definitions only (script GPT side, written before any code was opened), then repo functions evaluated on the same inputs. Script: `rederive.py.txt` (copy to a temp .py, run from `MyTradingSys/`). Repo values: `runner.forward_return_stats`, `positioning.trade_costs.net_return`, `mts_math.calculate_net_rr`.

| example | FORMULAS | GPT | repo | match |
|---|---|---|---|---|
| S7 long ret h=3 (own example; FORMULAS has none) | 0.03 | 0.03 | 0.03 | MATCH |
| S7 long mae h=3 | -0.01 | -0.01 | -0.01 | MATCH |
| S7 short ret h=3 | -0.03 | -0.03 | -0.03 | MATCH |
| S7 short mae h=3 | -0.03 | -0.03 | -0.03 | MATCH |
| S7 i+h>=len contributes nothing (n) | 0 | 0 | 0 | MATCH |
| S12 ATR SMA n=3 | 2.1667 | 2.16667 | - | NOT_IN_DATA |
| S13 long 100->101 net (records as written) | 0.0084 | 0.0084 | RAISES: funding records cover [8, 16] but trade window is (0, 16]; l | MISMATCH @ FORMULAS.md:353 vs trade_costs.py:27 (B103 guard) |
| S13 long 100->101 net (+t=0 zero-rate pad) | 0.0084 | 0.0084 | 0.0084 | MATCH |
| S13 short 100->99 net (records as written) | 0.0092 | 0.0092 | RAISES: funding records cover [8, 16] but trade window is (0, 16]; l | MISMATCH @ FORMULAS.md:353 vs trade_costs.py:27 (B103 guard) |
| S13 short 100->99 net (+t=0 zero-rate pad) | 0.0092 | 0.0092 | 0.0092 | MATCH |
| S17 net_rr 100/104/98 | 1.85714 | 1.85714 | 1.85714 | MATCH |
| S17 net_rr tight 100/100.3/99.9 | 1 | 1 | 1 | MATCH |
| S17 stop==entry -> 0 | 0 | 0 | 0 | MATCH |

Notes
- S7 has no numeric worked example in FORMULAS.md; the example (closes 100,102,99,103; i=0; h=3) is ours, derived from the definition at FORMULAS.md:135-137. Repo matches long and short, and the `i+h >= len` case contributes n=0.
- S12 ATR: the repo implementation named by FORMULAS.md:325 (`SetupCandidatesBuilder.averageTrueRange`, Java) is not in this tree (grep of *.java/*.py finds no `averageTrueRange`); the worked example is re-derived (6.5/3 = 2.16667) but the repo value is NOT_IN_DATA. Other python ATR helpers (fabio v3, trendlines, bigmoves) are out of this card's scope.
- S13 MISMATCH (severity LOW, spec staleness, not an arithmetic error): the worked example has funding records at t=8h and 16h with t_in=0. `trade_costs.py:27` (B103 fail-closed span guard: `t_in < funding[0][0]` raises) rejects exactly that input. Deciding definition: FORMULAS.md:353 (example) vs the guard's own comment at trade_costs.py:28. With a zero-rate record at t=0 added (outside (t_in, t_out], so it cannot change the sum) the repo returns 0.0084 / 0.0092, equal to FORMULAS and GPT. Suggested doc fix (not made, per card): state in section 13 that records must span the hold.
- S17: net_rr matches on all three cases (1.857143, 1.0, stop==entry -> 0.0). Fee constant: backtest/fees.py:23 DERIBIT_TAKER = 0.0005 = the FORMULAS.md value; `calculate_net_rr` default is that constant.

Verdict: SOUND (every re-derived number matches; the one mismatch is a stale worked example vs the intentional B103 guard, LOW; no HIGH mismatches so no follow-up cards).
