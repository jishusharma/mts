# B079 - CAPS_CHECK.WITHIN_MAX_LOSS COMPUTED BUT NEVER ENFORCED

Opened: 2026-09-27 by session Claude Sonnet 5 (execution-layer audit, continuing T050 review).
Severity: HIGH (a governance cap can be silently exceeded; caps are the
whole point of a "conservative first slice" execution layer).
Status: CLOSED. Receipt: 5e387a1, b05c1cf (full receipt in the BUGS.md B079 row).

## DESCRIPTION

plan_compiler.py's compile_plan() computes caps_check.within_max_loss -
whether the plan's actual computed worst-case loss (from real entry/stop
math, not the declared cap alone) fits within plan.caps.max_loss_usd - and
returns it as part of the compiled dict. Nothing reads this field
afterward. executor.py.execute_plan() takes the compiled dict and goes
straight to placing entry orders; it never references caps_check at all.

trade_plan_validator.py's _validate_caps() is a different, narrower check:
it confirms the plan's DECLARED caps (max_notional_usd, max_loss_usd,
max_concurrent_orders) are within system-wide ceilings
(MAX_NOTIONAL_CEILING, MAX_LOSS_FLOOR) and does a coarse pre-compile
sanity check on total sizing. It runs before plan_compiler.py and cannot
know the actual computed worst-case loss - that number only exists after
compile_plan() runs, which is exactly when caps_check.within_max_loss is
computed and then dropped.

## CONCRETE FAILURE SCENARIO

A plan declares max_loss_usd=-200 (validator accepts: it's within
[-500, 0)). Its actual stop distance and sizing, once compiled, produce a
worst_case_loss of -350 (caps_check.within_max_loss = False, since
-350 < -200). Nothing in the pipeline stops this plan from reaching
executor.py, which places the entry orders and the (real) stop with no
regard for the fact that the plan itself already flagged its own cap as
breached.

## REQUIRED FIX

executor.py.execute_plan() (or a thin wrapper called before it) must
check compiled["caps_check"]["within_max_loss"] (and ideally a
within_max_notional check, which does not currently exist at all - see
below) and raise ExecutionHalted before placing any order if either is
False or "unknown_until_fill" for a plan type where that matters.

## RELATED GAP: NO within_max_notional CHECK EXISTS

caps_check only carries max_notional_usd and max_loss_usd through as
pass-through values plus the one within_max_loss boolean. There is no
within_max_notional computed or checked anywhere - max_position_size
(total_entry_size) is returned but never compared against
plan["caps"]["max_notional_usd"] by plan_compiler.py or executor.py.
Only trade_plan_validator.py's coarse pre-compile 1.5x-margin sanity
check touches notional at all, and that runs on declared inputs before
compilation, not on the compiled order list.

## BLOCKS

- T050 Phase 3 exit criterion in spirit, if not in the letter (Phase 3's
  literal exit criterion is about order/cancel mechanics and does not
  mention caps enforcement, but placing real orders - even testnet -
  through a pipeline whose own safety numbers are decorative is a real
  gap worth closing before Phase 5 (live, operator-gated)).
- Governance limits generally: T050's own item doc lists "governance
  limits... all undefined today" as a named risk; this is that risk
  materializing in the one place caps math actually exists.

## UPDATES

2026-09-27: Found during an execution-layer audit prompted by the
operator wanting parallel work done while setting up testnet credentials.
Not yet fixed - filed per the same pattern as B077/B078 (file, do not
fix without review, since this touches the order-placement path).
