"""wt_c30_retest_10sym_2026-11-15: the wavetrend_c30_retest_2026-11-04 rule (WaveTrend dot in the +-53 band, RSI 40/60 or close divergence confluence,
signal-close or dot-bar-midpoint retest entry, daily-SMA200 trend gate, 12-bar exit) re-derived UNCHANGED on 10 Binance spot symbols, out of sample
2024-01-01..2026-11-14. See PRE_REG.md. Every rule function is reused by path from the 11-04 study.py (no rule edited); only the data layer, the
10-symbol pooling and the family statistics are new. Trend gate = each symbol's own daily SMA200; Malkan weekly/monthly RSI band = BTC (market regime, OURS).
Passes: --pass count (event counts, no returns), --pass run."""
import argparse
import calendar
import csv
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402

_sp = importlib.util.spec_from_file_location("wt_c30_base", REPO / "MyTradingSys/research/wavetrend_c30_retest_2026-11-04/study.py")
base = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(base)

CACHE = REPO / "runtime_data" / "wt-c30-10sym-1115"
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
DAY = 86400000
OOS_START = calendar.timegm((2024, 1, 1, 0, 0, 0)) * 1000
SPLIT_MS = calendar.timegm((2025, 7, 1, 0, 0, 0)) * 1000
OOS_END = calendar.timegm((2026, 11, 15, 0, 0, 0)) * 1000      # exclusive; last 15m bar 2026-11-14 23:45
TFS, TF_MS, SIDES, CONFS, ENTRIES = base.TFS, base.TF_MS, base.SIDES, base.CONFS, base.ENTRIES
GATES = ("all", "with", "against", "reg_bull", "reg_range", "reg_bear")
CONFIRM_CONFS = base.CONFIRM_CONFS
MIN_N, MIN_DAYS = base.MIN_N, base.MIN_DAYS
M_FAMILY = len(TFS) * len(SIDES) * len(CONFIRM_CONFS) * len(ENTRIES)      # 24
KEYS = ("tf", "side", "conf", "entry", "gate", "sym")


def load(sym, iv):
    rows = json.loads((CACHE / ("%s_%s.json" % (sym, iv))).read_text())
    return [{"t": r[0], "o": r[1], "h": r[2], "l": r[3], "c": r[4]} for r in rows]


def resample_from_15m(bars, tf):
    """Aligned complete buckets only (all sub-bars present); bar t = bucket open."""
    if tf == "15m":
        return bars
    n = TF_MS[tf] // 900000
    out, cur = [], {}
    for b in bars:
        k = b["t"] // TF_MS[tf]
        if cur.get("k") != k:
            if cur.get("cnt") == n:
                out.append(cur["bar"])
            cur = {"k": k, "cnt": 0, "bar": {"t": k * TF_MS[tf], "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"]}}
        x = cur["bar"]
        x["h"], x["l"], x["c"] = max(x["h"], b["h"]), min(x["l"], b["l"]), b["c"]
        cur["cnt"] += 1
    if cur.get("cnt") == n:
        out.append(cur["bar"])
    return out


def ctx_for(sym, wk, mo):
    d = load(sym, "1d")
    return base.make_ctx_at(([x["t"] + DAY for x in d], [x["c"] for x in d]), wk, mo)


def sym_events(sym, ctx_at, count_only):
    """{tf: {bars, ev {(side, conf): events with ctx}, tags}} for one symbol."""
    b15 = load(sym, "15m")
    out = {}
    for tf in TFS:
        bars = resample_from_15m(b15, tf)
        dots = base.dots_for(bars, tf)
        for e in dots:
            e["ctx"] = ctx_at(e["t_close"])
        res = {"bars": bars, "ev": {}, "tags": None if count_only else base.BarTags(bars, tf, ctx_at, OOS_START, OOS_END)}
        for sname, sgn in SIDES.items():
            idx, rsi = base.div_index(bars, sgn)
            side_ev = [e for e in dots if e["side"] == sgn]
            for conf in CONFS:
                res["ev"][(sname, conf)] = [e for e in side_ev if conf == "none" or (conf == "rsi" and base.rsi_ok(rsi, e["i"], sgn))
                                            or (conf == "div" and base.div_ok(idx, e["i"]))]
        out[tf] = res
    return out


