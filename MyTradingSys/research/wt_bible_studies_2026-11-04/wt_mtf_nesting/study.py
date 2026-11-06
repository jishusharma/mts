"""wt_mtf_nesting: 5m/15m WT valid dots gated by 30m cycle phase + 4h slope vs the rejected dots. See PRE_REG.md.

Passes: --pass count (event counts only, no returns), --pass dev (DEV returns). VALIDATION is not read by this script
(loader end = splits.DEV_END; HOLDOUT never loaded). WT = backtest/layers/wavetrend/wavetrend.py (golden-tested) only.
"""
import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest.layers.wavetrend import wavetrend as wtm  # noqa: E402

DAY = 86400000
BAND = 53.0                     # SOURCED LazyBear (wavetrend.OB2)
H = 12                          # exit bars of the entry TF, SOURCED SPEC Card 2
DEDUP = 48                      # bars of the TF, OURS (SPEC shared line)
COST = rk.TAKER_RT_PCT          # 0.14 % round trip, SOURCED
TF_MS = {"5m": 300000, "15m": 900000, "30m": 1800000, "4h": 14400000}
ENTRY_TFS = ("5m", "15m")
AGE_BINS = ((0.0, 0.5), (0.5, 1.0), (1.0, 1e9))   # median cycles, SOURCED SPEC
M_HOLM = 232                    # prereg_gate.py --m auto output (220 DEV variants + 12 new cells), frozen in PRE_REG
B_BOOT = 4000                   # OURS
SEED = 20261106                 # OURS
ROOT = "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1m_2022"   # DEV 1m bars from 2022-01
ARMS = ("nested", "phase_only", "slope_only", "age_0_0.5", "age_0.5_1", "age_gt1")


def ms(ts):
    return int(ts.tz_localize("UTC").timestamp() * 1000)


def valid_dots(rows):
    """[(i, +1 bottom | -1 top)]: wt1/wt2 cross with prior-bar wt1 beyond +-53 (OURS Bible), closed bars."""
    out = []
    for i, r in enumerate(rows):
        if i == 0 or r.event == 0:
            continue
        p = rows[i - 1].wt1
        if r.event == 1 and p == p and p <= -BAND:
            out.append((i, 1))
        elif r.event == -1 and p == p and p >= BAND:
            out.append((i, -1))
    return out


def dedup(dots):
    """Per side: after an event skip the same side for DEDUP bars of its TF."""
    last, out = {1: -10**9, -1: -10**9}, []
    for i, s in dots:
        if i - last[s] >= DEDUP:
            out.append((i, s))
            last[s] = i
    return out


def median_cycle_hours(t30, dots30):
    """Bible cycle: valid bottom -> the last valid top before the next bottom; length = hours between them. Median."""
    lens, bot, last_top = [], None, None
    for i, s in dots30:
        if s == 1:
            if bot is not None and last_top is not None:
                lens.append((t30[last_top] - t30[bot]) / 3600000.0)
            bot, last_top = i, None
        elif bot is not None:
            last_top = i
    if bot is not None and last_top is not None:
        lens.append((t30[last_top] - t30[bot]) / 3600000.0)
    return float(np.median(lens)) if lens else float("nan"), len(lens)


def phase_lookup(rows30, dots30, t30):
    """Sorted dot close times and sides on 30m, for the last valid 30m dot closed at or before t."""
    return np.array([t30[i] + TF_MS["30m"] for i, _ in dots30]), np.array([s for _, s in dots30])


def slope_4h(rows4, t4):
    """(close_times, slope sign) per closed 4h bar: sign(wt1[k] - wt1[k-3]); 0 if NaN."""
    ct = np.array([t + TF_MS["4h"] for t in t4])
    sl = np.zeros(len(rows4), dtype=int)
    for k in range(3, len(rows4)):
        a, b = rows4[k].wt1, rows4[k - 3].wt1
        if a == a and b == b:
            sl[k] = (a > b) - (a < b)
    return ct, sl


