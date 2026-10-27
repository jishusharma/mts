import sys
sys.dont_write_bytecode = True
import json, os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP_DIR = ROOT / "runtime_data" / "snapshots"
STATE_CODE = ROOT / "MyTradingSys" / "runtime" / "state_code_regime.json"

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def latest_snapshot():
    files = sorted(SNAP_DIR.glob("BTCUSDT_*.json"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None
def classify(snap):
    up = down = 0
    c = snap.get("conditions", {}) or {}
    vs = c.get("vwap_slope", "flat")
    cs = c.get("cvd_slope", "flat")
    vp = c.get("vp_shape", "B")
    nd = (snap.get("trade_flow") or {}).get("net_delta_1h", 0.0) or 0.0
    if vs == "rising": up += 1
    elif vs == "falling": down += 1
    if cs == "rising": up += 1
    elif cs == "falling": down += 1
    if nd > 0: up += 1
    elif nd < 0: down += 1
    if vp == "P": up += 1
    elif vp == "D": down += 1
    if up >= 3: cand = "TREND_UP"
    elif down >= 3: cand = "TREND_DOWN"
    else: cand = "RANGE"
    return cand, up, down

def confidence_of(published, cand, streak):
    if published == "UNKNOWN": return "LOW"
    if cand != published: return "LOW"
    if streak >= 5: return "HIGH"
    if streak >= 3: return "MEDIUM"
    return "LOW"
def main():
    snap_file = latest_snapshot()
    if snap_file is None:
        print("regime: no snapshot")
        return 1
    with open(snap_file, "r", encoding="utf-8") as f:
        snap = json.load(f)
    cand, up, down = classify(snap)

    state = {}
    if STATE_CODE.exists():
        with open(STATE_CODE, "r", encoding="utf-8-sig") as f:
            state = json.load(f)

    prev = state if isinstance(state, dict) else {}
    published = prev.get("label", "UNKNOWN")
    prev_cand = prev.get("candidate", "UNKNOWN")
    streak = int(prev.get("cycles_in_candidate_state", 0))
    consecutive = int(prev.get("consecutive_cycles", 0))
    entered = prev.get("entered_at_utc")

    if cand == prev_cand:
        streak += 1
    else:
        streak = 1
    if cand == published:
        consecutive += 1
    elif streak >= 3:
        published = cand
        entered = now_utc()
        consecutive = 1
    else:
        consecutive += 1

    conf = confidence_of(published, cand, streak if cand == published else 0)

    state = {
        "label": published,
        "confidence": conf,
        "consecutive_cycles": consecutive,
        "entered_at_utc": entered,
        "candidate": cand,
        "cycles_in_candidate_state": streak,
        "votes_up": up,
        "votes_down": down,
        "last_updated_utc": now_utc(),
    }
    tmp = STATE_CODE.with_suffix(".json.new")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.replace(tmp, STATE_CODE)

    print(f"regime label={published} cand={cand} up={up} down={down} "
          f"streak={streak} conf={conf}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
