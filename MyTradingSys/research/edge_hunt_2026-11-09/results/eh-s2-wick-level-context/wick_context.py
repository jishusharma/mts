"""eh-s2-wick-level-context: wick at an HTF level with the whole context (T09 long, T10 short).

Rules are frozen in PRE_REG.md (same folder). Everything is computed in "U space": for the long (sg = +1) U = price;
for the short (sg = -1) U = -price with high and low swapped, so one code path serves both sides and the short is the
exact mirror. Percent measures use abs(U) = the price.

Run:  python wick_context.py count        count pass (events, funnel, regime mix; no returns printed)
      python wick_context.py dev          DEV trials T09/T10 + exploratory cells -> cells.csv
      python wick_context.py validation   the ONE VALIDATION read, only for a trial that passed the DEV screen
"""
import csv
import sys
from math import erfc, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
_BT = HERE.parents[3] / "backtest"          # MyTradingSys/backtest (read-only imports)
sys.path.insert(0, str(_BT))
sys.path.insert(0, str(HERE.parents[4]))      # repo root: research_kit loads malkan_mtf, which imports MyTradingSys.*
import fees  # noqa: E402
import research_kit  # noqa: E402
import splits  # noqa: E402
from bt import bt_data  # noqa: E402

BAR_MS = 900_000
DAY_MS = 86_400_000
BARS_PER_DAY = 96

# ---- frozen parameters (PRE_REG.md; every one OURS unless the label says SOURCED)
PIVOT_N = 5            # OURS: days each side of a daily pivot
SWEEP_BARS = 3         # OURS: reclaim within 3 bars, the sweep bar is bar 1
VOL_MULT = 3.0         # OURS (the Friday case was 12x, WICKS_NOTE s2)
VOL_LOOKBACK = 96      # OURS
KNIFE_BARS = 12        # OURS (d-wicks-research-plan-first-1107 default)
KNIFE_FALL = 0.02      # OURS
KNIFE_COUNTER = 0.25   # OURS
ORDER_LIVE = 4         # OURS
MIN_R = 2.5            # OURS (POSTMORTEM s3 plan)
BE_R = 1.0             # SOURCED in kind (Fabio fast break-even, fZlNGWvd2Ko:43-61)
TIME_STOP = 96         # OURS
SLIP_TAKER_BPS = fees.SLIPPAGE_RT_S13 * 1e4 / 2   # PLAN s5: 1 bp slippage on taker legs (regime B); half of the s13 round trip, from fees.py
SLIP_RT_A_BPS = fees.SLIPPAGE_RT_S13 * 1e4       # FORMULAS s13: 2 bps round-trip slippage (regime A), from fees.py
PRIORITY = {"month": 0, "week": 1, "pivot": 2}

SPLIT_END = {"DEV": splits.DEV_END, "VALIDATION": splits.VALIDATION_END}
CACHE_FUT = Path("F:/MTS/Dumps/backtest/eh_s2_wick") if Path("F:/").exists() else \
    Path(__import__("tempfile").gettempdir()) / "mts_eh_cache" / "eh_s2_wick"
CACHE_SPOT_1D = Path("F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1d")


# ===================================================================== loading with the split guard
def _ms(ts):
    return int(pd.Timestamp(ts).timestamp() * 1000)


def _split_end_ms(split):
    if split not in SPLIT_END:
        raise splits.SplitViolation(f"split {split!r} is not loadable (HOLDOUT is sealed; known: {sorted(SPLIT_END)})")
    return _ms(SPLIT_END[split])


def check_bars_in_split(bars, split):
    lim = _split_end_ms(split)
    if len(bars["t"]) and int(np.max(bars["t"])) >= lim:
        raise splits.SplitViolation(f"bar at {int(np.max(bars['t']))} is at/after the {split} end {SPLIT_END[split]}")
    return bars


