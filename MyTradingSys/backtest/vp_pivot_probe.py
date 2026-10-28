import sys
sys.dont_write_bytecode = True
"""Anchored volume profile touch study (phase 2 of research/tom_core_bt_2026-10-09/PLAN.md).

Canonical definition: backtest/layers/FORMULAS.md section 18 (profile 18.1, pivots 18.2, size filter 18.3, families 18.4,
touch/outcome 18.5, placebo 18.6, statistics 18.7), ATR = plain SMA of true range (section 12), resample = section 8.
Everything NO-SOURCE is a measurement choice, flagged, never tuned.

CLI: python MyTradingSys/backtest/vp_pivot_probe.py --start 2022-01-01 --end 2026-10-08 --out <dir> [--families a,b]
"""
import argparse
import glob
import hashlib
import json
import multiprocessing as mp
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fees import BINANCE_MAKER, BINANCE_TAKER  # noqa: E402

# ------------------------------------------------------------------ constants
W_BIN = 10.0                 # NO-SOURCE bin width (FORMULAS 18.1)
VA_PCT = 0.70                # engine VALUE_AREA_PCT; Tom 1utSjHs_Mq8:19
ATR_PERIOD = 14
MIN_DEV_BARS = 12            # developing profiles need >= 12 bars (18.4)
H_BARS = 48                  # NO-SOURCE (phase 2 default 2026-10-09, not tuned): timeout horizon, 48 x 5m = 4h
WARMUP_DAYS = 60             # history loaded before --start so pivots / weekly / ATR are warm (events counted from --start)
N_BOOT = 2000
BOOT_SEED = 20261009
MIN_EVENTS = 300             # Tom's bar
PLACEBO_D = np.array([-3, -2, -1, -0.5, 0.5, 1, 2, 3], float)
KIND_TARGET, KIND_STOP, KIND_TIMEOUT = 0, 1, 2
PIVOT_NS = (2, 3, 5)
PIVOT_KS = (0, 2)
LEVELS = ("poc", "vah", "val")
MIN_MS, HOUR_MS, DAY_MS = 60_000, 3_600_000, 86_400_000
REFRESH_MS = 900_000

DATA_ROOT = Path("C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest")
KLINE_DIRS = (DATA_ROOT / "raw_1m_2022" / "klines", DATA_ROOT / "raw" / "klines")
CACHE_DIR = Path("C:/Users/E-NGIN~1/AppData/Local/Temp/claude/vp_cache")


# ------------------------------------------------------------------ 18.1 profile
def _expand(l, h, v, w):
    """Spread every bar over the bins it overlaps. Returns (offs, ks, wts, kl, kh): bar i owns ks[offs[i]:offs[i+1]]."""
    l = np.asarray(l, float); h = np.asarray(h, float); v = np.asarray(v, float)
    n = len(l)
    kl = np.floor(l / w).astype(np.int64)
    kh = np.where(h > l, np.ceil(h / w).astype(np.int64) - 1, kl)
    kh = np.maximum(kh, kl)
    cnt = kh - kl + 1
    offs = np.zeros(n + 1, np.int64)
    offs[1:] = np.cumsum(cnt)
    total = int(offs[-1])
    idx = np.repeat(np.arange(n), cnt)
    ks = kl[idx] + (np.arange(total, dtype=np.int64) - offs[:-1][idx])
    li, hi_, vi = l[idx], h[idx], v[idx]
    span = hi_ - li
    ov = np.clip(np.minimum(hi_, (ks + 1) * w) - np.maximum(li, ks * w), 0.0, None)
    wts = np.where(span > 0, vi * ov / np.where(span > 0, span, 1.0), vi)
    return offs, ks, wts, kl, kh


def _value_area(vol, ip, total):
    """18.1 value-area expansion on a python list. Returns (lo, hi) indices."""
    target = VA_PCT * total
    lo = hi = ip
    acc = vol[ip]
    last = len(vol) - 1
    while acc < target:
        vl = vol[lo - 1] if lo > 0 else -1.0
        vh = vol[hi + 1] if hi < last else -1.0
        if vl >= vh and lo > 0:
            lo -= 1; acc += vl
        elif hi < last:
            hi += 1; acc += vh
        elif lo > 0:
            lo -= 1; acc += vl
        else:
            break
    return lo, hi


def _levels_from_bins(seg, kbase, w):
    """seg: numpy bin volumes covering touched bins, seg[0] is bin kbase. Returns (poc_price, vah, val) or None."""
    total = float(seg.sum())
    if not total > 0:
        return None
    ip = int(seg.argmax())                      # first maximum = lowest bin
    lo, hi = _value_area(seg.tolist(), ip, total)
    return (kbase + ip) * w + w / 2.0, (kbase + hi + 1) * w, (kbase + lo) * w


