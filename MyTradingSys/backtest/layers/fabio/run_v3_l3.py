"""Fabio v3 L3 historical backtest, pre-registered in research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md (TF8, row 1.10).

Usage: python -m MyTradingSys.backtest.layers.fabio.run_v3_l3 [--out DIR] [--days-limit N]
Phases (the order is the pre-registration's): 1 IS grid -> freeze selection file -> 2 OOS grid + variants -> 3 stress + stats.
Output (off C:): selection.json, dayR.json, results.json, tables.md in --out (default F:/MTS/data/fabio_v3_bt).
"""
import argparse
import datetime as dt
import itertools
import json
import math
import os
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import TimeoutError as FutTimeout
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path

from MyTradingSys.backtest.bt import bt_stats
from MyTradingSys.backtest.layers.fabio import orderflow_bars as ob
from MyTradingSys.backtest.layers.fabio.v3 import engine
from MyTradingSys.backtest.layers.fabio.v3.day_gates import MAX_MISSING, WINDOW_BARS, ny_open_utc

DATA = "F:/MTS/data/orderflow_1m"
IS_RANGE = (dt.date(2024, 12, 2), dt.date(2025, 12, 31))        # spec 8
OOS_RANGE = (dt.date(2026, 1, 1), dt.date(2026, 6, 25))         # spec 8; holdout 2026-06-26.. is never read here
N_DECLARED = 139                                                # spec 7.2 NY total
SLIP_SEL = 2.0                                                  # spec 8: selection at 2 bps
PRIOR_DAYS = 20                                                 # spec 6 day gate
TASK_TIMEOUT = 900                                              # B099: seconds one day-task may take before the run fails closed
SLOW_TASK = 120                                                 # B099: a day-task slower than this is logged by name
_OUT = None                                                     # output dir, set by main(); log() and the phase cache use it


# ------------------------------------------------------------------ grid (spec 7.2)
def grid():
    cells = {}
    Ns, ps, fs, modes, gs = (60, 120, 240), (0.05, 0.10), (0.003, 0.005), ("rest", "confirm"), ("off", 0.8)
    base = dict(z_hi=2.5, mgmt="event", m_c=15, N=120, p=0.10, g="off")
    for N, p, f, e, g in itertools.product(Ns, ps, fs, modes, gs):
        cells["A|N%d|p%g|f%g|%s|g%s" % (N, p, f, e, g)] = ("A", dict(base, N=N, p=p, f=f, entry_mode=e, g=g))
    for N, z, f, e in itertools.product(Ns, (2.0, 3.0), fs, modes):
        cells["B|N%d|z%g|f%g|%s" % (N, z, f, e)] = ("B", dict(base, N=N, z_hi=z, f=f, entry_mode=e))
    for m, f, e, g in itertools.product((5, 15), fs, modes, gs):
        cells["C|m%d|f%g|%s|g%s" % (m, f, e, g)] = ("C", dict(base, m_c=m, f=f, entry_mode=e, g=g))
    for N, p, f, e in itertools.product(Ns, ps, fs, modes):
        cells["D|N%d|p%g|f%g|%s" % (N, p, f, e)] = ("D", dict(base, N=N, p=p, f=f, entry_mode=e))
    return cells


def variants(model, cfg):
    out = {"dist_k1.0": dict(cfg, mgmt="dist", be_k=1.0), "dist_k2.0": dict(cfg, mgmt="dist", be_k=2.0)}
    if model == "B":
        out["trail"] = dict(cfg, target_mode="trail")
    return out


