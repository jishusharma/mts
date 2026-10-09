import sys, json, glob, os

sys.path.insert(0, r".\MyTradingSys\runtime")
from math_object_builder import build_math_object

files = sorted(glob.glob(r".\runtime_data\snapshots\BTCUSDT_*.json"), key=os.path.getmtime)
path = files[-1]
print("FILE:", path)
print()

with open(path, encoding="utf-8") as f:
    snapshot = json.load(f)

m1 = build_math_object(snapshot)
m2 = build_math_object(snapshot)
assert m1 == m2, "NON-DETERMINISTIC"

print("current_price:", m1["current_price"])
print("speed_picking_up (builder):", m1["speed_picking_up"])
print("speed_picking_up (raw conditions):", snapshot.get("conditions", {}).get("speed_picking_up"))
print("zones:", len(m1["zones"]))
print("confluence clusters:", len(m1["confluence"]))
print("hard_stops_compiled:", m1["hard_stops_compiled"])

if "setup_candidate" in m1:
    sc = m1["setup_candidate"]
    print("setup_candidate:", sc["setup_type"], "@", sc["zone"]["name"], sc["zone"]["price"], "(raw=" + str(sc["score"]["raw"]) + ")")
    print("  net_rr:", sc["math"]["net_rr"], "| hard_stop_4 (net_rr below floor):", m1["hard_stops_compiled"]["top_candidate_rr_below_threshold"])
    print("  candidate speed proof:", sc.get("proof", {}).get("speed", {}).get("picking_up"))
else:
    print("setup_candidate: NOT PRESENT (legacy fallback path)")

print()
print("proof_direction_status:", m1.get("proof_direction_status", "(NOT PRESENT — BUG-008 not firing)"))
print("proof_direction_details:", m1.get("proof_direction_details", "(none)"))

print()
print("DETERMINISM: PASS")
