"""
MyTradingSys/execution/trade_plan_validator.py

Step 2 of the T050 execution-layer roadmap (see
MyTradingSys/research/_archive/loose_2026-10/execution_system_architecture.md). Validates a
trade-plan JSON file (MyTradingSys/execution/trade_plan_schema.json)
against structural rules AND business caps before it reaches
plan_compiler.py (step 3).

Dependency-free by design (no jsonschema package) to match the rest of
execution/ (urllib-only, stdlib-only). Validation is hand-written, not
schema-driven, so trade_plan_schema.json is the documentation of intent
and this file is the enforcement - keep them in sync by hand.

Conservative defaults (caps ceiling, ladder size) are the T050 dependency
list's placeholders, not operator-confirmed numbers. Flagged in
research/_archive/loose_2026-10/opus_handoff_context.md as pending operator/Opus decision.

Run directly against one file:
    python MyTradingSys/execution/trade_plan_validator.py path/to/plan.json

Run the example suite (5 valid, 3 invalid) and report pass/fail:
    python MyTradingSys/execution/trade_plan_validator.py --examples
"""
import sys
sys.dont_write_bytecode = True

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"

MAX_NOTIONAL_CEILING = 10000      # conservative T050 default; operator may raise later
MAX_LOSS_FLOOR = -500             # conservative T050 default
MAX_CONCURRENT_ORDERS_CEILING = 10
MAX_LADDER_RUNGS = 10
ALLOWED_INSTRUMENTS = {"BTC-PERPETUAL"}
ALLOWED_SIDES = {"LONG", "SHORT"}
ALLOWED_ENTRY_TYPES = {"market", "limit", "ladder"}
ALLOWED_STOP_TYPES = {"fixed_percent", "trailing_percent", "breakeven_after_fills"}


class ValidationError(Exception):
    """Raised with a human-readable reason; caught by validate() and turned
    into a (False, reason) result rather than propagating - a validator that
    crashes on bad input is itself a bug."""


def _require(cond, msg):
    if not cond:
        raise ValidationError(msg)


def _parse_iso8601(s, field_name):
    try:
        # Python's fromisoformat wants +00:00 not Z pre-3.11; normalise.
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception as e:
        raise ValidationError(f"{field_name}: not a valid ISO-8601 timestamp ({s!r}): {e}")


def validate(plan: dict) -> tuple:
    """Returns (ok: bool, reason: str). reason is 'OK' when ok is True,
    otherwise a specific rejection message. Never raises - a plan that
    fails validation is expected input, not a program error."""
    try:
        _validate_structure(plan)
        _validate_caps(plan)
        return True, "OK"
    except ValidationError as e:
        return False, str(e)


def _validate_structure(plan: dict):
    for field in ("plan_id", "account", "instrument", "side", "validity",
                  "entry", "base_unit", "stop", "caps"):
        _require(field in plan, f"missing required field: {field}")

    _require(isinstance(plan["plan_id"], str) and plan["plan_id"], "plan_id must be a non-empty string")
    _require(isinstance(plan["account"], str) and plan["account"], "account must be a non-empty string")
    _require(plan["instrument"] in ALLOWED_INSTRUMENTS,
              f"instrument must be one of {ALLOWED_INSTRUMENTS}, got {plan['instrument']!r}")
    _require(plan["side"] in ALLOWED_SIDES, f"side must be one of {ALLOWED_SIDES}, got {plan['side']!r}")

    v = plan["validity"]
    _require(isinstance(v, dict) and "start" in v and "end" in v, "validity must have start and end")
    start = _parse_iso8601(v["start"], "validity.start")
    end = _parse_iso8601(v["end"], "validity.end")
    _require(end > start, "validity.end must be after validity.start")

    base_unit = plan["base_unit"]
    _require(isinstance(base_unit, (int, float)) and base_unit > 0, "base_unit must be a positive number")

    _validate_entry(plan["entry"])
    _validate_stop(plan["stop"])
    if "targets" in plan:
        _validate_targets(plan["targets"])
    if "breakeven_after_first_target" in plan:   # R2: position_manager moves the stop to entry after target 1
        _require(plan["breakeven_after_first_target"] is True,
                 "breakeven_after_first_target must be the boolean true when present (omit it to disable)")
        _require(len(plan.get("targets") or []) >= 2,
                 "breakeven_after_first_target needs at least 2 targets (a runner must remain after the first fills)")


