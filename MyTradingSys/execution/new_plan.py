"""
MyTradingSys/execution/new_plan.py

Builds a trade plan by asking a few plain questions, validates it, and saves it
to execution/plans/<plan_id>.json. Sends nothing to any exchange.

Interactive (asks for anything not given on the command line):
    python MyTradingSys/execution/new_plan.py

Scripted (no questions):
    python MyTradingSys/execution/new_plan.py --side long --entry market --size 100 \
        --stop 2 --targets 2,5 --max-loss 50 --hours 2

Only fixed-percent stops are offered: executor refuses trailing and breakeven
stops pre-flight, so a plan using them could never be traded.
R2 runner exit (plan field, stop stays fixed_percent): --targets 50@2,50@5 --breakeven-after-first-target
splits the size over two targets and lets position_manager move the stop to the entry once target 1 fills.
"""
import sys
sys.dont_write_bytecode = True

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from trade_plan_validator import validate, MAX_NOTIONAL_CEILING, MAX_LOSS_FLOOR
from plan_compiler import compile_plan, CompileError

HERE = Path(__file__).resolve().parent
PLANS_DIR = HERE / "plans"
JOURNAL_DIR = HERE / "journal"
INSTRUMENT = "BTC-PERPETUAL"
ACCOUNT = "testnet"


def ask(prompt, default=None, cast=str, choices=None):
    """Ask until the answer casts cleanly (and is one of choices, if given)."""
    hint = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"  {prompt}{hint}: ").strip()
        if not raw and default is not None:
            raw = str(default)
        try:
            val = cast(raw)
        except ValueError:
            print("    not understood, try again")
            continue
        if choices and val not in choices:
            print(f"    choose one of: {', '.join(choices)}")
            continue
        return val


def parse_targets(text):
    """'2,5' -> equal split at +2% and +5%.  '30@2,70@5' -> 30% of size at +2%, 70% at +5%.  '' -> none."""
    text = text.strip()
    if not text or text.lower() == "none":
        return []
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if all("@" in p for p in parts):
        return [{"amount_percent": float(a), "pnl_target_percent": float(b)}
                for a, b in (p.split("@") for p in parts)]
    if any("@" in p for p in parts):
        raise ValueError("mix of '@' and plain targets")
    share = round(100 / len(parts), 4)
    return [{"amount_percent": share, "pnl_target_percent": float(p)} for p in parts]


def make_plan_id(side, entry_type, now):
    short = {"market": "mkt", "limit": "lim", "ladder": "lad"}[entry_type]
    base = f"{side[0]}-{short}-{now:%m%d-%H%M}"
    pid, n = base, 1
    while (PLANS_DIR / f"{pid}.json").exists() or (JOURNAL_DIR / f"{pid}.jsonl").exists():
        n += 1
        pid = f"{base}-{n}"
    return pid


