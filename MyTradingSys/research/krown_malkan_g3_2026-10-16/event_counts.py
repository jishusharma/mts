"""DEV-only event counts and minimum detectable effect (MDE) for KR-S1, KR-S8, MAL-2, MAL-5, MAL-16, MAL-17 (+ MAL-10 daily-40 variant).

COUNTS AND GEOMETRY ONLY. No forward return, no outcome of any trade is computed or read. Every series is cut to bars opened
before 2024-07-01 (DEV) before any indicator is built, so VALIDATION and HOLDOUT bars are never in memory.

Every pre-filter below is OURS (judgement, written down before any outcome is looked at). Run:
  python MyTradingSys/research/krown_malkan_g3_2026-10-16/event_counts.py --data F:/MTS/data/krown_daily --out MyTradingSys/research/krown_malkan_g3_2026-10-16
MDE: MyTradingSys/backtest/power_mde.py (two-point payoff +RR / -1, fixed cost in R, 95% two-sided CI lower bound above zero, 80% power).
"""
import argparse
import csv
import json
import sys
from bisect import bisect_right
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events  # noqa: E402
from MyTradingSys.backtest.power_mde import power_mde  # noqa: E402

DAY = 86400_000
CUT_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)  # DEV = bars opened before this
FEE_RT = 2 * 0.0005          # DERIBIT_TAKER both sides (fees.py:23), the conservative case
RR = 2.0                     # OURS: reward/risk used only for the MDE arithmetic
MIN_SEP = 5                  # OURS: events closer than this many bars count once (overlap, not independent)
TARGET_NET_R = 0.10          # OURS: the effect size the sample-size column asks about


# ---------- data ----------
def load(path, step):
    """Return dict of lists for bars opened before CUT_MS (cut first, indicators after)."""
    t, o, h, l, c = [], [], [], [], []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            ms = int(row[0])
            if ms >= CUT_MS:
                break
            t.append(ms)
            o.append(float(row[1]))
            h.append(float(row[2]))
            l.append(float(row[3]))
            c.append(float(row[4]))
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "step": step}


def monthly_from_daily(d):
    months = {}
    for i, ms in enumerate(d["t"]):
        dt = datetime.fromtimestamp(ms / 1000, timezone.utc)
        months.setdefault((dt.year, dt.month), []).append(i)
    t, o, h, l, c, close_t = [], [], [], [], [], []
    for (y, m), idx in sorted(months.items()):
        first = datetime(y, m, 1, tzinfo=timezone.utc)
        nxt = datetime(y + (m == 12), 1 if m == 12 else m + 1, 1, tzinfo=timezone.utc)
        ndays = (nxt - first).days
        if len(idx) != ndays or d["t"][idx[0]] != int(first.timestamp() * 1000):
            continue  # partial month
        t.append(d["t"][idx[0]])
        o.append(d["o"][idx[0]])
        h.append(max(d["h"][i] for i in idx))
        l.append(min(d["l"][i] for i in idx))
        c.append(d["c"][idx[-1]])
        close_t.append(int(nxt.timestamp() * 1000))
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "close_t": close_t}


def with_close_t(d):
    if "close_t" not in d:
        d["close_t"] = [x + d["step"] for x in d["t"]]
    return d


def asof_value(htf_close_t, htf_vals, ms):
    """Last higher-timeframe value whose bar closed at or before ms (never a bar still forming)."""
    k = bisect_right(htf_close_t, ms) - 1
    return htf_vals[k] if k >= 0 else None


def atr(d, n=14):
    tr = [None] * len(d["t"])
    out = [None] * len(d["t"])
    for i in range(len(d["t"])):
        pc = d["c"][i - 1] if i else d["c"][i]
        tr[i] = max(d["h"][i] - d["l"][i], abs(d["h"][i] - pc), abs(d["l"][i] - pc))
    for i in range(n - 1, len(tr)):
        out[i] = sum(tr[i - n + 1:i + 1]) / n
    return out


def dedupe(events, sep=MIN_SEP):
    """events: list of dicts with 'i' and 'side'; keep one per side per sep bars (greedy, earliest first)."""
    keep, last = [], {}
    for e in sorted(events, key=lambda e: (e["side"], e["i"])):
        if e["side"] in last and e["i"] - last[e["side"]] < sep:
            continue
        last[e["side"]] = e["i"]
        keep.append(e)
    return sorted(keep, key=lambda e: e["i"])


