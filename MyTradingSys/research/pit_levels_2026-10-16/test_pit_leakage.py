"""Point-in-time (PIT) leakage proofs for the level / phase / threshold builders (pit_levels_2026-10-16, step 2).

Contract tested for every family: a builder maps a bar series to `lev[j]` = the value in force at the OPEN of bar j,
i.e. built from bars[0..j-1] only.  PIT holds iff  builder(bars[:j])[j] == builder(bars)[j]  for every decision bar j.
Each family is run twice: on the repo code (expected identical) and on a planted copy that peeks one bar ahead
(expected to differ on at least one j).  A family PASSES only if the repo code is identical AND the planted copy is
caught, so a green row proves both the code and the test.

Run:  python MyTradingSys/research/pit_levels_2026-10-16/test_pit_leakage.py   (unittest; prints one line per family)
No production code is imported for side effects beyond module import; no market data is read (synthetic bars, seed 20261016).
"""
import bisect
import json
import math
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]          # worktree root (holds the MyTradingSys package)
sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest import vp_pivot_probe as vp                                  # noqa: E402
from MyTradingSys.backtest.layers.session_levels import session_levels as sl           # noqa: E402
from MyTradingSys.backtest.layers.cryptocred import cc_structure as cc                 # noqa: E402
from MyTradingSys.backtest.layers.timeframe import tf_resample as tfr                  # noqa: E402
from MyTradingSys.backtest.layers.fabio import orderflow_bars as ob                     # noqa: E402

sys.path.insert(0, str(ROOT / "MyTradingSys" / "research" / "gross_effect_screen_2026-10-15"))
import screen as gs                                                                   # noqa: E402

try:
    from MyTradingSys.backtest import tom_bt as T                                       # noqa: E402
except Exception as e:                                                                 # pragma: no cover
    T = None
    TOM_BT_IMPORT_ERROR = repr(e)

MIN = 60000
DAY = 86400000
T0 = 1640995200000          # 2022-01-01 00:00 UTC (a Saturday; weekday does not matter for these builders)
RESULTS = []


# ---------------------------------------------------------------- synthetic bars
def make_bars(n, seed=20261016, step_ms=MIN, p0=40000.0):
    rng = random.Random(seed)
    t, o, h, l, c, v, tbv = [], [], [], [], [], [], []
    p = p0
    for i in range(n):
        op = p
        cl = op * (1 + rng.gauss(0, 0.0012))
        hi = max(op, cl) * (1 + abs(rng.gauss(0, 0.0006)))
        lo = min(op, cl) * (1 - abs(rng.gauss(0, 0.0006)))
        vol = abs(rng.gauss(50, 20)) + 1
        t.append(T0 + i * step_ms); o.append(op); h.append(hi); l.append(lo); c.append(cl); v.append(vol)
        tbv.append(vol * rng.random())
        p = cl
    return dict(t=np.array(t, np.int64), o=np.array(o), h=np.array(h), l=np.array(l), c=np.array(c), v=np.array(v),
                tbv=np.array(tbv))


def as_dicts(B, n=None):
    n = len(B["t"]) if n is None else n
    return [dict(t=int(B["t"][i]), o=float(B["o"][i]), h=float(B["h"][i]), l=float(B["l"][i]), c=float(B["c"][i]),
                 v=float(B["v"][i])) for i in range(n)]


def slice_bars(B, n):
    return {k: a[:n] for k, a in B.items()}


def hourly_from(B5):
    """Complete 1h buckets only (FORMULAS 8) from 5m arrays."""
    t = B5["t"]; b = t // 3600000 * 3600000
    starts = np.concatenate([[0], np.flatnonzero(np.diff(b)) + 1]); ends = np.concatenate([starts[1:], [len(t)]])
    full = (ends - starts) == 12
    s, e = starts[full], ends[full]
    return dict(t1=b[s], h1=np.maximum.reduceat(B5["h"], starts)[full], l1=np.minimum.reduceat(B5["l"], starts)[full],
                c1=B5["c"][e - 1])


