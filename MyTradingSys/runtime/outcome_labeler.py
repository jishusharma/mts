"""outcome_labeler.py - labels each snapshot with forward outcomes.
Reads runtime_data/snapshots/BTCUSDT_*.json, writes runtime_data/outcome_labels.json.
For each snapshot >120m old with no label: compute return at +30m/+60m/+120m.
Idempotent: skips already-labeled snapshots WITHOUT opening them (their ts/price come from
the label entry), so the cost per cycle follows the unlabeled backlog, not the archive size.
Bounded cycles: one cycle opens at most MAX_OPEN_PER_CYCLE unlabeled files (oldest first by name, which carries
the epoch-ms time) plus the +120 min lookahead window, and stops opening after OPEN_BUDGET_S. A cold or corrupt-labels
backlog therefore drains over several cycles, each of which writes its labels atomically, instead of being killed
at 30 s with nothing written. A snapshot whose forward reference lies beyond the opened window stays unlabeled.
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
MAX_OPEN_PER_CYCLE = 1500   # OURS: ~5-16 ms per file measured, keeps a cold cycle near 8-24 s worst case
OPEN_BUDGET_S = 12.0        # OURS: wall-clock cap on the opening phase; the 30 s kill stays
SLOW_WARN_S = 20.0  # start-trading-day.ps1 kills this script at 30 s; say so before that happens

def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def load_snapshots(done=frozenset()):
    """Open only snapshot files whose name is not in `done` (already labeled), oldest name first, within the
    per-cycle budget. Returns (snaps sorted by ts, truncated). `truncated` means unopened unlabeled files remain
    (their ts is assumed >= the last opened one: names are BTCUSDT_<date>_<epoch ms>)."""
    snaps = []
    names = sorted(f for f in SNAPS.glob("BTCUSDT_*.json") if f.name not in done)
    t_open = time.monotonic()
    opened = 0
    max_ts = None
    stop_after = None  # set once the count budget is spent: keep opening until the +120 min window is covered
    truncated = False
    for f in names:
        if opened and time.monotonic() - t_open >= OPEN_BUDGET_S:  # always open one file: a cycle never idles; >= so a 0 budget stops even on a coarse clock (Windows ~15 ms ticks)
            truncated = True
            break
        if opened >= MAX_OPEN_PER_CYCLE and max_ts is None:
            truncated = True  # budget spent on unreadable files only: nothing to anchor a lookahead window on
            break
        if opened >= MAX_OPEN_PER_CYCLE:
            if stop_after is None:
                stop_after = max_ts + timedelta(minutes=max(HORIZONS_MIN))
            if max_ts > stop_after:
                truncated = True
                break
        opened += 1
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            ts = parse_ts(d["timestamp_utc"])
            price = float(d["current_price"])
            cond = d.get("conditions", {})
            vp_shape = cond.get("vp_shape", "?")
            price_vs_va = cond.get("price_vs_va", "?")
            cvd_slope = cond.get("cvd_slope", "?")
            if max_ts is None or ts > max_ts:
                max_ts = ts
            snaps.append({
                "file": f.name, "ts": ts, "price": price,
                "vp_shape": vp_shape, "price_vs_va": price_vs_va,
                "cvd_slope": cvd_slope,
                "raw": d
            })
        except Exception as e:
            print(f"skip {f.name}: {e}")
    snaps.sort(key=lambda x: x["ts"])
    return snaps, truncated

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
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            shutil.copyfile(LABELS, LABELS.with_suffix(f".json.corrupt.{stamp}"))
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
    # an entry counts as done only if its file, ts AND price parse; otherwise the snapshot is reopened (old behaviour)
    done = set()
    labeled_names = {l["file"] for l in labels["labels"] if isinstance(l, dict) and "file" in l}
    label_refs = []
    for l in labels["labels"]:
        try:
            label_refs.append((parse_ts(l["ts"]), l["file"], float(l["price"])))
            done.add(l["file"])
        except Exception:
            pass
    snaps, truncated = load_snapshots(done)  # unlabeled only: labeled files are never reopened
    if not snaps:
        if truncated:
            print("WARN backlog truncated by budget and no readable snapshot opened: no progress")
            sys.exit(4)  # visible in the launcher log; the next cycle retries from the same files
        print("no unlabeled snapshots")
        return
    # truncated: unopened files may sit between a snapshot and its forward reference, so only references strictly
    # older than the newest opened snapshot are trusted; anything later stays unlabeled for the next cycle
    ref_limit = max(s["ts"] for s in snaps) if truncated else None
    # forward references: unlabeled snapshots plus already-labeled ones; (ts, filename) order is deterministic
    refs = [(s["ts"], s["file"], s["price"]) for s in snaps] + label_refs
    refs.sort(key=lambda x: (x[0], x[1]))
    ref_ts = [r[0] for r in refs]
    now = datetime.now(timezone.utc)
    added = 0
    for s in snaps:
        if s["file"] in labeled_names:
            continue  # labeled (entry unusable as a reference, so it was reopened): used as a reference only
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
            if j < len(refs) and (ref_limit is None or refs[j][0] < ref_limit):
                entry["fwd_return_pct"][f"{h}m"] = round((refs[j][2] - s["price"]) / s["price"] * 100.0, 4)
            else:
                entry["fwd_return_pct"][f"{h}m"] = None
        if all(v is not None for v in entry["fwd_return_pct"].values()):
            labels["labels"].append(entry)
            added += 1
    write_labels(labels)
    elapsed = time.monotonic() - t0
    print(f"labeled {added} new, total {len(labels['labels'])}, elapsed {elapsed:.2f}s"
          + (" (backlog truncated by budget; more next cycle)" if truncated else "")
          + (" WARN no progress" if truncated and not added else ""))
    if truncated and not added:
        sys.exit(4)
    if elapsed > SLOW_WARN_S:
        print(f"SLOW: outcome_labeler took {elapsed:.1f}s (>{SLOW_WARN_S:.0f}s warn, 30s kill in start-trading-day.ps1)")
        sys.exit(3)

if __name__ == "__main__":
    main()
