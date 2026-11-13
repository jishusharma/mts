"""Tom's return-to-value on the prior NY cash-session value area. See PRE_REG.md (written before any outcome).

python -I study.py <npz_dir> <out_dir>      (npz from fetch_1m.py: columns t_ms,o,h,l,c,v)
"""
import sys
import json
import importlib.util
import datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import fees  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "auction_context", REPO / "MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py")
ac = importlib.util.module_from_spec(_spec)
sys.modules["auction_context"] = ac
_spec.loader.exec_module(ac)

MIN = 60_000
BLOCK = 30                                    # 30m closes
COST_SIDE = fees.BINANCE_TAKER + fees.BINANCE_TAKER / 5      # 5 bp taker + 1 bp slippage (OURS), per side
COST_RT = 2 * COST_SIDE
BUF_FRAC = fees.BINANCE_TAKER / 5             # 1 bp stop buffer beyond the session extreme (OURS)
MIN_STOP = fees.BINANCE_TAKER * 2             # 10 bp minimum stop distance (OURS)
BIN_FRAC = fees.BINANCE_TAKER                 # profile bin = 5 bp of price (OURS)
MIN_BARS_FRAC = 0.90
SPLIT_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
N_BOOT, N_PLC = 5000, 500


def load(npz_dir, sym):
    a = np.load(Path(npz_dir) / f"{sym}_1m.npz")["a"]
    return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5]


def sim_trade(side, entry_i, tgt, stop, H, L, C):
    """side +1 long / -1 short. Bars after entry_i. Returns (exit_price, kind, reach_any, reach_before_stop).
    Stop-first on a bar that touches both. Stop breached strictly (high > stop for short)."""
    n = len(C)
    if entry_i >= n - 1:
        return C[-1], "time", False, False
    if side == -1:
        hs = H[entry_i + 1:] > stop
        ht = L[entry_i + 1:] <= tgt
    else:
        hs = L[entry_i + 1:] < stop
        ht = H[entry_i + 1:] >= tgt
    i_s = int(np.argmax(hs)) if hs.any() else 10 ** 9
    i_t = int(np.argmax(ht)) if ht.any() else 10 ** 9
    reach_any = i_t < 10 ** 9
    if i_s <= i_t and i_s < 10 ** 9:
        return stop, "stop", reach_any, False
    if i_t < 10 ** 9:
        return tgt, "target", True, True
    return C[-1], "time", False, False


def net_r(side, entry, exit_, stop):
    risk = abs(stop - entry) / entry
    return (side * (exit_ - entry) / entry - COST_RT) / risk


def find_setup(inside_blocks, skip):
    """inside_blocks: list of bool per 30m block close. First pair of consecutive inside closes with first block index
    >= 1 (skip) or >= 0. Returns index of the second block, or None."""
    start = 1 if skip else 0
    for b in range(start, len(inside_blocks) - 1):
        if inside_blocks[b] and inside_blocks[b + 1]:
            return b + 1
    return None


def build_sessions(npz_dir, sym):
    t, o, h, l, c, v = load(npz_dir, sym)
    d0 = dt.datetime.fromtimestamp(t[0] / 1000, dt.timezone.utc).date()
    d1 = dt.datetime.fromtimestamp(t[-1] / 1000, dt.timezone.utc).date()
    days, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            days.append(d)
        d += dt.timedelta(days=1)
    sess = []   # dict per weekday session with a usable bar set
    for d in days:
        s0, s1 = ac.ny_session_window(d)
        i0, i1 = np.searchsorted(t, s0), np.searchsorted(t, s1)
        n_exp = (s1 - s0) // MIN
        if i1 - i0 < MIN_BARS_FRAC * n_exp or t[-1] < s1 - MIN:
            continue
        sess.append(dict(date=d, s0=s0, s1=s1, i0=i0, i1=i1,
                         hi=float(h[i0:i1].max()), lo=float(l[i0:i1].min()),
                         orng=float(h[i0:i0 + BLOCK].max() - l[i0:i0 + BLOCK].min())))
    return (t, o, h, l, c, v), sess