def build_profile(l, h, v, w=W_BIN):
    """Profile of a bar set (18.1). Returns {'poc_price','vah','val'} or None for an empty / zero-volume set."""
    l = np.asarray(l, float)
    if l.size == 0:
        return None
    _offs, ks, wts, _kl, _kh = _expand(l, h, v, w)
    kmin, kmax = int(ks.min()), int(ks.max())
    seg = np.bincount(ks - kmin, weights=wts, minlength=kmax - kmin + 1)
    r = _levels_from_bins(seg, kmin, w)
    if r is None:
        return None
    return {"poc_price": r[0], "vah": r[1], "val": r[2]}


# ------------------------------------------------------------------ 12 ATR, 18.2 pivots, 18.3 size filter
def atr_sma(h, l, c, period=ATR_PERIOD):
    """Plain-SMA ATR (FORMULAS 12): mean of the `period` true ranges ending at i; NaN for i < period."""
    h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    n = len(h)
    out = np.full(n, np.nan)
    if n <= period:
        return out
    tr = np.maximum.reduce([h[1:] - l[1:], np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])])   # tr[m] is TR of bar m+1
    cs = np.concatenate([[0.0], np.cumsum(tr)])             # cs[i] = sum TR[1..i]
    i = np.arange(period, n)
    out[period:] = (cs[i] - cs[i - period]) / period
    return out


def fractal_pivot_highs(h, n):
    h = np.asarray(h, float)
    N = len(h)
    if N < 2 * n + 1:
        return np.zeros(0, np.int64)
    c = h[n:N - n]
    ok = np.ones(len(c), bool)
    for d in range(1, n + 1):
        ok &= c > h[n - d:N - n - d]
        ok &= c > h[n + d:N - n + d]
    return np.flatnonzero(ok) + n


def fractal_pivot_lows(l, n):
    return fractal_pivot_highs(-np.asarray(l, float), n)


def meaningful_pivots(h, l, c, n, k):
    """18.3: (meaningful pivot-high indices, meaningful pivot-low indices) on one bar series."""
    hi = fractal_pivot_highs(h, n)
    lo = fractal_pivot_lows(l, n)
    if k == 0:
        return hi, lo
    atr = atr_sma(h, l, c)

    def filt(mine, other, mine_price, other_price):
        if len(mine) == 0:
            return mine
        pos = np.searchsorted(other, mine, side="left") - 1      # largest opposite pivot with index < p
        has = pos >= 0
        q = other[np.where(has, pos, 0)]
        dist = np.abs(mine_price[mine] - other_price[q])
        with np.errstate(invalid="ignore"):
            keep = has & (dist >= k * atr[mine])                 # NaN ATR -> False
        return mine[keep]

    h = np.asarray(h, float); l = np.asarray(l, float)
    return filt(hi, lo, h, l), filt(lo, hi, l, h)


def pivot_usable_index(i, n):
    """A pivot at bar i is confirmed at the close of bar i+n, usable from the open of bar i+n+1."""
    return i + n + 1


def last_confirmed_vec(piv, t1, n, g):
    """For each time g (ms) the last pivot index in `piv` whose confirmation (close of bar i+n) is <= g, else -1."""
    piv = np.asarray(piv, np.int64)
    g = np.asarray(g)
    if len(piv) == 0:
        return np.full(g.shape, -1, np.int64)
    act = np.asarray(t1)[piv + n] + HOUR_MS
    pos = np.searchsorted(act, g, side="right") - 1
    return np.where(pos >= 0, piv[np.maximum(pos, 0)], -1)


def last_confirmed(piv, t1, n, g):
    r = last_confirmed_vec(piv, t1, n, np.asarray([g]))
    return int(r[0])