# ---------- KR-S1: zone test with a proof candle ----------
def pivots(d, k, kind):
    key = "l" if kind == "low" else "h"
    s = 1 if kind == "low" else -1
    v = d[key]
    out = []
    for i in range(k, len(v) - k):
        if all(s * v[i] < s * v[i - j] for j in range(1, k + 1)) and all(s * v[i] <= s * v[i + j] for j in range(1, k + 1)):
            out.append(i)
    return out


def proof_candle(d, i, side):
    o, h, l, c = d["o"][i], d["h"][i], d["l"][i], d["c"][i]
    rng = h - l
    if rng <= 0:
        return None
    body = abs(c - o)
    lower, upper = min(o, c) - l, h - max(o, c)
    if body <= 0.10 * rng:
        return "doji"
    if side == "long":
        if lower >= 2 * body and (c - l) >= 2 * rng / 3:
            return "hammer"
        if i and d["l"][i] < d["l"][i - 1] and c > d["h"][i - 1]:
            return "engulf"
    else:
        if upper >= 2 * body and (h - c) >= 2 * rng / 3:
            return "star"
        if i and d["h"][i] > d["h"][i - 1] and c < d["l"][i - 1]:
            return "engulf"
    return None


def kr_s1(d, k):
    """Zone = pivot candle's wick extreme to its close (width floor 0.25 ATR); valid once a second pivot of the same kind lands inside it
    (turned twice); event = later bar that trades into the zone, closes back outside on the zone's near side, and prints a proof candle.
    The 'with the trend' leg is NOT applied (counts are an upper bound)."""
    a = atr(d)
    events = {}
    for kind, side in (("low", "long"), ("high", "short")):
        piv = pivots(d, k, kind)
        for x, p1 in enumerate(piv):
            if a[p1] is None:
                continue
            if kind == "low":
                lo, hi = d["l"][p1], max(d["c"][p1], d["l"][p1] + 0.25 * a[p1])
            else:
                lo, hi = min(d["c"][p1], d["h"][p1] - 0.25 * a[p1]), d["h"][p1]
            tol = 0.5 * a[p1]
            p2 = None
            for q in piv[x + 1:]:
                if q - p1 < 5:
                    continue
                v = d["l"][q] if kind == "low" else d["h"][q]
                if lo - tol <= v <= hi + tol:
                    p2 = q
                    break
            if p2 is None:
                continue
            start = p2 + k + 1
            horizon = 250 if d["step"] == DAY else 104
            last_fire = -999
            for j in range(start, min(len(d["t"]), start + horizon)):
                if kind == "low":
                    touched = d["l"][j] <= hi and d["c"][j] >= lo
                    risk = d["c"][j] - lo
                else:
                    touched = d["h"][j] >= lo and d["c"][j] <= hi
                    risk = hi - d["c"][j]
                if not touched or risk <= 0 or j - last_fire < 10:
                    continue
                pc = proof_candle(d, j, side)
                if pc:
                    last_fire = j
                    events[(j, side)] = {"i": j, "side": side, "risk_pct": risk / d["c"][j], "proof": pc}
    return dedupe(list(events.values()))


# ---------- KR-S8: volatility compression breakout (BBWP) ----------
def bbwp(c, length, lookback):
    n = len(c)
    bbw = [None] * n
    for i in range(length - 1, n):
        w = c[i - length + 1:i + 1]
        m = sum(w) / length
        sd = sqrt(sum((x - m) ** 2 for x in w) / length)
        bbw[i] = 2 * sd / m
    out = [None] * n
    for i in range(n):
        if bbw[i] is None or i < length - 1 + lookback - 1:
            continue
        win = bbw[i - lookback + 1:i + 1]
        out[i] = 100.0 * sum(1 for x in win if x <= bbw[i]) / lookback
    return out


