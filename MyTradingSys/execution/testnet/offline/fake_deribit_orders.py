"""Fake Deribit for offline G1/G2 logic tests. Position is the truth."""
class DeribitError(Exception):
    def __init__(self, m, e): super().__init__(m); self.error = e
S = {}
def reset():
    S.clear(); S.update(pos=0, orders={}, n=0)
def _new(side, amount, typ, label, reduce_only, trigger=None, price=None, state="open"):
    S["n"] += 1; oid = f"O{S['n']}"
    S["orders"][oid] = dict(order_id=oid, direction=side.lower(), amount=amount, order_type=typ, label=label,
                           reduce_only=reduce_only, trigger_price=trigger, price=price,
                           order_state=("untriggered" if typ == "stop_market" else state), filled_amount=0, average_price=0)
    return oid
def authenticate(): return "tok"
def active_env(): return "test"
MAINNET_MAX_NOTIONAL_USD = 50
def stop_market(t, i, side, amount, trig, label, trigger="mark_price"):
    return {"order": S["orders"][_new(side, amount, "stop_market", label, True, trig)]}
def edit(t, oid, amount=None, price=None, trigger_price=None):
    o = S["orders"][oid]
    if o["order_state"] not in ("open", "untriggered"): raise DeribitError("edit", {"code": 11044, "message": "not_open_order"})
    if amount is not None: o["amount"] = amount
    return {"order": o}
def cancel(t, oid):
    o = S["orders"][oid]
    if o["order_state"] not in ("open", "untriggered"): raise DeribitError("cancel", {"code": 11044})
    o["order_state"] = "cancelled"; return o
def close_position(t, i):
    amt = abs(S["pos"]); S["pos"] = 0; oid = _new("sell", amt, "market", "x", True, state="filled")
    S["orders"][oid]["filled_amount"] = amt; return {"order": S["orders"][oid]}
def get_position(t, i="BTC-PERPETUAL"): return {"size": S["pos"]}
def get_order_state(t, oid): return dict(S["orders"][oid])
def get_open_orders(t, i="BTC-PERPETUAL", type_="all"):
    return [dict(o) for o in S["orders"].values() if o["order_state"] in ("open", "untriggered")]
# test helpers
def fill(oid, amt):
    o = S["orders"][oid]; o["filled_amount"] += amt; o["average_price"] = 80000
    S["pos"] += amt if o["direction"] == "buy" else -amt
    if o["filled_amount"] >= o["amount"]: o["order_state"] = "filled"
def trigger_stop(oid):
    o = S["orders"][oid]; amt = min(o["amount"], abs(S["pos"]))  # reduce-only clamp ASSUMED here
    o["order_state"] = "filled"; o["filled_amount"] = amt; S["pos"] -= amt if S["pos"] > 0 else -amt