# ------------------------------------------------------------------ data
def build_windows(first, last):
    """-> list of dicts {date, bars} for valid NY windows (spec 1: thr_days > 0, <= 5 missing minutes)."""
    bars = ob.load_days(DATA, first - dt.timedelta(days=45), last)
    by_t = {b["t"]: b for b in bars}
    wins, skipped = [], {"closed": 0, "short": 0, "thr0": 0}
    d = first - dt.timedelta(days=45)
    while d <= last:
        o = ny_open_utc(d)
        if o is None:
            skipped["closed"] += d.weekday() < 5
            d += dt.timedelta(days=1)
            continue
        t0 = int(o.timestamp() * 1000)
        w = [by_t[t] for t in range(t0, t0 + WINDOW_BARS * 60000, 60000) if t in by_t]
        if WINDOW_BARS - len(w) > MAX_MISSING or not w:
            skipped["short"] += 1
        elif w[0]["thr_days"] == 0:
            skipped["thr0"] += 1
        else:
            hh, ll, rng = None, None, []
            for b in w:
                hh = b["h"] if hh is None else max(hh, b["h"])
                ll = b["l"] if ll is None else min(ll, b["l"])
                rng.append(hh - ll)
            wins.append({"date": d, "bars": w, "rng": rng})
        d += dt.timedelta(days=1)
    for k, w in enumerate(wins):
        w["prior"] = [x["rng"] for x in wins[max(0, k - PRIOR_DAYS):k]] if k >= PRIOR_DAYS else []
    return wins, skipped


# ------------------------------------------------------------------ one day, many cells
def _run_day(args):
    bars, prior, jobs = args          # jobs: list of (key, model, cfg, slip)
    out, t0 = {}, time.time()
    pr = (lambda el: [r[el] for r in prior if el < len(r)]) if len(prior) >= PRIOR_DAYS else (lambda el: [])
    for key, model, cfg, slip in jobs:
        c = dict(cfg, models=(model,), slip_bps=slip, prior_ranges=pr)
        try:
            r = engine.run(bars, c)
        except Exception as e:           # a crash is a result, not a skip (fail closed: 0 R, tallied)
            out[key] = (0.0, "error:%s" % type(e).__name__)
            continue
        tr = r["diagnostics"][model]["trade"]
        if tr is not None:
            out[key] = (float(tr["net_r"]), "trade")
        elif r["diagnostics"][model]["state"] == "IN_TRADE":
            out[key] = (0.0, "unmanaged")
        else:
            out[key] = (0.0, "none")
    out["__elapsed__"] = (time.time() - t0, "elapsed")
    return out


class RunFailed(RuntimeError):
    """B099: a phase stalled or a worker died. The run stops with a FAILED marker; no partial result is read."""


def log(msg):
    line = "%s %s" % (dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), msg)
    print(line, flush=True)
    if _OUT is not None:
        with open(_OUT / "run.log", "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")


def run_cells(pool, wins, cells, slip, name):
    """cells: {key: (model, cfg)} -> {key: {'r': [dayR per window], 'tag': {tag: n}}}.
    B099: per-day futures with a timeout, progress lines, and a per-phase disk cache so a re-run resumes."""
    cache = _OUT / ("phase_%s.json" % name) if _OUT is not None else None
    if cache is not None and cache.exists():
        got = json.loads(cache.read_text(encoding="utf-8"))
        if got.get("n") == len(wins) and set(got["res"]) == set(cells):
            log("phase %s: loaded from cache" % name)
            return got["res"]
    jobs = [(k, m, c, slip) for k, (m, c) in cells.items()]
    res = {k: {"r": [], "tag": {}} for k in cells}
    futs = [pool.submit(_run_day, (w["bars"], w["prior"], jobs)) for w in wins]
    log("phase %s: %d windows x %d cells submitted" % (name, len(wins), len(cells)))
    i = 0
    try:
        for i, (w, fu) in enumerate(zip(wins, futs)):
            day = fu.result(timeout=TASK_TIMEOUT)
            el = day.pop("__elapsed__")[0]
            if el > SLOW_TASK:
                log("phase %s: slow window %s took %.0fs" % (name, w["date"], el))
            for k, (r, tag) in day.items():
                res[k]["r"].append(r)
                res[k]["tag"][tag] = res[k]["tag"].get(tag, 0) + 1
            if (i + 1) % 20 == 0 or i + 1 == len(wins):
                log("phase %s: %d/%d windows" % (name, i + 1, len(wins)))
    except (FutTimeout, BrokenProcessPool) as e:
        for fu in futs:
            fu.cancel()
        raise RunFailed("phase %s stalled or a worker died at window %s (index %d): %s" % (
            name, wins[i]["date"], i, type(e).__name__))
    if cache is not None:
        cache.write_text(json.dumps({"n": len(wins), "res": res}), encoding="utf-8", newline="\n")
    return res


