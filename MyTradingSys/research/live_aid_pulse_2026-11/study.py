"""Live Aid pulse SETUP FORMING backtest (card live-aid-pulse-backtest-1109). DEV only. See PRE_REG.md for every rule.

    python study.py events [--from YYYY-MM-DD --to YYYY-MM-DD] [--out events.json]   stage 1: grid + setup at every 5-min decision
                                                                                      time near a level; reads NO price outcome
    python study.py counts                                                           count-only numbers for the PRE_REG gate (stage 1 output)
    python study.py outcomes                                                         stage 2: forward returns, null, CI, JSON (needs a frozen PRE_REG)

Data: BTCUSDT USD-M 1m klines in F:/MTS/data/tom_raw/klines (SOURCED: the repo research tape). Files dated 2024-07 or later are never opened.
"""
import argparse
import datetime as dt
import glob
import json
import multiprocessing as mp
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "backtest"))
import pulse_port as PP  # noqa: E402
from fees import BINANCE_TAKER, SLIPPAGE_RT_S13  # noqa: E402  shared cost source: 2 x taker = 10 bp round trip; s13 slippage 2 bp round trip

KLINES = os.environ.get("PULSE_KLINES", "F:/MTS/data/tom_raw/klines")
MIN, DAY = 60_000, 86_400_000
DEV_END = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)   # HOLDOUT/VALIDATION start: never read
FIRST_FILE = "2022-01"
STEP = 5 * MIN                      # decision cadence (OURS)
HORIZONS = (15, 30, 60)             # minutes
FEE_BP = BINANCE_TAKER * 2 * 1e4    # 10 bp
SLIP_BP_RT = SLIPPAGE_RT_S13 * 1e4 * 2   # OURS: twice the FORMULAS s13 round-trip allowance = 2 bp per side (PRE_REG_VOLUME_2026-10-09 convention), 4 bp
COST_BP = round(FEE_BP + SLIP_BP_RT, 9)   # 14 bp primary
COOLDOWN = 60 * MIN
SESSIONS = (("Asia", 0, 8), ("Europe", 8, 13), ("US", 13, 21), ("Late", 21, 24))   # UTC hours (OURS)
EVAL_FROM_DEFAULT = "2022-02-01"
NLAST = {"1m": 1000, "other": 150}   # candles the live page holds (live_aid.html l.1567: 1000 for 1m, 150 for the rest)
FOLD_MS = (180_000, 300_000, 900_000, 1_800_000, 3_600_000, 7_200_000, 14_400_000)
NAMES = {180_000: "3m", 300_000: "5m", 900_000: "15m", 1_800_000: "30m", 3_600_000: "1h", 7_200_000: "2h", 14_400_000: "4h"}


def session_of(t):
    h = (t % DAY) // 3_600_000
    for n, a, b in SESSIONS:
        if a <= h < b:
            return n
    return "Late"


def load_1m():
    import pandas as pd
    files = sorted(glob.glob(KLINES + "/BTCUSDT-1m-*.csv"))
    files = [f for f in files if FIRST_FILE <= Path(f).stem[-7:] < "2024-07"]
    assert files, "no 1m files"
    assert max(Path(f).stem[-7:] for f in files) <= "2024-06"
    df = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4, 5, 9]) for f in files], ignore_index=True)
    a = df.to_numpy(dtype=float)
    a = a[np.argsort(a[:, 0], kind="stable")]
    a = a[np.concatenate(([True], np.diff(a[:, 0]) > 0))]
    assert a[-1, 0] < DEV_END, "HOLDOUT/VALIDATION bar loaded"
    return a        # columns: t, o, h, l, c, v, buy


