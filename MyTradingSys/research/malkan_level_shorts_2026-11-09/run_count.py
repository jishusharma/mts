"""Count every firing of the Malkan level-short stack on BTCUSDT 4h, PRE_DEV + DEV only (2017-08 .. 2024-06), fee-net.
Usage: python run_count.py <dir with dev_4h.csv dev_1d.csv dev_1w.csv from fetch_klines.py> <out_dir>
Seal: backtest/splits.py. The last bar must be inside DEV (assert) so VALIDATION/HOLDOUT are never read. Writes tables.md."""
import csv, math, sys, statistics as st
from bisect import bisect_right
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from MyTradingSys.backtest import splits
from MyTradingSys.backtest.layers.rsi import malkan_level_short as m

H4, DAY = m.H4_MS, m.DAY_MS


def load(p):
    with open(p, newline="") as f:
        return [{"t": int(r["t"]), "o": float(r["o"]), "h": float(r["h"]), "l": float(r["l"]), "c": float(r["c"])} for r in csv.DictReader(f)]


def regime_of(t, dt_open, sma, dclose):
    i = bisect_right(dt_open, t - DAY) - 1
    if i < 0 or sma[i] is None:
        return None
    d = dclose[i] / sma[i] - 1
    return "bull" if d > 0.05 else "bear" if d < -0.05 else "range"


def ci(xs):
    n = len(xs)
    if n < 2:
        return ""
    return "%.2f" % (1.96 * st.stdev(xs) / math.sqrt(n))


def row(label, sims, key):
    xs = [s[key] for s in sims]
    if not xs:
        return "| %s | 0 | | | | |" % label
    return "| %s | %d | %.1f%% | %.1f%% | %+.3f | +-%s |" % (
        label, len(xs), 100 * sum(s["hit1"] for s in sims) / len(xs), 100 * sum(s["outcome"] == "target" for s in sims) / len(xs),
        sum(xs) / len(xs), ci(xs))


def nonoverlap(items):
    out, busy = [], -1
    for c, s in items:
        if c["entry_idx"] > busy:
            out.append((c, s))
            busy = s["exit_idx"]
    return out