def kr_s8(d, lookback, from_high):
    """Compression: BBWP <= 30 on some bar of the last 10, previous bar below 50, this bar >= 50, and the close breaks the prior 10-bar range.
    from_high=True also requires BBWP >= 70 somewhere in the 60 bars before the compression ('coming down from a high level')."""
    b = bbwp(d["c"], 13, lookback)
    events = []
    for i in range(lookback + 70, len(d["t"])):
        if b[i] is None or b[i - 1] is None or b[i] < 50 or b[i - 1] >= 50:
            continue
        window = [x for x in b[i - 10:i] if x is not None]
        if not window or min(window) > 30:
            continue
        if from_high:
            prior = [x for x in b[i - 70:i - 10] if x is not None]
            if not prior or max(prior) < 70:
                continue
        rng_hi, rng_lo = max(d["h"][i - 10:i]), min(d["l"][i - 10:i])
        if d["c"][i] > rng_hi:
            events.append({"i": i, "side": "long", "risk_pct": (d["c"][i] - rng_lo) / d["c"][i]})
        elif d["c"][i] < rng_lo:
            events.append({"i": i, "side": "short", "risk_pct": (rng_hi - d["c"][i]) / d["c"][i]})
    return dedupe(events)


# ---------- Malkan ----------
def malkan_gate(d, weekly, monthly):
    """Per daily bar: weekly and monthly RSI(14) both above 60 as of the bar's close (last closed higher-timeframe bar)."""
    w_rsi = rsi_core(weekly["c"], 14)
    m_rsi = rsi_core(monthly["c"], 14)
    wct, mct = with_close_t(weekly)["close_t"], monthly["close_t"]
    gate = []
    for ms in d["t"]:
        close = ms + DAY
        wv, mv = asof_value(wct, w_rsi, close), asof_value(mct, m_rsi, close)
        gate.append(wv is not None and mv is not None and wv > 60 and mv > 60)
    return gate


def mal_2(d, rsi, gate):
    """RSI(14) support event at 60 (rsi_events: dips into 60 +/- 2 from above and returns above) with the weekly and monthly gate on."""
    ev = [e for e in rsi_events(rsi, d["t"], 60.0, 2.0) if e["event"] == "support"]
    idx = {t: i for i, t in enumerate(d["t"])}
    out = []
    for e in ev:
        i = idx[e["t"]]
        if gate[i]:
            risk = d["h"][i] - d["l"][i]  # order above the signal candle high, stop below its low
            if risk > 0:
                out.append({"i": i, "side": "long", "risk_pct": risk / d["h"][i]})
    return dedupe(out)


def mal_5(d, rsi, gate):
    """Wider version of the buy example: gate on, daily RSI close within 58..62, green candle; order above its high, stop below the lowest low of 3 bars."""
    out = []
    for i in range(3, len(d["t"])):
        if rsi[i] is None or not gate[i] or not (58.0 <= rsi[i] <= 62.0) or d["c"][i] <= d["o"][i]:
            continue
        risk = d["h"][i] - min(d["l"][i - 2:i + 1])
        if risk > 0:
            out.append({"i": i, "side": "long", "risk_pct": risk / d["h"][i]})
    return dedupe(out)


def mal_10(d, rsi, gate):
    """Host-recap 5-star: gate on, daily RSI support event at 40 (tolerance 2); order above the signal candle high, stop below its low."""
    ev = [e for e in rsi_events(rsi, d["t"], 40.0, 2.0) if e["event"] == "support"]
    idx = {t: i for i, t in enumerate(d["t"])}
    out = []
    for e in ev:
        i = idx[e["t"]]
        if gate[i] and d["h"][i] > d["l"][i]:
            out.append({"i": i, "side": "long", "risk_pct": (d["h"][i] - d["l"][i]) / d["h"][i]})
    return dedupe(out)


def mal_div(d, rsi, kind):
    """Regular divergence, sourced window 3-10 bars, close to close (rsi_divergence.py), kept when the bar after B closes in the divergence direction
    (bullish candle after bullish divergence); order beyond that candle's extreme, stop at the other extreme."""
    ev = rsi_divergence(d["c"], rsi, d["t"], 3, 10, kind=kind)
    out = []
    for e in ev:
        i = e["i"]  # bar after B: the candle that confirms
        if i >= len(d["t"]):
            continue
        green = d["c"][i] > d["o"][i]
        ok = green if kind == "bullish" else (not green)
        rng = d["h"][i] - d["l"][i]
        if ok and rng > 0:
            out.append({"i": i, "side": "long" if kind == "bullish" else "short", "risk_pct": rng / d["h"][i]})
    return dedupe(out), len(ev)


