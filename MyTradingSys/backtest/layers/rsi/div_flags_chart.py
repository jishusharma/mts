"""
Malkan RSI divergence flags drawn on charts (operator 2026-10-28: he confirms/corrects readings by looking).

One PNG per (symbol, timeframe): candles on top, RSI(14) below. For every detected divergence a line joins swing A to
swing B on the price panel (at the closes: Malkan compares close to close) and on the RSI panel, and a numbered label
sits at B. The same numbering is written to a markdown + CSV table next to the charts.
Malkan kinds (rsi_divergence.py, only as Malkan says it): R-BULL / R-BEAR regular, PRD / NRD reverse divergence with the
trend condition (RSI >= 60 at both points for PRD, <= 40 for NRD). Drawn SOLID (regular) and THICK SOLID (PRD/NRD).
KROWN-CONFLUENCE (krown_hidden_divergence.py, generic hidden divergence, NO trend condition, not Malkan): K-HBULL /
K-HBEAR, drawn DOTTED in violet so they cannot be mistaken for Malkan flags.

Parameters: regular bars window 3-10 and min_rsi_diff 0 = SOURCED (params/malkan_divergence_default.json, quotes there);
PRD/NRD levels 60/40 = SOURCED (GbXnw_tNMtw_raw.txt:460), PRD/NRD bars window 5-14 = OURS, UNVERIFIED (sources conflict,
glossary C1); Krown hidden window 3-10 = OURS; RSI period 14 = SOURCED default of the layer
(run_divergence_mtf.RSI_PERIOD); the 250-bar view and 1w built from complete Mon-Sun UTC daily bars = OURS (display).
Causal: the event is stamped one bar after swing B (t_event); the label is drawn at B. The RSI is Wilder RSI from the
whole history, so truncating future bars never changes an earlier flag (test_div_flags_chart.py).
T01-F2: the raw_1d daily klines are a different feed from live (mismatch measured by the T01 audit); the flags
are for visual review only, never a trading input.
Data: local Binance daily klines (free public data) via bt_data.load_klines; 1w is aggregated from them.
Usage: python -m MyTradingSys.backtest.layers.rsi.div_flags_chart --symbol BTCUSDT --tfs 1d,1w --bars 250
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence, KINDS
from MyTradingSys.backtest.layers.rsi.krown_hidden_divergence import krown_hidden_divergence, KROWN_KINDS

PARAMS_PATH = Path(__file__).resolve().parent / "params" / "malkan_divergence_default.json"
REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
RSI_PERIOD = 14
ALL_KINDS = KINDS + KROWN_KINDS
CODE = {"bullish": "R-BULL", "bearish": "R-BEAR", "prd": "PRD", "nrd": "NRD",
        "hidden_bullish": "K-HBULL", "hidden_bearish": "K-HBEAR"}
COLOR = {"bullish": "#1b9e4b", "bearish": "#d6281f", "prd": "#0b6fb8", "nrd": "#c26a00",
         "hidden_bullish": "#8e7cc3", "hidden_bearish": "#a67c9a"}
LINESTYLE = {"hidden_bullish": ":", "hidden_bearish": ":"}
LINEWIDTH = {"prd": 2.8, "nrd": 2.8, "hidden_bullish": 1.5, "hidden_bearish": 1.5}
LOW_KINDS = ("bullish", "prd", "hidden_bullish")   # label below the swing low
WEEK_MS = 7 * 86400000


def _fmt(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def find_data_root(symbol="BTCUSDT"):
    """raw_1d lives in the main checkout (gitignored); a worktree has none, so look up the checkout path."""
    cands = [REPO / "Dumps" / "backtest" / "raw_1d"]
    for p in REPO.parents:
        if p.name == ".claude" and p.parent.name != ".claude":
            cands.append(p.parent / "Dumps" / "backtest" / "raw_1d")
    for c in cands:
        if (c / "klines").exists():
            return c
    raise FileNotFoundError("no Dumps/backtest/raw_1d/klines found; pass --data-root")


def load_daily(root, symbol="BTCUSDT"):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    return load_klines(root)


def weekly_from_daily(days):
    """Complete Monday-anchored UTC weeks only (7 daily bars); a partial trailing or leading week is dropped.
    Monday anchor: epoch day 0 is Thursday, so Monday = epoch_day % 7 == 4 (same rule as tf_resample)."""
    groups = {}
    for b in days:
        d = b["t"] // 86400000
        start = (d - ((d - 4) % 7)) * 86400000
        groups.setdefault(start, []).append(b)
    out = []
    for start in sorted(groups):
        g = sorted(groups[start], key=lambda b: b["t"])
        if len(g) != 7 or [x["t"] for x in g] != [start + k * 86400000 for k in range(7)]:
            continue
        out.append({"t": start, "o": g[0]["o"], "h": max(x["h"] for x in g), "l": min(x["l"] for x in g),
                    "c": g[-1]["c"], "v": sum(x["v"] for x in g)})
    return out


def detect_all(bars, params=None):
    """Malkan kinds (regular, PRD, NRD) plus KROWN-CONFLUENCE hidden kinds over the whole series.
    Returns events sorted by (b_i, kind) with the RSI series."""
    params = params or json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    close = [b["c"] for b in bars]
    ts = [b["t"] for b in bars]
    rsi = rsi_core(close, RSI_PERIOD) if len(close) > RSI_PERIOD + 2 else [None] * len(close)
    evs = []
    if any(r is not None for r in rsi):
        rv = params["reverse"]
        kh = params["krown_hidden_bars"]
        for kind in KINDS:
            lo, hi = ((rv["min_bars"], rv["max_bars"]) if kind in ("prd", "nrd")
                      else (params["min_bars"], params["max_bars"]))
            for e in rsi_divergence(close, rsi, ts, lo, hi, kind, params.get("min_rsi_diff", 0.0)):
                e["kind"] = kind
                evs.append(e)
        for kind in KROWN_KINDS:
            for e in krown_hidden_divergence(close, rsi, ts, kh["min_bars"], kh["max_bars"], kind,
                                             params.get("min_rsi_diff", 0.0)):
                e["kind"] = kind
                evs.append(e)
    evs.sort(key=lambda e: (e["b_i"], ALL_KINDS.index(e["kind"])))
    return evs, rsi


def select_window(evs, n_bars, total):
    """Events fully inside the last n_bars (A and B both visible), numbered #1..n by B."""
    start = max(0, total - n_bars)
    sel = [e for e in evs if e["a_i"] >= start]
    for k, e in enumerate(sel, 1):
        e["n"] = k
    return start, sel


