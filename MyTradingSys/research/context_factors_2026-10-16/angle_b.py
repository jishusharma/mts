"""Angle b (trader's eye): 12 seeded DEV decision hours, raw chart view rebuilt from the 1m archive directly (not from the
5m tape or any builder), printed next to the vectorised builder row. Prints compact lines; the prose is in ANGLES.md.

  python angle_b.py [seed]     (default seed 20261016)
"""
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
import context_asof as C  # noqa: E402

DAY, HOUR = C.DAY, C.HOUR


def load_1m(T):
    """1m bars from 130 days before T up to T (open < T), straight from the monthly CSVs."""
    lo = T - 130 * DAY
    parts = []
    for ym in C._months():
        y, m = map(int, ym.split("-"))
        ms = int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000)
        if ms > T or ms + 32 * DAY < lo:
            continue
        f = C.KLINE_DIR / f"BTCUSDT-1m-{ym}.csv"
        first = f.open().readline()
        d = pd.read_csv(f, header=0 if first.startswith("open_time") else None, usecols=range(6))
        d.columns = ["ot", "o", "h", "l", "c", "v"]
        parts.append(d)
    d = pd.concat(parts).drop_duplicates("ot").sort_values("ot")
    return d[(d.ot >= lo) & (d.ot < T)].reset_index(drop=True)


def candles(d, L, T):
    k = (d.ot // L) * L if L != "W" else C.week_start(d.ot.to_numpy())
    g = d.groupby(k)
    a = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum()})
    length = C.WEEK if L == "W" else L
    done = a[a.index + length <= T]
    part = a[a.index + length > T]
    return done, part


def fmt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def main(seed):
    fl = pd.read_pickle(C.CACHE / "frame_long.pkl")
    fs = pd.read_pickle(C.CACHE / "frame_short.pkl")
    rng = np.random.default_rng(seed)
    pick = np.sort(rng.choice(fl.index.to_numpy(), 12, replace=False))
    for T in pick:
        T = int(T)
        d = load_1m(T)
        c = float(d.c.iloc[-1])
        print(f"\n=== T {fmt(T)} UTC  close {c}")
        for nm, L in (("D", DAY), ("12h", 12 * HOUR), ("8h", 8 * HOUR), ("4h", 4 * HOUR)):
            done, part = candles(d, L, T)
            r = done.iloc[-1]
            pt = f"partial o{part.o.iloc[0]} h{part.h.iloc[0]} l{part.l.iloc[0]}" if len(part) else "partial none"
            print(f" {nm:>3} last closed {fmt(int(done.index[-1]))} o{r.o} h{r.h} l{r.l} c{r.c} | prev o{done.o.iloc[-2]} c{done.c.iloc[-2]} | {pt}")
        wd, _ = candles(d, "W", T)
        print(f"  W  last closed {fmt(int(wd.index[-1]))} h{wd.h.iloc[-1]} l{wd.l.iloc[-1]}")
        dd, _ = candles(d, DAY, T)
        tr = pd.concat([dd.h - dd.l, (dd.h - dd.c.shift()).abs(), (dd.l - dd.c.shift()).abs()], axis=1).max(axis=1)
        atrd = float(tr.iloc[-14:].mean())
        h1, _ = candles(d, HOUR, T)
        tr1 = pd.concat([h1.h - h1.l, (h1.h - h1.c.shift()).abs(), (h1.l - h1.c.shift()).abs()], axis=1).max(axis=1)
        atr1 = float(tr1.iloc[-14:].mean())
        w20 = h1.c.iloc[-20:]
        mid, sd = w20.mean(), w20.std(ddof=0)
        day0 = (T // DAY) * DAY
        s = d[d.ot >= day0]
        vwap1m = float(((s.h + s.l + s.c) / 3 * s.v).sum() / s.v.sum()) if len(s) else float("nan")
        print(f"  1m-direct: ATR14(D) {atrd:.1f} ({atrd / c * 100:.2f} %), ATR14(1h) {atr1:.1f}, 1h BB mid {mid:.1f} "
              f"lo {mid - 2 * sd:.1f} up {mid + 2 * sd:.1f}, session VWAP(1m hlc3) {vwap1m:.1f}")
        for side, f in (("long", fl), ("short", fs)):
            r = f.loc[T]
            print(f"  [{side}] near {r.f1_near_layer} {r.f1_near_px:.1f} dist {r.f1_dist_atr:.2f}ATR conf {r.f2_conf_obj} "
                  f"touch {r.f2_touch_cat} | armed {r.f3_armed} stop {r.f3_stop_tf} {r.f3_stop_pct:.2f}% wD {r.f3_w_D:.2f} "
                  f"w12 {r.f3_w_12h:.2f} w8 {r.f3_w_8h:.2f} wmax {r.f3_wmax:.2f} | D {r.f4_D_cat} 12h {r.f4_12h_cat} "
                  f"8h {r.f4_8h_cat} 4h {r.f4_4h_cat} | bb1h {r.f5_1h} bb4h {r.f5_4h} | phA {r.f6_phaseA} phB {r.f6_phaseB} "
                  f"intra {r.f6_intraday} | atr1h {r.atr1h:.1f}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20261016)
