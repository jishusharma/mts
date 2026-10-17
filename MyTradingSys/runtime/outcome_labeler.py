"""outcome_labeler.py - labels each snapshot with forward outcomes.
Reads runtime_data/snapshots/BTCUSDT_*.json, writes runtime_data/outcome_labels.json.
For each snapshot >120m old with no label: compute return at +30m/+60m/+120m.
Idempotent: skips already-labeled snapshots WITHOUT opening them (their ts/price come from
the label entry), so the cost per cycle follows the unlabeled backlog, not the archive size.
Run hourly or after each session.
"""
import bisect, json, sys, os, time, shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.dont_write_bytecode = True
R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
SNAPS = R / "runtime_data" / "snapshots"
LABELS = R / "runtime_data" / "outcome_labels.json"
HORIZONS_MIN = [30, 60, 120]
SLOW_WARN_S = 20.0  # start-trading-day.ps1 kills this script at 30 s; say so before that happens

def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_snapshots(done=frozenset()):
    """Open only snapshot files whose name is not in `done` (already labeled)."""
    snaps = []
    for f in SNAPS.glob("BTCUSDT_*.json"):
        if f.name in done:
            continue
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
            data = json.load(f)
        if not isinstance(data.get("labels"), list):
            raise ValueError("no labels list")
        return data
    except Exception as e:
        # fail closed: keep the unreadable file for inspection before it is rebuilt
        print(f"labels unreadable ({e}); kept as .corrupt, rebuilding")
        try:
            shutil.copyfile(LABELS, LABELS.with_suffix(".json.corrupt"))
        except Exception as e2:
            print(f"could not back up labels: {e2}")
        return {"version": "1.0.0", "labels": []}

def write_labels(data):
    tmp = LABELS.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, LABELS)

def main():
    t0 = time.monotonic()
    labels = load_labels()
    done = {l["file"] for l in labels["labels"] if isinstance(l, dict) and "file" in l}
    snaps = load_snapshots(done)  # unlabeled only: labeled files are never reopened
    if not snaps:
        print("no unlabeled snapshots")
        return
    # forward references: unlabeled snapshots plus already-labeled ones (ts/price kept in the label entry)
    refs = [(s["ts"], s["price"]) for s in snaps]
    for l in labels["labels"]:
        try:
            refs.append((parse_ts(l["ts"]), float(l["price"])))
        except Exception:
            pass
    refs.sort(key=lambda x: x[0])
    ref_ts = [r[0] for r in refs]
    now = datetime.now(timezone.utc)
    added = 0
    for s in snaps:
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
            j = bisect.bisect_left(ref_ts, target_ts)  # first snapshot >= target_ts
            if j < len(refs):
                entry["fwd_return_pct"][f"{h}m"] = round((refs[j][1] - s["price"]) / s["price"] * 100.0, 4)
            else:
                entry["fwd_return_pct"][f"{h}m"] = None
        if all(v is not None for v in entry["fwd_return_pct"].values()):
            labels["labels"].append(entry)
            added += 1
    write_labels(labels)
    elapsed = time.monotonic() - t0
    print(f"labeled {added} new, total {len(labels['labels'])}, elapsed {elapsed:.2f}s")
    if elapsed > SLOW_WARN_S:
        print(f"SLOW: outcome_labeler took {elapsed:.1f}s (>{SLOW_WARN_S:.0f}s warn, 30s kill in start-trading-day.ps1)")
        sys.exit(3)

if __name__ == "__main__":
    main()
