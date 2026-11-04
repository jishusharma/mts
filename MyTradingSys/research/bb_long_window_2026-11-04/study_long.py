"""bb_long_window_2026-11-04: LONG-window (spot 2017-08..2024-06) DEV pass for BOTH Bollinger studies, PRE_REG_LONG.md.

Study A = bb_range_to_range_2026-11-04 (15m/1h/4h, signal + next-open "retest" entries, by session).
Study B = bb_range_retest_2026-11-04 (15m, re-entry close then touch of level +- k ATR, session-range tag).
Event finding, brackets, level-arm fills, cell statistics, the session-range tag and the Holm/cluster maths are REUSED UNCHANGED from those
studies by path; the only new code is the gate wrapper (tagged-only ungated control, ONE OURS bear proxy P40) and the pooled Holm family.
Proxy P40 (OURS, coordinator d-bear-proxy-1104, never Malkan's): bear = weekly RSI14 <= 40 alone (monthly ignored) AND daily close below
SMA200, exactly as in rsi_divergence_mtf_gated_2026-11-04/study_long.py (its make_regime_at / load_spot are reused).
Passes: count (no returns), dev, val (survivors only). Spot, not spliced with futures. HOLDOUT is never loaded (loader end = window end).
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
RES = REPO / "MyTradingSys/research"


def _load(name, rel):
    sp = importlib.util.spec_from_file_location(name, RES / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


RSI = _load("rsi_long_for_bb", "rsi_divergence_mtf_gated_2026-11-04/study_long.py")   # make_regime_at(bear_proxy), load_spot, build_context
A = _load("bb_r2r_for_long", "bb_range_to_range_2026-11-04/study.py")                  # events, bracket, trades_for, cell_stats
B = _load("bb_retest_for_long", "bb_range_retest_2026-11-04/study.py")                 # level arm, session-range tag
rk, splits, DAY = A.rk, A.splits, A.DAY
SPOT_ROOT = RSI.SPOT_ROOT
LONG_START = RSI.LONG_START
ARM_P40 = "bearP40"
CONFIRM = A.CONFIRM_SESSIONS
FAM_A = len(CONFIRM) * len(A.ENTRIES)                 # 6 range cells (15m x 3 sessions x 2 entries)
FAM_B = len(CONFIRM) * len(B.K_GRID)                  # 9 range cells (15m x 3 sessions x 3 k)
FAMILY_PRIMARY = FAM_A + FAM_B                        # 15
FAMILY_M = 2 * FAMILY_PRIMARY                         # 30 = primary 15 + the same 15 cells under P40
MIN_N, MIN_DAYS = A.MIN_N, A.MIN_DAYS


def gate_pass(label, reg_p, reg_x, t):
    """Does an event whose signal bar closes at t (ms) belong to gate `label`? 'all' = every TAGGED event (regime known), so range / bull /
    bear / bearP40 / all share one time span (the first ~65 weeks have no SMA200 / monthly RSI and are dropped from every row)."""
    r = reg_p(t)
    if label == "all":
        return r is not None
    if label == ARM_P40:
        return reg_x(t) == "bear"
    return r == label


def window(pass_):
    if pass_ == "val":
        return A.ms(splits.VALIDATION_START), A.ms(splits.VALIDATION_END)
    return A.ms(RSI.pd.Timestamp(LONG_START)), A.ms(splits.DEV_END)


def run_a(d1, reg_p, reg_x, pass_, lo_ms, hi_ms, surv, root):
    """Study A rows: gate x side x width x TF x session x entry, as the original plus gate bearP40; ungated = tagged events of all regimes."""
    rows = []
    for tf in A.TFS:
        bars = d1 if tf == "1d" else RSI.load_spot(tf, hi_ms, root)
        evs = A.find_events(bars, A.TF_MS[tf])
        for e in evs:
            e["session"] = A.session_of_event(e)
        for entry in A.ENTRIES:
            gates = ("range", "all", "bull", "bear", ARM_P40)
            pool = {g: A.trades_for([e for e in evs if gate_pass(g, reg_p, reg_x, e["t_close"])], bars, entry, lo_ms=lo_ms, hi_ms=hi_ms)[0]
                    for g in gates}
            for gate in gates:
                inwin = [e for e in evs if lo_ms <= e["t_close"] < hi_ms and gate_pass(gate, reg_p, reg_x, e["t_close"])]
                for side in A.SIDES:
                    for sess in ("ALL",) + A.SESSIONS:
                        for wide in (None, True, False):
                            if pass_ == "val" and not (gate in ("range", ARM_P40) and side == "both" and wide is None
                                                       and [gate, tf, sess, entry] in surv):
                                continue
                            sel = A.select(pool[gate], side, sess, wide)
                            sg = [e for e in inwin if (side == "both" or e["side"] == (1 if side == "long" else -1))
                                  and (sess == "ALL" or e["session"] == sess) and (wide is None or e["wide"] == wide)]
                            row = {"study": "A_r2r", "tf": tf, "session": sess, "entry": entry, "gate": gate, "side": side, "k": "",
                                   "tag": "", "width": "any" if wide is None else ("wide" if wide else "narrow"), "signals": len(sg)}
                            if pass_ == "count":
                                row.update({"n": len(sel), "days": len({x["day"] for x in sel}),
                                            "median_stop_pct": float(np.median([x["stop_pct"] for x in sel])) if sel else float("nan")})
                            else:
                                row.update(A.cell_stats(sel))
                                if gate in ("range", ARM_P40) and side == "both" and wide is None:
                                    ung = A.select(pool["all"], "both", sess)
                                    if sel and ung:
                                        d, dse = rk.cluster_diff([x["gross"] for x in sel], [x["day"] for x in sel],
                                                                 [x["gross"] for x in ung], [x["day"] for x in ung])
                                        row.update({"vs_ungated": d, "vs_ungated_se": dse, "vs_ungated_t": rk.t_stat(d, dse)})
                            rows.append(row)
        print("A", tf, "done", file=sys.stderr, flush=True)
    return rows


def _regime_variant(evs, reg_p, reg_x, variant):
    for e in evs:
        e["regime"] = (reg_x(e["t_close"]) if variant == ARM_P40 else reg_p(e["t_close"])) or "none"


def run_b(pass_, lo_ms, hi_ms, reg_p, reg_x, root, surv):
    """Study B rows (15m): gate {range, all(tagged-regime), bearP40} x session x tag x side x k. Two builds over the same events:
    build_trades reads e['regime'], so the primary variant sets it from reg_p and the P40 variant from reg_x; fills do not depend on it."""
    bars = RSI.load_spot("15m", hi_ms, root)
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    tags = B.session_range_tags(bars, B.TF_MS)
    evs = A.find_events(bars, B.TF_MS)
    for e in evs:
        e["session"] = rk.session_tag(e["t_close"] / 1000)
        e["tag"] = tags[e["i"]]
    rows = []
    for k in B.K_GRID:
        trs = {}
        for variant in ("primary", ARM_P40):
            _regime_variant(evs, reg_p, reg_x, variant)
            trs[variant] = B.build_trades(evs, bars, k, lo_ms, hi_ms)       # also stores e['fill_<k>']
        _regime_variant(evs, reg_p, reg_x, "primary")
        pri_all = [x for x in trs["primary"] if x["regime"] != "none"]        # ungated control = tagged-regime events only
        inwin = [e for e in evs if lo_ms <= e["t_close"] < hi_ms]
        for sess in ("ALL",) + B.SESSIONS:
            for gate in ("range", "all", ARM_P40):
                for tag in ("tagged", "untagged", "any"):
                    for side in ("both", "long", "short"):
                        if pass_ == "val" and not (gate in ("range", ARM_P40) and tag == "tagged" and side == "both" and [gate, sess, k] in surv):
                            continue
                        src = pri_all if gate == "all" else (trs[ARM_P40] if gate == ARM_P40 else trs["primary"])
                        gname = "bear" if gate == ARM_P40 else gate
                        s = [x for x in src if (gate == "all" or x["regime"] == gname)
                             and (sess == "ALL" or x["session"] == sess) and (tag == "any" or (x["tag"] if tag == "tagged" else not x["tag"]))
                             and (side == "both" or x["side"] == (1 if side == "long" else -1))]
                        ev_s = [e for e in inwin if gate_pass(gate, reg_p, reg_x, e["t_close"]) and (sess == "ALL" or e["session"] == sess)
                                and (tag == "any" or (e["tag"] if tag == "tagged" else not e["tag"]))
                                and (side == "both" or e["side"] == (1 if side == "long" else -1))]
                        row = {"study": "B_retest", "tf": "15m", "session": sess, "entry": "level", "gate": gate, "side": side, "k": k,
                               "tag": tag, "width": "", "signals": len(ev_s), "reentered": sum(1 for e in ev_s if B.reentered(ohlc, e)),
                               "fills": sum(1 for e in ev_s if e.get("fill_" + str(k)) is not None)}
                        row["fill_rate"] = row["fills"] / row["signals"] if row["signals"] else float("nan")
                        if pass_ == "count":
                            row.update({"n": len(s), "days": len({x["day"] for x in s}),
                                        "median_stop_pct": float(np.median([x["stop_pct"] for x in s])) if s else float("nan")})
                        else:
                            row.update(A.cell_stats(s))
                            if gate in ("range", ARM_P40) and tag == "tagged" and side == "both":
                                ung = [x for x in pri_all if (sess == "ALL" or x["session"] == sess) and x["tag"]]
                                unt = [x for x in trs["primary"] if x["regime"] == "range" and not x["tag"] and (sess == "ALL" or x["session"] == sess)]
                                for nm, other in (("vs_ungated", ung), ("vs_untagged", unt)):
                                    if s and other:
                                        d, dse = rk.cluster_diff([x["gross"] for x in s], [x["day"] for x in s],
                                                                 [x["gross"] for x in other], [x["day"] for x in other])
                                        row.update({nm: d, nm + "_se": dse, nm + "_t": rk.t_stat(d, dse)})
                        rows.append(row)
        print("B k", k, "done", file=sys.stderr, flush=True)
    return rows


def holm_family(rows):
    """Pooled Holm over the declared family: A cells (15m x asia/london/ny x entry) and B cells (asia/london/ny x k), each under range and
    bearP40 = 30 cells; empty cells count through m. Sets holm_p and survivor on the eligible rows."""
    fam = [r for r in rows if r["tf"] == "15m" and r["session"] in CONFIRM and r["side"] == "both" and r.get("n", 0) > 0
           and r["gate"] in ("range", ARM_P40)
           and ((r["study"] == "A_r2r" and r["width"] == "any") or (r["study"] == "B_retest" and r["tag"] == "tagged"))]
    adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=FAMILY_M)
    for r, q in zip(fam, adj):
        r["holm_p"] = float(q)
        vt = r.get("vs_ungated_t", float("nan"))
        r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05 and vt == vt and vt >= 2)
    return fam


def cell_key(r):
    return [r["study"], r["gate"], r["tf"], r["session"], r["entry"] if r["study"] == "A_r2r" else r["k"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    ap.add_argument("--root", default=SPOT_ROOT)
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    surv = []
    if a.pass_ == "val":
        surv = json.loads((HERE / "dev_survivors_long.json").read_text(encoding="utf-8"))
        if not surv:
            print("no long-DEV survivors: VALIDATION not read")
            return 0
        if (HERE / "val_cells_long.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
    lo_ms, hi_ms = window(a.pass_)
    d1 = RSI.load_spot("1d", hi_ms, a.root)
    daily, wk, mo = RSI.build_context(d1, registry)
    reg_p = RSI.make_regime_at(daily, wk, mo)
    reg_x = RSI.make_regime_at(daily, wk, mo, bear_proxy=True)
    sa = [[x[1], x[2], x[3], x[4]] for x in surv if x[0] == "A_r2r"]
    sb = [[x[1], x[3], x[4]] for x in surv if x[0] == "B_retest"]
    rows = run_a(d1, reg_p, reg_x, a.pass_, lo_ms, hi_ms, sa, a.root) + run_b(a.pass_, lo_ms, hi_ms, reg_p, reg_x, a.root, sb)
    if a.pass_ == "dev":
        fam = holm_family(rows)
        (HERE / "dev_survivors_long.json").write_text(json.dumps([cell_key(r) for r in fam if r.get("survivor")]), encoding="utf-8", newline="\n")
    name = {"count": "counts_long.csv", "dev": "dev_cells_long.csv", "val": "val_cells_long.csv"}[a.pass_]
    first = ("study", "tf", "session", "entry", "gate", "side", "k", "tag", "width")
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in first, first.index(k) if k in first else 0, k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    starts = A.week_starts(lo_ms, hi_ms)
    tp, tx = [reg_p(t) for t in starts], [reg_x(t) for t in starts]
    line = (rk.regime_mix_line(tp) + f" | bear weeks: primary Malkan (weekly AND monthly <=40) {tp.count('bear')}, "
            f"proxy P40 (weekly <=40 alone, below SMA200, OURS) {tx.count('bear')}")
    (HERE / ("regime_mix_%s_long.txt" % a.pass_)).write_text(line + "\nproxy P40 mix: " + rk.regime_mix_line(tx) + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
