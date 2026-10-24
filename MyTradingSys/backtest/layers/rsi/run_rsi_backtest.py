"""
MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py

Backtest driver for the RSI-layer setups that were never tested on history:
  --family malkan_40_60   single-timeframe regime-gated 40/60 bounce/reject setups (MLK-S1/S2)
  --family malkan_mtf     5-star Grandfather(1M)/Father(1w)/Son(1d) composition (MLK-S1-MTF/S2-MTF)
  --family rsi_ma_events  RSI x RSI-MA touch (ma_support/ma_rejection) or cross events
Same method and verdict rule as fabio/run_backtest.py: BTCUSDT 1m history -> tf_resample, 70/30
chronological IS/OOS split, grid searched on IS only, chosen params frozen and applied to OOS, PBO
(bt.ref_pbo.ref_pbo_cscv) on IS daily-bucketed net returns over the whole grid.

Differences from the Fabio L1 driver (deliberate):
- Trades are scored NET with a bracket (default stop 1% / target 2%, the live indicator-layer bracket,
  MTS_USER_GUIDE.md s4) through bt.bt_engine.simulate_trade on the signal-timeframe bars (stop first if
  both are hit in one bar, gap through the stop fills at the open). Fees are sim.py's canonical schedule
  (B080, operator 2026-09-30): maker 0 / taker 5 bps; entry and stop/timeout pay taker, target pays maker.
  Fee constants are read from sim.py, never hardcoded here.
- Entry = close of the signal bar (the signal is only known at that close). One position at a time.
- Indicators/signals are computed ONCE over the full series (all causal) and the events split by bar index,
  so OOS has no RSI/regime cold start. IS trades are simulated on IS bars only (a trade still open at the
  IS boundary is dropped); OOS trades on the full series (open at series end: dropped).
- malkan_mtf: malkan_mtf.state_asof compares HTF bar OPEN times to the daily timestamp, which lets a daily
  bar see a weekly/monthly bar that has not closed yet. This driver passes each HTF bar's CLOSE time
  (tf_resample.bucket_end) instead, so the gate only ever uses closed higher-timeframe bars.
- The 40/60 levels live only in malkan_40_60; this driver calls it with its defaults and never names them.

Verdict: "insufficient n" if OOS n < 30; "edge" needs OOS mean net > 0 and PBO < 0.5; else "no edge".
Research code only; never touches execution/ or Tom core.
"""

import argparse
import inspect
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.bt.bt_data import load_klines, load_funding
from MyTradingSys.backtest.bt.bt_engine import simulate_trade
from MyTradingSys.backtest.bt.ref_pbo import ref_pbo_cscv
from MyTradingSys.backtest.layers.timeframe.tf_resample import resample, bucket_end
from MyTradingSys.backtest.layers.runner import forward_return_stats, baseline_return_stats
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma
from MyTradingSys.backtest.layers.rsi.rsi_ma_events import rsi_ma_events
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bull, malkan_setup_bear
from MyTradingSys.backtest.layers.rsi.malkan_mtf import malkan_mtf_bull, malkan_mtf_bear

REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
HORIZONS = (1, 5, 20)
STOP_PCT = 0.01
TARGET_PCT = 0.02
MAX_BARS = 100
MIN_OOS_N = 30
MAX_PBO = 0.5


def load_fees():
    """(taker, maker) from MyTradingSys/backtest/fees.py (single source of truth, B081)."""
    from MyTradingSys.backtest.fees import DERIBIT_TAKER, DERIBIT_MAKER
    return DERIBIT_TAKER, DERIBIT_MAKER


TAKER_FEE, MAKER_FEE = load_fees()


def load_registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def chronological_split(bars, is_frac=0.70):
    n_is = int(len(bars) * is_frac)
    return bars[:n_is], bars[n_is:], n_is


def _day(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).date()


def verdict(n_oos, mean_net_oos, pbo):
    if not n_oos or n_oos < MIN_OOS_N:
        return "insufficient n"
    if mean_net_oos is not None and mean_net_oos > 0 and pbo is not None and pbo < MAX_PBO:
        return "edge"
    return "no edge"


