"""Test 2 runner (PRE_REG.md). python run.py  -> RESULT_raw.json + RESULT_tables.md
Variants: PRIMARY (RSI context, decides the verdict), SEC_WT (WaveTrend context), CONTROL (no context, descriptive)."""
import json
import os
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from fetch import COINS  # noqa: E402

DRAWS, BOOT, SEED = 1000, 2000, 1114
T_VAL = int(np.datetime64("2024-01-01", "ms").astype("int64"))
T_RECENT = int(np.datetime64("2025-07-01", "ms").astype("int64"))
BLOCK_MS = 10 * lib.DAY
PERIODS = ("DEV", "MID", "RECENT")  # VAL = MID + RECENT; RECENT is reported separately and is a subset of VAL
SPLITS = {"DEV": ("DEV",), "VAL": ("MID", "RECENT"), "RECENT": ("RECENT",), "ALL": PERIODS}


def period(t):
    return "DEV" if t < T_VAL else ("MID" if t < T_RECENT else "RECENT")


def candidates(co):
    """All decision bars usable as a placebo entry, per side: arrays for fast fixed-hold simulation."""
    out = {}
    lw = sliding_window_view(co.l, lib.HOLD_BARS + 1)
    hw = sliding_window_view(co.h, lib.HOLD_BARS + 1)
    ow = sliding_window_view(co.o, lib.HOLD_BARS + 1)
    for side, _brk, phs, _cx in lib.SIDES:
        rows = []
        for j in range(1, co.n - lib.HOLD_BARS - 2):
            if co.phase[j] in phs:
                s = lib.setup(co, j, side)
                if s is not None:
                    rows.append((j, *s))
        if not rows:
            out[side] = None
            continue
        a = np.array(rows)
        j, e, stop, risk = a[:, 0].astype(int), a[:, 1], a[:, 2], a[:, 3]
        ent = j + 1
        # window starting at the entry bar: offsets 0..60 (offset h = open of exit bar)
        L, Hh, O = lw[ent], hw[ent], ow[ent]
        hit = (L[:, :lib.HOLD_BARS] <= stop[:, None]) if side > 0 else (Hh[:, :lib.HOLD_BARS] >= stop[:, None])
        stop_off = np.where(hit.any(1), hit.argmax(1), 999)
        so = np.minimum(stop_off, lib.HOLD_BARS - 1)
        ob = O[np.arange(len(ent)), so]
        fill = np.where(stop_off == 0, stop, np.minimum(stop, ob) if side > 0 else np.maximum(stop, ob))
        stopR = side * (fill - e) / risk
        openR = (side * (O - e[:, None]) / risk[:, None]).astype(np.float32)
        out[side] = dict(t=co.t[ent], phase=co.phase[j].astype(int), stop_off=stop_off, stopR=stopR, openR=openR, fee=e / risk)
    return out


def build_pool(coins):
    pool = {}
    for co in coins:
        cd = candidates(co)
        for side, d in cd.items():
            if d is None:
                continue
            per = np.array([period(t) for t in d["t"]])
            for ph in np.unique(d["phase"]):
                for pe in PERIODS:
                    m = (d["phase"] == ph) & (per == pe)
                    if m.any():
                        pool.setdefault((side, int(ph), pe), []).append({k: v[m] for k, v in d.items()})
    return {k: {f: np.concatenate([x[f] for x in v]) for f in v[0]} for k, v in pool.items()}


def placebo_matrix(trades, pool, rng):
    """(DRAWS x ntrades) fee-net R at 12 and 6 bp: each real trade gets a random same-side, same-phase, same-period bar
    with the real trade's planned hold and the same stop rule."""
    n = len(trades)
    m12, m6 = np.full((DRAWS, n), np.nan), np.full((DRAWS, n), np.nan)
    keys = {}
    for i, r in enumerate(trades):
        keys.setdefault((r["side"], r["phase"], period(r["t"])), []).append(i)
    for key, idx in keys.items():
        p = pool.get(key)
        if p is None:
            continue
        idx = np.array(idx)
        h = np.array([trades[i]["planned"] for i in idx])
        c = rng.integers(0, len(p["t"]), size=(DRAWS, len(idx)))
        stopped = p["stop_off"][c] < h[None, :]
        gross = np.where(stopped, p["stopR"][c], p["openR"][c, h[None, :]])
        fee = p["fee"][c]
        m12[:, idx] = gross - 12e-4 * fee
        m6[:, idx] = gross - 6e-4 * fee
    return m12, m6


