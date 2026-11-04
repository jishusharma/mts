"""wt_extreme_cross_2026-11: WaveTrend extreme-cross bounce/drop size on 1m vs 5m vs 15m, by day type and HTF trend. DEV only.

Card wt-1m-extreme-cross-bounce-size-after-cr (EAGLE_EYES_BIBLE lesson 8). Buy event = wt1 crosses above wt2 with wt1 <= -50;
sell event = wt1 crosses below wt2 with wt1 >= +40. Entry at the event bar close; outcome over the next K bars:
MFE (bounce/drop size), MAE, close-to-close return, fee-net return. Baseline = the same K-bar MFE / return from every bar
close (same side), so "bounce size" is read against the unconditional excursion. WT = research/wavetrend_2026-10-17/
wt_parity_ref.py (pinned). HTF = research_kit.regime_tag (as-of). Day type = fabio v3 TREND_RATIO rule on the UTC day:
'same' (ex-post, the operator's description, NOT tradable) and 'prior' (as-of, the previous UTC day). Times are UTC ms.
"""
import csv
import importlib.util
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
from MyTradingSys.backtest.layers.fabio.v3.day_gates import TREND_RATIO  # noqa: E402  (0.6, fabio spec P41, SIM)

DAY = 86400000
BUY_LVL = -50.0              # SOURCED card (operator): cross up from below -50
SELL_LVL = 40.0              # SOURCED card / bible lesson 8 (operator): cross down from above +40
BUY_LVL_BIBLE = -60.0        # SOURCED bible lesson 8 (operator 11-02 16:33Z: "-60 zone"), sensitivity row
K = 10                       # SOURCED bible lesson 8: "bounce of 100-250 points within 5-10 bars"; 10 = upper end (OURS pick)
COST = rk.TAKER_RT_PCT       # 0.14 % round trip, SOURCED research_kit
WARMUP = 200                 # SOURCED-in-repo PARITY_CONTRACT s3
BASE_STRIDE = 7              # OURS: baseline samples every 7th bar (cuts 1m baseline cost; unbiased in time)
TFS = ("1m", "5m", "15m")
TF_MS = {"1m": 60000, "5m": 300000, "15m": 900000}
DATA_ROOTS = ("F:/MTS/Dumps/backtest/raw_1m_2019", "F:/MTS/Dumps/backtest/raw_1m_2022", "F:/MTS/Dumps/backtest/raw")
KEYS = ("tf", "side", "lvl", "daytag", "htf")


def ms(ts):
    return int(ts.tz_localize(timezone.utc).timestamp() * 1000)