def table_rows(sel, tf):
    rows = []
    for e in sel:
        rows.append({"n": e["n"], "code": CODE[e["kind"]], "tf": tf, "date_A": _fmt(e["a_t"]),
                     "date_B": _fmt(e["b_t"]), "event_known_on": _fmt(e["t"]), "bars_A_to_B": e["bars"],
                     "price_A": e["close_a"], "price_B": e["close_b"],
                     "rsi_A": round(e["rsi_a"], 2), "rsi_B": round(e["rsi_b"], 2), "chain": e["chain"]})
    return rows


def render(bars, evs, rsi, tf, symbol, n_bars, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    start, sel = select_window(evs, n_bars, len(bars))
    view = list(range(start, len(bars)))
    fig, (ax, ar) = plt.subplots(2, 1, figsize=(20, 11), sharex=True, gridspec_kw={"height_ratios": [3, 1.4]})
    for i in view:
        b = bars[i]
        up = b["c"] >= b["o"]
        col = "#26a69a" if up else "#ef5350"
        ax.plot([i, i], [b["l"], b["h"]], color=col, lw=0.8, zorder=1)
        ax.add_patch(plt.Rectangle((i - 0.35, min(b["o"], b["c"])), 0.7, max(abs(b["c"] - b["o"]), 1e-9),
                                   color=col, zorder=2))
    rv = [(i, rsi[i]) for i in view if rsi[i] is not None]
    ar.plot([p[0] for p in rv], [p[1] for p in rv], color="#444", lw=1.2)
    for lv, st in ((60, "--"), (50, "-"), (40, "--")):
        ar.axhline(lv, color="#999", lw=0.6, ls=st)
    ar.set_ylim(0, 100)
    ar.set_ylabel("RSI(%d)" % RSI_PERIOD)
    n_ann = 0
    for e in sel:
        col = COLOR[e["kind"]]
        ls = LINESTYLE.get(e["kind"], "-")
        lw = LINEWIDTH.get(e["kind"], 1.8)
        ax.plot([e["a_i"], e["b_i"]], [e["close_a"], e["close_b"]], color=col, lw=lw, ls=ls, zorder=3,
                marker="o", ms=4)
        ar.plot([e["a_i"], e["b_i"]], [e["rsi_a"], e["rsi_b"]], color=col, lw=lw, ls=ls, zorder=3,
                marker="o", ms=4)
        low = e["kind"] in LOW_KINDS
        dy = -1 if low else 1
        lab = "%s #%d" % (CODE[e["kind"]], e["n"])
        t1 = ax.annotate(lab, (e["b_i"], e["close_b"]), xytext=(0, (26 + 16 * (e["n"] % 2)) * dy), textcoords="offset points",
                         ha="center", va="top" if low else "bottom", fontsize=8, color="white", zorder=5,
                         bbox=dict(boxstyle="round,pad=0.2", fc=col, ec="none"),
                         arrowprops=dict(arrowstyle="-", color=col, lw=0.8))
        t1.set_gid("div-label")
        t2 = ar.annotate("#%d" % e["n"], (e["b_i"], e["rsi_b"]), xytext=(0, (12 + 10 * (e["n"] % 2)) * dy), textcoords="offset points",
                         ha="center", va="top" if low else "bottom", fontsize=8, color=col, zorder=5)
        t2.set_gid("div-label-rsi")
        n_ann += 1
    ax.set_title("%s %s  Malkan RSI divergence flags  (thin solid = regular, thick solid = PRD/NRD reverse "
                 "divergence with RSI 60/40 trend condition; DOTTED violet K-HBULL/K-HBEAR = KROWN-CONFLUENCE generic "
                 "hidden, not Malkan; label at swing B, event known 1 bar later)  last %d bars" % (symbol, tf, len(view)))
    step = max(1, len(view) // 14)
    ticks = view[::step]
    ar.set_xticks(ticks)
    ar.set_xticklabels([_fmt(bars[i]["t"]) for i in ticks], rotation=45, ha="right", fontsize=8)
    ax.set_xlim(start - 1, len(bars) + 1)
    lo = min(bars[i]["l"] for i in view)
    hi = max(bars[i]["h"] for i in view)
    pad = (hi - lo) * 0.08
    ax.set_ylim(lo - pad, hi + pad)
    ax.grid(alpha=0.2)
    ar.grid(alpha=0.2)
    fig.tight_layout()
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=90)
    plt.close(fig)
    return {"n_events": len(sel), "n_annotations": n_ann, "events": sel}


def write_table(rows_by_tf, out_dir, symbol):
    out_dir = Path(out_dir)
    cols = ["n", "code", "tf", "date_A", "date_B", "event_known_on", "bars_A_to_B", "price_A", "price_B",
            "rsi_A", "rsi_B", "chain"]
    with open(out_dir / ("%s_divergences.csv" % symbol), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for rows in rows_by_tf.values():
            w.writerows(rows)
    lines = ["# %s Malkan RSI divergence flags" % symbol, "",
             "Numbers match the labels on the charts. Malkan flags: R-BULL / R-BEAR regular divergence (window 3-10 bars "
             "A..B inclusive, SOURCED); PRD = price higher low + RSI lower low in an uptrend (RSI >= 60 at both "
             "points), NRD = price lower high + RSI higher high in a downtrend (RSI <= 40 at both points); levels "
             "SOURCED (GbXnw_tNMtw_raw.txt:460), window 5-14 bars OURS/UNVERIFIED (sources conflict). "
             "KROWN-CONFLUENCE flags: K-HBULL / K-HBEAR = generic hidden divergence with NO trend condition, not "
             "Malkan, window 3-10 OURS. Price = close (Malkan: close to close).", ""]
    for tf, rows in rows_by_tf.items():
        lines += ["## %s  (%d events)" % (tf, len(rows)), "",
                  "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        for r in rows:
            lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        lines.append("")
    with open(out_dir / ("%s_divergences.md" % symbol), "w", newline="\n", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--tfs", default="1d,1w")
    ap.add_argument("--bars", type=int, default=250)
    ap.add_argument("--data-root", default=None, help="folder holding klines/ with daily csv files")
    ap.add_argument("--out", default=str(REPO / "MyTradingSys" / "research" / "malkan_div_flags_2026-10-28"))
    a = ap.parse_args(argv)
    days = load_daily(a.data_root or find_data_root(a.symbol), a.symbol)
    if not days:
        print("no daily data", file=sys.stderr)
        return 2
    out = Path(a.out)
    rows_by_tf = {}
    for tf in a.tfs.split(","):
        bars = days if tf == "1d" else weekly_from_daily(days) if tf == "1w" else None
        if bars is None:
            raise ValueError("only 1d and 1w supported here")
        evs, rsi = detect_all(bars)
        res = render(bars, evs, rsi, tf, a.symbol, a.bars, out / "charts" / ("%s_%s.png" % (a.symbol, tf)))
        rows_by_tf[tf] = table_rows(res["events"], tf)
        print("%s %s: %d bars (%s..%s), %d events in last %d bars" % (
            a.symbol, tf, len(bars), _fmt(bars[0]["t"]), _fmt(bars[-1]["t"]), res["n_events"], a.bars))
    write_table(rows_by_tf, out, a.symbol)
    return 0


if __name__ == "__main__":
    sys.exit(main())
