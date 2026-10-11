"""
MyTradingSys/backtest/layers/fabio/run_of_model_v2.py - Fabio conditional model with the Deribit BTC-PERPETUAL cost model.

Same state/location/trigger as run_of_model (see fabio_of_model), different execution:
  * entry 'limit' = resting limit AT the level (maker, 0 bp, fees.py DERIBIT_MAKER), fills only if price trades through the
    level by 1 tick (fades: within 3 tf bars of the trigger; breaks: limit at the broken level right after the aggression
    bar, within 6 tf bars, no retest-hold information); entry 'mkt' = taker 5 bps at the next open (breaks: after the
    retest holds).
  * target = resting limit (maker; needs 1 tick through); stop / breakeven / trail / session-end exits = market (taker).
  * slippage 2 bps on each taker leg in the headline (net at 0 / 2 / 5 bps also reported).
  * minimum stop distance floor {0 (spec tight stop), 0.15, 0.3, 0.5}% of price; target stays min(3R, next HVN/POC >= 1R).
Fill rate = fills / limit signals not blocked by an open position.
Output (off C:): results_v2.json + tables_v2.md in --out.
"""
import argparse
import itertools
import json
import statistics
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import fabio_of_model as M
from MyTradingSys.backtest.layers.fabio import run_of_model as R1
from MyTradingSys.backtest.layers.fabio.orderflow_bars import load_days
from MyTradingSys.backtest.layers.fabio.run_backtest import pbo_from_columns

FLOORS = (0.0, 0.0015, 0.003, 0.005)
SLIP = 0.0002
KEYS_SLIP = (0.0, 0.0002, 0.0005)


def simulate2(bars, events, tf, entry, mgmt, floor):
    trades, busy, att, fills = [], {}, 0, 0
    for e in sorted(events, key=lambda x: x["t"]):
        if e["first"] > e["last"] or bars[e["first"]]["t"] != e["t"]:
            continue
        key = (e["day"], e["session"])
        if e["first"] <= busy.get(key, -1):
            continue
        att += 1
        r = M.simulate_trade(bars, e["first"], e["last"], e["side"], entry, e["level"], e["stop"], e["hvns"],
                             mgmt == "trail", e["fill_tf"] * tf, floor)
        if r is None:
            continue
        if r["risk"] < R1.MIN_RISK_FRAC * r["entry"]:
            continue
        fills += 1
        busy[key] = r["exit_idx"]
        r.update({"day": e["day"], "session": e["session"], "model": e["model"], "kind": e["kind"], "side": e["side"]})
        trades.append(r)
    return trades, att, fills


def stats(trs, slip=SLIP):
    net = [M.net_at(t, slip) for t in trs]
    st = M.trade_stats(net, [t["gross_R"] for t in trs], [t["reason"] for t in trs])
    st["fee_drag_R"] = (st["avg_gross_R"] - st["exp_net_R"]) if st["n"] else None
    st["net_0bps"] = (sum(M.net_at(t, 0.0) for t in trs) / len(trs)) if trs else None
    st["net_5bps"] = (sum(M.net_at(t, 0.0005) for t in trs) / len(trs)) if trs else None
    return st