def prior_profile(bars, sess_prev, sess_cur):
    """VA of the prior session via the repo's prior_ny_session_profile, bars = only the prior session's 1m bars."""
    t, o, h, l, c, v = bars
    i0, i1 = sess_prev["i0"], sess_prev["i1"]
    px = float(c[i0:i1].mean())
    bs = [dict(t=int(t[k]), o=float(o[k]), h=float(h[k]), l=float(l[k]), c=float(c[k]), v=float(v[k])) for k in range(i0, i1)]
    p = ac.prior_ny_session_profile(bs, now_ms=sess_cur["s0"], bin_size=px * BIN_FRAC, step_ms=MIN)
    if p is None or p["date"] != sess_prev["date"].isoformat():
        return None
    return p


def day_events(sym, npz_dir):
    bars, sess = build_sessions(npz_dir, sym)
    t, o, h, l, c, v = bars
    events, n_sess = [], 0
    ors = []
    for k in range(1, len(sess)):
        cur, prev = sess[k], sess[k - 1]
        # prior session must be the previous weekday (no skipped weekday with missing data)
        gap = (cur["date"] - prev["date"]).days
        if not (gap == 1 or (gap == 3 and cur["date"].weekday() == 0)):
            ors.append(cur["orng"]); continue
        n_sess += 1
        prof = prior_profile(bars, prev, cur)
        hist_or = ors[-20:]
        ors.append(cur["orng"])
        if prof is None:
            continue
        vah, val = prof["vah"], prof["val"]
        i0, i1 = cur["i0"], cur["i1"]
        op = float(o[i0])
        if not (op > vah or op < val):
            continue
        side = -1 if op > vah else 1
        tgt = val if side == -1 else vah
        # balance flag
        inside_day = None
        if k >= 2 and (prev["date"] - sess[k - 2]["date"]).days in (1, 3):
            inside_day = prev["hi"] <= sess[k - 2]["hi"] and prev["lo"] >= sess[k - 2]["lo"]
        small_or = (len(hist_or) >= 20 and cur["orng"] < float(np.median(hist_or)))
        balanced = bool(inside_day) or bool(small_or)
        H, L, C = h[i0:i1], l[i0:i1], c[i0:i1]
        nb = len(C) // BLOCK
        close_blk = [C[(b + 1) * BLOCK - 1] for b in range(nb)]
        inside = [val <= x <= vah for x in close_blk]
        touch = bool((L <= vah).any()) if side == -1 else bool((H >= val).any())   # any 1m touch of the value edge facing price
        events.append(dict(sym=sym, date=cur["date"].isoformat(), ms=cur["s0"], side=side, balanced=balanced, poc=prof["poc"], touch=touch,
                           val=val, vah=vah, tgt=tgt, i0=i0, i1=i1, inside=inside, H=H, L=L, C=C))
    return events, n_sess, bars, sess


def run_trade(ev, skip):
    """Trade record for this event/variant or None (no setup, or stop too tight)."""
    b = find_setup(ev["inside"], skip)
    if b is None:
        return None
    ei = (b + 1) * BLOCK - 1                       # index of the 1m bar whose close is the second 30m close
    H, L, C = ev["H"], ev["L"], ev["C"]
    side = ev["side"]
    entry = float(C[ei])
    ext = float(H[:ei + 1].max()) if side == -1 else float(L[:ei + 1].min())
    stop = ext * (1 + BUF_FRAC) if side == -1 else ext * (1 - BUF_FRAC)
    if abs(stop - entry) / entry < MIN_STOP:
        return None
    ex, kind, ra, rb = sim_trade(side, ei, ev["tgt"], stop, H, L, C)
    poc = ev["poc"]
    if side == -1:
        reach_poc = bool((L[ei + 1:] <= poc).any()) if ei + 1 < len(L) else False
    else:
        reach_poc = bool((H[ei + 1:] >= poc).any()) if ei + 1 < len(H) else False
    rec = dict(reach_poc=reach_poc, sym=ev["sym"], date=ev["date"], ms=ev["ms"], side=side, balanced=ev["balanced"], skip=skip,
               R=net_r(side, entry, ex, stop), kind=kind, reach=ra, reach_bs=rb, ei=ei)
    # placebo candidates: later 1m closes inside value, same side/target, stop = running extreme at that bar
    runext = np.maximum.accumulate(H) if side == -1 else np.minimum.accumulate(L)
    cand = []
    for k in range(ei, len(C) - 1):
        if not (ev["val"] <= C[k] <= ev["vah"]):
            continue
        st = runext[k] * (1 + BUF_FRAC) if side == -1 else runext[k] * (1 - BUF_FRAC)
        if abs(st - C[k]) / C[k] < MIN_STOP:
            continue
        e2, _, _, _ = sim_trade(side, k, ev["tgt"], st, H, L, C)
        cand.append(net_r(side, float(C[k]), e2, st))
    rec["cand"] = np.array(cand)
    return rec


