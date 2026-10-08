"""
MyTradingSys/backtest/layers/fabio/run_of_model.py - driver for the Fabio conditional-model test (see fabio_of_model).

Usage: python -m MyTradingSys.backtest.layers.fabio.run_of_model [--data F:\\MTS\\data\\orderflow_1m] [--out F:\\MTS\\data\\fabio_of]
Writes results.json + tables.md in --out (bulk output stays off C:). Chronological 70/30 split by DAY over the days that
have a full 30-day prior big-trade threshold window (thr_days >= 30). PBO = ref_pbo_cscv over the variant grid on IS daily
net-R (no-trade day = 0, S=12), same as FABIO_L1.
"""
import argparse
import itertools
import json
from bisect import bisect_left
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import fabio_of_model as M
from MyTradingSys.backtest.layers.fabio.orderflow_bars import load_days
from MyTradingSys.backtest.layers.fabio.run_backtest import pbo_from_columns

TFS = (5, 15)
PCTS = ("99", "999")
KS = (1.5, 2.5)
ENTRIES = ("mkt", "limit")
MGMTS = ("plain", "trail")
FLOORS = (0.0, 0.0015)   # min stop distance as fraction of price: 0 = spec tight stop, 0.15% = fee-survivable
MIN_RISK_FRAC = 0.0002   # trades whose stop is tighter than 0.02% of price (~$14) are skipped as untradeable
MIN_THR_DAYS = 30


def day_of(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).date().isoformat()


