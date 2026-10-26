"""T10-F2 / C05: stop-first vs target-first bounds for the tight-stop 1m sims (Tom tom_bt, Fabio v3, bt_engine).

No sim file is edited: tom_bt.sim_limit_trade, bt_engine.simulate_trade and fabio v3 manage.simulate_trade already
take stop_first (default True = stop wins a bar holding both). This script forces it per run (OURS: that is the
"resolve_both" seam; the Fabio engine and the CryptoCred runner hard-wire the default, so the call name is wrapped).
DEV/VALIDATION only: Tom rows t < 2026-06-26 (HOLDOUT start), Fabio windows <= 2026-06-25, CC runs dev span only.
Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/intrabar_bounds.py
Writes ../../INTRABAR_BOUNDS.md (and prints it)."""
import datetime as dt
import functools
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT_MD = HERE.parents[1] / "INTRABAR_BOUNDS.md"
for p in (ROOT, ROOT / "MyTradingSys" / "backtest"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

TIGHT = 0.0015            # "stops under 0.15%" of entry (card)
T_HOLD = dt.datetime(2026, 6, 26, tzinfo=dt.timezone.utc).timestamp()   # HOLDOUT start, never read
FABIO_LAST = dt.date(2026, 6, 25)
FABIO_FIRST = dt.date(2024, 12, 2)
MODES = ("stop", "target")


def stop_first_of(both):
    if both not in MODES:
        raise ValueError("both must be 'stop' or 'target', got %r" % (both,))
    return both == "stop"


# ---- single-trade seams (used by the tests with planted bars)
def tom_trade(b, i0, side, entry, stop, target, both, **kw):
    import tom_bt as T
    fees = kw.pop("fees", T.FEES_DERIBIT)
    return T.sim_limit_trade(b, i0, side, entry, stop, target, kw.pop("fill_window", 5), kw.pop("hold", 5), fees,
                             stop_first_of(both), **kw)


def engine_trade(both, **kw):
    from MyTradingSys.backtest.bt import bt_engine
    return bt_engine.simulate_trade(stop_first=stop_first_of(both), **kw)


def install_fabio(both):
    """Force the resolution inside Fabio v3 models (they import simulate_trade by name and never pass stop_first)."""
    from MyTradingSys.backtest.layers.fabio.v3 import manage, models
    models.simulate_trade = functools.partial(manage.simulate_trade, stop_first=stop_first_of(both))


def install_cc(both):
    """Same for the CryptoCred runner and its adapter (hard-wired stop_first=True / default)."""
    from MyTradingSys.backtest.bt import bt_engine
    from MyTradingSys.backtest.layers.cryptocred import cc_bt_adapter, run_cc_setups
    f = functools.partial(bt_engine.simulate_trade, stop_first=stop_first_of(both))
    run_cc_setups.simulate_trade = f
    cc_bt_adapter.simulate_trade = f


# ---- reporting helpers
def agg(nets):
    return dict(n=len(nets), total=sum(nets), mean=(sum(nets) / len(nets)) if nets else None)


def fmt(x, nd=4):
    return "n/a" if x is None else ("%+.*f" % (nd, x))


def row(name, n, both, a_stop, a_tgt):
    gap = None if a_stop["mean"] is None or a_tgt["mean"] is None else a_tgt["mean"] - a_stop["mean"]
    flip = (a_stop["mean"] is not None and a_tgt["mean"] is not None and a_stop["mean"] * a_tgt["mean"] < 0)
    return "| %s | %d | %d | %s (n=%d) | %s (n=%d) | %s | %s |" % (
        name, n, both, fmt(a_stop["mean"]), a_stop["n"], fmt(a_tgt["mean"]), a_tgt["n"], fmt(gap),
        "YES" if flip else "no"), flip


# ---- Tom
def run_tom():
    import tom_bt as T
    import tom_bt_run as R
    rows = [r for r in R.load_rows() if r["t"] < T_HOLD]
    b = T.load_bars_1m(R.RAW)
    out, flips = [], []
    for var in ("episode", "A", "watch_episode", "p4_episode"):
        sigs = T.signals(rows, var)
        res = {m: T.run_variant(sigs, b, stop_first=stop_first_of(m)) for m in MODES}
        for label, keep in (("all stops", lambda t: True),
                            ("stop<0.15%", lambda t: abs(float(t["zprice"]) - float(t["stop"])) / float(t["zprice"]) < TIGHT)):
            d = {m: [t for t in res[m] if t.get("filled") and t["reason"] in ("target", "stop", "timeout") and keep(t)]
                 for m in MODES}
            both = sum(t["ambiguous"] for t in d["stop"])
            line, flip = row("Tom %s / %s" % (var, label), len(d["stop"]), both,
                             agg([t["net_r"] for t in d["stop"]]), agg([t["net_r"] for t in d["target"]]))
            out.append(line)
            if flip:
                flips.append("Tom %s / %s" % (var, label))
    return out, flips, len(rows)


# ---- Fabio v3
def _fabio_day(args):
    both, bars, prior, cells = args
    install_fabio(both)
    from MyTradingSys.backtest.layers.fabio.v3 import engine
    res = {}
    pr = (lambda el: [r[el] for r in prior if el < len(r)]) if len(prior) >= 20 else (lambda el: [])
    for key, model, cfg in cells:
        c = dict(cfg, models=(model,), slip_bps=2.0, prior_ranges=pr)
        try:
            tr = engine.run(bars, c)["diagnostics"][model]["trade"]
        except Exception:
            tr = None
        res[key] = None if tr is None else (float(tr["net_r"]), tr["reason"], tr["exit_idx"],
                                            abs(tr["entry"] - tr["stop0"]) / tr["entry"])
    return res


def run_fabio():
    import json
    from MyTradingSys.backtest.layers.fabio import run_v3_l3 as L
    sel = json.loads(Path("F:/MTS/data/fabio_v3_bt/selection.json").read_text(encoding="utf-8"))["chosen"]
    cg = L.grid()
    cells = [(m, cg[k][0], cg[k][1]) for m, k in sel.items()]
    wins, _ = L.build_windows(FABIO_FIRST, FABIO_LAST)
    wins = [w for w in wins if FABIO_FIRST <= w["date"] <= FABIO_LAST]
    per = {}
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as pool:
        for m in MODES:
            per[m] = list(pool.map(_fabio_day, [(m, w["bars"], w["prior"], cells) for w in wins], chunksize=4))
    out, flips = [], []
    for key, _model, _cfg in cells:
        for label, keep in (("all stops", lambda t: True), ("stop<0.15%", lambda t: t[3] < TIGHT)):
            d = {m: [x[key] for x in per[m] if x[key] is not None and keep(x[key])] for m in MODES}
            sf, tf = [x[key] for x in per["stop"]], [x[key] for x in per["target"]]
            # a trade holds a both-hit bar exactly when the two orderings diverge (stop-first exits there)
            both = sum(1 for a, c in zip(sf, tf) if a is not None and c is not None and keep(a)
                       and (a[1], a[2]) != (c[1], c[2]))
            line, flip = row("Fabio v3 model %s (%s) / %s" % (key, sel[key], label), len(d["stop"]), both,
                             agg([t[0] for t in d["stop"]]), agg([t[0] for t in d["target"]]))
            out.append(line)
            if flip:
                flips.append("Fabio v3 %s / %s" % (key, label))
    return out, flips, len(wins)


# ---- bt_engine (CryptoCred runner, DEV span only)
def run_cc():
    from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as C
    base = ROOT.parent / "BinanceDataFeed" / "Dumps" / "backtest"
    r1 = os.environ.get("MTS_CC_DATA_ROOT", str(base / "raw_1m_2022"))
    r2 = os.environ.get("MTS_CC_DATA_ROOT2", str(base / "raw_fund"))
    bars, tfb, fund = C.load_data(r1, r2, "1h")
    _, bo, _ = C.chronological_split(tfb, 0.70)
    split = bo[0]["t"]
    sim = [x for x in bars if x["t"] < split + 1440 * 60000]
    out, flips = [], []
    for name in C.SETUPS:
        res = {}
        sigs = [g for g in C.SETUPS[name](tfb) if g["entry_t"] < split]
        for m in MODES:
            install_cc(m)
            res[m] = C.build_trades(sigs, sim, fund, "maker_entry", 3600000, 1440)
        for label, keep in (("all stops", lambda t: True),
                            ("stop<0.15%", lambda t: t["net_r"] != 0 and abs(t["net_pct"] / t["net_r"]) < TIGHT)):
            d = {m: [t for t in res[m] if keep(t)] for m in MODES}
            tg = {t["t"]: t for t in res["target"]}
            both = sum(1 for a in res["stop"] if keep(a) and a["t"] in tg and a["net_r"] != tg[a["t"]]["net_r"])
            line, flip = row("bt_engine/CryptoCred %s / %s" % (name, label), len(d["stop"]), both,
                             agg([t["net_r"] for t in d["stop"]]), agg([t["net_r"] for t in d["target"]]))
            out.append(line)
            if flip:
                flips.append("CC %s / %s" % (name, label))
    return out, flips, len(bars)


def main():
    head = ("| sim / slice | trades (stop-first) | bars holding both | mean net R stop-first | mean net R target-first "
            "| gap R (target minus stop) | sign flips |")
    sep = "|---|---|---|---|---|---|---|"
    parts, allflips, notes = [], [], []
    for name, fn in (("Tom (tom_bt.sim_limit_trade)", run_tom), ("Fabio v3 (manage.simulate_trade)", run_fabio),
                     ("bt_engine (CryptoCred 1h signals, 1m sim)", run_cc)):
        try:
            lines, flips, n = fn()
            parts.append("### %s\n\n%s\n%s\n%s\n" % (name, head, sep, "\n".join(lines)))
            allflips += flips
            notes.append("%s: input size %d" % (name, n))
        except Exception as e:                      # fail closed: a missing sim is reported, not skipped
            parts.append("### %s\n\nNOT RUN: %s: %s\n" % (name, type(e).__name__, e))
            notes.append("%s: NOT RUN" % name)
    verdict = ("Verdict: %d slice(s) change the sign of mean net R between the stop-first and target-first bounds: %s."
               % (len(allflips), "; ".join(allflips) if allflips else "none"))
    md = ("# Intrabar stop/target ordering bounds (T10-F2, C05)\n\nDEV/VALIDATION only, no HOLDOUT. Force per run: "
          "stop-first (stop wins a bar holding both, the shipped default) vs target-first. Bars holding both = trades "
          "whose exit differs between the two orderings (Tom: sum of the sim's own `ambiguous` counter). Gap R = mean "
          "net R target-first minus stop-first; trade sets can differ between modes (one-at-a-time busy window), as "
          "in the published runs. Tight slice = stop distance < 0.15% of entry (OURS threshold, from the card). Fill "
          "bar: all three sims test only the stop there, so fill-bar ambiguity is not in these bounds. Fabio v3: the "
          "four selection.json cells at 2 bps, windows 2024-12-02..2026-06-25. Tom: rows with t < 2026-06-26, base "
          "fees. bt_engine: CryptoCred maker_entry, dev span (first 70% of bars).\n\n"
          + "\n".join(parts) + "\n" + "\n".join("- " + n for n in notes) + "\n\n" + verdict + "\n")
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(md)


if __name__ == "__main__":
    main()
