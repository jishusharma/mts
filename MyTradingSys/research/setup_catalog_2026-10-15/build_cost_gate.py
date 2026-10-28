"""Cost-in-R gate for the setup catalogue (audit E3, operator default D2 YES).

cost_R = round-trip fee / stop_pct. Fees from backtest/fees.py (Binance USDT-M): taker 0.0005 per side, maker 0.0002 per side.
Gate: CLEARS if stop_pct >= 0.40 % (OURS, FABLE_RUNS_AUDIT.md section 4 candidate-order item 3), FAILS below, NOT_STATED if no stop distance.
stop_pct is filled only where the trader states a distance with a quote; the catalogue states none (SETUP_CATALOG.md count paragraph), so none is invented.
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
TAKER, MAKER = 0.0005, 0.0002
GATE_MIN_STOP_PCT = 0.004  # OURS

# id -> stop as a fraction of price (e.g. 0.004). Empty: no trader quote with a distance exists.
STOP_PCT = {}
# id -> timeframe the catalogue names in its row title
TF = {"TOM-1b": "daily", "FAB-6": "30m opening range"}
# id -> SOURCED hit rate / RR (his words; catalogue file:line)
HIT_RR = {
    "TOM-1a": "hit 40-45% needs RR>=1.5; 'about 1:6' (k0zm5NYn0IQ:549-552, 93-96; SETUP_CATALOG.md:319)",
    "TOM-2": "hit 30-40%, RR>3 (BVpY; SETUP_CATALOG.md:434)",
    "TOM-6": "breakout hit 75% typical (hQ8sOq67x5o); RR 1:1-1.5 (uk4P; SETUP_CATALOG.md:167,699)",
}


def cost_r(stop_pct, side_fee):
    return 2 * side_fee / stop_pct


def section0_ids(text):
    sec = text.split("## 0. Summary", 1)[1].split("\n## ", 1)[0]
    return [m.group(1) for m in re.finditer(r"^\| ((?:TOM|FAB)-\d+[ab]?) \|", sec, re.M)]


def gate(stop_pct):
    if stop_pct is None:
        return "NOT_STATED"
    return "CLEARS" if stop_pct >= GATE_MIN_STOP_PCT else "FAILS"


def build(catalog=HERE / "SETUP_CATALOG.md"):
    rows = []
    for i in section0_ids(Path(catalog).read_text(encoding="utf-8")):
        sp = STOP_PCT.get(i)
        rows.append({
            "id": i, "tf": TF.get(i, "NOT STATED"),
            "stop_pct": "" if sp is None else sp,
            "cost_R_taker": "" if sp is None else round(cost_r(sp, TAKER), 4),
            "cost_R_maker": "" if sp is None else round(cost_r(sp, MAKER), 4),
            "sourced_hitrate_RR": HIT_RR.get(i, "NOT STATED"), "gate": gate(sp)})
    return rows


if __name__ == "__main__":
    rows = build()
    cols = ["id", "tf", "stop_pct", "cost_R_taker", "cost_R_maker", "sourced_hitrate_RR", "gate"]
    with open(HERE / "COST_GATE.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for g in ("CLEARS", "FAILS", "NOT_STATED"):
        print(g, sum(r["gate"] == g for r in rows))
