"""T06-F3 planted-gap fill canary. Read-only: imports five engine fill paths, edits none.

Planted series (long): entry 100.0, stop 99.0 (R = 1.0), a bar whose OPEN is 1% beyond the stop (98.01).
  scenario P: the gap bar is the first bar AFTER the entry bar (post-fill gap).
  scenario F: the gap bar is the entry-limit FILL bar itself (only tom_bt / fabio v3 test the stop on it).
Per engine it records the stop-exit price, the slippage charged and where it lives (file:line).
Run: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/fill_canary.py [--write]
"""
import inspect
import sys
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[5]
BT = REPO / "MyTradingSys" / "backtest"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(BT))

ENTRY, STOP, TARGET = 100.0, 99.0, 102.0
GAP_OPEN = STOP * 0.99          # 1% beyond the stop = 98.01
MD = Path(__file__).resolve().parents[2] / "FILL_CANARY.md"

# fill-function signatures the canary was written against (parameter names, in order)
EXPECTED_SIGS = {
    "bt_engine.simulate_trade": ["side", "entry_price", "entry_t", "stop", "targets", "bars", "mark_bars", "funding",
                                 "taker_fee", "maker_fee", "max_bars", "stop_first", "target_through"],
    "run_rsi_backtest.trades_from_events": ["events", "bars", "stop_pct", "target_pct", "max_bars", "taker", "maker",
                                            "funding"],
    "sim.run": ["rows", "rule", "stops", "taker", "maker"],
    "fabio_v3.walk_trade": ["bars", "fill_idx", "s", "entry", "D", "stop", "ctrl", "absorbed", "mgmt", "be_k", "tick",
                            "end_idx", "target", "s8_kw", "stop_first", "force_close"],
    "fabio_v3.simulate_trade": ["bars", "fill_idx", "s", "entry", "D", "stop", "q1", "entry_kind", "be_k", "ctrl",
                                "tick", "end_idx", "target", "slip_bps", "mgmt", "absorbed", "s8_kw", "stop_first"],
    "tom_bt.sim_limit_trade": ["b", "i0", "side", "entry", "stop", "target", "fill_window", "hold_bars", "fees",
                               "stop_first", "slip", "slip_pts", "through_ticks"],
}


def _load():
    import importlib
    import sim as sim_mod
    return {
        "bt_engine": importlib.import_module("MyTradingSys.backtest.bt.bt_engine"),
        "run_rsi_backtest": importlib.import_module("MyTradingSys.backtest.layers.rsi.run_rsi_backtest"),
        "sim": sim_mod,
        "fabio_manage": importlib.import_module("MyTradingSys.backtest.layers.fabio.v3.manage"),
        "tom_bt": importlib.import_module("MyTradingSys.backtest.tom_bt"),
    }


def _fns(m):
    return {
        "bt_engine.simulate_trade": m["bt_engine"].simulate_trade,
        "run_rsi_backtest.trades_from_events": m["run_rsi_backtest"].trades_from_events,
        "sim.run": m["sim"].run,
        "fabio_v3.walk_trade": m["fabio_manage"].walk_trade,
        "fabio_v3.simulate_trade": m["fabio_manage"].simulate_trade,
        "tom_bt.sim_limit_trade": m["tom_bt"].sim_limit_trade,
    }


def check_signatures(fns=None, expected=None):
    """Raise if any fill function's parameter names changed (the canary would be calling it wrongly)."""
    fns = _fns(_load()) if fns is None else fns
    expected = EXPECTED_SIGS if expected is None else expected
    bad = {}
    for k, want in expected.items():
        got = list(inspect.signature(fns[k]).parameters)
        if got != want:
            bad[k] = {"expected": want, "got": got}
    if bad:
        raise RuntimeError("fill-function signature changed, canary must be revisited: %r" % bad)


def _bar(t, o, h, l, c):
    return {"t": t, "o": o, "h": h, "l": l, "c": c}


ENTRY_BAR = _bar(0, 100.1, 100.3, 99.8, 100.0)
GAP_BAR = _bar(60000, GAP_OPEN, 98.5, 97.5, 98.2)
FILL_GAP_BAR = _bar(0, GAP_OPEN, 98.5, 97.5, 98.2)   # scenario F: the fill bar opens beyond the stop
TAIL_BAR = _bar(120000, 98.2, 98.4, 98.0, 98.3)


def _tom_bars(m, rows):
    from array import array

    def mk(k):
        return array("d", [r[k] for r in rows])
    return m["tom_bt"].Bars1m(0, mk("o"), mk("h"), mk("l"), mk("c"), array("d", [1.0] * len(rows)),
                              array("d", [0.5] * len(rows)))


