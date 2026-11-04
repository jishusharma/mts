"""wt_extreme_cross_volmatch_2026-11: WT extreme-cross bounce vs an ATR(14)-decile-matched baseline, BTCUSDT + ETHUSDT USD-M futures. DEV only.

Card ms-wt-extreme-cross-volmatch-eth; see PRE_REG.md. Events, outcome, day type and HTF tag are reused by path from wt_extreme_cross_2026-11
(no retuning); the futures loader, spot-1d regime context and symbol-day cluster are reused from bb_range_retest_eth_pool_2026-11. New here:
Wilder ATR(14) % per bar, ATR deciles over the DEV bars of each symbol x TF, and a same-side 10-bar MFE baseline per decile.
"""
import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest import research_kit as rk  # noqa: E402


def _load(name, rel):
    sp = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


src = _load("wt_extreme_cross_src", "MyTradingSys/research/wt_extreme_cross_2026-11/study.py")
pool = _load("bb_retest_eth_pool_src", "MyTradingSys/research/bb_range_retest_eth_pool_2026-11/study.py")

DAY = src.DAY
K = src.K                                     # SOURCED source study (10 bars)
WARMUP = src.WARMUP
ATR_N = 14                                    # SOURCED Wilder ATR(14)
COST10 = 2 * fees.BINANCE_TAKER * 100.0       # SOURCED fees.py: Binance USD-M taker both legs, % round trip
COST14 = rk.TAKER_RT_PCT                      # SOURCED research_kit, the source study's cost
POWER_DAYS = 100                              # OURS: focal-cell day floor for a VOLATILITY-ONLY verdict (PRE_REG)
HOLM_ALPHA = 0.05                             # OURS (PRE_REG)
FOCAL = (("1m", "against", "all"), ("1m", "all", "prior_trend"), ("15m", "against", "all"), ("15m", "all", "prior_trend"))
SYMBOLS = pool.SYMBOLS
DEV_START_MS, DEV_END_MS = pool.DEV_START_MS, pool.DEV_END_MS
TFS = src.TFS
KEYS = ("sym", "tf", "side", "daytag", "htf")
load_sym_1m = pool.load_sym_1m               # raises on an end after DEV_END
cluster_key = pool.cluster_key


