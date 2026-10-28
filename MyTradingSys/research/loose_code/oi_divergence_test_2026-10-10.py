import sys
sys.dont_write_bytecode = True

import json
import statistics
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
SNAPS = ROOT / "runtime_data" / "snapshots"
LABELS = ROOT / "runtime_data" / "outcome_labels.json"
OUT = ROOT / "MyTradingSys" / "research" / "_archive" / "loose_2026-10" / "OI_DIVERGENCE_2026-10-10.md"

HORIZONS = ["30m", "60m", "120m"]
STATES = ["confirm_long", "divergence_bearish", "divergence_bullish", "confirm_short", "flat_price", "flat_oi", "neutral"]


def load_labels():
    with open(LABELS, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {r["file"]: r for r in d["labels"]}


def ts_ms(name):
    base = name.replace("BTCUSDT_", "").replace(".json", "")
    return int(base.split("_")[-1])


def sign(x):
    if x is None: return 0
    if x > 0: return 1
    if x < 0: return -1
    return 0


def classify(price_d, oi_pct):
    ps = sign(price_d)
    os_ = sign(oi_pct)
    if ps == 0 and os_ == 0: return "neutral"
    if ps == 0: return "flat_price"
    if os_ == 0: return "flat_oi"
    if ps > 0 and os_ > 0: return "confirm_long"
    if ps > 0 and os_ < 0: return "divergence_bearish"
    if ps < 0 and os_ > 0: return "divergence_bullish"
    if ps < 0 and os_ < 0: return "confirm_short"
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
    skip_oi = 0
    for ms, name, j in ms_list:
        lab = labels.get(name)
        if lab is None:
            skip_label += 1
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
            skip_lag += 1
            continue
        p_now = j.get("current_price")
        p_ago = by_ms[best].get("current_price")
        oi_pct = (j.get("open_interest") or {}).get("change_1h_pct")
        if p_now is None or p_ago is None or oi_pct is None:
            skip_oi += 1
            continue
        price_d = p_now - p_ago
        rows.append({
            "file": name,
            "ts": lab.get("ts", ""),
            "state": classify(price_d, float(oi_pct)),
            "price_d": price_d,
            "oi_pct": float(oi_pct),
            "fwd": lab.get("fwd_return_pct") or {},
        })
    print("rows={0} skip_label={1} skip_lag={2} skip_oi={3}".format(len(rows), skip_label, skip_lag, skip_oi))

    def agg(state, horizon):
        vals = []
        days = defaultdict(list)
        for r in rows:
            if r["state"] != state: continue
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

    counts = {s: 0 for s in STATES}
    for r in rows:
        counts[r["state"]] += 1

    out = []
    out.append("# OI Divergence Backtest - 2026-10-10")
    out.append("")
    out.append("Purpose: test price-vs-OI divergence as a directional signal over the full 28-day snapshot window.")
    out.append("")
    out.append("Method: for each BTCUSDT snapshot take the nearest at or before T-60m.")
    out.append("price_delta = current_price now minus current_price 1h ago.")
    out.append("oi_pct = snapshot open_interest.change_1h_pct (1-hour OI percent change).")
    out.append("")
    out.append("States (sign of price_delta, sign of oi_pct):")
    out.append("- confirm_long      (+ +) : price up, OI up. New longs.")
    out.append("- divergence_bearish(+ -) : price up, OI down. Short covering, weak rally.")
    out.append("- divergence_bullish(- +) : price down, OI up. New shorts.")
    out.append("- confirm_short     (- -) : price down, OI down. Long liquidation.")
    out.append("- flat_price        (0 *) : no price move.")
    out.append("- flat_oi           (* 0) : no OI move.")
    out.append("- neutral           (0 0) : both flat.")
    out.append("")
    out.append("Rows joined: {0}".format(len(rows)))
    out.append("State counts: {0}".format(counts))
    out.append("Horizons: {0}".format(", ".join(HORIZONS)))
    out.append("")
    out.append("Reading: mean is percent forward return. se is day-clustered standard error.")
    out.append("")
    out.append("| state | horizon | n | days | mean pct | sd | se(day) |")
    out.append("|---|---|---|---|---|---|---|")
    for st in STATES:
        for hz in HORIZONS:
            n, d, mean, sd, se = agg(st, hz)
            out.append("| {0} | {1} | {2} | {3} | {4:+.4f} | {5:.4f} | {6:.4f} |".format(st, hz, n, d, mean, sd, se))
    out.append("")
    out.append("## Caveats")
    out.append("")
    out.append("- Snapshot window 2026-09-12 to 2026-10-10. ~28 days.")
    out.append("- Lag uses nearest snapshot at or before T-60m.")
    out.append("- OI is the snapshot's own change_1h_pct, not an absolute OI level.")
    out.append("- Gauge-class fields. No verdict layer touched.")
    out.append("- Predecessor report: OI_DELTA_4STATE_BACKTEST_2026-09-21.md (9 days, 6362 rows).")
    out.append("")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote " + str(OUT))


if __name__ == "__main__":
    main()