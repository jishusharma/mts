"""
MyTradingSys/execution/plan_compiler.py

Step 3 of the T050 execution-layer roadmap. Converts a validated trade
plan (trade_plan_validator.py has already returned ok=True) into an
exact order list: entry orders (with tick/size rounding), a stop order,
and target orders. Sends nothing - this is pure computation, no network
calls, so it is fully testable without a Deribit connection or API key.

Rounding rules (BTC-PERPETUAL, inverse, USD-denominated contracts):
  - Price snapped to the nearest 0.5 USD tick.
  - Size (amount) rounded to the nearest $10 contract.
These are Deribit's actual BTC-PERPETUAL contract conventions and are
NOT configurable per-plan - they are exchange constants.

Run directly against one plan file and print the compiled table:
    python MyTradingSys/execution/plan_compiler.py path/to/plan.json

Run against the example suite and print every valid plan's compiled table:
    python MyTradingSys/execution/plan_compiler.py --examples
"""
import sys
sys.dont_write_bytecode = True

import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trade_plan_validator import validate  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"

PRICE_TICK = 0.5
SIZE_INCREMENT = 10


def snap_price(price: float) -> float:
    """Round to the nearest 0.5 USD tick."""
    return round(price / PRICE_TICK) * PRICE_TICK


def round_size(amount: float) -> int:
    """Round to the nearest $10 contract, minimum 10."""
    rounded = round(amount / SIZE_INCREMENT) * SIZE_INCREMENT
    return max(SIZE_INCREMENT, int(rounded))


class CompileError(Exception):
    """Raised when a plan cannot be compiled - e.g. it was never validated,
    or contains a combination the compiler does not yet handle (trailing
    stops need live price tracking, not a static compile step)."""


def compile_plan(plan: dict) -> dict:
    ok, reason = validate(plan)
    if not ok:
        raise CompileError(f"refusing to compile an invalid plan: {reason}")

    side = plan["side"]
    entry = plan["entry"]
    base_unit = plan["base_unit"]
    order_side = "BUY" if side == "LONG" else "SELL"
    opposite_side = "SELL" if side == "LONG" else "BUY"

    entry_orders = []
    if entry["type"] == "market":
        entry_orders.append({
            "label": "entry_market",
            "side": order_side,
            "order_type": "market",
            "price": None,
            "amount": round_size(base_unit),
        })
        # No fill price known until execution; caller supplies fill_price
        # in a second pass for stop/target calc. Compiler returns the
        # order list; executor.py fills in realized entry price after fill.
        avg_entry_estimate = None

    elif entry["type"] == "limit":
        price = snap_price(entry["price"])
        entry_orders.append({
            "label": "entry_limit",
            "side": order_side,
            "order_type": "limit",
            "price": price,
            "amount": round_size(base_unit),
        })
        avg_entry_estimate = price

    elif entry["type"] == "ladder":
        low = entry["range"]["low"]
        high = entry["range"]["high"]
        rungs = entry["rungs"]
        mults = entry["size_multipliers"]

        # Distribute rungs evenly across [low, high]. For a LONG ladder,
        # rung 1 is nearest the top of the range (best/first price touched
        # on the way down), rung N is at the bottom (worst price, biggest
        # size per the multiplier convention in the T050 handoff example).
        # For a SHORT ladder this is mirrored: rung 1 near the bottom.
        if rungs == 1:
            rung_prices = [high if side == "LONG" else low]
        else:
            step = (high - low) / (rungs - 1)
            if side == "LONG":
                rung_prices = [high - i * step for i in range(rungs)]
            else:
                rung_prices = [low + i * step for i in range(rungs)]

        total_weighted_notional = 0.0
        total_size = 0
        for i, (price, mult) in enumerate(zip(rung_prices, mults), start=1):
            snapped_price = snap_price(price)
            size = round_size(base_unit * mult)
            entry_orders.append({
                "label": f"entry_rung_{i}",
                "side": order_side,
                "order_type": "limit",
                "price": snapped_price,
                "amount": size,
            })
            total_weighted_notional += snapped_price * size
            total_size += size

        avg_entry_estimate = (total_weighted_notional / total_size) if total_size else None

    else:
        raise CompileError(f"unhandled entry.type: {entry['type']!r}")

    total_entry_size = sum(o["amount"] for o in entry_orders)

    # --- Stop order ---
    stop_spec = plan["stop"]
    stop_order = None
    worst_case_loss = None
    if avg_entry_estimate is not None:
        if stop_spec["type"] == "fixed_percent":
            pct = stop_spec["percent_below_entry"] / 100.0
            stop_price = (avg_entry_estimate * (1 - pct) if side == "LONG"
                          else avg_entry_estimate * (1 + pct))
            stop_price = snap_price(stop_price)
            stop_order = {
                "label": "stop_order",
                "side": opposite_side,
                "order_type": "stop_market",  # B077: executor places stop_market(trigger=mark); price = trigger
                "price": stop_price,
                "amount": total_entry_size,
                "reduce_only": True,
            }
            price_delta = abs(avg_entry_estimate - stop_price)
            worst_case_loss = -round(price_delta * total_entry_size / avg_entry_estimate, 2) if avg_entry_estimate else None

        elif stop_spec["type"] == "trailing_percent":
            # Trailing stops require live price tracking after entry;
            # the compiler emits the intended trail percent as metadata,
            # not a static order - executor.py (step 4) computes the
            # actual resting stop price on each price update.
            stop_order = {
                "label": "stop_order_trailing",
                "side": opposite_side,
                "order_type": "trailing_stop_metadata_only",
                "trail_percent": stop_spec["percent_below_entry"],
                "amount": total_entry_size,
                "reduce_only": True,
                "note": "executor.py computes the live resting price; compiler cannot precompute a trailing stop.",
            }
            worst_case_loss = None  # depends on live trail behavior, not compile-time knowable

        elif stop_spec["type"] == "breakeven_after_fills":
            stop_order = {
                "label": "stop_order_breakeven_pending",
                "side": opposite_side,
                "order_type": "breakeven_metadata_only",
                "min_fills_for_breakeven": stop_spec["min_fills_for_breakeven"],
                "amount": total_entry_size,
                "reduce_only": True,
                "note": "executor.py places an initial wide stop and moves it to avg_entry once min_fills_for_breakeven rungs land.",
            }
            worst_case_loss = None
    else:
        # Market entry: fill price unknown at compile time.
        stop_order = {
            "label": "stop_order_pending_fill",
            "side": opposite_side,
            "order_type": stop_spec["type"],
            "amount": total_entry_size,
            "reduce_only": True,
            "note": "market entry - executor.py places the stop once the fill price is known.",
        }

    # --- Target orders ---
    target_orders = []
    if avg_entry_estimate is not None:
        for i, t in enumerate(plan.get("targets", []), start=1):
            target_price = (avg_entry_estimate * (1 + t["pnl_target_percent"] / 100.0) if side == "LONG"
                            else avg_entry_estimate * (1 - t["pnl_target_percent"] / 100.0))
            target_price = snap_price(target_price)
            target_amount = round_size(total_entry_size * t["amount_percent"] / 100.0)
            target_orders.append({
                "label": f"target_{i}",
                "side": opposite_side,
                "order_type": "limit",
                "price": target_price,
                "amount": target_amount,
                "reduce_only": True,
            })

    return {
        "plan_id": plan["plan_id"],
        "entry_orders": entry_orders,
        "stop_order": stop_order,
        "target_orders": target_orders,
        "entry_avg_if_ladder_fills": round(avg_entry_estimate, 2) if avg_entry_estimate is not None else None,
        "max_position_size": total_entry_size,
        "worst_case_loss_usd": worst_case_loss,
        "caps_check": {
            "max_notional_usd": plan["caps"]["max_notional_usd"],
            "max_loss_usd": plan["caps"]["max_loss_usd"],
            "within_max_loss": (worst_case_loss >= plan["caps"]["max_loss_usd"]) if worst_case_loss is not None else "unknown_until_fill",
        },
    }


