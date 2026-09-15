import sys, json
sys.path.insert(0, r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\mts\runtime")
from math_object_builder import build_math_object
with open(sys.argv[1], "r", encoding="utf-8") as f:
    snap = json.load(f)
mo = build_math_object(snap)
with open(sys.argv[2], "w", encoding="utf-8") as f:
    json.dump(mo, f)
print("OK")
