"""Library for the imbalance filter on the lc-levels-hold level layer (PRE_REG.md in this folder; DEV only).

Pure functions, tested by hand-built cases in test_filter_join.py:
  - the causal join "was there a closed volume-anomaly candle at this price before this touch" (imbalance_flags / attach_flags),
  - the layer trade (first touch, fade side from the previous bar's close, bracket with stop first, net R after fees),
  - the DEV guard (no bar with open >= 2024-07-01 is ever loaded),
  - level blocks that equal one long window (levels.py is quadratic in the number of days, so it is called per block),
  - the pre-registered statistics and decisions (stats, holm_p, decide_h1, decide_h2).
Every threshold is OURS and is fixed in PRE_REG.md before any outcome; the detector (relative volume, body fraction, windows,
midpoint tolerance) is imb.py's, unchanged.
"""
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
for _p in (HERE.parent, REPO / "MyTradingSys" / "research" / "levels_confluence_2026-10-14", REPO / "MyTradingSys" / "backtest"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import imb  # noqa: E402  (detector: resample, rel_volume, body_frac, LOOKBACK_DAYS, TOL_MID, _read_kline_csv)
import levels as lv  # noqa: E402  (lc level builder, unchanged)
import levels_hold  # noqa: E402  (LC1 stop_width)
import research_kit as RK  # noqa: E402

DAY = 86_400_000
MIN_MS = 60_000
DEV_END_MS = pd.Timestamp("2024-07-01").value // 10**6          # first ms that is NOT DEV
FIRST_DAY = pd.Timestamp("2022-04-01").value // 10**6 // DAY      # decisions start (90-day warmup)
LAST_DAY = (DEV_END_MS - 1) // DAY                                # 2024-06-30
H2_START_DAY = pd.Timestamp("2023-04-01").value // 10**6 // DAY   # stability halves: H1 < this <= H2

KEEP = ("prior_day_high", "prior_day_low", "prior_day_poc", "naked_poc", "4h_fractal_low", "4h_fractal_high",
        "round_1000", "prior_week_high")                          # LC1 KEEP families (levels_hold.md)
TFS = ("1h", "4h", "12h", "1d")
K_PRIMARY, K_SENS = 2.0, 3.0
SMALL_BODY, LARGE_BODY, NORMAL_VOL = imb.SMALL_BODY, imb.LARGE_BODY, imb.NORMAL_VOL
TAKER_SIDE = 0.0005 + 0.0002        # taker fee (backtest/fees.py BINANCE_TAKER) + 2 bp slippage per leg
MAKER_SIDE = 0.0002                 # BINANCE_MAKER, no slippage (filled only by trade-through; readout only)
N_MIN, DAYS_MIN, T_MIN, ALPHA, MDE_BAR, HOLM_M = 200, 100, 2.0, 0.05, 0.15, 16
MIN_BARS_DAY = 1400                 # session_levels.py convention: a day with fewer 1m bars is skipped


# ------------------------------------------------------------------ DEV guard and loading
def dev_month_files(names):
    """The 1m month files with YYYY-MM <= 2024-06, sorted. Later files are never opened."""
    out = []
    for n in names:
        m = re.fullmatch(r"BTCUSDT-1m-(\d{4})-(\d{2})\.csv", n)
        if m and (int(m.group(1)), int(m.group(2))) <= (2024, 6):
            out.append(n)
    return sorted(out)


def assert_dev(t):
    t = np.asarray(t)
    if len(t) and int(t.max()) >= DEV_END_MS:
        raise ValueError(f"bar open {int(t.max())} is at or after 2024-07-01: DEV only")


def load_dev_1m(root=None):
    root = Path(root or imb.KLINES_1M)
    names = dev_month_files(os.listdir(root))
    df = pd.concat([imb._read_kline_csv(root / n) for n in names]).drop_duplicates("t").sort_values("t").reset_index(drop=True)
    assert_dev(df.t.to_numpy())
    return df


# ------------------------------------------------------------------ imbalance candles and the join
def candle_table(df1m, tf):
    """Closed TF candles with start, end, mid, rv (volume / median of the prior 50 bars), bf (body fraction), h, l."""
    b = imb.resample(df1m, tf)
    return pd.DataFrame({"start": b.t.to_numpy(), "end": b.t.to_numpy() + imb.TF_MS[tf], "mid": ((b.h + b.l) / 2).to_numpy(),
                         "rv": imb.rel_volume(b.v), "bf": imb.body_frac(b.o, b.h, b.l, b.c), "h": b.h.to_numpy(), "l": b.l.to_numpy()})


def _np(tbl):
    c = tbl.attrs.get("_np")
    if c is None:
        c = {k: tbl[k].to_numpy(dtype=float) for k in ("start", "end", "mid", "rv", "bf")} if len(tbl) else None
        tbl.attrs["_np"] = c if c is not None else {}
    return tbl.attrs["_np"] or None


def imbalance_flags(tables, touch_t, level, k):
    """Flags at a touch bar opening at touch_t for a level price. Only candles that CLOSED at or before touch_t (end <= touch_t)
    and opened within imb.LOOKBACK_DAYS[tf] before it count; 'at the level' = candle midpoint within imb.TOL_MID of the level.
    small: rv >= k and bf <= SMALL_BODY; large: rv >= k and bf >= LARGE_BODY; ctrl: rv < NORMAL_VOL and bf <= SMALL_BODY."""
    small_tf, large, ctrl = {}, False, False
    for tf in TFS:
        a = _np(tables[tf]) if len(tables[tf]) else None
        small_tf[tf] = False
        if a is None:
            continue
        hi = int(np.searchsorted(a["end"], touch_t, side="right"))
        lo = int(np.searchsorted(a["start"], touch_t - imb.LOOKBACK_DAYS[tf] * DAY, side="left"))
        if lo >= hi:
            continue
        sl = slice(lo, hi)
        at = np.abs(a["mid"][sl] - level) / level <= imb.TOL_MID
        with np.errstate(invalid="ignore"):
            rv, bf = a["rv"][sl], a["bf"][sl]
            small_tf[tf] = bool((at & (rv >= k) & (bf <= SMALL_BODY)).any())
            large = large or bool((at & (rv >= k) & (bf >= LARGE_BODY)).any())
            ctrl = ctrl or bool((at & (rv < NORMAL_VOL) & (bf <= SMALL_BODY)).any())
    return {"small": any(small_tf.values()), "large": large, "ctrl": ctrl, "small_tf": small_tf}


def attach_flags(trades, tables, k, suffix=""):
    """trades needs columns t (touch bar open, ms) and level; returns a copy with small/large/ctrl and small_<tf> columns."""
    rows = [imbalance_flags(tables, int(t), float(p), k) for t, p in zip(trades["t"], trades["level"])]
    out = trades.copy().reset_index(drop=True)
    out[f"small{suffix}"] = [r["small"] for r in rows]
    out[f"large{suffix}"] = [r["large"] for r in rows]
    out[f"ctrl{suffix}"] = [r["ctrl"] for r in rows]
    for tf in TFS:
        out[f"small{suffix}_{tf}"] = [r["small_tf"][tf] for r in rows]
    return out


# ------------------------------------------------------------------ the layer trade
def fade_side(prev_close, level):
    """+1 long (price came from above, level is support), -1 short (came from below), 0 ambiguous."""
    return 1 if prev_close > level else (-1 if prev_close < level else 0)


def stop_width_for(day_open, level):
    return levels_hold.stop_width(day_open, level)


def day_complete(n_today, n_prior):
    return n_today >= MIN_BARS_DAY and n_prior >= MIN_BARS_DAY


def first_touch(t, o, h, l, c, level, prev_close):
    """First bar of the day with low <= level <= high. Side from the close of the bar BEFORE it (prev_close for bar 0)."""
    hit = np.flatnonzero((np.asarray(l) <= level) & (level <= np.asarray(h)))
    if len(hit) == 0:
        return None
    i = int(hit[0])
    side = fade_side(float(c[i - 1]) if i > 0 else float(prev_close), level)
    if side == 0:
        return None
    return {"idx": i, "t": int(t[i]), "side": side}


def bracket(side, level, width, rr, o, h, l, c):
    """Arrays start at the touch bar. stop = level - side x W, target = level + side x rr x W. Touch bar: only the stop can be hit
    (a move to the target there may precede the fill). Later bars: stop first when one bar holds both; a bar opening beyond the stop
    fills at its open; a target is filled at its price. No hit: exit at the last close. Returns (exit_price, 'stop'|'target'|'time')."""
    o, h, l, c = (np.asarray(x, dtype=float) for x in (o, h, l, c))
    n = len(h)
    stop = level - side * width
    target = level + side * rr * width
    adverse = (l <= stop) if side > 0 else (h >= stop)
    fav = (h >= target) if side > 0 else (l <= target)
    fav[0] = False
    ja = int(np.argmax(adverse)) if adverse.any() else n
    jf = int(np.argmax(fav)) if fav.any() else n
    if ja == n and jf == n:
        return float(c[-1]), "time"
    if ja <= jf:
        px = stop
        if ja > 0 and ((side > 0 and o[ja] <= stop) or (side < 0 and o[ja] >= stop)):
            px = float(o[ja])
        return float(px), "stop"
    return float(target), "target"


def net_r(side, level, width, exit_px, maker_in=False):
    """(gross_R, cost_R, net_R) of a trade entered at `level` and exited at `exit_px`; R = width."""
    gross = side * (exit_px - level) / width
    cost = ((MAKER_SIDE * level + TAKER_SIDE * exit_px) if maker_in else TAKER_SIDE * (level + exit_px)) / width
    return gross, cost, gross - cost


def dedup_levels(rows):
    """One row per price (e.g. prior_day_poc = naked_poc); families joined with '|' in first-seen order."""
    out, at = [], {}
    for r in rows:
        key = round(float(r["price"]), 8)
        if key in at:
            out[at[key]]["family"] += "|" + r["family"]
        else:
            at[key] = len(out)
            out.append(dict(r))
    return out


def levels_blocks(df1m, first_day, last_day, keep, block=30, history=15):
    """{day: KEEP-family level rows} for first_day..last_day. levels.levels_by_day costs O(days^2), so it is called per block of
    `block` target days with `history` days of earlier bars (13 days is the longest reach: prior week; 10: naked POC, fractals)."""
    t = df1m.t.to_numpy()
    day = t // DAY
    out = {}
    d = first_day
    while d <= last_day:
        d1 = min(d + block - 1, last_day)
        sub = df1m[(day >= d - history) & (day <= d1)]
        got = lv.levels_by_day(sub[["t", "o", "h", "l", "c", "v"]].to_dict("records"))
        for dd in range(d, d1 + 1):
            out[dd] = [x for x in got.get(dd, []) if x["family"] in keep]
        d = d1 + 1
    return out


def build_events(df1m, first_day=FIRST_DAY, last_day=LAST_DAY, keep=KEEP, block=30, levels=None):
    """One row per first touch of a (deduplicated) KEEP level, no outcome. Returns (events, skips)."""
    assert_dev(df1m.t.to_numpy())
    t, o, h, l, c = (df1m[x].to_numpy() for x in ("t", "o", "h", "l", "c"))
    day = t // DAY
    starts = np.searchsorted(day, np.arange(first_day - 1, last_day + 2))      # start index of each day (day - (first_day-1))
    if levels is None:
        levels = levels_blocks(df1m, first_day, last_day, keep, block=block)
    rows, skips = [], {"incomplete_day": 0, "ambiguous_side": 0, "levels": 0, "touched": 0}
    for d in range(first_day, last_day + 1):
        a, b = starts[d - first_day + 1], starts[d - first_day + 2]
        n_prior = starts[d - first_day + 1] - starts[d - first_day]
        if not day_complete(b - a, n_prior):
            skips["incomplete_day"] += 1
            continue
        prev_close = float(c[a - 1])
        day_open = float(o[a])
        for lev in dedup_levels(levels.get(d, [])):
            skips["levels"] += 1
            px = float(lev["price"])
            ft = first_touch(t[a:b], o[a:b], h[a:b], l[a:b], c[a:b], px, prev_close)
            if ft is None:
                if ((l[a:b] <= px) & (px <= h[a:b])).any():
                    skips["ambiguous_side"] += 1
                continue
            skips["touched"] += 1
            rows.append({"day": d, "t": ft["t"], "gidx": a + ft["idx"], "eidx": b, "family": lev["family"], "level": px,
                         "side": ft["side"], "width": stop_width_for(day_open, px)})
    ev = pd.DataFrame(rows, columns=["day", "t", "gidx", "eidx", "family", "level", "side", "width"])
    ev["w_pct"] = ev["width"] / ev["level"] * 100
    return ev, skips


def simulate(events, df1m, rrs=(1.0, 2.0)):
    """Adds exit/kind/gross/cost/net (taker both legs) and net_m (maker entry readout) per rr. Needs events from build_events."""
    o, h, l, c = (df1m[x].to_numpy() for x in ("o", "h", "l", "c"))
    cols = {}
    for rr in rrs:
        res = [bracket(int(s), float(p), float(w), rr, o[i:e], h[i:e], l[i:e], c[i:e])
               for s, p, w, i, e in zip(events["side"], events["level"], events["width"], events["gidx"], events["eidx"])]
        exit_px = np.array([r[0] for r in res])
        nr = [net_r(int(s), float(p), float(w), x) for s, p, w, x in zip(events["side"], events["level"], events["width"], exit_px)]
        nm = [net_r(int(s), float(p), float(w), x, maker_in=True)[2] for s, p, w, x in zip(events["side"], events["level"], events["width"], exit_px)]
        cols[f"exit_{rr:g}"] = exit_px
        cols[f"kind_{rr:g}"] = [r[1] for r in res]
        cols[f"gross_{rr:g}"] = [r[0] for r in nr]
        cols[f"cost_{rr:g}"] = [r[1] for r in nr]
        cols[f"net_{rr:g}"] = [r[2] for r in nr]
        cols[f"net_m_{rr:g}"] = nm
    return events.assign(**cols)


# ------------------------------------------------------------------ statistics and the pre-registered decisions
def stats(values, days):
    v = np.asarray(values, dtype=float)
    mean, se = RK.cluster_mean_se(v, days)
    return {"n": len(v), "days": int(len(np.unique(np.asarray(days)))) if len(v) else 0, "mean": mean, "se": se, "t": RK.t_stat(mean, se)}


def diff_stats(va, da, vb, db):
    d, se = RK.cluster_diff(va, da, vb, db)
    t = RK.t_stat(d, se)
    return {"diff": d, "se": se, "t": t, "p": RK.norm_p_two(t), "mde": RK.mde(se)}


def holm_p(p, m=HOLM_M):
    return [float(x) for x in RK.holm(p, m=m)]


def _pos(x):
    return x == x and x > 0


def decide_h1(s):
    """PRE_REG section 4, H1. s: n_imb, n_noimb, days_imb, mean_imb, t_imb, delta, p_holm, delta_h1, delta_h2, mean_ctrl, mde."""
    if s["n_imb"] < N_MIN or s["n_noimb"] < N_MIN or s["days_imb"] < DAYS_MIN:
        return "INCONCLUSIVE", "n gate"
    b = s["mean_imb"] > 0 and s["t_imb"] >= T_MIN
    c = s["delta"] > 0 and s["p_holm"] <= ALPHA
    d = s["delta_h1"] > 0 and s["delta_h2"] > 0
    e = s["mean_ctrl"] == s["mean_ctrl"] and s["mean_imb"] > s["mean_ctrl"]
    if b and c and d and e:
        return "PASS", ""
    if s["mde"] > MDE_BAR:
        return "INCONCLUSIVE", "underpowered"
    return "FAIL", "filter lifts" if (c and d and not b) else "no lift"


def decide_h2(s):
    """PRE_REG section 4, H2. s: n_large, delta, p_holm, delta_h1, delta_h2, mde."""
    if s["n_large"] < N_MIN:
        return "INCONCLUSIVE", "n gate"
    if s["delta"] < 0 and s["p_holm"] <= ALPHA and s["delta_h1"] < 0 and s["delta_h2"] < 0:
        return "PASS", ""
    if s["mde"] > MDE_BAR:
        return "INCONCLUSIVE", "underpowered"
    return "FAIL", "no veto effect"
