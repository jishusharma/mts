"""malkan_window_dev_2026-11: Malkan regular-divergence window arms, fee-net, DEV only (BTC+ETH, 1h/4h). See PRE_REG.md.

Arms are swing-to-swing bar counts inclusive of both swings (rsi_divergence convention):
  S3_10 = 3..10 (SOURCED Malkan), B11_12 / C13_18 / D19_50 = OURS bands that tile the operator's 12 / 18 / >18 window.
Passes: --pass count (event counts, no returns), --pass dev (fee-net stats). VALIDATION/HOLDOUT are never loaded.
"""
import argparse
import csv
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence  # noqa: E402

DAY = 86400000
H = 10                                  # exit H bars after the entry bar close (OURS, as the 2026-10-09 / 11-04 runs)
RSI_PERIOD = 14
COST = rk.TAKER_RT_PCT                  # 0.14 % round trip incl. slippage (SOURCED research_kit); fees.py taker alone = 2 x BINANCE_TAKER
assert abs(2 * fees.BINANCE_TAKER * 100 - 0.10) < 1e-9 and COST >= 2 * fees.BINANCE_TAKER * 100
TF_MS = {"1h": 3600000, "4h": 14400000}
ARMS = {"S3_10": (3, 10), "B11_12": (11, 12), "C13_18": (13, 18), "D19_50": (19, 50)}
KINDS = {"bullish": 1.0, "bearish": -1.0}
SYMBOLS = {"BTCUSDT": "F:/MTS/data/tom_raw/klines", "ETHUSDT": "F:/MTS/data/tom_raw/klines_eth"}
MIN_N, MIN_DAYS = 30, 20


def _ms(y, m):
    return int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000)


DEV_START_MS = _ms(2022, 1)
DEV_END_MS = _ms(2024, 7)
assert (DEV_START_MS, DEV_END_MS) == (
    int(datetime(splits.DEV_START.year, splits.DEV_START.month, splits.DEV_START.day, tzinfo=timezone.utc).timestamp() * 1000),
    int(datetime(splits.DEV_END.year, splits.DEV_END.month, splits.DEV_END.day, tzinfo=timezone.utc).timestamp() * 1000))


def arm_of(bars):
    for name, (lo, hi) in ARMS.items():
        if lo <= bars <= hi:
            return name
    return None