def boot_ci(t, x, rng):
    blk = (t // BLOCK_MS).astype(int)
    ub, inv = np.unique(blk, return_inverse=True)
    if len(ub) < 2:
        return (np.nan, np.nan)
    sums = np.bincount(inv, weights=x)
    cnts = np.bincount(inv).astype(float)
    s = rng.integers(0, len(ub), size=(BOOT, len(ub)))
    m = sums[s].sum(1) / cnts[s].sum(1)
    return (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)))


def cell(tr, idx, m12, m6, rng):
    n = len(idx)
    if n == 0:
        return dict(n=0)
    g = np.array([tr[i]["gross_R"] for i in idx])
    n12 = np.array([lib.net(tr[i], 12) for i in idx])
    n6 = np.array([lib.net(tr[i], 6) for i in idx])
    t = np.array([tr[i]["t"] for i in idx])
    ci = boot_ci(t, n12, rng)
    pm = m12[:, idx].mean(1)
    pm6 = m6[:, idx].mean(1)
    ok = ~np.isnan(pm)
    return dict(n=n, win=float((n12 > 0).mean()), gross=float(g.mean()), net12=float(n12.mean()), net6=float(n6.mean()),
                ci_lo=ci[0], ci_hi=ci[1],
                pl_pct=float((pm[ok] < n12.mean()).mean() * 100) if ok.any() else None,
                pl_lo=float(np.percentile(pm[ok], 2.5)) if ok.any() else None, pl_hi=float(np.percentile(pm[ok], 97.5)) if ok.any() else None,
                pl6_pct=float((pm6[ok] < n6.mean()).mean() * 100) if ok.any() else None)


def verdict(c_val, c_dev):
    if c_val.get("n", 0) < 30:
        return f"UNDERPOWERED (VAL n={c_val.get('n', 0)} < 30), no claim"
    ok = c_val["net12"] > 0 and c_val["ci_lo"] > 0 and (c_val["pl_pct"] or 0) >= 97.5 and c_dev.get("n", 0) > 0 and c_dev["net12"] > 0
    why = (f"VAL net12 mean R {c_val['net12']:+.3f} (CI {c_val['ci_lo']:+.3f}..{c_val['ci_hi']:+.3f}), placebo pct {c_val['pl_pct']:.1f}, "
           f"DEV net12 {c_dev.get('net12', float('nan')):+.3f} (n={c_dev.get('n', 0)})")
    return ("PASS: " if ok else "KILL: ") + why


def fmt(c):
    if not c.get("n"):
        return "| 0 | | | | | | |"
    pl = f"{c['pl_pct']:.0f} [{c['pl_lo']:+.2f},{c['pl_hi']:+.2f}]" if c["pl_pct"] is not None else "n/a"
    return (f"| {c['n']} | {100 * c['win']:.0f}% | {c['gross']:+.3f} | {c['net12']:+.3f} | [{c['ci_lo']:+.3f},{c['ci_hi']:+.3f}] "
            f"| {c['net6']:+.3f} | {pl} |")


