# Q76 DEV_EXT trust re-check - 2026-11-01 (DSA)

## Reviewer and producer

- Reviewer: DeepSeek (DSA builder) on JIS-NUC, 2026-11-01. This is a different vendor from the producer.
- Producer: CODEX/GPT, per `MyTradingSys/system/tasks/archive/q76-dev-ext-power-check.json` (`note`, producer=CODEX).
- Prior review: `2026-10-23_trust-recheck-q76-dev-ext-power-check.md` was GPT reviewing GPT and therefore could not propose VERIFIED-C2 (vendor separation unmet). That gap is what this NUC desk row closes.

## Method

Independent count-only script `F:/MTS/dsa_q76_recheck/independent_count.py`, written from `MyTradingSys/backtest/layers/FORMULAS.md:422-435` (section 18.1 profile) and `MyTradingSys/research/pit_levels_2026-10-16/PRE_REG_V2.md:17-31` plus `:44` (stop floor 0.40 %). It imports neither `count_prior_va.py` nor `vp_pivot_probe.build_profile`. Only timestamps and OHLCV columns are read; no outcome column is touched.

Data: `F:/MTS/data/dev_ext_2019_2021/klines`, 24 monthly files BTCUSDT-1m-2020-01 .. 2021-12, 1,052,640 of 1,052,640 minute bars loaded, zero files dated 2022 or later.
## Re-derivation

| Check | Independent result | Assessment |
|---|---:|---|
| DEV_EXT feasible events and distinct UTC days, stop floor 0.40 % | 1,742 events / 545 days | MATCH - `2026-10-18_q76-dev-ext-power-check.md:10` gives 1,742 / 545 |
| Combined feasible days | 662 + 545 = 1,207 | MATCH - 662 is `COUNT.txt` baseline; the sum is arithmetic |
| Frozen requirement | 2,427 days | MATCH - `PRE_REG_V2.md:28`; 1,207 is 1,220 short |
| Production run of `count_prior_va.py` (baseline 662) | not re-run by me | not claimed - outside this card's `scope_in`, which names the DEV_EXT files only |

Tolerance: exact counts are the gate (DSA role C, `DSA_SESSION_PROMPT.md` 5e). The result is 0 % off, inside the 1 % lab tolerance.

Both missing-minute policies were tested: dropping prior days with more than 5 missing minutes and keeping every day give the same 545 / 1,742. The result does not rest on that choice.
## Cutoff proof

The loader raises on any bar timestamp at or after 2022-01-01 (`CUT = 1640995200000`). It ran clean, so no bar at or after the cutoff was read. The source directory holds zero files dated 2022 or later. No outcome, VALIDATION or HOLDOUT bar was accessed.

## Mutation check

Changed only the floor constant in a scratch copy: 0.40 -> 0.50. Count moved 1,742/545 -> 1,443/524, which is a real change, so the floor is live in the count. Production script and the read-only data are unchanged.

## Conclusion

The producer's numbers reproduce exactly under an independent implementation and a different reviewing vendor.

Tag proposal: **VERIFIED-C2**. The study itself stays BLOCKED: 1,207 feasible days against 2,427 required, 1,220 short, per `PRE_REG_V2.md:28`. Trust tag and study verdict are separate things; this report certifies the count only.