def build_events(tf, bars, rows, ph_t, ph_s, sl_t, sl_s, cyc_h):
    """Deduped baseline dots of one entry TF with gates. Returns list of dicts incl. gross return and the arm flags."""
    c = [b["c"] for b in bars]
    out = []
    for i, s in dedup(valid_dots(rows)):
        if i + H >= len(bars):
            continue
        tc = bars[i]["t"] + TF_MS[tf]
        k = int(np.searchsorted(ph_t, tc, side="right")) - 1
        m = int(np.searchsorted(sl_t, tc, side="right")) - 1
        e = {"i": i, "side": s, "tc": tc, "day": int(bars[i]["t"] // DAY),
             "gross": s * (c[i + H] - c[i]) / c[i] * 100.0, "phase": 0, "age": float("nan"), "slope": 0}
        if k >= 0:
            e["phase"] = 1 if ph_s[k] == 1 else -1                       # last 30m dot bottom => UP, top => DOWN
            e["age"] = (tc - ph_t[k]) / 3600000.0 / cyc_h
        if m >= 0:
            e["slope"] = int(sl_s[m])
        out.append(e)
    return out


def arm_flags(e):
    ph = e["phase"] == e["side"]            # long needs UP(+1), short needs DOWN(-1): phase value equals side
    sl = e["slope"] == e["side"]            # long needs slope up(+1), short slope down(-1)
    known = e["phase"] != 0 and e["slope"] != 0
    f = {"known": known, "nested": known and ph and sl, "phase_only": e["phase"] != 0 and ph,
         "slope_only": e["slope"] != 0 and sl}
    a = e["age"]
    nested = f["nested"]
    for name, (lo, hi) in zip(("age_0_0.5", "age_0.5_1", "age_gt1"), AGE_BINS):
        f[name] = bool(nested and a == a and lo <= a < hi)
    return f


def boot_days(g, d, rng, b=B_BOOT):
    """Day-block bootstrap of the mean: resample UTC days with replacement; returns means array."""
    days = np.unique(d)
    idx = {x: np.where(d == x)[0] for x in days}
    s = np.array([g[idx[x]].sum() for x in days])
    n = np.array([len(idx[x]) for x in days], dtype=float)
    pick = rng.integers(0, len(days), size=(b, len(days)))
    num, den = s[pick].sum(1), n[pick].sum(1)
    return np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)


def diff_stats(ga, da, gb, db, rng, b=B_BOOT):
    """Difference of means A - B, day-block bootstrap over the union of days (zero-trade days stay in the resample)."""
    days = np.unique(np.concatenate([da, db]))
    ia = {x: np.where(da == x)[0] for x in days}
    ib = {x: np.where(db == x)[0] for x in days}
    sa = np.array([ga[ia[x]].sum() for x in days]); na = np.array([len(ia[x]) for x in days], float)
    sb = np.array([gb[ib[x]].sum() for x in days]); nb = np.array([len(ib[x]) for x in days], float)
    pick = rng.integers(0, len(days), size=(b, len(days)))
    A, NA, B_, NB = sa[pick].sum(1), na[pick].sum(1), sb[pick].sum(1), nb[pick].sum(1)
    ok = (NA > 0) & (NB > 0)
    dm = (A[ok] / NA[ok]) - (B_[ok] / NB[ok])
    point = ga.mean() - gb.mean()
    lo, hi = np.percentile(dm, [2.5, 97.5])
    p = 2.0 * min((dm <= 0).mean(), (dm >= 0).mean())          # two-sided bootstrap p, floor 1/b
    return point, float(lo), float(hi), max(p, 1.0 / b)


def net_stats(g, d, rng):
    net = g - COST
    means = boot_days(net, d, rng)
    lo, hi = np.percentile(means[~np.isnan(means)], [2.5, 97.5])
    return float(net.mean()), float(lo), float(hi)


def cells_for(tf, events, rng):
    rows = []
    fl = [arm_flags(e) for e in events]
    kn = [i for i, f in enumerate(fl) if f["known"] or f["phase_only"] or f["slope_only"]]
    g_all = np.array([e["gross"] for e in events]); d_all = np.array([e["day"] for e in events])
    def pick(arm, inv=False):
        m = np.array([bool(f[arm]) for f in fl])
        if arm == "phase_only":
            m = np.array([f["phase_only"] for f in fl]);
        if arm == "slope_only":
            m = np.array([f["slope_only"] for f in fl])
        return ~m if inv else m
    known = np.array([f["known"] for f in fl])
    for arm in ARMS:
        m = pick(arm)
        if arm == "phase_only":
            comp = np.array([e["phase"] != 0 for e in events]) & ~m
        elif arm == "slope_only":
            comp = np.array([e["slope"] != 0 for e in events]) & ~m
        else:
            comp = known & ~m          # rejected = known-gate baseline dots the arm does not take
        n_a, n_c = int(m.sum()), int(comp.sum())
        r = {"tf": tf, "arm": arm, "n": n_a, "n_comp": n_c, "days": int(len(set(d_all[m])))}
        if n_a >= 2 and n_c >= 2:
            mean, lo, hi = net_stats(g_all[m], d_all[m], rng)
            pt, dlo, dhi, p = diff_stats(g_all[m], d_all[m], g_all[comp], d_all[comp], rng)
            r.update({"net": mean, "net_lo": lo, "net_hi": hi, "comp_net": float(g_all[comp].mean() - COST),
                      "diff": pt, "diff_lo": dlo, "diff_hi": dhi, "p": p})
        rows.append(r)
    r = {"tf": tf, "arm": "baseline", "n": len(events), "n_comp": 0, "days": int(len(set(d_all)))}
    if len(events) >= 2:
        mean, lo, hi = net_stats(g_all, d_all, rng)
        r.update({"net": mean, "net_lo": lo, "net_hi": hi})
    rows.append(r)
    return rows