# ------------------------------------------------------------------ stats
def week_boot(dates, x, n_boot=2000, seed=12345):
    wk = {}
    for d, v in zip(dates, x):
        wk.setdefault(d.isocalendar()[:2], []).append(v)
    blocks, rng, n = list(wk.values()), random.Random(seed), len(x)
    means = []
    for _ in range(n_boot):
        s, c = 0.0, 0
        while c < n:
            b = rng.choice(blocks)
            s += sum(b)
            c += len(b)
        means.append(s / c)
    means.sort()
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def summ(x):
    n = len(x)
    tr = [v for v in x if v != 0.0]
    m = statistics.fmean(x) if x else float("nan")
    sd = statistics.pstdev(x) if n > 1 else float("nan")
    return {"days": n, "trade_days": len(tr), "mean": m, "sd": sd, "sum": sum(x),
            "win": (sum(1 for v in tr if v > 0) / len(tr)) if tr else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="F:/MTS/data/fabio_v3_bt")
    ap.add_argument("--days-limit", type=int, default=0, help="smoke test: first N IS windows and N OOS windows only")
    a = ap.parse_args()
    global _OUT
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    _OUT = out
    (out / "FAILED").unlink(missing_ok=True)
    wins, skipped = build_windows(IS_RANGE[0], OOS_RANGE[1])
    is_w = [w for w in wins if IS_RANGE[0] <= w["date"] <= IS_RANGE[1]]
    oos_w = [w for w in wins if OOS_RANGE[0] <= w["date"] <= OOS_RANGE[1]]
    if a.days_limit:
        is_w, oos_w = is_w[:a.days_limit], oos_w[:a.days_limit]
    log("IS windows %d, OOS windows %d, skipped %s" % (len(is_w), len(oos_w), skipped))
    cells = grid()
    assert len(cells) == 112, len(cells)
    res = {"n_declared": N_DECLARED, "skipped": skipped, "n_is": len(is_w), "n_oos": len(oos_w), "models": {}}
    pool = ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1))
    try:
        # phase 1: IS grid at 2 bps; selection frozen to disk BEFORE any OOS window is run
        is_res = run_cells(pool, is_w, cells, SLIP_SEL, "is_grid")
        chosen = {}
        for m in "ABCD":
            ks = [k for k in cells if cells[k][0] == m]
            best = max(ks, key=lambda k: (statistics.fmean(is_res[k]["r"]), -ks.index(k)))
            chosen[m] = best
        is_var = {m: {} for m in "ABCD"}
        for m, k in chosen.items():
            for vn, vc in variants(m, cells[k][1]).items():
                is_var[m][vn] = vc
        vres_is = {m: run_cells(pool, is_w, {vn: (m, vc) for vn, vc in is_var[m].items()}, SLIP_SEL, "is_var_" + m) for m in "ABCD"}
        sel = {"chosen": chosen, "is_mean": {k: statistics.fmean(is_res[k]["r"]) for k in cells},
               "variants_is_mean": {m: {vn: statistics.fmean(v["r"]) for vn, v in vres_is[m].items()} for m in "ABCD"}}
        frozen = out / "selection.json"
        if frozen.exists():            # B099 re-run: the first run's selection is the registered one; IS must reproduce it
            was = json.loads(frozen.read_text(encoding="utf-8"))["chosen"]
            if was != chosen:
                raise RunFailed("IS selection differs from the frozen selection.json: %s vs %s" % (chosen, was))
            log("selection reproduced the frozen selection.json: %s" % chosen)
        else:
            frozen.write_text(json.dumps(sel, indent=1), encoding="utf-8", newline="\n")
            log("selection frozen: %s" % chosen)
        # phase 2: OOS for the whole main grid (PBO matrix) and the variants
        oos_res = run_cells(pool, oos_w, cells, SLIP_SEL, "oos_grid")
        vres_oos = {m: run_cells(pool, oos_w, {vn: (m, vc) for vn, vc in is_var[m].items()}, SLIP_SEL, "oos_var_" + m) for m in "ABCD"}
        # phase 3: stress on the chosen cells (OOS)
        stress = {m: {s: run_cells(pool, oos_w, {chosen[m]: cells[chosen[m]]}, s, "stress_%s_%g" % (m, s))[chosen[m]] for s in (0.0, 5.0)}
                  for m in "ABCD"}
    except RunFailed as e:         # B099: fail closed, name the phase, leave no results file
        pool.shutdown(wait=False, cancel_futures=True)
        (out / "FAILED").write_text(str(e) + "\n", encoding="utf-8", newline="\n")
        log("FAILED: %s" % e)
        raise SystemExit(1)
    pool.shutdown()
    all_is = [statistics.fmean(is_res[k]["r"]) for k in cells] + \
             [statistics.fmean(v["r"]) for m in "ABCD" for v in vres_is[m].values()]
    sr_cells = [bt_stats.sharpe(is_res[k]["r"] + oos_res[k]["r"]) for k in cells if any(is_res[k]["r"] + oos_res[k]["r"])]
    var_sr = statistics.pvariance(sr_cells) if len(sr_cells) > 1 else 0.0
    oos_dates = [w["date"] for w in oos_w]
    daily = {}
    for m in "ABCD":
        k = chosen[m]
        x = oos_res[k]["r"]
        isr = is_res[k]["r"]
        lo, hi = week_boot(oos_dates, x)
        sd_is = statistics.pstdev(isr)
        need = math.ceil(((1.96 + 0.8416) * sd_is / 0.2) ** 2) if sd_is > 0 else None
        mat = [[is_res[c]["r"][i] for c in cells if cells[c][0] == m] for i in range(len(is_w))] + \
              [[oos_res[c]["r"][i] for c in cells if cells[c][0] == m] for i in range(len(oos_w))]
        try:
            pbo = bt_stats.pbo_cscv(mat, S=16)[0]
        except Exception as e:
            pbo = "error:%s" % e
        try:
            dsr = bt_stats.dsr(isr + x, N_DECLARED, var_sr) if any(isr + x) else None
        except Exception as e:
            dsr = "error:%s" % e
        mo = summ(x)
        passes = {"oos_mean_gt0": mo["mean"] > 0, "ci_lo_gt0": lo > 0, "dsr_ge_0.95": isinstance(dsr, float) and dsr >= 0.95,
                  "pbo_le_0.2": isinstance(pbo, float) and pbo <= 0.2, "n_met": need is not None and len(x) >= need}
        res["models"][m] = {"cell": k, "is": summ(isr), "oos_2bps": mo, "oos_ci95": [lo, hi], "n_needed": need,
                            "oos_0bps": summ(stress[m][0.0]["r"]), "oos_5bps": summ(stress[m][5.0]["r"]),
                            "dsr": dsr, "pbo": pbo, "tags_oos": oos_res[k]["tag"], "tags_is": is_res[k]["tag"],
                            "variants_oos": {vn: summ(v["r"]) for vn, v in vres_oos[m].items()},
                            "variants_is": {vn: summ(v["r"]) for vn, v in vres_is[m].items()},
                            "thresholds": passes, "verdict": "L3-PARTIAL-PASS" if all(passes.values()) else "L3-FAIL"}
        daily[m] = {"dates": [str(d) for d in oos_dates], "oos": x, "is": isr}
    res["var_sr_cells"] = var_sr
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline="\n")
    (out / "dayR.json").write_text(json.dumps(daily), encoding="utf-8", newline="\n")
    lines = ["| model | chosen cell | IS mean | OOS mean 2bps (0/5) | CI95 | trade days | DSR | PBO | need n | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
    for m, r in res["models"].items():
        lines.append("| %s | %s | %.4f | %.4f (%.4f/%.4f) | %.4f..%.4f | %d | %s | %s | %s | %s |" % (
            m, r["cell"], r["is"]["mean"], r["oos_2bps"]["mean"], r["oos_0bps"]["mean"], r["oos_5bps"]["mean"],
            r["oos_ci95"][0], r["oos_ci95"][1], r["oos_2bps"]["trade_days"], r["dsr"], r["pbo"], r["n_needed"], r["verdict"]))
    (out / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
