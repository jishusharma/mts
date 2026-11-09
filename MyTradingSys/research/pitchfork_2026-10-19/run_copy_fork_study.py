"""Copy-paste pitchforks vs random same-slope parallels: reaction rate given a touch (PRE_REG_COPY_FORK.md).

DEV-side only: rows at/after splits.DEV_END are dropped before any computation; VALIDATION/HOLDOUT untouched.
Run: python MyTradingSys/research/pitchfork_2026-10-19/run_copy_fork_study.py
Writes RESULT_COPY_FORK.md next to this file.
"""

import csv
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

import pandas as pd  # noqa: E402

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (  # noqa: E402
    PitchforkVariant, construct_pitchfork, copy_fork, find_pivots_zigzag,
)

LOOKBACK = 4            # OURS (scanner default)
MIN_CHANGE = 0.03       # OURS (scanner default)
N_PASTES = 3            # OURS: next 3 pivots of P0's type after P2
WINDOW = 60             # OURS (= max_eval_bars)
N_CONTROL = 10          # OURS
U_SPAN = 1.5            # OURS: control ML shift in channel widths, U(-1.5, 1.5)
H = 6                   # OURS: bars to react
R = 0.015               # OURS: 1.5 % move away / through
SEED = 20261105         # OURS
DAY = 86400000


ETH_ROOT = "F:/MTS/data/tom_raw/klines_eth"   # ETH 1m files (moved from klines 2026-11-05)