def week_starts(lo_ms, hi_ms):
    d0 = int(lo_ms // DAY)
    d0 += (4 - d0) % 7
    return [d * DAY for d in range(d0, int(hi_ms // DAY), 7)]


def _c30():
    spec = importlib.util.spec_from_file_location("c30", REPO / "MyTradingSys/research/wavetrend_c30_retest_2026-11-04/study.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["c30"] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    from MyTradingSys.backtest.bt.bt_data import load_klines
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev"))
    a = ap.parse_args()
    lo_ms, hi_ms = ms(splits.DEV_START), ms(splits.DEV_END)
    bars_1m = load_klines(ROOT, end_ms=hi_ms)
    assert bars_1m and bars_1m[-1]["t"] < hi_ms and bars_1m[0]["t"] >= lo_ms - DAY
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    tfb, tfr, tft = {}, {}, {}
    for tf in TF_MS:
        tfb[tf] = resample(bars_1m, tf, registry)
        tft[tf] = [b["t"] for b in tfb[tf]]
        tfr[tf] = wtm.compute([(b["t"], b["h"], b["l"], b["c"]) for b in tfb[tf]], TF_MS[tf])
    d30 = dedup(valid_dots(tfr["30m"])) if False else valid_dots(tfr["30m"])   # phase uses every valid 30m dot, not deduped
    cyc_h, ncyc = median_cycle_hours(tft["30m"], d30)
    ph_t, ph_s = phase_lookup(tfr["30m"], d30, tft["30m"])
    sl_t, sl_s = slope_4h(tfr["4h"], tft["4h"])
    rng = np.random.default_rng(SEED)
    out, counts = [], []
    for tf in ENTRY_TFS:
        ev = [e for e in build_events(tf, tfb[tf], tfr[tf], ph_t, ph_s, sl_t, sl_s, cyc_h) if lo_ms <= e["tc"] < hi_ms]
        fl = [arm_flags(e) for e in ev]
        known = sum(f["known"] for f in fl)
        nested = sum(f["nested"] for f in fl)
        counts.append({"tf": tf, "baseline": len(ev), "known": known, "nested": nested, "rejected": known - nested,
                       "days_nested": len({e["day"] for e, f in zip(ev, fl) if f["nested"]}),
                       "days_rejected": len({e["day"] for e, f in zip(ev, fl) if f["known"] and not f["nested"]}),
                       "unknown_gate": len(ev) - known})
        if a.pass_ == "dev":
            out += cells_for(tf, ev, rng)
    c30 = _c30()
    daily, wk, mo = c30.build_context(bars_1m, registry)
    ctx_at = c30.make_ctx_at(daily, wk, mo)
    line = rk.regime_mix_line([ctx_at(t)["regime"] for t in week_starts(lo_ms, hi_ms)])
    (HERE / ("regime_mix_" + a.pass_ + ".txt")).write_text(line + "\n", encoding="utf-8", newline="\n")
    meta = {"median_cycle_hours_30m": cyc_h, "n_cycles": ncyc, "first_bar": bars_1m[0]["t"], "last_bar": bars_1m[-1]["t"]}
    (HERE / ("meta_" + a.pass_ + ".json")).write_text(json.dumps(meta), encoding="utf-8", newline="\n")
    rows, name = (counts, "counts.csv") if a.pass_ == "count" else (out, "dev_cells.csv")
    if a.pass_ == "dev":
        fam = [r for r in rows if r["arm"] in ARMS and "p" in r]
        adj = rk.holm([r["p"] for r in fam], m=M_HOLM)
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
    cols = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("tf", "arm"), k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(line, meta)
    if a.pass_ == "count":
        for c in counts:
            print(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