def _print_table(compiled: dict):
    print(f"plan_id: {compiled['plan_id']}")
    print("entry_orders:")
    for o in compiled["entry_orders"]:
        print(f"  {o['label']:20s} {o['side']:5s} {o['order_type']:8s} "
              f"price={o.get('price')!s:>10s} amount={o['amount']}")
    print("stop_order:")
    s = compiled["stop_order"]
    price_str = str(s.get("price", s.get("trail_percent", "n/a")))
    print(f"  {s['label']:20s} {s['side']:5s} {s['order_type']:28s} "
          f"price/trail={price_str:>10s} amount={s['amount']} {s.get('note', '')}")
    if compiled["target_orders"]:
        print("target_orders:")
        for o in compiled["target_orders"]:
            print(f"  {o['label']:20s} {o['side']:5s} {o['order_type']:8s} "
                  f"price={o['price']} amount={o['amount']}")
    print(f"entry_avg_if_ladder_fills: {compiled['entry_avg_if_ladder_fills']}")
    print(f"max_position_size: {compiled['max_position_size']}")
    print(f"worst_case_loss_usd: {compiled['worst_case_loss_usd']}")
    print(f"caps_check: {compiled['caps_check']}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_file", nargs="?")
    ap.add_argument("--examples", action="store_true")
    args = ap.parse_args()

    if args.examples:
        files = sorted(EXAMPLES_DIR.glob("valid_*.json"))
        if not files:
            print(f"NO VALID EXAMPLES FOUND in {EXAMPLES_DIR}")
            return 2
        for f in files:
            plan = json.loads(f.read_text(encoding="utf-8"))
            try:
                compiled = compile_plan(plan)
                print(f"=== {f.name} ===")
                _print_table(compiled)
            except CompileError as e:
                print(f"FAIL to compile {f.name}: {e}")
                return 1
        return 0

    if not args.plan_file:
        print("usage: plan_compiler.py <plan.json> | --examples")
        return 2

    path = Path(args.plan_file)
    plan = json.loads(path.read_text(encoding="utf-8"))
    try:
        compiled = compile_plan(plan)
    except CompileError as e:
        print(f"FAIL: {e}")
        return 1
    _print_table(compiled)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