def _validate_entry(entry: dict):
    _require(isinstance(entry, dict) and "type" in entry, "entry must have a type")
    etype = entry["type"]
    _require(etype in ALLOWED_ENTRY_TYPES, f"entry.type must be one of {ALLOWED_ENTRY_TYPES}, got {etype!r}")

    if etype == "limit":
        _require("price" in entry, "entry.type=limit requires entry.price")
        _require(isinstance(entry["price"], (int, float)) and entry["price"] > 0,
                  "entry.price must be a positive number")

    elif etype == "ladder":
        for f in ("range", "rungs", "size_multipliers"):
            _require(f in entry, f"entry.type=ladder requires entry.{f}")
        rng = entry["range"]
        _require(isinstance(rng, dict) and "low" in rng and "high" in rng, "entry.range must have low and high")
        _require(rng["low"] > 0 and rng["high"] > 0, "entry.range values must be positive")
        _require(rng["low"] < rng["high"], "entry.range.low must be less than entry.range.high")

        rungs = entry["rungs"]
        _require(isinstance(rungs, int) and 1 <= rungs <= MAX_LADDER_RUNGS,
                  f"entry.rungs must be an integer in [1, {MAX_LADDER_RUNGS}], got {rungs!r}")

        mults = entry["size_multipliers"]
        _require(isinstance(mults, list) and len(mults) == rungs,
                  f"entry.size_multipliers length ({len(mults) if isinstance(mults, list) else 'n/a'}) "
                  f"must equal entry.rungs ({rungs})")
        _require(all(isinstance(m, (int, float)) and m > 0 for m in mults),
                  "entry.size_multipliers values must all be positive numbers")

    # type == "market" needs nothing further


def _validate_stop(stop: dict):
    _require(isinstance(stop, dict) and "type" in stop, "stop must have a type")
    stype = stop["type"]
    _require(stype in ALLOWED_STOP_TYPES, f"stop.type must be one of {ALLOWED_STOP_TYPES}, got {stype!r}")

    if stype in ("fixed_percent", "trailing_percent"):
        _require("percent_below_entry" in stop, f"stop.type={stype} requires stop.percent_below_entry")
        pct = stop["percent_below_entry"]
        _require(isinstance(pct, (int, float)) and 0 < pct <= 50,
                  "stop.percent_below_entry must be in (0, 50]")
    elif stype == "breakeven_after_fills":
        _require("min_fills_for_breakeven" in stop, "stop.type=breakeven_after_fills requires min_fills_for_breakeven")
        n = stop["min_fills_for_breakeven"]
        _require(isinstance(n, int) and n >= 1, "stop.min_fills_for_breakeven must be a positive integer")


def _validate_targets(targets: list):
    _require(isinstance(targets, list), "targets must be a list")
    total_pct = 0
    for i, t in enumerate(targets):
        _require(isinstance(t, dict) and "amount_percent" in t and "pnl_target_percent" in t,
                  f"targets[{i}] must have amount_percent and pnl_target_percent")
        ap = t["amount_percent"]
        pp = t["pnl_target_percent"]
        _require(isinstance(ap, (int, float)) and 0 < ap <= 100, f"targets[{i}].amount_percent must be in (0, 100]")
        _require(isinstance(pp, (int, float)) and pp > 0, f"targets[{i}].pnl_target_percent must be positive")
        total_pct += ap
    _require(total_pct <= 100.0001, f"targets amount_percent sums to {total_pct}, must not exceed 100")


