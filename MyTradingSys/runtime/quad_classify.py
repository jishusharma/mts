"""quad_classify.py - Price x CVD x OI quadrant classifier.
Reads latest snapshot + nearest ~1h-ago snapshot from runtime_data/snapshots/.
Prints one line: CLASS | price_1h_pct | cvd_delta_1h | oi_change_1h_pct | delta_15m | delta_aligned

Classifications:
  new_longs       price up + cvd up + oi up     (real buyers entering)
  short_cover     price up + cvd up + oi down   (squeeze, no new money)
  distribution    price up + cvd down + oi up   (sellers absorbing rally)
  weak_rally      price up + cvd down + oi down (drift, fade)
  new_shorts      price down + cvd down + oi up (real sellers entering)
  long_liquidation price down + cvd down + oi down (capitulation)
  accumulation    price down + cvd up + oi up   (buyers absorbing)
  weak_sell       price down + cvd up + oi down (drift lower, bounce pending)
  flat            no direction
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[2]
SNAPS = R / "runtime_data" / "snapshots"

def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_all():
    out = []
    for f in SNAPS.glob("BTCUSDT_*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh: d = json.load(fh)
            out.append((parse_ts(d["timestamp_utc"]), d))
        except Exception:
            pass
    out.sort(key=lambda x: x[0])
    return out

def classify(cur, past):
    if past is None:
        return None
    try:
        p_cur = float(cur["current_price"])
        p_past = float(past["current_price"])
        cvd_d1h = float(cur.get("cvd", {}).get("cvd_recent", {}).get("delta_1h", 0.0))
        oi_chg = float(cur.get("open_interest", {}).get("change_1h_pct", 0.0))
        nd15 = float(cur.get("trade_flow", {}).get("net_delta_15m", 0.0))
    except Exception:
        return None

    # thresholds
    PRICE_EPS = 0.05   # % move to count as up/down
    CVD_EPS = 1.0      # absolute delta_1h threshold
    OI_EPS = 0.02      # % change threshold

    price_pct = (p_cur - p_past) / p_past * 100.0
    if abs(price_pct) < PRICE_EPS:
        return {"cls": "flat", "price_pct": round(price_pct, 3), "cvd_d1h": cvd_d1h,
                "oi_chg": oi_chg, "nd15": nd15, "delta_aligned": True}

    pdir = "up" if price_pct > 0 else "down"
    cdir = "up" if cvd_d1h > CVD_EPS else ("down" if cvd_d1h < -CVD_EPS else "flat")
    odir = "up" if oi_chg > OI_EPS else ("down" if oi_chg < -OI_EPS else "flat")

    table = {
        ("up","up","up"): "new_longs",
        ("up","up","down"): "short_cover",
        ("up","down","up"): "distribution",
        ("up","down","down"): "weak_rally",
        ("down","down","up"): "new_shorts",
        ("down","down","down"): "long_liquidation",
        ("down","up","up"): "accumulation",
        ("down","up","down"): "weak_sell",
    }
    cls = table.get((pdir, cdir, odir), "flat")

    # delta confirmation: for long-bias cls, nd15 should be positive
    long_bias = {"new_longs","short_cover","accumulation","weak_sell"}
    short_bias = {"new_shorts","long_liquidation","distribution","weak_rally"}
    if cls in long_bias:
        delta_aligned = nd15 > 0
    elif cls in short_bias:
        delta_aligned = nd15 < 0
    else:
        delta_aligned = True

    return {"cls": cls, "price_pct": round(price_pct, 3), "cvd_d1h": cvd_d1h,
            "oi_chg": oi_chg, "nd15": nd15, "delta_aligned": delta_aligned}

def nearest_1h_ago(snaps):
    if not snaps: return None
    now = snaps[-1][0]
    target = now.timestamp() - 3600
    best = None
    best_dist = 1e9
    for ts, d in snaps[:-1]:
        dist = abs(ts.timestamp() - target)
        if dist < best_dist:
            best_dist = dist
            best = d
    return best

def main():
    snaps = load_all()
    if len(snaps) < 2:
        print("QUAD: insufficient_data")
        return
    cur_ts, cur = snaps[-1]
    past = nearest_1h_ago(snaps)
    r = classify(cur, past)
    if r is None:
        print("QUAD: error")
        return
    flag = "" if r["delta_aligned"] else " delta_conflict"
    print(f"QUAD: {r['cls']} (1h price {r['price_pct']:+.2f}% | cvd {r['cvd_d1h']:+.0f} | oi {r['oi_chg']:+.3f}% | nd15 {r['nd15']:+.1f}){flag}")

if __name__ == "__main__":
    main()
