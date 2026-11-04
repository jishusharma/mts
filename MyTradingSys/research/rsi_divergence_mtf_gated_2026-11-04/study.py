"""rsi_divergence_mtf_gated_2026-11-04: RSI divergence re-run under Malkan's monthly/weekly RSI gate. See PRE_REG.md.

Context comes ONLY from backtest/research_kit.py (regime_tag, retest_entry, regime_mix_line, cluster stats); no trend tag here.
Passes: --pass count (event counts, no returns), --pass dev, --pass val (survivors only), written to this folder.
Times are UTC milliseconds throughout. Regime at a bar close is read as-of that close (research_kit.regime_tag).
"""
import argparse
import csv
import json
import sys
from datetime import timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence  # noqa: E402

DAY = 86400000
H = 10                      # exit H bars after entry bar close (OURS, carried from the 2026-10-09 run, NO-SOURCE)
RETEST_N = 10               # OURS
COST = rk.TAKER_RT_PCT      # 0.14 % round trip, SOURCED research_kit
RSI_PERIOD = 14             # as the original run
TFS = ("15m", "1h", "4h", "1d")
TF_MS = {"15m": 900000, "1h": 3600000, "4h": 14400000, "1d": DAY}
ARMS = {"W12": (3, 12), "W18": (3, 18), "C3_10": (3, 10), "C5_14": (5, 14)}   # W12/W18 SOURCED (operator relay); C* OURS comparison
HOLM_ARMS = ("W12", "W18")
KINDS = {"bullish": (1.0, "bull"), "bearish": (-1.0, "bear")}   # kind -> (side sign, aligned regime)
ENTRIES = ("signal", "retest")
MIN_N, MIN_DAYS = 30, 20    # OURS: survivor eligibility
DATA_ROOTS = ("F:/MTS/Dumps/backtest/raw_1m_2019", "F:/MTS/Dumps/backtest/raw_1m_2022", "F:/MTS/Dumps/backtest/raw")


def ms(ts):
    return int(ts.tz_localize(timezone.utc).timestamp() * 1000)


def gate_label(regime, kind):
    """aligned = regime matches the divergence side (bull for bullish, bear for bearish); counter = the opposite; range."""
    if regime is None:
        return "none"
    if regime == "range":
        return "range"
    return "aligned" if regime == KINDS[kind][1] else "counter"


def gate_events(events, regime_at, kind, mode="aligned"):
    """Keep events whose as-of regime at the event bar CLOSE has gate label `mode` ('all' keeps everything with a regime)."""
    out = []
    for e in events:
        lab = gate_label(regime_at(e["t_close"]), kind)
        if lab == "none":
            continue
        if mode == "all" or lab == mode:
            out.append(e)
    return out


