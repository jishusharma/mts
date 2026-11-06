"""wt_cycle_clock: descriptive WT cycle clock per TF (SPEC Card 3). Count-only, no fees, no edge claim. See PRE_REG.md.

Passes: --pass count only (DEV bars; loader end = splits.DEV_END, VALIDATION/HOLDOUT never loaded). WT = layers/wavetrend only.
State per closed bar: last valid dot type + age in median-cycle units; targets: time to the next opposite-type valid dot and the
close-to-close move to it (raw %, signed as price change). Bars without a later opposite dot inside DEV are dropped (counted).
"""
import csv, importlib.util, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest.layers.wavetrend import wavetrend as wtm  # noqa: E402

TF_MS = {"5m": 300000, "15m": 900000, "30m": 1800000, "1h": 3600000, "4h": 14400000}
EDGES = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1e9)     # median cycles, SPEC "0-0.25 .. >1.5"
HOUR = 3600000.0


def _nest():
    spec = importlib.util.spec_from_file_location("nest", HERE.parent / "wt_mtf_nesting" / "study.py")
    m = importlib.util.module_from_spec(spec); sys.modules["nest"] = m; spec.loader.exec_module(m)
    return m


def cycles(t, dots):
    """Bible cycle: valid bottom -> last valid top before the next bottom. Returns lengths in hours."""
    out, bot, last_top = [], None, None
    for i, s in dots:
        if s == 1:
            if bot is not None and last_top is not None:
                out.append((t[last_top] - t[bot]) / HOUR)
            bot, last_top = i, None
        elif bot is not None:
            last_top = i
    if bot is not None and last_top is not None:
        out.append((t[last_top] - t[bot]) / HOUR)
    return out


def quart(x):
    return (float(np.median(x)), float(np.percentile(x, 25)), float(np.percentile(x, 75))) if len(x) else (float("nan"),) * 3


def clock_rows(tf, bars, dots, med_h):
    """Rows per (last dot type, age bin)."""
    n = len(bars)
    t = np.array([b["t"] for b in bars], dtype=float) + TF_MS[tf]      # close times
    c = np.array([b["c"] for b in bars])
    dix = np.array([i for i, _ in dots]); dty = np.array([s for _, s in dots])
    rows = {}
    nxt_drop = 0
    for k, (i, s) in enumerate(dots):
        # next opposite-type dot index after bar i
        j = next((dots[q][0] for q in range(k + 1, len(dots)) if dots[q][1] == -s), None)
        end = dots[k + 1][0] if k + 1 < len(dots) else n       # state holds until the next dot of ANY type
        if j is None:
            nxt_drop += end - i
            continue
        for b in range(i, end):
            age = (t[b] - t[i]) / HOUR / med_h
            ai = int(np.searchsorted(EDGES, age, side="right")) - 1
            r = rows.setdefault((s, ai), {"dt": [], "mv": [], "ep": set()})
            r["dt"].append((t[j] - t[b]) / HOUR)
            r["mv"].append((c[j] - c[b]) / c[b] * 100.0)
            r["ep"].add(i)
    out = []
    for (s, ai), r in sorted(rows.items()):
        dm, d25, d75 = quart(r["dt"]); mm, m25, m75 = quart(r["mv"])
        lab = f"{EDGES[ai]:g}-{EDGES[ai+1]:g}" if EDGES[ai + 1] < 1e8 else f">{EDGES[ai]:g}"
        out.append({"tf": tf, "last_dot": "bottom" if s == 1 else "top", "age_bin": lab, "n_bars": len(r["dt"]), "n_episodes": len(r["ep"]),
                    "dt_h_median": dm, "dt_h_p25": d25, "dt_h_p75": d75, "move_pct_median": mm, "move_pct_p25": m25, "move_pct_p75": m75})
    return out, nxt_drop


def main():
    from MyTradingSys.backtest.bt.bt_data import load_klines
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    N = _nest()
    lo, hi = N.ms(splits.DEV_START), N.ms(splits.DEV_END)
    bars_1m = load_klines(N.ROOT, end_ms=hi)
    assert bars_1m and bars_1m[-1]["t"] < hi
    reg = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    freq, tables, drops = [], [], {}
    pairs = []
    for tf in TF_MS:
        bars = resample(bars_1m, tf, reg)
        rows = wtm.compute([(b["t"], b["h"], b["l"], b["c"]) for b in bars], TF_MS[tf])
        dots = N.valid_dots(rows)                                    # all valid dots, not deduped (descriptive clock)
        t = [b["t"] for b in bars]
        first_ok = next(i for i, r in enumerate(rows) if r.wt1 == r.wt1)
        weeks = (t[-1] - t[first_ok]) / (7 * 86400000.0)
        L = cycles(t, dots)
        med_h = float(np.median(L))
        pairs.append((tf, len(dots), sum(s == 1 for _, s in dots)))
        cr = sum(1 for r in rows if r.event != 0)
        freq.append({"tf": tf, "valid_dots": len(dots), "bottoms": sum(s == 1 for _, s in dots), "tops": sum(s == -1 for _, s in dots),
                     "crosses": cr, "zone_dot_share_pct": 100.0 * len(dots) / max(cr, 1), "cycles": len(L), "weeks": weeks,
                     "cycles_per_week": len(L) / weeks, "cycle_len_h_median": med_h,
                     "cycle_len_h_p25": quart(L)[1], "cycle_len_h_p75": quart(L)[2]})
        tb, dr = clock_rows(tf, bars, dots, med_h)
        tables += tb; drops[tf] = dr
        print(tf, "done", file=sys.stderr, flush=True)
    for name, rows in (("freq.csv", freq), ("clock.csv", tables)):
        with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    c30 = N._c30()
    daily, wk, mo = c30.build_context(bars_1m, reg)
    ctx = c30.make_ctx_at(daily, wk, mo)
    line = rk.regime_mix_line([ctx(t)["regime"] for t in N.week_starts(lo, hi)])
    (HERE / "regime_mix_count.txt").write_text(line + "\n", encoding="utf-8", newline="\n")
    (HERE / "meta.json").write_text(json.dumps({"dropped_state_bars_no_next_dot": drops}), encoding="utf-8", newline="\n")
    print(line)
    for r in freq: print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    print(pairs)


if __name__ == "__main__":
    main()
