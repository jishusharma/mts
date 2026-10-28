"""G-d orphan sweep core (pure logic): detect a testnet account holding a BTC-PERPETUAL
position or open orders while no live position manager owns it, and append a HALT line.
Strictly read-only towards the exchange: never places, cancels or closes anything; the
operator or kill_switch.py does the sweep. An account whose state cannot be read is
logged in errors but is NOT treated as an orphan (no false HALT on a network blip).
NOT scheduled: run manually on testnet first (see MAINNET_READINESS_CHECKLIST.md).
"""
import sys
sys.dont_write_bytecode = True

from datetime import datetime, timezone
from pathlib import Path
import json


DEFAULT_LABEL = "default"
INSTRUMENT = "BTC-PERPETUAL"


def account_state(client, token, currency="BTC", instrument=INSTRUMENT):
    """Get account state for a specific instrument."""
    positions = client.get_positions(token, currency=currency, kind="future")
    position_sum = 0
    for p in positions:
        if p.get("instrument_name") == instrument:
            size = p.get("size", 0)
            position_sum += abs(float(size) if isinstance(size, (int, float)) else 0)

    orders = client.get_open_orders(token, instrument_name=instrument, type_="all")
    open_orders = len(orders)
    
    return {"position": position_sum, "open_orders": open_orders}


def find_orphans(states, live):
    """Find orphan accounts that are not managed by any live manager."""
    orphans = []
    for account, state in states.items():
        if "error" in state:
            continue
        if account not in live and (state["position"] > 0 or state["open_orders"] > 0):
            orphans.append({"account": account, "position": state["position"], "open_orders": state["open_orders"]})
    
    # Sort by account name
    orphans.sort(key=lambda x: x["account"])
    return orphans


def write_orphan_halt(halt_path, orphans, now):
    """Write halt information to the halt file."""
    parent = Path(halt_path).parent
    parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    for o in orphans:
        lines.append(f"{o['account']}: position={o['position']} open_orders={o['open_orders']} with no live position manager")
    
    content = f"{now.isoformat()} orphan_watchdog: " + "; ".join(lines) + "\n"
    
    with open(halt_path, "a", encoding="utf-8", newline="\n") as f:
        f.write(content)


def run_once(get_client, accounts, live, halt_path, log_path=None, now=None, currency="BTC"):
    """Run the orphan watchdog once."""
    if now is None:
        now = datetime.now(timezone.utc)
    
    states = {}
    errors = {}
    
    for label in accounts:
        try:
            client, token = get_client(label)
            states[label] = account_state(client, token, currency=currency)
        except Exception as e:
            errors[label] = repr(e)
            states[label] = {"error": repr(e)}
    
    orphans = find_orphans(states, live)
    
    # halt_path=None: detect and log only; the caller decides when to halt (orphan_watchdog_cli --confirm-sweeps)
    halted = bool(orphans) and halt_path is not None
    if halted:
        write_orphan_halt(halt_path, orphans, now)
    
    if log_path is not None:
        log_entry = {
            "ts": now.isoformat(),
            "event": ("orphan_halt" if halted else "orphan_seen") if orphans else "ok",
            "orphans": orphans,
            "errors": errors,
            "live": sorted(live)
        }
        parent = Path(log_path).parent
        parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    return {"orphans": orphans, "errors": errors, "halted": halted, "states": states}