def make_regime_at(daily, weekly_rsi, monthly_rsi):
    """regime(t_ms) -> regime str|None via research_kit.regime_tag. Daily, weekly and monthly bars all close at 00:00 UTC, so
    the as-of tag is constant inside a UTC day; it is evaluated at the day's first instant and cached per day."""
    cache = {}

    def regime_at(t):
        d = int(t // DAY)
        if d not in cache:
            cache[d] = rk.regime_tag(d * DAY, daily, weekly_rsi, monthly_rsi)["regime"]
        return cache[d]
    return regime_at


def find_events(bars, kind, arm, tf):
    """rsi_divergence events (close-to-close, strict-swing pivots, stamped one bar after swing B) with the bar close time."""
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    closes = [b["c"] for b in bars]
    ts = [b["t"] for b in bars]
    rsi = rsi_core(closes, RSI_PERIOD)
    lo, hi = ARMS[arm]
    evs = rsi_divergence(closes, rsi, ts, lo, hi, kind, 0.0)
    for e in evs:
        e["t_close"] = ts[e["i"]] + TF_MS[tf]
    return evs


def trades_for(events, bars, kind, entry, h=H, n=RETEST_N, lo_ms=None, hi_ms=None):
    """Per event {day, gross_pct}. signal: enter at the close of the event bar. retest: first pullback to swing B's close
    within n bars after the event bar (research_kit.retest_entry), fill at the level or the open if gapped.
    Exit = close h bars after the entry bar. Events with no exit bar in the data, or outside [lo_ms, hi_ms), are dropped."""
    sgn = KINDS[kind][0]
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    out, nsig = [], 0
    for e in events:
        if (lo_ms is not None and e["t_close"] < lo_ms) or (hi_ms is not None and e["t_close"] >= hi_ms):
            continue
        i = e["i"]
        nsig += 1
        if entry == "signal":
            j, px = i, ohlc[i][3]
        else:
            r = rk.retest_entry(ohlc, i, e["close_b"], int(sgn), n)
            if r is None:
                continue
            j, px = r
        if j + h >= len(ohlc):
            continue
        out.append({"day": int(bars[j]["t"] // DAY), "gross": sgn * (ohlc[j + h][3] - px) / px * 100.0, "t": bars[j]["t"]})
    return out, nsig


def cell_stats(trs, drift):
    """Net (after COST) and excess-over-regime-drift stats, day-clustered. drift = (gross list, day list) same side, same regime."""
    g = np.array([x["gross"] for x in trs])
    d = [x["day"] for x in trs]
    if len(g) == 0:
        return {"n": 0, "days": 0}
    net = g - COST
    m, se = rk.cluster_mean_se(net, d)
    t = rk.t_stat(m, se)
    if drift and len(drift[0]):
        ex, ex_se = rk.cluster_diff(g, d, np.array(drift[0]), drift[1])
    else:
        ex, ex_se = float("nan"), float("nan")
    return {"n": len(g), "days": len(set(d)), "gross": float(g.mean()), "net": m, "se": se, "t": t, "p": rk.norm_p_two(t),
            "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se, "hit_net": float((net > 0).mean()),
            "excess": ex, "excess_se": ex_se, "excess_t": rk.t_stat(ex, ex_se)}


def regime_drift(bars, regime_at, sgn, tf, label, h=H, lo_ms=None, hi_ms=None):
    """Same-side gross h-bar return from every bar close whose as-of regime == label inside the window (drift control)."""
    c = np.array([b["c"] for b in bars])
    g, day = [], []
    for i in range(len(bars) - h):
        tc = bars[i]["t"] + TF_MS[tf]
        if (lo_ms is not None and tc < lo_ms) or (hi_ms is not None and tc >= hi_ms):
            continue
        if regime_at(tc) == label:
            g.append(sgn * (c[i + h] - c[i]) / c[i] * 100.0)
            day.append(int(bars[i]["t"] // DAY))
    return g, day


def load_1m(end_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = {}
    for r in DATA_ROOTS:
        for b in load_klines(r, end_ms=end_ms):
            bars[b["t"]] = b
    return [bars[k] for k in sorted(bars)]


def rsi_series(bars):
    """(t_close, rsi) for weekly/monthly bars. t_close = next bar's open; the final bar is dropped (its close time is not
    known from the data, and guessing it early would be look-ahead)."""
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    r = rsi_core([x["c"] for x in bars], RSI_PERIOD)
    keep = [k for k in range(len(bars) - 1) if r[k] is not None]
    return [bars[k + 1]["t"] for k in keep], [r[k] for k in keep]


def build_context(bars_1m, registry):
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    d = resample(bars_1m, "1d", registry)
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    return daily, rsi_series(resample(bars_1m, "1w", registry)), rsi_series(resample(bars_1m, "1M", registry))


def week_starts(lo_ms, hi_ms):
    """Monday 00:00 UTC instants in [lo_ms, hi_ms). Epoch day 4 (1970-01-05) is a Monday."""
    d0 = int(lo_ms // DAY)
    d0 += (4 - d0) % 7
    return [d * DAY for d in range(d0, int(hi_ms // DAY), 7)]


def main():
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    if a.pass_ == "val":
        survivors = json.loads((HERE / "dev_survivors.json").read_text(encoding="utf-8"))
        if not survivors:
            print("no DEV survivors: VALIDATION not read")
            return 0
        if (HERE / "val_cells.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
        lo_ms, hi_ms = ms(splits.VALIDATION_START), ms(splits.VALIDATION_END)
    else:
        lo_ms, hi_ms = ms(splits.DEV_START), ms(splits.DEV_END)
    bars_1m = load_1m(hi_ms)                      # never a bar at/after the window end (HOLDOUT never loaded)
    assert bars_1m[-1]["t"] < hi_ms
    daily, wk, mo = build_context(bars_1m, registry)
    regime_at = make_regime_at(daily, wk, mo)
    rows = []
    for tf in TFS:
        bars = resample(bars_1m, tf, registry)
        for arm in ARMS:
            for kind, (sgn, aligned) in KINDS.items():
                evs = find_events(bars, kind, arm, tf)
                for mode in ("all", "aligned", "counter", "range"):
                    ge = gate_events(evs, regime_at, kind, mode) if mode != "all" else list(evs)
                    for entry in ENTRIES:
                        if a.pass_ == "val" and not (mode == "aligned" and [tf, arm, kind, entry] in survivors):
                            continue
                        trs, nsig = trades_for(ge, bars, kind, entry, lo_ms=lo_ms, hi_ms=hi_ms)
                        row = {"tf": tf, "arm": arm, "kind": kind, "gate": mode, "entry": entry, "signals": nsig}
                        if a.pass_ == "count":
                            row.update({"n": len(trs), "days": len({x["day"] for x in trs})})
                        else:
                            dr = regime_drift(bars, regime_at, sgn, tf, aligned, lo_ms=lo_ms, hi_ms=hi_ms) if mode == "aligned" else None
                            row.update(cell_stats(trs, dr))
                        rows.append(row)
        print(tf, "done", file=sys.stderr, flush=True)
    if a.pass_ == "dev":
        fam = [r for r in rows if r["gate"] == "aligned" and r["arm"] in HOLM_ARMS and r.get("n", 0) > 0]
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=len(HOLM_ARMS) * len(TFS) * len(KINDS) * len(ENTRIES))
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05
                                 and r["excess_t"] == r["excess_t"] and r["excess_t"] >= 2)
        with open(HERE / "dev_survivors.json", "w", newline="\n") as f:
            json.dump([[r["tf"], r["arm"], r["kind"], r["entry"]] for r in fam if r.get("survivor")], f)
    name = {"count": "counts.csv", "dev": "dev_cells.csv", "val": "val_cells.csv"}[a.pass_]
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("tf", "arm", "kind", "gate", "entry"), k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    line = rk.regime_mix_line([regime_at(t) for t in week_starts(lo_ms, hi_ms)])
    (HERE / ("regime_mix_%s.txt" % a.pass_)).write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
