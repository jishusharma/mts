import sys
sys.dont_write_bytecode = True

import json
import statistics
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
SNAPS = ROOT / "runtime_data" / "snapshots"
LABELS = ROOT / "runtime_data" / "outcome_labels.json"
OUT = ROOT / "MyTradingSys" / "research" / "OI_DELTA_4STATE_BACKTEST_2026-09-21.md"

HORIZONS = ["30m", "60m", "120m"]
PRICE_LAG_MIN = 60
STATES = ["aggressive_long", "aggressive_short", "rekt_long", "rekt_short", "neutral"]


def load_labels():
    with open(LABELS, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {r["file"]: r for r in d["labels"]}


def ts_ms(name):
    base = name.replace("BTCUSDT_", "").replace(".json", "")
    return int(base.split("_")[-1])


def classify(oi_dir, delta):
    if oi_dir == "rising" and delta > 0: return "aggressive_long"
    if oi_dir == "rising" and delta < 0: return "aggressive_short"
    if oi_dir == "falling" and delta < 0: return "rekt_long"
    if oi_dir == "falling" and delta > 0: return "rekt_short"
    return "neutral"


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

    rows = []
    skip_label = 0
    skip_lag = 0
    for ms, name, j in ms_list:
        lab = labels.get(name)
        if lab is None:
            skip_label += 1
            continue
        oi_dir = (j.get("open_interest") or {}).get("direction", "flat")
        nd1h = (j.get("trade_flow") or {}).get("net_delta_1h", 0.0)
        target = ms - PRICE_LAG_MIN * 60 * 1000
        lo, hi, best = 0, len(times) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            if times[mid] <= target:
                best = times[mid]
                lo = mid + 1
            else:
                hi = mid - 1
        if best is None:
            skip_lag += 1
            continue
        ago = by_ms[best].get("current_price")
        now = j.get("current_price")
        if ago is None or now is None:
            skip_lag += 1
            continue
        rows.append({
            "file": name,
            "ts": lab.get("ts", ""),
            "vs_state": classify(oi_dir, nd1h),
            "ps_state": classify(oi_dir, now - ago),
            "fwd": lab.get("fwd_return_pct") or {},
        })
    print("rows={0} skip_label={1} skip_lag={2}".format(len(rows), skip_label, skip_lag))

    def agg(key, val, horizon):
        vals = []
        days = defaultdict(list)
        for r in rows:
            if r[key] != val: continue
            h = r["fwd"].get(horizon)
            if h is None: continue
            vals.append(h)
            days[r["ts"][:10]].append(h)
        if not vals:
            return (0, 0, 0.0, 0.0, 0.0)
        n = len(vals)
        mean = statistics.mean(vals)
        sd = statistics.pstdev(vals) if n > 1 else 0.0
        dm = [statistics.mean(v) for v in days.values() if v]
        se = (statistics.pstdev(dm) / (len(dm) ** 0.5)) if len(dm) > 1 else 0.0
        return (n, len(dm), mean, sd, se)

    cv = {s: 0 for s in STATES}
    cp = {s: 0 for s in STATES}
    for r in rows:
        cv[r["vs_state"]] += 1
        cp[r["ps_state"]] += 1

    out = []
    out.append("# OI Delta 4-state Backtest - 2026-09-21")
    out.append("")
    out.append("Purpose: compare two classifier inputs for the same four-state OI classifier.")
    out.append("")
    out.append("- delta_state (volume-delta school): sign of trade_flow.net_delta_1h")
    out.append("- delta_state_price (price school): current_price[now] minus current_price[nearest snapshot at or before T-60m]")
    out.append("")
    out.append("Rows joined: {0}".format(len(rows)))
    out.append("Horizons: {0}".format(", ".join(HORIZONS)))
    out.append("")
    out.append("State counts, volume-delta school: {0}".format(cv))
    out.append("State counts, price school: {0}".format(cp))
    out.append("")
    out.append("Reading: mean is percent forward return. se is day-clustered standard error (std of daily means over sqrt days).")
    out.append("")

    for sk, label in [("vs_state", "Volume-delta school (nd1h sign)"), ("ps_state", "Price school (close delta over 60m)")]:
        out.append("## {0}".format(label))
        out.append("")
        out.append("| state | horizon | n | days | mean pct | sd | se(day) |")
        out.append("|---|---|---|---|---|---|---|")
        for st in STATES:
            for hz in HORIZONS:
                n, d, mean, sd, se = agg(sk, st, hz)
                out.append("| {0} | {1} | {2} | {3} | {4:+.4f} | {5:.4f} | {6:.4f} |".format(st, hz, n, d, mean, sd, se))
        out.append("")

    out.append("## Caveats")
    out.append("")
    out.append("- Snapshot window 2026-09-13 to 2026-09-22. Hard cap.")
    out.append("- Price lag uses nearest snapshot at or before T-60m.")
    out.append("- Gauge-class fields. No verdict layer touched.")
    out.append("- Sample clusters on few days; se is day-clustered to reflect that. See BUGS T038.")
    out.append("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote " + str(OUT))


if __name__ == "__main__":
    main()