def _validate_caps(plan: dict):
    caps = plan["caps"]
    for f in ("max_notional_usd", "max_loss_usd", "max_concurrent_orders"):
        _require(f in caps, f"caps.{f} is required")

    max_notional = caps["max_notional_usd"]
    _require(isinstance(max_notional, (int, float)) and 0 < max_notional <= MAX_NOTIONAL_CEILING,
              f"caps.max_notional_usd must be in (0, {MAX_NOTIONAL_CEILING}], got {max_notional!r}")

    max_loss = caps["max_loss_usd"]
    _require(isinstance(max_loss, (int, float)) and MAX_LOSS_FLOOR <= max_loss < 0,
              f"caps.max_loss_usd must be in [{MAX_LOSS_FLOOR}, 0), got {max_loss!r}")

    max_orders = caps["max_concurrent_orders"]
    _require(isinstance(max_orders, int) and 1 <= max_orders <= MAX_CONCURRENT_ORDERS_CEILING,
              f"caps.max_concurrent_orders must be in [1, {MAX_CONCURRENT_ORDERS_CEILING}], got {max_orders!r}")

    # Cross-check: a ladder's rung count + 1 stop + len(targets) must not exceed the cap.
    entry = plan["entry"]
    order_count = 1  # stop order always present
    if entry["type"] == "ladder":
        order_count += entry["rungs"]
    else:
        order_count += 1  # single market/limit entry order
    order_count += len(plan.get("targets", []))
    _require(order_count <= max_orders,
              f"plan requires {order_count} concurrent orders (entry+stop+targets) "
              f"but caps.max_concurrent_orders is {max_orders}")

    # Worst-case notional sanity check against the base_unit * multipliers (or base_unit alone).
    entry = plan["entry"]
    if entry["type"] == "ladder":
        total_units = sum(entry["size_multipliers"]) * plan["base_unit"]
    else:
        total_units = plan["base_unit"]
    # total_units is a contract-count proxy in USD terms for this inverse instrument;
    # exact notional depends on fill price, so this is a coarse pre-check, not the
    # authoritative figure - plan_compiler.py computes the precise worst case.
    _require(total_units <= max_notional * 1.5,
              f"entry sizing ({total_units} units) looks inconsistent with "
              f"caps.max_notional_usd ({max_notional}) even at a loose 1.5x margin - "
              f"check base_unit/size_multipliers before compiling")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_file", nargs="?", help="Path to a trade-plan JSON file")
    ap.add_argument("--examples", action="store_true",
                     help="Validate every file in execution/examples/ and report pass/fail vs filename convention")
    args = ap.parse_args()

    if args.examples:
        return _run_examples()

    if not args.plan_file:
        print("usage: trade_plan_validator.py <plan.json> | --examples")
        return 2

    path = Path(args.plan_file)
    if not path.exists():
        print(f"MISSING: {path}")
        return 2

    plan = json.loads(path.read_text(encoding="utf-8"))
    ok, reason = validate(plan)
    print(f"{'PASS' if ok else 'FAIL'}: {path.name}: {reason}")
    return 0 if ok else 1


def _run_examples() -> int:
    if not EXAMPLES_DIR.exists():
        print(f"MISSING: {EXAMPLES_DIR}")
        return 2

    files = sorted(EXAMPLES_DIR.glob("*.json"))
    if not files:
        print(f"NO EXAMPLES FOUND in {EXAMPLES_DIR}")
        return 2

    all_ok = True
    for f in files:
        expected_valid = f.name.startswith("valid_")
        expected_invalid = f.name.startswith("invalid_")
        if not (expected_valid or expected_invalid):
            print(f"SKIP: {f.name} (name does not start with valid_ or invalid_)")
            continue

        plan = json.loads(f.read_text(encoding="utf-8"))
        ok, reason = validate(plan)

        matches_expectation = (ok and expected_valid) or (not ok and expected_invalid)
        status = "PASS" if matches_expectation else "MISMATCH"
        if not matches_expectation:
            all_ok = False
        print(f"{status}: {f.name}: validator_says={'valid' if ok else 'invalid'} ({reason})")

    print()
    print("ALL EXAMPLES BEHAVED AS EXPECTED" if all_ok else "SOME EXAMPLES DID NOT MATCH EXPECTATION - see above")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