# ---------- summaries ----------
def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def mde_block(events):
    n = len(events)
    if n < 2:
        return {"n_eff": n, "risk_pct_median": None, "cost_r": None, "p0": None, "mde_net_r": None, "mde_win_rate_pp": None,
                "events_for_80pct_power": None}
    risk = median([e["risk_pct"] for e in events])
    cost_r = FEE_RT / risk
    p0 = (1.0 + cost_r) / (RR + 1.0)
    m = power_mde(p0, RR, cost_r, n)
    p_target = (TARGET_NET_R + 1.0 + cost_r) / (RR + 1.0)
    need = power_mde(p_target, RR, cost_r, n)["trades_for_80_power"]
    return {"n_eff": n, "risk_pct_median": risk, "cost_r": cost_r, "p0": p0, "mde_net_r": m["mde_net_r"],
            "mde_win_rate_pp": 100.0 * m["mde_net_r"] / (RR + 1.0), "events_for_80pct_power": need}


def by_year(events, d):
    yrs = {}
    for e in events:
        y = datetime.fromtimestamp(d["t"][e["i"]] / 1000, timezone.utc).year
        yrs[y] = yrs.get(y, 0) + 1
    return yrs


def run(data_dir):
    series = {}
    for sym in ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"):
        d = with_close_t(load(Path(data_dir) / f"{sym}_1d.csv", DAY))
        w = with_close_t(load(Path(data_dir) / f"{sym}_1w_from_1d.csv", 7 * DAY))
        series[sym] = {"1d": d, "1w": w, "1M": monthly_from_daily(d)}
    rows = []
    pool = {}

    def add(row_id, tf, sym, label, events, extra=None):
        d = series[sym][tf]
        pool.setdefault((row_id, tf, label), []).extend(events)
        r = {"row": row_id, "tf": tf, "asset": sym, "filter": label, "raw_events": (extra or {}).get("raw", len(events))}
        r.update(mde_block(events))
        r["by_year"] = by_year(events, d)
        r["bars"] = len(d["t"])
        r["first"] = datetime.fromtimestamp(d["t"][0] / 1000, timezone.utc).strftime("%Y-%m-%d")
        r["last"] = datetime.fromtimestamp(d["t"][-1] / 1000, timezone.utc).strftime("%Y-%m-%d")
        rows.append(r)

    for sym in series:
        for tf, k in (("1d", 3), ("1w", 2)):
            d = series[sym][tf]
            add("KR-S1", tf, sym, f"zone twice-turned (pivot k={k}) + hammer/engulf/doji/star, no trend leg", kr_s1(d, k))
            lb = 252 if tf == "1d" else 104
            add("KR-S8", tf, sym, f"BBWP(13,{lb}) <=30 in last 10, >=50 now, 10-bar range break", kr_s8(d, lb, False))
            add("KR-S8-high", tf, sym, "same + BBWP>=70 in the 60 bars before the compression", kr_s8(d, lb, True))
    for sym in series:
        d, w, m = series[sym]["1d"], series[sym]["1w"], series[sym]["1M"]
        rsi = rsi_core(d["c"], 14)
        gate = malkan_gate(d, w, m)
        add("MAL-2", "1d", sym, "weekly+monthly RSI>60 gate, daily RSI support event at 60 (tol 2)", mal_2(d, rsi, gate))
        add("MAL-5", "1d", sym, "gate, daily RSI close in 58..62, green candle; order over high, stop under 3-bar low", mal_5(d, rsi, gate))
        add("MAL-10", "1d", sym, "gate, daily RSI support event at 40 (tol 2) [host 5-star variant, extra]", mal_10(d, rsi, gate))
        for tf in ("1d", "1w"):
            x = series[sym][tf]
            rs = rsi_core(x["c"], 14)
            for rid, kind in (("MAL-17", "bullish"), ("MAL-16", "bearish")):
                ev, raw = mal_div(x, rs, kind)
                add(rid, tf, sym, f"{kind} divergence 3-10 bars close to close + confirming candle", ev, {"raw": raw})
    for (row_id, tf, label), ev in pool.items():
        r = {"row": row_id, "tf": tf, "asset": "POOLED4", "filter": label, "raw_events": len(ev), "bars": "-", "first": "-", "last": "-", "by_year": {}}
        r.update(mde_block(ev))
        rows.append(r)
    return rows


def verdict(r):
    """OURS: ENOUGH when the MDE is at most 0.30R, MARGINAL up to 0.60R, THIN above."""
    m = r["mde_net_r"]
    if m is None:
        return "NO EVENTS"
    return "ENOUGH" if m <= 0.30 else ("MARGINAL" if m <= 0.60 else "THIN")