def check(name, builder_repo, builder_planted, B, js, maker=slice_bars, where=""):
    """Record PASS iff repo values identical at every j and the planted copy differs at >= 1 j."""
    full_r = builder_repo(B)
    full_p = builder_planted(B)
    same_r, caught = True, False
    for j in js:
        tr = builder_repo(maker(B, j))
        if not _eq(tr[j], full_r[j]):
            same_r = False
        tp = builder_planted(maker(B, j))
        if not _eq(tp[j], full_p[j]):
            caught = True
    verdict = "PASS" if (same_r and caught) else ("FAIL" if not same_r else "TEST-BLIND")
    RESULTS.append((name, verdict, where, same_r, caught))
    return same_r, caught


def _eq(a, b):
    if isinstance(a, (tuple, list, np.ndarray)):
        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    if a is None or b is None:
        return a is b
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


# ---------------------------------------------------------------- F1 prior-period high/low (session_levels.day_levels)
def f1_repo(B):
    bars = as_dicts(B)
    lev = sl.day_levels(bars) if bars else {}
    n = len(bars)
    out = [None] * (n + 1)
    for j in range(n + 1):
        d = (T0 + j * MIN) // DAY
        p = lev.get(d - 1)
        out[j] = (p["high"], p["low"]) if p else None
    return out


def f1_planted(B):                     # leak: the level of the CURRENT day (bars at and after j), i.e. a bucket aligned to the day's close
    bars = as_dicts(B)
    lev = sl.day_levels(bars) if bars else {}
    n = len(bars)
    out = [None] * (n + 1)
    for j in range(n + 1):
        d = (T0 + j * MIN) // DAY
        p = lev.get(d)
        out[j] = (p["high"], p["low"]) if p else None
    return out


# ---------------------------------------------------------------- F2a swing pivots (cc_structure.find_swings, confirmed_i)
def f2a_repo(B):
    bars = as_dicts(B); n = len(bars)
    sw = cc.find_swings(bars, 2, 2, use_body=False) if n >= 5 else []
    out = [None] * (n + 1)
    for j in range(n + 1):
        known = [s for s in sw if s["confirmed_i"] < j]            # cc_structure.py:99 rule
        out[j] = (known[-1]["i"], known[-1]["price"]) if known else None
    return out


def f2a_planted(B):                    # leak: pivot used as soon as its own bar exists (right window not closed)
    bars = as_dicts(B); n = len(bars)
    sw = cc.find_swings(bars, 2, 2, use_body=False) if n >= 5 else []
    out = [None] * (n + 1)
    for j in range(n + 1):
        known = [s for s in sw if s["i"] < j]
        out[j] = (known[-1]["i"], known[-1]["price"]) if known else None
    return out


# ---------------------------------------------------------------- F2b fractal pivots + ATR (vp_pivot_probe 18.2 / 12)
NPIV = 2


def f2b_repo(B):                        # B = 1h arrays; decision at the open of bar j = t[j]
    n = len(B["t"]); out = [None] * (n + 1)
    hi = vp.fractal_pivot_highs(B["h"], NPIV)
    atr = vp.atr_sma(B["h"], B["l"], B["c"])
    for j in range(n + 1):
        g = T0 + j * 3600000
        k = vp.last_confirmed(hi, B["t"], NPIV, g)
        a = float(atr[j - 1]) if 0 < j <= n else float("nan")
        out[j] = (int(k), float(B["h"][k]) if k >= 0 else None, a)
    return out