# ---------------------------------------------------------------- scoring

def trades_from_events(events, bars, stop_pct=STOP_PCT, target_pct=TARGET_PCT, max_bars=MAX_BARS,
                       taker=None, maker=None, funding=None):
    """Bracket-simulate events {"i","side"} (entry = close of bar i). One position at a time: an event
    at or before the previous trade's exit bar is skipped. Trades still open at the end of `bars` are
    dropped. Returns [{"i","t","side","net","exit_reason","bars_held"}], net = fraction of entry price."""
    taker = TAKER_FEE if taker is None else taker
    maker = MAKER_FEE if maker is None else maker
    funding = [] if funding is None else funding  # [] = explicit no-funding model; records = real funding (B103)
    trades, free_from = [], 0
    for e in sorted(events, key=lambda x: x["i"]):
        i, side = e["i"], e["side"]
        if i < free_from or i >= len(bars) - 1:
            continue
        px = bars[i]["c"]
        sgn = 1.0 if side == "long" else -1.0
        r = simulate_trade(side, px, bars[i]["t"], px * (1.0 - sgn * stop_pct), [(px * (1.0 + sgn * target_pct), 1.0)],
                           bars[i + 1:i + 1 + max_bars], taker_fee=taker, maker_fee=maker, max_bars=max_bars, funding=funding)
        if r["net_r"] is None:
            continue
        trades.append({"i": i, "t": bars[i]["t"], "side": side, "net": r["pnl_pct_net"] / 100.0,
                       "exit_reason": r["exit_reason"], "bars_held": r["bars_held"]})
        free_from = i + r["bars_held"]
    return trades


def trade_stats(trades):
    n = len(trades)
    if n == 0:
        return {"n": 0, "mean_net": None, "sum_net": None, "hit_rate": None, "exits": {}}
    nets = [t["net"] for t in trades]
    return {"n": n, "mean_net": sum(nets) / n, "sum_net": sum(nets),
            "hit_rate": sum(1 for x in nets if x > 0) / n,
            "exits": dict(Counter(t["exit_reason"] for t in trades))}


def daily_net_returns(trades, days):
    """Sum of trade net returns per UTC day (entry bar) on a COMMON day axis; 0.0 for no-trade days."""
    per = {}
    for t in trades:
        d = _day(t["t"])
        per[d] = per.get(d, 0.0) + t["net"]
    return [per.get(d, 0.0) for d in days]


