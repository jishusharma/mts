# promote.py gate logic bug hunt

## Verdict: FIX-FIRST (1 low-severity manifest validation defect)

Scope: read `MyTradingSys/backtest/layers/promotion/promote.py`, its specification `MyTradingSys/system/PROMOTION_PIPELINE.md`, and `MyTradingSys/backtest/layers/promotion/test_promote.py`. No market bars or outcome data were needed. No existing test command was run because the test fixture launches Git subprocesses, which this task explicitly prohibits.

## Finding

| Severity | File:line | Finding | Reproducing input / actual result | Proposed fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/backtest/layers/promotion/promote.py:293-296` | Validation read `at` is checked only as a nonempty string, despite the manifest contract documenting an ISO date (`promote.py:20`) and the broader fail-closed requirement. A malformed or impossible date is accepted if the rest of the manifest passes. | Starting with the passing fixture in `test_promote.py:63-71`, replace `validation_reads[0].at` with `"not-a-date"`; `check()` passes this record because the branch tests `_is_str` only. `"2026-99-99"` is also accepted. | Parse with `date.fromisoformat` (and require the declared ISO form) before accepting a read record; reject invalid dates. Add this test before changing implementation. |

This is a metadata integrity issue: code does not read VALIDATION/HOLDOUT data, as stated in the module and pipeline spec. The VALIDATION reference is checked for existence; the HOLDOUT reference intentionally is not required to be a repository file. Neither manifest `at` value is checked against the PRE_REG/screen chronology. The latter behavior is not asserted as a defect because the written gate spec only requires exactly one read record.

## Boundary observations (current behavior)

| Gate | Reproducing boundary | Actual result |
|---|---|---|
| Holm critical value | `holm_z(1)`, `holm_z(3)`, `holm_z(40)` | `1.959964`, `2.393980`, `3.227218`; variant 1 matches the documented two-sided 5% z. |
| Holm adjusted CI | OOS `net_r=0.12`, CI `[0.09,0.15]`, variants `3` | Adjusted low is `0.12 - holm_z(3) * (0.06/3.92) = 0.08336`; passes this sub-gate. At equality `net_r == z*se`, code rejects because it uses `<= 0` (`promote.py:259-260`). |
| MDE floor | Same OOS values, 250 trades, variants `3` | Computed floor `170.1542`; 250 passes. Since code compares integer `n_trades < floor`, the effective minimum is `ceil(floor)`; exactly 171 passes and 170 rejects this sub-gate (`promote.py:261-263`). |
| Basic trade floor | `n_trades=30` (integer, with consistent positive OOS evidence) | The explicit floor rejects only values below 30 (`promote.py:264-265`); equality is allowed per spec. Existing test covers 5 but not equality. |
| CSV tolerances | Recomputed CSV count `n2`; manifest count difference exactly `0.05*n2` | Accepted at the tolerance boundary because mismatch rejects only `>` (`promote.py:245-246`). Existing tests cover a large mismatch, not equality. |

Computed using read-only command: `python -c "from MyTradingSys.backtest.layers.promotion import promote as p; print('holm', [(v, round(p.holm_z(v),6)) for v in (1,3,40)]); ..."`. These are gate arithmetic observations, not backtest results.

## Existing tests that reach these branches

- Holm rejection: `test_promote.py:95-99` (40 variants; adjusted CI fails). This reaches the Holm rejection branch, but no equality/just-above boundary test exists.
- MDE rejection: `test_promote.py:105-106` (31 trades and wider CI). This reaches MDE rejection, but not its exact computed-floor equality or a case where MDE alone rejects while Holm-adjusted CI passes.
- Basic floor rejection: `test_promote.py:194-195` (5 trades). No exact 30-trade acceptance boundary.
- CSV count rejection: `test_promote.py:126-127` (300 vs 250). No exact 5% tolerance boundary.
- Validation read count/ref: `test_promote.py:101-103`, `206-209`. No date-format or date-validity test.

## Gate branches not reached by the current tests

The list is limited to gate branches in `check()` and adjacent gate arithmetic that the read test file does not exercise directly:

1. `promote.py:156-167`: wrong `setup_id`/`layer` prefix pairing; non-string but nonempty `layer`; a requested mode validly set to `shadow` versus `testnet` at `check()` level.
2. `promote.py:182-191`: a SHA that contains the PRE_REG path but its blob differs from HEAD, and HEAD missing the PRE_REG path. Existing `test_pre_reg_edited_after_registration` does exercise the changed-blob case at `test_promote.py:359-365` (so only the missing-HEAD branch is absent).
3. `promote.py:206-210`: equal PRE_REG and first-screen commit timestamps (strict `<` boundary); screen file added in multiple commits where first-add date determines the result.
4. `promote.py:230-246`: `legacy=True` with an absent CSV passes recomputation by design (covered at `test_promote.py:129-134`); CSV recomputation error branches for missing `net_r` column, empty file, non-finite entry, and manifest-vs-CSV delta exactly at `TOL_R` are not directly covered.
5. `promote.py:253-265`: Holm equality boundary; malformed `variants` values skip Holm/MDE inside G4 and are later rejected by G5; MDE exact-boundary and MDE-only rejection; integer trade-floor equality 30; fractional `n_trades` rejection.
6. `promote.py:270-284`: ledger CSV read error, malformed CSV header/no `study` column, and multiple matching rows with variants count mismatch.
7. `promote.py:287-296`: a non-list read record, malformed date (the finding above), missing/invalid read date; a `holdout_reads.ref` that is any nonempty string (not required to resolve to a file by the written spec).
8. `promote.py:298-300` and `_blocked` `124-140`: malformed blocklist types, malformed entries, and reverse-prefix overlap where a listed prefix is more specific than `setup_id`.
9. `check()` return ordering with multiple simultaneous failures: there is no precedence contract or test for reason ordering; result remains REJECT. No pass-bypass from this was identified.

Adjacent `register()` branches are partly covered (duplicate shadow, testnet needs shadow/size, mode mismatch, unreadable registry, demote) in the latter half of `test_promote.py`. I did not characterize those as `check()` gate coverage.

## Proposed test status

`proposed_test_promote.py` contains one EXPECT-FAILS-CURRENT test for the malformed ISO date defect and PASS-ONLY boundary probes for equality cases. It was not executed because its inherited fixture creates and commits a temporary Git repository; therefore the fail-on-current-code behavior is established by code-path inspection, not a test run. No backtest or promotion verdict was produced.

Follow-up cards created: none.

Noticed: none.