def load_bars(root, split, end_ms=None):
    """15m (or any) klines under root/klines up to the end of `split` (DEV or VALIDATION). Refuses HOLDOUT and any end_ms
    past the split end; rows at/after the end are never read."""
    lim = _split_end_ms(split)
    if end_ms is not None and end_ms > lim:
        raise splits.SplitViolation(f"end_ms {end_ms} is past the {split} end {SPLIT_END[split]}")
    raw = bt_data.load_klines(root, end_ms=lim if end_ms is None else end_ms)
    bars = {"t": np.array([r["t"] for r in raw], dtype=np.int64)}
    for k in "ohlcv":
        bars[k] = np.array([r[k] for r in raw], dtype=float)
    return check_bars_in_split(bars, split)


def load_funding_split(root, split):
    lim = _split_end_ms(split)
    return [r for r in bt_data.load_funding(root) if r[0] < lim]


# ===================================================================== helpers
def _u(b, sg):
    if sg == 1:
        return b["o"], b["h"], b["l"], b["c"]
    return -b["o"], -b["l"], -b["h"], -b["c"]


def nearest_above(entry, cands):
    """Smallest candidate strictly above entry, else None."""
    above = [x for x in cands if x > entry]
    return min(above) if above else None


def is_knife(highs, lows):
    """U-space knife test over the approach bars (oldest first). H = highest high (first one) at k; L = lowest low over the
    bars after k; fall = H - L; counter = largest (later high - earlier low) over the bars after k, floor 0.
    Knife = fall >= 2 % of |H| and counter < 25 % of the fall. No bar after k -> not a knife."""
    hi = np.asarray(highs, float)
    lo = np.asarray(lows, float)
    if len(hi) < 2:
        return False
    k = int(np.argmax(hi))
    if k >= len(hi) - 1:
        return False
    H = hi[k]
    L = float(lo[k + 1:].min())
    fall = H - L
    if fall <= 0 or fall / abs(H) < KNIFE_FALL:
        return False
    counter = 0.0
    run_min = lo[k + 1]
    for b in range(k + 2, len(hi)):
        counter = max(counter, hi[b] - run_min)
        run_min = min(run_min, lo[b])
    return bool(counter < KNIFE_COUNTER * fall)


def exit_cost_bps(kind, regime):
    """Round-trip cost in bps charged at the exit (entry is a maker limit in B, a taker in A)."""
    if regime == "B":   # fees.FEES_DERIBIT: entry/target maker, stop/timeout taker (BE exits are stop orders)
        if kind == "target":
            return fees.FEES_DERIBIT["target"] * 1e4
        return fees.FEES_DERIBIT["stop"] * 1e4 + SLIP_TAKER_BPS
    if regime == "A":   # taker both legs + 2 bps round-trip slippage
        return (fees.FEES_ALL_TAKER["entry"] + fees.FEES_ALL_TAKER["target"]) * 1e4 + SLIP_RT_A_BPS
    raise ValueError(regime)


def fee_r(cost_bps, level_price, stop_dist):
    return cost_bps / (stop_dist / level_price * 1e4)


