"""Per-trade chart data for one Malkan-gated RSI divergence cell (sim page: divergence drawn on CLOSES, 12/18 bar window).
Rebuilds the DEV trades exactly as study.py --pass dev does (same bars, same find_events / gate_events / trades_for), checks the
trade count and mean net % against dev_cells.csv, then writes per trade the candles around it as % from the entry price (no
prices), RSI 14, the signal/entry/exit bars and the two divergence closes (swing A, swing B). DEV window only, as the study read it;
HOLDOUT never loaded. Research only, no orders.
Cell pick (DECISION, OURS): 4h, W18 (3-18 bars, SOURCED), bullish, gate aligned, entry signal: the largest aligned cell above 15m.
Usage: python malkan_div_trade_charts.py [results_json]"""
import csv
import json
import sys
from datetime import datetime, timezone

import study as S

TF, ARM, KIND, GATE, ENTRY = "4h", "W18", "bullish", "aligned", "signal"
BEFORE, AFTER = 30, 4  # candles shown before swing B and after the exit (OURS, display only)
RID = "rsi-divergence-mtf-gated-run1-2026-11-04"


def window_start(a_i, b_i, before=BEFORE, pad_a=4):
    """First candle drawn: the EARLIER of (pad_a bars before swing A) and (`before` bars before swing B), never below 0."""
    return max(0, min(a_i - pad_a, b_i - before))


def span_class(span):
    """Arm bucket of the A-to-B distance in bars: '3-12' (W12 and W18 both fire), '13-18' (W18 only), '>18' (neither arm)."""
    return "3-12" if span <= 12 else ("13-18" if span <= 18 else ">18")


def ledger_row():
    for r in csv.DictReader(open(S.HERE / "dev_cells.csv", encoding="utf-8")):
        if (r["tf"], r["arm"], r["kind"], r["gate"], r["entry"]) == (TF, ARM, KIND, GATE, ENTRY):
            return r
    raise SystemExit("cell not in dev_cells.csv")


def build():
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    registry = json.loads((S.REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    lo_ms, hi_ms = S.ms(S.splits.DEV_START), S.ms(S.splits.DEV_END)
    bars_1m = S.load_1m(hi_ms)
    assert bars_1m[-1]["t"] < hi_ms
    regime_at = S.make_regime_at(*S.build_context(bars_1m, registry))
    bars = resample(bars_1m, TF, registry)
    ge = S.gate_events(S.find_events(bars, KIND, ARM, TF), regime_at, KIND, GATE)
    trs, _ = S.trades_for(ge, bars, KIND, ENTRY, lo_ms=lo_ms, hi_ms=hi_ms)
    ev = {bars[e["i"]]["t"]: e for e in ge}
    T = {b["t"]: k for k, b in enumerate(bars)}
    C = [b["c"] for b in bars]
    R = rsi_core(C, S.RSI_PERIOD)
    rd = lambda v: None if v is None else round(v, 1)
    out = []
    for x in trs:
        e, i = ev[x["t"]], T[x["t"]]  # signal entry: fill at the close of event bar i, exit at the close of bar i + H
        a, z = window_start(e["a_i"], e["b_i"]), min(len(bars) - 1, i + S.H + AFTER)
        E = C[i]
        pc = lambda v: round((v / E - 1) * 100, 3)
        out.append(dict(
            d=datetime.fromtimestamp(x["t"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M"), t0=bars[a]["t"],
            net=round(x["gross"] - S.COST, 3), bars=S.H, why="time exit: close %d candles after entry" % S.H,
            sig=i - a, ent=i - a, ext=i + S.H - a, div=[e["a_i"] - a, e["b_i"] - a], span=e["b_i"] - e["a_i"], arm=span_class(e["b_i"] - e["a_i"]),
            c=[[pc(bars[m]["o"]), pc(bars[m]["h"]), pc(bars[m]["l"]), pc(bars[m]["c"])] for m in range(a, z + 1)],
            w1=[None] * (z - a + 1), w2=[None] * (z - a + 1), rsi=[rd(R[m]) for m in range(a, z + 1)]))
    return out


def main():
    ref = ledger_row()
    trades = build()
    assert len(trades) == int(ref["n"]), (len(trades), ref["n"])
    m = sum(t["net"] for t in trades) / len(trades)
    assert abs(m - float(ref["net"])) < 1e-2, (m, ref["net"])
    path = sys.argv[1] if len(sys.argv) > 1 else str(S.REPO / "MyTradingSys/research/sim_desk/results" / (RID + ".json"))
    r = json.load(open(path, encoding="utf-8"))
    ex = [e for e in r["examples"] if e.get("kind") not in ("none", "trade_chart")]
    ex.insert(0, {
        "kind": "trade_chart", "tf": TF, "tf_min": 240, "div_on": "close", "ledger_n": int(ref["n"]),
        "title": "Every DEV trade of the 4h W18 bullish cell (Malkan gate aligned): where it entered, where it exited",
        "stop_note": "No stop loss: entry at the close of the signal candle, exit at the close 10 candles later.",
        "caption": "Rebuilt by malkan_div_trade_charts.py from the same bars and code as study.py; trade count %s and mean net %s %% "
                   "match dev_cells.csv. DEV window only." % (ref["n"], ref["net"][:6]),
        "div_rule": "Divergence drawn here: Malkan's rule on candle CLOSES (swing A to swing B within 3-18 candles, W18 SOURCED).",
        "trades": trades})
    r["examples"] = ex
    sys.path.insert(0, str(S.REPO / "MyTradingSys/research/sim_desk/artifact"))
    import build_artifact as ba
    r["banner"] = ba.banner_of(r)  # the banner reads n from the trade list now
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("ok", len(trades), "trades; count and mean net match dev_cells.csv")


if __name__ == "__main__":
    main()
