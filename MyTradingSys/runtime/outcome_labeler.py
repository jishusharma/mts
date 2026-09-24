"""outcome_labeler.py - labels each snapshot with forward outcomes.
Reads runtime_data/snapshots/BTCUSDT_*.json, writes runtime_data/outcome_labels.json.
For each snapshot >120m old with no label: compute return at +30m/+60m/+120m.
Idempotent: skips already-labeled snapshots. Run hourly or after each session.
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.dont_write_bytecode = True
R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
SNAPS = R / "runtime_data" / "snapshots"
LABELS = R / "runtime_data" / "outcome_labels.json"
HORIZONS_MIN = [30, 60, 120]

def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_snapshots():
    snaps = []
    for f in SNAPS.glob("BTCUSDT_*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            ts = parse_ts(d["timestamp_utc"])
            price = float(d["current_price"])
            cond = d.get("conditions", {})
            vp_shape = cond.get("vp_shape", "?")
            price_vs_va = cond.get("price_vs_va", "?")
            cvd_slope = cond.get("cvd_slope", "?")
            snaps.append({
                "file": f.name, "ts": ts, "price": price,
                "vp_shape": vp_shape, "price_vs_va": price_vs_va,
                "cvd_slope": cvd_slope,
                "raw": d
            })
        except Exception as e:
            print(f"skip {f.name}: {e}")
    snaps.sort(key=lambda x: x["ts"])
    return snaps

def load_labels():
    if not LABELS.exists():
        return {"version": "1.0.0", "labels": []}
    try:
        with open(LABELS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": "1.0.0", "labels": []}

def write_labels(data):
    tmp = LABELS.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, LABELS)

def main():
    snaps = load_snapshots()
    if not snaps:
        print("no snapshots")
        return
    labels = load_labels()
    done = {l["file"] for l in labels["labels"]}
    now = datetime.now(timezone.utc)
    added = 0
    for i, s in enumerate(snaps):
        if s["file"] in done:
            continue
        age_min = (now - s["ts"]).total_seconds() / 60
        if age_min < max(HORIZONS_MIN):
            continue  # too recent
        entry = {
            "file": s["file"], "ts": s["ts"].isoformat(),
            "price": s["price"],
            "vp_shape": s["vp_shape"],
            "price_vs_va": s["price_vs_va"],
            "cvd_slope": s["cvd_slope"],
            "fwd_return_pct": {}
        }
        for h in HORIZONS_MIN:
            target_ts = s["ts"] + timedelta(minutes=h)
            # find first snapshot >= target_ts
            fwd = next((x for x in snaps[i+1:] if x["ts"] >= target_ts), None)
            if fwd:
                entry["fwd_return_pct"][f"{h}m"] = round((fwd["price"] - s["price"]) / s["price"] * 100.0, 4)
            else:
                entry["fwd_return_pct"][f"{h}m"] = None
        if all(v is not None for v in entry["fwd_return_pct"].values()):
            labels["labels"].append(entry)
            added += 1
    write_labels(labels)
    print(f"labeled {added} new, total {len(labels['labels'])}")

if __name__ == "__main__":
    main()
