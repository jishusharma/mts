"""Run the frozen PRE_REG.md (pre-US failed-break short, BTCUSDT 1m) sections 2-7 once on DEV 2022-01-01..2024-06-30, fee-net.

Card backtest-pre-us-failed-break-dev-run. Every number is from PRE_REG.md; reading choices where the text is silent are
listed in DECISIONS and printed (conservative side). The loader refuses any bar with open >= 2024-07-01 (section 6).
Writes ledger.csv, cells.json. RESULT.md is written by hand from the printed output.
"""
import csv
import datetime as dt
import glob
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

DATA_GLOB = "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-20??-??.csv"
DEV_START_MS = 1640995200000          # 2022-01-01 00:00Z
DEV_END_MS = 1719792000000            # 2024-07-01 00:00Z, exclusive (section 6)
MIN_MS, HOUR, DAY = 60000, 3600000, 86400000
TICK = 0.1
TAKER, MAKER, SLIP = 0.0005, 0.0002, 0.0002     # fees.py:27-28 (BINANCE_*); slippage 2 bps per taker leg (section 5)
FUND_BP = 1.0                                    # flat 1 bp when held across 08:00Z, raw_fund absent (section 5)
BRK, EXC, FAILN = 0.10, 1.5, 3                   # section 2
LVL_MIN = 0.5                                    # level at least 0.5 ATR above the day's 00:00 open
TR_N = 4                                         # tranches (section 3)
NMIN = 250

DECISIONS = [
    "levels (PDH/ASH/swing) are fixed from bars BEFORE the break bar; a level counts only if >= 0.5 ATR above the day's 00:00 open",
    "break = first crossing per level per day with the break bar open inside W; ATR(break) used for break/E, ATR(signal bar) for the trade",
    "high of a bar that pushes E above 1.5 ATR kills the level even if that bar also closes below L (high precedes close)",
    "ATR = last 1h bar whose close time <= signal bar close; Wilder, seeded with the mean of the first 14 TR",
    "limit tranches and the target are active from bar t+2 (bar t+1 only holds the open fill); limit fills at its own price on trade-through of one tick",
    "same bar hits both the target and a higher tranche limit: target first (tranche not filled), the conservative order",
    "time-cap exit at the open of the window-end bar, taker, +2 bps slippage; funding: raw_fund absent -> flat 1 bp of the open size at 08:00Z (funding NOT_IN_DATA)",
    "one position per day: only the first signal of the day is traded; the 3-per-day cap is therefore moot",
    "second reported variant 'window end 13:00' equals the primary (PRE_REG s10 names it, defines nothing different): printed once as primary",
]


def load_dev():
    """Monthly BTCUSDT 1m files only, strictly open < DEV_END_MS. Raises on any bar at/after 2024-07-01 inside a file we read."""
    t, o, h, l, c = [], [], [], [], []
    for f in sorted(glob.glob(DATA_GLOB)):
        ym = Path(f).stem.split("-1m-")[1]
        if ym >= "2024-07":
            continue                                  # month file wholly after DEV: never opened
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                ts = int(row[0])
                if ts >= DEV_END_MS:
                    raise ValueError("bar dated %s is at or after 2024-07-01 (section 6)" % dt.datetime.fromtimestamp(ts / 1000, dt.timezone.utc))
                if ts < DEV_START_MS:
                    continue
                t.append(ts); o.append(float(row[1])); h.append(float(row[2])); l.append(float(row[3])); c.append(float(row[4]))
    return t, o, h, l, c