def cell_trades(per_sym, tf, sname, conf, gate, entry, sym_list):
    sgn = SIDES[sname]
    trs, nsig, dg, dd = [], 0, [], []
    for s in sym_list:
        r = per_sym[s][tf]
        ge = [e for e in r["ev"][(sname, conf)] if base.event_in_gate(e["ctx"], sgn, gate)]
        t, n = base.trades_for(ge, r["bars"], entry, lo_ms=OOS_START, hi_ms=OOS_END)
        for x in t:
            x["sym"] = s
        trs += t
        nsig += n
        if r["tags"] is not None:
            g, d = r["tags"].drift(sgn, gate, "ALL")
            dg += g
            dd += d
    return trs, nsig, (dg, dd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "run"))
    a = ap.parse_args()
    count_only = a.pass_ == "count"
    wk = base.rsi_series(load("BTC", "1w"))
    mo = base.rsi_series(load("BTC", "1M"))
    per_sym, ctxs = {}, {}
    for s in SYMS:
        ctxs[s] = ctx_for(s, wk, mo)
        per_sym[s] = sym_events(s, ctxs[s], count_only)
        print(s, "done", file=sys.stderr, flush=True)
    mix = rk.regime_mix_line([ctx_for("BTC", wk, mo)(t)["regime"] for t in base.week_starts(OOS_START, OOS_END)])
    split_day = SPLIT_MS // DAY
    rows = []
    for tf in TFS:
        for sname in SIDES:
            for conf in CONFS:
                for gate in GATES:
                    for entry in ENTRIES:
                        for sl in ("ALL",) + tuple(SYMS):
                            if sl != "ALL" and not (gate == "with" and conf in CONFIRM_CONFS):
                                continue          # per-symbol rows only for the confirmatory arm (descriptive)
                            trs, nsig, drift = cell_trades(per_sym, tf, sname, conf, gate, entry, SYMS if sl == "ALL" else [sl])
                            row = dict(zip(KEYS, (tf, sname, conf, entry, gate, sl)))
                            row["signals"] = nsig
                            if count_only:
                                row.update({"n": len(trs), "days": len({x["day"] for x in trs})})
                            else:
                                row.update(base.cell_stats(trs, drift))
                                if sl == "ALL":
                                    for nm, f in (("w1", lambda x: x["day"] < split_day), ("w2", lambda x: x["day"] >= split_day)):
                                        st = base.cell_stats([x for x in trs if f(x)], None)
                                        row[nm + "_n"], row[nm + "_net"] = st["n"], st.get("net", float("nan"))
                            rows.append(row)
        print(tf, "cells done", file=sys.stderr, flush=True)
    if a.pass_ == "run":
        fam = [r for r in rows if r["gate"] == "with" and r["conf"] in CONFIRM_CONFS and r["sym"] == "ALL" and r.get("n", 0) > 0]
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=M_FAMILY)
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05 and r["excess_t"] == r["excess_t"]
                                 and r["excess_t"] >= 2 and r["w1_net"] > 0 and r["w2_net"] > 0)
        (HERE / "survivors.json").write_text(json.dumps([[r["tf"], r["side"], r["conf"], r["entry"]] for r in fam if r["survivor"]]))
    name = "counts.csv" if count_only else "cells.csv"
    cols = sorted({k for r in rows for k in r}, key=lambda k: (k not in KEYS, k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (HERE / "regime_mix.txt").write_text(mix + "\n", encoding="utf-8", newline="\n")
    print(mix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
