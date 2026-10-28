"""Lazy per-day option-trade panel (Deribit history shards) with per-instrument time-sorted arrays.

Read-only on the data. Days are parsed once (optionally cached on disk as npz), kept in a small LRU, and
queried through numpy searchsorted. No query ever looks at data later than the stated time except
`first_fill`/`obs_range`, whose forward window is explicit in their arguments.
"""
import bisect  # noqa: F401
import csv
import gzip
import hashlib
import json
import math
import os
import re
import sys
from collections import OrderedDict

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from instruments import (DAY_MS, HOUR_MS, ms_to_ymd, parse_instrument, ymd_to_ms,  # noqa: E402
                         load_delivery_prices)

CACHE_VERSION = 1
FILL_EPS = 1e-9
_SHARD_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.jsonl\.gz$")
_NAN = float("nan")


def _daynum(ts_ms):
    return int(ts_ms // DAY_MS)


def parse_shard(path, daynum=None):
    """Parse one gz shard into filtered, instrument-sorted numpy arrays. Returns dict (see keys below)."""
    with gzip.open(path, "rb") as fh:
        raw = fh.read()
    lines = [ln for ln in raw.split(b"\n") if ln.strip()]
    n_bad = 0
    try:
        data = json.loads(b"[" + b",".join(lines) + b"]")
    except ValueError:
        data = []
        for ln in lines:
            try:
                data.append(json.loads(ln))
            except ValueError:
                n_bad += 1
    lo = daynum * DAY_MS if daynum is not None else None
    hi = lo + DAY_MS if lo is not None else None
    names, ts, price, iv, idx, amt, dr = [], [], [], [], [], [], []
    n_flag = n_out = 0
    for d in data:
        if not isinstance(d, dict):
            n_bad += 1
            continue
        if d.get("block_trade_id") or d.get("combo_id") or d.get("liquidation"):
            n_flag += 1
            continue
        try:
            t = int(d["timestamp"])
            p = float(d["price"])
            a = float(d["amount"])
            ix = float(d["index_price"])
            nm = d["instrument_name"]
            side = d["direction"]
        except (KeyError, TypeError, ValueError):
            n_bad += 1
            continue
        if not (p > 0.0 and a > 0.0 and ix > 0.0) or math.isinf(p) or math.isinf(a) or math.isinf(ix):
            n_bad += 1
            continue
        if side == "buy":
            s = 1
        elif side == "sell":
            s = -1
        else:
            n_bad += 1
            continue
        if parse_instrument(nm) is None:
            n_bad += 1
            continue
        if lo is not None and not (lo <= t < hi):
            n_out += 1
            continue
        v = d.get("iv")
        try:
            v = float(v) if v is not None else _NAN
        except (TypeError, ValueError):
            v = _NAN
        names.append(nm)
        ts.append(t)
        price.append(p)
        iv.append(v)
        idx.append(ix)
        amt.append(a)
        dr.append(s)
    n = len(names)
    ts_a = np.asarray(ts, dtype=np.int64)
    seq = np.arange(n)
    if n:
        uniq, ids = np.unique(np.asarray(names), return_inverse=True)
        order = np.lexsort((seq, ts_a, ids))
        ids_s = ids[order]
        starts = np.searchsorted(ids_s, np.arange(len(uniq) + 1)).astype(np.int64)
        g_order = np.lexsort((seq, ts_a))
    else:
        uniq = np.asarray([], dtype="<U1")
        order = g_order = np.asarray([], dtype=np.int64)
        starts = np.zeros(1, dtype=np.int64)
    price_a = np.asarray(price, dtype=np.float64)
    iv_a = np.asarray(iv, dtype=np.float64)
    idx_a = np.asarray(idx, dtype=np.float64)
    amt_a = np.asarray(amt, dtype=np.float64)
    dr_a = np.asarray(dr, dtype=np.int8)
    return {
        "names": uniq, "starts": starts,
        "ts": ts_a[order], "price": price_a[order], "iv": iv_a[order], "index": idx_a[order],
        "amount": amt_a[order], "dir": dr_a[order],
        "g_ts": ts_a[g_order], "g_index": idx_a[g_order],
        "counts": np.asarray([len(data), n, n_flag, n_bad, n_out], dtype=np.int64),
    }


class _Day:
    __slots__ = ("daynum", "names", "slices", "first", "last", "name_pos", "ts", "price", "iv", "index",
                 "amount", "dir", "g_ts", "g_index", "counts", "_by_expiry")

    def __init__(self, daynum, arrs):
        self.daynum = daynum
        self.names = [str(x) for x in arrs["names"]]
        starts = arrs["starts"]
        self.slices = {nm: (int(starts[i]), int(starts[i + 1])) for i, nm in enumerate(self.names)}
        self.ts = arrs["ts"]
        self.price = arrs["price"]
        self.iv = arrs["iv"]
        self.index = arrs["index"]
        self.amount = arrs["amount"]
        self.dir = arrs["dir"]
        self.g_ts = arrs["g_ts"]
        self.g_index = arrs["g_index"]
        self.counts = arrs["counts"]
        if self.names:
            self.first = self.ts[starts[:-1]]
            self.last = self.ts[starts[1:] - 1]
        else:
            self.first = self.last = np.zeros(0, dtype=np.int64)
        self._by_expiry = None

    @property
    def by_expiry(self):
        if self._by_expiry is None:
            m = {}
            for nm in self.names:
                inst = parse_instrument(nm)
                if inst is not None:
                    m.setdefault(inst.expiry_ms, []).append(nm)
            self._by_expiry = m
        return self._by_expiry


def _read_csv_cols(path, cols):
    """Return {col: np.ndarray(float)} for the given numeric columns; missing file -> empty arrays."""
    out = {c: [] for c in cols}
    if path and os.path.exists(path):
        with open(path, "r", newline="") as fh:
            for row in csv.DictReader(fh):
                try:
                    vals = [float(row[c]) for c in cols]
                except (KeyError, TypeError, ValueError):
                    continue
                for c, v in zip(cols, vals):
                    out[c].append(v)
    return {c: np.asarray(v, dtype=np.float64) for c, v in out.items()}


class Panel:
    def __init__(self, trades_dir, hist_dir=None, cache_days=16, cache_dir=None):
        self.trades_dir = os.path.abspath(trades_dir)
        self.hist_dir = os.path.abspath(hist_dir) if hist_dir else os.path.dirname(self.trades_dir)
        self.cache_days = max(2, int(cache_days))
        self.cache_dir = os.path.abspath(cache_dir) if cache_dir else None
        self._lru = OrderedDict()
        self._chain_cache = OrderedDict()
        self._files = {}
        self._csv = {}
        self.stats = {"days_loaded": 0, "days_from_cache": 0, "days_parsed": 0, "parse_seconds": 0.0}
        self.reload_listing()

    # ---- listing / coverage -------------------------------------------------------------------
    def reload_listing(self):
        self._files = {}
        if os.path.isdir(self.trades_dir):
            for fn in os.listdir(self.trades_dir):
                m = _SHARD_RE.match(fn)  # *.tmp and the manifest never match
                if m:
                    self._files[_daynum(ymd_to_ms(m.group(1)))] = os.path.join(self.trades_dir, fn)
        self._lru.clear()
        self._chain_cache.clear()

    def available_dates(self):
        return [ms_to_ymd(dn * DAY_MS) for dn in sorted(self._files)]

    def has_day(self, date_str):
        return _daynum(ymd_to_ms(date_str)) in self._files

    def date_range(self):
        if not self._files:
            return (None, None)
        return (ms_to_ymd(min(self._files) * DAY_MS), ms_to_ymd(max(self._files) * DAY_MS))

    def coverage(self, start, end):
        """Days with a shard vs calendar days in [start, end] (inclusive date strings)."""
        d0, d1 = _daynum(ymd_to_ms(start)), _daynum(ymd_to_ms(end))
        total = max(0, d1 - d0 + 1)
        missing = [ms_to_ymd(d * DAY_MS) for d in range(d0, d1 + 1) if d not in self._files]
        return {"calendar_days": total, "days_with_shard": total - len(missing), "missing": missing}

    # ---- day loading --------------------------------------------------------------------------
    def _cache_path(self, daynum):
        key = hashlib.sha1(self.trades_dir.encode("utf-8")).hexdigest()[:10]
        return os.path.join(self.cache_dir, "%s_%s.npz" % (key, ms_to_ymd(daynum * DAY_MS)))

    def _load_day(self, daynum):
        path = self._files.get(daynum)
        if path is None:
            return None
        import time
        t0 = time.time()
        st = os.stat(path)
        meta = np.asarray([CACHE_VERSION, st.st_size, st.st_mtime_ns], dtype=np.int64)
        arrs = None
        cpath = self._cache_path(daynum) if self.cache_dir else None
        if cpath and os.path.exists(cpath):
            try:
                with np.load(cpath, allow_pickle=False) as z:
                    if np.array_equal(z["meta"], meta):
                        arrs = {k: z[k] for k in z.files if k != "meta"}
            except (OSError, ValueError, KeyError):
                arrs = None
        if arrs is not None:
            self.stats["days_from_cache"] += 1
        else:
            arrs = parse_shard(path, daynum)
            self.stats["days_parsed"] += 1
            if cpath:
                os.makedirs(self.cache_dir, exist_ok=True)
                tmp = cpath + ".tmp.npz"
                np.savez(tmp, meta=meta, **arrs)
                os.replace(tmp, cpath)
        self.stats["days_loaded"] += 1
        self.stats["parse_seconds"] += time.time() - t0
        return _Day(daynum, arrs)

    def _day(self, daynum):
        d = self._lru.get(daynum)
        if d is not None:
            self._lru.move_to_end(daynum)
            return d
        d = self._load_day(daynum)
        if d is None:
            return None
        self._lru[daynum] = d
        while len(self._lru) > self.cache_days:
            self._lru.popitem(last=False)
        return d

    def day_counts(self, date_str):
        """(raw, kept, flag_dropped, bad_dropped, out_of_day_dropped) for a day, or None."""
        d = self._day(_daynum(ymd_to_ms(date_str)))
        return None if d is None else tuple(int(x) for x in d.counts)

    # ---- spec queries -------------------------------------------------------------------------
    def last_obs(self, instrument, ts_ms, lookback_ms):
        """Latest kept trade of `instrument` with ts_ms - lookback_ms < ts <= ts_ms, else None."""
        lo = ts_ms - lookback_ms
        for dn in range(_daynum(ts_ms), _daynum(lo) - 1, -1):
            day = self._day(dn)
            if day is None:
                continue
            sl = day.slices.get(instrument)
            if sl is None:
                continue
            i0, i1 = sl
            k = int(np.searchsorted(day.ts[i0:i1], ts_ms, side="right"))
            if k == 0:
                continue
            j = i0 + k - 1
            t = int(day.ts[j])
            if t <= lo:
                return None
            return {"price": float(day.price[j]), "iv": float(day.iv[j]),
                    "index": float(day.index[j]), "ts": t}
        return None

    def live_instruments(self, ts_ms, lookback_ms):
        """Names with a kept trade in (ts_ms - lookback_ms, ts_ms]."""
        lo = ts_ms - lookback_ms
        out = set()
        for dn in range(_daynum(lo), _daynum(ts_ms) + 1):
            day = self._day(dn)
            if day is None or not day.names:
                continue
            cand = np.nonzero((day.first <= ts_ms) & (day.last > lo))[0]
            for i in cand:
                nm = day.names[i]
                if nm in out:
                    continue
                if day.first[i] > lo:
                    out.add(nm)
                    continue
                i0, i1 = day.slices[nm]
                k = int(np.searchsorted(day.ts[i0:i1], lo, side="right"))
                if i0 + k < i1 and day.ts[i0 + k] <= ts_ms:
                    out.add(nm)
        return out

    def first_fill(self, instrument, side, ts_ms, window_ms, size=1.0, slip_pct=0.0):
        """Fill our order of `side` ('sell'|'buy') against taker prints of the same word in
        [ts_ms, ts_ms + window_ms]. Needs cumulative same-direction amount >= size (counted from ts_ms up to
        and including the fill print). Fill price = completing print's price (+/- slip_pct, adverse)."""
        want = -1 if side == "sell" else 1
        if side not in ("sell", "buy"):
            raise ValueError("side must be 'buy' or 'sell'")
        t_end = ts_ms + window_ms
        cum = 0.0
        for dn in range(_daynum(ts_ms), _daynum(t_end) + 1):
            day = self._day(dn)
            if day is None:
                continue
            sl = day.slices.get(instrument)
            if sl is None:
                continue
            i0, i1 = sl
            tsv = day.ts[i0:i1]
            a = int(np.searchsorted(tsv, ts_ms, side="left"))
            b = int(np.searchsorted(tsv, t_end, side="right"))
            if b <= a:
                continue
            m = day.dir[i0 + a:i0 + b] == want
            if not m.any():
                continue
            amts = np.where(m, day.amount[i0 + a:i0 + b], 0.0)
            cs = cum + np.cumsum(amts)
            hit = np.nonzero(m & (cs + FILL_EPS >= size))[0]
            if hit.size:
                j = i0 + a + int(hit[0])
                px = float(day.price[j])
                if slip_pct:
                    px = px * (1.0 - slip_pct) if side == "sell" else px * (1.0 + slip_pct)
                return {"price": px, "ts": int(day.ts[j]), "index": float(day.index[j])}
            cum = float(cs[-1])
        return None

    # ---- extras -------------------------------------------------------------------------------
    def chain_obs(self, ts_ms, expiry_ms, lookback_ms):
        """{name: last_obs} for every instrument of `expiry_ms` that traded in (ts-lookback, ts]. Memoised;
        the returned dict is shared - do not mutate."""
        key = (ts_ms, expiry_ms, lookback_ms)
        hit = self._chain_cache.get(key)
        if hit is not None:
            return hit
        lo = ts_ms - lookback_ms
        found = {}
        for dn in range(_daynum(ts_ms), _daynum(lo) - 1, -1):
            day = self._day(dn)
            if day is None:
                continue
            for nm in day.by_expiry.get(expiry_ms, ()):
                if nm in found:
                    continue
                i0, i1 = day.slices[nm]
                k = int(np.searchsorted(day.ts[i0:i1], ts_ms, side="right"))
                if k == 0:
                    continue
                j = i0 + k - 1
                t = int(day.ts[j])
                if t <= lo:
                    continue
                found[nm] = {"price": float(day.price[j]), "iv": float(day.iv[j]),
                             "index": float(day.index[j]), "ts": t}
        self._chain_cache[key] = found
        while len(self._chain_cache) > 512:
            self._chain_cache.popitem(last=False)
        return found

    def live_expiries(self, ts_ms, lookback_ms):
        out = set()
        for nm in self.live_instruments(ts_ms, lookback_ms):
            inst = parse_instrument(nm)
            if inst is not None:
                out.add(inst.expiry_ms)
        return sorted(out)

    def index_at(self, ts_ms, lookback_ms):
        """Index price of the latest kept trade (any instrument) in (ts-lookback, ts], else None."""
        lo = ts_ms - lookback_ms
        for dn in range(_daynum(ts_ms), _daynum(lo) - 1, -1):
            day = self._day(dn)
            if day is None or day.g_ts.size == 0:
                continue
            k = int(np.searchsorted(day.g_ts, ts_ms, side="right"))
            if k == 0:
                continue
            if int(day.g_ts[k - 1]) <= lo:
                return None
            return float(day.g_index[k - 1])
        return None

    def obs_range(self, instrument, t0_ms, t1_ms):
        """All kept trades of `instrument` with t0 <= ts <= t1 as numpy arrays (time order)."""
        parts = {k: [] for k in ("ts", "price", "iv", "index", "amount", "dir")}
        for dn in range(_daynum(t0_ms), _daynum(t1_ms) + 1):
            day = self._day(dn)
            if day is None:
                continue
            sl = day.slices.get(instrument)
            if sl is None:
                continue
            i0, i1 = sl
            tsv = day.ts[i0:i1]
            a = int(np.searchsorted(tsv, t0_ms, side="left"))
            b = int(np.searchsorted(tsv, t1_ms, side="right"))
            if b > a:
                for k in parts:
                    parts[k].append(getattr(day, k)[i0 + a:i0 + b])
        out = {}
        for k, v in parts.items():
            if v:
                out[k] = np.concatenate(v)
            else:
                out[k] = np.zeros(0, dtype=np.int64 if k == "ts" else (np.int8 if k == "dir" else np.float64))
        return out

    # ---- side data (lazy) ---------------------------------------------------------------------
    def _lazy(self, key, fn):
        if key not in self._csv:
            self._csv[key] = fn()
        return self._csv[key]

    @property
    def delivery_prices(self):
        return self._lazy("delivery", lambda: load_delivery_prices(os.path.join(self.hist_dir, "delivery_prices.csv")))

    def settlement_price(self, date_str):
        return self.delivery_prices.get(date_str)

    @property
    def dvol_daily(self):
        return self._lazy("dvol", lambda: _rename(
            _read_csv_cols(os.path.join(self.hist_dir, "dvol_1d.csv"), ["ts_ms", "close"])))

    @property
    def perp_1h(self):
        return self._lazy("perp", lambda: _rename(_read_csv_cols(os.path.join(self.hist_dir, "perp_1h.csv"), ["ts_ms", "close"])))

    @property
    def funding(self):
        return self._lazy("funding", lambda: _rename(
            _read_csv_cols(os.path.join(self.hist_dir, "funding.csv"), ["ts_ms", "interest_1h"])))


def _rename(cols):
    out = dict(cols)
    out["ts"] = out.pop("ts_ms").astype(np.int64)
    return out
