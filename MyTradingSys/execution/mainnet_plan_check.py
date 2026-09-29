"""Pure logic, no I/O, no exchange call; executor.preflight calls it with do.active_env() and do.MAINNET_MAX_NOTIONAL_USD."""
import sys
sys.dont_write_bytecode = True

def plan_refusals(compiled, plan, env, cap_usd) -> list:
    """Check if a compiled trade plan should be refused on mainnet.
    
    Args:
        compiled: The compiled trade plan
        plan: The original plan (None for pre-compiled)
        env: Environment name ("test" or others)
        cap_usd: Mainnet cap in USD
        
    Returns:
        List of refusal reasons, empty if plan is acceptable
    """
    # Testnet is unchanged
    if env == "test":
        return []
    
    # All other environments are treated as mainnet
    reasons = []
    
    # If plan is None, it's pre-compiled and refused
    if plan is None:
        reasons.append("mainnet refuses a pre-compiled plan file - pass the raw plan so it is re-compiled and re-checked")
        return reasons
    
    # Check entry orders
    entries = compiled.get("entry_orders")
    if not isinstance(entries, list) or len(entries) == 0:
        reasons.append("mainnet plan has no entry orders")
        return reasons
    
    # Validate each entry amount
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            reasons.append(f"entry {i} has a bad amount {entry!r}")
            return reasons
            
        amount = entry.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            reasons.append(f"entry {i} has a bad amount {amount!r}")
            return reasons
            
        if amount <= 0:
            reasons.append(f"entry {i} has a bad amount {amount!r}")
            return reasons
    
    # Check max_position_size
    mps = compiled.get("max_position_size")
    if not isinstance(mps, (int, float)) or isinstance(mps, bool):
        reasons.append("mainnet plan has no numeric max_position_size")
        return reasons
    
    # Calculate total entry amount
    total = sum(entry["amount"] for entry in entries)
    
    # Check if total matches max_position_size
    if abs(total - mps) > 1e-9:
        reasons.append(f"sum of entry amounts {total:g} != max_position_size {mps:g}")
    
    # Check if total exceeds cap
    if total > cap_usd:
        reasons.append(f"sum of entry amounts {total:g} > mainnet cap {cap_usd:g}")
        
    # Check if max_position_size exceeds cap
    if mps > cap_usd:
        reasons.append(f"max_position_size {mps:g} > mainnet cap {cap_usd:g}")
    
    return reasons
