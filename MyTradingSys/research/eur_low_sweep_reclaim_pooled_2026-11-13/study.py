"""EUR-LOW sweep -> reclaim -> LONG (and mirror short), pooled BTC/ETH/SOL Bybit 5m linear. See PRE_REG.md.

    python study.py --count     geometry only (events, stop distance); computes NO outcome
    python study.py --run       full outcomes (only after PRE_REG.md is committed)
Outcome helpers are named fwd_* (look-ahead lint: they read bars after the decision by design).
"""
import argparse, collections, json, os, sys
from datetime import datetime, timezone
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest"))
import fees  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "..", "runtime_data", "edge-session-sweep-reclaim-1113")
M5, DAY = 300000, 86400000
EU0, EU1, US0, US1 = 84, 162, 162, 240        # 5-min slots: 07:00, 13:30, 13:30, 20:00 (UTC, fixed)
RECLAIM_BARS = 12                              # 60 min
MIN_RISK = 0.0015                              # OURS, skip if entry-stop < 0.15 %
MAKER_WAIT = 12                                # bars the resting limit lives (OURS)
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
DEV_END, VAL_END = "2024-06-30", "2025-06-30"
DRAWS, BOOT, SEED = 200, 2000, 1113
EXITS = ["MID", "HIGH", "2R"]
ENTRIES = ["taker", "maker"]
SIDES = ["long", "short"]
CELLS = [(s, x, e) for s in SIDES for x in EXITS for e in ENTRIES]


