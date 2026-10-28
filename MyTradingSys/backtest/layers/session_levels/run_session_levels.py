"""
T087 runner: base rates after a failed first break of the previous-day high (and mirror: low), BTCUSDT 1m.
Writes RESULT.md + events.json. Verdict rule fixed before the run: fewer than MIN_EVENTS (300) events in a cell =
"insufficient n"; "edge candidate" needs net mean > 0 and t >= T_MIN (2.0); otherwise "no edge".
See session_levels.py for the event definition (all clock/threshold parameters NO-SOURCE).
"""
import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.session_levels import session_levels as sl

MIN_EVENTS = 300
T_MIN = 2.0


def cell(rows):
    n = len(rows)
    firsts = [r["first"] for r in rows]
    nets = [r["net"] for r in rows]
    out = {"n": n, "target": firsts.count("target"), "stop": firsts.count("stop"), "neither": firsts.count("neither")}
    if n:
        m = sum(nets) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in nets) / (n - 1)) if n > 1 else 0.0
        out["net_mean_pct"] = 100 * m
        out["t"] = m / (sd / math.sqrt(n)) if sd > 0 else 0.0
        out["win"] = sum(1 for x in nets if x > 0) / n
    if n < MIN_EVENTS:
        out["verdict"] = "insufficient n"
    elif out["net_mean_pct"] > 0 and out["t"] >= T_MIN:
        out["verdict"] = "edge candidate"
    else:
        out["verdict"] = "no edge"
    return out


def fmt_cell(c):
    n = c["n"]
    if not n:
        return "n=0"
    return ("n=%d target %.0f%% / stop %.0f%% / neither %.0f%%, net %.3f%% t %.2f win %.0f%% -> %s" % (
        n, 100 * c["target"] / n, 100 * c["stop"] / n, 100 * c["neither"] / n, c["net_mean_pct"], c["t"],
        100 * c["win"], c["verdict"]))


def main():
    from MyTradingSys.backtest.bt.bt_data import load_klines
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    bars = load_klines(args.data_root)
    last = bars[-1]["t"] if bars else 0
    bars += [b for b in load_klines(args.data_root2) if b["t"] > last]
    bars.sort(key=lambda b: b["t"])
    if not bars:
        sys.exit("no data")
    fmt = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")
    print("Loaded %d 1m bars %s .. %s" % (len(bars), fmt(bars[0]["t"]), fmt(bars[-1]["t"])), file=sys.stderr)
    ev_all = {s: sl.failed_break_events(bars, s) for s in ("high", "low")}
    L = ["# T087 failed first break: base rates, BTCUSDT 1m %s .. %s" % (fmt(bars[0]["t"]), fmt(bars[-1]["t"])), "",
         "Event: first touch of the previous UTC day high (side high) / low (side low) before 14:00 UTC, close back "
         "through the level within 60 min. Entry at that close, stop = spike extreme, target = Asia or EU session "
         "extreme on the other side, time exit 14:00 UTC (US-open placeholder). Net = minus 2 x taker 0.05%%. "
         "Same-bar target+stop counts as stop. All clocks/thresholds NO-SOURCE. Verdict: n >= %d and t >= %.1f." % (MIN_EVENTS, T_MIN),
         "", "Events found: high side %d, low side %d (days with a failed first break)." % (len(ev_all["high"]), len(ev_all["low"])), ""]
    summary = {}
    for target in ("asia", "eu"):
        for sess in ("asia", "eu", "all"):
            for side in ("high", "low", "both"):
                evs = ev_all["high"] + ev_all["low"] if side == "both" else ev_all[side]
                rows = [e[target] for e in evs if e[target] and (sess == "all" or e["touch_session"] == sess)]
                key = "%s_target|touch_%s|%s" % (target, sess, side)
                summary[key] = cell(rows)
                L.append("- %s: %s" % (key, fmt_cell(summary[key])))
    L += ["", "## By year (both sides, touch session all)", ""]
    for target in ("asia", "eu"):
        for y in range(2022, 2027):
            rows = [e[target] for s in ("high", "low") for e in ev_all[s] if e[target]
                    and datetime.fromtimestamp(e["day"] * 86400, timezone.utc).year == y]
            L.append("- %s_target %d: %s" % (target, y, fmt_cell(cell(rows))))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