class Tape:
    def __init__(self, t, o, h, l, c):
        self.t, self.o, self.h, self.l, self.c = t, o, h, l, c
        self.idx = {x: i for i, x in enumerate(t)}
        # 1h bars from full hours present
        hs, ho, hh, hl, hc = [], [], [], [], []
        i, n = 0, len(t)
        while i < n:
            hstart = t[i] - t[i] % HOUR
            j = i
            while j < n and t[j] < hstart + HOUR:
                j += 1
            hs.append(hstart); ho.append(o[i]); hh.append(max(h[i:j])); hl.append(min(l[i:j])); hc.append(c[j - 1])
            i = j
        self.hs, self.ho, self.hh, self.hl, self.hc = hs, ho, hh, hl, hc
        self.hidx = {x: i for i, x in enumerate(hs)}
        tr = [None] + [max(hh[k] - hl[k], abs(hh[k] - hc[k - 1]), abs(hl[k] - hc[k - 1])) for k in range(1, len(hs))]
        atr = [None] * len(hs)
        if len(hs) > 14:
            a = sum(tr[1:15]) / 14.0
            atr[14] = a
            for k in range(15, len(hs)):
                a = (a * 13 + tr[k]) / 14.0
                atr[k] = a
        self.atr = atr
        # swing highs / lows: bar higher/lower than both neighbours; usable at hour start + 3h
        self.swh = [k for k in range(1, len(hs) - 1) if hh[k] > hh[k - 1] and hh[k] > hh[k + 1]]
        self.swl = [k for k in range(1, len(hs) - 1) if hl[k] < hl[k - 1] and hl[k] < hl[k + 1]]

    def atr_at(self, ts):
        """ATR of the last 1h bar closed at or before the close of 1m bar ts."""
        close = ts + MIN_MS
        k = self.hidx.get(close - HOUR - (close % HOUR), None) if close % HOUR == 0 else self.hidx.get((close - close % HOUR) - HOUR)
        return None if k is None else self.atr[k]

    def swing(self, which, day0, b_ts):
        ks = self.swh if which == "h" else self.swl
        arr = self.hh if which == "h" else self.hl
        lo = day0 - 5 * DAY
        vals = [arr[k] for k in ks if lo <= self.hs[k] and self.hs[k] + 3 * HOUR <= b_ts]
        if not vals:
            return None
        return max(vals) if which == "h" else min(vals)


def day_range(tp, day0):
    a = tp.idx.get(day0)
    if a is None:
        return None
    b = a
    n = len(tp.t)
    while b < n and tp.t[b] < day0 + DAY:
        b += 1
    return a, b


def run(tp, wend_h):
    wend = wend_h * HOUR
    days = sorted({x - x % DAY for x in tp.t})
    eps = []
    nsig = 0
    for di, day0 in enumerate(days):
        if di < 5:
            continue
        rng = day_range(tp, day0)
        prev = day_range(tp, day0 - DAY)
        if rng is None or prev is None:
            continue
        a, b = rng
        pa, pb = prev
        pdh, pdl = max(tp.h[pa:pb]), min(tp.l[pa:pb])
        open0 = tp.o[a]
        w0, w1 = day0 + 7 * HOUR, day0 + wend
        sigs = []
        # candidate levels per break bar
        for name in ("PDH", "ASH", "SWH"):
            fired = False
            for i in range(a, b):
                ts = tp.t[i]
                if ts < w0 or ts >= w1:
                    continue
                atr_b = tp.atr_at(ts)
                if atr_b is None:
                    continue
                if name == "PDH":
                    L = pdh
                elif name == "ASH":
                    seg = tp.h[a:i]
                    if not seg:
                        continue
                    m = max(seg)
                    k = a + seg.index(m)
                    if i - k < 60:
                        continue
                    L = m
                else:
                    L = tp.swing("h", day0, ts)
                    if L is None:
                        continue
                if L < open0 + LVL_MIN * atr_b:
                    continue
                if tp.h[i] > L + BRK * atr_b:
                    # first crossing for this level
                    dead, sig = False, None
                    for j in range(i, min(i + FAILN + 1, b)):
                        if (max(tp.h[i:j + 1]) - L) / atr_b > EXC:
                            dead = True
                            break
                        if tp.c[j] < L:
                            sig = j
                            break
                    if sig is not None and not dead:
                        sigs.append((sig, name, L))
                    fired = True
                if fired:
                    break
        if not sigs:
            continue
        sigs.sort()
        nsig += len(sigs)
        ti, lname, L = sigs[0]
        ei = ti + 1
        if ei >= b or tp.t[ei] >= w1:
            continue
        atr = tp.atr_at(tp.t[ti])
        e1 = tp.o[ei]
        ep = trade(tp, day0, a, b, ei, atr, e1, w1)
        ep.update(day=dt.datetime.fromtimestamp(day0 / 1000, dt.timezone.utc).strftime("%Y-%m-%d"), level=lname, L=L)
        eps.append(ep)
    return eps, nsig