def f2b_planted(B):                     # leak: pivot active at the OPEN of bar i+n (its confirming bar not closed)
    n = len(B["t"]); out = [None] * (n + 1)
    hi = vp.fractal_pivot_highs(B["h"], NPIV)
    atr = vp.atr_sma(B["h"], B["l"], B["c"])
    for j in range(n + 1):
        g = T0 + j * 3600000
        if len(hi):
            act = B["t"][hi + NPIV]                                # no + HOUR_MS
            pos = int(np.searchsorted(act, g, side="right") - 1)
            k = int(hi[pos]) if pos >= 0 else -1
        else:
            k = -1
        a = float(atr[j - 1]) if 0 < j <= n else float("nan")
        out[j] = (k, float(B["h"][k]) if k >= 0 else None, a)
    return out


# ---------------------------------------------------------------- F3 anchored volume profiles (vp_pivot_probe ctx families)
CTX = next(c for c in vars(vp).values() if isinstance(c, type) and hasattr(c, "family_levels"))


class CtxPeek(CTX):
    """Planted copies: developing profiles add the refresh bar itself; the static prior-day segment runs 5 min into today."""
    def _add(self, vol, s, e):
        super()._add(vol, s, min(e + 1, self.N))

    def static_levels(self, seg_start, seg_end):
        return super().static_levels(seg_start, np.asarray(seg_end) + 5 * MIN)

    def family_levels(self, fam):
        """A1/A2 peek: a pivot is active at the OPEN of its confirming 1h bar (no + HOUR_MS), one hourly bar early."""
        if not fam.startswith("A"):
            return super().family_levels(fam)
        orig = vp.last_confirmed_vec

        def peek(piv, t1, n, g):
            piv = np.asarray(piv, np.int64); g = np.asarray(g)
            if len(piv) == 0:
                return np.full(g.shape, -1, np.int64)
            act = np.asarray(t1)[piv + n]
            pos = np.searchsorted(act, g, side="right") - 1
            return np.where(pos >= 0, piv[np.maximum(pos, 0)], -1)
        vp.last_confirmed_vec = peek
        try:
            return super().family_levels(fam)
        finally:
            vp.last_confirmed_vec = orig


def _ctx_builder(cls, fam):
    def build(B5):
        H = hourly_from(B5)
        d = dict(t5=B5["t"], o5=B5["o"], h5=B5["h"], l5=B5["l"], c5=B5["c"], v5=B5["v"], **H)
        ctx = cls(d, int(B5["t"][0]))
        fl = ctx.family_levels(fam)
        lev = np.stack([ctx.ffill(fl[i]) for i in range(3)])   # (3, N): level in force at bar index (refresh at the bar included)
        n = len(B5["t"])
        out = [None] * (n + 1)
        for j in range(n):
            out[j] = tuple(None if np.isnan(x) else round(float(x), 6) for x in lev[:, j])
        return out
    return build


def with_dummy(B5, j):
    """bars[:j] plus a dummy bar AT the open of bar j so the refresh at j exists; a PIT builder never reads it."""
    S = slice_bars(B5, j)
    px = float(B5["c"][j - 1]) * 1.5
    S = {k: np.concatenate([S[k], [x]]) for k, x in
         (("t", int(B5["t"][j])), ("o", px), ("h", px), ("l", px), ("c", px), ("v", 1e9), ("tbv", 0.0))}
    return S


# ---------------------------------------------------------------- F4 closed-bucket resampling (tf_resample, tom_bt.resample_dicts)
REG = {"timeframes": {"1h": {"unit": "seconds", "seconds": 3600}}}


def f4_repo(B):
    bars = as_dicts(B); n = len(bars); out = [None] * (n + 1)
    res = tfr.resample(bars, "1h", REG) if bars else []
    ends = [r["t"] + 3600000 for r in res]
    for j in range(n + 1):
        g = T0 + j * MIN
        k = int(np.searchsorted(np.asarray(ends, np.int64), g, side="right") - 1) if ends else -1
        out[j] = (res[k]["t"], res[k]["c"], res[k]["h"], res[k]["l"]) if k >= 0 else None
    return out


