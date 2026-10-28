"""T09-F5: funding_cvd_fade re-tested on 1h bars (live runs it on 1h; the T055 verdict was on 15m).

DEV only: 1m klines cut to bar open < 2024-07-01 UTC (repo split, VALIDATION/HOLDOUT never loaded).
Same rule code as live (positioning.funding_cvd_fade.funding_cvd_fade_events), same cost model
(trade_costs.net_return: 10 bps RT fee + 2 bps slippage + funding; FORMULAS.md s13).

Labels:
  SOURCED  timeframe 1h = live (live_layers.py bars passed per tf; T09_live_parity.md F5).
  SOURCED  exit after 8 bars of the signal tf (T09_live_parity.md:75, auto_trader.py:443); stop 1% (same line),
           so 1R = 1% and net R = net return / 0.01.
  OURS     rule parameters = module defaults lookback 90, n 20, hi 0.95, lo 0.05, divergence on (the layer
           docstring says the thresholds are UNDEFINED in the source; live uses the defaults).
  OURS     the 36-point T055 grid x horizons (4, 8, 16, 48) bars = 144 variants, all logged as trials; the
           headline is the live configuration only, not the best variant.
Look-ahead: events use closed 1h bars, entry = close of the event bar (as run_t055.score_trades).
"""
import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers import run_t055 as T  # noqa: E402

DEV_END_MS = 1719792000000  # 2024-07-01 00:00 UTC (exclusive)
R_UNIT = 0.01  # live stop distance 1% (SOURCED T09_live_parity.md:75)
LIVE_HOLD_BARS = 8  # SOURCED
LIVE_PARAMS = {"lookback": 90, "n": 20, "hi": 0.95, "lo": 0.05, "use_divergence": True}  # OURS (defaults)
HORIZONS = (4, 8, 16, 48)
TF_MS = {"15m": 900000, "1h": 3600000}


def dev_slice(bars):
    return [b for b in bars if b["t"] < DEV_END_MS]


def to_tf(bars_1m, tf):
    registry = json.loads(T.REGISTRY_PATH.read_text(encoding="utf-8"))
    return T.resample_with_tbv(bars_1m, tf, registry)


def events_1h(bars, funding, **params):
    from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import funding_cvd_fade_events
    return funding_cvd_fade_events(bars, funding, **params)


def score(events, bars, horizon, funding, bar_ms=3600000):
    net_return = T._cost_fn()
    tr = T.score_trades(events, bars, horizon, bar_ms, funding, net_return)
    for t in tr:
        t["r"] = t["net"] / R_UNIT
    return tr


def mean_ci(xs):
    n = len(xs)
    if n == 0:
        return {"n": 0, "mean": None, "ci": [None, None]}
    m = sum(xs) / n
    if n < 2:
        return {"n": n, "mean": m, "ci": [None, None]}
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    half = 1.96 * sd / math.sqrt(n)
    return {"n": n, "mean": m, "ci": [m - half, m + half]}


def thin(trades, hold):
    """Greedy non-overlapping subset: next entry at i >= previous kept i + hold."""
    out, last = [], None
    for t in sorted(trades, key=lambda x: x["i"]):
        if last is None or t["i"] >= last + hold:
            out.append(t)
            last = t["i"]
    return out


def _dd_streak(rs):
    eq = peak = dd = 0.0
    streak = worst = 0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
        streak = streak + 1 if r < 0 else 0
        worst = max(worst, streak)
    return dd, worst


def run(data_root1, data_root2, tf="1h"):
    from MyTradingSys.backtest.bt.bt_data import load_klines, load_funding
    bars_1m = dev_slice(load_klines(data_root1))
    funding = load_funding(data_root2)
    bars = to_tf(bars_1m, tf)
    last_f = funding[-1][0]
    bars = [b for b in bars if b["t"] + TF_MS[tf] <= last_f]
    bar_ms = TF_MS[tf]
    out = {"tf": tf, "n_bars": len(bars), "first_bar": bars[0]["t"], "last_bar": bars[-1]["t"],
           "n_funding": len(funding)}

    ev = events_1h(bars, funding, **LIVE_PARAMS)
    tr = score(ev, bars, LIVE_HOLD_BARS, funding, bar_ms)
    out["live_events"] = len(ev)
    out["live"] = {"trades": tr, "stats": mean_ci([t["r"] for t in tr]),
                   "thinned": mean_ci([t["r"] for t in thin(tr, LIVE_HOLD_BARS)]),
                   "mean_gross_r": sum(t["gross"] for t in tr) / len(tr) / R_UNIT if tr else None}
    variants = []
    for params in T.c1_grid():
        e = events_1h(bars, funding, **params)
        for h in HORIZONS:
            t2 = score(e, bars, h, funding, bar_ms)
            s = mean_ci([t["r"] for t in t2])
            variants.append({"params": params, "horizon": h, "n": s["n"], "mean_net_r": s["mean"]})
    out["variants"] = variants
    return out