def trade(tp, day0, a, b, ei, atr, e1, w1):
    fills = [(e1 * (1 - SLIP), 0.25, "T")]                      # sell, taker, slippage against us
    limits = [e1 + j * 0.5 * atr for j in range(1, TR_N)]
    # S_dn candidates as of the signal bar close
    ts_sig = tp.t[ei - 1]
    cands = [min(tp.l[a:ei]), min(tp.l[tp.idx[day0 - DAY]:a])]
    sw = tp.swing("l", day0, ts_sig)
    if sw is not None:
        cands.append(sw)
    ok = [x for x in cands if x <= e1 - 1.0 * atr]
    target = max(ok) if ok else e1 - 1.5 * atr
    nfill = 1
    mae = 0.0
    exit_px, kind = None, None
    for i in range(ei + 1, b):
        ts = tp.t[i]
        if ts >= w1:
            exit_px, kind = tp.o[i] * (1 + SLIP), "TIMECAP"
            break
        if tp.l[i] <= target - TICK:
            exit_px, kind = target, "TARGET"
            mae = max(mae, _mae(fills, tp.h[i]))
            break
        while nfill < TR_N and tp.h[i] >= limits[nfill - 1] + TICK:
            fills.append((limits[nfill - 1], 0.25, "M"))
            nfill += 1
        mae = max(mae, _mae(fills, tp.h[i]))
    if exit_px is None:                                           # window end beyond data day end
        exit_px, kind = tp.c[b - 1] * (1 + SLIP), "TIMECAP"
    gross = net = 0.0
    held_0800 = day0 + 8 * HOUR
    for px, size, how in fills:
        units = size / px
        g = units * (px - exit_px) if how == "T" else units * (px - exit_px)
        fee_in = (TAKER if how == "T" else MAKER) * size
        fee_out = (TAKER if kind == "TIMECAP" else MAKER) * units * exit_px
        gross += g
        net += g - fee_in - fee_out
    # slippage already inside e1*(1-SLIP) and the cap exit price; target-hit tranche exits are maker, 0 slip
    # funding: flat 1 bp of the open size when the position straddles 08:00Z
    if tp.t[ei] < held_0800 and (kind == "TIMECAP" or True) and _exit_ts(tp, ei, b, exit_px, kind, target, w1) > held_0800:
        net -= FUND_BP * 1e-4 * sum(f[1] for f in fills)
    return {"entry_ts": tp.t[ei], "entry": e1, "n_tr": len(fills), "kind": kind, "gross": gross, "net": net, "mae": mae,
            "target": target, "atr": atr}


def _exit_ts(tp, ei, b, exit_px, kind, target, w1):
    for i in range(ei + 1, b):
        if tp.t[i] >= w1:
            return tp.t[i]
        if kind == "TARGET" and tp.l[i] <= target - TICK:
            return tp.t[i]
    return tp.t[b - 1]


def _mae(fills, high):
    return sum(sz * (high - px) / px for px, sz, _ in fills if high > px)


def stats(eps, bh_mdd):
    n = len(eps)
    nets = [e["net"] * 100 for e in eps]                          # % of K
    out = {"n": n}
    if n < 2:
        out["verdict"] = "INCONCLUSIVE"
        return out
    m = sum(nets) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in nets) / (n - 1))
    se = sd / math.sqrt(n)
    t = m / se if se else 0.0
    win = [x for x in nets if x > 0]
    los = [x for x in nets if x <= 0]
    cum, peak, mdd = 0.0, 0.0, 0.0
    for e in sorted(eps, key=lambda z: z["day"]):
        cum += e["net"] * 100
        peak = max(peak, cum)
        mdd = max(mdd, peak - cum)
    tc = [e for e in eps if e["kind"] == "TIMECAP"]
    tg = [e for e in eps if e["kind"] == "TARGET"]
    maes = sorted(e["mae"] * 100 for e in eps)
    q = lambda p: maes[min(n - 1, int(p * n))]
    out.update(mean_pct=m, sd_pct=sd, se_pct=se, t=t, win_rate=len(win) / n,
               mean_win=sum(win) / len(win) if win else 0.0, mean_loss=sum(los) / len(los) if los else 0.0,
               mae_p50=q(0.5), mae_p90=q(0.9), mae_max=maes[-1],
               timecap_days=len(tc), timecap_sum=sum(e["net"] * 100 for e in tc),
               target_days=len(tg), target_sum=sum(e["net"] * 100 for e in tg),
               mdd_pct=mdd, bh_mdd_pct=bh_mdd, mean_bps=m * 100)
    if n < NMIN:
        v = "INCONCLUSIVE"
    elif m > 0 and t >= 2.0 and -out["timecap_sum"] < out["target_sum"] and mdd <= bh_mdd:
        v = "PASS"
    else:
        v = "FAIL"
    out["verdict"] = v
    return out