def build(a, now):
    side = a.side.upper()
    entry = {"type": a.entry}
    if a.entry == "limit":
        entry["price"] = a.price
        total = a.size
    elif a.entry == "ladder":
        mults = [1] * a.rungs
        entry.update({"range": {"low": a.low, "high": a.high}, "rungs": a.rungs, "size_multipliers": mults})
        total = a.size * a.rungs
    else:
        total = a.size
    targets = parse_targets(a.targets)
    orders = 1 + (a.rungs if a.entry == "ladder" else 1) + len(targets)
    plan = {
        "plan_id": make_plan_id(side, a.entry, now),
        "account": ACCOUNT,
        "instrument": INSTRUMENT,
        "side": side,
        "validity": {"start": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "end": (now + timedelta(hours=a.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "entry": entry,
        "base_unit": a.size,
        "stop": {"type": "fixed_percent", "percent_below_entry": a.stop},
        "targets": targets,
        "caps": {"max_notional_usd": total, "max_loss_usd": -abs(a.max_loss), "max_concurrent_orders": orders},
    }
    if getattr(a, "max_hold_minutes", None):
        plan["max_hold_minutes"] = a.max_hold_minutes
    if getattr(a, "breakeven_after_first_target", False):
        plan["breakeven_after_first_target"] = True
    return plan


def fill_missing(a):
    """Ask for every value not supplied on the command line."""
    if None not in (a.side, a.entry, a.size, a.stop, a.targets, a.max_loss, a.hours):
        return
    print("New trade plan (BTC-PERPETUAL, Deribit TESTNET). Enter accepts [default].")
    if a.side is None:
        a.side = ask("Side (long/short)", "long", str.lower, ["long", "short"])
    if a.entry is None:
        a.entry = ask("Entry (market/limit/ladder)", "market", str.lower, ["market", "limit", "ladder"])
    if a.entry == "limit" and a.price is None:
        a.price = ask("Limit price (USD)", cast=float)
    if a.entry == "ladder":
        if a.low is None:
            a.low = ask("Ladder low price", cast=float)
        if a.high is None:
            a.high = ask("Ladder high price", cast=float)
        if a.rungs is None:
            a.rungs = ask("Number of rungs", 3, int)
    per = "per rung " if a.entry == "ladder" else ""
    if a.size is None:
        a.size = ask(f"Size {per}in USD (multiples of 10)", 100, int)
    if a.stop is None:
        a.stop = ask("Stop distance from entry, %", 2.0, float)
    if a.targets is None:
        a.targets = ask("Targets, profit % (e.g. 2,5  or  30@2,70@5  or none)", "2,5")
    if a.max_loss is None:
        a.max_loss = ask("Max loss you accept, USD", 50, float)
    if a.hours is None:
        a.hours = ask("Plan valid for how many hours", 2, float)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build and save a trade plan (no exchange contact).")
    ap.add_argument("--side", choices=["long", "short"])
    ap.add_argument("--entry", choices=["market", "limit", "ladder"])
    ap.add_argument("--price", type=float, help="limit price")
    ap.add_argument("--low", type=float, help="ladder low")
    ap.add_argument("--high", type=float, help="ladder high")
    ap.add_argument("--rungs", type=int, help="ladder rungs")
    ap.add_argument("--size", type=int, help="USD size (per rung for a ladder)")
    ap.add_argument("--stop", type=float, help="stop distance from entry, percent")
    ap.add_argument("--targets", help="'2,5' or '30@2,70@5' or 'none'")
    ap.add_argument("--max-loss", type=float, help="USD, positive number")
    ap.add_argument("--hours", type=float, help="validity window from now")
    ap.add_argument("--max-hold-minutes", type=float,
                    help="time exit: close the position this many minutes after the entry fill")
    ap.add_argument("--breakeven-after-first-target", action="store_true",
                    help="R2: position_manager moves the stop to the average entry once the first target is "
                         "completely filled (needs >= 2 targets, so a runner remains)")
    ap.add_argument("--yes", action="store_true", help="save without asking")
    a = ap.parse_args(argv)

    try:
        fill_missing(a)
        plan = build(a, datetime.now(timezone.utc))
    except ValueError as e:
        print(f"REFUSED: {e}")
        return 1

    ok, reason = validate(plan)
    if not ok:
        print(f"REFUSED: {reason}")
        print(f"  limits: total size <= {MAX_NOTIONAL_CEILING} USD, max loss <= {-MAX_LOSS_FLOOR} USD")
        return 1
    try:
        compiled = compile_plan(plan)
    except CompileError as e:
        print(f"REFUSED: {e}")
        return 1
    if compiled["caps_check"].get("within_max_loss") is False:
        print(f"REFUSED: worst-case loss {compiled['worst_case_loss_usd']} USD is more than your max loss "
              f"{plan['caps']['max_loss_usd']} USD. Tighten the stop, cut the size, or raise max loss.")
        return 1

    wc = compiled["worst_case_loss_usd"]
    print()
    print(f"  {plan['side']} {plan['entry']['type']}  size {plan['caps']['max_notional_usd']} USD  "
          f"stop {a.stop}%  targets {a.targets or 'none'}")
    print(f"  worst-case loss: {wc if wc is not None else 'known after fill (market entry)'}  "
          f"(your cap {plan['caps']['max_loss_usd']} USD)")
    print(f"  valid until {plan['validity']['end']}")
    if not a.yes and ask("Save this plan? (y/n)", "y", str.lower, ["y", "n"]) != "y":
        print("not saved")
        return 1

    PLANS_DIR.mkdir(exist_ok=True)
    path = PLANS_DIR / f"{plan['plan_id']}.json"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(plan, f, indent=2)
        f.write("\n")
    print(f"SAVED {plan['plan_id']}  ->  {path.relative_to(HERE.parents[1])}")
    print(f"next:  mts check {plan['plan_id']}    then    mts trade {plan['plan_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
