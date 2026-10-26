import sys
sys.dont_write_bytecode = True

import json
import statistics
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
SNAPS = ROOT / "runtime_data" / "snapshots"
LABELS = ROOT / "runtime_data" / "outcome_labels.json"
OUT = ROOT / "MyTradingSys" / "research" / "_archive" / "loose_2026-10" / "OI_EVENT_STUDY_2026-10-10.md"

HORIZONS = ["30m", "60m", "120m"]
PRICE_THRESH = 0.30
OI_THRESH = 0.0
DEDUP_MIN = 60


def load_labels():
    with open(LABELS, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {r["file"]: r for r in d["labels"]}


def ts_ms(name):
    base = name.replace("BTCUSDT_", "").replace(".json", "")
    return int(base.split("_")[-1])


def main():
    labels = load_labels()
    files = sorted(SNAPS.glob("BTCUSDT_*.json"))
    ms_list = []
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                j = json.load(f)
            ms_list.append((ts_ms(p.name), p.name, j))
        except Exception:
            continue
    ms_list.sort(key=lambda t: t[0])
    by_ms = {ms: j for ms, _, j in ms_list}
    times = sorted(by_ms.keys())
    print("snapshots={0} labels={1}".format(len(ms_list), len(labels)))

    events = []
    base_pool = {"30m": [], "60m": [], "120m": []}
    skip = 0
    for ms, name, j in ms_list:
        lab = labels.get(name)
        if lab is None:
            skip += 1
            continue
        target = ms - 60 * 60 * 1000
        lo, hi, best = 0, len(times) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            if times[mid] <= target:
                best = times[mid]; lo = mid + 1
            else:
                hi = mid - 1
        if best is None:
            skip += 1
            continue
        p_now = j.get("current_price")
        p_ago = by_ms[best].get("current_price")
        oi_pct = (j.get("open_interest") or {}).get("change_1h_pct")
        if p_now is None or p_ago is None or oi_pct is None:
            skip += 1
            continue
        price_pct = (p_now - p_ago) / p_ago * 100.0
        oi_pct = float(oi_pct)
        fwd = lab.get("fwd_return_pct") or {}
        for hz in HORIZONS:
            v = fwd.get(hz)
            if v is not None:
                base_pool[hz].append(v)
        ev = None
        if price_pct > PRICE_THRESH and oi_pct < OI_THRESH:
            ev = "bearish_div"
        elif price_pct < -PRICE_THRESH and oi_pct > OI_THRESH:
            ev = "bullish_div"
        if ev:
            events.append({"ms": ms, "name": name, "ts": lab.get("ts",""), "type": ev, "price_pct": price_pct, "oi_pct": oi_pct, "fwd": fwd})
    print("events_raw={0} skip={1}".format(len(events), skip))

    baseline = {}
    for hz in HORIZONS:
        v = base_pool[hz]
        baseline[hz] = statistics.mean(v) if v else 0.0
    print("baseline mean: " + ", ".join("{0}={1:+.4f}".format(h, baseline[h]) for h in HORIZONS))

    events.sort(key=lambda e: e["ms"])
    kept = []
    last = {}
    for e in events:
        t = e["type"]
        if t in last and e["ms"] - last[t] < DEDUP_MIN * 60 * 1000:
            continue
        kept.append(e)
        last[t] = e["ms"]
    print("events_dedup={0}".format(len(kept)))

    by_type = defaultdict(list)
    for e in kept:
        by_type[e["type"]].append(e)

    out = []
    out.append("# OI Divergence Event Study - 2026-10-10")
    out.append("")
    out.append("Method: event study. Single asset (BTCUSDT).")
    out.append("Event bearish_div: 1h price change > +0.30% AND OI 1h change < 0.")
    out.append("Event bullish_div: 1h price change < -0.30% AND OI 1h change > 0.")
    out.append("Forward return measured at 30m, 60m, 120m from the label file.")
    out.append("Abnormal return = raw forward return minus the unconditional mean at the same horizon.")
    out.append("Dedup: at least 60 minutes between events of the same type.")
    out.append("")
    out.append("Baseline unconditional means: " + ", ".join("{0}={1:+.4f}".format(h, baseline[h]) for h in HORIZONS))
    out.append("")
    for t in ["bearish_div", "bullish_div"]:
        evs = by_type[t]
        out.append("## {0} (n={1})".format(t, len(evs)))
        out.append("")
        out.append("| horizon | n | days | raw mean | abn mean | sd | se(day) | t |")
        out.append("|---|---|---|---|---|---|---|---|")
        for hz in HORIZONS:
            vals = []
            days = defaultdict(list)
            for e in evs:
                v = e["fwd"].get(hz)
                if v is None: continue
                vals.append(v - baseline[hz])
                days[e["ts"][:10]].append(v - baseline[hz])
            if not vals:
                out.append("| {0} | 0 | 0 | 0 | 0 | 0 | 0 | 0 |".format(hz)); continue
            n = len(vals)
            raw = statistics.mean([e["fwd"].get(hz) for e in evs if e["fwd"].get(hz) is not None])
            m = statistics.mean(vals)
            sd = statistics.pstdev(vals) if n > 1 else 0.0
            dm = [statistics.mean(v) for v in days.values() if v]
            se = (statistics.pstdev(dm) / (len(dm) ** 0.5)) if len(dm) > 1 else 0.0
            tstat = m / se if se > 0 else 0.0
            out.append("| {0} | {1} | {2} | {3:+.4f} | {4:+.4f} | {5:.4f} | {6:.4f} | {7:+.2f} |".format(hz, n, len(dm), raw, m, sd, se, tstat))
        out.append("")
    out.append("## Caveats")
    out.append("")
    out.append("- Snapshot window 2026-09-12 to 2026-10-10. ~28 days.")
    out.append("- OI signal is the snapshot change_1h_pct, quantized to 0.01.")
    out.append("- Baseline is unconditional mean forward return over the same window.")
    out.append("- Day-clustered se. t is abn mean / se.")
    out.append("- Predecessor: OI_DIVERGENCE_2026-10-10.md (state table, no edge).")
    out.append("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote " + str(OUT))


if __name__ == "__main__":
    main()