9 rules checked: 7 MATCH, 1 DEVIATES, 1 NOT_CHECKABLE.

# GPT audit: pace plan vs exhaust document

**Verdict: FIX-FIRST** ? the 5-hour stop and weekly cap arithmetic align with the written policy. One gap: `exhaust.plan` labels quota exhaustion from weekly usage only and does not gate phase on the 5-hour stop; its output is guidance, while enforcement is performed by `traffic.py`/`pace_plan`.

## What was checked

Read `MyTradingSys/system/EXHAUST_PHASE.md:1-48`, `MyTradingSys/system/SUPER_SESSION.md:105-119` (referenced budget policy), `scripts/dev/supervisor.py:895-1023`, `scripts/dev/exhaust.py:23-29,220-236`, and `scripts/dev/traffic.py` (shared limits). No market data or secret files were read. The card-referenced `2026-11-04_gpt-audit-pace-plan.md` was not present. The report follows the Layer Lab dated report path.

## Findings

| # | Severity | Written rule (file:line; quoted evidence) | Implementation (file:line; quoted evidence) | Verdict | Finding / proposed fix |
|---|---|---|---|---|---|
| 1 | LOW | `EXHAUST_PHASE.md:3`: ?from 2 hours before a login's weekly reset? enter quota-use window; ?in the last hour it does.? | `exhaust.py:23-24,223-231`: `PLAN_MIN = 120`, `EXHAUST_MIN = 60`; phase uses `minutes <= 60` exhaust and `<=120` plan. | MATCH | Integer floor of minutes produces the documented T-120/T-60 boundaries; see phase-boundary note below. |
| 2 | LOW | `EXHAUST_PHASE.md:5`: ?In this window the 5 h stop is 95 ? not 100.? `SUPER_SESSION.md:108`: ?Last 2 h ? 5 h stop moves to 95.? | `traffic.py` `EXHAUST_CEIL = 95`; `five_ceiling` returns it for `0 < h_to_reset <= EXHAUST_H` (2h). `supervisor.py:988-989,1011-1012` caps room and STOPs at that ceiling. `exhaust.py:233-235` reports `five_stop` using the shared helper. | MATCH | Shared enforcement lives in `pace_plan`; `exhaust.plan` reports the same stop value. |
| 3 | MED | `SUPER_SESSION.md:106-108`: do not ?run the 5 h window to 100?; stop at 80 normally, 95 within last 2h. | `traffic.py` `SPAWN_CEIL=80`, `EXHAUST_CEIL=95`; `supervisor.py:988-989,1011-1012` computes `room = max(0, min(share / k, ceil - five))`, then STOPs at `five >= ceil`. | MATCH | Daily window room is clamped at the appropriate ceiling and cannot schedule past it. |
| 4 | MED | `SUPER_SESSION.md:107-108`: weekly caps A 95, B 75 on JIS-NB else 95, C 85 on JIS-NB else 95; last 24h cap 99; `EXHAUST_PHASE.md:3` says spend each model quota in the final 2h. | `supervisor.py:903-915` applies host/login caps and last-day cap; `supervisor.py:1375` passes `weekly_cap(...)` into `pace_plan`. `supervisor.py:978-982` calculates remaining capped weekly room. `exhaust.py:232` lists models whose used percentage is `<100`. | MATCH | Weekly cap enters pace math; exhaust list preserves all models with remaining quota. |
| 5 | MED | `SUPER_SESSION.md:107`: over pace `U > 100 f + 5` throttles to model-free work; `SUPER_SESSION.md:108`: last 24h pace throttle is off. | `supervisor.py:968-982` distributes `cap-week` over `ceil(week_hours/5)` windows; does not itself evaluate `U > 100 f + 5`. | DEVIATES | `pace_plan` computes spend target from the cap, but no pace-throttle predicate is present in this function. `traffic.py budget` owns that policy; the planner?s weekly share alone is not equivalent to the stated over-pace rule. Keep the throttle gate in its caller and add an explicit test/row-level assertion that it is applied before worker dispatch. |
| 6 | LOW | `EXHAUST_PHASE.md:16`: ?spend the model with the most headroom first?; `:17`: ?use the highest-cost model that still has quota.? | `exhaust.py:232`: `sorted((m for m, used in models.items() if used < 100), key=lambda m: models[m])`. | MATCH | Lower used percentage sorts first, which means more quota headroom first. The code has no model cost metadata, so the ?highest-cost? qualifier is not implemented; this is guidance not enforceable from percentage-only input. |
| 7 | LOW | `EXHAUST_PHASE.md:15-18`: plan/exhaust until ?100% or reset?; phase transitions at T-120, T-60, reset. | `exhaust.py:223-231`: floors minutes to integer; done if `minutes <= 0` or `week >= 100`, exhaust if `<=60`, plan if `<=120`. | MATCH | Boundaries follow the document; `week>=100` ends planning at quota exhaustion. |
| 8 | LOW | `EXHAUST_PHASE.md:30`: `--read` older than 10m or over 2m future exits 2; without it reports unstated. | `exhaust.py:25-26,289-...`: limits are 10 and 2; command parses read, rejects age above max or future skew, and defaults to `unstated`. | MATCH | Freshness guard and provenance default follow the written rule. |
| 9 | LOW | `EXHAUST_PHASE.md:21`: choose a card below remaining quota (`est_turns`); `:24`: model with headroom but no fitting card does independent audits. | `exhaust.py:133-151` `_fitting_ready_cards` reads ready cards and sorts by priority/turns for radar banner only; `plan` receives no card estimate. | NOT_CHECKABLE | The plan output does not select or validate work against quota estimates. This rule is handled by the session/operator workflow, not auditable from `plan`?s inputs. |

## Phase boundary note

`exhaust.py` computes `minutes = int(seconds // 60)` at `:223`, so a reset less than one minute away floors to zero and reports `done` (since `minutes <= 0`). That is consistent with stopping at reset but can stop slightly early. The `T-121`, `T-120`, `T-59`, and past-reset cases in `EXHAUST_PHASE.md:39` are otherwise represented by the comparison branches at `:224-231`.

## Follow-up cards

None created. No source or script files were edited.