def pbo_from_columns(cols, S=12):
    if len(cols) < 2:
        return None
    T = len(cols[0])
    S = min(S, (T // 2) * 2)
    if S < 4:
        return None
    M = [list(r) for r in zip(*cols)]
    try:
        return ref_pbo_cscv(M, S=S)[0]
    except Exception:
        return None


def _fwd(events, closes):
    if not events or not closes:
        return {h: {"n": 0, "mean_return": None, "hit_rate": None, "mae": None} for h in HORIZONS}
    return forward_return_stats([{"i": e["i"], "side": e["side"]} for e in events], closes, horizons=HORIZONS)


def grid_search_and_oos(events_fn, grid, bars, n_is, stop_pct=STOP_PCT, target_pct=TARGET_PCT,
                        max_bars=MAX_BARS, taker=None, maker=None, min_events=5, S=12, funding=None, dev_only=False):
    """events_fn(params) -> events over the FULL `bars` series. Chooses the IS-best variant by mean net
    per trade (>= min_events IS trades), reports IS and OOS stats and PBO over the IS grid.
    funding: records passed to every simulated trade. dev_only=True stops after the IS grid (no OOS bar is scored)."""
    kw = dict(stop_pct=stop_pct, target_pct=target_pct, max_bars=max_bars, taker=taker, maker=maker, funding=funding)
    if n_is < 50 or len(bars) - n_is < 10:
        return {"chosen": None, "reason": "too_few_bars", "pbo": None, "n_variants": len(grid),
                "verdict": "insufficient n"}
    bars_is = bars[:n_is]
    days = sorted({_day(b["t"]) for b in bars_is})
    results, cols = [], []
    for params in grid:
        try:
            ev = events_fn(params)
        except Exception as exc:
            results.append({"params": params, "error": str(exc), "n_is": 0, "mean_is": None})
            cols.append([0.0] * len(days))
            continue
        tr = trades_from_events([e for e in ev if e["i"] < n_is], bars_is, **kw)
        st = trade_stats(tr)
        results.append({"params": params, "n_is": st["n"], "mean_is": st["mean_net"], "is_stats": st,
                        "events_is": [e for e in ev if e["i"] < n_is]})
        cols.append(daily_net_returns(tr, days))
    pbo_val = pbo_from_columns(cols, S=S)
    summary = [{"params": r["params"], "n_is": r["n_is"], "mean_is": r["mean_is"]} for r in results]
    ok = [r for r in results if r["n_is"] >= min_events and r["mean_is"] is not None]
    if not ok:
        return {"chosen": None, "reason": "no_variant_with_min_events", "pbo": pbo_val,
                "n_variants": len(grid), "all_grid": summary, "verdict": "insufficient n"}
    best = max(ok, key=lambda r: r["mean_is"])
    if dev_only:
        return {"chosen": best["params"], "n_variants": len(grid), "is_stats": best["is_stats"], "oos_stats": None,
                "pbo": pbo_val, "all_grid": summary, "verdict": "dev_only (OOS not scored)"}
    ev_oos = [e for e in events_fn(best["params"]) if e["i"] >= n_is]
    tr_oos = trades_from_events(ev_oos, bars, **kw)
    oos = trade_stats(tr_oos)
    return {"chosen": best["params"], "n_variants": len(grid), "is_stats": best["is_stats"], "oos_stats": oos,
            "is_fwd_gross": _fwd(best["events_is"], [b["c"] for b in bars_is]),
            "oos_fwd_gross": _fwd(ev_oos, [b["c"] for b in bars]),
            "pbo": pbo_val, "all_grid": summary, "verdict": verdict(oos["n"], oos["mean_net"], pbo_val)}


# ---------------------------------------------------------------- signal families

def safe_rsi(closes, period):
    """rsi_core, but an all-None series (instead of ValueError) when the series is too short."""
    if len(closes) <= period:
        return [None] * len(closes)
    return rsi_core(closes, period)


def signals_to_events(signals, bars):
    idx = {b["t"]: i for i, b in enumerate(bars)}
    return [{"i": idx[s["t"]], "side": s["side"]} for s in sorted(signals, key=lambda s: s["t"])]


def malkan_events(bars, p):
    """malkan_40_60: bull (MLK-S1) + bear (MLK-S2) single-timeframe setups. p: period, tolerance, lookback."""
    rsi = safe_rsi([b["c"] for b in bars], p["period"])
    regime = malkan_regime(rsi, lookback=p["lookback"])
    sigs = malkan_setup_bull(bars, rsi, regime, tolerance=p["tolerance"]) + \
        malkan_setup_bear(bars, rsi, regime, tolerance=p["tolerance"])
    return signals_to_events(sigs, bars)


def htf_close_times(htf_bars, tf, registry):
    """Bar CLOSE times for higher-timeframe bars labelled by open time (no-look-ahead gate)."""
    return [bucket_end(b["t"], tf, registry) for b in htf_bars]


def malkan_mtf_events(bars, htf, registry, p):
    """5-star: entry-tf (1d) setup gated by closed 1w and 1M regimes. htf = {"1w": bars, "1M": bars}.
    p: period, tolerance, lookback (entry tf), htf_lookback."""
    rsi = safe_rsi([b["c"] for b in bars], p["period"])
    regime = malkan_regime(rsi, lookback=p["lookback"])
    gates = []
    for tf in ("1w", "1M"):
        hb = htf[tf]
        hr = malkan_regime(safe_rsi([b["c"] for b in hb], p["period"]), lookback=p["htf_lookback"])
        gates += [htf_close_times(hb, tf, registry), hr]
    sigs = malkan_mtf_bull(bars, rsi, regime, *gates, tolerance=p["tolerance"]) + \
        malkan_mtf_bear(bars, rsi, regime, *gates, tolerance=p["tolerance"])
    return signals_to_events(sigs, bars)


def rsi_ma_to_events(events, bars, mode):
    if mode not in ("touch", "cross"):
        raise ValueError("mode must be touch or cross")
    idx = {b["t"]: i for i, b in enumerate(bars)}
    out = []
    for e in events:
        side = None
        if mode == "touch":
            side = {"ma_support": "long", "ma_rejection": "short"}.get(e["event"])
        elif e["event"] == "cross":
            side = "long" if e.get("direction") == "up" else "short"
        if side:
            out.append({"i": idx[e["t"]], "side": side})
    return sorted(out, key=lambda e: e["i"])


def rsi_ma_family_events(bars, p):
    """rsi_ma_events: p: period, ma_length, tolerance (RSI points), mode touch|cross."""
    rsi = safe_rsi([b["c"] for b in bars], p["period"])
    ma = rsi_ma(rsi, "SMA", p["ma_length"])
    ev = rsi_ma_events(rsi, ma, [b["t"] for b in bars], p["tolerance"])
    return rsi_ma_to_events(ev, bars, p["mode"])


GRIDS = {
    "malkan_40_60": [{"period": pe, "tolerance": tol, "lookback": lb}
                     for pe in (10, 14, 21) for tol in (1.0, 2.0, 3.0) for lb in (10, 20, 40)],
    "malkan_mtf": [{"period": pe, "tolerance": tol, "lookback": 20, "htf_lookback": hl}
                   for pe in (9, 14) for tol in (1.0, 2.0, 3.0) for hl in (3, 6, 12)],
    "rsi_ma_events": [{"period": pe, "ma_length": ml, "tolerance": tol, "mode": m}
                      for pe in (9, 14) for ml in (9, 14) for tol in (0.5, 1.0, 2.0) for m in ("touch", "cross")],
}
DEFAULT_TFS = {"malkan_40_60": ["1h", "4h", "1d"], "malkan_mtf": ["1d"], "rsi_ma_events": ["15m", "1h", "4h"]}


def run_family(family, bars_1m, registry, tfs=None, grid=None, out_dir=None, **kw):
    """Returns {tf: {"n_bars","n_bars_is","n_bars_oos","baseline_oos","result": grid_search_and_oos(...)}}.
    kw: stop_pct, target_pct, max_bars, taker, maker, min_events, funding, dev_only."""
    if family not in GRIDS:
        raise ValueError("unknown family %r (expected one of %s)" % (family, ", ".join(GRIDS)))
    grid = grid or GRIDS[family]
    out = {}
    for tf in tfs or DEFAULT_TFS[family]:
        bars = resample(bars_1m, tf, registry)
        n_is = int(len(bars) * 0.70)
        if family == "malkan_40_60":
            fn = lambda p, b=bars: malkan_events(b, p)
        elif family == "rsi_ma_events":
            fn = lambda p, b=bars: rsi_ma_family_events(b, p)
        else:
            htf = {t: resample(bars_1m, t, registry) for t in ("1w", "1M")}
            fn = lambda p, b=bars, h=htf: malkan_mtf_events(b, h, registry, p)
        res = {"n_bars": len(bars), "n_bars_is": n_is, "n_bars_oos": len(bars) - n_is}
        if len(bars) - n_is > 0 and not kw.get("dev_only"):
            res["baseline_oos"] = baseline_return_stats([b["c"] for b in bars[n_is:]], horizons=HORIZONS)
        res["result"] = grid_search_and_oos(fn, grid, bars, n_is, **kw)
        out[tf] = res
        if out_dir is not None:
            with open(Path(out_dir) / ("%s_%s_result.json" % (family, tf)), "w", newline="\n", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)
    return out


def _fmt(x, pct=False, nd=3):
    if x is None:
        return "-"
    return ("%.*f%%" % (nd, x * 100)) if pct else ("%.*f" % (nd, x))


def render_report(summary):
    fam = summary["family"]
    lines = ["# %s backtest (IS/OOS 70/30)" % fam, "",
             "Fees: taker %.4f / maker %.4f (sim.py canonical); bracket stop %.2f%% / target %.2f%%. "
             "Verdict: OOS n >= %d, OOS mean net > 0, PBO < %.1f -> edge." % (
                 TAKER_FEE, MAKER_FEE, STOP_PCT * 100, TARGET_PCT * 100, MIN_OOS_N, MAX_PBO), "",
             "| TF | Variants | Chosen params | IS n / mean net | OOS n / mean net / hit | PBO | Verdict |",
             "|---|---|---|---|---|---|---|"]
    for tf, r in summary["tfs"].items():
        res = r["result"]
        i, o = res.get("is_stats") or {}, res.get("oos_stats") or {}
        lines.append("| %s | %s | %s | %s / %s | %s / %s / %s | %s | %s |" % (
            tf, res.get("n_variants"), json.dumps(res.get("chosen")) if res.get("chosen") else res.get("reason", "-"),
            i.get("n", "-"), _fmt(i.get("mean_net"), True), o.get("n", "-"), _fmt(o.get("mean_net"), True),
            _fmt(o.get("hit_rate"), True, 1), _fmt(res.get("pbo")), res.get("verdict")))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=sorted(GRIDS))
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--out", default=None, help="default Dumps/backtest/runs/rsi_<family>")
    ap.add_argument("--tfs", default=None, help="comma list; default per family (malkan_mtf: entry tf, gates fixed 1w+1M)")
    ap.add_argument("--stop-pct", type=float, default=STOP_PCT)
    ap.add_argument("--target-pct", type=float, default=TARGET_PCT)
    ap.add_argument("--max-bars", type=int, default=MAX_BARS)
    ap.add_argument("--min-events", type=int, default=5)
    ap.add_argument("--no-funding", action="store_true", help="explicit no-funding model (old behaviour)")
    ap.add_argument("--dev-only", action="store_true", help="score the IS (DEV) span only; OOS is not touched")
    args = ap.parse_args()

    out_dir = Path(args.out or REPO / "Dumps" / "backtest" / "runs" / ("rsi_" + args.family))
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = load_registry()
    bars_1m = load_klines(args.data_root)
    last_t = bars_1m[-1]["t"] if bars_1m else 0
    bars_1m += [b for b in load_klines(args.data_root2) if b["t"] > last_t]
    bars_1m.sort(key=lambda b: b["t"])
    print("Loaded %d 1m bars" % len(bars_1m), file=sys.stderr, flush=True)
    if not bars_1m:
        print("No data found under --data-root/--data-root2", file=sys.stderr)
        return 2

    funding = [] if args.no_funding else (load_funding(args.data_root2) or load_funding(args.data_root))
    print("Loaded %d funding records" % len(funding), file=sys.stderr, flush=True)
    tfs = args.tfs.split(",") if args.tfs else None
    res = run_family(args.family, bars_1m, registry, tfs=tfs, out_dir=out_dir, stop_pct=args.stop_pct,
                     target_pct=args.target_pct, max_bars=args.max_bars, min_events=args.min_events,
                     funding=funding, dev_only=args.dev_only)
    summary = {"family": args.family, "fees": {"taker": TAKER_FEE, "maker": MAKER_FEE},
               "n_funding": len(funding), "stop_pct": args.stop_pct, "target_pct": args.target_pct, "max_bars": args.max_bars, "tfs": res}
    with open(out_dir / "summary.json", "w", newline="\n", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, default=str)
    with open(out_dir / "REPORT.md", "w", newline="\n", encoding="utf-8") as f:
        f.write(render_report(summary))
    print("Done. Results in %s" % out_dir, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
