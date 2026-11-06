"""Pre-US failed-break short, DEV run pooled on 10 USD-M symbols. Rule = research/pre_us_failed_break_2026-10/PRE_REG.md s2-7, unchanged.
See PRE_REG.md here. Passes: `count` (signals only, no return column ever built) and `dev` (one run, every cell printed).
Missing 1m bars are never filled: a day without all bars 00:00..13:00 UTC is no-signal, an hour without 60 bars has no ATR/swing.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

ROOT = Path("F:/MTS/data/tom_raw")
FOLDERS = {"BTCUSDT": "klines", "ETHUSDT": "klines_eth"}
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT")
# OURS except BTC (SOURCED PRE_REG.md:37, 0.1 USDT): Binance USD-M tick sizes as remembered, used only for the trade-through margin.
TICK = {"BTCUSDT": 0.1, "ETHUSDT": 0.01, "SOLUSDT": 0.01, "BNBUSDT": 0.01, "XRPUSDT": 0.0001, "DOGEUSDT": 0.00001,
        "ADAUSDT": 0.0001, "AVAXUSDT": 0.001, "LINKUSDT": 0.001, "LTCUSDT": 0.01}
NDAYS = (splits.DEV_END - splits.DEV_START).days
GRID = pd.date_range(splits.DEV_START, splits.DEV_END, freq="min", inclusive="left")
W0, W1 = 7 * 60, 13 * 60          # window W = minutes 420..779 of the UTC day (signals need t+1 inside W)
ATR_MULT_ELIG, ATR_BREAK, ATR_DEAD, ATR_STEP, ATR_FALLBACK = 0.5, 0.10, 1.5, 0.5, 1.5
# PRE_REG s5 says Binance maker/taker; this card orders Deribit all_taker (fees.py regime A): every leg taker fee + 2 bps slippage.
FEE_LEG = fees.FEES_ALL_TAKER["entry"]
ADVERSE_PX = 2 / 1e4              # 2 bps adverse price per leg (the slippage assumption, OURS; fees.py holds no slippage)
LEG_COST = FEE_LEG + ADVERSE_PX     # 7 bps per leg, 14 bps round trip (the gate cost)
FUNDING = 0.0001                  # flat 1 bp on weight held across 08:00 UTC, 'funding NOT_IN_DATA' (PRE_REG s5)
TRANCHE = 0.25
_NAME = re.compile(r"-1m-(\d{4})-(\d{2})(?:-\d{2})?\.csv$")


def load_klines(sym, root=ROOT, folder=None):
    """DEV 1m bars of one symbol as a DataFrame indexed by open time (gaps stay gaps). Files of months at/after 2024-07 are not opened;
    any remaining bar with open >= DEV_END raises splits.SplitViolation."""
    d = Path(root) / (folder or FOLDERS.get(sym, "klines_" + sym[:-4].lower()))
    parts = []
    for p in sorted(d.glob(sym + "-1m-*.csv")):
        m = _NAME.search(p.name)
        if not m or (int(m.group(1)), int(m.group(2))) >= (splits.DEV_END.year, splits.DEV_END.month):
            continue
        x = pd.read_csv(p, header=None, usecols=range(5), names=["open_time", "open", "high", "low", "close"], dtype=str)   # some months have no header row
        parts.append(x.apply(pd.to_numeric, errors="coerce").dropna())
    if not parts:
        raise FileNotFoundError(sym)
    df = pd.concat(parts)
    df.index = pd.to_datetime(df.pop("open_time"), unit="ms")
    df = df[~df.index.duplicated(keep="first")].sort_index()
    splits.assert_dev_only(df.index.min(), df.index.max())
    return df


def to_grid(df):
    """Arrays (D, 1440) of o,h,l,c on the full DEV minute grid; missing bars are NaN, never interpolated."""
    g = df.reindex(GRID)
    return [g[k].to_numpy(float).reshape(NDAYS, 1440) for k in ("open", "high", "low", "close")]


def usable_days(o, h, l, c):
    """Per day: bars 00:00..13:00 (781 incl. the 13:00 open) all present, and day index >= 5 (swing look-back)."""
    ok = ~np.isnan(o[:, :W1 + 1]).any(axis=1) & ~np.isnan(h[:, :W1 + 1]).any(axis=1) & ~np.isnan(l[:, :W1 + 1]).any(axis=1) \
        & ~np.isnan(c[:, :W1 + 1]).any(axis=1)
    ok[:5] = False
    return ok


def hourly(o, h, l, c):
    """Flat hourly arrays; an hour with any missing 1m bar is NaN."""
    def r(a):
        return a.reshape(-1, 60)
    full = ~np.isnan(r(h)).any(axis=1) & ~np.isnan(r(l)).any(axis=1) & ~np.isnan(r(c)).any(axis=1) & ~np.isnan(r(o)).any(axis=1)
    H, L, C = r(h).max(axis=1), r(l).min(axis=1), r(c)[:, -1].copy()
    H[~full], L[~full], C[~full] = np.nan, np.nan, np.nan
    return H, L, C


def wilder_atr(H, L, C):
    """ATR14 Wilder on hourly bars; atr[k] includes hour k. Restarts after any NaN hour. NaN until 14 contiguous hours."""
    n = len(H)
    atr = np.full(n, np.nan)
    tr = np.full(n, np.nan)
    tr[1:] = np.maximum.reduce([H[1:] - L[1:], np.abs(H[1:] - C[:-1]), np.abs(L[1:] - C[:-1])])
    run, cur = 0, np.nan
    for k in range(n):
        if np.isnan(tr[k]):
            run, cur = 0, np.nan
            continue
        run += 1
        if run < 14:
            cur = np.nan
            continue
        cur = tr[k - 13:k + 1].mean() if run == 14 else (cur * 13 + tr[k]) / 14
        atr[k] = cur
    return atr


def swings(H, L):
    """Hourly swing highs / lows (strictly above/below both neighbours); value at the swing hour, else NaN."""
    sh, sl = np.full(len(H), np.nan), np.full(len(H), np.nan)
    sh[1:-1] = np.where((H[1:-1] > H[:-2]) & (H[1:-1] > H[2:]), H[1:-1], np.nan)
    sl[1:-1] = np.where((L[1:-1] < L[:-2]) & (L[1:-1] < L[2:]), L[1:-1], np.nan)
    return sh, sl


class Sym:
    def __init__(self, name, o, h, l, c):
        self.name, self.o, self.h, self.l, self.c = name, o, h, l, c
        self.ok = usable_days(o, h, l, c)
        self.HH, self.HL, self.HC = hourly(o, h, l, c)
        self.atr = wilder_atr(self.HH, self.HL, self.HC)
        self.sh, self.sl = swings(self.HH, self.HL)
        self.tick = TICK[name]

    def atr_at(self, d, m):
        """ATR of the last hour CLOSED by the close of minute m of day d (hour closes with its minute 59)."""
        k = d * 24 + m // 60
        return self.atr[k] if m % 60 == 59 else self.atr[k - 1]

    def swing_hi(self, d, m):
        """Highest hourly swing high of the last 5 UTC days, usable once its next hour has closed (confirmed 2h after formation)."""
        kmax = (m + 1) // 60 + d * 24 - 2
        lo = (d - 5) * 24
        v = self.sh[lo:kmax + 1]
        return np.nan if len(v) == 0 or np.isnan(v).all() else np.nanmax(v)

    def swing_lo(self, d, m):
        kmax = (m + 1) // 60 + d * 24 - 2
        lo = (d - 5) * 24
        v = self.sl[lo:kmax + 1]
        return np.nan if len(v) == 0 or np.isnan(v).all() else np.nanmin(v)

    def _first_signal(self, d, lvl, atr_b):
        """lvl, atr_b: arrays over minutes W0..W1-2 (candidate break bars). Returns the signal bar t (minute) or None."""
        h, c = self.h[d], self.c[d]
        op = self.o[d][0]
        ms = np.arange(W0, W1)                         # break bar b in W
        cond = (h[ms] > lvl + ATR_BREAK * atr_b) & (lvl >= op + ATR_MULT_ELIG * atr_b) & ~np.isnan(lvl) & ~np.isnan(atr_b)
        idx = np.flatnonzero(cond)
        if len(idx) == 0:
            return None
        j = idx[0]                                     # first crossing; the level is consumed after this episode
        b = int(ms[j])
        L, a = lvl[j], atr_b[j]
        for t in range(b, min(b + 3, W1 - 2) + 1):     # failure within 3 bars after the break bar, inclusive; t+1 must be in W
            if h[b:t + 1].max() - L > ATR_DEAD * a:
                return None                            # excursion over 1.5 ATR first: level dead for the day
            if c[t] < L:
                return t
        return None

    def signal(self, d):
        """Earliest signal bar t of day d over the three resistance levels, or None (one position per day)."""
        if not self.ok[d]:
            return None
        h = self.h[d]
        ms = np.arange(W0, W1)
        k = d * 24 + ms // 60
        atr_b = np.where(ms % 60 == 59, self.atr[k], self.atr[k - 1])
        cands = []
        if not np.isnan(self.h[d - 1]).any():
            cands.append(np.full(len(ms), self.h[d - 1].max()))                              # (a) PDH
        pre = np.maximum.accumulate(h[:W1])                                                   # (b) ASH through the bar BEFORE b
        first, best, fi = np.zeros(W1, int), -np.inf, 0
        for i in range(W1):                                                                   # bar where the running max was first set
            if h[i] > best:
                best, fi = h[i], i
            first[i] = fi
        ash = np.where(first[ms - 1] <= ms - 60, pre[ms - 1], np.nan)
        cands.append(ash)
        sw = {q: self.swing_hi(d, q * 60 - 1) for q in range(7, 14)}                          # usable level changes once per hour
        cands.append(np.array([sw[(int(m) + 1) // 60] for m in ms]))                          # (c) swing high
        ts = [t for t in (self._first_signal(d, lv, atr_b) for lv in cands) if t is not None]
        return min(ts) if ts else None

    def support(self, d, t):
        out = []
        if not np.isnan(self.l[d - 1]).any():
            out.append(self.l[d - 1].min())                                                   # PDL
        out.append(self.l[d][:t + 1].min())                                                   # SL
        s = self.swing_lo(d, t)
        if not np.isnan(s):
            out.append(s)
        return out

    def simulate(self, d, t):
        """One episode. Returns dict with net bps of K, mae_pct, outcome, filled tranches."""
        o, h, l = self.o[d], self.h[d], self.l[d]
        e = t + 1
        a = self.atr_at(d, t)
        e1 = o[e]
        lims = [e1 + j * ATR_STEP * a for j in (1, 2, 3)]
        below = [s for s in self.support(d, t) if s <= e1 - a]
        target = max(below) if below else e1 - ATR_FALLBACK * a
        fills = [e1]
        mae, outcome, exit_px, fund_w, exit_j = 0.0, "TIME", None, 0.0, W1
        for j in range(e + 1, W1):
            if j == 480:
                fund_w = TRANCHE * len(fills)                                                  # weight open at the 08:00 settlement
            if l[j] <= target - self.tick:                                                     # target first: same-bar tranche fills not counted
                exit_px, outcome, exit_j = target, "TARGET", j
                break
            for k, lim in enumerate(lims):
                if len(fills) == k + 1 and h[j] >= lim + self.tick:
                    fills.append(lim)
            loss = sum(TRANCHE * (h[j] - f) / f for f in fills)
            mae = max(mae, loss)
        if exit_px is None:
            exit_px = o[W1]
        gross = sum(TRANCHE * (f - exit_px) / f for f in fills)
        cost = 2 * LEG_COST * TRANCHE * len(fills)
        fund = FUNDING * fund_w if (e < 480 and exit_j >= 480) else 0.0
        net = gross - cost - fund
        return {"net_bps": net * 1e4, "gross_bps": gross * 1e4, "mae_pct": mae * 100, "outcome": outcome, "tranches": len(fills),
                "entry": e1, "atr": a, "target": target, "t_min": t}


def build(sym, root=ROOT):
    return Sym(sym, *to_grid(load_klines(sym, root)))


def day_str(d):
    return str((splits.DEV_START + pd.Timedelta(days=int(d))).date())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["count", "dev"])
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args()
    out = Path(a.out)
    rows, per = [], {}
    for s in SYMBOLS:
        S = build(s)
        miss = int(np.isnan(S.h).sum())
        sig = [(d, S.signal(d)) for d in range(NDAYS)]
        sig = [(d, t) for d, t in sig if t is not None]
        per[s] = {"n": len(sig), "days_usable": int(S.ok.sum()), "missing_bars": miss}
        for d, t in sig:
            r = {"sym": s, "day": d, "date": day_str(d), "t_min": t}
            if a.mode == "dev":
                r.update(S.simulate(d, t))
            rows.append(r)
        print(s, per[s], flush=True)
    n = len(rows)
    print("POOLED n", n)
    if a.mode == "count":
        json.dump({"per_symbol": per, "pooled_n": n}, open(out / "COUNT.json", "w", newline="\n"), indent=1)
        return
    with open(out / "ledger.csv", "w", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    json.dump({"per_symbol": per, "pooled_n": n}, open(out / "COUNT_RUN.json", "w", newline="\n"), indent=1)


if __name__ == "__main__":
    main()