def main(src, out):
    b4, bd, bw = load(Path(src) / "dev_4h.csv"), load(Path(src) / "dev_1d.csv"), load(Path(src) / "dev_1w.csv")
    last = datetime.fromtimestamp(b4[-1]["t"] / 1000, timezone.utc).replace(tzinfo=None)
    first = datetime.fromtimestamp(b4[0]["t"] / 1000, timezone.utc).replace(tzinfo=None)
    assert splits.window_of(last) == "DEV", "last bar %s is outside DEV: seal" % last
    assert first >= splits.PRE_DEV_START
    gaps = sum(1 for a, b in zip(b4, b4[1:]) if b["t"] - a["t"] != H4)
    ind, htf = m.indicators_and_htf(b4, bd, bw)
    dopen = [b["t"] for b in bd]
    dclose = [b["c"] for b in bd]
    sma = [None if i < 199 else sum(dclose[i - 199:i + 1]) / 200 for i in range(len(bd))]
    reg_bars = [regime_of(b["t"], dopen, sma, dclose) for b in b4]
    mix = {k: sum(1 for r in reg_bars if r == k) for k in ("bull", "bear", "range", None)}
    tot = sum(mix.values())
    L = []
    L.append("Data: BTCUSDT spot 4h, %s .. %s UTC, %d bars, %d gaps (a gap resets WaveTrend). Sealed: VALIDATION 2024-07..2025-06 and HOLDOUT 2025-07.. not read.\n" % (first, last, len(b4), gaps))
    L.append("Regime mix: bull %.1f%% / bear %.1f%% / range %.1f%% of 4h bars (daily close vs 200d SMA +-5%%); %.1f%% warm-up (NOT_IN_DATA).\n" % tuple(100 * mix[k] / tot for k in ("bull", "bear", "range", None)))
    arms = [{"div": d, "basis": b, "strict60": s} for d in "WS" for b in ("close", "wick") for s in (False, True)]
    summary = ["| arm (div / basis / trigger) | L1-3 chains | +L4 | +L5 = firings | too tight | non-overlap trades | hit >=1R | target 1R hit | net R/trade 1R exit | CI | net R/trade 2R exit | CI |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    detail = []
    for arm in arms:
        name = "%s / %s / %s" % ("window 3-10" if arm["div"] == "W" else "swing-swing", arm["basis"], "cross+RSI<60" if arm["strict60"] else "cross")
        ch = m.scan(b4, ind, htf, arm)
        n3 = len(ch)
        l4 = [c for c in ch if c["l4"]]
        fires = [c for c in ch if c["fires"]]
        tight = sum(1 for c in ch if c["l4"] and c["l5"] and c["too_tight"])
        sim1 = [(c, m.simulate(b4, c["entry_idx"], c["entry"], c["stop"], 1.0)) for c in fires]
        sim2 = [(c, m.simulate(b4, c["entry_idx"], c["entry"], c["stop"], 2.0)) for c in fires]
        n1, n2 = nonoverlap(sim1), nonoverlap(sim2)
        s1, s2 = [s for _, s in n1], [s for _, s in n2]
        a1 = "%+.3f" % (sum(s["r_net"] for s in s1) / len(s1)) if s1 else ""
        a2 = "%+.3f" % (sum(s["r_net"] for s in s2) / len(s2)) if s2 else ""
        summary.append("| %s | %d | %d | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
            name, n3, len(l4), len(fires), tight, len(s1),
            "%.1f%%" % (100 * sum(s["hit1"] for s in s1) / len(s1)) if s1 else "", "%.1f%%" % (100 * sum(s["outcome"] == "target" for s in s1) / len(s1)) if s1 else "",
            a1, ci([s["r_net"] for s in s1]), a2, ci([s["r_net"] for s in s2])))
        # ladder expectancy: does each layer add anything? (1R exit, non-overlapping within the tier)
        d = ["\n### Arm: %s\n" % name, "Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):\n",
             "| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |", "|---|---|---|---|---|---|"]
        for lab, sel in (("L1-3", ch), ("L1-4", l4), ("L1-5 (firings)", fires)):
            sims = nonoverlap([(c, m.simulate(b4, c["entry_idx"], c["entry"], c["stop"], 1.0)) for c in sel if not c["too_tight"]])
            d.append(row(lab, [s for _, s in sims], "r_net"))
        for exit_lab, items in (("1R exit", n1), ("2R exit", n2)):
            d.append("\nFirings by regime, %s (non-overlapping):\n" % exit_lab)
            d += ["| regime | trades | hit >=1R | target hit | net R/trade | CI |", "|---|---|---|---|---|---|"]
            for rg in ("bull", "bear", "range", None):
                sub = [s for c, s in items if reg_bars[c["entry_idx"]] == rg]
                d.append(row(str(rg if rg else "warm-up"), sub, "r_net"))
            d.append("\nFirings by year, %s:\n" % exit_lab)
            d += ["| year | trades | hit >=1R | target hit | net R/trade | CI |", "|---|---|---|---|---|---|"]
            for y in range(2017, 2025):
                sub = [s for c, s in items if datetime.fromtimestamp(c["t"] / 1000, timezone.utc).year == y]
                d.append(row(str(y), sub, "r_net"))
        d.append("\nFirings (all, overlapping allowed): %d; kind: %d sweep / %d div." % (len(fires), sum(c["kind"] == "sweep" for c in fires), sum(c["kind"] == "div" for c in fires)))
        detail += d
    Path(out, "tables.md").write_text("\n".join(L) + "\n## Arm summary\n\n" + "\n".join(summary) + "\n\n## Per-arm detail\n" + "\n".join(detail) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L)); print("\n".join(summary))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
