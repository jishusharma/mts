"""G3 marking pack: seeded windows, causal pre-filters, blind chart drawing, marking sheets.

DEV only. Definitions live in research/layer_rebuild_2026-10-15/READER_PROTOCOL.md; every number here is OURS
(a definition or a window-selection filter), fixed before any outcome was read. Charts are drawn through Windows GDI+
(render_png.ps1) because Pillow/matplotlib are not installed on JIS-NB; the geometry is built here and is pure Python.

  python g3_pack.py counts              # candidate counts per row (no outcomes involved)
  python g3_pack.py build               # WINDOWS.csv, MARKING_SHEET_reader{1,2}.csv, ANSWER_KEY_CLOSED/KEY.csv
  python g3_pack.py draw --out DIR      # one PNG per window, rebuilt from WINDOWS.csv (PNGs are not committed)
"""
from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import hashlib
import json
import random
import statistics
import subprocess
import tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20261016
N_HALF = 10
MIN, HOUR, DAY = 60_000, 3_600_000, 86_400_000
BIN = 10.0  # footprint bin in USD (the fp field of orderflow_1m)
INTRA_DIR = r"F:\MTS\data\orderflow_1m"
DAILY_DIR = r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest\raw_1d\klines"
# Tom/Fabio footprint track DEV (task brief): 2024-12..2025-03. Daily/weekly rows: standard DEV (before 2024-07-01).
INTRA_FIRST, INTRA_EDGE0, INTRA_LAST = date(2024, 12, 2), date(2024, 12, 8), date(2025, 3, 31)
DAILY_FIRST, DAILY_EDGE0, DAILY_LAST = date(2020, 1, 1), date(2021, 3, 1), date(2024, 6, 30)