def load(sym):
    rows = json.load(open(os.path.join(DATA, sym + "_5m.json")))
    t0 = rows[0][0] - rows[0][0] % DAY
    n = int((rows[-1][0] - t0) // M5) + 1
    n += (-n) % 288
    a = np.full((4, n), np.nan)
    for r in rows:
        a[:, int((r[0] - t0) // M5)] = (r[1], r[2], r[3], r[4])
    return t0, a[0], a[1], a[2], a[3]   # t0, o, h, l, c


def day_levels(h, l, d0):
    h_eu, l_eu = h[d0 + EU0:d0 + EU1], l[d0 + EU0:d0 + EU1]
    if np.isnan(h_eu).sum() > 3 or np.isnan(l_eu).sum() > 3:
        return None
    return float(np.nanmin(l_eu)), float(np.nanmax(h_eu))


def find_event(side, o, h, l, c, d0, EL, EH):
    """Decision-time geometry only. Nothing after the reclaim bar is read."""
    lvl = EL if side == "long" else EH
    i0 = None
    for i in range(d0 + US0, d0 + US1):
        if np.isnan(l[i]) or np.isnan(h[i]):
            continue
        if (side == "long" and l[i] < lvl) or (side == "short" and h[i] > lvl):
            i0 = i
            break
    if i0 is None:
        return None
    j = None
    for k in range(i0, min(i0 + RECLAIM_BARS, d0 + US1)):
        if np.isnan(c[k]):
            continue
        if (side == "long" and c[k] > lvl) or (side == "short" and c[k] < lvl):
            j = k
            break
    if j is None or j + 1 >= d0 + US1 or np.isnan(o[j + 1]):
        return None
    S = float(np.nanmin(l[i0:j + 1])) if side == "long" else float(np.nanmax(h[i0:j + 1]))
    return {"side": side, "i0": i0, "j": j, "S": S, "lvl": lvl, "EL": EL, "EH": EH}


def geometry(side, ev, entry_px):
    return entry_px - ev["S"] if side == "long" else ev["S"] - entry_px


def target_px(side, kind, entry, risk, EL, EH):
    if kind == "2R":
        return entry + 2 * risk if side == "long" else entry - 2 * risk
    mid = (EL + EH) / 2
    if side == "long":
        t = mid if kind == "MID" else EH
        return t if t > entry else None
    t = mid if kind == "MID" else EL
    return t if t < entry else None


def fwd_sim(side, l, h, c, e, end, stop, tgt):
    """From entry slot e (filled at its open) to slot end-1. Stop wins a same-bar tie. Returns exit price."""
    lo, hi = l[e:end], h[e:end]
    if side == "long":
        s_hit = np.nonzero(lo <= stop)[0]
        t_hit = np.nonzero(hi >= tgt)[0]
    else:
        s_hit = np.nonzero(hi >= stop)[0]
        t_hit = np.nonzero(lo <= tgt)[0]
    si = s_hit[0] if len(s_hit) else 10 ** 9
    ti = t_hit[0] if len(t_hit) else 10 ** 9
    if si == 10 ** 9 and ti == 10 ** 9:
        v = c[e:end]
        v = v[~np.isnan(v)]
        return float(v[-1])
    return stop if si <= ti else tgt


def net_r(side, entry, exit_, risk, entry_kind):
    pnl = exit_ - entry if side == "long" else entry - exit_
    fee = (fees.BINANCE_MAKER if entry_kind == "maker" else fees.BINANCE_TAKER) * entry + fees.BINANCE_TAKER * exit_
    return (pnl - fee) / risk


def fwd_trade(side, ev, kind, entry_kind, o, h, l, c, d0):
    """Real trade for one cell. Returns (net R, risk_pct, target in R) or None."""
    j, S = ev["j"], ev["S"]
    end = d0 + US1
    if entry_kind == "taker":
        fill_slot = j + 1
        entry = float(o[fill_slot])
    else:                                  # resting limit at the reclaimed level, trade-through, lives 60 min
        entry, fill_slot = ev["lvl"], None
        for k in range(j + 1, min(j + 1 + MAKER_WAIT, end - 1)):
            if np.isnan(l[k]):
                continue
            if (side == "long" and l[k] <= S) or (side == "short" and h[k] >= S):
                return None                # stop level touched before any fill: cancelled
            if (side == "long" and l[k] < entry) or (side == "short" and h[k] > entry):
                fill_slot = k + 1          # filled in bar k; bar k is not scanned for exits (conservative)
                break
        if fill_slot is None or fill_slot >= end:
            return None
    risk = geometry(side, ev, entry)
    if risk <= 0 or risk / entry < MIN_RISK:
        return None
    tgt = target_px(side, kind, entry, risk, ev["EL"], ev["EH"])
    if tgt is None:
        return None
    xit = fwd_sim(side, l, h, c, fill_slot, end, S, tgt)
    return net_r(side, entry, xit, risk, entry_kind), risk / entry, abs(tgt - entry) / risk


def fwd_placebo(side, ev, entry_kind, rpct, tR, o, h, l, c, d0, rng):
    """Random 5m bar in the same US window whose previous close is above EL (long) / below EH (short);
    same stop %, same target in R, same time stop, same fee kind (filled at the open: favourable to the placebo)."""
    lvl = ev["EL"] if side == "long" else ev["EH"]
    cand = [e for e in range(d0 + US0 + 1, d0 + US1)
            if not np.isnan(c[e - 1]) and not np.isnan(o[e]) and ((c[e - 1] > lvl) if side == "long" else (c[e - 1] < lvl))]
    if not cand:
        return None
    e = cand[rng.integers(len(cand))]
    entry = float(o[e])
    risk = entry * rpct
    stop = entry - risk if side == "long" else entry + risk
    tgt = entry + tR * risk if side == "long" else entry - tR * risk
    return net_r(side, entry, fwd_sim(side, l, h, c, e, d0 + US1, stop, tgt), risk, entry_kind)


def events_for(sym):
    t0, o, h, l, c = load(sym)
    out = []
    for d in range(len(o) // 288):
        d0 = d * 288
        day = datetime.fromtimestamp((t0 + d * DAY) / 1000, timezone.utc)
        if day.weekday() >= 5:
            continue
        lv = day_levels(h, l, d0)
        if lv is None:
            continue
        for side in SIDES:
            ev = find_event(side, o, h, l, c, d0, *lv)
            if ev:
                ev.update(sym=sym, d0=d0, date=day.strftime("%Y-%m-%d"))
                out.append(ev)
    return (o, h, l, c), out


def split_of(date):
    return "DEV" if date <= DEV_END else "VAL" if date <= VAL_END else "RECENT"


def count():
    rows = []
    for sym in SYMS:
        (o, h, l, c), evs = events_for(sym)
        for ev in evs:
            ent = float(o[ev["j"] + 1])
            rows.append((sym, ev["side"], ev["date"], geometry(ev["side"], ev, ent) / ent))
    return rows


def boot_ci(day_ids, rs, rng):
    u, inv = np.unique(day_ids, return_inverse=True)
    s = np.bincount(inv, weights=rs)
    n = np.bincount(inv)
    idx = rng.integers(len(u), size=(BOOT, len(u)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (BOOT + 1))


def run():
    rng = np.random.default_rng(SEED)
    recs = {cell: [] for cell in CELLS}    # (sym, date, R, placebo draws)
    for sym in SYMS:
        (o, h, l, c), evs = events_for(sym)
        for ev in evs:
            for kind in EXITS:
                for ek in ENTRIES:
                    r = fwd_trade(ev["side"], ev, kind, ek, o, h, l, c, ev["d0"])
                    if r is None:
                        continue
                    R, rpct, tR = r
                    pl = [fwd_placebo(ev["side"], ev, ek, rpct, tR, o, h, l, c, ev["d0"], rng) for _ in range(DRAWS)]
                    if any(p is None for p in pl):
                        continue
                    recs[(ev["side"], kind, ek)].append((sym, ev["date"], R, pl))
        print(sym, "done", flush=True)
    return recs


def summarize(recs):
    rng = np.random.default_rng(SEED + 1)
    res = {}
    for cell, rr in recs.items():
        for sp in ["DEV", "VAL", "RECENT", "ALL"]:
            sel = [x for x in rr if sp == "ALL" or split_of(x[1]) == sp]
            if not sel:
                res[(cell, sp)] = {"n": 0}
                continue
            R = np.array([x[2] for x in sel])
            days = np.array([x[1] for x in sel])
            P = np.array([x[3] for x in sel]).mean(0)          # draw-set means
            lo, hi, p = boot_ci(days, R, rng)
            res[(cell, sp)] = {"n": len(R), "ndays": len(set(days)), "mean": float(R.mean()), "lo": lo, "hi": hi, "p": p,
                               "hit": float((R > 0).mean()), "pl_mean": float(P.mean()), "pl_p95": float(np.percentile(P, 95)),
                               "beats": bool(R.mean() > np.percentile(P, 95))}
        for sym in SYMS:
            sel = [x for x in rr if x[0] == sym and split_of(x[1]) == "VAL"]
            res[(cell, "VAL:" + sym)] = {"n": len(sel), "mean": float(np.mean([x[2] for x in sel])) if sel else None}
    return res


def bh(pvals, q=0.10):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m, k = len(pvals), 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            k = rank
    return {order[r] for r in range(k)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.count:
        rows = count()
        by = collections.defaultdict(list)
        for sym, side, date, rp in rows:
            by[(side, split_of(date))].append(rp)
        for k in sorted(by):
            v = np.array(by[k])
            print(k, "events", len(v), "median stop %", round(float(np.median(v)) * 100, 3))
        for side in SIDES:
            v = np.array([r[3] for r in rows if r[1] == side])
            print(side, "ALL events", len(v), "median stop %", round(float(np.median(v)) * 100, 3))
        print("event-days:", len({(r[0], r[2]) for r in rows}), "VAL event-days:", len({(r[0], r[2]) for r in rows if split_of(r[2]) == "VAL"}))
    if a.run:
        recs = run()
        res = summarize(recs)
        json.dump({"|".join(map(str, k)): v for k, v in res.items()}, open(os.path.join(HERE, "results.json"), "w"), indent=1)
        print("ok")
