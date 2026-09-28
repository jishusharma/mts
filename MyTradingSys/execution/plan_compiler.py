"""
MyTradingSys/execution/plan_compiler.py

Step 3 of the T050 execution-layer roadmap. Converts a validated trade
plan (trade_plan_validator.py has already returned ok=True) into an
exact order list: entry orders (with tick/size rounding), a stop order,
and target orders. Sends nothing - this is pure computation, no network
calls, so it is fully testable without a Deribit connection or API key.

Rounding rules (BTC-PERPETUAL, inverse, USD-denominated contracts) - see
FORMULAS.md 11.1/11.2 for the full derivation and the Opus-review
rejection of the earlier round-half-to-even version:
  - Price snapped to the nearest 0.5 USD tick, DIRECTIONALLY per order
    purpose + side, never plain round-to-nearest: entry prices snap
    away from the market (never a worse fill than planned), stop prices
    snap toward entry (loss can never exceed budget), target prices
    snap toward entry (more likely to fill at the stated price or better).
  - Size (amount) FLOORED to the nearest $10 contract, never rounded up
    and never forced up to the $10 minimum - a size below the minimum
    means the plan cannot be traded at that risk budget, so
    compile_plan() refuses it (CompileError) rather than silently
    trading a larger size than intended.
These are Deribit's actual BTC-PERPETUAL contract conventions (0.5 USD
tick, 10 USD minimum trade amount / increment) and are NOT configurable
per-plan - they are exchange constants.

Run directly against one plan file and print the compiled table:
    python MyTradingSys/execution/plan_compiler.py path/to/plan.json

Run against the example suite and print every valid plan's compiled table:
    python MyTradingSys/execution/plan_compiler.py --examples
"""
import sys
sys.dont_write_bytecode = True

import json
import argparse
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trade_plan_validator import validate  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"

PRICE_TICK = 0.5
SIZE_INCREMENT = 10


class CompileError(Exception):
    """Raised when a plan cannot be compiled - e.g. it was never validated,
    contains a combination the compiler does not yet handle (trailing
    stops need live price tracking, not a static compile step), or an
    entry/target size floors below the minimum tradeable size (see
    round_size below - moved above snap_price/round_size so they can
    raise it directly)."""


def snap_price(price: float, mode: str) -> float:
    """Snap price to the nearest PRICE_TICK, in the direction given by
    `mode` ('floor' or 'ceil'). The direction is ALWAYS chosen by the
    caller from the order's purpose and side (see FORMULAS.md 11.1) -
    this function never guesses a direction from price alone, and never
    rounds to the nearest tick (round-half-to-even was rejected in Opus
    review: it is a definition borrowed from Python's round() rather than
    from risk direction, and it can snap a stop/target the wrong way).

    Uses Decimal arithmetic (not float + epsilon) so the tick boundary is
    exact regardless of binary-float representation error, e.g.
    Decimal("50000.5")/Decimal("0.5") is exactly Decimal("100001"), with
    no risk of landing on 100000.99999999998 or 100001.00000000002.
    """
    if mode not in ("floor", "ceil"):
        raise ValueError(f"snap_price mode must be 'floor' or 'ceil', got {mode!r}")
    d_price = Decimal(str(price))
    d_tick = Decimal(str(PRICE_TICK))
    rounding = ROUND_FLOOR if mode == "floor" else ROUND_CEILING
    snapped_units = (d_price / d_tick).to_integral_value(rounding=rounding)
    return float(snapped_units * d_tick)


def round_size(amount: float) -> int:
    """Floor to the nearest SIZE_INCREMENT (10 USD) - never rounds up.
    Raises CompileError if the floored size is below SIZE_INCREMENT: the
    old behaviour (`max(SIZE_INCREMENT, floored)`) forced every too-small
    size up to the 10 USD minimum, which can trade MORE size (and take
    MORE risk) than the plan's own risk budget calls for - forcing a
    minimum can exceed the risk budget, so refusing is the safe default.
    """
    d_amount = Decimal(str(amount))
    d_inc = Decimal(str(SIZE_INCREMENT))
    floored_units = (d_amount / d_inc).to_integral_value(rounding=ROUND_FLOOR)
    size = int(floored_units * d_inc)
    if size < SIZE_INCREMENT:
        raise CompileError(
            f"amount {amount} floors to {size}, below the {SIZE_INCREMENT} USD minimum tradeable "
            f"size - refusing rather than forcing it up to {SIZE_INCREMENT} (that would trade more "
            f"size, and take more risk, than the plan's own risk budget calls for)"
        )
    return size


def compile_plan(plan: dict) -> dict:
    ok, reason = validate(plan)
    if not ok:
        raise CompileError(f"refusing to compile an invalid plan: {reason}")

    side = plan["side"]
    entry = plan["entry"]
    base_unit = plan["base_unit"]
    order_side = "BUY" if side == "LONG" else "SELL"
    opposite_side = "SELL" if side == "LONG" else "BUY"

    # Entry snap direction (FORMULAS.md 11.1): never a worse fill than
    # planned - a BUY limit/ladder rung snaps DOWN (floor, cheaper or
    # equal), a SELL snaps UP (ceil, more expensive or equal).
    entry_mode = "floor" if order_side == "BUY" else "ceil"

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
        price = snap_price(entry["price"], entry_mode)
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

        # FORMULAS.md 11.4: inverse-contract average price across fills is
        # the harmonic mean weighted by USD size, sum(size)/sum(size/price)
        # - NOT the notional-weighted arithmetic mean sum(price*size)/sum(size).
        total_inverse_weighted = 0.0
        total_size = 0
        for i, (price, mult) in enumerate(zip(rung_prices, mults), start=1):
            snapped_price = snap_price(price, entry_mode)
            size = round_size(base_unit * mult)
            entry_orders.append({
                "label": f"entry_rung_{i}",
                "side": order_side,
                "order_type": "limit",
                "price": snapped_price,
                "amount": size,
            })
            total_inverse_weighted += size / snapped_price
            total_size += size

        avg_entry_estimate = (total_size / total_inverse_weighted) if total_size else None

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
            # FORMULAS.md 11.1: stop snaps TOWARD entry so the loss can
            # never exceed budget - LONG stop (below entry) snaps UP
            # (ceil), SHORT stop (above entry) snaps DOWN (floor).
            stop_mode = "ceil" if side == "LONG" else "floor"
            stop_price = snap_price(stop_price, stop_mode)
            stop_order = {
                "label": "stop_order",
                "side": opposite_side,
                "order_type": "stop_market",  # B077: executor places stop_market(trigger=mark); price = trigger
                "price": stop_price,
                "amount": total_entry_size,
                "reduce_only": True,
            }
            price_delta = abs(avg_entry_estimate - stop_price)
            # NOTE (FORMULAS.md 11.6): this is the loss AT the stop price
            # only - it excludes stop-market trigger slippage and fees.
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
        # FORMULAS.md 11.1: target snaps TOWARD entry so it is more likely
        # to fill at the stated price or better - LONG target (above
        # entry) snaps DOWN (floor), SHORT target (below entry) snaps UP
        # (ceil).
        target_mode = "floor" if side == "LONG" else "ceil"
        for i, t in enumerate(plan.get("targets", []), start=1):
            target_price = (avg_entry_estimate * (1 + t["pnl_target_percent"] / 100.0) if side == "LONG"
                            else avg_entry_estimate * (1 - t["pnl_target_percent"] / 100.0))
            target_price = snap_price(target_price, target_mode)
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