def prepare(bars):
    times = [b["t"] for b in bars]
    day_starts = sorted({t // M.DAY_MS * M.DAY_MS for t in times})
    seq = M.session_sequence(day_starts)
    info = []
    for name, s, e in seq:
        i0, i1 = bisect_left(times, s), bisect_left(times, e)
        full = (i1 - i0) == (e - s) // 60000
        info.append({"name": name, "s": s, "e": e, "i0": i0, "i1": i1, "full": full})
    return times, info


def collect_events(bars, times, info, flow, lim=False):
    """{(tf,pct,k): [events]} plus state counts. Events carry session name/day, first/last 1m idx, hvns."""
    prof_lv = {}
    for idx in range(len(info)):
        s = info[idx]
        if s["full"] and s["i1"] > s["i0"]:
            prof_lv[idx] = M.profile_levels(M.build_profile(bars[s["i0"]:s["i1"]], flow))
    state_counts = {}
    tfdata = {}
    for tf in TFS:
        tb = M.build_tf_bars(bars, tf)
        tfdata[tf] = (tb, M.mean_abs_delta_prev(tb), [x["t"] for x in tb])
    out = {}
    combos = [(tf, p, k) for tf in TFS for p in (PCTS if flow == "true" else ("99",)) for k in KS]
    for idx in range(1, len(info)):
        cur, prv = info[idx], info[idx - 1]
        lv = prof_lv.get(idx - 1)
        if not (cur["full"] and prv["full"] and lv):
            continue
        if bars[cur["i0"]]["thr_days"] < MIN_THR_DAYS:
            continue
        st_i = bisect_left(times, cur["s"] + (M.STATE_MIN - 1) * 60000)
        if st_i >= cur["i1"] or times[st_i] != cur["s"] + (M.STATE_MIN - 1) * 60000:
            continue
        state = M.session_state(bars[st_i]["c"], lv)
        state_counts[(cur["name"], state)] = state_counts.get((cur["name"], state), 0) + 1
        levels = M.location_list(lv)
        for tf, pct, k in combos:
            tb, avg, tts = tfdata[tf]
            lo = bisect_left(tts, cur["s"] + M.STATE_MIN * 60000)
            hi = bisect_left(tts, cur["e"] - tf * 60000 + 1)
            if state == "balance":
                evs = M.fade_events(tb, avg, levels, lo, hi, k, pct, flow)
            else:
                fn = M.break_limit_events if lim else M.break_events
                evs = fn(tb, avg, levels, lo, hi, 1 if state == "imb_up" else -1, k, pct, flow)
            for e in evs:
                b = tb[e["bi"]]
                e.update({"session": cur["name"], "state": state, "day": day_of(cur["s"]), "first": b["i1"],
                          "last": cur["i1"] - 1, "hvns": lv["hvns"], "t": b["t_end"],
                          "fill_tf": (M.RETEST_BARS if (lim and e["model"] == "imb_break") else M.FILL_TF_BARS)})
                out.setdefault((tf, pct, k), []).append(e)
    return out, state_counts


def simulate(bars, events, tf, entry, mgmt, floor=0.0):
    trades, busy_until = [], {}
    for e in sorted(events, key=lambda x: x["t"]):
        if e["first"] > e["last"] or bars[e["first"]]["t"] != e["t"]:
            continue
        key = (e["day"], e["session"])
        if e["first"] <= busy_until.get(key, -1):
            continue
        mode = entry if (entry == "limit" and e["model"] == "balance_fade") else "mkt"
        r = M.simulate_trade(bars, e["first"], e["last"], e["side"], mode, e["level"], e["stop"], e["hvns"],
                             mgmt == "trail", M.FILL_TF_BARS * tf, floor)
        if r is None or r["risk"] < MIN_RISK_FRAC * r["entry"]:
            continue
        busy_until[key] = r["exit_idx"]
        r.update({"day": e["day"], "session": e["session"], "model": e["model"], "kind": e["kind"], "side": e["side"]})
        trades.append(r)
    return trades


def _f(x, spec="{:+.3f}"):
    return "-" if x is None else spec.format(x)


def render_tables(res):
    L = []
    L.append("| flow | model | scope | chosen variant (tf, big pct, k, entry, mgmt, min-stop) | IS n / exp net R | OOS n | win | avg gross R | exp net R | PF | maxDD R | BE share | PBO | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in res["rows"]:
        if "oos" not in r:
            L.append(f"| {r['flow']} | {r['model']} | {r['scope']} | - | - | - | - | - | - | - | - | - | {_f(r['pbo'], '{:.2f}')} | {r['verdict']} |")
            continue
        o, i = r["oos"], r["is"]
        v = r["variant"]
        vt = f"{v[0]}m, p{v[1]}, k{v[2]}, {v[3]}, {v[4]}, floor {v[5]}"
        L.append(f"| {r['flow']} | {r['model']} | {r['scope']} | {vt} | {i['n']} / {_f(i['exp_net_R'])} | {o['n']} | "
                 f"{_f(o['win'], '{:.0%}')} | {_f(o['avg_gross_R'])} | {_f(o['exp_net_R'])} | {_f(o['pf'], '{:.2f}')} | "
                 f"{_f(o['max_dd_R'], '{:.1f}')} | {_f(o['be_share'], '{:.0%}')} | {_f(r['pbo'], '{:.2f}')} | {r['verdict']} |")
    L.append("")
    L.append("Grid summary (pooled over ALL variants of the group; OOS only): variants with n>=30 / of those with net exp > 0 / median OOS avg gross R / median OOS net exp R")
    L.append("")
    L.append("| flow | model | scope | variants | OOS n>=30 | net exp > 0 | median gross R | median net R |")
    L.append("|---|---|---|---|---|---|---|---|")
    import statistics
    grp = {}
    for g in res["grid"]:
        grp.setdefault((g["flow"], g["model"], g["scope"]), []).append(g["oos"])
    for (fl, mo, sc), lst in grp.items():
        ok = [x for x in lst if x["n"] >= 30]
        pos = [x for x in ok if x["exp_net_R"] > 0]
        gr = [x["avg_gross_R"] for x in lst if x["n"] >= 30]
        ne = [x["exp_net_R"] for x in lst if x["n"] >= 30]
        L.append(f"| {fl} | {mo} | {sc} | {len(lst)} | {len(ok)} | {len(pos)} | "
                 f"{_f(statistics.median(gr) if gr else None)} | {_f(statistics.median(ne) if ne else None)} |")
    return chr(10).join(L) + chr(10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"F:\MTS\data\orderflow_1m")
    ap.add_argument("--out", default=r"F:\MTS\data\fabio_of")
    ap.add_argument("--min-thr-days", type=int, default=30, help="smoke tests only; the real run needs 30")
    a = ap.parse_args()
    global MIN_THR_DAYS
    MIN_THR_DAYS = a.min_thr_days
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bars = load_days(a.data)
    times, info = prepare(bars)
    days = sorted({day_of(b["t"]) for b in bars if b["thr_days"] >= MIN_THR_DAYS})
    n_is = int(len(days) * 0.7)
    is_days, oos_days = days[:n_is], days[n_is:]
    is_set = set(is_days)
    print(f"{len(bars)} bars, {len(days)} analysis days ({days[0]}..{days[-1]}), IS {len(is_days)} / OOS {len(oos_days)}", flush=True)

    variants = {}   # (flow, tf, pct, k, entry, mgmt) -> trades
    counts = {}
    for flow in ("true", "proxy"):
        evs, sc = collect_events(bars, times, info, flow)
        counts[flow] = {f"{k[0]}|{k[1]}": v for k, v in sc.items()}
        for (tf, pct, k), ev in evs.items():
            for entry, mgmt, floor in itertools.product(ENTRIES, MGMTS, FLOORS):
                variants[(flow, tf, pct, k, entry, mgmt, floor)] = simulate(bars, ev, tf, entry, mgmt, floor)
        print(f"{flow}: events done", flush=True)

    scopes = {"all": None, "ny": "ny", "asia": "asia", "london": "london"}
    models = {"balance_fade": ("balance_fade",), "imb_break": ("imb_break",), "combined": ("balance_fade", "imb_break")}
    results = {"days": {"is": [is_days[0], is_days[-1], len(is_days)], "oos": [oos_days[0], oos_days[-1], len(oos_days)]},
               "state_counts": counts, "rows": [], "grid": []}

    def pick(trs, mset, scope):
        return [t for t in trs if t["model"] in mset and (scope is None or t["session"] == scope)]

    for flow in ("true", "proxy"):
        keys = [k for k in variants if k[0] == flow]
        for mname, mset in models.items():
            for sname, scope in scopes.items():
                cols, per = [], {}
                for k in keys:
                    trs = pick(variants[k], mset, scope)
                    is_t = [t for t in trs if t["day"] in is_set]
                    oos_t = [t for t in trs if t["day"] not in is_set]
                    per[k] = (is_t, oos_t)
                    d = {}
                    for t in is_t:
                        d[t["day"]] = d.get(t["day"], 0.0) + t["net_R"]
                    cols.append([d.get(x, 0.0) for x in is_days])
                pbo = pbo_from_columns(cols, S=12) if any(any(c) for c in cols) else None
                qual = [(k, M.trade_stats([t["net_R"] for t in per[k][0]])) for k in keys if len(per[k][0]) >= 20]
                for k in keys:
                    i_s = M.trade_stats([t["net_R"] for t in per[k][0]], [t["gross_R"] for t in per[k][0]],
                                        [t["reason"] for t in per[k][0]])
                    o_s = M.trade_stats([t["net_R"] for t in per[k][1]], [t["gross_R"] for t in per[k][1]],
                                        [t["reason"] for t in per[k][1]])
                    results["grid"].append({"flow": flow, "model": mname, "scope": sname, "variant": list(k[1:]),
                                            "is": i_s, "oos": o_s})
                row = {"flow": flow, "model": mname, "scope": sname, "pbo": pbo, "n_variants": len(keys)}
                if qual:
                    kb, sb = max(qual, key=lambda x: x[1]["exp_net_R"])
                    o_t = per[kb][1]
                    row.update({"variant": list(kb[1:]), "is": sb,
                                "oos": M.trade_stats([t["net_R"] for t in o_t], [t["gross_R"] for t in o_t],
                                                     [t["reason"] for t in o_t])})
                    n_oos = row["oos"]["n"]
                    if n_oos < 30:
                        row["verdict"] = "insufficient n"
                    elif row["oos"]["exp_net_R"] > 0 and pbo is not None and pbo < 0.5:
                        row["verdict"] = "edge"
                    else:
                        row["verdict"] = "no edge"
                else:
                    row["verdict"] = "insufficient n (no variant with >= 20 IS trades)"
                results["rows"].append(row)
    (out / "tables.md").write_text(render_tables(results), encoding="utf-8", newline=chr(10))
    (out / "results.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8", newline="\n")
    print("wrote", out / "results.json")


if __name__ == "__main__":
    main()
