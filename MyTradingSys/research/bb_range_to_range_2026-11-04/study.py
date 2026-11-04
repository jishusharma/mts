"""bb_range_to_range_2026-11-04: in a range, does the Bollinger band-to-band move repeat, by session? See PRE_REG.md.

Context comes ONLY from backtest/research_kit.py (regime_tag, session_tag, retest_entry, regime_mix_line, cluster stats, holm);
no trend tag is written here. Data loading and the as-of regime wrapper are reused by path from the sibling gated-divergence study.
Passes: --pass count (events and fills, geometry, no returns), --pass dev, --pass val (survivors only). Times are UTC ms.
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

_sp = importlib.util.spec_from_file_location("rsi_gated_sibling", REPO / "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py")
_sib = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_sib)
ms, load_1m, build_context, make_regime_at, week_starts = _sib.ms, _sib.load_1m, _sib.build_context, _sib.make_regime_at, _sib.week_starts

DAY = 86400000
BB_N, BB_K = 20, 2.0         # OURS (the common default; same as research/bb_state_map_2026-10)
K_BARS = 24                  # OURS: time-out, close of the 24th bar after the entry bar
STOP_FRAC = 0.5              # OURS: stop distance = 0.5 x distance to the target (reward : risk = 2 : 1)
RETEST_N = 10                # OURS (as the sibling gated-divergence study)
WIDTH_LOOKBACK = 500         # OURS: wide = band width >= median of the prior 500 bars' widths (descriptive stratum only)
COST = rk.TAKER_RT_PCT       # 0.14 % round trip, SOURCED research_kit
TFS = ("15m", "1h", "4h")
TF_MS = {"15m": 900000, "1h": 3600000, "4h": 14400000}
ENTRIES = ("signal", "retest")
SESSIONS = ("asia", "london", "ny", "late")
GATES = ("range", "all", "bull", "bear")
SIDES = ("both", "long", "short")
MIN_N, MIN_DAYS = 30, 20     # OURS: survivor eligibility
CONFIRM_SESSIONS = ("asia", "london", "ny")   # confirmatory family = 15m x these x ENTRIES = 6 cells (prereg_gate PASS); every other cell is descriptive


def bb_bands(closes, n=BB_N, k=BB_K):
    """(mid, upper, lower) as numpy arrays; bar i uses closes i-n+1..i only (population std). NaN until n closes exist."""
    c = np.asarray(closes, float)
    mid = np.full(len(c), np.nan)
    sd = np.full(len(c), np.nan)
    for i in range(n - 1, len(c)):
        w = c[i - n + 1:i + 1]
        mid[i] = w.mean()
        sd[i] = w.std()
    return mid, mid + k * sd, mid - k * sd


def find_events(bars, tf_ms=0):
    """First bar of each excursion beyond a band: close <= lower (long, side +1) or close >= upper (short, side -1).
    level = the touched band at that bar, target = the opposite band at that bar (both static for the trade).
    t_close = bar open + tf_ms; width = (upper - lower) / mid; wide = width >= median of the prior WIDTH_LOOKBACK widths."""
    c = [b["c"] for b in bars]
    mid, up, lo = bb_bands(c)
    width = (up - lo) / mid
    out = []
    for i in range(BB_N, len(c)):
        if np.isnan(up[i]) or np.isnan(up[i - 1]) or up[i] <= lo[i]:
            continue
        for side, hit, prev, level, target in ((1, c[i] <= lo[i], c[i - 1] <= lo[i - 1], lo[i], up[i]),
                                               (-1, c[i] >= up[i], c[i - 1] >= up[i - 1], up[i], lo[i])):
            if hit and not prev:
                hist = width[max(0, i - WIDTH_LOOKBACK):i]
                hist = hist[~np.isnan(hist)]
                wide = bool(len(hist) >= 100 and width[i] >= np.median(hist))
                out.append({"i": i, "side": side, "level": float(level), "target": float(target), "t_close": bars[i]["t"] + tf_ms,
                            "width": float(width[i]), "wide": wide})
    return out


def bracket_trade(ohlc, j, px, sgn, target, k_bars=K_BARS, stop_frac=STOP_FRAC):
    """Gross % of a bracket entered at px on bar j: target (static), stop = px -+ stop_frac x |target - px|, time-out at the close of
    bar j + k_bars. Bars j+1.. only (bar j itself is never read). Stop first when one bar touches both. Gap through the stop fills at
    the open. Returns the gross return in % of px, or None when the data ends before the exit or the target is on the wrong side."""
    if (target - px) * sgn <= 0:
        return None
    stop = px - sgn * stop_frac * abs(target - px)
    if j + k_bars >= len(ohlc):
        return None
    for b in range(j + 1, j + k_bars + 1):
        o, h, l, c = ohlc[b]
        if sgn > 0:
            if l <= stop:
                return (min(o, stop) - px) / px * 100.0
            if h >= target:
                return (target - px) / px * 100.0
        else:
            if h >= stop:
                return (px - max(o, stop)) / px * 100.0
            if l <= target:
                return (px - target) / px * 100.0
    return sgn * (ohlc[j + k_bars][3] - px) / px * 100.0


def session_of_event(e):
    return rk.session_tag(e["t_close"] / 1000)


def gate_events(events, regime_at, mode):
    """mode 'all' keeps every event (including those with no regime tag); otherwise events whose as-of regime at the signal-bar
    close equals `mode` (range, bull, bear)."""
    return [e for e in events if mode == "all" or regime_at(e["t_close"]) == mode]


def trades_for(events, bars, entry, n=RETEST_N, lo_ms=None, hi_ms=None):
    """One dict per taken trade. signal: fill at the close of the signal bar. retest: first pullback to the touched band within n bars
    after the signal bar (research_kit.retest_entry), limit at the band, open if gapped; no touch = no trade. Events whose signal
    close lies outside [lo_ms, hi_ms) are dropped. Returns (trades, number_of_signals_in_window)."""
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    out, nsig = [], 0
    for e in events:
        if (lo_ms is not None and e["t_close"] < lo_ms) or (hi_ms is not None and e["t_close"] >= hi_ms):
            continue
        nsig += 1
        i, sgn = e["i"], e["side"]
        if entry == "signal":
            j, px = i, ohlc[i][3]
        else:
            r = rk.retest_entry(ohlc, i, e["level"], sgn, n)
            if r is None:
                continue
            j, px = r
        g = bracket_trade(ohlc, j, px, sgn, e["target"])
        if g is None:
            continue
        reach = sgn * (e["target"] - px) / px * 100.0
        out.append({"day": int(bars[j]["t"] // DAY), "gross": g, "entry_px": px, "side": sgn, "hit": bool(abs(g - reach) < 1e-9),
                    "session": e.get("session"), "wide": e["wide"], "t": bars[j]["t"],
                    "stop_pct": STOP_FRAC * abs(e["target"] - px) / px * 100.0})
    return out, nsig


def cell_stats(trs):
    g = np.array([x["gross"] for x in trs])
    d = [x["day"] for x in trs]
    if len(g) == 0:
        return {"n": 0, "days": 0}
    net = g - COST
    m, se = rk.cluster_mean_se(net, d)
    t = rk.t_stat(m, se)
    hit, _ = rk.cluster_mean_se(np.array([1.0 if x["hit"] else 0.0 for x in trs]), d)
    return {"n": len(g), "days": len(set(d)), "gross": float(g.mean()), "net": m, "se": se, "t": t, "p": rk.norm_p_two(t),
            "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se, "hit_target": hit, "net_pos_share": float((net > 0).mean()),
            "median_stop_pct": float(np.median([x["stop_pct"] for x in trs]))}


def select(trs, side, session, wide=None):
    return [x for x in trs if (side == "both" or x["side"] == (1 if side == "long" else -1))
            and (session == "ALL" or x["session"] == session) and (wide is None or x["wide"] == wide)]


def main():
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    surv = []
    if a.pass_ == "val":
        surv = json.loads((HERE / "dev_survivors.json").read_text(encoding="utf-8"))
        if not surv:
            print("no DEV survivors: VALIDATION not read")
            return 0
        if (HERE / "val_cells.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
        lo_ms, hi_ms = ms(splits.VALIDATION_START), ms(splits.VALIDATION_END)
    else:
        lo_ms, hi_ms = ms(splits.DEV_START), ms(splits.DEV_END)
    bars_1m = load_1m(hi_ms)                       # never a bar at/after the window end (HOLDOUT never loaded)
    assert bars_1m[-1]["t"] < hi_ms
    daily, wk, mo = build_context(bars_1m, registry)
    regime_at = make_regime_at(daily, wk, mo)
    rows = []
    for tf in TFS:
        bars = resample(bars_1m, tf, registry)
        evs = find_events(bars, TF_MS[tf])
        for e in evs:
            e["session"] = session_of_event(e)
        for entry in ENTRIES:
            pool = {g_: trades_for(gate_events(evs, regime_at, g_), bars, entry, lo_ms=lo_ms, hi_ms=hi_ms)[0] for g_ in GATES}
            for gate in GATES:
                ge = gate_events(evs, regime_at, gate)
                inwin = [e for e in ge if lo_ms <= e["t_close"] < hi_ms]
                for side in SIDES:
                    for sess in ("ALL",) + SESSIONS:
                        for wide in (None, True, False):
                            if a.pass_ == "val" and not (gate == "range" and side == "both" and wide is None and [tf, sess, entry] in surv):
                                continue
                            sel = select(pool[gate], side, sess, wide)
                            sg = [e for e in inwin if (side == "both" or e["side"] == (1 if side == "long" else -1))
                                  and (sess == "ALL" or e["session"] == sess) and (wide is None or e["wide"] == wide)]
                            row = {"tf": tf, "session": sess, "entry": entry, "gate": gate, "side": side,
                                   "width": "any" if wide is None else ("wide" if wide else "narrow"), "signals": len(sg)}
                            if a.pass_ == "count":
                                row.update({"n": len(sel), "days": len({x["day"] for x in sel}),
                                            "median_stop_pct": float(np.median([x["stop_pct"] for x in sel])) if sel else float("nan")})
                            else:
                                row.update(cell_stats(sel))
                                if gate == "range" and side == "both" and wide is None:
                                    ung = select(pool["all"], "both", sess)
                                    if sel and ung:
                                        d, dse = rk.cluster_diff([x["gross"] for x in sel], [x["day"] for x in sel],
                                                                 [x["gross"] for x in ung], [x["day"] for x in ung])
                                        row.update({"vs_ungated": d, "vs_ungated_se": dse, "vs_ungated_t": rk.t_stat(d, dse)})
                            rows.append(row)
        print(tf, "done", file=sys.stderr, flush=True)
    if a.pass_ == "dev":
        fam = [r for r in rows if r["gate"] == "range" and r["side"] == "both" and r["width"] == "any" and r["tf"] == "15m"
               and r["session"] in CONFIRM_SESSIONS and r.get("n", 0) > 0]
        m = len(CONFIRM_SESSIONS) * len(ENTRIES)
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=m)
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            vt = r.get("vs_ungated_t", float("nan"))
            r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05 and vt == vt and vt >= 2)
        with open(HERE / "dev_survivors.json", "w", newline="\n") as f:
            json.dump([[r["tf"], r["session"], r["entry"]] for r in fam if r.get("survivor")], f)
    name = {"count": "counts.csv", "dev": "dev_cells.csv", "val": "val_cells.csv"}[a.pass_]
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("tf", "session", "entry", "gate", "side", "width"), k))
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
