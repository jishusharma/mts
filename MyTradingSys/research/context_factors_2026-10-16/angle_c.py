"""Angle c (hand arithmetic): raw ingredients for one decision hour, read from the 1m archive (angle_b.load_1m), printed
so each factor can be recomputed by hand in ANGLES.md. Prints the builder row next to them. No builder code is used for
the ingredients.  python angle_c.py ["2022-10-29 01:00"]
"""
import sys
from datetime import datetime, timezone

import pandas as pd

sys.dont_write_bytecode = True
import context_asof as C  # noqa: E402
from angle_b import candles, load_1m  # noqa: E402


def main(ts):
    T = int(datetime.strptime(ts, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp() * 1000)
    d = load_1m(T)
    c = float(d.c.iloc[-1])
    W, _ = candles(d, "W", T)
    D, _ = candles(d, C.DAY, T)
    H4, _ = candles(d, 4 * C.HOUR, T)
    H1, _ = candles(d, C.HOUR, T)
    print("T", ts, "close", c)
    print("last 12 completed weekly closes:", W.c.iloc[-12:].round(1).tolist())
    print("D close now-30 and now:", D.c.iloc[-31], D.c.iloc[-1], "| 90 D low/high:", D.l.iloc[-90:].min(), D.h.iloc[-90:].max())
    print("last 20 4h closes:", H4.c.iloc[-20:].round(1).tolist())
    print("last 20 D closes (SMA20 for HTF align):", D.c.iloc[-20:].round(1).tolist())
    print("last 25 1h closes (ER):", H1.c.iloc[-25:].round(1).tolist())
    print("last 15 D bars (h, l, c) for ATR14(D):", list(zip(D.h.iloc[-15:], D.l.iloc[-15:], D.c.iloc[-15:])))
    day0 = (T // C.DAY) * C.DAY
    s = d[d.ot >= day0]
    print("session so far: high", s.h.max() if len(s) else None, "low", s.l.min() if len(s) else None)
    print("last 4 1h bars (o, h, l, c):", list(zip(H1.o.iloc[-4:], H1.h.iloc[-4:], H1.l.iloc[-4:], H1.c.iloc[-4:])))
    for side in ("long", "short"):
        r = pd.read_pickle(C.CACHE / f"frame_{side}.pkl").loc[T]
        print(f"[{side}]", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ("T", "side")})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2022-10-29 01:00")