def f4_planted(B):                     # leak: the partial trailing bucket is emitted (its running close/high/low)
    bars = as_dicts(B); n = len(bars); out = [None] * (n + 1)
    ts = [b["t"] for b in bars]                                # ascending: bars[lo:j+1] == the O(n) filter t >= bs
    for j in range(n + 1):
        if not bars:
            out[j] = None; continue
        g = T0 + j * MIN
        bs = tfr.bucket_start(g, "1h", REG)
        grp = bars[bisect.bisect_left(ts, bs):j + 1]           # peek: bar j itself (not closed at its open)
        out[j] = (bs, grp[-1]["c"], max(b["h"] for b in grp), min(b["l"] for b in grp)) if grp else None
    return out


def f4b_repo(B):
    if T is None:
        return None
    n = len(B["t"]); out = [None] * (n + 1)
    b = T.Bars1m(int(B["t"][0]), list(B["o"]), list(B["h"]), list(B["l"]), list(B["c"]), list(B["v"]), list(B["tbv"]))
    res = T.resample_dicts(b, 60) if n else []
    ends = np.asarray([r["t"] + 3600000 for r in res], np.int64)
    for j in range(n + 1):
        g = T0 + j * MIN
        k = int(np.searchsorted(ends, g, side="right") - 1) if len(ends) else -1
        out[j] = (res[k]["t"], res[k]["c"], res[k]["h"]) if k >= 0 else None
    return out


# ---------------------------------------------------------------- F5 regime tags (tom_bt.regime_features / trend_tag / tercile_cuts)
def f5_repo(B):
    n = len(B["t"]); out = [None] * (n + 1)
    b = T.Bars1m(int(B["t"][0]), list(B["o"]), list(B["h"]), list(B["l"]), list(B["c"]), list(B["v"]), list(B["tbv"]))
    for j in range(n + 1):
        rf = T.regime_features(b, (T0 + j * MIN) / 1000.0) if j >= 1 else None
        out[j] = (round(rf[0], 12), T.trend_tag(rf[0])) if rf else None
    return out


def f5_planted(B):                     # leak: ret30 read at the bar whose close is not yet known (label at bar open)
    n = len(B["t"]); out = [None] * (n + 1)
    for j in range(n + 1):
        i = min(j, n - 1)
        if i < 30 * 1440:
            out[j] = None; continue
        r = float(B["c"][i] / B["c"][i - 30 * 1440] - 1.0)
        out[j] = (round(r, 12), T.trend_tag(r))
    return out


# ---------------------------------------------------------------- F6 percentile thresholds (screen L4; orderflow rolling 99th)
def _A_from(B, ndays):
    n = ndays * 1440
    A = {k: np.full(n, np.nan) for k in ("O", "H", "L", "C", "V", "TBV", "QV")}
    m = min(n, len(B["t"]))
    A["O"][:m], A["H"][:m], A["L"][:m], A["C"][:m] = B["o"][:m], B["h"][:m], B["l"][:m], B["c"][:m]
    A["V"][:m], A["TBV"][:m], A["QV"][:m] = B["v"][:m], B["tbv"][:m], B["v"][:m] * B["c"][:m]
    return A


def f6_repo_set(B, ndays):
    led = gs.build_ledger(_A_from(B, ndays), ndays)
    return set(zip(led["t"].tolist(), led["side"].tolist(), led["F"].tolist()))


def f6_planted_thr(B, ndays, i, m):
    """L4 threshold at day i, minute m with the OWN day in the reference window (legs[i-19:i+1])."""
    A = _A_from(B, ndays)
    legs = np.full((ndays, 1440), np.nan)
    for d in range(ndays):
        s = slice(d * 1440, (d + 1) * 1440)
        o, h, l = A["O"][s], A["H"][s], A["L"][s]
        bad = np.isnan(o) | np.isnan(h) | np.isnan(l)
        hf = np.where(bad, -np.inf, h); lf = np.where(bad, np.inf, l)
        leg = (np.maximum.accumulate(hf) - np.minimum.accumulate(lf)) / o[0]
        legs[d] = np.where(np.cumsum(bad) == 0, leg, np.nan)
    ref = np.concatenate([legs[max(0, i - 19):i, m], [legs[i, 1439]]])     # own day's END-of-day leg = full-sample peek
    return float(np.nanpercentile(ref, 80))