def boot_mean_ci(dates, R, rng):
    """Cluster (by session date) bootstrap of the mean. Returns mean, lo, hi, p(one-sided mean<=0)."""
    if len(R) == 0:
        return float("nan"), float("nan"), float("nan"), 1.0
    ud, inv = np.unique(dates, return_inverse=True)
    S = np.bincount(inv, weights=R); N = np.bincount(inv).astype(float)
    D = len(ud)
    cnt = rng.multinomial(D, np.ones(D) / D, size=N_BOOT)       # resample dates
    m = (cnt @ S) / (cnt @ N)
    return float(R.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((m <= 0).mean())


def bh(pvals, q=0.10):
    order = np.argsort(pvals)
    m = len(pvals)
    keep = np.zeros(m, bool)
    thr = -1
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            thr = rank
    for rank, i in enumerate(order, 1):
        if rank <= thr:
            keep[i] = True
    return keep


def main(npz_dir, out_dir):
    rng = np.random.default_rng(20261113)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    all_ev, cover, daily_btc = [], {}, None
    for sym in SYMS:
        ev, n_sess, bars, sess = day_events(sym, npz_dir)
        all_ev += ev
        t = bars[0]
        cover[sym] = dict(first=dt.datetime.fromtimestamp(t[0] / 1000, dt.timezone.utc).date().isoformat(),
                          last=dt.datetime.fromtimestamp(t[-1] / 1000, dt.timezone.utc).date().isoformat(),
                          bars=int(len(t)), sessions_used=len(sess), sessions_with_prior=n_sess, open_outside=len(ev))
        if sym == "BTCUSDT":
            daily_btc = bars
        print(sym, cover[sym], flush=True)
    trades = []
    for ev in all_ev:
        for skip in (True, False):
            r = run_trade(ev, skip)
            if r:
                trades.append(r)
    print("trades", len(trades), flush=True)
    # ---- cells
    def sel(split, skip, reg, side):
        o = []
        for r in trades:
            if r["skip"] != skip or r["side"] != side:
                continue
            if (r["ms"] >= SPLIT_MS) != (split == "VAL"):
                continue
            if reg == "balanced" and not r["balanced"]:
                continue
            if reg == "trending" and r["balanced"]:
                continue
            o.append(r)
        return o
    cells, rows = [], []
    for reg in ("all", "balanced", "trending"):
        for skip in (True, False):
            for side in (1, -1):
                cells.append((reg, skip, side))
    pvals = []
    for (reg, skip, side) in cells:
        dev, val = sel("DEV", skip, reg, side), sel("VAL", skip, reg, side)
        R = np.array([r["R"] for r in val]); d = np.array([r["date"] for r in val])
        mean, lo, hi, p = boot_mean_ci(d, R, rng)
        # placebo
        plc_means, plc_p95, beats = [], float("nan"), False
        vc = [r["cand"] for r in val if len(r["cand"])]
        if vc:
            draws = np.stack([rng.choice(cd, size=N_PLC) for cd in vc])      # trades x draws
            plc_means = draws.mean(axis=0)
            plc_p95 = float(np.percentile(plc_means, 95))
            beats = bool(len(R) and R.mean() > plc_p95)
            plc_mean = float(plc_means.mean())
        else:
            plc_mean = float("nan")
        row = dict(reg=reg, skip=skip, side="long" if side == 1 else "short",
                   n_dev=len(dev), n_val=len(val),
                   reach_dev=(100 * np.mean([r["reach"] for r in dev]) if dev else float("nan")),
                   reach_val=(100 * np.mean([r["reach"] for r in val]) if val else float("nan")),
                   reachbs_val=(100 * np.mean([r["reach_bs"] for r in val]) if val else float("nan")),
                   mean_dev=(float(np.mean([r["R"] for r in dev])) if dev else float("nan")),
                   mean_val=mean, lo=lo, hi=hi, p=p, plc_mean=plc_mean, plc_p95=plc_p95, beats=beats,
                   win_val=(100 * float(np.mean([r["R"] > 0 for r in val])) if val else float("nan")))
        rows.append(row); pvals.append(p)
    keep = bh(np.array(pvals))
    for row, k in zip(rows, keep):
        row["bh"] = bool(k)
        row["pass"] = bool(row["n_val"] >= 30 and row["mean_val"] > 0 and row["lo"] > 0 and row["beats"] and k)
    # per-symbol descriptive (both sides, all days)
    persym = []
    for sym in SYMS:
        for skip in (True, False):
            v = [r for r in trades if r["sym"] == sym and r["skip"] == skip and r["ms"] >= SPLIT_MS]
            dv = [r for r in trades if r["sym"] == sym and r["skip"] == skip and r["ms"] < SPLIT_MS]
            persym.append(dict(sym=sym, skip=skip, n_dev=len(dv), n_val=len(v),
                               reach_val=100 * np.mean([r["reach"] for r in v]) if v else float("nan"),
                               mean_val=float(np.mean([r["R"] for r in v])) if v else float("nan"),
                               mean_dev=float(np.mean([r["R"] for r in dv])) if dv else float("nan")))
    # supplementary descriptive counts (not cells): open-outside sessions, any touch of value, setups, reach POC / other edge
    supp = []
    for split in ("DEV", "VAL"):
        evs = [e for e in all_ev if (e["ms"] >= SPLIT_MS) == (split == "VAL")]
        row = dict(split=split, n_open_outside=len(evs), touch_value_pct=100 * float(np.mean([e["touch"] for e in evs])))
        for skip in (True, False):
            tr = [r for r in trades if r["skip"] == skip and (r["ms"] >= SPLIT_MS) == (split == "VAL")]
            row[f"skip{int(skip)}"] = dict(n=len(tr), setup_pct_of_open_outside=100 * len(tr) / len(evs),
                                           reach_poc_pct=100 * float(np.mean([r["reach_poc"] for r in tr])),
                                           reach_edge_pct=100 * float(np.mean([r["reach"] for r in tr])))
        supp.append(row)
    # regime mix of the windows (BTC close vs 200d SMA, band 5%) per UTC day
    t, o, h, l, c, v = daily_btc
    day = t // 86_400_000
    ud, first = np.unique(day, return_index=True)
    last = np.r_[first[1:], len(t)] - 1
    dclose = c[last]
    regs = {}
    for i in range(200, len(ud)):
        sma = dclose[i - 200:i].mean()
        lab = "bull" if dclose[i - 1] > sma * 1.05 else ("bear" if dclose[i - 1] < sma * 0.95 else "range")
        regs[int(ud[i])] = lab
    def mix(lo_ms, hi_ms):
        labs = [lab for d_, lab in regs.items() if lo_ms <= d_ * 86_400_000 < hi_ms]
        n = max(len(labs), 1)
        return {k: round(100 * labs.count(k) / n, 1) for k in ("bull", "bear", "range")}
    far = 10 ** 15
    mixes = dict(DEV=mix(0, SPLIT_MS), VAL=mix(SPLIT_MS, far))
    tmix = {}
    for split in ("DEV", "VAL"):
        tt = [r for r in trades if r["skip"] is True and ((r["ms"] >= SPLIT_MS) == (split == "VAL"))]
        labs = [regs.get(r["ms"] // 86_400_000, "n/a") for r in tt]
        n = max(len(labs), 1)
        tmix[split] = {k: round(100 * labs.count(k) / n, 1) for k in ("bull", "bear", "range", "n/a")}
        tmix[split]["balanced_share"] = round(100 * float(np.mean([r["balanced"] for r in tt])) if tt else 0, 1)
        tmix[split]["n_trades_skip_yes"] = len(tt)
    # event-level (open outside) count: share balanced, n
    res = dict(supp=supp, cover=cover, rows=rows, persym=persym, mixes=mixes, trade_mix=tmix,
               cost=dict(side=COST_SIDE, rt=COST_RT, buf=BUF_FRAC, min_stop=MIN_STOP, bin_frac=BIN_FRAC),
               n_open_outside=len(all_ev))
    (out / "results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps(res["trade_mix"]), json.dumps(mixes), flush=True)
    for r in rows:
        print(r, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
