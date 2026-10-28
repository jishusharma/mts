"""
MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py  (T089 + T091, items/T088_all_timeframe_module.md)

Regular RSI/price divergence measured on EVERY timeframe in layers/timeframe/registry.json over the
BTCUSDT 1m history (2022-01 .. latest on disk), resampled with tf_resample. Backtest only, no live gate.

Two event columns per timeframe:
- "malkan"   rsi_divergence.py with the sourced window (params/malkan_divergence_default.json: 3-10 bars,
             consecutive swing points, close to close, decimals count).
- "operator" T091, operator idea, NO-SOURCE: long-range divergence 11-60 bars between a swing point A and a
             later same-kind swing point B, NON-adjacent (at least one same-kind swing point between them),
             every swing point between them smaller than A ("highs 14 bars apart with smaller swings
             between", live read R2 2026-10-09). Malkan rejects this range in his own words
             (extract_Wvq1TZh8aF0.md:13, extract_cQ-y1oULkBw.md:15). 11 and 60 come from the T091 item text,
             not from a trader. Measured only; never wired live without a source.

Outcome: FORMULAS.md s7 forward return from the event bar's close (event = bar after B closes, causal),
side long for bullish / short for bearish, at horizons HORIZONS (bars of that timeframe). Net = gross minus
one round trip of taker fee (fees.py DERIBIT_TAKER, entry and exit both taker: the conservative case).
Baseline = the same-side forward return averaged over every bar of that timeframe (drift control).

Verdict per (timeframe, column, kind) at PRIMARY_H:
  "insufficient n"  fewer than MIN_EVENTS (300, operator rule in the T089 item) events with data at PRIMARY_H
  "edge candidate"  net mean > 0, t-stat of net >= T_MIN, gross mean > same-side baseline, and net mean > 0
                    in at least half of the calendar years that hold >= 30 events
  "no edge"         otherwise
PRIMARY_H = 10 bars and T_MIN = 2.0 are engineering choices (NO-SOURCE), fixed before the run, not tuned.
Overlapping horizons on dense timeframes make the t-stat optimistic; a candidate is a lead, not a result.

Splits: by calendar year (UTC), and by two 12-hour UTC halves (00-12, 12-24) for timeframes shorter than
12h (B154 names two 12-hour sessions but no boundary; 00/12 UTC is a placeholder, NO-SOURCE). B154's regime
split does not exist yet in code, so it is not here.
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence, _pivots

HORIZONS = (1, 5, 10, 20)
PRIMARY_H = 10
MIN_EVENTS = 300
T_MIN = 2.0
MIN_YEAR_EVENTS = 30
OPERATOR_MIN_BARS = 11
OPERATOR_MAX_BARS = 60
RSI_PERIOD = 14

PARAMS_PATH = Path(__file__).resolve().parent / "params" / "malkan_divergence_default.json"
REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"


def load_taker():
    from MyTradingSys.backtest.fees import DERIBIT_TAKER
    return DERIBIT_TAKER


# ---------------------------------------------------------------- detector (T091)

def long_range_divergence(close, rsi, ts, min_bars, max_bars, kind="bullish"):
    """Non-adjacent long-range divergence. For each swing point B take the MOST RECENT earlier same-kind
    swing point A with min_bars <= B - A + 1 <= max_bars such that: B is more extreme than A (bullish:
    close lower; bearish: close higher), RSI disagrees (bullish: rsi[B] > rsi[A]; bearish: rsi[B] < rsi[A]),
    at least one same-kind swing point lies strictly between them, and every such in-between swing point is
    less extreme than A. One event per B at most, stamped ts[B+1] (swing known one bar later)."""
    if kind not in ("bullish", "bearish"):
        raise ValueError("kind must be 'bullish' or 'bearish'")
    if not (len(close) == len(rsi) == len(ts)):
        raise ValueError("close, rsi and ts must have the same length")
    if min_bars < 3 or max_bars < min_bars:
        raise ValueError("need 3 <= min_bars <= max_bars")
    ext = (lambda x: -x) if kind == "bullish" else (lambda x: x)   # larger = more extreme
    rsi_ok = (lambda ra, rb: rb > ra) if kind == "bullish" else (lambda ra, rb: rb < ra)
    piv = _pivots(close, rsi, "low" if kind == "bullish" else "high")
    events = []
    for k in range(1, len(piv)):
        b = piv[k]
        eb = ext(close[b])
        max_between = None
        for j in range(k - 1, -1, -1):
            a = piv[j]
            bars = b - a + 1
            if bars > max_bars:
                break
            ea = ext(close[a])
            n_between = k - j - 1
            if (bars >= min_bars and n_between >= 1 and eb > ea and max_between < ea
                    and rsi_ok(rsi[a], rsi[b])):
                events.append({
                    "t": ts[b + 1], "i": b + 1, "event": kind + "_divergence_long",
                    "a_i": a, "b_i": b, "a_t": ts[a], "b_t": ts[b], "bars": bars, "n_between": n_between,
                    "close_a": close[a], "close_b": close[b], "rsi_a": rsi[a], "rsi_b": rsi[b],
                })
                break
            max_between = ea if max_between is None else max(max_between, ea)
    return events


# ---------------------------------------------------------------- scoring

def forward_returns(i, sgn, closes, horizons=HORIZONS):
    """FORMULAS s7: {h: sgn*(c[i+h]-c[i])/c[i]} for horizons with data (missing h = no entry)."""
    out = {}
    for h in horizons:
        if i + h < len(closes):
            out[h] = sgn * (closes[i + h] - closes[i]) / closes[i]
    return out


def baseline(closes, horizons=HORIZONS):
    """Mean long forward return over every bar with data at h. Short baseline = minus this."""
    out = {}
    for h in horizons:
        n = len(closes) - h
        out[h] = (sum((closes[i + h] - closes[i]) / closes[i] for i in range(n)) / n) if n > 0 else None
    return out


def _mean_t(xs):
    n = len(xs)
    if n == 0:
        return None, None
    m = sum(xs) / n
    if n < 2:
        return m, None
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, (m / math.sqrt(var / n) if var > 0 else None)


def _year(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).year


def _half(t_ms):
    return "00-12" if datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).hour < 12 else "12-24"


def score(events, closes, sgn, base, taker, with_half=False):
    """events: [{"i","t"}]. Returns stats per horizon, by year and by 12h half at PRIMARY_H, and verdict."""
    rt = 2 * taker
    rows = [(e, forward_returns(e["i"], sgn, closes)) for e in events]
    per_h = {}
    for h in HORIZONS:
        g = [f[h] for _, f in rows if h in f]
        gm, _ = _mean_t(g)
        nm, nt = _mean_t([x - rt for x in g])
        b = base.get(h)
        per_h[h] = {"n": len(g), "gross_mean": gm, "net_mean": nm, "net_t": nt,
                    "hit_net": (sum(1 for x in g if x - rt > 0) / len(g)) if g else None,
                    "baseline_side": (sgn * b) if b is not None else None}

    def split(keyf):
        groups = {}
        for e, f in rows:
            if PRIMARY_H in f:
                groups.setdefault(keyf(e["t"]), []).append(f[PRIMARY_H] - rt)
        return {k: {"n": len(v), "net_mean": sum(v) / len(v)} for k, v in sorted(groups.items())}

    by_year = split(_year)
    by_half = split(_half) if with_half else None
    return {"horizons": per_h, "by_year": by_year, "by_half": by_half,
            "verdict": verdict(per_h[PRIMARY_H], by_year)}


def verdict(p, by_year):
    if p["n"] < MIN_EVENTS:
        return "insufficient n"
    years = [v for v in by_year.values() if v["n"] >= MIN_YEAR_EVENTS]
    years_ok = years and sum(1 for v in years if v["net_mean"] > 0) * 2 >= len(years)
    if (p["net_mean"] is not None and p["net_mean"] > 0 and p["net_t"] is not None and p["net_t"] >= T_MIN
            and p["baseline_side"] is not None and p["gross_mean"] > p["baseline_side"] and years_ok):
        return "edge candidate"
    return "no edge"


# ---------------------------------------------------------------- per timeframe

def run_tf(bars, malkan_params, taker, with_half):
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    closes = [b["c"] for b in bars]
    ts = [b["t"] for b in bars]
    if len(closes) <= RSI_PERIOD + 2:
        return {"n_bars": len(bars), "columns": {}}
    rsi = rsi_core(closes, RSI_PERIOD)
    base = baseline(closes)
    cols = {}
    for kind, sgn in (("bullish", 1.0), ("bearish", -1.0)):
        mk = rsi_divergence(closes, rsi, ts, malkan_params["min_bars"], malkan_params["max_bars"], kind,
                            malkan_params.get("min_rsi_diff", 0.0))
        op = long_range_divergence(closes, rsi, ts, OPERATOR_MIN_BARS, OPERATOR_MAX_BARS, kind)
        cols.setdefault("malkan", {})[kind] = score(mk, closes, sgn, base, taker, with_half)
        cols.setdefault("operator", {})[kind] = score(op, closes, sgn, base, taker, with_half)
        cols["malkan"][kind]["n_events"] = len(mk)
        cols["operator"][kind]["n_events"] = len(op)
    return {"n_bars": len(bars), "first_t": ts[0], "last_t": ts[-1], "columns": cols}


def _pct(x):
    return "-" if x is None else "%+.3f%%" % (x * 100)


def render_report(summary):
    L = ["# T089 RSI divergence on every timeframe (+ T091 operator long-range column)", "",
         "Data: BTCUSDT 1m %s .. %s, resampled per registry. RSI %d. Fees: one taker round trip %.2f%% "
         "deducted from every event (fees.py). Primary horizon %d bars; verdict needs >= %d events, net > 0, "
         "t >= %.1f, gross above same-side drift, net > 0 in half the years. Malkan column = sourced 3-10 bar "
         "rule; operator column = T091 11-60 bar non-adjacent idea (NO-SOURCE)." % (
             summary["data_from"], summary["data_to"], RSI_PERIOD, 2 * summary["taker"] * 100, PRIMARY_H,
             MIN_EVENTS, T_MIN), "",
         "| TF | Column | Kind | Events | n@h | Gross | Drift (side) | Net | t | Hit net | Verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for tf, r in summary["tfs"].items():
        for col, kinds in r["columns"].items():
            for kind, s in kinds.items():
                p = s["horizons"][PRIMARY_H] if PRIMARY_H in s["horizons"] else s["horizons"][str(PRIMARY_H)]
                L.append("| %s | %s | %s | %d | %d | %s | %s | %s | %s | %s | %s |" % (
                    tf, col, kind, s["n_events"], p["n"], _pct(p["gross_mean"]), _pct(p["baseline_side"]),
                    _pct(p["net_mean"]), "-" if p["net_t"] is None else "%.2f" % p["net_t"],
                    "-" if p["hit_net"] is None else "%.1f%%" % (p["hit_net"] * 100), s["verdict"]))
    L += ["", "## Net mean at the primary horizon by year (events with >= %d per cell shown as n/net)" %
          MIN_YEAR_EVENTS, ""]
    years = sorted({y for r in summary["tfs"].values() for k in r["columns"].values() for s in k.values()
                    for y in s["by_year"]})
    L.append("| TF | Column | Kind | " + " | ".join(str(y) for y in years) + " |")
    L.append("|---|---|---|" + "---|" * len(years))
    for tf, r in summary["tfs"].items():
        for col, kinds in r["columns"].items():
            for kind, s in kinds.items():
                cells = []
                for y in years:
                    v = s["by_year"].get(y) or s["by_year"].get(str(y))
                    cells.append("-" if not v else "%d/%s" % (v["n"], _pct(v["net_mean"])))
                L.append("| %s | %s | %s | %s |" % (tf, col, kind, " | ".join(cells)))
    return "\n".join(L) + "\n"


def main():
    from MyTradingSys.backtest.bt.bt_data import load_klines
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--tfs", default=None, help="comma list; default every registry timeframe")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    mp = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    taker = load_taker()
    bars_1m = load_klines(args.data_root)
    last_t = bars_1m[-1]["t"] if bars_1m else 0
    bars_1m += [b for b in load_klines(args.data_root2) if b["t"] > last_t]
    bars_1m.sort(key=lambda b: b["t"])
    if not bars_1m:
        print("No data found", file=sys.stderr)
        return 2
    print("Loaded %d 1m bars" % len(bars_1m), file=sys.stderr, flush=True)
    fmt = lambda t: datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    tfs = args.tfs.split(",") if args.tfs else list(registry["timeframes"])
    res = {}
    for tf in tfs:
        bars = bars_1m if tf == "1m" else resample(bars_1m, tf, registry)
        spec = registry["timeframes"][tf]
        with_half = spec.get("unit") == "seconds" and spec["seconds"] < 43200
        res[tf] = run_tf(bars, mp, taker, with_half)
        print("%s: %d bars done" % (tf, len(bars)), file=sys.stderr, flush=True)
    summary = {"task": "T089+T091", "data_from": fmt(bars_1m[0]["t"]), "data_to": fmt(bars_1m[-1]["t"]),
               "taker": taker, "rsi_period": RSI_PERIOD, "primary_h": PRIMARY_H, "min_events": MIN_EVENTS,
               "malkan_params": {k: mp[k] for k in ("min_bars", "max_bars", "min_rsi_diff")},
               "operator_window": [OPERATOR_MIN_BARS, OPERATOR_MAX_BARS], "tfs": res}
    with open(out_dir / "summary.json", "w", newline="\n", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    with open(out_dir / "REPORT.md", "w", newline="\n", encoding="utf-8") as f:
        f.write(render_report(summary))
    print("Done. %s" % out_dir, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
