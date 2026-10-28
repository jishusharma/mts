"""
MyTradingSys/backtest/layers/run_t055.py   (staged as run_t055.py.new)

T055 backtest driver for candidates C1 (funding_cvd_fade), C2 (session_momentum) and
C3 (turn_of_candle). Modelled on layers/fabio/run_backtest.py: load_klines, tf_resample
(+ tbv merge), 70/30 chronological IS/OOS split, grid search on IS only, runner
.forward_return_stats and bt.ref_pbo.ref_pbo_cscv on daily-bucketed IS net returns.

Every trade is scored NET with trade_costs.net_return (FORMULAS.md section 13: 10 bps RT
fee + 2 bps slippage + funding). Entry = close of the event bar, exit = close of bar
i+h (C1 4/16/48 bars, C3 1/2/5 bars) or the close of the session-end bar (C2, 1440 min
session). The grid is searched over (params x horizon); each combination is one PBO
variant. Parameters are chosen on IS only and applied unchanged to OOS.

PASS criteria (T055 runbook step 4, all must hold on the IS-chosen params applied to OOS):
n_oos >= 30; mean net > 0; net Sharpe (bt_stats.sharpe of per-trade net returns, not
annualised) >= 0.3; PBO < 0.5; same sign of net edge in IS and OOS; C2/C3 additionally
positive mean net in >= 2 separate OOS calendar years. C1 pass is provisional (~12 months
of funding, single split). Alert-only research code; never touches execution or Tom core.

Layer modules are imported lazily, so tests inject stubs through `events_fn`.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("MTS_REPO") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.bt.bt_stats import sharpe
from MyTradingSys.backtest.bt.ref_pbo import ref_pbo_cscv
from MyTradingSys.backtest.layers.runner import forward_return_stats

REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
MD_DIR = REPO / "MyTradingSys" / "research" / "fast_track_2026-09-27"
DAY_MS = 86400000
SESSION_LEN_MIN = 1440

MIN_OOS_EVENTS = 30
MIN_SHARPE = 0.3
MAX_PBO = 0.5


# ---------------------------------------------------------------- candidate specs

def _c1_events(bars, funding, **p):
    from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import funding_cvd_fade_events
    return funding_cvd_fade_events(bars, funding, **p)


def _c2_events(bars, funding, **p):
    from MyTradingSys.backtest.layers.session.session_momentum import session_momentum_events
    return session_momentum_events(bars, **p)


def _c3_events(bars, funding, **p):
    from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import turn_of_candle_events
    return turn_of_candle_events(bars, **p)


def c1_grid():
    return [{"lookback": lb, "n": n, "hi": hi, "lo": lo, "use_divergence": ud}
            for lb in (60, 90, 180) for n in (20, 50)
            for hi, lo in ((0.90, 0.10), (0.95, 0.05), (0.99, 0.01)) for ud in (True, False)]


def c2_grid(bar_min=5):
    out = []
    for fm in (30, 60):
        for em in (fm, SESSION_LEN_MIN - 30):
            for ss in (0, "ny"):  # B102: "ny" = day_gates.ny_open_utc (DST-aware), was fixed 810
                for ma in (0.0, 0.001):
                    out.append({"bar_min": bar_min, "session_start_min": ss, "first_min": fm,
                                "entry_min": em, "min_abs": ma})
    return out


def c3_grid():
    return [{"lead_minutes": lm, "side": s} for lm in (1, 2) for s in ("long", "short")]


CANDIDATES = {
    "c1": {"name": "funding_cvd_fade", "tf": "15m", "bar_min": 15, "horizons": (4, 16, 48),
           "grid": c1_grid, "events_fn": _c1_events, "use_funding": True, "years_required": False,
           "roots": "raw"},
    "c2": {"name": "session_momentum", "tf": "5m", "bar_min": 5, "horizons": ("session",),
           "grid": c2_grid, "events_fn": _c2_events, "use_funding": True, "years_required": True,
           "roots": "both"},
    "c3": {"name": "turn_of_candle", "tf": "1m", "bar_min": 1, "horizons": (1, 2, 5),
           "grid": c3_grid, "events_fn": _c3_events, "use_funding": True, "years_required": True,
           "roots": "both"},
}


# ---------------------------------------------------------------- scoring

def chronological_split(bars, is_frac=0.70):
    n_is = int(len(bars) * is_frac)
    return bars[:n_is], bars[n_is:], n_is


def _cost_fn():
    from MyTradingSys.backtest.layers.positioning.trade_costs import net_return
    return net_return


def score_trades(events, bars, horizon, bar_ms, funding, net_return, fee_rt=0.0010, slip_rt=0.0002):
    """Entry at closes[i] (instant t_i + bar_ms), exit at closes[j]. Returns a list of
    {"i", "t", "side", "gross", "net"}. horizon: int bars, or "session" = session-end bar."""
    end_idx = None
    if horizon == "session":
        end_idx = {b["t"] + bar_ms: k for k, b in enumerate(bars)}
    trades = []
    for e in events:
        i, side = e["i"], e["side"]
        if horizon == "session":
            j = end_idx.get(e["session_start"] + SESSION_LEN_MIN * 60000)
            if j is None or j <= i:
                continue
        else:
            j = i + horizon
            if j >= len(bars):
                continue
        p_in, p_out = bars[i]["c"], bars[j]["c"]
        t_in, t_out = bars[i]["t"] + bar_ms, bars[j]["t"] + bar_ms
        net = net_return(side, p_in, p_out, t_in, t_out, funding or [], fee_rt, slip_rt)
        net_nf = net_return(side, p_in, p_out, t_in, t_out, [], fee_rt, slip_rt)
        funded = bool(funding) and t_in >= funding[0][0]  # funding history covers the whole hold
        gross = (1.0 if side == "long" else -1.0) * (p_out - p_in) / p_in
        trades.append({"i": i, "t": bars[i]["t"], "side": side, "gross": gross, "net": net,
                       "net_nofund": net_nf, "funded": funded})
    return trades


def summarize(trades):
    n = len(trades)
    if n == 0:
        return {"n": 0, "mean_gross": None, "mean_net": None, "hit_gross": None, "hit_net": None,
                "sharpe_net": None}
    nets = [t["net"] for t in trades]
    grs = [t["gross"] for t in trades]
    fund = [t for t in trades if t.get("funded")]
    nf = [t for t in trades if "funded" in t and not t["funded"]]
    return {"n": n, "mean_gross": sum(grs) / n, "mean_net": sum(nets) / n,
            "n_funded": len(fund),
            "mean_net_funded": (sum(t["net"] for t in fund) / len(fund)) if fund else None,
            "mean_net_nofund_funded": (sum(t["net_nofund"] for t in fund) / len(fund)) if fund else None,
            "n_unfunded": len(nf),
            "mean_net_unfunded": (sum(t["net"] for t in nf) / len(nf)) if nf else None,
            "hit_gross": sum(1 for g in grs if g > 0) / n, "hit_net": sum(1 for x in nets if x > 0) / n,
            "sharpe_net": sharpe(nets) if n >= 2 else None}


def yearly_net(trades):
    by = {}
    for t in trades:
        y = datetime.fromtimestamp(t["t"] / 1000, tz=timezone.utc).year
        by.setdefault(y, []).append(t["net"])
    return {y: {"n": len(v), "mean_net": sum(v) / len(v)} for y, v in sorted(by.items())}


def daily_matrix_column(trades, bars):
    """Mean net return per UTC day over the whole bar span, 0.0 on days without a trade."""
    if not bars:
        return []
    d0, d1 = bars[0]["t"] // DAY_MS, bars[-1]["t"] // DAY_MS
    per = {}
    for t in trades:
        per.setdefault(t["t"] // DAY_MS, []).append(t["net"])
    return [(sum(per[d]) / len(per[d])) if d in per else 0.0 for d in range(d0, d1 + 1)]


def compute_pbo(columns, max_s=16):
    if len(columns) < 2:
        return None
    T = len(columns[0])
    S = min(max_s, T)
    S -= S % 2
    if S < 4:
        return None
    M = [list(r) for r in zip(*columns)]
    try:
        return ref_pbo_cscv(M, S=S)[0]
    except Exception:
        return None


# ---------------------------------------------------------------- driver core

def run_candidate(cand, bars, funding, events_fn=None, grid=None, horizons=None, bar_ms=None,
                  net_return=None, is_frac=0.70, min_events=20, fee_rt=0.0010, slip_rt=0.0002,
                  pbo_s=16):
    """Grid search on IS only, apply the IS-best (params, horizon) to OOS, PBO on the IS grid.
    events_fn(bars, funding, **params) -> events; events_fn/grid/horizons/bar_ms/net_return
    default to the candidate spec and real modules, and are injectable for tests."""
    spec = CANDIDATES[cand]
    events_fn = events_fn or spec["events_fn"]
    grid = grid if grid is not None else spec["grid"]()
    horizons = tuple(horizons if horizons is not None else spec["horizons"])
    bar_ms = bar_ms or spec["bar_min"] * 60000
    net_return = net_return or _cost_fn()

    bars_is, bars_oos, n_is = chronological_split(bars, is_frac)
    variants, columns = [], []
    for params in grid:
        try:
            ev = events_fn(bars_is, funding, **params)
        except Exception as exc:
            variants.append({"params": params, "error": str(exc)})
            continue
        for h in horizons:
            tr = score_trades(ev, bars_is, h, bar_ms, funding, net_return, fee_rt, slip_rt)
            variants.append({"params": params, "horizon": h, "stats": summarize(tr)})
            columns.append(daily_matrix_column(tr, bars_is))

    result = {"candidate": cand, "layer": spec["name"], "n_bars": len(bars), "n_is_bars": n_is,
              "n_oos_bars": len(bars) - n_is, "n_variants": len(columns),
              "fee_rt": fee_rt, "slip_rt": slip_rt,
              "funding_included": bool(spec["use_funding"] and funding),
              "funding_start": funding[0][0] if funding else None,
              "grid": [{"params": v["params"], "horizon": v.get("horizon"),
                        "n": v.get("stats", {}).get("n"), "mean_net": v.get("stats", {}).get("mean_net"),
                        "error": v.get("error")} for v in variants]}

    qual = [v for v in variants if v.get("stats") and v["stats"]["n"] >= min_events
            and v["stats"]["mean_net"] is not None]
    result["pbo"] = compute_pbo(columns, pbo_s)
    if not qual:
        result.update({"chosen": None, "is": None, "oos": None, "criteria": {}, "verdict": "FAIL",
                       "reason": f"no IS variant with >= {min_events} events"})
        return result

    best = max(qual, key=lambda v: v["stats"]["mean_net"])
    ev_oos = events_fn(bars_oos, funding, **best["params"])
    tr_oos = score_trades(ev_oos, bars_oos, best["horizon"], bar_ms, funding, net_return, fee_rt, slip_rt)
    oos = summarize(tr_oos)
    is_stats = best["stats"]
    runner_gross = None
    if best["horizon"] != "session" and ev_oos:
        fr = forward_return_stats([{"i": e["i"], "side": e["side"]} for e in ev_oos],
                                  [b["c"] for b in bars_oos], horizons=(best["horizon"],))
        runner_gross = fr[best["horizon"]]["mean_return"]
    years = yearly_net(tr_oos)

    crit = {
        "oos_n>=30": oos["n"] >= MIN_OOS_EVENTS,
        "oos_mean_net>0": oos["mean_net"] is not None and oos["mean_net"] > 0,
        "oos_net_sharpe>=0.3": oos["sharpe_net"] is not None and oos["sharpe_net"] >= MIN_SHARPE,
        "pbo<0.5": result["pbo"] is not None and result["pbo"] < MAX_PBO,
        "same_sign_is_oos": (oos["mean_net"] is not None and is_stats["mean_net"] is not None
                             and is_stats["mean_net"] * oos["mean_net"] > 0),
    }
    if spec["years_required"]:
        crit[">=2_positive_oos_years"] = sum(1 for y in years.values() if y["mean_net"] > 0) >= 2
    result.update({"chosen": {"params": best["params"], "horizon": best["horizon"]},
                   "is": is_stats, "oos": oos, "oos_years": years, "runner_gross_oos": runner_gross,
                   "criteria": crit, "verdict": "PASS" if all(crit.values()) else "FAIL",
                   "provisional": cand == "c1"})
    return result


# ---------------------------------------------------------------- report

def _f(x, pct=True):
    if x is None:
        return "n/a"
    return f"{x * 100:.4f}%" if pct else f"{x:.4f}"


def write_markdown(result, path):
    r = result
    prov = " (provisional: ~12 months of funding, single 70/30 split)" if r.get("provisional") else ""
    lines = [f"# T055 backtest - {r['candidate'].upper()} ({r['layer']})", "",
             f"Verdict: **{r['verdict']}**{prov}", "",
             f"Bars {r['n_bars']} (IS {r['n_is_bars']} / OOS {r['n_oos_bars']}); variants {r['n_variants']}; "
             f"cost: fee {r['fee_rt']*1e4:.0f} bps RT + slip {r['slip_rt']*1e4:.0f} bps RT + funding "
             f"({'included' if r['funding_included'] else 'NOT included'}). "
             f"PBO (CSCV, IS daily net): {_f(r['pbo'], False)}", ""]
    if r.get("chosen") is None:
        lines += [f"No result: {r.get('reason')}", ""]
    else:
        lines += [f"IS-chosen: `{json.dumps(r['chosen'])}`", "",
                  "| split | n events | gross mean | net mean | hit (gross) | hit (net) | net Sharpe |",
                  "|---|---|---|---|---|---|---|"]
        for k in ("is", "oos"):
            s = r[k]
            lines.append(f"| {k.upper()} | {s['n']} | {_f(s['mean_gross'])} | {_f(s['mean_net'])} | "
                         f"{_f(s['hit_gross'], False)} | {_f(s['hit_net'], False)} | {_f(s['sharpe_net'], False)} |")
        lines += ["", f"Funding coverage (funding history from {r.get('funding_start')} ms; trades before it are "
                      "net of fees+slippage only, no funding): "
                      + "; ".join(f"{k.upper()}: {r[k].get('n_funded', 0)} funded / {r[k].get('n_unfunded', 0)} "
                                  f"fee-only trades, funded-trade net {_f(r[k].get('mean_net_funded'))} vs same trades "
                                  f"without funding {_f(r[k].get('mean_net_nofund_funded'))}, fee-only-trade net "
                                  f"{_f(r[k].get('mean_net_unfunded'))}" for k in ("is", "oos"))]
        yrs = ", ".join(f"{y}: n={v['n']} net={_f(v['mean_net'])}" for y, v in r["oos_years"].items())
        lines += ["", "OOS by calendar year: " + (yrs or "none"), "",
                  "## Criteria (runbook step 4)", "", "| criterion | result |", "|---|---|"]
        lines += [f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in r["criteria"].items()]
        lines += ["", "No parameter was tuned on OOS. On FAIL the candidate closes; on PASS register alert-only.", ""]
    top = sorted([g for g in r["grid"] if g.get("mean_net") is not None], key=lambda g: -g["mean_net"])[:10]
    lines += ["## Top IS grid points (by net mean)", "", "| params | horizon | n | net mean |", "|---|---|---|---|"]
    lines += [f"| `{json.dumps(g['params'])}` | {g['horizon']} | {g['n']} | {_f(g['mean_net'])} |" for g in top]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- data + CLI

def resample_with_tbv(bars_1m, tf, registry):
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample, bucket_start
    out = resample(bars_1m, tf, registry)
    tbv = {}
    for b in bars_1m:
        s = bucket_start(b["t"], tf, registry)
        tbv[s] = tbv.get(s, 0.0) + b.get("tbv", 0.0)
    for b in out:
        b["tbv"] = tbv.get(b["t"], 0.0)
    return out


def load_data(cand, root1, root2, tf):
    from MyTradingSys.backtest.bt.bt_data import load_klines, load_funding
    spec = CANDIDATES[cand]
    if spec["roots"] == "raw":
        bars_1m = load_klines(root2)
    else:
        bars_1m = load_klines(root1)
        last = bars_1m[-1]["t"] if bars_1m else 0
        bars_1m += [b for b in load_klines(root2) if b["t"] > last]
        bars_1m.sort(key=lambda b: b["t"])
    funding = load_funding(root2) if spec["use_funding"] else []
    tf_ms = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000}.get(tf, 60000)
    if tf == "1m":
        bars = bars_1m
    else:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        bars = resample_with_tbv(bars_1m, tf, registry)
    if funding:
        # Funding archive can end before the klines (monthly files publish after month end). A hold past the last funding
        # record raises in trade_costs.funding_paid, so keep only bars that close inside funding coverage.
        last_f = funding[-1][0]
        bars = [b for b in bars if b["t"] + tf_ms <= last_f]
    return bars, funding


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, choices=sorted(CANDIDATES))
    ap.add_argument("--out", default=None)
    ap.add_argument("--md-dir", default=str(MD_DIR))
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--tf", default=None, help="C1 only: 15m (default) or 1h; C2/C3 fixed")
    ap.add_argument("--min-events", type=int, default=20)
    ap.add_argument("--fee-rt", type=float, default=0.0010)
    ap.add_argument("--slip-rt", type=float, default=0.0002)
    ap.add_argument("--pbo-s", type=int, default=16)
    a = ap.parse_args(argv)

    spec = CANDIDATES[a.candidate]
    tf = a.tf if (a.candidate == "c1" and a.tf) else spec["tf"]
    if a.candidate == "c1" and tf not in ("15m", "1h"):
        ap.error("C1 supports --tf 15m or 1h")
    bar_ms = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000}[tf]
    out_dir = Path(a.out or REPO / "Dumps" / "backtest" / "runs" / f"t055_{a.candidate}")
    out_dir.mkdir(parents=True, exist_ok=True)

    bars, funding = load_data(a.candidate, a.data_root, a.data_root2, tf)
    print(f"Loaded {len(bars)} {tf} bars, {len(funding)} funding records", file=sys.stderr)
    grid = spec["grid"](spec["bar_min"]) if a.candidate == "c2" else spec["grid"]()
    res = run_candidate(a.candidate, bars, funding, grid=grid, bar_ms=bar_ms, min_events=a.min_events,
                        fee_rt=a.fee_rt, slip_rt=a.slip_rt, pbo_s=a.pbo_s)
    res["tf"] = tf
    with open(out_dir / "result.json", "w", newline="\n", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    write_markdown(res, Path(a.md_dir) / f"T055_BT_{a.candidate}.md")
    print(f"{a.candidate}: {res['verdict']}", file=sys.stderr)
    return res


if __name__ == "__main__":
    main()
