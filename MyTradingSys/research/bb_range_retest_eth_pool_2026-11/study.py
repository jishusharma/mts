"""bb_range_retest_eth_pool_2026-11: the frozen bb_range_retest level arm re-run on BTCUSDT + ETHUSDT USD-M futures 1m, pooled. See PRE_REG.md.

Same rule, grid and family as bb_range_retest_2026-11-04 (events, level-arm fill, bracket, session-range tag and cell stats reused by
path). New here: a per-symbol futures loader that refuses any end after DEV_END, regime context from each symbol's own spot 1d history
(the futures files start 2022-01, too short for monthly RSI(14)), and a day cluster over symbol + UTC day. Passes: count (no returns), dev.
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

_sp = importlib.util.spec_from_file_location("bb_retest_src", REPO / "MyTradingSys/research/bb_range_retest_2026-11-04/study.py")
rt = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(rt)
prev, sib = rt.prev, rt.prev._sib

DAY = 86400000
FUT_ROOT = Path("F:/MTS/data/tom_raw/klines")          # USD-M futures 1m (BTC), <SYM>-1m-<YYYY-MM>[-DD].csv
ETH_ROOT = Path("F:/MTS/data/tom_raw/klines_eth")      # ETH 1m, moved out of klines 2026-11-05 (duplicate open_time vs BTC)


def root_for(sym):
    return ETH_ROOT if sym == "ETHUSDT" else FUT_ROOT


SPOT_1D_ROOT = Path("F:/MTS/Dumps/backtest/spot_2017")  # <SYM>/1d/klines/*.csv, context only (regime)
SYMBOLS = ("BTCUSDT", "ETHUSDT")
DEV_START_MS, DEV_END_MS = prev.ms(splits.DEV_START), prev.ms(splits.DEV_END)
REPRO_N_TOL = 0.25           # OURS: BTC futures n within 25 % of the shipped spot n per family cell (PRE_REG)
BIN_RT = 2 * fees.BINANCE_TAKER * 100.0   # SOURCED fees.py: Binance USD-M taker both legs, % round trip (second cost column)
MIN_N, MIN_DAYS = rt.MIN_N, rt.MIN_DAYS


def cluster_key(sym, day):
    """One cluster per (symbol, UTC day): two symbols on one day are two clusters (PRE_REG)."""
    return SYMBOLS.index(sym) * 10 ** 6 + int(day) if sym in SYMBOLS else hash((sym, int(day)))


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if row and row[0].isdigit():
                yield row


def load_sym_1m(sym, end_ms, root=None):
    """1m bars of one symbol with open time < end_ms. Refuses end_ms after DEV_END (VALIDATION/HOLDOUT never loaded); files whose
    period starts at or after end_ms are not opened."""
    if end_ms > DEV_END_MS:
        raise ValueError("end %d after DEV_END %d: VALIDATION/HOLDOUT not loadable here" % (end_ms, DEV_END_MS))
    root = Path(root) if root is not None else root_for(sym)
    end_day = datetime.fromtimestamp(end_ms / 1000, timezone.utc).strftime("%Y-%m-%d")
    bars = {}
    for p in sorted(root.glob(sym + "-1m-*.csv")):
        per = p.stem.split("-1m-")[1]
        if (per + "-01" if len(per) == 7 else per) >= end_day:
            continue
        for r in _rows(p):
            t = int(r[0])
            if t < end_ms:
                bars[t] = {"t": t, "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5])}
    return [bars[k] for k in sorted(bars)]


def spot_context(sym, end_ms):
    """(daily, weekly_rsi, monthly_rsi) in the shape research_kit.regime_tag reads, from spot 1d bars with open < end_ms. Weekly bars =
    Monday 00:00 UTC buckets, monthly = calendar months; the last bucket is dropped by rsi_series (as the source study)."""
    d = {}
    for p in sorted((SPOT_1D_ROOT / sym / "1d" / "klines").glob("*.csv")):
        for r in _rows(p):
            t = int(r[0])
            if t < end_ms:
                d[t] = float(r[4])
    ts = sorted(d)
    daily = ([t + DAY for t in ts], [d[t] for t in ts])
    wk, mo = {}, {}
    for t in ts:
        dd = t // DAY
        wk[(dd - (dd - 4) % 7) * DAY] = d[t]
        dt = datetime.fromtimestamp(t / 1000, timezone.utc)
        mo[int(datetime(dt.year, dt.month, 1, tzinfo=timezone.utc).timestamp() * 1000)] = d[t]
    w = [{"t": k, "c": wk[k]} for k in sorted(wk)]
    m = [{"t": k, "c": mo[k]} for k in sorted(mo)]
    return daily, sib.rsi_series(w), sib.rsi_series(m)


def symbol_trades(sym, registry):
    """Events (with session, tag, regime) and per-k trades for one symbol in DEV; trade 'day' = cluster_key(sym, UTC day)."""
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    bars_1m = load_sym_1m(sym, DEV_END_MS)
    assert bars_1m and bars_1m[-1]["t"] < DEV_END_MS
    regime_at = prev.make_regime_at(*spot_context(sym, DEV_END_MS))
    bars = resample(bars_1m, rt.TF, registry)
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    tags = rt.session_range_tags(bars, rt.TF_MS)
    evs = prev.find_events(bars, rt.TF_MS)
    for e in evs:
        e["session"] = rk.session_tag(e["t_close"] / 1000)
        e["tag"] = tags[e["i"]]
        e["regime"] = regime_at(e["t_close"]) or "none"
        e["sym"] = sym
    trs = {}
    for k in rt.K_GRID:
        trs[k] = rt.build_trades(evs, bars, k, DEV_START_MS, DEV_END_MS)
        for x in trs[k]:
            x["day"] = cluster_key(sym, x["day"])
    inwin = [e for e in evs if DEV_START_MS <= e["t_close"] < DEV_END_MS]
    for e in inwin:
        e["reentered"] = rt.reentered(ohlc, e)
    weeks = [regime_at(t) for t in prev.week_starts(DEV_START_MS, DEV_END_MS)]
    return inwin, trs, weeks


def cell_rows(label, inwin, trs, pass_):
    rows = []
    for k in rt.K_GRID:
        for sess in ("ALL",) + rt.SESSIONS:
            for gate in ("range", "all"):
                for tag in ("tagged", "untagged", "any"):
                    for side in ("both", "long", "short"):
                        s = rt.sel(trs[k], sess, gate, tag, side)
                        ev_s = [e for e in inwin if (sess == "ALL" or e["session"] == sess) and (gate == "all" or e["regime"] == gate)
                                and (tag == "any" or (e["tag"] if tag == "tagged" else not e["tag"]))
                                and (side == "both" or e["side"] == (1 if side == "long" else -1))]
                        row = {"symbol": label, "session": sess, "k": k, "gate": gate, "tag": tag, "side": side, "signals": len(ev_s),
                               "reentered": sum(1 for e in ev_s if e["reentered"]),
                               "fills": sum(1 for e in ev_s if e.get("fill_" + str(k)) is not None)}
                        row["fill_rate"] = row["fills"] / row["signals"] if row["signals"] else float("nan")
                        if pass_ == "count":
                            row.update({"n": len(s), "days": len({x["day"] for x in s}),
                                        "median_stop_pct": float(np.median([x["stop_pct"] for x in s])) if s else float("nan")})
                        else:
                            row.update(prev.cell_stats(s))
                            if s:
                                row["net_bin"] = row["gross"] - BIN_RT
                                row["ci_lo_bin"], row["ci_hi_bin"] = row["net_bin"] - 1.96 * row["se"], row["net_bin"] + 1.96 * row["se"]
                            if gate == "range" and tag == "tagged" and side == "both":
                                for nm, other in (("vs_ungated", rt.sel(trs[k], sess, "all", "tagged")),
                                                  ("vs_untagged", rt.sel(trs[k], sess, "range", "untagged"))):
                                    if s and other:
                                        d, dse = rk.cluster_diff([x["gross"] for x in s], [x["day"] for x in s],
                                                                 [x["gross"] for x in other], [x["day"] for x in other])
                                        row.update({nm: d, nm + "_se": dse, nm + "_t": rk.t_stat(d, dse)})
                        rows.append(row)
    return rows


def holm_family(rows, label):
    fam = [r for r in rows if r["symbol"] == label and r["gate"] == "range" and r["tag"] == "tagged" and r["side"] == "both"
           and r["session"] in rt.CONFIRM_SESSIONS and r.get("n", 0) > 0]
    adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=len(rt.CONFIRM_SESSIONS) * len(rt.K_GRID))
    for r, q in zip(fam, adj):
        r["holm_p"] = float(q)
        vt = r.get("vs_ungated_t", float("nan"))
        r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05 and vt == vt and vt >= 2)
    return fam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default=",".join(SYMBOLS))
    ap.add_argument("--pass", dest="pass_", default="dev", choices=("count", "dev"))
    a = ap.parse_args()
    syms = [s for s in a.symbols.split(",") if s]
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    per, rows, weeks_all = {}, [], []
    for sym in syms:
        per[sym] = symbol_trades(sym, registry)
        rows += cell_rows(sym, per[sym][0], per[sym][1], a.pass_)
        weeks_all += per[sym][2]
        print(sym, "done", file=sys.stderr, flush=True)
    if len(syms) > 1:
        inwin = [e for s in syms for e in per[s][0]]
        trs = {k: [x for s in syms for x in per[s][1][k]] for k in rt.K_GRID}
        rows += cell_rows("POOL", inwin, trs, a.pass_)
    if a.pass_ == "dev":
        surv = []
        for label in syms + (["POOL"] if len(syms) > 1 else []):
            surv += [[label, r["session"], r["k"]] for r in holm_family(rows, label) if r.get("survivor")]
        with open(HERE / "dev_survivors.json", "w", newline="\n") as f:
            json.dump(surv, f)
    name = {"count": "counts.csv", "dev": "dev_cells.csv"}[a.pass_]
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("symbol", "session", "k", "gate", "tag", "side"), k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    lines = [s + " " + rk.regime_mix_line(per[s][2]) for s in syms] + ["POOL " + rk.regime_mix_line(weeks_all)]
    (HERE / ("regime_mix_%s.txt" % a.pass_)).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