def fmt(v, nd=3):
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def write_md(rows, path):
    L = []
    w = L.append
    w("# EVENT_COUNTS: how many DEV events do KR-S1, KR-S8 and MAL-2/5/16/17 hold, and what effect can they detect? (2026-10-16)\n")
    w("Session `krown-malkan-p6` (Fable P6, CATALOGUE_AUDIT.md). **Counts and geometry only: no forward return and no trade outcome was computed or read.**\n"
      "Data: Binance spot daily files from `F:/MTS/data/krown_daily` (DATA_COVERAGE.md), cut to bars opened before 2024-07-01 (DEV) before any indicator was built.\n"
      "Reproduce: `python MyTradingSys/research/krown_malkan_g3_2026-10-16/event_counts.py --data F:/MTS/data/krown_daily --out MyTradingSys/research/krown_malkan_g3_2026-10-16` "
      "(full per-asset, per-year table: `event_counts.csv`).\n")
    btc = {(r["row"], r["tf"]): r for r in rows if r["asset"] == "BTCUSDT"}
    pooled = {(r["row"], r["tf"]): r for r in rows if r["asset"] == "POOLED4"}
    name = lambda k: f"{k[0]} {k[1]}"
    enough = [name(k) for k, r in btc.items() if verdict(r) == "ENOUGH"]
    rescued = [f"{name(k)} ({fmt(pooled[k]['mde_net_r'], 2)}R)" for k, r in btc.items() if verdict(r) == "THIN" and verdict(pooled[k]) in ("ENOUGH", "MARGINAL")]
    still = [name(k) for k, r in btc.items() if verdict(r) == "THIN" and verdict(pooled[k]) == "THIN"]
    w("## Answer\n")
    w(f"- **Enough events on BTC alone (MDE <= 0.30R net):** {', '.join(enough) or 'none'}.\n"
      f"- **Too few on BTC alone but MARGINAL when pooled over BTC, ETH, BNB, SOL (MDE in brackets, assumes independent events, so optimistic):** {', '.join(rescued) or 'none'}.\n"
      f"- **Too few even pooled (descriptive reading only, no G5 test):** {', '.join(still) or 'none'}.\n"
      f"- No row can confirm a +{TARGET_NET_R:.2f}R net edge: that needs about {fmt(btc[('KR-S1', '1d')]['events_for_80pct_power'], 0)} independent events. The question G5 can answer is whether a large effect is present, not a small one.\n")
    w("## How to read it\n")
    w("- Every pre-filter is **OURS** (written down before any outcome was looked at); it is a cheap stand-in for the trader's chart reading, not the rule itself. "
      "Where a leg of his rule cannot be computed from OHLC alone it is dropped, so the count is an order of magnitude, not a guaranteed upper bound.\n"
      f"- `n` = events after merging events closer than {MIN_SEP} bars on the same side (OURS; neighbours share one move). `bars` = DEV bars in the series.\n"
      "- Stop geometry is read from the event bar itself (never the future): stop % = distance from the planned entry to the stated stop reference; "
      f"cost in R = round trip taker fee {FEE_RT * 100:.2f}% / stop %. Fees are the Deribit taker rate (`fees.py:23`), both sides.\n"
      f"- **MDE** = smallest mean net R per trade the sample could detect with 80% power at a two-sided 95% test, from `MyTradingSys/backtest/power_mde.py` with a +{RR:.0f}R / -1R payoff (OURS), "
      "variance taken at the break-even win rate. 'Win-rate pp' is the same MDE as extra win rate over break-even.\n"
      f"- `Events for +{TARGET_NET_R:.2f}R` = events needed for 80% power if the true edge is +{TARGET_NET_R:.2f}R net (OURS target). "
      "Verdict (OURS): ENOUGH if MDE <= 0.30R, MARGINAL up to 0.60R, THIN above.\n")
    w("## 1. BTCUSDT (the series every row is judged on)\n")
    w(f"| row | tf | pre-filter (OURS) | bars | n | by year | median stop | cost R | MDE net R | MDE win-rate pp | events for +{TARGET_NET_R:.2f}R | verdict |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["asset"] != "BTCUSDT":
            continue
        yrs = " ".join(f"{y}:{n}" for y, n in sorted(r["by_year"].items()))
        raw = f"{r['n_eff']} (of {r['raw_events']} divergences)" if r["row"] in ("MAL-16", "MAL-17") else str(r["n_eff"])
        stop = f"{100 * r['risk_pct_median']:.1f}%" if r["risk_pct_median"] else "-"
        w(f"| {r['row']} | {r['tf']} | {r['filter']} | {r['bars']} | {raw} | {yrs} | {stop} | "
          f"{fmt(r['cost_r'], 3)} | {fmt(r['mde_net_r'], 2)} | {fmt(r['mde_win_rate_pp'], 1)} | {fmt(r['events_for_80pct_power'], 0)} | **{verdict(r)}** |")
    w("")
    w("## 2. Pooled over BTC, ETH, BNB, SOL (daily and weekly-from-daily)\n")
    w("Pooling adds events but the four coins move together, so the MDE below is **optimistic** (it assumes independent events). Use it as a floor, not a promise.\n")
    w("| row | tf | n BTC | n ETH | n BNB | n SOL | pooled n | pooled MDE net R | verdict if independent |")
    w("|---|---|---|---|---|---|---|---|---|")
    per = {}
    for r in rows:
        per.setdefault((r["row"], r["tf"], r["filter"]), {})[r["asset"]] = r
    for (row, tf, label), d in per.items():
        if "POOLED4" not in d:
            continue
        pr = d["POOLED4"]
        w(f"| {row} | {tf} | " + " | ".join(str(d[a]["n_eff"]) for a in ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT")) +
          f" | {pr['n_eff']} | {fmt(pr['mde_net_r'], 2)} | {verdict(pr)} |")
    w("")
    w("## 3. What this means for G3 and G5\n")
    w("- A row whose BTC MDE is above 0.60R cannot reject 'no edge' on BTC alone unless the trader's claimed edge is large; on DEV it can only be **described** "
      "(does the pattern look like his chart), not **tested**. Pool it with the other coins, or widen the pre-filter and say so, before spending a G5 slot.\n"
      "- MAL-2 and MAL-10 are small because the 'weekly and monthly RSI both above 60' gate is true in only a few bull stretches of BTC; "
      "the monthly RSI(14) also needs 14 closed months, so the gate is blank before late 2018.\n"
      "- Weekly rows hold under 40 events on BTC; they are descriptive only. The weekly stops are wide (see the stop column), which makes fees negligible but the sample tiny.\n"
      "- No pre-filter here uses the 'with the trend' leg (KR-S1) or the 5-star timeframe pairing that is garbled in the transcript (MAL-2, MAL-5), "
      "so those counts are likely above what the trader's full rule would flag.\n"
      "- KR-S8 weekly shows a median stop of 87% because a 10-week range on BTC is that wide: that row is not tradeable as written, whatever its count.\n"
      "- MAL-2 and MAL-5 are two readings of the same sentence (RSI back at the sixty line while weekly and monthly are above 60); the support event is the "
      "narrower one. The timeframe of that sixty line is NOT STATED in the transcript (see malkan_extract_2026-10-15/COMPARE.md s1.2).\n")
    Path(path).write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = run(a.data)
    out = Path(a.out)
    with open(out / "event_counts.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["row", "tf", "asset", "filter", "bars", "first", "last", "raw_events", "n_eff", "risk_pct_median", "cost_r", "p0",
                    "mde_net_r", "mde_win_rate_pp", "events_for_80pct_power", "by_year"])
        for r in rows:
            w.writerow([r["row"], r["tf"], r["asset"], r["filter"], r["bars"], r["first"], r["last"], r["raw_events"], r["n_eff"],
                        fmt(r["risk_pct_median"], 4), fmt(r["cost_r"], 4), fmt(r["p0"], 4), fmt(r["mde_net_r"], 4),
                        fmt(r["mde_win_rate_pp"], 2), fmt(r["events_for_80pct_power"], 0), json.dumps(r["by_year"], sort_keys=True)])
    write_md(rows, out / "EVENT_COUNTS.md")
    print("event_counts.csv rows", len(rows))
    for r in rows:
        if r["asset"] == "BTCUSDT":
            print(r["row"], r["tf"], "raw", r["raw_events"], "n_eff", r["n_eff"], "risk", fmt(r["risk_pct_median"], 4), "cost_r", fmt(r["cost_r"], 3),
                  "MDE", fmt(r["mde_net_r"], 3), "need", fmt(r["events_for_80pct_power"], 0))


if __name__ == "__main__":
    main()
