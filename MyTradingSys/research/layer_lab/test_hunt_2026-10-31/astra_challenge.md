# Astra challenge: luna promote-gates and auto_trader fail-closed hunts

Producer: gemini (Claude Sonnet 5.5 via Antigravity). Independent re-derivation from source on trunk `fc6e69c89`; reproductions run with `research`-free read-only Python (no engine, no market data, no network). Ratings: CONFIRMED / WRONG / MISSED. Nothing here is a backtest verdict.

## A. `test_hunt_2026-10-31/promote_gates_bug_hunt.md` (5 findings re-derived)

| # | Luna claim | Rating | file:line and reproducing input |
|---|---|---|---|
| A1 | `validation_reads.at` / `holdout_reads.at` only checked non-empty (LOW, FIX-FIRST) | CONFIRMED | `promote.py:293` uses `_is_str` (`:108-109`). `_is_str("not-a-date")` and `_is_str("2026-99-99")` both return True. Spec says ISO date (`promote.py:20`). Also applies to `holdout_reads` (same branch), which Luna's text only half-states. |
| A2 | Holm gate rejects at equality (`<= 0`) | CONFIRMED | `promote.py:259`. `holm_z(1,3,40)` = 1.959964, 2.39398, 3.227218; OOS net_r 0.12, CI [0.09,0.15], 3 variants -> adjusted low 0.083357 (Luna: 0.08336). |
| A3 | MDE floor 170.1542 for 250 trades; effective minimum ceil(floor) | CONFIRMED | `promote.py:261-263`, `mde_floor` `:62-66` -> 170.15412 on the same input. 170 rejects, 171 passes. |
| A4 | Basic floor allows exactly 30 | CONFIRMED | `promote.py:264` (`< MIN_TRADES`), `MIN_TRADES = 30` at `:40`. |
| A5 | CSV count tolerance uses `>`, so exactly 5% passes | CONFIRMED | `promote.py:245` (`> TOL_N * n2`), `TOL_N = 0.05` at `:47`. |

Verdict on report A: no false alarms among the 5. Weak point: severity is not argued (a malformed `at` date weakens the "read once" audit trail but cannot change PASS/REJECT of the statistics).

### Missed (A)
- A-M1 (LOW): the `ref` of `holdout_reads` is never checked at all (`promote.py:295` is `key == "validation_reads"` only). Luna notes this as "intentional"; the spec text was not cited, so intent is unverified here.
- A-M2 (LOW): `at` of validation and holdout is not compared with each other or with the PRE_REG/screen commit dates (chronology), so a holdout "read" dated before the screen passes. Luna mentioned it and dropped it; this challenge keeps it as an open question for the spec owner, not a proven bug.

## B. `test_hunt_2026-10-31/auto_trader_failclosed_matrix.md` (5 claims re-derived, plus staleness check)

Key fact: the matrix was shipped in `1080ce6f7` (2026-10-31 02:00 +05:30). `MyTradingSys/execution/test_auto_trader_failclosed.py` landed 12 minutes later in `9cf5a2191` (19 tests). The matrix searched only `test_auto_trader.py` style files, so several "NONE" test rows are now false.

| # | Luna claim | Rating | file:line and evidence |
|---|---|---|---|
| B1 | `exchange_flat` exception conversion untested | WRONG (stale) | Source `auto_trader.py:688-689`. Tests: `test_auto_trader_failclosed.py:60-72` (auth error, ValueError, size "abc" -> None) and `:82-95` (MTS_ACCOUNT restored). |
| B2 | manager respawn raise untested | WRONG (stale) | Source `auto_trader.py:730-734`. Test `test_auto_trader_failclosed.py:102-117` (`OSError("process table full")`, slot stays busy, retried). |
| B3 | ledger write error untested | WRONG (stale) | Test `test_auto_trader_failclosed.py:128-139` (`ledger_error` and `trade_closed` both logged). |
| B4 | two live managers for one account untested | WRONG (stale) | Source `auto_trader.py:851-856`. Test `test_auto_trader_failclosed.py:252-260` asserts `adopt_skipped` and the alert. |
| B5a | process enumeration failure -> `[]` -> live manager treated dead, duplicate respawn risk, NOT fail closed | CONFIRMED (and still unfixed) | `auto_trader.py:798-808` returns `[]` on any exception; `recover_slots` `:845,850,862` then builds `DeadProc`; `settle_slot` respawns when the exchange shows an open position (`:716-734`). Repro: patch `subprocess.run` to raise `OSError`; `list_process_cmdlines()` -> `[]`. The only test, `test_auto_trader_failclosed.py:297-305`, PINS the `[]` result instead of guarding the consequence. |
| B5b | missing/unreadable log -> `[]`, open exposure forgotten | CONFIRMED | `auto_trader.py:822-824`. Repro: `open_plans_from_log(<missing path>)` -> `[]`. No test of the OSError branch (test at `:247-250` covers only garbage lines). |
| B6 | `place` exceptions from `run` (timeout, OSError) escape | CONFIRMED | `auto_trader.py:636-640` (no try/except; `subprocess.run` with `timeout`) vs docstring "never raises" at `:644`. Repro: `at.run(["python","-c","import time;time.sleep(5)"], timeout=1)` raises `TimeoutExpired`. No test (`PlaceRefusalTest` `:147-196` only fakes return codes). |

Verdict on report B: 4 of 6 re-derived "untested" rows are false today because they predate the 19-test file; the 3 real gaps (B5a, B5b, B6) hold.

### Missed (B)
- B-M1 (MEDIUM): `open_plans_from_log` crashes on a valid JSON line that is not an object. `auto_trader.py:827-830` catches only `ValueError`, then calls `e.get`. Repro: log containing `[]` after an entered row -> `AttributeError: 'list' object has no attribute 'get'`; recovery at start fails. Existing test uses only `{not json` (`test_auto_trader_failclosed.py:247-250`).
- B-M2 (LOW): `exchange_flat` uses `int(size) == 0` (`auto_trader.py:687`): a fractional size of 0.5 truncates to 0 and is reported flat. Repro: `get_position` -> `{"size": 0.5}` -> `exchange_flat("x")` is `True`. Deribit BTC-PERPETUAL size is integer USD, so this is latent; no test.
- B-M3 (LOW): `place` docstring "never raises" is false (see B6); the contract and the code disagree.

## Reproductions
`python <scratch>/repro.py` run on this tree: outputs quoted above (holm, floor, `_is_str`, AttributeError, TimeoutExpired, exchange_flat 0.5 -> True, `[]` on enumeration failure and missing log).

## Not done
No fixes made (card scope: report only). Follow-up cards for A1, B5a, B5b, B6, B-M1 filed separately if the operator wants fixes.
