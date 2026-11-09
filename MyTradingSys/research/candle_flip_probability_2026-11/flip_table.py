"""Per timeframe, per minute inside each bar: d, t_left, HTF pair, session, BB position, outcome (both colour definitions).

    python flip_table.py            # reads klines_1m_cache.csv.gz (fetch_1m.py), writes flip_table.csv.gz (gitignored) + counts.csv

Definitions are frozen in PRE_REG.md. `tf_rows()` is a pure function of dense 1m arrays, so the tests can feed it a simulated walk.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
START_MS = 1704067200000   # 2024-01-01T00:00Z, a Monday: every bar tiles forward from here (OURS)
CUT_MS = 1735689600000     # 2025-01-01T00:00Z: fit bars close <= CUT, score bars open >= CUT
MIN_MS = 60000
SIGMA_K = 2.0 * math.sqrt(2.0 / math.pi)   # expected range of a Brownian motion in sd units, 1.5958 (SOURCED)
POINTS = 6          # evaluation points per bar, OURS
MAX_ROWS = 100_000  # per timeframe, OURS (19 timeframes -> 1.9M <= 2M)
WARM = 20           # complete prior bars needed (ATR14 and Bollinger 19 prior closes)
TF_MIN = {"1w": 10080, "5d": 7200, "3d": 4320, "2d": 2880, "1d": 1440, "12h": 720, "8h": 480, "7h": 420, "6h": 360, "4h": 240,
          "3h": 180, "2h": 120, "1h": 60, "30m": 30, "15m": 15, "10m": 10, "5m": 5, "3m": 3, "2m": 2, "1m": 1}
GROUPS = {"G1 1m-15m": ["15m", "10m", "5m", "3m", "2m", "1m"],
          "G2 30m-4h": ["4h", "3h", "2h", "1h", "30m"],
          "G3 6h-1d": ["1d", "12h", "8h", "7h", "6h"],
          "G4 2d-1w": ["1w", "5d", "3d", "2d"]}
SESSIONS = ("Asia", "EU", "US")   # 00-08, 08-13, 13-21 UTC; 21-24 = late, outside the 12 cells
_erf = np.frompyfunc(math.erf, 1, 1)


def phi(x):
    """Standard normal CDF, exact via math.erf, array in -> array out."""
    x = np.asarray(x, float)
    return 0.5 * (1.0 + np.asarray(_erf(x / math.sqrt(2.0)), dtype=float))


def offsets(S, points=POINTS):
    """Minute offsets j (0..S-2) inside a bar of S minutes at elapsed fractions k/(P+1); the price is the close of 1m bar j."""
    if S < 2:
        return np.array([], int)
    P = min(S - 1, points)
    j = np.round(S * np.arange(1, P + 1) / (P + 1)).astype(int) - 1
    return np.unique(np.clip(j, 0, S - 2))


def tf_rows(o, h, l, c, S, t0_ms=START_MS, cut_ms=CUT_MS, max_rows=MAX_ROWS, points=POINTS, seed=None, tf="?"):
    """Rows for one timeframe from dense 1m arrays starting at t0 (no gaps). Returns a DataFrame (empty for S < 2)."""
    o, h, l, c = (np.asarray(x, float) for x in (o, h, l, c))
    J = offsets(S, points)
    nb = len(c) // S
    if len(J) == 0 or nb <= WARM + 1:
        return pd.DataFrame()
    O = o[:nb * S].reshape(nb, S)
    H = h[:nb * S].reshape(nb, S).max(1)
    L = l[:nb * S].reshape(nb, S).min(1)
    C = c[:nb * S].reshape(nb, S)
    bo, bc = O[:, 0], C[:, -1]
    # true range per bar, ATR14 as of bar b = mean TR of bars b-14..b-1 (complete bars only)
    tr = np.empty(nb)
    tr[0] = H[0] - L[0]
    tr[1:] = np.maximum.reduce([H[1:] - L[1:], np.abs(H[1:] - bc[:-1]), np.abs(L[1:] - bc[:-1])])
    cs = np.concatenate([[0.0], np.cumsum(tr)])
    atr = np.full(nb, np.nan)
    atr[14:] = (cs[14:nb] - cs[0:nb - 14]) / 14.0
    # 19 prior closes, centred for numeric stability
    m0 = float(bc[0])   # centring constant only (cancels exactly in mean/var); the first close, so no later information is even nominally used
    z = bc - m0
    c1 = np.concatenate([[0.0], np.cumsum(z)])
    c2 = np.concatenate([[0.0], np.cumsum(z * z)])
    s19 = np.full(nb, np.nan)
    q19 = np.full(nb, np.nan)
    s19[19:] = c1[19:nb] - c1[0:nb - 19]
    q19[19:] = c2[19:nb] - c2[0:nb - 19]
    b_idx = np.arange(nb)
    b_open_ms = t0_ms + b_idx * S * MIN_MS
    b_close_ms = b_open_ms + S * MIN_MS
    win = np.where(b_close_ms <= cut_ms, 0, np.where(b_open_ms >= cut_ms, 1, -1))   # 0 fit, 1 score, -1 straddles the cut (dropped)
    ok = (b_idx >= WARM) & (win >= 0) & np.isfinite(atr) & (atr > 0)
    sel = b_idx[ok]
    if len(sel) * len(J) > max_rows:
        rng = np.random.default_rng(1106 + S if seed is None else seed)
        sel = np.sort(rng.choice(sel, size=max_rows // len(J), replace=False))
    B = np.repeat(sel, len(J))
    Jf = np.tile(J, len(sel))
    g = B * S + Jf                                  # index of the 1m bar whose close is the price
    price = c[g]
    open_ = bo[B]
    pc = bc[B - 1]
    close = bc[B]
    sigma = atr[B] / SIGMA_K
    t_left = 1.0 - (Jf + 1.0) / S
    d_open = (price - open_) / sigma
    d_pc = (price - pc) / sigma
    y_open = ((price - open_) * (close - open_) > 0).astype(np.int8)
    y_pc = ((price - pc) * (close - pc) > 0).astype(np.int8)
    p0_open = phi(np.abs(d_open) / np.sqrt(t_left))
    p0_pc = phi(np.abs(d_pc) / np.sqrt(t_left))
    # Bollinger(20, 2) on own timeframe: 19 prior closes + the current price
    zp = price - m0
    mean = (s19[B] + zp) / 20.0
    var = (q19[B] + zp * zp) / 20.0 - mean * mean
    sd = np.sqrt(np.maximum(var, 0.0))
    at_band = (sd > 0) & ((zp >= mean + 2 * sd) | (zp <= mean - 2 * sd))
    # HTF: forming 1d and 1w candle colours at the evaluation minute
    day_open = o[(g // 1440) * 1440]
    week_open = o[(g // 10080) * 10080]
    cd, cw = np.sign(price - day_open), np.sign(price - week_open)
    aligned = (cd == cw) & (cd != 0)
    own = tf in ("1d", "1w")   # amendment A2 (REVIEW.md #5): for a 1d or 1w row one of the two colours IS the row's own colour, so the HTF cell is undefined: label "na"
    hr = ((g + 1) % 1440) // 60                     # session of the evaluation minute CLOSE time
    sess = np.where(hr < 8, 0, np.where(hr < 13, 1, np.where(hr < 21, 2, 3))).astype(np.int8)
    keep = (price != open_) & (price != pc) & (sd > 0)
    df = pd.DataFrame({
        "tf": tf, "bar_ms": b_open_ms[B], "j": Jf, "t_left": t_left, "d_open": d_open, "d_pc": d_pc,
        "htf": "na" if own else np.where(aligned, "aligned", "split"), "sess": sess, "bb": np.where(at_band, "at", "inside"),
        "y_open": y_open, "y_pc": y_pc, "p0_open": p0_open, "p0_pc": p0_pc, "win": np.where(win[B] == 0, "fit", "score"),
    })
    return df[keep].reset_index(drop=True)


def load_1m(path):
    d = pd.read_csv(path)
    t = d["open_time_ms"].values
    n = (t[-1] - t[0]) // MIN_MS + 1
    if t[0] != START_MS or n != len(t) or (np.diff(t) != MIN_MS).any():
        raise SystemExit("1m cache has gaps or does not start at the anchor: refetch")
    return d["open"].values, d["high"].values, d["low"].values, d["close"].values, int(t[-1])


def main():
    o, h, l, c, last_ms = load_1m(HERE / "klines_1m_cache.csv.gz")
    frames, bars = [], {}
    for tf, S in TF_MIN.items():
        df = tf_rows(o, h, l, c, S, tf=tf)
        bars[tf] = len(c) // S
        if len(df):
            frames.append(df)
        print(tf, S, "complete bars", bars[tf], "rows", len(df), flush=True)
    tab = pd.concat(frames, ignore_index=True)
    assert len(tab) <= 2_000_000, len(tab)
    for col in ("d_open", "d_pc", "t_left", "p0_open", "p0_pc"):
        tab[col] = tab[col].round(6)
    tab.to_csv(HERE / "flip_table.csv.gz", index=False, lineterminator="\n")
    fam = tab[tab["sess"] < 3].copy()
    fam["session"] = fam["sess"].map(dict(enumerate(SESSIONS)))
    fam["bar"] = fam["tf"] + "|" + fam["bar_ms"].astype(str)
    cnt = fam.groupby(["tf", "win", "htf", "session", "bb"]).agg(rows=("y_open", "size"), bars=("bar", "nunique")).reset_index()
    cnt.to_csv(HERE / "counts.csv", index=False, lineterminator="\n")
    summ = tab.groupby(["tf", "win"]).size().rename("rows").reset_index()
    print(summ.to_string())
    print("total rows", len(tab), "last 1m bar open ms", last_ms)


if __name__ == "__main__":
    sys.exit(main())