class PitLeakage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.B1 = make_bars(6 * 1440)                                    # 6 days of 1m bars
        cls.B5 = make_bars(12 * 288, seed=7, step_ms=5 * MIN)           # 12 days of 5m bars
        cls.B1h = make_bars(400, seed=11, step_ms=3600000)              # 400 hourly bars
        rng = random.Random(3)
        cls.js1 = sorted(rng.sample(range(1500, 6 * 1440 - 10), 12))
        cls.js5 = sorted(rng.sample(range(300, 12 * 288 - 5), 12)) + [288 * 4, 288 * 4 + 3, 288 * 7 + 9]   # include refresh/midnight bars
        cls.jsh = sorted(rng.sample(range(30, 399), 15))

    def test_f1_prior_day_levels(self):
        same, caught = check("F1 prior-period high/low", f1_repo, f1_planted, self.B1, self.js1,
                             where="session_levels.py:43-52 day_levels; consumer :90-93 levels[d-1]")
        self.assertTrue(same and caught)

    def test_f2a_swings(self):
        same, caught = check("F2a swing pivots (confirmed_i)", f2a_repo, f2a_planted, self.B1, self.js1[:8],
                             where="cc_structure.py:49,:57 confirmed_i=i+right; consumer :99 confirmed_i < k")
        self.assertTrue(same and caught)

    def test_f2b_fractal_atr(self):
        same, caught = check("F2b fractal pivots + ATR14", f2b_repo, f2b_planted, self.B1h, self.jsh,
                             where="vp_pivot_probe.py:130-141, :175-183 (+HOUR_MS), :116-127 atr_sma")
        self.assertTrue(same and caught)

    def test_f3_profiles(self):
        for fam in ("session", "prior_day", "A1_n2_k0", "A2_n2_k0"):
            same, caught = check(f"F3 volume profile {fam}", _ctx_builder(CTX, fam), _ctx_builder(CtxPeek, fam),
                                 self.B5, self.js5, maker=with_dummy,
                                 where="vp_pivot_probe.py:403-429 developing (bars [anchor, refresh)), :431-453 static_levels, :456-484 family_levels")
            self.assertTrue(same and caught, fam)

    def test_f4_resample(self):
        same, caught = check("F4 closed buckets tf_resample", f4_repo, f4_planted, self.B1, self.js1,
                             where="tf_resample.py:114-116 skip bucket_end > last close")
        self.assertTrue(same and caught)
        if T is not None:
            same, caught = check("F4b closed buckets tom_bt.resample_dicts", f4b_repo, f4_planted, self.B1, self.js1,
                                 where="tom_bt.py:105-116 while j0+tf <= n")
            self.assertTrue(same and caught)

    def test_f5_regime(self):
        if T is None:
            RESULTS.append(("F5 regime tags", "IMPORT-FAIL", TOM_BT_IMPORT_ERROR, False, False)); self.skipTest(TOM_BT_IMPORT_ERROR)
        B = make_bars(32 * 1440, seed=5)
        js = [30 * 1440 + 7, 30 * 1440 + 500, 31 * 1440 + 100]
        same, caught = check("F5 regime trend_tag (ret30, data <= t)", f5_repo, f5_planted, B, js,
                             where="tom_bt.py:256-268 i = idx(t)-1 (last closed bar)")
        self.assertTrue(same and caught)
        # tercile cuts: tom_bt_report.py:158-161 computes cuts over ALL trades' vol30 (full sample), then tags each trade.
        vols = [abs(random.Random(k).gauss(0.02, 0.01)) for k in range(60)]
        t_idx = 20
        cuts_full = T.tercile_cuts(vols)
        cuts_pit = T.tercile_cuts(vols[:t_idx + 1])
        tag_full, tag_pit = T.vol_tag(vols[t_idx], cuts_full), T.vol_tag(vols[t_idx], cuts_pit)
        leaks = cuts_full != cuts_pit
        RESULTS.append(("F5 vol terciles (tom_bt_report.py:161 full-sample cuts)", "FAIL" if leaks else "PASS",
                        f"cuts over all trades {tuple(round(x, 4) for x in cuts_full)} vs over trades <= t {tuple(round(x, 4) for x in cuts_pit)}; tag {tag_full} vs {tag_pit}; descriptive split only, no decision reads it",
                        not leaks, True))
        self.assertTrue(leaks)

    def test_f6_percentiles(self):
        ndays = 40
        B = make_bars(ndays * 1440, seed=9)
        i, m = 33, 700
        g = i * 1440 + m
        full = f6_repo_set(B, ndays)
        trunc = f6_repo_set(slice_bars(B, g + 1), ndays)
        same = {e for e in full if e[0] <= g} == {e for e in trunc if e[0] <= g}
        caught = f6_planted_thr(B, ndays, i, m) != f6_planted_thr(slice_bars(B, g + 1), ndays, i, m)
        RESULTS.append(("F6a screen L4 percentile (prior 20 days)", "PASS" if same and caught else "FAIL",
                        "screen.py:111-117 ref = legs[i-20:i]; planted legs[i-19:i+1] caught", same, caught))
        self.assertTrue(same and caught)
        # orderflow_bars.rolling_thresholds: prior `window` calendar days only (k = 1..window)
        import datetime as dt
        with tempfile.TemporaryDirectory() as td:
            day = dt.date(2024, 3, 10)
            for k in range(1, 6):
                (Path(td) / f"{(day - dt.timedelta(days=k)).isoformat()}.json").write_text(json.dumps({"100": 50 * k, "200": 5, "300": 1}))
            a = ob.rolling_thresholds(td, day, None)
            (Path(td) / f"{day.isoformat()}.json").write_text(json.dumps({"300": 1000}))
            (Path(td) / f"{(day + dt.timedelta(days=1)).isoformat()}.json").write_text(json.dumps({"300": 1000}))
            b = ob.rolling_thresholds(td, day, None)
            # planted: window k = 0..window-1 (own day included)
            def planted(hist_dir, day, window=30):
                total = {}
                for k in range(0, window):
                    p = Path(hist_dir) / f"{(day - dt.timedelta(days=k)).isoformat()}.json"
                    if p.exists():
                        for bb, cc_ in json.loads(p.read_text()).items():
                            total[int(bb)] = total.get(int(bb), 0) + cc_
                return ob.threshold_from_hist(total, 0.99)
            (Path(td) / f"{day.isoformat()}.json").unlink()
            p_without = planted(td, day)
            (Path(td) / f"{day.isoformat()}.json").write_text(json.dumps({"300": 1000}))
            p_with = planted(td, day)
        same2, caught2 = (a == b), (p_without != p_with)
        RESULTS.append(("F6b orderflow big-trade 99th pct (prior 30 days)", "PASS" if same2 and caught2 else "FAIL",
                        "orderflow_bars.py:144-157 k in 1..window; own-day fallback flagged thr_days=0 (:236-241), excluded by day_gates.py:99",
                        same2, caught2))
        self.assertTrue(same2 and caught2)


if __name__ == "__main__":
    r = unittest.main(exit=False, verbosity=1)
    print("\nFAMILY RESULTS (PASS = repo identical on bars[:t] vs bars[:t+N] AND planted peek caught)")
    for name, verdict, where, same, caught in RESULTS:
        print(f"{verdict:10s} {name:55s} repo_identical={same} planted_caught={caught} | {where}")
    sys.exit(0 if r.result.wasSuccessful() else 1)
