"""T6 step C extras: descriptive tables for RESULT.md (pooled row, R-converted CIs, regime mix, funding split, active-today).
Writes extras.json. No rule or bar is computed here; the bars live in t6_stats.py / summary.json."""
import sys
import json
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t6_core as core  # noqa: E402
import t6_stats as st  # noqa: E402

CACHE = pathlib.Path(r"F:/MTS/data_cache/binance/wave2-1114")
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"


def _d(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d")


def row_stats(rows, nb=2000):
    m = lambda k: float(np.mean([r[k] for r in rows]))
    out = dict(n=len(rows), weeks=len({r["iso_week"] for r in rows}), win=float(np.mean([r["net"] > 0 for r in rows])),
               gross=m("gross"), fee=m("fee"), funding=m("funding"), net_nofund=m("net_nofund"), net=m("net"))
    out["boot_net"] = st.cluster_bootstrap(rows, "net", nb)
    rr = [r for r in rows if r["net_R"] == r["net_R"]]
    out["R_n"] = len(rr)
    out["gross_R"] = float(np.mean([r["gross_R"] for r in rr]))
    out["net_R"] = float(np.mean([r["net_R"] for r in rr]))
    out["boot_net_R"] = st.cluster_bootstrap(rr, "net_R", nb)
    out["boot_gross_R"] = st.cluster_bootstrap(rr, "gross_R", nb)
    sr = [r for r in rows if r["stop_R"] == r["stop_R"]]
    out["stop_R_n"] = len(sr)
    out["stop_R"] = float(np.mean([r["stop_R"] for r in sr]))
    out["stop_boot"] = st.cluster_bootstrap(sr, "stop_R", nb)
    out["stop_hit_share"] = float(np.mean([r["stop_reason"] == "STOP" for r in sr]))
    out["net_R_median"] = float(np.median([r["net_R"] for r in rr]))
    return out


def mix(rows, key):
    c = {}
    for r in rows:
        c[r[key]] = c.get(r[key], 0) + 1
    t = sum(c.values())
    return {k: round(v / t, 3) for k, v in sorted(c.items())}


def main():
    here = pathlib.Path(__file__).resolve().parent
    trades = st.read_trades_csv(here / "trades.csv")
    phase = core.load_phase_table(PHASE)
    cov = json.load(open(here / "coverage.json", encoding="utf-8"))
    pool, open_ev, btc = [], [], None
    for name in cov["kept"]:
        c = core.load_coin(CACHE / "spot_1d" / (name + "USDT.csv"), name)
        f = core.load_funding(CACHE / "funding" / (name + "USDT.csv"))
        pool.extend(core.all_monday_trades(c, f))
        done = {r["entry_ts"] for r in core.event_trades(c, f)}
        for ev in core.events_dd20(c):
            ms = int(c.ms[ev["d0"]])
            if ms not in done:
                open_ev.append(dict(coin=name, entry=_d(ms), last_bar=_d(int(c.ms[-1])), ended=c.ended))
    for r in pool:
        lab, cyc = core.phase_tag(phase, r["entry_ts"])
        r.update(label=lab, cycle=cyc)
    E = {}
    val = st.sub(trades, split="VAL")
    dev = st.sub(trades, split="DEV")
    E["VAL"], E["DEV"], E["POOLED"] = row_stats(val), row_stats(dev), row_stats(trades)
    E["mix"] = {}
    for sp, rows in (("DEV", dev), ("VAL", val)):
        pl = st.sub(pool, split=sp)
        E["mix"][sp] = dict(signals_bull=mix(rows, "bull"), mondays_bull=mix(pl, "bull"),
                            signals_cycle=mix(rows, "cycle"), mondays_cycle=mix(pl, "cycle"),
                            n_mondays=len(pl), n_signals=len(rows))
    big = [r for r in val if (r["coin"], r["entry_date"]) in (("ONE", "2026-09-07"), ("ZIL", "2026-02-02"), ("AXS", "2026-02-09"))]
    rest = [r for r in val if r not in big]
    E["val_ex_three_named"] = dict(n=len(rest), mean=float(np.mean([r["net"] for r in rest])),
                                   dropped=[(r["coin"], r["entry_date"], round(r["net"], 4), round(r["funding"], 4)) for r in big])
    E["flat_vs_real_val"] = {k: dict(n=len(v), net=float(np.mean([r["net"] for r in v])) if v else None)
                             for k, v in (("FLAT", [r for r in val if r["funding_rule"] == "FLAT"]),
                                          ("REAL", [r for r in val if r["funding_rule"] == "REAL"]))}
    E["open_events_window_not_complete"] = open_ev
    E["no_stop_row_trades"] = [(r["coin"], r["entry_date"], r["split"]) for r in trades if r["stop_reason"] == ""]
    wb = np.loadtxt(CACHE / "spot_1d" / "BTCUSDT.csv", delimiter=",", skiprows=1, usecols=(0, 4))
    b = core.Coin("BTC", np.c_[wb[:, 0], wb[:, 1] * 0, wb[:, 1] * 0, wb[:, 1] * 0, wb[:, 1]] if False else
                  np.loadtxt(CACHE / "spot_1d" / "BTCUSDT.csv", delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4)))
    w = b.nw - 1
    E["btc"] = dict(last_complete_week_end=_d(int(b.ms[7 * w + 6])), week_close=float(b.wc[w]),
                    max_prior8=float(b.wc[w - 8:w].max()), ratio=float(b.wc[w] / b.wc[w - 8:w].max()),
                    last_bar=_d(int(b.ms[-1])), last_close=float(b.c[-1]), events_total=len(core.events_dd20(b)))
    (here / "extras.json").write_text(json.dumps(E, indent=1, default=str), encoding="utf-8")
    print("wrote extras.json")


if __name__ == "__main__":
    main()
