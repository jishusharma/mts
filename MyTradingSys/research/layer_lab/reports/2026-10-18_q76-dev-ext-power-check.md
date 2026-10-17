# Q76 DEV_EXT power check — 2026-10-18

**1,207 feasible days total (662 baseline reproduced + 545 new DEV_EXT days), 1,220 below the 2,427-day gate. B187 remains open; fetching later history alone is not justified as a complete fix.**

## What was checked

- `MyTradingSys/research/pit_levels_2026-10-16/bug_b187_evidence.txt:1-6` records the baseline: 662 feasible T days from 912 DEV days and 2,427 needed at m=42. Lines 13-18 estimate DEV_EXT, rather than counting it for this T setup.
- `MyTradingSys/research/pit_levels_2026-10-16/PRE_REG_V2.md:31-45` freezes the power gate and feasibility context: 0.30 R plausible gross effect (OURS), 1.46 R SD, 0.179 R cost, m=42, 2,427 required days. `MyTradingSys/research/pit_levels_2026-10-16/COUNT.txt:1-8` gives 1,835 baseline feasible events on 662 days.
- `MyTradingSys/research/pit_levels_2026-10-16/count_prior_va.py:1-8,25-29,83-131,160-188` defines the count-only PIT event and the stop >=0.40% feasibility rule. The source script was run unchanged first: it reproduced **1,835 events across 662 feasible days**. Command: `python MyTradingSys/research/pit_levels_2026-10-16/count_prior_va.py`.
- DEV_EXT source files found under `F:/MTS/data/dev_ext_2019_2021/klines/` are monthly `BTCUSDT-1m-2020-01.csv` through `BTCUSDT-1m-2021-12.csv`. An in-memory adaptation of that same count script loaded 2020-01-01 through 2021-12-31 only and retained a 2022-01-01 cutoff. It reproduced the same profile builder, prior-day value area, 5m failed-auction event, probe-extreme stop, and 0.40% stop filter. Output: **1,742 feasible events across 545 distinct UTC days**. No outcome column or later bar was read.

## B187 update

DEV_EXT contributes 545 distinct feasible days in 2020–2021. These dates do not overlap the 2022–2024 baseline, so 662 + 545 = **1,207**, still **1,220 short** of 2,427. Thus B187's central power concern is confirmed; the prior estimate of 465 added days in `bug_b187_evidence.txt:17` is superseded by this direct count for the registered failed-auction T rule. Even fully feasible 2019 adds at most 365 calendar days, leaving at least 855 days missing; a qualifying history extension beyond 2019 or a written pre-registration change to the gate would be needed. No data was fetched. `PRE_REG_V2.md` and the existing evidence file were not edited (both are read-only scope).

## Findings

| Severity | Evidence | Finding | Proposed action |
|---|---|---|---|
| HIGH | `bug_b187_evidence.txt:3-6`; `PRE_REG_V2.md:35-45`; count output above | **MATCH:** 662 baseline reproduced and the total with DEV_EXT is 1,207, below 2,427. | Keep this study blocked unless additional eligible history or a written gate revision supplies the missing 1,220 feasible days. |
| LOW | `bug_b187_evidence.txt:17` | **MISMATCH:** prior DEV_EXT estimate (+465) understates the directly counted addition (+545) for this setup. | Use the direct count in the B187 status record. |

Follow-up cards created: none.