def atr_pct(h, l, c, n=ATR_N):
    """Wilder ATR(n) as % of the bar close; NaN before bar n-1 (seed = mean of the first n true ranges)."""
    h, l, c = np.asarray(h, float), np.asarray(l, float), np.asarray(c, float)
    pc = np.concatenate(([c[0]], c[:-1]))
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = h[0] - l[0]
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    a = tr[:n].mean()
    out[n - 1] = a
    for i in range(n, len(c)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out / c * 100.0


def decile_edges(x):
    """The 9 inner decile edges of x (NaN ignored)."""
    return np.nanquantile(np.asarray(x, float), np.arange(1, 10) / 10.0)


def decile_of(x, edges):
    """Decile 0..9 of each x against the inner edges (right-closed bins, as searchsorted left)."""
    return np.searchsorted(edges, np.asarray(x, float), side="left").astype(int)


def decile_baseline(mfe, dec):
    """Mean MFE per decile 0..9 (NaN for an empty decile)."""
    mfe, dec = np.asarray(mfe, float), np.asarray(dec, int)
    return np.array([mfe[dec == d].mean() if (dec == d).any() else np.nan for d in range(10)])


def bar_mfe(h, l, c, side, k=K):
    """Same-side k-bar MFE % from every bar close (NaN where fewer than k bars follow)."""
    from numpy.lib.stride_tricks import sliding_window_view as sw
    n = len(c)
    out = np.full(n, np.nan)
    if n <= k:
        return out
    hmax = sw(h[1:], k).max(axis=1)[:n - k]
    lmin = sw(l[1:], k).min(axis=1)[:n - k]
    px = c[:n - k]
    out[:n - k] = (hmax - px) / px * 100.0 if side > 0 else (px - lmin) / px * 100.0
    return out


def _p_one_sided(t):
    return 0.5 * math.erfc(t / math.sqrt(2.0)) if t is not None and not math.isnan(t) else 1.0


def holm(ps, alpha=HOLM_ALPHA):
    """Holm step-down: list of pass flags in input order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    ok = [False] * len(ps)
    for r, i in enumerate(order):
        if ps[i] > alpha / (len(ps) - r):
            break
        ok[i] = True
    return ok


def cell(rows):
    if not rows:
        return {"n": 0, "days": 0}
    cl = [r["cl"] for r in rows]
    out = {"n": len(rows), "days": len(set(cl)), "mfe_mean": float(np.mean([r["mfe"] for r in rows])),
           "base_unm": float(np.mean([r["b_unm"] for r in rows])), "base_match": float(np.mean([r["b_match"] for r in rows]))}
    for name, key in (("unm_excess", "x_unm"), ("match_excess", "x_match"), ("net10", "net10"), ("net14", "net14")):
        m, se = rk.cluster_mean_se(np.array([r[key] for r in rows]), cl)
        out[name], out[name + "_t"] = float(m), rk.t_stat(m, se)
    return out


def symbol_rows(sym, registry):
    """Event rows over all TFs of one symbol, plus its DEV regime-mix line."""
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    bars_1m = load_sym_1m(sym, DEV_END_MS)
    assert bars_1m[-1]["t"] < DEV_END_MS
    ctx_at = src.make_ctx_at(*pool.spot_context(sym, DEV_END_MS))
    types = src.day_types([b for b in bars_1m if b["t"] >= DEV_START_MS - DAY])
    rows = []
    for tf in TFS:
        bars = bars_1m if tf == "1m" else resample(bars_1m, tf, registry)
        h, l, c = src._arrays(bars)
        tclose = np.array([b["t"] for b in bars]) + src.TF_MS[tf]
        atr = atr_pct(h, l, c)
        dev = (tclose >= DEV_START_MS) & (tclose < DEV_END_MS) & (np.arange(len(c)) >= WARMUP) & ~np.isnan(atr)
        mfe_side = {s: bar_mfe(h, l, c, s) for s in (1, -1)}
        dev &= ~np.isnan(mfe_side[1])
        edges = decile_edges(atr[dev])
        dec_all = decile_of(atr, edges)
        base = {s: decile_baseline(mfe_side[s][dev], dec_all[dev]) for s in (1, -1)}
        unm = {s: float(mfe_side[s][dev].mean()) for s in (1, -1)}
        evs = [e for e in src.events_for(bars, tf) if DEV_START_MS <= e["t_close"] < DEV_END_MS and not np.isnan(atr[e["i"]])]
        src.dev_guard([bars[e["i"]] for e in evs] + [bars[min(e["i"] + K, len(bars) - 1)] for e in evs])
        for e in evs:
            o = src.outcome(bars, e["i"], e["side"])
            if o is None:
                continue
            s, d = e["side"], int(dec_all[e["i"]])
            day = int(e["t_close"] // DAY)
            rows.append({"sym": sym, "tf": tf, "side": "buy" if s > 0 else "sell", "cl": cluster_key(sym, day), "dec": d,
                         "mfe": o["mfe"], "b_unm": unm[s], "b_match": float(base[s][d]), "x_unm": o["mfe"] - unm[s],
                         "x_match": o["mfe"] - float(base[s][d]), "net10": o["ret"] - COST10, "net14": o["ret"] - COST14,
                         "prior": src.prior_day_type(types, e["t_close"]), "htf": src.htf_label(ctx_at(e["t_close"]), s)})
        print(sym, tf, len(evs), "events", file=sys.stderr, flush=True)
    mix = rk.regime_mix_line([ctx_at(t)["regime"] for t in src.week_starts(DEV_START_MS, DEV_END_MS)])
    return rows, mix


def cells(rows):
    out = []
    for sym in SYMBOLS + ("POOL",):
        rs = rows if sym == "POOL" else [r for r in rows if r["sym"] == sym]
        for tf in TFS:
            for side in ("buy", "sell"):
                rt = [r for r in rs if r["tf"] == tf and r["side"] == side]
                for daytag in ("all", "prior_range", "prior_trend"):
                    rd = rt if daytag == "all" else [r for r in rt if r["prior"] == daytag.split("_")[1]]
                    for htf in ("all", "with", "against"):
                        rh = rd if htf == "all" else [r for r in rd if r["htf"] == htf]
                        row = dict(zip(KEYS, (sym, tf, side, daytag, htf)))
                        row.update(cell(rh))
                        out.append(row)
    return out


def verdict(out):
    """PRE_REG rule over the 4 POOL buy focal cells."""
    foc = []
    for tf, htf, daytag in FOCAL:
        r = next(x for x in out if (x["sym"], x["tf"], x["side"], x["htf"], x["daytag"]) == ("POOL", tf, "buy", htf, daytag))
        foc.append(r)
    ps = [_p_one_sided(r.get("match_excess_t")) for r in foc]
    ok = holm(ps)
    if any(ok):
        v = "SURVIVES-MATCHING"
    elif all(r["days"] >= POWER_DAYS for r in foc):
        v = "VOLATILITY-ONLY"
    else:
        v = "UNDERPOWERED"
    return v, [{"tf": f[0], "htf": f[1], "daytag": f[2], "n": r["n"], "days": r["days"], "match_excess": r.get("match_excess"),
                "t": r.get("match_excess_t"), "p": p, "holm_pass": k} for f, r, p, k in zip(FOCAL, foc, ps, ok)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default=",".join(SYMBOLS))
    a = ap.parse_args(argv)
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    rows, mixes = [], {}
    for sym in a.symbols.split(","):
        r, mixes[sym] = symbol_rows(sym, registry)
        rows += r
    out = cells(rows)
    cols = sorted({k for r in out for k in r}, key=lambda k: (k not in KEYS, k))
    with open(HERE / "dev_cells.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    v, foc = verdict(out)
    summary = {"verdict": v, "focal": foc, "regime_mix": mixes}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