def run_canary():
    m = _load()
    fns = _fns(m)
    check_signatures(fns)
    out = []

    def row(engine, where, scen, fill, slip, note):
        out.append({"engine": engine, "where": where, "scenario": scen, "fill": fill, "slip": slip, "note": note,
                    "at_stop": abs(fill - STOP) < 1e-9, "at_open": abs(fill - GAP_OPEN) < 1e-9})

    # bt_engine (P)
    r = fns["bt_engine.simulate_trade"]("long", ENTRY, 0, STOP, [(TARGET, 1.0)], [GAP_BAR, TAIL_BAR], funding=[])
    row("bt_engine.simulate_trade", "MyTradingSys/backtest/bt/bt_engine.py:88-89,98", "P", r["fills"][0][1], None,
        "no slippage parameter; taker fee only (:57)")
    # run_rsi_backtest -> bt_engine (P): capture the engine fill through the driver
    mod = m["run_rsi_backtest"]
    seen = {}
    real = mod.simulate_trade

    def spy(*a, **k):
        res = real(*a, **k)
        seen["fills"] = res["fills"]
        return res
    with mock.patch.object(mod, "simulate_trade", spy):
        mod.trades_from_events([{"i": 0, "side": "long"}], [ENTRY_BAR, GAP_BAR, TAIL_BAR], stop_pct=0.01,
                               target_pct=0.02, taker=0.0005, maker=0.0, funding=[])
    row("run_rsi_backtest.trades_from_events", "MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:107-110", "P",
        seen["fills"][0][1], None, "delegates to bt_engine; no slippage argument is passed")
    # sim.py (P) both stop modes
    rows = [dict(ts="t0", t=0, setup="s", dir="long", price=ENTRY, stop=STOP, target=TARGET, verdict="SETUP_FORMING"),
            dict(ts="t1", t=60, setup="s", dir="long", price=GAP_OPEN, stop=STOP, target=TARGET, verdict="WATCH")]
    for mode in ("observed", "ideal"):
        tr = fns["sim.run"](rows, "A", mode, 0.0005, 0.0)
        assert len(tr) == 1 and tr[0]["kind"] == "stop", tr
        row("sim.run (--stops %s)" % mode, "MyTradingSys/backtest/sim.py:68-69,77", "P",
            ENTRY + tr[0]["gross"] * 1.0, None, "snapshot price path; no slippage term, fees only (:77)")
    # fabio v3 (P and F)
    wt = fns["fabio_v3.simulate_trade"]
    for scen, bars in (("P", [ENTRY_BAR, GAP_BAR]), ("F", [FILL_GAP_BAR, TAIL_BAR])):
        t = wt(bars, 0, 1, ENTRY, 1.0, STOP, q1=1.0, entry_kind="maker")
        row("fabio v3 manage.walk_trade", "MyTradingSys/backtest/layers/fabio/v3/manage.py:141-143", scen, t["exit"],
            t["slip_r"], "slip_bps default 0.0 (costs.py leg_r); fill bar keeps the stop price, later bars the open")
    # tom_bt (P and F)
    for scen, rows_ in (("P", [_bar(0, 100.1, 100.3, 99.9, 100.0), GAP_BAR, TAIL_BAR]),
                        ("F", [FILL_GAP_BAR, TAIL_BAR, TAIL_BAR])):
        res = fns["tom_bt.sim_limit_trade"](_tom_bars(m, rows_), 0, "long", ENTRY, STOP, TARGET, 3, 3)
        assert res["filled"] and res["reason"] == "stop", res
        sp = inspect.signature(fns["tom_bt.sim_limit_trade"]).parameters
        row("tom_bt.sim_limit_trade", "MyTradingSys/backtest/tom_bt.py:211-213,224", scen, ENTRY + res["gross_r"],
            sp["slip"].default + sp["slip_pts"].default, "slip/slip_pts default 0.0, run_variant passes 0 (:260-261)")
    return out


def verdict(rows):
    """Engines (with mode/scenario) that fill the gapped stop at the stop price instead of the open."""
    return sorted({"%s [%s]" % (r["engine"], r["scenario"]) for r in rows if r["at_stop"]})


def render(rows):
    L = ["# FILL_CANARY: where a gapped stop fills (T06-F3)", "",
         "Planted long: entry %.2f, stop %.2f (R = 1.00), gap bar open %.2f (1%% beyond the stop). No engine was edited; "
         "generated by `scripts/T06/fill_canary.py --write`. Scenario P = gap bar right after the entry bar; "
         "scenario F = the gap bar is the entry-limit fill bar (only tom_bt and fabio v3 test the stop there)."
         % (ENTRY, STOP, GAP_OPEN), "",
         "| Engine | Scen | Stop-exit price | vs stop | vs open | Slippage charged | file:line | Note |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        sl = "none (no parameter)" if r["slip"] is None else "%g" % r["slip"]
        L.append("| %s | %s | %.4f | %s | %s | %s | %s | %s |" % (
            r["engine"], r["scenario"], r["fill"], "AT STOP" if r["at_stop"] else "%+.4f" % (r["fill"] - STOP),
            "AT OPEN" if r["at_open"] else "%+.4f" % (r["fill"] - GAP_OPEN), sl, r["where"], r["note"]))
    stop_fill = verdict(rows)
    n_eng = len({s.split(" [")[0].split(" (")[0] for s in stop_fill})
    L += ["", "Optimism direction: a fill at the stop price (99.00) instead of the open (98.01) understates the long's "
          "loss by 0.99 R on this plant, so every row marked AT STOP is optimistic and rows at the open are the "
          "conservative convention. No engine charges slippage on the stop by default (all 0 or no parameter).", "",
          "**Verdict: %d engine(s) fill a gap at the stop price: %s.** All other tested paths fill at the open."
          % (n_eng, "; ".join(stop_fill) if stop_fill else "none")]
    if n_eng > 1:
        L.append("More than one, so a follow-up card is filed to size how often it bites on real bars.")
    return "\n".join(L) + "\n"


def main():
    rows = run_canary()
    text = render(rows)
    if "--write" in sys.argv:
        with open(MD, "w", newline="\n", encoding="utf-8") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