def load_1m(root, sym, end_ms=DEV_END_MS):
    """1m bars [DEV_START, end_ms) from monthly files only; end_ms past DEV end is refused, files at/after it are never opened."""
    if end_ms > DEV_END_MS:
        raise ValueError("loader end %d is past DEV end %d" % (end_ms, DEV_END_MS))
    out = []
    y, m = 2022, 1
    while _ms(y, m) < end_ms:
        p = Path(root) / ("%s-1m-%04d-%02d.csv" % (sym, y, m))
        if p.exists():
            with open(p, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    t = int(r["open_time"])
                    if DEV_START_MS <= t < end_ms:
                        out.append({"t": t, "o": float(r["open"]), "h": float(r["high"]), "l": float(r["low"]), "c": float(r["close"])})
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    out.sort(key=lambda b: b["t"])
    return out


def resample(bars_1m, tf):
    """Full UTC-aligned buckets only (a bucket with a missing minute is dropped, never filled)."""
    ms = TF_MS[tf]
    k = ms // 60000
    out, cur, key = [], [], None
    for b in bars_1m + [None]:
        bk = None if b is None else b["t"] // ms
        if cur and bk != key:
            if len(cur) == k:
                out.append({"t": key * ms, "o": cur[0]["o"], "h": max(x["h"] for x in cur), "l": min(x["l"] for x in cur), "c": cur[-1]["c"]})
            cur = []
        if b is not None:
            cur.append(b)
            key = bk
    return out


def divergences(closes, rsi, ts, kind):
    """All regular divergences with 3..50 bars between swings, each tagged with its arm."""
    evs = rsi_divergence(closes, rsi, ts, 3, 50, kind, 0.0)
    for e in evs:
        e["arm"] = arm_of(e["bars"])
    return evs


def trades_for(events, bars, kind, h=H):
    """Per event {day, gross}: enter at the close of the event bar, exit at the close h bars later; no exit bar = dropped."""
    sgn = KINDS[kind]
    out = []
    for e in events:
        i = e["i"]
        if i + h >= len(bars):
            continue
        px = bars[i]["c"]
        out.append({"day": int(bars[i]["t"] // DAY), "gross": sgn * (bars[i + h]["c"] - px) / px * 100.0})
    return out


def cell_stats(g, day):
    g = np.asarray(g, float)
    if len(g) == 0:
        return {"n": 0, "days": 0}
    net = g - COST
    m, se = rk.cluster_mean_se(net, day)
    t = rk.t_stat(m, se)
    return {"n": len(g), "days": len(set(day)), "gross": float(g.mean()), "net": m, "se": se, "t": t, "p": rk.norm_p_two(t),
            "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se, "hit_net": float((net > 0).mean())}


def collect():
    """(tf, kind, arm) -> (gross list, cluster-key list). Cluster key = symbol index x 1e6 + UTC day of entry."""
    cells = {}
    for si, (sym, root) in enumerate(SYMBOLS.items()):
        m1 = load_1m(root, sym)
        assert m1 and m1[-1]["t"] < DEV_END_MS
        for tf in TF_MS:
            bars = resample(m1, tf)
            closes = [b["c"] for b in bars]
            ts = [b["t"] for b in bars]
            rsi = rsi_core(closes, RSI_PERIOD)
            for kind in KINDS:
                evs = [e for e in divergences(closes, rsi, ts, kind) if e["arm"]]
                for arm in ARMS:
                    trs = trades_for([e for e in evs if e["arm"] == arm], bars, kind)
                    g, k = cells.setdefault((tf, kind, arm), ([], []))
                    g.extend(x["gross"] for x in trs)
                    k.extend(si * 1000000 + x["day"] for x in trs)
        print(sym, "done", file=sys.stderr, flush=True)
    return cells


def regime_mix_line_dev():
    """Context only (not a filter): weekly regime mix of the DEV window via the 11-04 gated study's context builder (BTC)."""
    p = REPO / "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py"
    spec = importlib.util.spec_from_file_location("rsi_gated_ctx", p)
    ctx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ctx)
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    bars = ctx.load_1m(DEV_END_MS)
    assert bars[-1]["t"] < DEV_END_MS
    daily, wk, mo = ctx.build_context(bars, registry)
    at = ctx.make_regime_at(daily, wk, mo)
    return rk.regime_mix_line([at(t) for t in ctx.week_starts(DEV_START_MS, DEV_END_MS)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", default="dev", choices=("count", "dev"))
    a = ap.parse_args()
    cells = collect()
    rows = []
    for (tf, kind, arm), (g, k) in sorted(cells.items()):
        row = {"tf": tf, "kind": kind, "arm": arm}
        row.update({"n": len(g), "days": len(set(k))} if a.pass_ == "count" else cell_stats(g, k))
        rows.append(row)
    if a.pass_ == "dev":
        fam = [r for r in rows if r["n"] > 0]
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=len(ARMS) * len(TF_MS) * len(KINDS))
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05)
        for r in fam:        # each OURS arm minus the SOURCED arm, same tf and kind, independent cluster keys (disjoint swing sets)
            if r["arm"] != "S3_10":
                g0, k0 = cells[(r["tf"], r["kind"], "S3_10")]
                g1, k1 = cells[(r["tf"], r["kind"], r["arm"])]
                d, se = rk.cluster_diff(g1, k1, g0, k0)
                r["diff_vs_S"], r["diff_se"] = d, se
    name = "counts.csv" if a.pass_ == "count" else "dev_cells.csv"
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("tf", "kind", "arm"), k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    line = regime_mix_line_dev()
    (HERE / ("regime_mix_%s.txt" % a.pass_)).write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