def bh_mdd(tp):
    pk, mdd = 0.0, 0.0
    for i in range(1439, len(tp.c), 1440):
        pass
    daily = {}
    for ts, cl in zip(tp.t, tp.c):
        daily[ts - ts % DAY] = cl
    for d in sorted(daily):
        cl = daily[d]
        pk = max(pk, cl)
        mdd = max(mdd, (pk - cl) / pk * 100)
    return mdd


def regime_mix():
    """Weekly regime mix over DEV via research_kit (needs 2019+ history for the monthly RSI), same helper as sibling studies."""
    import importlib.util
    import json as _j
    from MyTradingSys.backtest import research_kit as rk
    sp = importlib.util.spec_from_file_location("sib", REPO / "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py")
    sib = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(sib)
    registry = _j.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    bars = {}
    for f in sorted(glob.glob("F:/MTS/data/dev_ext_2019_2021/klines/BTCUSDT-1m-20??-??.csv")) + sorted(glob.glob(DATA_GLOB)):
        if Path(f).stem.split("-1m-")[1] >= "2024-07":
            continue
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh)
            next(r)
            for row in r:
                ts = int(row[0])
                if ts >= DEV_END_MS:
                    raise ValueError("bar at/after 2024-07-01")
                bars[ts] = {"t": ts, "o": float(row[1]), "h": float(row[2]), "l": float(row[3]), "c": float(row[4]), "v": float(row[5])}
    bars = [bars[k] for k in sorted(bars)]
    daily, wk, mo = sib.build_context(bars, registry)
    reg = sib.make_regime_at(daily, wk, mo)
    return rk.regime_mix_line([reg(x) for x in sib.week_starts(DEV_START_MS, DEV_END_MS)]), reg


def regime_only():
    """Add the regime columns to ledger.csv / cells.json written by the DEV pass (no re-run of the cells)."""
    line, reg = regime_mix()
    print("Regime mix:", line)
    rows = list(csv.DictReader(open(HERE / "ledger.csv", encoding="utf-8")))
    mix = {}
    for r in rows:
        d0 = int(dt.datetime.strptime(r["day"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        r["regime"] = reg(d0) or "n/a"
        mix[r["regime"]] = mix.get(r["regime"], 0) + 1
    print("episodes by regime:", mix)
    with open(HERE / "ledger.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator=chr(10))
        w.writeheader()
        w.writerows(rows)
    cells = json.loads((HERE / "cells.json").read_text(encoding="utf-8"))
    cells["regime_mix"], cells["episodes_by_regime"] = line, mix
    (HERE / "cells.json").write_text(json.dumps(cells, indent=1, sort_keys=True) + chr(10), encoding="utf-8", newline=chr(10))


def main():
    if "--regime-only" in sys.argv:
        return regime_only()
    t, o, h, l, c = load_dev()
    print("DEV bars %d  %s .. %s" % (len(t), dt.datetime.fromtimestamp(t[0] / 1000, dt.timezone.utc), dt.datetime.fromtimestamp(t[-1] / 1000, dt.timezone.utc)))
    tp = Tape(t, o, h, l, c)
    bh = bh_mdd(tp)
    print("buy-and-hold BTC max drawdown over DEV (daily close): %.1f %%" % bh)
    print("funding NOT_IN_DATA (flat 1 bp across 08:00Z)")
    for d in DECISIONS:
        print("DECISION (OURS):", d)
    cells = {}
    for name, wh in (("primary_W13", 13), ("variant_W12", 12)):
        eps, nsig = run(tp, wh)
        s = stats(eps, bh)
        s["signals"] = nsig
        cells[name] = s
        print("CELL", name, json.dumps(s, sort_keys=True))
        if name == "primary_W13":
            prim = eps
    with open(HERE / "ledger.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["day", "level", "L", "entry_ts", "entry", "n_tranches", "exit_kind", "gross_pctK", "net_pctK", "mae_pctK", "target", "atr"])
        for e in prim:
            w.writerow([e["day"], e["level"], "%.1f" % e["L"], e["entry_ts"], "%.1f" % e["entry"], e["n_tr"], e["kind"],
                        "%.4f" % (e["gross"] * 100), "%.4f" % (e["net"] * 100), "%.4f" % (e["mae"] * 100), "%.1f" % e["target"], "%.1f" % e["atr"]])
    (HERE / "cells.json").write_text(json.dumps(cells, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("VERDICT (section 7, primary):", cells["primary_W13"]["verdict"])


if __name__ == "__main__":
    main()