def run_variant(name, osc, ctx, pool, coins, rng):
    tr = []
    for co in coins:
        tr += lib.real_trades(co, ctx)
    tr.sort(key=lambda r: r["t"])
    per = np.array([period(r["t"]) for r in tr]) if tr else np.array([])
    m12, m6 = placebo_matrix(tr, pool, rng)
    side = np.array([r["side"] for r in tr])
    phase = np.array([r["phase"] for r in tr])
    coin = np.array([r["coin"] for r in tr])
    res = dict(variant=name, ntrades=len(tr), cells={}, coins={}, notes={})

    def sel(sd=None, ph=None, sp="ALL", drop=None):
        m = np.isin(per, SPLITS[sp])
        if sd is not None:
            m &= side == sd
        if ph is not None:
            m &= phase == ph
        if drop is not None:
            m &= coin != drop
        return np.where(m)[0]

    for sdn, sd in (("both", None), ("long", 1), ("short", -1)):
        for phn, ph in [("all", None)] + [(lib.PHASE_NAME[p], p) for p in ((1, 2) if sd == 1 else (3, 4) if sd == -1 else (1, 2, 3, 4))]:
            for sp in SPLITS:
                res["cells"][f"{sdn}|{phn}|{sp}"] = cell(tr, sel(sd, ph, sp), m12, m6, rng)
    # per-coin contribution (VAL, both sides) and top-coin removal
    for cn in COINS:
        i = sel(None, None, "VAL")
        i = i[coin[i] == cn]
        x = np.array([lib.net(tr[k], 12) for k in i])
        res["coins"][cn] = dict(n=int(len(i)), sum_net12=float(x.sum()) if len(x) else 0.0, mean_net12=float(x.mean()) if len(x) else None)
    top = max(res["coins"], key=lambda k: res["coins"][k]["sum_net12"])
    res["notes"]["top_coin_val"] = top
    for sdn, sd in (("both", None), ("long", 1), ("short", -1)):
        res["cells"][f"{sdn}|all|VAL_minus_top"] = cell(tr, sel(sd, None, "VAL", top), m12, m6, rng)
        res["notes"][f"verdict_{sdn}"] = verdict(res["cells"][f"{sdn}|all|VAL"], res["cells"][f"{sdn}|all|DEV"])
        vm = res["cells"][f"{sdn}|all|VAL_minus_top"]
        res["notes"][f"top_removed_{sdn}"] = (f"VAL minus {top}: n={vm.get('n', 0)} net12 {vm.get('net12', float('nan')):+.3f} "
                                              f"CI [{vm.get('ci_lo', float('nan')):+.3f},{vm.get('ci_hi', float('nan')):+.3f}]")
    return res


def tables(res):
    L = [f"## Variant {res['variant']}  (trades: {res['ntrades']})", ""]
    for sdn in ("both", "long", "short"):
        L += [f"### Side: {sdn}", "", "| phase | split | n | win | gross R | net R 12bp | CI 95% (10d block) | net R 6bp | placebo pct [2.5,97.5 band of mean R] |", "|---|---|---|---|---|---|---|---|---|"]
        for k, c in res["cells"].items():
            s, ph, sp = k.split("|")
            if s == sdn:
                L.append(f"| {ph} | {sp} " + fmt(c))
        L.append("")
    L += ["### Per-coin contribution (VAL, both sides, net 12bp R)", "", "| coin | n | sum R | mean R |", "|---|---|---|---|"]
    for cn, d in sorted(res["coins"].items(), key=lambda x: -x[1]["sum_net12"]):
        L.append(f"| {cn} | {d['n']} | {d['sum_net12']:+.2f} | {'' if d['mean_net12'] is None else f'{d['mean_net12']:+.3f}'} |")
    L += ["", "### Verdicts and top-coin removal", ""]
    for k, v in res["notes"].items():
        L.append(f"- {k}: {v}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    out = {}
    md = ["# Test 2 result tables (generated by run.py; see RESULT.md for the verdict)", ""]
    for name, osc, ctx in (("PRIMARY", "rsi", "on"), ("SEC_WT", "wt", "on"), ("CONTROL", "rsi", "off")):
        coins = [lib.Coin(c, osc) for c in COINS]
        pool = build_pool(coins)
        rng = np.random.default_rng(SEED)
        r = run_variant(name, osc, ctx, pool, coins, rng)
        out[name] = r
        md.append(tables(r))
        print(name, r["ntrades"], r["notes"].get("verdict_both"), flush=True)
    json.dump(out, open(os.path.join(HERE, "RESULT_raw.json"), "w"), indent=1)
    open(os.path.join(HERE, "RESULT_tables.md"), "w").write("\n".join(md))