# code: label, family, timeframe, bars shown, minimum spacing between windows in bars, enriched quotas by tag
UNITS = {
    "TOM4": dict(label="TOM-4", fam="intra", tf=15, shown=288, space=48),
    "TOM6": dict(label="TOM-6", fam="intra", tf=30, shown=240, space=24),
    "TOM12": dict(label="TOM-12", fam="intra", tf=30, shown=240, space=24),
    "TOM15": dict(label="TOM-15", fam="intra", tf=30, shown=240, space=24),
    "FAB1": dict(label="FAB-1", fam="intra", tf=5, shown=288, space=72),
    "FAB4": dict(label="FAB-4", fam="intra", tf=5, shown=288, space=72),
    "FAB5": dict(label="FAB-5", fam="intra", tf=5, shown=288, space=72),
    "KRS1": dict(label="KR-S1", fam="daily", tf="1d", shown=180, space=10),
    "KRS8": dict(label="KR-S8", fam="daily", tf="1d", shown=180, space=10),
    "MAL25": dict(label="MAL-2/5", fam="daily", tf="1w", shown=60, space=4),
    "MAL1617": dict(label="MAL-16/17", fam="daily", tf="1d", shown=180, space=10, quota={"bear": 5, "bull": 5}),
}


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- intraday data (footprint 1m)
def load_intraday(data_dir=INTRA_DIR):
    rows = []
    d = INTRA_FIRST
    end_ms = int(datetime(INTRA_LAST.year, INTRA_LAST.month, INTRA_LAST.day, tzinfo=timezone.utc).timestamp() * 1000) + DAY
    while d <= INTRA_LAST:  # the date loop is the DEV fence: no file past INTRA_LAST is ever opened
        p = Path(data_dir) / f"{d.isoformat()}.csv.gz"
        if p.exists():
            with gzip.open(p, "rt", encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    if int(r["t"]) >= end_ms:  # timestamp fence (audit HIGH): a file may hold rows past the last allowed day
                        continue
                    rows.append(dict(t=int(r["t"]), o=float(r["o"]), h=float(r["h"]), l=float(r["l"]), c=float(r["c"]),
                                     buy=float(r["buy_vol"]), sell=float(r["sell_vol"]), delta=float(r["delta"]),
                                     cvd=float(r["cvd_day"]), bbn=int(r["b999_buy_n"]), bsn=int(r["b999_sell_n"]), fp=r["fp"]))
        d += timedelta(days=1)
    return rows


def aggregate(rows, tf_min):
    ms, out, cur = tf_min * MIN, [], None
    for k, r in enumerate(rows):
        b = r["t"] // ms * ms
        if cur is None or cur["t"] != b:
            if cur and cur["n"] == tf_min:
                out.append(cur)
            cur = dict(t=b, o=r["o"], h=r["h"], l=r["l"], c=r["c"], vol=0.0, delta=0.0, cvd=0.0, bbn=0, bsn=0, n=0)
        cur["h"], cur["l"], cur["c"] = max(cur["h"], r["h"]), min(cur["l"], r["l"]), r["c"]
        cur["vol"] += r["buy"] + r["sell"]
        cur["delta"] += r["delta"]
        cur["cvd"] = r["cvd"]
        cur["bbn"] += r["bbn"]
        cur["bsn"] += r["bsn"]
        cur["n"] += 1
    if cur and cur["n"] == tf_min:
        out.append(cur)
    return out


def fp_bins(r):
    v = r.get("_fp")
    if v is None:
        v = [(float(k), float(b) + float(s)) for k, b, s in (q.split(":") for q in r["fp"].split("|"))] if r["fp"] else []
        r["_fp"] = v
    return v


def value_area(profile):
    """70 % value area, contiguous bins from the POC, ties lower (same convention as chart_lab._value_area)."""
    if not profile:
        return None
    prices = sorted(profile)
    poc = max(prices, key=lambda p: (profile[p], -p))
    target, total = sum(profile.values()) * 0.70, profile[poc]
    lo = hi = prices.index(poc)
    while total < target and (lo > 0 or hi < len(prices) - 1):
        lower = profile[prices[lo - 1]] if lo else -1
        upper = profile[prices[hi + 1]] if hi < len(prices) - 1 else -1
        if upper > lower:
            hi += 1
            total += profile[prices[hi]]
        else:
            lo -= 1
            total += profile[prices[lo]]
    return prices[lo], prices[hi], poc


class Intra:
    """Causal helpers over the 1m rows; every method takes explicit time limits at or before the edge."""

    def __init__(self, rows, tf_min):
        self.rows, self.tf_ms = rows, tf_min * MIN
        self.rt = [r["t"] for r in rows]
        self.bars = aggregate(rows, tf_min)
        self.vwap = self._vwap()
        self.day_first = {}
        for k, b in enumerate(self.bars):
            self.day_first.setdefault(b["t"] // DAY, k)
        self._va = {}

    def _vwap(self):
        out, day, pv, vv = [], None, 0.0, 0.0
        for b in self.bars:
            if b["t"] // DAY != day:
                day, pv, vv = b["t"] // DAY, 0.0, 0.0
            pv += (b["h"] + b["l"] + b["c"]) / 3 * b["vol"]
            vv += b["vol"]
            out.append(pv / vv if vv > 0 else b["c"])
        return out

    def profile(self, t0, t1):
        prof = defaultdict(float)
        for r in self.rows[bisect.bisect_left(self.rt, t0):bisect.bisect_left(self.rt, t1)]:
            for price, vol in fp_bins(r):
                prof[price] += vol
        return prof

    def vpoc(self, t0, t1):
        prof = self.profile(t0, t1)
        return max(prof, key=lambda p: (prof[p], -p)) if prof else None

    def va_prior(self, t):
        day = t // DAY - 1
        if day not in self._va:
            self._va[day] = value_area(self.profile(day * DAY, (day + 1) * DAY))
        return self._va[day]


def bal_run(B, a, b, wpct):
    cs = [x["c"] for x in B[a:b + 1]]
    lo, hi = min(cs), max(cs)
    return (hi - lo) / cs[-1] * 100 <= wpct, lo, hi


# ---------------------------------------------------------------- pre-filters (OURS; causal: bars up to index i only)
def pf_tom4(B, i, cx):
    b, v = B[i], cx.vwap[i]
    end = b["t"] + cx.tf_ms
    for d in ("up", "down"):
        if (d == "up" and not (b["l"] <= v < b["c"])) or (d == "down" and not (b["h"] >= v > b["c"])):
            continue
        v0, v1, v2 = (cx.vpoc(end - 12 * HOUR, end - 8 * HOUR), cx.vpoc(end - 8 * HOUR, end - 4 * HOUR), cx.vpoc(end - 4 * HOUR, end))
        if None in (v0, v1, v2):
            continue
        if (d == "up" and v1 >= v0 + BIN and v2 >= v1 + BIN) or (d == "down" and v1 <= v0 - BIN and v2 <= v1 - BIN):
            return d
    return None


def pf_tom6(B, i, cx):
    ok, lo, hi = bal_run(B, i - 12, i - 1, 1.5)
    if not ok or B[i]["vol"] < statistics.fmean(x["vol"] for x in B[i - 12:i]):
        return None
    c = B[i]["c"]
    past = [x["c"] for x in B[max(0, i - 240):i - 12]]
    if c > hi and not any(hi <= p <= hi * 1.005 for p in past):
        return "up"
    if c < lo and not any(lo * 0.995 <= p <= lo for p in past):
        return "down"
    return None


def pf_tom12(B, i, cx):
    va = cx.va_prior(B[i]["t"])
    if not va or i < 4:
        return None
    val, vah, _ = va
    cl = [B[k]["c"] for k in range(i - 4, i + 1)]
    if val <= cl[4] <= vah:
        if all(c > vah for c in cl[:4]):
            return "failed_p_above"
        if all(c < val for c in cl[:4]):
            return "failed_b_below"
    return None


def pf_tom15(B, i, cx):
    ok, lo, hi = bal_run(B, i - 12, i - 1, 1.5)
    if not ok:
        return None
    b, p = B[i], B[i - 1]
    med = statistics.median(x["h"] - x["l"] for x in B[i - 21:i - 1])
    up3 = all(B[k]["c"] > B[k]["o"] for k in (i - 2, i - 1, i)) and B[i]["c"] > B[i - 1]["c"] > B[i - 2]["c"]
    dn3 = all(B[k]["c"] < B[k]["o"] for k in (i - 2, i - 1, i)) and B[i]["c"] < B[i - 1]["c"] < B[i - 2]["c"]
    outside = b["h"] > p["h"] and b["l"] < p["l"]
    inside = b["h"] <= p["h"] and b["l"] >= p["l"] and (p["h"] - p["l"]) >= 1.5 * med
    if (up3 or outside or inside) and b["h"] >= hi * (1 - 0.0015):
        return "top"
    if (dn3 or outside or inside) and b["l"] <= lo * (1 + 0.0015):
        return "bottom"
    return None


def pf_fab1(B, i, cx):
    ok, lo, hi = bal_run(B, i - 36, i - 1, 1.0)
    seg = B[i - 36:i]
    vol = sum(x["vol"] for x in seg)
    if not ok or vol <= 0:
        return None
    ratio, b = sum(x["delta"] for x in seg) / vol, B[i]
    if b["c"] > hi and ratio >= 0.10 and (b["bbn"] > 0 or B[i - 1]["bbn"] > 0):
        return "up"
    if b["c"] < lo and ratio <= -0.10 and (b["bsn"] > 0 or B[i - 1]["bsn"] > 0):
        return "down"
    return None


def pf_fab4(B, i, cx):
    va = cx.va_prior(B[i]["t"])
    j0 = cx.day_first.get(B[i]["t"] // DAY)
    if not va or j0 is None or i - j0 < 6:
        return None
    val, vah, _ = va
    if not (val <= B[j0]["c"] <= vah and val <= B[i]["c"] <= vah) or val <= B[i - 1]["c"] <= vah:
        return None
    above = B[i - 1]["c"] > vah
    run, k = 0, i - 1
    while k >= j0 and ((B[k]["c"] > vah) if above else (B[k]["c"] < val)):
        run, k = run + 1, k - 1
    return ("down" if above else "up") if run >= 4 else None  # READER_PROTOCOL sec.1 "outside P / break-in": at least 4 closes outside


def pf_fab5(B, i, cx):
    b = B[i]
    for side in ("long", "short"):
        lvl = b["l"] if side == "long" else b["h"]
        if side == "long":
            def touch(x): return abs(x["l"] - lvl) / lvl <= 0.0005 and x["delta"] < -0.15 * x["vol"] and x["c"] > lvl * 1.0003
        else:
            def touch(x): return abs(x["h"] - lvl) / lvl <= 0.0005 and x["delta"] > 0.15 * x["vol"] and x["c"] < lvl * 0.9997
        if not touch(b):
            continue
        sel = [i]
        for k in range(i - 1, i - 61, -1):
            if touch(B[k]) and sel[-1] - k >= 3:
                sel.append(k)
        if len(sel) < 3:
            continue
        held = all((x["c"] >= lvl * 0.9995) if side == "long" else (x["c"] <= lvl * 1.0005) for x in B[sel[-1]:i + 1])
        if held:
            return side
    return None


INTRA_PF = dict(TOM4=pf_tom4, TOM6=pf_tom6, TOM12=pf_tom12, TOM15=pf_tom15, FAB1=pf_fab1, FAB4=pf_fab4, FAB5=pf_fab5)


# ---------------------------------------------------------------- daily / weekly / monthly data
def load_daily(dir_path=DAILY_DIR):
    bars, end = {}, int(datetime.combine(DAILY_LAST + timedelta(days=1), datetime.min.time(), timezone.utc).timestamp() * 1000)
    for p in sorted(Path(dir_path).glob("BTCUSDT-1d-*.csv")):
        with open(p, newline="") as f:
            for row in csv.reader(f):
                if row and row[0].isdigit() and int(row[0]) < end:  # DEV fence: nothing from 2024-07-01 on is kept
                    bars[int(row[0])] = dict(t=int(row[0]), o=float(row[1]), h=float(row[2]), l=float(row[3]), c=float(row[4]), vol=float(row[5]))
    return [bars[k] for k in sorted(bars)]


def rsi14(closes):
    out = [None] * len(closes)
    if len(closes) < 15:
        return out
    g = [max(closes[k] - closes[k - 1], 0.0) for k in range(1, len(closes))]
    ls = [max(closes[k - 1] - closes[k], 0.0) for k in range(1, len(closes))]
    ag, al = sum(g[:14]) / 14, sum(ls[:14]) / 14
    for k in range(14, len(closes)):
        if k > 14:
            ag, al = (ag * 13 + g[k - 1]) / 14, (al * 13 + ls[k - 1]) / 14
        out[k] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def bbwp(closes, n=20, look=252):
    width = [None] * len(closes)
    for k in range(n - 1, len(closes)):
        w = closes[k - n + 1:k + 1]
        m = sum(w) / n
        width[k] = 4 * statistics.pstdev(w) / m
    out = [None] * len(closes)
    for k in range(n - 1 + look, len(closes)):
        out[k] = 100.0 * sum(1 for x in width[k - look:k] if x <= width[k]) / look
    return out


def weekly(daily):
    groups = defaultdict(list)
    for d in daily:
        groups[(d["t"] // DAY + 3) // 7].append(d)  # Monday-start UTC week; epoch day 0 is a Thursday
    out = []
    for k in sorted(groups):
        g = groups[k]
        if len(g) == 7:
            out.append(dict(t=g[0]["t"], o=g[0]["o"], h=max(x["h"] for x in g), l=min(x["l"] for x in g), c=g[-1]["c"], vol=sum(x["vol"] for x in g), end=g[-1]["t"] + DAY))
    return out


def monthly(daily):
    groups = defaultdict(list)
    for d in daily:
        dt = datetime.fromtimestamp(d["t"] / 1000, timezone.utc)
        groups[(dt.year, dt.month)].append(d)
    out = []
    for key in sorted(groups):
        g = groups[key]
        nxt = datetime.fromtimestamp(g[-1]["t"] / 1000 + DAY / 1000, timezone.utc)
        if nxt.month != key[1]:  # the last calendar day is present: month complete
            out.append(dict(t=g[0]["t"], c=g[-1]["c"], end=g[-1]["t"] + DAY))
    return out


class Daily:
    def __init__(self, daily):
        self.d = daily
        self.c = [x["c"] for x in daily]
        self.rsi, self.bbwp = rsi14(self.c), bbwp(self.c)
        self.w = weekly(daily)
        self.rsi_w = rsi14([x["c"] for x in self.w])
        self.m = monthly(daily)
        self.rsi_m = rsi14([x["c"] for x in self.m])
        self.m_end = [x["end"] for x in self.m]

    def rsi_m_at(self, t_end):
        k = bisect.bisect_right(self.m_end, t_end) - 1
        return self.rsi_m[k] if k >= 0 else None


def proof_candle(b, prev):
    rng = b["h"] - b["l"]
    if rng <= 0:
        return None
    body = abs(b["c"] - b["o"])
    lo_w, up_w = min(b["o"], b["c"]) - b["l"], b["h"] - max(b["o"], b["c"])
    if lo_w >= 2 * body and b["c"] >= b["l"] + 0.66 * rng:
        return "hammer"
    if up_w >= 2 * body and b["c"] <= b["l"] + 0.34 * rng:
        return "shooting_star"
    pb = (min(prev["o"], prev["c"]), max(prev["o"], prev["c"]))
    if (b["c"] > b["o"]) != (prev["c"] > prev["o"]) and min(b["o"], b["c"]) < pb[0] and max(b["o"], b["c"]) > pb[1]:
        return "engulf_bull" if b["c"] > b["o"] else "engulf_bear"
    if body <= 0.1 * rng:
        return "doji"
    return None


def pf_krs1(D, i):
    d = D.d
    b = d[i]
    kind = proof_candle(b, d[i - 1])
    if kind is None or b["vol"] < statistics.fmean(x["vol"] for x in d[i - 30:i]):
        return None
    side = "support" if kind in ("hammer", "engulf_bull") else "resistance" if kind in ("shooting_star", "engulf_bear") else "either"
    n_low = n_high = 0
    for k in range(max(3, i - 250), i - 3):  # swing points need 3 bars on each side, all at or before i - 1
        if d[k]["l"] < min(x["l"] for x in d[k - 3:k]) and d[k]["l"] < min(x["l"] for x in d[k + 1:k + 4]) and abs(d[k]["l"] - b["l"]) / b["l"] <= 0.015:
            n_low += 1
        if d[k]["h"] > max(x["h"] for x in d[k - 3:k]) and d[k]["h"] > max(x["h"] for x in d[k + 1:k + 4]) and abs(d[k]["h"] - b["h"]) / b["h"] <= 0.015:
            n_high += 1
    if (side in ("support", "either") and n_low >= 2) or (side in ("resistance", "either") and n_high >= 2):
        return kind
    return None


def pf_krs8(D, i):
    bw, c = D.bbwp, D.c
    if bw[i] is None or any(x is None for x in bw[i - 10:i]):
        return None
    if min(bw[i - 10:i]) <= 30 and bw[i] > 50 and (c[i] > max(c[i - 20:i]) or c[i] < min(c[i - 20:i])):
        return "up" if c[i] > max(c[i - 20:i]) else "down"
    return None


def pf_mal25(D, wk):
    r, rm = D.rsi_w, D.rsi_m_at(D.w[wk]["end"])
    if wk < 20 or r[wk] is None or r[wk - 3] is None or rm is None or rm <= 60:
        return None
    if max(r[wk - 12:wk - 1]) > 60 and r[wk] >= 60 and r[wk] > r[wk - 1] and 55 <= min(r[wk - 3:wk]) <= 66:
        return "rsi60_support"
    return None


def pf_mal1617(D, i):
    c, r, d = D.c, D.rsi, D.d
    if i < 80 or r[i] is None:
        return None
    hi20, lo20 = max(c[i - 19:i + 1]), min(c[i - 19:i + 1])
    # READER_PROTOCOL sec.1 RSI row: highest (lowest) close of the last 20 bars vs the highest (lowest) close in bars 5..60 before it
    bh = max(k for k in range(i - 19, i + 1) if c[k] == hi20)
    bl = max(k for k in range(i - 19, i + 1) if c[k] == lo20)
    if bh - 60 >= 0:
        a = max(range(bh - 60, bh - 4), key=lambda k: c[k])
        if c[a] < c[bh] and r[a] is not None and r[bh] is not None and r[a] > r[bh] + 2 and d[i]["c"] < d[i]["o"]:
            return "bear"
    if bl - 60 >= 0:
        a = min(range(bl - 60, bl - 4), key=lambda k: c[k])
        if c[a] > c[bl] and r[a] is not None and r[bl] is not None and r[a] < r[bl] - 2 and d[i]["c"] > d[i]["o"]:
            return "bull"
    return None


# ---------------------------------------------------------------- window selection (seeded)
def spaced_pick(order, taken, space, n):
    got = []
    for i in order:
        if len(got) >= n:
            break
        if all(abs(i - j) >= space for j in taken + got):
            got.append(i)
    return got


def pick(code, eligible, tag_of, quota=None, seed=SEED):
    """Half enriched (pre-filter true at the edge, seeded draw), half random; spaced; returns records unsorted."""
    u = UNITS[code]
    rng = random.Random(f"{seed}-{code}")
    cands = [i for i in eligible if tag_of(i)]
    rng.shuffle(cands)
    taken, recs = [], []
    quota = quota or {"*": N_HALF}
    for tag, n in quota.items():
        pool = [i for i in cands if tag == "*" or tag_of(i) == tag]
        got = spaced_pick(pool, taken, u["space"], n)
        taken += got
        recs += [dict(edge=i, half="enriched", tag=tag_of(i)) for i in got]
    rest = list(eligible)
    rng.shuffle(rest)
    got = spaced_pick(rest, taken, u["space"], N_HALF)
    recs += [dict(edge=i, half="random", tag=tag_of(i) or "") for i in got]
    rng.shuffle(recs)
    for k, r in enumerate(recs, 1):
        r["window_id"] = f"{code}-{k:02d}"
    return recs


def intra_units(rows):
    out = {}
    for code, u in UNITS.items():
        if u["fam"] != "intra":
            continue
        cx = Intra(rows, u["tf"])
        lo = int(datetime.combine(INTRA_EDGE0, datetime.min.time(), timezone.utc).timestamp() * 1000)
        elig = [i for i, b in enumerate(cx.bars) if b["t"] >= lo and i >= u["shown"]]
        out[code] = (cx, elig, lambda i, cx=cx, f=INTRA_PF[code]: f(cx.bars, i, cx))
    return out


def daily_units(daily):
    D = Daily(daily)
    lo = int(datetime.combine(DAILY_EDGE0, datetime.min.time(), timezone.utc).timestamp() * 1000)
    hi = int(datetime.combine(DAILY_LAST, datetime.min.time(), timezone.utc).timestamp() * 1000)
    days = [i for i, b in enumerate(D.d) if lo <= b["t"] <= hi and i >= 280]
    weeks = [k for k, w in enumerate(D.w) if lo <= w["end"] - DAY <= hi and k >= UNITS["MAL25"]["shown"] - 1]
    return D, dict(
        KRS1=(days, lambda i: pf_krs1(D, i)), KRS8=(days, lambda i: pf_krs8(D, i)),
        MAL25=(weeks, lambda k: pf_mal25(D, k)), MAL1617=(days, lambda i: pf_mal1617(D, i)))


def edge_end(code, cx_or_D, i):
    u = UNITS[code]
    if u["fam"] == "intra":
        return cx_or_D.bars[i]["t"] + cx_or_D.tf_ms
    return cx_or_D.w[i]["end"] if u["tf"] == "1w" else cx_or_D.d[i]["t"] + DAY


def build_windows(rows, daily):
    recs = []
    for code, (cx, elig, tag) in intra_units(rows).items():
        for r in pick(code, elig, tag):
            recs.append(dict(r, unit=code, end=edge_end(code, cx, r["edge"])))
    D, du = daily_units(daily)
    for code, (elig, tag) in du.items():
        for r in pick(code, elig, tag, UNITS[code].get("quota")):
            recs.append(dict(r, unit=code, end=edge_end(code, D, r["edge"])))
    return recs


# ---------------------------------------------------------------- drawing geometry (blind: no dates, % axis)
W_PX, H_PX, X0, X1 = 1400, 860, 70, 1300
GREEN, RED, GREY, TXT = "#39bd93", "#e66c6c", "#6b7a88", "#d7dee5"


def nice_step(span):
    for s in (0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 50, 100):
        if span / s <= 9:
            return s
    return 200


class Chart:
    def __init__(self, title, n):
        self.p = [dict(k="rect", x=0, y=0, w=W_PX, h=H_PX, c="#101820")]
        self.n, self.title = n, title
        self.text(12, 8, title, 14)

    def text(self, x, y, s, size=11, c=TXT):
        self.p.append(dict(k="text", x=x, y=y, s=s, c=c, size=size))

    def x(self, k):
        return X0 + (k + 0.5) * (X1 - X0) / self.n

    def panel(self, top, height, lo, hi, label, fmt="{:.2f}", step=None):
        self.top, self.h, self.lo, self.hi = top, height, lo, hi
        self.p.append(dict(k="line", pts=[[X0, top], [X1, top], [X1, top + height], [X0, top + height], [X0, top]], c="#2a3744", w=1))
        self.text(X0 + 4, top + 2, label, 11, GREY)
        step = step or (hi - lo) / 6
        v = (lo // step + 1) * step
        while v < hi:
            self.line([(X0, self.y(v)), (X1, self.y(v))], "#1b2733")
            self.text(8, self.y(v) - 7, fmt.format(v), 10, GREY)
            v += step

    def y(self, v):
        return self.top + self.h - (v - self.lo) / (self.hi - self.lo) * self.h

    def line(self, pts, c, w=1):
        pts = [[round(a, 1), round(b, 1)] for a, b in pts]
        if len(pts) >= 2:
            self.p.append(dict(k="line", pts=pts, c=c, w=w))

    def series(self, vals, c, w=1):
        run = []
        for k, v in enumerate(vals):
            if v is None:
                self.line(run, c, w)
                run = []
            else:
                run.append((self.x(k), self.y(v)))
        self.line(run, c, w)

    def seg(self, k0, k1, v, c, label=""):
        if not self.top <= self.y(v) <= self.top + self.h:
            return  # outside the visible price range: not drawn
        self.line([(self.x(k0) - 3, self.y(v)), (self.x(k1) + 3, self.y(v))], c, 1)
        if label:
            self.text(self.x(k1) + 4, self.y(v) - 7, label, 10, c)

    def bars(self, vals, base, color_of):
        w = max(1.0, (X1 - X0) / self.n * 0.6)
        for k, v in enumerate(vals):
            y0, y1 = self.y(base), self.y(v)
            self.p.append(dict(k="rect", x=round(self.x(k) - w / 2, 1), y=round(min(y0, y1), 1), w=round(w, 1), h=max(1.0, round(abs(y1 - y0), 1)), c=color_of(k, v)))


def draw_price(ch, vis, ref, top, height, hmargin=0.0):
    pct = lambda p: (p / ref - 1) * 100
    lo, hi = pct(min(b["l"] for b in vis)), pct(max(b["h"] for b in vis))
    pad = (hi - lo) * 0.04 or 0.1
    lo, hi = lo - pad, hi + pad
    ch.panel(top, height, lo, hi, "price, % from last close", "{:+.2f}%", nice_step(hi - lo))
    w = max(1.0, (X1 - X0) / ch.n * 0.6)
    for k, b in enumerate(vis):
        col = GREEN if b["c"] >= b["o"] else RED
        ch.line([(ch.x(k), ch.y(pct(b["h"]))), (ch.x(k), ch.y(pct(b["l"])))], col, 1)
        y0, y1 = ch.y(pct(b["o"])), ch.y(pct(b["c"]))
        ch.p.append(dict(k="rect", x=round(ch.x(k) - w / 2, 1), y=round(min(y0, y1), 1), w=round(w, 1), h=max(1.0, round(abs(y1 - y0), 1)), c=col))
    return pct


def draw_profile(ch, prof, pct, color="#7793aa"):
    if not prof:
        return
    mx = max(prof.values())
    for price, vol in prof.items():
        y = ch.y(pct(price))
        if ch.top <= y <= ch.top + ch.h:
            ch.line([(X1 + 4, y), (X1 + 4 + vol / mx * 80, y)], color, 2)


def hist_closes(closes, bins=20):
    if len(closes) < 2 or max(closes) == min(closes):
        return {}
    lo, hi = min(closes), max(closes)
    out = defaultdict(float)
    for c in closes:
        k = min(bins - 1, int((c - lo) / (hi - lo) * bins))
        out[lo + (k + 0.5) * (hi - lo) / bins] += 1
    return out


def intra_chart(code, cx, i, blind_id):
    u = UNITS[code]
    n, B = u["shown"], cx.bars
    if i - n + 1 < 0:
        raise ValueError("window starts before the first bar")
    vis = B[i - n + 1:i + 1]
    ch = Chart(f"{blind_id} | {u['label']} | BTCUSDT {u['tf']}m | last closed bar = right edge (offset 0) | dates hidden", n)
    ref = vis[-1]["c"]
    sub = {"TOM4": ["vol"], "TOM6": ["vol", "delta"], "TOM12": ["vol"], "TOM15": ["vol"], "FAB1": ["cvd", "delta"], "FAB4": ["delta"], "FAB5": ["delta"]}[code]
    price_h = 470 if len(sub) == 2 else 520
    pct = draw_price(ch, vis, ref, 36, price_h)
    day_k = {}
    for k, b in enumerate(vis):
        day_k.setdefault(b["t"] // DAY, []).append(k)
        if k % 24 == 0:  # bar offsets from the right edge, never a clock time (the edge's time of day is a side channel)
            ch.text(ch.x(k) - 8, ch.top + ch.h + 2, str(k - n + 1), 10, GREY)
        if b["t"] % DAY == 0:
            ch.line([(ch.x(k), ch.top), (ch.x(k), ch.top + ch.h)], "#7a6a2f", 1)
    if code in ("TOM4", "TOM6"):
        ch.series([pct(v) for v in cx.vwap[i - n + 1:i + 1]], "#e6c76a", 1)
        ch.text(X0 + 230, ch.top + 2, "yellow = session VWAP (00:00 UTC)", 11, "#e6c76a")
    if code in ("TOM4", "TOM12", "FAB4"):
        for d, ks in day_k.items():
            va = cx.va_prior(d * DAY)
            if va:
                for v, lab, col in ((va[1], "VAH", "#d98b65"), (va[0], "VAL", "#d98b65"), (va[2], "POC", "#55b9d1")):
                    ch.seg(ks[0], ks[-1], pct(v), col, lab if ks is list(day_k.values())[-1] else "")
    if code == "TOM4":
        end = vis[-1]["t"] + cx.tf_ms
        for t0 in (end - 12 * HOUR, end - 8 * HOUR, end - 4 * HOUR):  # the three 4h blocks the pre-filter compares
            v = cx.vpoc(t0, t0 + 4 * HOUR)
            ks = [k for k, b in enumerate(vis) if t0 <= b["t"] < t0 + 4 * HOUR]
            if v and ks:
                ch.seg(ks[0], ks[-1], pct(v), "#c78cff")
    if code == "TOM6":
        end = vis[-1]["t"] + cx.tf_ms
        draw_profile(ch, cx.profile(end - 5 * DAY, end), pct)
    if code in ("TOM12", "FAB1"):
        d0 = vis[-1]["t"] // DAY
        draw_profile(ch, hist_closes([b["c"] for b in B[:i + 1] if b["t"] // DAY == d0]), pct, "#e6c76a")
    if code == "TOM15":
        win = [b["c"] for b in B[i - 12:i]]  # always drawn: drawing only when a balance exists would disclose the pre-filter
        ch.seg(n - 13, n - 2, pct(max(win)), "#d98b65", "range hi (12 closes)")
        ch.seg(n - 13, n - 2, pct(min(win)), "#d98b65", "range lo (12 closes)")
    if code == "FAB5":
        end = vis[-1]["t"] + cx.tf_ms
        prof = cx.profile(end - DAY, end)
        for price in sorted(prof, key=prof.get, reverse=True)[:3]:
            ch.seg(0, n - 1, pct(price), "#c78cff", "top volume bin")
    if code in ("FAB1", "FAB4", "FAB5"):
        for k, b in enumerate(vis):
            for cnt, col, yy in ((b["bbn"], GREEN, b["l"]), (b["bsn"], RED, b["h"])):
                if cnt:
                    ch.p.append(dict(k="text", x=round(ch.x(k) - 4, 1), y=round(ch.y(pct(yy)) + (2 if yy == b["l"] else -14), 1), s="^" if col == GREEN else "v", c=col, size=11))
    top = 36 + price_h + 24
    for kind in sub:
        h = 110
        if kind == "vol":
            ch.panel(top, h, 0, max(b["vol"] for b in vis) * 1.05, "volume (BTC)", "{:.0f}")
            ch.bars([b["vol"] for b in vis], 0, lambda k, v: GREEN if vis[k]["c"] >= vis[k]["o"] else RED)
        elif kind == "delta":
            m = max(abs(b["delta"]) for b in vis) * 1.1 or 1
            ch.panel(top, h, -m, m, "per-bar delta (BTC)", "{:.0f}")
            ch.bars([b["delta"] for b in vis], 0, lambda k, v: GREEN if v >= 0 else RED)
        else:
            vals = [b["cvd"] for b in vis]
            ch.panel(top, h, min(vals + [0]) * 1.05, max(vals + [0]) * 1.05 or 1, "CVD, resets 00:00 UTC (BTC)", "{:.0f}")
            ch.series(vals, "#e6c76a", 2)
        top += h + 12
    ch.text(12, H_PX - 18, "Offset 0 = last closed bar. Marks: trigger bar offset, side, stop %, target % from the last close.", 10, GREY)
    return ch


def daily_chart(code, D, i, blind_id):
    u = UNITS[code]
    n = u["shown"]
    if i - n + 1 < 0:
        raise ValueError("window starts before the first bar")
    if u["tf"] == "1w":
        vis, rs = D.w[i - n + 1:i + 1], D.rsi_w[i - n + 1:i + 1]
        rm = [D.rsi_m_at(w["end"]) for w in vis]
    else:
        vis, rs = D.d[i - n + 1:i + 1], D.rsi[i - n + 1:i + 1]
    ch = Chart(f"{blind_id} | {u['label']} | BTCUSDT {u['tf']} | last closed bar = right edge (offset 0) | dates hidden", n)
    pct = draw_price(ch, vis, vis[-1]["c"], 36, 470)
    for k in range(0, n, 20):
        ch.text(ch.x(k) - 8, ch.top + ch.h + 2, str(k - n + 1), 10, GREY)
    top = 36 + 470 + 24
    if code == "KRS1":
        avg = [statistics.fmean(x["vol"] for x in D.d[j - 29:j + 1]) for j in range(i - n + 1, i + 1)]
        ch.panel(top, 120, 0, max(b["vol"] for b in vis) * 1.05, "volume (BTC) with 30-day average", "{:.0f}")
        ch.bars([b["vol"] for b in vis], 0, lambda k, v: GREEN if vis[k]["c"] >= vis[k]["o"] else RED)
        ch.series(avg, "#e6c76a", 1)
    elif code == "KRS8":
        ch.panel(top, 120, 0, 100, "BBWP % (20d BB width rank in 252d); lines 30 and 50", "{:.0f}", 25)
        for lvl in (30, 50):
            ch.line([(X0, ch.y(lvl)), (X1, ch.y(lvl))], "#d98b65", 1)
        ch.series(D.bbwp[i - n + 1:i + 1], "#55b9d1", 2)
    else:
        for label, vals in (("RSI(14) of this timeframe; lines 40 and 60", rs),) + ((("monthly RSI(14), last completed month; lines 40 and 60", rm),) if u["tf"] == "1w" else ()):
            ch.panel(top, 110, 0, 100, label, "{:.0f}", 20)
            for lvl in (40, 60):
                ch.line([(X0, ch.y(lvl)), (X1, ch.y(lvl))], "#d98b65", 1)
            ch.series(vals, "#55b9d1", 2)
            top += 124
    ch.text(12, H_PX - 18, "Offset 0 = last closed bar. Marks: trigger bar offset, side, stop %, target % from the last close.", 10, GREY)
    return ch


def render(jobs, ps1=HERE / "render_png.ps1", batch=20):
    with tempfile.TemporaryDirectory() as td:  # primitives never land in the repo folder
        for s in range(0, len(jobs), batch):
            tmp = Path(td) / f"render_{s}.json"
            tmp.write_text(json.dumps([dict(out=str(j["out"]), w=W_PX, h=H_PX, prims=j["prims"]) for j in jobs[s:s + batch]]), encoding="utf-8")
            subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1), str(tmp)], check=True)


# ---------------------------------------------------------------- outputs
SHEET_COLS = ["window_id", "row", "reader", "take_skip", "side", "trigger_bar_offset", "concepts_seen", "stop_pct", "target_pct", "note"]


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def cmd_build(args):
    rows, daily = load_intraday(args.intra), load_daily(args.daily)
    recs = build_windows(rows, daily)
    order = {c: n for n, c in enumerate(UNITS)}
    recs.sort(key=lambda r: (order[r["unit"]], r["window_id"]))
    win = [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], timeframe=UNITS[r["unit"]]["tf"], bars_shown=UNITS[r["unit"]]["shown"],
                right_edge_utc=iso(r["end"]), seed=f"{SEED}-{r['unit']}", data=UNITS[r["unit"]]["fam"]) for r in recs]
    write_csv(HERE / "WINDOWS.csv", list(win[0]), win)
    key = [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], half=r["half"], prefilter_tag=r["tag"], right_edge_utc=iso(r["end"])) for r in recs]
    (HERE / "ANSWER_KEY_CLOSED").mkdir(exist_ok=True)
    write_csv(HERE / "ANSWER_KEY_CLOSED" / "KEY.csv", list(key[0]), key)
    for n, who in ((1, "operator"), (2, "claude")):
        write_csv(HERE / f"MARKING_SHEET_reader{n}_{who}.csv", SHEET_COLS,
                  [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], reader=f"reader{n}_{who}") for r in recs])
    sha = hashlib.sha256((HERE / "ANSWER_KEY_CLOSED" / "KEY.csv").read_bytes()).hexdigest()
    print(f"windows={len(recs)} key_sha256={sha}")
    per = defaultdict(lambda: defaultdict(int))
    for r in recs:
        per[UNITS[r["unit"]]["label"]][r["half"]] += 1
    for k, v in per.items():
        print(k, dict(v))


def cmd_counts(args):
    rows, daily = load_intraday(args.intra), load_daily(args.daily)
    for code, (cx, elig, tag) in intra_units(rows).items():
        tags = [tag(i) for i in elig]
        print(code, "eligible", len(elig), "candidates", sum(1 for t in tags if t))
    D, du = daily_units(daily)
    for code, (elig, tag) in du.items():
        tags = [tag(i) for i in elig]
        print(code, "eligible", len(elig), "candidates", sum(1 for t in tags if t), {t: tags.count(t) for t in set(tags) if t})


def cmd_draw(args):
    rows, daily = load_intraday(args.intra), load_daily(args.daily)
    wins = list(csv.DictReader(open(HERE / "WINDOWS.csv", encoding="utf-8")))
    label_to_code = {u["label"]: c for c, u in UNITS.items()}
    intra = {}
    D = Daily(daily)
    jobs = []
    Path(args.out).mkdir(parents=True, exist_ok=True)
    for w in wins:
        code = label_to_code[w["row"]]
        end = int(datetime.strptime(w["right_edge_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000)
        if UNITS[code]["fam"] == "intra":
            cx = intra.setdefault(UNITS[code]["tf"], Intra(rows, UNITS[code]["tf"]))
            i = next(k for k in range(len(cx.bars) - 1, -1, -1) if cx.bars[k]["t"] + cx.tf_ms == end)
            ch = intra_chart(code, cx, i, w["window_id"])
        else:
            i = next(k for k in range(len(D.w) - 1, -1, -1) if D.w[k]["end"] == end) if UNITS[code]["tf"] == "1w" else next(k for k in range(len(D.d) - 1, -1, -1) if D.d[k]["t"] + DAY == end)
            ch = daily_chart(code, D, i, w["window_id"])
        jobs.append(dict(out=Path(args.out) / f"{w['window_id']}.png", prims=ch.p))
    render(jobs)
    print(f"drawn={len(jobs)} -> {args.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["counts", "build", "draw"])
    ap.add_argument("--intra", default=INTRA_DIR)
    ap.add_argument("--daily", default=DAILY_DIR)
    ap.add_argument("--out", default=r"F:\MTS\data\g3_pack_2026-10-16\charts")
    a = ap.parse_args()
    {"counts": cmd_counts, "build": cmd_build, "draw": cmd_draw}[a.cmd](a)