# ------------------------------------------------------------------ 18.5 outcomes
def resolve_events(o, h, l, c, j, side, L, R, H=H_BARS, chunk=20000):
    """Vectorised 18.5 resolution. Returns (exit_price, kind, exit_bar); kind -1 = window runs past the data."""
    o = np.asarray(o, float); h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    j = np.asarray(j, np.int64); sd = np.asarray(side, float); L = np.asarray(L, float); R = np.asarray(R, float)
    N, n = len(h), len(j)
    pad = np.full(H, np.nan)                       # NaN padding: no hit past the data, an unfinished timeout is dropped
    o, h, l, c = (np.concatenate([x, pad]) for x in (o, h, l, c))
    ex = np.full(n, np.nan)
    kind = np.full(n, -1, np.int8)
    eb = np.full(n, -1, np.int64)
    ok = np.flatnonzero(j < N)
    offs = np.arange(1, H + 1)
    for s in range(0, len(ok), chunk):
        sel = ok[s:s + chunk]
        jj, d = j[sel], sd[sel]
        Lp = d * L[sel]; stop = Lp - R[sel]; tgt = Lp + R[sel]          # side frame: long logic
        up = (d > 0)[:, None]
        idx = jj[:, None] + offs
        lo_w = np.where(up, l[idx], -h[idx]); hi_w = np.where(up, h[idx], -l[idx]); op_w = d[:, None] * o[idx]
        lo_t = np.where(d > 0, l[jj], -h[jj])
        sh = lo_w <= stop[:, None]; th = hi_w >= tgt[:, None]
        fs = np.where(sh.any(1), sh.argmax(1), H); ft = np.where(th.any(1), th.argmax(1), H)
        touch_stop = lo_t <= stop
        stop_win = (~touch_stop) & (fs <= ft) & (fs < H)
        tgt_win = (~touch_stop) & (~stop_win) & (ft < H)
        tmo = ~(touch_stop | stop_win | tgt_win)
        rows = np.arange(len(sel))
        gap_open = op_w[rows, np.minimum(fs, H - 1)]
        px = np.where(touch_stop, stop, np.where(stop_win, np.minimum(stop, gap_open), np.where(tgt_win, tgt, d * c[jj + H])))
        k = np.where(touch_stop | stop_win, KIND_STOP, np.where(tgt_win, KIND_TARGET, KIND_TIMEOUT))
        e = np.where(touch_stop, jj, np.where(stop_win, jj + 1 + fs, np.where(tgt_win, jj + 1 + ft, jj + H)))
        ex[sel] = d * px
        kind[sel] = np.where(tmo & (jj + H >= N), -1, k)
        eb[sel] = e
    return ex, kind, eb


def gross_r(side, L, R, exit_price):
    return np.asarray(side, float) * (np.asarray(exit_price, float) - L) / R


def net_r(side, L, R, exit_price, kind, variant="taker"):
    """18.5 net R. taker: both legs taker. maker: entry + target maker, stop + timeout taker."""
    side = np.asarray(side, float); exit_price = np.asarray(exit_price, float); kind = np.asarray(kind)
    if variant == "taker":
        fee_in = BINANCE_TAKER
        fee_out = BINANCE_TAKER
    else:
        fee_in = BINANCE_MAKER
        fee_out = np.where(kind == KIND_TARGET, BINANCE_MAKER, BINANCE_TAKER)
    r = (side * (exit_price - L) - fee_in * L - fee_out * exit_price) / R
    return r if r.ndim else float(r)


def select_events(j, exit_bar):
    """One open event per stream: skip a touch while the previous accepted event's exit bar >= this bar."""
    keep = np.zeros(len(j), bool)
    last = -1
    for i in range(len(j)):
        if j[i] > last:
            keep[i] = True
            last = exit_bar[i]
    return keep


# ------------------------------------------------------------------ 18.6 placebo, 18.7 statistics
def placebo_level(L, R_ref, refresh_index):
    return L + PLACEBO_D[np.asarray(refresh_index, np.int64) % 8] * R_ref


def boot_stat(day_sum, day_cnt, idx):
    """Resampled mean: sum of R over the resampled days / events in them. idx: (..., n_days) day indices."""
    idx = np.asarray(idx)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.asarray(day_sum)[idx].sum(-1) / np.asarray(day_cnt)[idx].sum(-1)
    return r if np.ndim(r) else float(r)


def longest_losing_streak(x):
    best = cur = 0
    for v in x:
        cur = cur + 1 if v < 0 else 0
        best = max(best, cur)
    return best


# ------------------------------------------------------------------ data loading
_FN = re.compile(r"BTCUSDT-1m-(\d{4})-(\d{2})(?:-(\d{2}))?\.csv$")


def _utc_ms(y, m, d=1):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


def list_files(start_ms, end_ms):
    out = []
    for d in KLINE_DIRS:
        for f in sorted(glob.glob(str(d / "BTCUSDT-1m-*.csv"))):
            m = _FN.search(f)
            if not m:
                continue
            y, mo, dd = int(m.group(1)), int(m.group(2)), m.group(3)
            if dd:
                a = _utc_ms(y, mo, int(dd)); b = a + DAY_MS
            else:
                a = _utc_ms(y, mo); b = _utc_ms(y + (mo == 12), mo % 12 + 1)
            if a < end_ms and b > start_ms:
                out.append(f)
    return out