def _f(x, spec="{:+.3f}"):
    return "-" if x is None else spec.format(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"F:\MTS\data\orderflow_1m")
    ap.add_argument("--out", default=r"F:\MTS\data\fabio_of2")
    ap.add_argument("--min-thr-days", type=int, default=30)
    ap.add_argument("--no-pbo", action="store_true")
    a = ap.parse_args()
    R1.MIN_THR_DAYS = a.min_thr_days
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bars = load_days(a.data)
    times, info = R1.prepare(bars)
    days = sorted({R1.day_of(b["t"]) for b in bars if b["thr_days"] >= a.min_thr_days})
    n_is = int(len(days) * 0.7)
    is_days, oos_days = days[:n_is], days[n_is:]
    is_set = set(is_days)
    print(f"{len(bars)} bars, {len(days)} days {days[0]}..{days[-1]}, IS {len(is_days)} / OOS {len(oos_days)}", flush=True)

    ev_m, sc = R1.collect_events(bars, times, info, "true", lim=False)
    ev_l, _ = R1.collect_events(bars, times, info, "true", lim=True)
    print("events done", flush=True)
    variants, fillstat = {}, {}
    for mode, evs in (("mkt", ev_m), ("limit", ev_l)):
        for (tf, pct, k), ev in evs.items():
            for mgmt, floor in itertools.product(R1.MGMTS, FLOORS):
                key = (tf, pct, k, mode, mgmt, floor)
                trs, att, fl = simulate2(bars, ev, tf, mode, mgmt, floor)
                variants[key] = trs
                fillstat[key] = (att, fl)
    print(f"{len(variants)} variants simulated", flush=True)

    models = {"balance_fade": ("balance_fade",), "imb_break": ("imb_break",), "combined": ("balance_fade", "imb_break")}
    scopes = {"all": None, "ny": "ny"}
    res = {"days": {"is": [is_days[0], is_days[-1], len(is_days)], "oos": [oos_days[0], oos_days[-1], len(oos_days)]},
           "state_counts": {f"{k[0]}|{k[1]}": v for k, v in sc.items()}, "rows": [], "grid": []}
    keys = list(variants)

    def pick(trs, mset, scope):
        return [t for t in trs if t["model"] in mset and (scope is None or t["session"] == scope)]

    for mname, mset in models.items():
        for sname, scope in scopes.items():
            per, cols = {}, []
            for k in keys:
                trs = pick(variants[k], mset, scope)
                is_t = [t for t in trs if t["day"] in is_set]
                oos_t = [t for t in trs if t["day"] not in is_set]
                per[k] = (is_t, oos_t)
                d = {}
                for t in is_t:
                    d[t["day"]] = d.get(t["day"], 0.0) + M.net_at(t, SLIP)
                cols.append([d.get(x, 0.0) for x in is_days])
            pbo = None if a.no_pbo else pbo_from_columns(cols, S=12)
            for k in keys:
                att, fl = fillstat[k]
                res["grid"].append({"model": mname, "scope": sname, "variant": list(k), "is": stats(per[k][0]),
                                    "oos": stats(per[k][1]), "fill_rate_all": (fl / att if att else None)})
            qual = [(k, stats(per[k][0])) for k in keys if len(per[k][0]) >= 30]
            row = {"model": mname, "scope": sname, "pbo": pbo, "n_variants": len(keys)}
            if qual:
                kb, sb = max(qual, key=lambda x: x[1]["exp_net_R"])
                o = stats(per[kb][1])
                row.update({"variant": list(kb), "is": sb, "oos": o,
                            "fill_rate": (fillstat[kb][1] / fillstat[kb][0]) if fillstat[kb][0] else None})
                if o["n"] < 30:
                    row["verdict"] = "insufficient n"
                elif o["exp_net_R"] > 0 and pbo is not None and pbo < 0.5:
                    row["verdict"] = "edge" if o["net_5bps"] > 0 else "edge at 2 bps only (fails 5 bps stress)"
                else:
                    row["verdict"] = "no edge"
            else:
                row["verdict"] = "insufficient n (no variant with >= 30 IS trades)"
            res["rows"].append(row)
    (out / "results_v2.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline=chr(10))

    L = ["| model | scope | chosen (tf, pct, k, entry, mgmt, floor) | IS n / net R | OOS n | win | avg gross R | fee drag R | net R @2bps | @0 | @5 | PF | maxDD R | BE | fill | PBO | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["rows"]:
        if "oos" not in r:
            L.append(f"| {r['model']} | {r['scope']} | - | - | - | - | - | - | - | - | - | - | - | - | - | {_f(r['pbo'], '{:.2f}')} | {r['verdict']} |")
            continue
        o, i, v = r["oos"], r["is"], r["variant"]
        L.append(f"| {r['model']} | {r['scope']} | {v[0]}m p{v[1]} k{v[2]} {v[3]} {v[4]} floor {v[5]*100:.2f}% | {i['n']} / {_f(i['exp_net_R'])} | {o['n']} | "
                 f"{_f(o['win'], '{:.0%}')} | {_f(o['avg_gross_R'])} | {_f(o['fee_drag_R'], '{:.2f}')} | {_f(o['exp_net_R'])} | {_f(o['net_0bps'])} | "
                 f"{_f(o['net_5bps'])} | {_f(o['pf'], '{:.2f}')} | {_f(o['max_dd_R'], '{:.1f}')} | {_f(o['be_share'], '{:.0%}')} | "
                 f"{_f(r['fill_rate'], '{:.0%}')} | {_f(r['pbo'], '{:.2f}')} | {r['verdict']} |")
    L += ["", "Fee drag and net by entry x stop floor (combined model, all sessions, OOS, medians over tf/pct/k/mgmt variants with n >= 30; fill = limit fill rate over the whole window)", "",
          "| entry | floor | variants (n>=30) | median OOS n | median fill | median gross R | median fee drag R | median net R @2bps | best net R | variants net>0 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for mode, fl in itertools.product(("mkt", "limit"), FLOORS):
        g = [x for x in res["grid"] if x["model"] == "combined" and x["scope"] == "all"
             and x["variant"][3] == mode and x["variant"][5] == fl and x["oos"]["n"] >= 30]
        if not g:
            L.append(f"| {mode} | {fl*100:.2f}% | 0 | - | - | - | - | - | - | - |")
            continue
        med = lambda f: statistics.median(f(x) for x in g)
        L.append(f"| {mode} | {fl*100:.2f}% | {len(g)} | {med(lambda x: x['oos']['n']):.0f} | "
                 f"{_f(med(lambda x: x['fill_rate_all'] if x['fill_rate_all'] is not None else 0), '{:.0%}')} | "
                 f"{_f(med(lambda x: x['oos']['avg_gross_R']))} | {_f(med(lambda x: x['oos']['fee_drag_R']), '{:.2f}')} | "
                 f"{_f(med(lambda x: x['oos']['exp_net_R']))} | {_f(max(x['oos']['exp_net_R'] for x in g))} | "
                 f"{sum(1 for x in g if x['oos']['exp_net_R'] > 0)} |")
    L += ["", "Top 8 variants by OOS net R @2bps (n >= 30; data-snooped on OOS, shown with their IS result; not a verdict)", "",
          "| model | scope | variant | IS n / net R | OOS n | win | gross R | drag R | net R @2bps | @5bps | PF | fill |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    top = sorted([x for x in res["grid"] if x["oos"]["n"] >= 30], key=lambda x: -x["oos"]["exp_net_R"])[:8]
    for x in top:
        o, i, v = x["oos"], x["is"], x["variant"]
        L.append(f"| {x['model']} | {x['scope']} | {v[0]}m p{v[1]} k{v[2]} {v[3]} {v[4]} floor {v[5]*100:.2f}% | {i['n']} / {_f(i['exp_net_R'])} | "
                 f"{o['n']} | {_f(o['win'], '{:.0%}')} | {_f(o['avg_gross_R'])} | {_f(o['fee_drag_R'], '{:.2f}')} | {_f(o['exp_net_R'])} | "
                 f"{_f(o['net_5bps'])} | {_f(o['pf'], '{:.2f}')} | {_f(x['fill_rate_all'], '{:.0%}')} |")
    (out / "tables_v2.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8", newline=chr(10))
    print("wrote", out)


if __name__ == "__main__":
    main()