def fold_arrays(a, ms):
    """Full-history buckets (UTC-day aligned == epoch aligned for these ms); only completed buckets are used per decision."""
    bid = (a[:, 0] // ms).astype(np.int64)
    cut = np.concatenate(([0], np.nonzero(np.diff(bid))[0] + 1))
    end = np.concatenate((cut[1:], [len(a)]))
    start = bid[cut] * ms
    o = a[cut, 1]
    h = np.maximum.reduceat(a[:, 2], cut)
    l = np.minimum.reduceat(a[:, 3], cut)
    c = a[end - 1, 4]
    v = np.add.reduceat(a[:, 5], cut)
    b = np.add.reduceat(a[:, 6], cut)
    return np.column_stack((start, o, h, l, c, v, start + ms - 1, np.zeros(len(cut)), np.zeros(len(cut)), b))


def level_tables(a):
    """Per UTC day: o, h, l, c, n bars, Asia high/low (00-08Z). Per week (Monday start): o, h, l."""
    day = (a[:, 0] // DAY).astype(np.int64)
    cut = np.concatenate(([0], np.nonzero(np.diff(day))[0] + 1))
    end = np.concatenate((cut[1:], [len(a)]))
    D = {}
    for s, e in zip(cut, end):
        d = int(day[s])
        seg = a[s:e]
        asia = seg[(seg[:, 0] - d * DAY) < 8 * 3_600_000]
        D[d] = {"o": seg[0, 1], "h": seg[:, 2].max(), "l": seg[:, 3].min(), "c": seg[-1, 4], "n": e - s,
                "ah": asia[:, 2].max() if len(asia) else None, "al": asia[:, 3].min() if len(asia) else None}
    W = {}
    for d, x in D.items():
        w = d - (d + 3) % 7                    # epoch day 0 is a Thursday: Monday days have (d + 3) % 7 == 0
        r = W.setdefault(w, {"o": None, "h": -1e18, "l": 1e18, "n": 0, "d0": d})
        if r["o"] is None or d < r["d0"]:
            r["o"], r["d0"] = x["o"], d
        r["h"], r["l"], r["n"] = max(r["h"], x["h"]), min(r["l"], x["l"]), r["n"] + 1
    return D, W


def levels_at(T, D, W):
    d = T // DAY
    w = d - (d + 3) % 7
    items = []

    def add(price, label):
        if price is not None and price > 0:
            items.append({"price": float(price), "label": label})
    p = D.get(d - 1)
    if p and p["n"] >= 1300:
        add(p["h"], "PDH"); add(p["l"], "PDL"); add(p["c"], "PDC")
    td = D.get(d)
    if td and T - d * DAY >= 8 * 3_600_000:
        add(td["ah"], "AsiaH"); add(td["al"], "AsiaL")
    if td:
        add(td["o"], "DO")
    wk, pw = W.get(w), W.get(w - 7)
    if wk:
        add(wk["o"], "WO")
    if pw and pw["n"] >= 6:
        add(pw["h"], "PWH"); add(pw["l"], "PWL")
    return items


def decision(T, a, folds, D, W):
    """One decision time. Uses 1m bars with open < T only. Returns None (no data / no level near) or a record."""
    i = int(np.searchsorted(a[:, 0], T))          # first bar with open >= T
    if i < NLAST["1m"] or a[i - 1, 0] != T - MIN:
        return None
    px = float(a[i - 1, 4])
    zones = PP.merge(levels_at(T, D, W))
    for z in zones:
        z["name"] = z["label"]
    lad = PP.ladder(zones, px)
    cand = [z for z in (lad["at"], (lad["above"] or [None])[0], (lad["below"] or [None])[0]) if z and abs(px / z["price"] - 1) <= PP.P["near"]]
    if not cand:
        return None
    w = a[i - NLAST["1m"]:i]
    k1 = [[r[0], r[1], r[2], r[3], r[4], r[5], r[0] + 59_999, 0, 0, r[6]] for r in w.tolist()]
    tfk = {"1m": k1}
    for ms, f in folds.items():
        j = int(np.searchsorted(f[:, 0] + ms, T, side="right"))         # completed buckets: start + ms <= T
        rows = f[max(0, j - NLAST["other"]):j].tolist()
        s = (T - MIN) // ms * ms
        if s + ms > T:                                                   # forming bucket from the 1m bars so far
            i0 = int(np.searchsorted(a[:, 0], s))
            seg = a[i0:i]
            if len(seg):
                rows.append([s, seg[0, 1], seg[:, 2].max(), seg[:, 3].min(), seg[-1, 4], seg[:, 5].sum(), s + ms - 1, 0, 0, seg[:, 6].sum()])
                rows = rows[-NLAST["other"]:]
        tfk[NAMES[ms]] = rows
    g = PP.grid(tfk)
    s = PP.setup(g, lad, px, None)            # homeDir unavailable historically (DECISION, PRE_REG s.3)
    hi = g["hi"]
    return [T, session_of(T), None if not PP.fin(hi) else hi, None if not PP.fin(g["lean"]) else g["lean"], s["side"] if s else "",
            s["name"] if s else "", len(s["divs"]) if s else 0, round(px, 2)]


def _work(args):
    t0, t1 = args
    a = load_1m()
    folds = {ms: fold_arrays(a, ms) for ms in FOLD_MS}
    D, W = level_tables(a)
    out = []
    for T in range(t0, t1, STEP):
        r = decision(T, a, folds, D, W)
        if r:
            out.append(r)
    return out


def ms_of(day):
    return int(dt.datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def cmd_events(a):
    t0, t1 = ms_of(a.frm), min(ms_of(a.to) if a.to else DEV_END - 2 * 3_600_000, DEV_END - 2 * 3_600_000)
    chunks, t = [], t0
    while t < t1:
        chunks.append((t, min(t + 7 * DAY, t1)))
        t += 7 * DAY
    with mp.Pool(min(7, len(chunks))) as p:
        res = p.map(_work, chunks)
    rec = sorted((r for part in res for r in part), key=lambda r: r[0])
    Path(a.out).write_text(json.dumps({"cols": ["T", "session", "hi", "lean", "side", "level", "ndiv", "px"], "from": t0, "to": t1, "rows": rec}))
    print(f"decision times near a level: {len(rec)}; setups forming: {sum(1 for r in rec if r[4])}; wrote {a.out}")


def eligible(rows):
    """Cooldown 60 min per side, applied once to the setup ledger before any outcome is read."""
    last, out = {}, []
    for r in rows:
        if not r[4]:
            continue
        if r[0] - last.get(r[4], -10**18) < COOLDOWN:
            continue
        last[r[4]] = r[0]
        out.append(r)
    return out


def regime_by_day(a):
    D, _ = level_tables(a)
    ds = sorted(D)
    out = {}
    for d in ds:
        p = D.get(d - 30)
        if p:
            r = D[d]["c"] / p["c"] - 1
            out[d] = "bull" if r > 0.10 else "bear" if r < -0.10 else "range"
    return out


def cmd_counts(a):
    ev = json.loads(Path(a.out).read_text())
    rows = ev["rows"]
    sig = eligible(rows)
    pool = [r for r in rows if not r[4]]
    lean_pool = [r for r in pool if r[2] is not None and r[2] != 0]
    arr = load_1m()
    reg = regime_by_day(arr)
    days = {d for d in range(ev["from"] // DAY, ev["to"] // DAY + 1)}
    mix = {k: sum(1 for d in days if reg.get(d) == k) for k in ("bull", "bear", "range")}
    smix = {k: sum(1 for r in sig if reg.get(r[0] // DAY) == k) for k in ("bull", "bear", "range")}
    ses = {n: sum(1 for r in sig if r[1] == n) for n, *_ in SESSIONS}
    sd = {n: sum(1 for r in sig if r[1] == n and r[4] == "SHORT") for n, *_ in SESSIONS}
    print(json.dumps({"window_days": len(days), "decision_times_near_level": len(rows), "setups_raw": sum(1 for r in rows if r[4]),
                      "signals_after_cooldown": len(sig), "signal_days": len({r[0] // DAY for r in sig}), "by_session": ses, "short_by_session": sd,
                      "pool_near_not_forming": len(pool), "pool_lean_aligned": len(lean_pool), "regime_mix_days": mix, "regime_mix_signals": smix}, indent=1))
    # unconditional sd of the 30-minute close-to-close return over the window (price only, no rule outcome)
    c = arr[:, 4]
    t = arr[:, 0]
    m = (t >= ev["from"]) & (t < ev["to"])
    tw, cw = t[m], c[m]
    ok = tw[30:] - tw[:-30] == 30 * MIN
    r = (cw[30:][ok] / cw[:-30][ok] - 1) * 100
    print(f"sd of unconditional 30m return, percent: {r.std():.4f} (n={len(r)})")


# ---------------- stage 2 ----------------
def forward(a, T, h):
    """Gross return (fraction) entering at the open of the 1m bar at T + 1 min, exiting h minutes later; None if either bar is missing."""
    t = a[:, 0]
    i = int(np.searchsorted(t, T + MIN))
    j = int(np.searchsorted(t, T + MIN + h * MIN))
    if i >= len(t) or j >= len(t) or t[i] != T + MIN or t[j] != T + MIN + h * MIN:
        return None
    return a[j, 1] / a[i, 1] - 1


def boot_scope(sig, pool, lean, allp, B=4000, seed=7):
    """sig/lean: list of (day, sign, ret) ; pool/allp: list of (day, ret). Cost in fraction. Day-clustered bootstrap (resample UTC days)."""
    cost = COST_BP / 1e4
    days = sorted({x[0] for x in sig} | {x[0] for x in pool} | {x[0] for x in lean} | {x[0] for x in allp})
    ix = {d: i for i, d in enumerate(days)}
    nd = len(days)

    def agg(items, f):
        s, n = np.zeros(nd), np.zeros(nd)
        for it in items:
            k = ix[it[0]]
            s[k] += f(it)
            n[k] += 1
        return s, n
    sS, nS = agg(sig, lambda x: x[1] * x[2])          # signed gross sum
    shS, _ = agg(sig, lambda x: 1.0 if x[1] < 0 else 0.0)
    sL, nL = agg(lean, lambda x: x[1] * x[2])
    sP, nP = agg(pool, lambda x: x[1])
    sA, nA = agg(allp, lambda x: x[1])
    rng = np.random.default_rng(seed)

    def stat(w):
        ns = (w * nS).sum()
        if ns == 0:
            return None
        gross = (w * sS).sum() / ns
        p = (w * shS).sum() / ns                       # share of SHORT among the signals: the null copies the same side mix
        mu_p = (w * sP).sum() / max((w * nP).sum(), 1)
        mu_a = (w * sA).sum() / max((w * nA).sum(), 1)
        null_p = (1 - 2 * p) * mu_p                    # expected signed gross of a random side with that mix at a pool time
        null_a = (1 - 2 * p) * mu_a
        nl = (w * nL).sum()
        lean_g = (w * sL).sum() / nl if nl else np.nan
        return gross, null_p, null_a, lean_g
    full = stat(np.ones(nd))
    if full is None:
        return None
    bs = []
    for _ in range(B):
        w = rng.multinomial(nd, np.full(nd, 1 / nd)).astype(float)
        s = stat(w)
        if s:
            bs.append(s)
    bs = np.array(bs)

    def ci(x):
        return [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]
    g, n_p, n_a, l_g = full
    out = {"n": len(sig), "n_days": int(sum(1 for v in nS if v > 0)),
           "gross_bp": g * 1e4, "gross_ci_bp": [v * 1e4 for v in ci(bs[:, 0])],
           "net_bp": g * 1e4 - COST_BP, "net_ci_bp": [v * 1e4 - COST_BP for v in ci(bs[:, 0])],
           "net10_bp": g * 1e4 - FEE_BP,
           "null_near_not_forming": {"n_pool": len(pool), "gross_bp": n_p * 1e4, "net_bp": n_p * 1e4 - COST_BP},
           "diff_vs_null_bp": (g - n_p) * 1e4, "diff_ci_bp": [v * 1e4 for v in ci(bs[:, 0] - bs[:, 1])],
           "null_random_time": {"n_pool": len(allp), "gross_bp": n_a * 1e4, "net_bp": n_a * 1e4 - COST_BP},
           "diff_vs_random_time_bp": (g - n_a) * 1e4, "diff_vs_random_ci_bp": [v * 1e4 for v in ci(bs[:, 0] - bs[:, 2])],
           "lean_only": {"n_pool": len(lean), "gross_bp": None if np.isnan(l_g) else l_g * 1e4},
           "diff_vs_lean_only_bp": None if np.isnan(l_g) else (g - l_g) * 1e4,
           "diff_vs_lean_only_ci_bp": None if np.isnan(l_g) else [v * 1e4 for v in ci(bs[:, 0] - bs[:, 3])],
           "share_short": float(sum(1 for x in sig if x[1] < 0) / len(sig))}
    return out


def standard_card(res):
    """Fields the sim_desk results schema requires (sim_desk/DESIGN.md, build_artifact.REQUIRED), written from the cells above."""
    C = res["cells"]
    p = C["h30|ALL|ALL"]
    f = lambda x: "%.1f" % x  # noqa: E731
    ci = lambda v: "[%s, %s]" % (f(v[0]), f(v[1]))  # noqa: E731
    kp = [{"label": "signals (raw setups %d)" % res["setups_raw"], "value": str(p["n"])}]
    for h in HORIZONS:
        c = C["h%d|ALL|ALL" % h]
        kp.append({"label": "h%d fee-net mean, 14 bp" % h, "value": "%s bp %s" % (f(c["net_bp"]), ci(c["net_ci_bp"])), "tone": "bad"})
    kp.append({"label": "h30 signal minus near-level null", "value": "%s bp %s" % (f(p["diff_vs_null_bp"]), ci(p["diff_ci_bp"]))})
    rows = []
    for h in HORIZONS:
        for ses in ("ALL", "Asia", "Europe", "US", "Late"):
            c = C["h%d|%s|ALL" % (h, ses)]
            rows.append([str(h), ses, str(c["n"]), f(c["gross_bp"]), f(c["net_bp"]), ci(c["net_ci_bp"]), f(c["diff_vs_null_bp"]), ci(c["diff_ci_bp"])])
    return {
        "id": "live_aid-pulse-backtest", "kind": "backtest", "parity": None, "provenance": "run", "date": "2026-11-10",
        "family": "Live Aid pulse SETUP FORMING",
        "title": "Live Aid pulse SETUP FORMING (level within 0.15 %, 1h-4h lean away, low-timeframe divergence) vs a matched near-level null, fee-net 15/30/60 min, by session, DEV",
        "what": [
            {"name": "Rule", "value_plain": "pulse.js setup() ported line for line to python and parity-tested against the live JS through node; thresholds as shipped", "label": "OURS"},
            {"name": "Levels", "value_plain": "PDH, PDL, PDC, day open, week open, PWH, PWL, Asia high/low merged within 0.15 %; analyst, VAL/POC/VAH, MA-strip, VWAP levels and the Home direction are NOT_IN_DATA", "label": "OURS"},
            {"name": "Entry and exit", "value_plain": "5-minute decision times, entry at the open of the next 1m bar plus one bar, exit by time after 15, 30 or 60 min, 60-minute same-side cooldown", "label": "OURS"},
            {"name": "Costs", "value_plain": "Binance taker 0.05 % per side (fees.py) plus a 2 bp per side fill allowance = 14 bp round trip", "label": "SOURCED"},
        ],
        "how": "Walk BTCUSDT USD-M 1m klines (Binance perp tape, proxy for the page's feed) every 5 minutes, rebuild the page's candles per timeframe (1000 x 1m, 150 for the rest, forming candle included), run grid() and setup(); null = same near-level times with no setup and the signal's side mix; 95 % day-clustered bootstrap, 4000 draws.",
        "window": "DEV 2022-02-01 to 2024-06-30 (881 UTC days); VALIDATION and HOLDOUT never opened",
        "verdict": {"label": "FAIL: SETUP FORMING is a coin flip beyond being near a level; fee-net about -14 bp at every horizon", "tone": "bad"},
        "why": ["At 30 min n = %d, gross %s bp %s and fee-net %s bp %s; the flag minus the near-level null is %s bp %s." % (p["n"], f(p["gross_bp"]), ci(p["gross_ci_bp"]), f(p["net_bp"]), ci(p["net_ci_bp"]), f(p["diff_vs_null_bp"]), ci(p["diff_ci_bp"])),
                "No horizon, session or regime cell has a fee-net mean above zero; the best is about -12 bp against a 14 bp cost.",
                "The flag fires at 62 % of the 5-minute times near a level, so it is not selective; one secondary contrast (60 min, bear, vs lean-only) has a CI above zero and is a lead for a PRE_REG only."],
        "kpis": kp,
        "examples": [{"kind": "table", "title": "Horizon x session: n, gross and fee-net means and signal minus near-level null (bp)", "caption": "CI = 95 % day-clustered bootstrap; cost 14 bp",
                      "cols": ["horizon min", "session", "n", "gross bp", "net bp", "net CI", "vs null bp", "vs null CI"], "rows": rows}],
        "source_files": ["MyTradingSys/research/live_aid_pulse_2026-11/RESULT.md", "MyTradingSys/research/live_aid_pulse_2026-11/PRE_REG.md", "MyTradingSys/research/live_aid_pulse_2026-11/study.py",
                         "MyTradingSys/research/live_aid_pulse_2026-11/pulse_port.py"],
        "commit": "this card",
    }


def cmd_outcomes(a):
    pre = (HERE / "PRE_REG.md").read_text(encoding="utf-8")
    assert "FROZEN_UTC:" in pre, "PRE_REG.md is not frozen: no outcome may be read"
    ev = json.loads(Path(a.out).read_text())
    rows = ev["rows"]
    arr = load_1m()
    assert arr[-1, 0] < DEV_END
    sig = eligible(rows)
    sig_t = {r[0] for r in sig}
    pool = [r for r in rows if not r[4]]
    lean = [r for r in pool if r[2] is not None and r[2] != 0]
    allT = range(ev["from"], ev["to"], STEP)
    reg = regime_by_day(arr)
    res = {"study": "live_aid_pulse_2026-11", "card": "live-aid-pulse-backtest-1109", "split": "DEV only (2022-02-01 to 2024-06-30), VALIDATION and HOLDOUT never opened",
           "data": "BTCUSDT USD-M perpetual 1m klines, F:/MTS/data/tom_raw/klines (proxy for the page's feed)",
           "cost_bp_round_trip": COST_BP, "fee_bp": FEE_BP, "slippage_bp_round_trip": round(SLIP_BP_RT, 9), "decision_step_min": 5, "horizons_min": list(HORIZONS),
           "setups_raw": sum(1 for r in rows if r[4]), "signals": len(sig), "window_from": ev["from"], "window_to": ev["to"], "cells": {}}
    print("computing forward returns ...", flush=True)
    fw = {h: {} for h in HORIZONS}
    for T in allT:
        for h in HORIZONS:
            r = forward(arr, T, h)
            if r is not None:
                fw[h][T] = r
    res["dropped_missing_bars"] = {str(h): len(list(allT)) - len(fw[h]) for h in HORIZONS}
    sessions = [n for n, *_ in SESSIONS] + ["ALL"]
    regs = ["bull", "bear", "range", "ALL"]
    for h in HORIZONS:
        for ses in sessions:
            for rg in regs:
                if ses != "ALL" and rg != "ALL":
                    continue
                ok = lambda T, ses=ses, rg=rg: (ses == "ALL" or session_of(T) == ses) and (rg == "ALL" or reg.get(T // DAY) == rg)  # noqa: E731
                S = [(r[0] // DAY, 1 if r[4] == "LONG" else -1, fw[h][r[0]]) for r in sig if r[0] in fw[h] and ok(r[0])]
                Pl = [(r[0] // DAY, fw[h][r[0]]) for r in pool if r[0] in fw[h] and ok(r[0])]
                Ln = [(r[0] // DAY, 1 if r[2] > 0 else -1, fw[h][r[0]]) for r in lean if r[0] in fw[h] and ok(r[0])]
                Al = [(T // DAY, fw[h][T]) for T in allT if T in fw[h] and ok(T)]
                cell = boot_scope(S, Pl, Ln, Al) if S else None
                res["cells"][f"h{h}|{ses}|{rg}"] = cell or {"n": 0}
    res.update(standard_card(res))
    sys.path.insert(0, str(HERE.parent / "sim_desk" / "artifact"))
    import build_artifact as ba  # noqa: E402  the desk's fixed verdict banner rule (test_every_committed_result_has_banner)
    res["banner"] = ba.banner_of(res)
    Path(a.json).write_text(json.dumps(res, indent=1), newline="\n")
    print("wrote", a.json)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["events", "counts", "outcomes"])
    ap.add_argument("--from", dest="frm", default=EVAL_FROM_DEFAULT)
    ap.add_argument("--to", default=None)
    ap.add_argument("--out", default=str(HERE / "events.json"))
    ap.add_argument("--json", default=str(HERE.parent / "sim_desk" / "results" / "live_aid-pulse-backtest.json"))
    a = ap.parse_args()
    {"events": cmd_events, "counts": cmd_counts, "outcomes": cmd_outcomes}[a.stage](a)


if __name__ == "__main__":
    main()