def _wt():
    spec = importlib.util.spec_from_file_location("wt_parity_ref", REPO / "MyTradingSys/research/wavetrend_2026-10-17/wt_parity_ref.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extreme_crosses(wt1, wt2, buy_lvl=BUY_LVL, sell_lvl=SELL_LVL):
    """[(bar, side)]: +1 = wt1 crosses above wt2 with wt1 <= buy_lvl; -1 = crosses below with wt1 >= sell_lvl (closed bars)."""
    ev = _wt().cross_events(wt1, wt2, "le")
    out = []
    for i, e in enumerate(ev):
        if e == 1 and wt1[i] <= buy_lvl:
            out.append((i, 1))
        elif e == -1 and wt1[i] >= sell_lvl:
            out.append((i, -1))
    return out


def events_for(bars, tf, buy_lvl=BUY_LVL):
    wt1, wt2 = _wt().wavetrend([b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars])
    return [{"i": i, "side": s, "t_close": bars[i]["t"] + TF_MS[tf]}
            for i, s in extreme_crosses(wt1, wt2, buy_lvl) if i >= WARMUP]


def dev_guard(bars):
    """SplitViolation unless every scored bar (events and their outcome windows) lies inside DEV."""
    import pandas as pd
    lo, hi = min(b["t"] for b in bars), max(b["t"] for b in bars)
    splits.assert_dev_only(pd.Timestamp(lo, unit="ms"), pd.Timestamp(hi, unit="ms"))


def outcome(bars, i, side, k=K):
    """Entry at bar i close; bars i+1..i+k. mfe/mae/ret in % of entry (side-signed); pts = mfe in price units; None if short."""
    if i + k >= len(bars):
        return None
    px = bars[i]["c"]
    hi = max(b["h"] for b in bars[i + 1:i + k + 1])
    lo = min(b["l"] for b in bars[i + 1:i + k + 1])
    end = bars[i + k]["c"]
    up, dn = (hi - px) / px * 100.0, (px - lo) / px * 100.0
    mfe, mae = (up, dn) if side > 0 else (dn, up)
    ret = side * (end - px) / px * 100.0
    return {"mfe": mfe, "mae": mae, "ret": ret, "net": ret - COST, "pts": mfe * px / 100.0}


def day_types(bars_1m):
    """{utc_day: 'trend'|'range'}: trend iff |last close - first open| / (high - low) >= TREND_RATIO over the UTC day."""
    agg = {}
    for b in bars_1m:
        d = int(b["t"] // DAY)
        a = agg.get(d)
        if a is None:
            agg[d] = [b["o"], b["h"], b["l"], b["c"]]
        else:
            a[1] = max(a[1], b["h"])
            a[2] = min(a[2], b["l"])
            a[3] = b["c"]
    out = {}
    for d, (o, h, l, c) in agg.items():
        out[d] = "trend" if h > l and abs(c - o) / (h - l) >= TREND_RATIO else "range"
    return out


def same_day_type(types, t_ms):
    return types.get(int(t_ms // DAY))         # ex-post: uses the whole day (description only)


def prior_day_type(types, t_ms):
    return types.get(int(t_ms // DAY) - 1)     # as-of: previous UTC day, closed before t


def make_ctx_at(daily, weekly_rsi, monthly_rsi):
    cache = {}

    def ctx_at(t):
        d = int(t // DAY)
        if d not in cache:
            cache[d] = rk.regime_tag(d * DAY, daily, weekly_rsi, monthly_rsi)
        return cache[d]
    return ctx_at


def htf_label(ctx, side):
    if ctx["side"] is None:
        return None
    return "with" if (ctx["side"] == "above") == (side > 0) else "against"


def _arrays(bars):
    return (np.array([b["h"] for b in bars]), np.array([b["l"] for b in bars]), np.array([b["c"] for b in bars]))


def baseline(bars, tf, lo_ms, hi_ms, side, k=K, stride=BASE_STRIDE):
    """Mean MFE % and mean K-bar return % from every stride-th bar close in [lo, hi) (unconditional, same side)."""
    h, l, c = _arrays(bars)
    t = np.array([b["t"] for b in bars]) + TF_MS[tf]
    n = len(c) - k
    idx = np.arange(0, n, stride)
    idx = idx[(t[idx] >= lo_ms) & (t[idx] < hi_ms)]
    from numpy.lib.stride_tricks import sliding_window_view as sw
    hmax = sw(h[1:], k).max(axis=1)[idx]
    lmin = sw(l[1:], k).min(axis=1)[idx]
    px = c[idx]
    mfe = (hmax - px) / px * 100.0 if side > 0 else (px - lmin) / px * 100.0
    ret = side * (c[idx + k] - px) / px * 100.0
    return float(mfe.mean()), float(np.median(mfe)), float(ret.mean())


def cell(rows, base):
    if not rows:
        return {"n": 0, "days": 0}
    mfe = np.array([r["mfe"] for r in rows])
    net = np.array([r["net"] for r in rows])
    day = [r["day"] for r in rows]
    m, se = rk.cluster_mean_se(net, day)
    mm, mse = rk.cluster_mean_se(mfe - base[0], day)
    return {"n": len(rows), "days": len(set(day)), "mfe_mean": float(mfe.mean()), "mfe_med": float(np.median(mfe)),
            "pts_med": float(np.median([r["pts"] for r in rows])), "mae_mean": float(np.mean([r["mae"] for r in rows])),
            "ret_mean": float(np.mean([r["ret"] for r in rows])), "net_mean": m, "net_t": rk.t_stat(m, se),
            "hit_net": float((net > 0).mean()), "base_mfe": base[0], "base_ret": base[2],
            "mfe_excess": mm, "mfe_excess_t": rk.t_stat(mm, mse)}


def load_1m(end_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = {}
    for r in DATA_ROOTS:
        for b in load_klines(r, end_ms=end_ms):
            bars[b["t"]] = b
    return [bars[k] for k in sorted(bars)]


def rsi_series(bars):
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    r = rsi_core([x["c"] for x in bars], 14)
    keep = [k for k in range(len(bars) - 1) if r[k] is not None]
    return [bars[k + 1]["t"] for k in keep], [r[k] for k in keep]


def week_starts(lo_ms, hi_ms):
    d0 = int(lo_ms // DAY)
    d0 += (4 - d0) % 7
    return [d * DAY for d in range(d0, int(hi_ms // DAY), 7)]


def main():
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    lo_ms, hi_ms = ms(splits.DEV_START), ms(splits.DEV_END)
    bars_1m = load_1m(hi_ms)                     # context history before DEV is read; nothing at/after DEV_END
    assert bars_1m[-1]["t"] < hi_ms
    d = resample(bars_1m, "1d", registry)
    ctx_at = make_ctx_at(([x["t"] + DAY for x in d], [x["c"] for x in d]),
                         rsi_series(resample(bars_1m, "1w", registry)), rsi_series(resample(bars_1m, "1M", registry)))
    types = day_types([b for b in bars_1m if b["t"] >= lo_ms - DAY])
    out = []
    for tf in TFS:
        bars = bars_1m if tf == "1m" else resample(bars_1m, tf, registry)
        for lvl_name, lvl in (("card", BUY_LVL), ("bible60", BUY_LVL_BIBLE)):
            evs = [e for e in events_for(bars, tf, lvl) if lo_ms <= e["t_close"] < hi_ms]
            if lvl_name == "bible60":
                evs = [e for e in evs if e["side"] > 0]
            rows = []
            for e in evs:
                o = outcome(bars, e["i"], e["side"])
                if o is None:
                    continue
                o.update(side=e["side"], day=int(e["t_close"] // DAY), same=same_day_type(types, e["t_close"]),
                         prior=prior_day_type(types, e["t_close"]), htf=htf_label(ctx_at(e["t_close"]), e["side"]))
                o["regime"] = ctx_at(e["t_close"])["regime"]
                rows.append(o)
            scored = [bars[e["i"]] for e in evs] + [bars[min(e["i"] + K, len(bars) - 1)] for e in evs]
            dev_guard(scored)
            for sname, sgn in (("buy", 1), ("sell", -1)):
                if lvl_name == "bible60" and sgn < 0:
                    continue
                base = baseline(bars, tf, lo_ms, hi_ms, sgn)
                rs = [r for r in rows if r["side"] == sgn]
                for daytag in ("all", "same_range", "same_trend", "prior_range", "prior_trend"):
                    rd = rs if daytag == "all" else [r for r in rs if r[daytag.split("_")[0]] == daytag.split("_")[1]]
                    for htf in ("all", "with", "against"):
                        rh = rd if htf == "all" else [r for r in rd if r["htf"] == htf]
                        row = dict(zip(KEYS, (tf, sname, lvl_name, daytag, htf)))
                        row.update(cell(rh, base))
                        out.append(row)
        print(tf, "done", file=sys.stderr, flush=True)
    cols = sorted({k for r in out for k in r}, key=lambda k: (k not in KEYS, k))
    with open(HERE / "dev_cells.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    line = rk.regime_mix_line([ctx_at(t)["regime"] for t in week_starts(lo_ms, hi_ms)])
    (HERE / "regime_mix_dev.txt").write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