def bars_from_1m(paths, symbol):
    """4H bars (UTC-aligned, complete 240-minute groups only) from 1m kline CSVs; rows at/after DEV_END dropped first."""
    end_ms = int(splits.DEV_END.value // 1_000_000)
    df = pd.concat([pd.read_csv(p, usecols=["open_time", "open", "high", "low", "close", "volume"]) for p in paths], ignore_index=True)
    df = df[df.open_time < end_ms].sort_values("open_time").drop_duplicates("open_time")
    g = df.groupby(df.open_time // (240 * 60_000))
    r = g.agg(t=("open_time", "first"), o=("open", "first"), h=("high", "max"), l=("low", "min"), c=("close", "last"),
              v=("volume", "sum"), n=("open_time", "size"))
    r = r[r.n == 240]
    rows = [{"t": int(x.t), "dt": str(pd.Timestamp(int(x.t), unit="ms")), "o": x.o, "h": x.h, "l": x.l, "c": x.c, "v": x.v}
            for x in r.itertuples()]
    assert pd.Timestamp(rows[-1]["dt"]) < splits.DEV_END
    return rows


def load_bars(symbol="BTCUSDT", root=None):
    """DEV-side bars only. BTCUSDT: the in-repo 4H csv. Other symbols: 4H built from <root>/<symbol>-1m-*.csv."""
    if symbol != "BTCUSDT":
        files = sorted(Path(root or ETH_ROOT).glob(symbol + "-1m-*.csv"))
        if not files:
            raise SystemExit("no %s 1m files under %s" % (symbol, root or ETH_ROOT))
        return bars_from_1m(files, symbol)
    rows = []
    with open(HERE / "btc_4h_2020_2026.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if pd.Timestamp(r["datetime"]) >= splits.DEV_END:
                break
            rows.append({"t": int(r["timestamp"]), "dt": r["datetime"], "o": float(r["open"]), "h": float(r["high"]),
                         "l": float(r["low"]), "c": float(r["close"]), "v": float(r["volume"])})
    assert pd.Timestamp(rows[-1]["dt"]) < splits.DEV_END
    return rows


class Line:
    """A straight line in log or linear price: value(t) = base + slope * (t - t0)."""

    def __init__(self, t0, base, slope, log_scale):
        self.t0, self.base, self.slope, self.log = t0, base, slope, log_scale

    def at(self, t):
        v = self.base + self.slope * (t - self.t0)
        return math.exp(v) if self.log else v


def reaction(bars, line, start, end):
    """(touched, reacted) for the first touch of `line` in bars[start:end] (PRE_REG Touch / Reaction)."""
    for i in range(max(start, 1), min(end, len(bars))):
        lv = line.at(i)
        if lv <= 0 or not (bars[i]["l"] <= lv <= bars[i]["h"]):
            continue
        above = bars[i - 1]["c"] > lv
        for j in range(i, min(i + H, len(bars))):
            if above:
                if j > i and bars[j]["c"] <= lv * (1 - R):
                    return True, False
                if bars[j]["h"] >= lv * (1 + R):
                    return True, True
            else:
                if j > i and bars[j]["c"] >= lv * (1 + R):
                    return True, False
                if bars[j]["l"] <= lv * (1 - R):
                    return True, True
        return True, False
    return False, False


def fork_lines(g, log_scale):
    """ML, UML, LML of a CopiedFork as Line objects."""
    return [Line(g.t0, g.p0 + off, g.slope, log_scale) for off in (0.0, g.offset_uml, g.offset_lml)]


def run(bars, pivots, log_scale, rng):
    counts = {k: [0, 0, 0] for k in ("copy", "control", "source")}  # lines, touches, reactions
    sources = pasted = 0
    for k in range(len(pivots) - 2):
        p0, p1, p2 = pivots[k], pivots[k + 1], pivots[k + 2]
        if p0.is_high == p1.is_high or p1.is_high == p2.is_high:
            continue
        try:
            pf = construct_pitchfork(p0, p1, p2, variant=PitchforkVariant.STANDARD, auto_schiff=False, log_scale=log_scale)
        except ValueError:
            continue
        sources += 1
        src = copy_fork(pf, p0.index, p0.price)  # identity paste: the source fork's own lines
        s0 = p2.index + LOOKBACK + 1
        for ln in fork_lines(src, log_scale):
            _tally(counts["source"], reaction(bars, ln, s0, s0 + WINDOW))
        anchors = [p for p in pivots[k + 3:] if p.is_high == p0.is_high][:N_PASTES]
        for a in anchors:
            cp = copy_fork(pf, a.index, a.price)
            pasted += 1
            s = a.index + LOOKBACK + 1
            for ln in fork_lines(cp, log_scale):
                _tally(counts["copy"], reaction(bars, ln, s, s + WINDOW))
            for _ in range(N_CONTROL):
                u = rng.uniform(-U_SPAN, U_SPAN)
                ln = Line(cp.t0, cp.p0 + u * cp.channel_width, cp.slope, log_scale)
                _tally(counts["control"], reaction(bars, ln, s, s + WINDOW))
    return counts, sources, pasted


def _tally(c, res):
    c[0] += 1
    c[1] += int(res[0])
    c[2] += int(res[1])


def two_prop(a_hit, a_n, b_hit, b_n):
    pa, pb = a_hit / a_n, b_hit / b_n
    pp = (a_hit + b_hit) / (a_n + b_n)
    se = math.sqrt(pp * (1 - pp) * (1 / a_n + 1 / b_n))
    return pa, pb, (pa - pb) * 100, (pa - pb) / se if se > 0 else float("nan")


def regime_mix(bars):
    sp = importlib.util.spec_from_file_location("pf_rsi_long", REPO / "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study_long.py")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    days = {}
    for b in bars:
        d = b["t"] // DAY
        x = days.get(d)
        if x is None:
            days[d] = dict(t=d * DAY, o=b["o"], h=b["h"], l=b["l"], c=b["c"], v=b["v"])
        else:
            x["h"], x["l"], x["c"], x["v"] = max(x["h"], b["h"]), min(x["l"], b["l"]), b["c"], x["v"] + b["v"]
    d1 = [days[d] for d in sorted(days)]
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    regime_at = mod.make_regime_at(*mod.build_context(d1, registry))
    lo, hi = bars[0]["t"], bars[-1]["t"] + 1
    d0 = int(lo // DAY)
    d0 += (4 - d0) % 7
    weeks = [d * DAY for d in range(d0, int(hi // DAY), 7)]
    return rk.regime_mix_line([regime_at(t) for t in weeks])


def main(symbol="BTCUSDT", root=None):
    bars = load_bars(symbol, root)
    pivots = find_pivots_zigzag([b["h"] for b in bars], [b["l"] for b in bars], lookback=LOOKBACK, min_change_pct=MIN_CHANGE)
    out = []
    for name, log_scale in (("log (primary)", True), ("linear (secondary)", False)):
        counts, sources, pasted = run(bars, pivots, log_scale, random.Random(SEED))
        c, k, s = counts["copy"], counts["control"], counts["source"]
        pa, pb, diff, z = two_prop(c[2], c[1], k[2], k[1])
        verdict = "copies attract" if diff >= 5 and z >= 2 else "no difference shown"
        out.append((name, sources, pasted, c, k, s, pa, pb, diff, z, verdict))
    mix = regime_mix(bars)
    lines = [
        "# RESULT: copy-paste pitchforks vs random parallels, %s 4H (DEV side only)" % symbol + "",
        "",
        f"Pre-reg: PRE_REG_COPY_FORK.md. Bars {bars[0]['dt']} .. {bars[-1]['dt']} (n={len(bars)}), pivots {len(pivots)}. "
        "VALIDATION/HOLDOUT (2024-07-01+) not read.",
        "",
        f"Regime mix: {mix}",
        "",
        "| Scale | Source forks | Pastes | Copy lines touched / react | Copy rate | Control lines touched / react | Control rate | Diff (pts) | z | Source-fork lines touched / react | Read |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, sources, pasted, c, k, s, pa, pb, diff, z, verdict in out:
        lines.append(f"| {name} | {sources} | {pasted} | {c[1]}/{c[0]} touched, {c[2]} react | {pa:.1%} | "
                     f"{k[1]}/{k[0]} touched, {k[2]} react | {pb:.1%} | {diff:+.1f} | {z:.2f} | "
                     f"{s[1]}/{s[0]} touched, {s[2]} react ({s[2] / max(1, s[1]):.1%}) | {verdict} |")
    lines += ["", "Read rule (pre-registered): copies attract iff diff >= +5 points and z >= 2. Descriptive, no fee-net, "
              "no trade claim; lines from the same source fork are not independent (z is optimistic)."]
    (HERE / ("RESULT_COPY_FORK.md" if symbol == "BTCUSDT" else "RESULT_COPY_FORK_%s.md" % symbol[:3])).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--root", default=None, help="1m kline folder for non-BTC symbols")
    a = ap.parse_args()
    main(a.symbol, a.root)