def rsi14(c):
    """Wilder RSI(14); NaN for the first 14 values."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) < 15:
        return out
    d = np.diff(c)
    g = np.where(d > 0, d, 0.0)
    ls = np.where(d < 0, -d, 0.0)
    ag, al = g[:14].mean(), ls[:14].mean()
    out[14] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    for i in range(14, len(d)):
        ag = (ag * 13 + g[i]) / 14
        al = (al * 13 + ls[i]) / 14
        out[i + 1] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    return out


# ===================================================================== regime tag (report only)
def regime_tags(t_open_ms, close, times_ms):
    """research_kit.regime_tag as of each time in times_ms (UTC ms), from daily closes (t_open_ms = day open, ms)."""
    t_open_ms = np.asarray(t_open_ms, np.int64)
    s = pd.Series(np.asarray(close, float), index=pd.to_datetime(t_open_ms, unit="ms"))
    wk = s.resample("W-SUN", closed="right", label="right").last().dropna()
    mo = s.resample("MS").last().dropna()
    w_close = [int((x + pd.Timedelta(days=1)).timestamp()) for x in wk.index]
    m_close = [int((x + pd.offsets.MonthBegin(1)).timestamp()) for x in mo.index]
    w_rsi, m_rsi = rsi14(wk.values), rsi14(mo.values)
    wr = ([a for a, r in zip(w_close, w_rsi) if r == r], [r for r in w_rsi if r == r])
    mr = ([a for a, r in zip(m_close, m_rsi) if r == r], [r for r in m_rsi if r == r])
    daily = (list((t_open_ms + DAY_MS) // 1000), list(map(float, close)))
    return [research_kit.regime_tag(int(t // 1000), daily, wr, mr)["regime"] for t in times_ms]


def regime_mix_text(tags):
    return research_kit.regime_mix_line(tags)


# ===================================================================== events
def _agg(key, h, l, t):
    df = pd.DataFrame({"k": key, "h": h, "l": l, "t": t})
    g = df.groupby("k", sort=True).agg(lo=("l", "min"), hi=("h", "max"), n=("t", "size"), t0=("t", "min"))
    return {int(k): (float(r.lo), float(r.hi), int(r.n), int(r.t0)) for k, r in g.iterrows()}


def _month_key(t):
    ts = pd.to_datetime(t, unit="ms")
    return (ts.year * 12 + ts.month - 1).to_numpy().astype(np.int64)


def _month_start_ms(mk):
    y, m = divmod(int(mk), 12)
    return _ms(pd.Timestamp(year=y, month=m + 1, day=1))


def find_events(b, sg):
    """Every first-touch sweep-and-reclaim of an HTF level (before the volume / knife / target gates, which are flags).
    Causal: an event is released at its reclaim close r and uses only bars <= r."""
    t = b["t"]
    n = len(t)
    o, h, l, c = _u(b, sg)
    v = b["v"]
    day = t // DAY_MS
    wk = (day + 3) // 7                      # Monday-based ISO weeks (1970-01-01 was a Thursday)
    mo = _month_key(t)
    dagg = _agg(day, h, l, t)
    wagg = _agg(wk, h, l, t)
    magg = _agg(mo, h, l, t)

    def day_ok(d):
        return d in dagg and dagg[d][2] == BARS_PER_DAY

    events, pending = [], {}
    sup, tpv = [], []
    tgt_day = tgt_week = None
    cur_day = cur_wk = cur_mo = None
    for i in range(n):
        d = int(day[i])
        if d != cur_day:
            cur_day = d
            tgt_day = dagg[d - 1][1] if day_ok(d - 1) else None
            p = d - (PIVOT_N + 1)
            if all(day_ok(q) for q in range(p - PIVOT_N, p + PIVOT_N + 1)):
                lo_p, hi_p = dagg[p][0], dagg[p][1]
                others = [q for q in range(p - PIVOT_N, p + PIVOT_N + 1) if q != p]
                if all(lo_p < dagg[q][0] for q in others):
                    sup.append({"price": lo_p, "type": "pivot"})
                if all(hi_p > dagg[q][1] for q in others):
                    tpv.append(hi_p)
            if int(wk[i]) != cur_wk:
                cur_wk = int(wk[i])
                sup = [x for x in sup if x["type"] != "week"]
                pw = cur_wk - 1
                tgt_week = None
                if pw in wagg and wagg[pw][3] == (pw * 7 - 3) * DAY_MS:
                    sup.append({"price": wagg[pw][0], "type": "week"})
                    tgt_week = wagg[pw][1]
            if int(mo[i]) != cur_mo:
                cur_mo = int(mo[i])
                sup = [x for x in sup if x["type"] != "month"]
                pm = cur_mo - 1
                if pm in magg and magg[pm][3] == _month_start_ms(pm):
                    sup.append({"price": magg[pm][0], "type": "month"})
        if tpv:
            tpv = [x for x in tpv if h[i] <= x]          # an unbroken pivot high: no bar traded above it
        if sup:
            touched = [x for x in sup if l[i] < x["price"]]
            if touched:
                sup = [x for x in sup if l[i] >= x["price"]]       # first touch used up, reclaimed or not
                rec = []
                for x in touched:
                    for r in range(i, min(i + SWEEP_BARS, n)):
                        if c[r] > x["price"]:
                            rec.append((r, PRIORITY[x["type"]], -x["price"], x))
                            break
                if rec and i >= VOL_LOOKBACK:
                    r, _, _, x = min(rec, key=lambda z: z[:3])      # earliest reclaim, then month > week > pivot, then higher
                    med = float(np.median(v[i - VOL_LOOKBACK:i]))
                    ratio = float(v[i] / med) if med > 0 else float("inf")
                    pending.setdefault(r, []).append({
                        "s": i, "r": r, "x": x, "ext": float(l[i:r + 1].min()), "ratio": ratio,
                        "knife": is_knife(h[i - KNIFE_BARS:i], l[i - KNIFE_BARS:i]), "n_touched": len(touched)})
        for q in pending.pop(i, []):
            x, level, ext = q["x"], q["x"]["price"], q["ext"]
            cands = [z for z in (tgt_day, tgt_week) if z is not None] + list(tpv)
            tgt = nearest_above(level, cands)
            events.append({
                "s": q["s"], "r": q["r"], "t_s": int(t[q["s"]]), "t_r": int(t[q["r"]]), "ltype": x["type"],
                "level_u": level, "price_level": abs(level), "ext_u": ext, "ext_price": abs(ext),
                "target_u": tgt, "target_price": None if tgt is None else abs(tgt),
                "target_r": None if tgt is None else (tgt - level) / (level - ext),
                "vol_ratio": q["ratio"], "vol_ok": bool(q["ratio"] >= VOL_MULT), "knife": bool(q["knife"]),
                "n_touched": q["n_touched"]})
    events.sort(key=lambda e: e["r"])
    return events


# ===================================================================== simulation
def simulate(b, events, sg, funding=None, regime="B", vol_gate=True, start_ms=None, end_ms=None):
    """Apply the gates in order (volume, knife, target, one-at-a-time), place the limit, fill, manage, exit.
    Returns (trades, funnel). funnel['log'] = [(t_r, status)] for the per-year counts."""
    o, h, l, c = _u(b, sg)
    t = b["t"]
    n = len(t)
    fn = {k: 0 for k in ("events", "vol_fail", "knife_veto", "no_target", "target_lt", "busy", "orders", "unfilled",
                         "filled", "unresolved", "target", "stop", "be", "timeout")}
    fn["log"] = []
    trades = []
    busy_until = -1

    def note(e, status):
        fn["log"].append((e["t_r"], status))

    for e in events:
        if start_ms is not None and e["t_r"] < start_ms:
            continue
        if end_ms is not None and e["t_r"] >= end_ms:
            continue
        fn["events"] += 1
        if vol_gate and not e["vol_ok"]:
            fn["vol_fail"] += 1
            note(e, "vol_fail")
            continue
        if e["knife"]:
            fn["knife_veto"] += 1
            note(e, "knife_veto")
            continue
        if e["target_u"] is None:
            fn["no_target"] += 1
            note(e, "no_target")
            continue
        if e["target_r"] < MIN_R:
            fn["target_lt"] += 1
            note(e, "target_lt")
            continue
        r = e["r"]
        if r <= busy_until:
            fn["busy"] += 1
            note(e, "busy")
            continue
        fn["orders"] += 1
        level, ext, tgt = e["level_u"], e["ext_u"], e["target_u"]
        R = level - ext
        fill = None
        for j in range(r + 1, min(r + 1 + ORDER_LIVE, n)):
            if l[j] < level:                       # strictly through the level
                fill = j
                break
        if fill is None:
            if r + ORDER_LIVE >= n:                # the order window is not fully in the data
                fn["unresolved"] += 1
                note(e, "unresolved")
                busy_until = n
            else:
                fn["unfilled"] += 1
                note(e, "unfilled")
                busy_until = r + ORDER_LIVE
            continue
        kind = gross = exit_i = None
        if l[fill] <= ext:                         # fill bar: only the stop is checked, and it wins
            kind, gross, exit_i = "stop", -1.0, fill
        else:
            be = False
            for k in range(fill + 1, min(fill + 1 + TIME_STOP, n)):
                stop_px = level if be else ext
                if l[k] <= stop_px:
                    kind, gross, exit_i = ("be", 0.0, k) if be else ("stop", -1.0, k)
                    break
                if h[k] > tgt:
                    kind, gross, exit_i = "target", (tgt - level) / R, k
                    break
                if not be and h[k] >= level + BE_R * R:
                    be = True                       # armed from the next bar
                if k == fill + TIME_STOP:
                    kind, gross, exit_i = "timeout", (c[k] - level) / R, k
                    break
        if kind is None:
            fn["unresolved"] += 1
            note(e, "unresolved")
            busy_until = n
            continue
        fn["filled"] += 1
        fn[kind] += 1
        note(e, "filled")
        busy_until = exit_i
        price = abs(level)
        stop_frac = R / price
        fr = fee_r(exit_cost_bps(kind, regime), price, R)
        fund = 0.0
        if funding:
            pct = float(bt_data.funding_cost_pct(funding, int(t[fill]), int(t[exit_i]) + BAR_MS, sg))
            fund = pct / 100.0 / stop_frac
        trades.append({
            "side": sg, "ltype": e["ltype"], "s": e["s"], "r": r, "fill_idx": fill, "exit_idx": exit_i, "kind": kind,
            "gross_r": float(gross), "fee_r": float(fr), "fund_r": float(fund), "net_r": float(gross - fr - fund),
            "t_s": e["t_s"], "t_r": e["t_r"], "t_fill": int(t[fill]), "day": int(t[fill] // DAY_MS),
            "stop_bps": stop_frac * 1e4, "target_r": e["target_r"], "vol_ratio": e["vol_ratio"]})
    return trades, fn


# ===================================================================== statistics
def summarize(trades):
    n = len(trades)
    if n == 0:
        return {"n": 0, "hit_net": float("nan"), "target_share": float("nan"), "gross": float("nan"),
                "fee_r": float("nan"), "fund_r": float("nan"), "net": float("nan"), "se": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan"), "mde": float("nan")}
    net = np.array([x["net_r"] for x in trades])
    day = np.array([x["day"] for x in trades])
    m, se = research_kit.cluster_mean_se(net, day)
    return {"n": n, "hit_net": float((net > 0).mean()), "target_share": float(np.mean([x["kind"] == "target" for x in trades])),
            "gross": float(np.mean([x["gross_r"] for x in trades])), "fee_r": float(np.mean([x["fee_r"] for x in trades])),
            "fund_r": float(np.mean([x["fund_r"] for x in trades])), "net": m, "se": se,
            "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se, "mde": research_kit.mde(se)}


def dev_screen(s):
    return bool(s["n"] >= 30 and s["net"] > 0 and s["ci_lo"] > 0)


def one_sided_p(s):
    if s["n"] < 2 or s["se"] != s["se"] or s["se"] == 0:
        return float("nan")
    z = s["net"] / s["se"]
    return 0.5 * erfc(z / sqrt(2.0))


def _fmt(x, d=4):
    return "nan" if x != x else f"{x:.{d}f}"


def row(trial, split, kind, cell, s):
    return [trial, split, kind, cell, s["n"], _fmt(s["hit_net"], 3), _fmt(s["gross"]), _fmt(s["fee_r"]), _fmt(s["fund_r"]),
            _fmt(s["net"]), _fmt(s["se"]), _fmt(s["ci_lo"]), _fmt(s["ci_hi"]), _fmt(s["mde"]),
            _fmt(s["target_share"], 3)]


CELL_HEAD = ["trial", "split", "cell_kind", "cell", "n", "hit_net", "mean_gross_r", "mean_fee_r", "mean_fund_r",
             "mean_net_r", "se", "ci_lo", "ci_hi", "mde80", "target_share"]
SIDES = {"T09": 1, "T10": -1}


def year_of(ms):
    return int(pd.Timestamp(ms, unit="ms").year)


# ===================================================================== driver
def _dev_inputs(split="DEV"):
    bars = load_bars(CACHE_FUT, split)
    fund = load_funding_split(CACHE_FUT, split)
    return bars, fund


def _spot_daily(split):
    sp = load_bars(CACHE_SPOT_1D, split)
    return sp["t"], sp["c"]


def weeks_in(first_ms, end_ms):
    start = pd.Timestamp(first_ms, unit="ms").normalize()
    start = start + pd.Timedelta(days=(7 - start.weekday()) % 7)
    wk = []
    while _ms(start) + 7 * DAY_MS <= end_ms:
        wk.append(_ms(start))
        start += pd.Timedelta(days=7)
    return wk


def cmd_count():
    bars, fund = _dev_inputs("DEV")
    print(f"DEV bars {len(bars['t'])} {pd.Timestamp(int(bars['t'][0]), unit='ms')} .. {pd.Timestamp(int(bars['t'][-1]), unit='ms')}")
    st, sc = _spot_daily("DEV")
    wks = weeks_in(int(bars["t"][0]), _ms(splits.DEV_END))
    print("Regime mix:", regime_mix_text(regime_tags(st, sc, wks)))
    for trial, sg in SIDES.items():
        ev = find_events(bars, sg)
        trades, fn = simulate(bars, ev, sg, funding=None)
        print(f"\n{trial} side {sg}: reclaim events {len(ev)}; by type", {k: sum(1 for e in ev if e['ltype'] == k) for k in PRIORITY})
        print("funnel", {k: v for k, v in fn.items() if k != "log"})
        tab = {}
        for tr, stt in fn["log"]:
            tab.setdefault(year_of(tr), {}).setdefault(stt, 0)
            tab[year_of(tr)][stt] += 1
        for y in sorted(tab):
            print(" ", y, tab[y])
        nv = simulate(bars, ev, sg, vol_gate=False)[1]
        print("no-volume-gate funnel", {k: v for k, v in nv.items() if k != "log"})


def cmd_dev():
    bars, fund = _dev_inputs("DEV")
    st, sc = _spot_daily("DEV")
    rows, out = [], []
    wks = weeks_in(int(bars["t"][0]), _ms(splits.DEV_END))
    mix = regime_mix_text(regime_tags(st, sc, wks))
    out.append(f"Regime mix: {mix}")
    for trial, sg in SIDES.items():
        ev = find_events(bars, sg)
        tr, fn = simulate(bars, ev, sg, funding=fund)
        s = summarize(tr)
        out.append(f"\n## {trial} DEV primary (regime B, volume gate, funding): {s}  screen={dev_screen(s)}")
        out.append("funnel " + str({k: v for k, v in fn.items() if k != 'log'}))
        rows.append(row(trial, "DEV", "primary", "regime B", s))
        fills = fn["filled"] + fn["unfilled"]
        rows.append([trial, "DEV", "fill_rate", "filled/(filled+unfilled)", fn["filled"], _fmt(fn["filled"] / fills if fills else float("nan"), 3)] + [""] * 9)
        for y in sorted({year_of(x["t_fill"]) for x in tr}):
            rows.append(row(trial, "DEV", "year", str(y), summarize([x for x in tr if year_of(x["t_fill"]) == y])))
        for kind in ("target", "stop", "be", "timeout"):
            rows.append(row(trial, "DEV", "exit_kind", kind, summarize([x for x in tr if x["kind"] == kind])))
        for lt in PRIORITY:
            rows.append(row(trial, "DEV", "level_type", lt, summarize([x for x in tr if x["ltype"] == lt])))
        for blk in range(6):
            sel = [x for x in tr if int(pd.Timestamp(x["t_s"], unit="ms").hour) // 4 == blk]
            rows.append(row(trial, "DEV", "utc_4h_block_of_sweep", f"{blk * 4:02d}-{blk * 4 + 4:02d}", summarize(sel)))
        trA, _ = simulate(bars, ev, sg, funding=fund, regime="A")
        rows.append(row(trial, "DEV", "exploratory", "regime A (taker both legs)", summarize(trA)))
        trN, fnN = simulate(bars, ev, sg, funding=fund, vol_gate=False)
        rows.append(row(trial, "DEV", "exploratory", "no volume gate", summarize(trN)))
        rows.append(row(trial, "DEV", "exploratory", "no volume gate, regime A", summarize(simulate(bars, ev, sg, funding=fund, vol_gate=False, regime="A")[0])))
        if tr:
            tags = regime_tags(st, sc, [x["t_r"] for x in tr])
            for g in ("bull", "bear", "range", None):
                rows.append(row(trial, "DEV", "regime_tag_exploratory", str(g), summarize([x for x, y in zip(tr, tags) if y == g])))
        out.append("no-volume-gate: " + str(summarize(trN)))
        out.append("regime A: " + str(summarize(trA)))
    with open(HERE / "cells.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(CELL_HEAD)
        w.writerows(rows)
    print("\n".join(out))


def cmd_validation(trials):
    lock = HERE / "VALIDATION_READ.lock"
    if lock.exists():
        raise SystemExit("VALIDATION was already read once (VALIDATION_READ.lock); refusing a second read")
    lock.write_text("VALIDATION read for " + ",".join(trials) + "\n", encoding="utf-8", newline="\n")
    bars, fund = _dev_inputs("VALIDATION")
    st, sc = _spot_daily("VALIDATION")
    vstart = _ms(splits.VALIDATION_START)
    wks = weeks_in(vstart, _ms(splits.VALIDATION_END))
    print("Regime mix (VALIDATION weeks):", regime_mix_text(regime_tags(st, sc, wks)))
    res, rows = {}, []
    for trial in trials:
        sg = SIDES[trial]
        ev = find_events(bars, sg)
        tr, fn = simulate(bars, ev, sg, funding=fund, start_ms=vstart)
        s = summarize(tr)
        res[trial] = s
        rows.append(row(trial, "VALIDATION", "primary", "regime B", s))
        print(trial, s, "funnel", {k: v for k, v in fn.items() if k != "log"})
    ps = [one_sided_p(res[x]) for x in trials]
    adj = research_kit.holm([1.0 if p != p else p for p in ps], m=15)
    for trial, p, a in zip(trials, ps, adj):
        print(f"{trial}: one-sided p {p:.4g}, Holm(m=15) adjusted {a:.4g}, pass={bool(a <= 0.05 and res[trial]['net'] > 0)}")
    with open(HERE / "cells.csv", "a", newline="\n", encoding="utf-8") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "count"
    if cmd == "count":
        cmd_count()
    elif cmd == "dev":
        cmd_dev()
    elif cmd == "validation":
        cmd_validation(sys.argv[2:] or ["T09", "T10"])
    else:
        raise SystemExit("usage: wick_context.py count|dev|validation [T09 T10]")