def _read_csv(f):
    with open(f, "r") as fh:
        first = fh.readline()
    skip = 0 if first[:1].isdigit() else 1
    try:
        a = np.loadtxt(f, delimiter=",", skiprows=skip, usecols=(0, 1, 2, 3, 4, 5), dtype=np.float64, ndmin=2)
    except Exception as e:  # noqa: BLE001
        print(f"WARN unreadable {f}: {e}", file=sys.stderr)
        return np.zeros((0, 6))
    return a


def resample(t, o, h, l, c, v, bucket_ms):
    """FORMULAS 8: UTC epoch buckets, only complete buckets (all minutes present). Returns arrays + (incomplete count)."""
    b = t // bucket_ms * bucket_ms
    starts = np.concatenate([[0], np.flatnonzero(np.diff(b)) + 1])
    ends = np.concatenate([starts[1:], [len(t)]])
    full = (ends - starts) == bucket_ms // MIN_MS
    s, e = starts[full], ends[full]
    return (b[s], o[s], np.maximum.reduceat(h, starts)[full], np.minimum.reduceat(l, starts)[full], c[e - 1],
            np.add.reduceat(v, starts)[full], int((~full).sum()))


def load_bars(start_ms, end_ms):
    """Returns dict of 5m / 1h arrays + coverage meta; cached as .npz in CACHE_DIR."""
    files = list_files(start_ms, end_ms)
    if not files:
        raise SystemExit("no kline files in range")
    key = hashlib.md5("|".join(f"{os.path.basename(f)}:{os.path.getsize(f)}" for f in files).encode()).hexdigest()[:12]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp = CACHE_DIR / f"bars_{key}.npz"
    if cp.exists():
        z = np.load(cp, allow_pickle=False)
        d = {k: z[k] for k in z.files if k != "meta"}
        d["meta"] = json.loads(str(z["meta"]))
        return d
    parts = [_read_csv(f) for f in files]
    a = np.concatenate(parts)
    t = a[:, 0].copy()
    t[t > 1e14] = np.floor(t[t > 1e14] / 1000.0)                 # microsecond stamps -> ms
    order = np.argsort(t, kind="stable")
    t, a = t[order], a[order]
    t, ui = np.unique(t, return_index=True)                       # dedup (monthly / daily overlap)
    a = a[ui]
    t = t.astype(np.int64)
    o, h, l, c, v = a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5]
    dt = np.diff(t)
    gi = np.flatnonzero(dt > MIN_MS)
    miss = (dt[gi] // MIN_MS - 1).astype(int)
    big = np.argsort(-miss)[:10]
    meta = {
        "files": len(files), "rows_1m": int(len(t)), "first_ms": int(t[0]), "last_ms": int(t[-1]),
        "gap_count": int(len(gi)), "missing_minutes": int(miss.sum()),
        "largest_gaps": [{"start_ms": int(t[gi[i]]), "minutes": int(miss[i])} for i in big],
        "off_grid_1m": int((t % MIN_MS != 0).sum()),
    }
    t5, o5, h5, l5, c5, v5, inc5 = resample(t, o, h, l, c, v, 5 * MIN_MS)
    t1, o1, h1, l1, c1, v1, inc1 = resample(t, o, h, l, c, v, HOUR_MS)
    meta["incomplete_5m_buckets"] = inc5
    meta["incomplete_1h_buckets"] = inc1
    d = dict(t5=t5, o5=o5, h5=h5, l5=l5, c5=c5, v5=v5, t1=t1, o1=o1, h1=h1, l1=l1, c1=c1, v1=v1)
    np.savez(cp, meta=json.dumps(meta), **d)
    d["meta"] = meta
    return d


# ------------------------------------------------------------------ context + families
class Ctx:
    def __init__(self, d, start_ms):
        self.t5, self.o, self.h, self.l, self.c, self.v = (d[k] for k in ("t5", "o5", "h5", "l5", "c5", "v5"))
        self.t1, self.h1, self.l1, self.c1 = (d[k] for k in ("t1", "h1", "l1", "c1"))
        self.N = len(self.t5)
        self.start_idx = int(np.searchsorted(self.t5, start_ms))
        self.atr1 = atr_sma(self.h1, self.l1, self.c1)
        pos = np.searchsorted(self.t1 + HOUR_MS, self.t5, side="right") - 1      # 1h bars closed before the 5m open
        self.R5 = np.where(pos >= 0, self.atr1[np.maximum(pos, 0)], np.nan)
        self.ref_idx = np.flatnonzero(self.t5 % REFRESH_MS == 0)
        self.g = self.t5[self.ref_idx]
        self.offs, self.ks, self.wts, self.kl, self.kh = _expand(self.l, self.h, self.v, W_BIN)
        self.K0 = int(self.kl.min())
        self.nbins = int(self.kh.max()) - self.K0 + 1
        self.day0 = int(self.t5[self.start_idx] // DAY_MS) if self.start_idx < self.N else 0
        self.nd = int(self.t5[-1] // DAY_MS) - self.day0 + 1
        self._pivots = {}

    def pivots(self, n, k):
        key = (n, k)
        if key not in self._pivots:
            self._pivots[key] = meaningful_pivots(self.h1, self.l1, self.c1, n, k)
        return self._pivots[key]

    def _add(self, vol, s, e):
        a, b = self.offs[s], self.offs[e]
        ks, w = self.ks[a:b], self.wts[a:b]
        if e - s > 300:
            lo = int(ks.min())
            vol[lo - self.K0:lo - self.K0 + int(ks.max()) - lo + 1] += np.bincount(ks - lo, weights=w)
        else:
            np.add.at(vol, ks - self.K0, w)

    def developing(self, anchors):
        """Incremental profile from anchor_ms (per refresh; -1 = none) to the refresh. Returns (3, nref): poc, vah, val."""
        nref = len(self.ref_idx)
        out = np.full((3, nref), np.nan)
        vol = np.zeros(self.nbins)
        cur = None; start = added = 0; kmin = kmax = 0
        for r in range(nref):
            a = int(anchors[r])
            if a < 0:
                continue
            j = int(self.ref_idx[r])
            if a != cur:
                if cur is not None:
                    vol[kmin - self.K0:kmax - self.K0 + 1] = 0.0
                cur = a
                start = added = int(np.searchsorted(self.t5, a))
                kmin, kmax = 1 << 60, -(1 << 60)
            if j > added:
                self._add(vol, added, j)
                kmin = min(kmin, int(self.kl[added:j].min())); kmax = max(kmax, int(self.kh[added:j].max()))
                added = j
            if j - start < MIN_DEV_BARS:
                continue
            res = _levels_from_bins(vol[kmin - self.K0:kmax - self.K0 + 1], kmin, W_BIN)
            if res:
                out[0, r], out[1, r], out[2, r] = res
        return out

    def static_levels(self, seg_start, seg_end):
        """Profile of bars in [seg_start, seg_end) ms per refresh (-1 = none), cached per unique segment."""
        nref = len(seg_start)
        out = np.full((3, nref), np.nan)
        valid = (np.asarray(seg_start) >= 0) & (np.asarray(seg_end) > np.asarray(seg_start))
        if not valid.any():
            return out
        pairs = np.stack([np.asarray(seg_start)[valid], np.asarray(seg_end)[valid]], 1)
        uniq, inv = np.unique(pairs, axis=0, return_inverse=True)
        inv = np.asarray(inv).reshape(-1)
        res = np.full((3, len(uniq)), np.nan)
        for u, (a, b) in enumerate(uniq):
            s, e = int(np.searchsorted(self.t5, a)), int(np.searchsorted(self.t5, b))
            if e <= s:
                continue
            ks, w = self.ks[self.offs[s]:self.offs[e]], self.wts[self.offs[s]:self.offs[e]]
            lo = int(ks.min())
            seg = np.bincount(ks - lo, weights=w, minlength=int(ks.max()) - lo + 1)
            r = _levels_from_bins(seg, lo, W_BIN)
            if r:
                res[:, u] = r
        out[:, valid] = res[:, inv]
        return out

    # ---- families: each returns (3, nref) levels [poc, vah, val] at every 15-minute refresh
    def family_levels(self, fam):
        g = self.g
        day = g // DAY_MS
        none = np.full(len(g), -1, np.int64)
        if fam == "session":
            return self.developing(day * DAY_MS)
        if fam == "weekly":
            return self.developing((day - ((day + 3) % 7)) * DAY_MS)
        if fam == "prior_day":
            return self.static_levels((day - 1) * DAY_MS, day * DAY_MS)
        if fam == "prior_week":
            ws = (day - ((day + 3) % 7)) * DAY_MS
            return self.static_levels(ws - 7 * DAY_MS, ws)
        m = re.fullmatch(r"(A1|A2)_n(\d+)_k(\d+)", fam)
        if not m:
            raise ValueError(fam)
        kind, n, k = m.group(1), int(m.group(2)), int(m.group(3))
        hi, lo = self.pivots(n, k)
        ih = last_confirmed_vec(hi, self.t1, n, g)
        il = last_confirmed_vec(lo, self.t1, n, g)
        if kind == "A1":
            both = (ih >= 0) & (il >= 0)
            a, b = np.minimum(ih, il), np.maximum(ih, il)
            s = np.where(both, self.t1[np.maximum(a, 0)], -1)
            e = np.where(both, self.t1[np.maximum(b, 0)] + HOUR_MS, -1)
            return self.static_levels(s, e)
        last = np.maximum(ih, il)
        return self.developing(np.where(last >= 0, self.t1[np.maximum(last, 0)], none))

    # ---- level stream -> events
    def ffill(self, per_ref):
        pos = np.searchsorted(self.ref_idx, np.arange(self.N), side="right") - 1
        return np.where(pos >= 0, per_ref[np.maximum(pos, 0)], np.nan)

    def events(self, lev5):
        c, h, l = self.c, self.h, self.l
        L = lev5[1:]
        with np.errstate(invalid="ignore"):
            m = (l[1:] <= L) & (L <= h[1:]) & (c[:-1] != L) & (self.R5[1:] > 0)
        jj = np.flatnonzero(m) + 1
        jj = jj[jj >= self.start_idx]
        Lj = lev5[jj]; Rj = self.R5[jj]
        side = np.where(c[jj - 1] > Lj, 1, -1)
        ex, kind, eb = resolve_events(self.o, h, l, c, jj, side, Lj, Rj, H_BARS)
        good = kind >= 0
        jj, Lj, Rj, side, ex, kind, eb = (x[good] for x in (jj, Lj, Rj, side, ex, kind, eb))
        keep = select_events(jj, eb)
        jj, Lj, Rj, side, ex, kind = (x[keep] for x in (jj, Lj, Rj, side, ex, kind))
        return {"t": self.t5[jj], "kind": kind,
                "gross": gross_r(side, Lj, Rj, ex),
                "net_t": net_r(side, Lj, Rj, ex, kind, "taker") if len(jj) else np.zeros(0),
                "net_m": net_r(side, Lj, Rj, ex, kind, "maker") if len(jj) else np.zeros(0)}

    def placebo_ref(self, per_ref):
        d = PLACEBO_D[(self.g // REFRESH_MS) % 8]
        return per_ref + d * self.R5[self.ref_idx]


def all_families():
    fams = ["session", "weekly", "prior_day", "prior_week"]
    for kind in ("A1", "A2"):
        for n in PIVOT_NS:
            for k in PIVOT_KS:
                fams.append(f"{kind}_n{n}_k{k}")
    return fams


# ------------------------------------------------------------------ statistics
def _years(t):
    return (t.astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970)


def _day_sums(ctx, ev, key):
    d = (ev["t"] // DAY_MS - ctx.day0).astype(np.int64)
    return np.bincount(d, weights=ev[key], minlength=ctx.nd), np.bincount(d, minlength=ctx.nd).astype(float)


def _ci(x):
    if np.all(np.isnan(x)):
        return None
    return [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]


def _stream_stats(ctx, ev, idx):
    n = len(ev["t"])
    if n == 0:
        return {"n": 0, "flag": "below Tom's 300-event bar"}
    k = ev["kind"]
    s, cnt = _day_sums(ctx, ev, "net_t")
    yrs = _years(ev["t"])
    return {
        "n": int(n), "hit_pct": float((k == KIND_TARGET).mean() * 100), "stop_pct": float((k == KIND_STOP).mean() * 100),
        "timeout_pct": float((k == KIND_TIMEOUT).mean() * 100),
        "mean_gross_R": float(ev["gross"].mean()), "mean_net_R_taker": float(ev["net_t"].mean()),
        "mean_net_R_maker": float(ev["net_m"].mean()),
        "ci95_net_R_taker": _ci(boot_stat(s, cnt, idx)),
        "longest_losing_streak": int(longest_losing_streak(ev["net_t"])),
        "by_year": {int(y): {"n": int((yrs == y).sum()), "mean_net_R_taker": float(ev["net_t"][yrs == y].mean())}
                    for y in np.unique(yrs)},
        "flag": "below Tom's 300-event bar" if n < MIN_EVENTS else "",
    }


_G = {}


def _init_worker(d, start_ms):
    _G["ctx"] = Ctx(d, start_ms)
    _G["idx"] = np.random.default_rng(BOOT_SEED).integers(0, _G["ctx"].nd, size=(N_BOOT, _G["ctx"].nd), dtype=np.int32)


def run_family(fam):
    t0 = time.time()
    ctx, idx = _G["ctx"], _G["idx"]
    lev = ctx.family_levels(fam)
    res = {}
    for li, name in enumerate(LEVELS):
        real_ref = lev[li]
        ev_r = ctx.events(ctx.ffill(real_ref))
        ev_p = ctx.events(ctx.ffill(ctx.placebo_ref(real_ref)))
        entry = {"real": _stream_stats(ctx, ev_r, idx), "placebo": _stream_stats(ctx, ev_p, idx)}
        if len(ev_r["t"]) and len(ev_p["t"]):
            sr, cr = _day_sums(ctx, ev_r, "net_t"); sp, cp = _day_sums(ctx, ev_p, "net_t")
            diff = boot_stat(sr, cr, idx) - boot_stat(sp, cp, idx)
            entry["diff_net_R_taker"] = float(ev_r["net_t"].mean() - ev_p["net_t"].mean())
            entry["diff_ci95"] = _ci(diff)
        res[name] = entry
    return fam, res, time.time() - t0


# ------------------------------------------------------------------ side table (R-5Ljf-7, NO-SOURCE measurement)
def poc_body_table(d, start_ms, end_ms):
    t, o, h, l, c, v = (d[k] for k in ("t5", "o5", "h5", "l5", "c5", "v5"))
    day = t // DAY_MS
    days = np.unique(day[(t >= start_ms) & (t < end_ms)])
    share, off = [], []
    for dd in days:
        s, e = np.searchsorted(day, dd, "left"), np.searchsorted(day, dd, "right")
        if e - s < 288:
            continue
        p = build_profile(l[s:e], h[s:e], v[s:e], W_BIN)
        if not p:
            continue
        lo_b, hi_b = np.minimum(o[s:e], c[s:e]), np.maximum(o[s:e], c[s:e])
        share.append(float(((lo_b <= p["poc_price"]) & (p["poc_price"] <= hi_b)).mean()))
        off.append(float((p["poc_price"] - np.median((lo_b + hi_b) / 2)) / W_BIN))

    def q(x):
        return {"q1": float(np.percentile(x, 25)), "median": float(np.median(x)), "q3": float(np.percentile(x, 75))} if x else None
    return {"days": len(share), "share_of_bodies_containing_poc": q(share), "poc_minus_median_body_mid_in_bins": q(off)}


# ------------------------------------------------------------------ output
def _ts(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")


def _f(x, nd=3):
    return "-" if x is None else f"{x:.{nd}f}"


def render_md(out, meta, args):
    L = []
    L.append(f"# VP pivot probe phase 2 results ({args['start']} .. {args['end']})")
    L.append("")
    L.append(f"Data: {meta['rows_1m']} 1m rows from {_ts(meta['first_ms'])} to {_ts(meta['last_ms'])} UTC, {meta['files']} files. "
             f"Gaps: {meta['gap_count']} gaps, {meta['missing_minutes']} missing minutes; incomplete (dropped) buckets: "
             f"{meta['incomplete_5m_buckets']} x 5m, {meta['incomplete_1h_buckets']} x 1h; off-grid 1m stamps {meta['off_grid_1m']}.")
    if meta["largest_gaps"]:
        L.append("Largest gaps: " + "; ".join(f"{_ts(g['start_ms'])} +{g['minutes']}m" for g in meta["largest_gaps"][:5]))
    L.append(f"Params: w={W_BIN}, H={H_BARS} x 5m (NO-SOURCE default, not tuned), R=ATR14(1h) SMA, fees taker {BINANCE_TAKER} / maker {BINANCE_MAKER}, "
             f"warmup {WARMUP_DAYS}d, bootstrap {N_BOOT} day-block resamples seed {BOOT_SEED}. Events counted from {args['start']}.")
    L.append("`<300` = below Tom's 300-event bar. Streak = longest run of net_R<0 (taker). CI = 95% day-block bootstrap of mean net_R (taker).")
    L.append("")
    L.append("| family | level | n | hit% | stop% | to% | gross R | net R taker | CI95 | net R maker | streak | pl n | pl net R | real-pl | diff CI95 | flag |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for fam, lv in out["families"].items():
        for name in LEVELS:
            e = lv[name]; r, p = e["real"], e["placebo"]
            if r["n"] == 0:
                L.append(f"| {fam} | {name} | 0 | | | | | | | | | {p['n']} | | | | <300 |")
                continue
            ci = r["ci95_net_R_taker"]; dci = e.get("diff_ci95")
            L.append(f"| {fam} | {name} | {r['n']} | {r['hit_pct']:.1f} | {r['stop_pct']:.1f} | {r['timeout_pct']:.1f} | "
                     f"{_f(r['mean_gross_R'])} | {_f(r['mean_net_R_taker'])} | {_f(ci[0]) + '..' + _f(ci[1]) if ci else '-'} | "
                     f"{_f(r['mean_net_R_maker'])} | {r['longest_losing_streak']} | {p['n']} | {_f(p.get('mean_net_R_taker'))} | "
                     f"{_f(e.get('diff_net_R_taker'))} | {_f(dci[0]) + '..' + _f(dci[1]) if dci else '-'} | {'<300' if r['flag'] else ''} |")
    L.append("")
    L.append("## Real stream by calendar year (n / mean net R taker)")
    L.append("")
    for fam, lv in out["families"].items():
        for name in LEVELS:
            by = lv[name]["real"].get("by_year", {})
            if by:
                L.append(f"- {fam} {name}: " + ", ".join(f"{y}: {v['n']} / {_f(v['mean_net_R_taker'])}" for y, v in sorted(by.items())))
    L.append("")
    st = out["side_table_poc_vs_bodies"]
    L.append("## Side table R-5Ljf-7 (NO-SOURCE measurement): prior_day POC vs that day's 5m candle bodies")
    L.append("")
    if st["share_of_bodies_containing_poc"]:
        a, b = st["share_of_bodies_containing_poc"], st["poc_minus_median_body_mid_in_bins"]
        L.append(f"Complete days: {st['days']}. Share of bodies containing POC: q1 {a['q1']:.3f}, median {a['median']:.3f}, q3 {a['q3']:.3f}. "
                 f"(POC - median body midpoint)/w: q1 {b['q1']:.2f}, median {b['median']:.2f}, q3 {b['q3']:.2f}.")
    L.append("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--families", default="")
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    a = ap.parse_args(argv)
    t0 = time.time()
    st = datetime.strptime(a.start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    en = datetime.strptime(a.end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)   # end date inclusive
    start_ms, end_ms = int(st.timestamp() * 1000), int(en.timestamp() * 1000)
    d = load_bars(start_ms - WARMUP_DAYS * DAY_MS, end_ms)
    meta = d["meta"]
    lo5 = int(np.searchsorted(d["t5"], start_ms - WARMUP_DAYS * DAY_MS)); hi5 = int(np.searchsorted(d["t5"], end_ms))
    lo1 = int(np.searchsorted(d["t1"], start_ms - WARMUP_DAYS * DAY_MS)); hi1 = int(np.searchsorted(d["t1"], end_ms))
    sub = {k: (v[lo5:hi5] if k.endswith("5") else v[lo1:hi1]) for k, v in d.items() if k != "meta"}
    print(f"loaded {len(sub['t5'])} 5m / {len(sub['t1'])} 1h bars in {time.time() - t0:.1f}s; gaps {meta['gap_count']} "
          f"({meta['missing_minutes']} min)", flush=True)
    fams = [f for f in a.families.split(",") if f] or all_families()
    heavy = [f for f in fams if f in ("weekly", "session") or f.startswith("A2")]
    order = heavy + [f for f in fams if f not in heavy]
    results = {}
    if a.workers <= 1:
        _init_worker(sub, start_ms)
        it = map(run_family, order)
    else:
        pool = mp.Pool(a.workers, _init_worker, (sub, start_ms))
        it = pool.imap_unordered(run_family, order, chunksize=1)
    for fam, res, dt in it:
        results[fam] = res
        print(f"  {fam} done in {dt:.0f}s", flush=True)
    if a.workers > 1:
        pool.close(); pool.join()
    out = {
        "args": {"start": a.start, "end": a.end}, "coverage": meta,
        "params": {"w": W_BIN, "H_bars_5m": H_BARS, "warmup_days": WARMUP_DAYS, "n_boot": N_BOOT, "seed": BOOT_SEED,
                   "taker": BINANCE_TAKER, "maker": BINANCE_MAKER},
        "families": {f: results[f] for f in fams},
        "side_table_poc_vs_bodies": poc_body_table(sub, start_ms, end_ms),
    }
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "results.json", "w", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    with open(od / "results.md", "w", newline="\n") as fh:
        fh.write(render_md(out, meta, out["args"]))
    print(f"wrote {od / 'results.json'} and results.md; total {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