def verdict(stats):
    if stats["n"] < 30:
        return "NOT_ENOUGH_DATA"
    lo = stats["ci"][0]
    return "PASSED_DEV" if lo is not None and lo > 0 else "FAILED"


def sim_json(res, rid="t09-f5-funding-cvd-fade-1h"):
    tr = res["live"]["trades"]
    st = res["live"]["stats"]
    rs = [t["r"] for t in tr]
    dd, worst = _dd_streak(rs)
    day = lambda ms: datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    top = sorted([v for v in res["variants"] if v["n"] >= 30], key=lambda v: -v["mean_net_r"])[:5]
    th = res["live"]["thinned"]
    # 8-bar holds overlap, so the all-events CI is too narrow; the verdict uses the non-overlapping subset.
    status = verdict(th)
    return {
        "id": rid,
        "title": "funding_cvd_fade on 1h bars (live timeframe), DEV",
        "plain": "The funding-extreme plus volume-delta fade, run on the hourly bars the live runner uses, "
                 "held 8 hours, after fees, slippage and funding. DEV data only.",
        "status": status,
        "why": f"live configuration n {st['n']}, mean net R {st['mean']:.3f}, 95% CI "
               f"[{st['ci'][0]:.3f}, {st['ci'][1]:.3f}] (1R = 1% stop, overlapping holds); non-overlapping n {th['n']}, "
               f"mean {th['mean']:.3f}, CI [{th['ci'][0]:.3f}, {th['ci'][1]:.3f}] decides the status; 144 variants tried, headline is not the best one",
        "try_no": 144,
        "window": [day(res["first_bar"]), day(res["last_bar"])],
        "fees": {"gross_r": res["live"]["mean_gross_r"], "fee_r": 0.0012 / R_UNIT},
        "n_ideas": res["live_events"],
        "n_filled": st["n"],
        "mean_net_r": st["mean"],
        "ci": st["ci"],
        "win_rate": sum(1 for r in rs if r > 0) / len(rs) if rs else None,
        "max_dd_r": dd,
        "worst_streak": worst,
        "trades": [[day(t["t"]), t["side"], "funding_cvd_fade", round(t["r"], 4)] for t in tr],
        "variants": [{"label": f"lb{v['params']['lookback']} n{v['params']['n']} "
                               f"{v['params']['hi']}/{v['params']['lo']} div{int(v['params']['use_divergence'])} h{v['horizon']}",
                      "mean_net_r": v["mean_net_r"], "n": v["n"]} for v in top],
        "families": [{"name": "funding_cvd_fade", "n": st["n"], "mean_r": st["mean"]}],
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--tf", default="1h", choices=sorted(TF_MS))
    ap.add_argument("--out", default=str(REPO / "MyTradingSys" / "research" / "sim_desk" / "results"
                                         / "t09-f5-funding-cvd-fade-1h.json"))
    a = ap.parse_args(argv)
    res = run(a.data_root, a.data_root2, a.tf)
    sj = sim_json(res)
    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="\n", encoding="utf-8") as f:
        json.dump(sj, f, indent=1)
    summ = {k: v for k, v in res.items() if k not in ("variants", "live")}
    summ["live_stats"] = res["live"]["stats"]
    summ["live_thinned"] = res["live"]["thinned"]
    summ["mean_gross_r"] = res["live"]["mean_gross_r"]
    summ["status"] = sj["status"]
    summ["top_variants"] = sj["variants"]
    print(json.dumps(summ, indent=1))
    return res


if __name__ == "__main__":
    main()
