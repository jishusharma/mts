"""wavetrend_c30 long-window DEV pass (PRE_REG_LONG.md). Same arms and parameters as study.py (imported, not copied); only the data
(public SPOT klines 2017-08.. via bt_data.load_klines, native 15m/30m/1h/1d bars), the DEV start (2018-04-01) and ONE added proxy
arm differ. Passes: --pass count (event counts, no returns), dev, val (DEV survivors only, once). HOLDOUT is never loaded: every
loader call has end_ms <= the window end. Times are UTC milliseconds."""
import argparse
import csv
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

_spec = importlib.util.spec_from_file_location("wt_c30_study_run1", HERE / "study.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

DAY = S.DAY
SPOT_ROOT = "F:/MTS/Dumps/backtest/spot_2017"
SYMBOL = "BTCUSDT"
LONG_START = "2018-04-01"            # OURS: SMA200 of daily spot bars (first 2017-08-17) is defined from about 2018-03-05
GATES_LONG = S.GATES + ("reg_bearp",)       # reg_bearp = the proxy arm (OURS): weekly RSI14 <= 40 alone, close below SMA200
M_POOLED_LONG = 2 * S.M_POOLED               # strict trend-gate family (24) + proxy family (24)
M_SESSION_LONG = 2 * S.M_SESSION
SEGMENTS = ("long", "fresh", "old")          # fresh = before 2022-01-01 (new DEV data); old = run 1 DEV window (seen in run 1)
SEG_GATES = ("with", "reg_bearp")
KEYS = S.KEYS + ("seg",)


def ms(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


def window_long(pass_):
    if pass_ == "val":
        return S.ms(splits.VALIDATION_START), S.ms(splits.VALIDATION_END)
    return ms(LONG_START), S.ms(splits.DEV_END)


def segment_of(t_ms):
    return "fresh" if t_ms < S.ms(splits.DEV_START) else "old"


def spot_bars(root, symbol, tf, end_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    return load_klines(Path(root) / symbol / tf, end_ms=end_ms)


def proxy_regime(side, weekly_rsi):
    """OURS proxy: bear = weekly RSI14 <= 40 (monthly ignored) AND close below the daily SMA200; else other; None if unavailable."""
    if side is None or weekly_rsi is None:
        return None
    return "bear" if (weekly_rsi <= rk.RSI_BEAR and side == "below") else "other"


def make_ctx_pair(daily, wk, mo):
    """(ctx_strict, ctx_proxy): both as-of, cached per UTC day. ctx_proxy has regime = proxy tag so BarTags/event_in_gate reuse it."""
    cache = {}

    def get(t):
        d = int(t // DAY)
        if d not in cache:
            c = rk.regime_tag(d * DAY, daily, wk, mo)
            p = proxy_regime(c["side"], rk._last_closed(wk, d * DAY))
            cache[d] = (c, {"side": c["side"], "band": None, "regime": p})
        return cache[d]
    return (lambda t: get(t)[0]), (lambda t: get(t)[1])


def build_context(end_ms, registry):
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    d = spot_bars(SPOT_ROOT, SYMBOL, "1d", end_ms)
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    return daily, S.rsi_series(resample(d, "1w", registry)), S.rsi_series(resample(d, "1M", registry))


def ev_in(ctx_s, ctx_p, side, gate):
    if gate == "reg_bearp":
        return S.event_in_gate(ctx_p, side, "reg_bear")
    return S.event_in_gate(ctx_s, side, gate)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    surv = []
    if a.pass_ == "val":
        surv = json.loads((HERE / "dev_survivors_long.json").read_text(encoding="utf-8"))
        if not surv:
            print("VALIDATION not read: no_survivors")
            return 0
        if (HERE / "val_cells_long.csv").exists():
            print("VALIDATION not read: already_read")
            return 3
    lo_ms, hi_ms = window_long(a.pass_)
    daily, wk, mo = build_context(hi_ms, registry)
    ctx_s, ctx_p = make_ctx_pair(daily, wk, mo)
    seg_win = {"long": (lo_ms, hi_ms), "fresh": (lo_ms, S.ms(splits.DEV_START)), "old": (S.ms(splits.DEV_START), hi_ms)}
    rows = []
    for tf in S.TFS:
        bars = spot_bars(SPOT_ROOT, SYMBOL, tf, hi_ms)
        assert bars[-1]["t"] < hi_ms
        dots = S.dots_for(bars, tf)
        for e in dots:
            e["ctx"], e["ctxp"] = ctx_s(e["t_close"]), ctx_p(e["t_close"])
        tags = {}
        if a.pass_ != "count":
            tags = {(s, g): S.BarTags(bars, tf, ctx_p if g == "reg_bearp" else ctx_s, *seg_win[s])
                    for s in SEGMENTS for g in ("main", "reg_bearp")}
        for sname, sgn in S.SIDES.items():
            idx, rsi = S.div_index(bars, sgn)
            ev_side = [e for e in dots if e["side"] == sgn]
            for conf in S.CONFS:
                evs = [e for e in ev_side if conf == "none" or (conf == "rsi" and S.rsi_ok(rsi, e["i"], sgn))
                       or (conf == "div" and S.div_ok(idx, e["i"]))]
                for gate in GATES_LONG:
                    ge = [e for e in evs if ev_in(e["ctx"], e["ctxp"], sgn, gate)]
                    for sess in ("ALL",) + S.SESSIONS:
                        se_ = S.by_session(ge, sess)
                        for entry in S.ENTRIES:
                            for seg in SEGMENTS:
                                if seg != "long" and not (gate in SEG_GATES and conf != "none" and sess == "ALL"):
                                    continue
                                if a.pass_ == "val" and not (seg == "long" and [tf, sname, conf, entry, sess, gate] in surv):
                                    continue
                                slo, shi = seg_win[seg]
                                trs, nsig = S.trades_for(se_, bars, entry, lo_ms=slo, hi_ms=shi)
                                row = dict(zip(KEYS, (tf, sname, conf, entry, gate, sess, seg)))
                                row["signals"] = nsig
                                if a.pass_ == "count":
                                    row.update({"n": len(trs), "days": len({x["day"] for x in trs})})
                                else:
                                    tg = tags[(seg, "reg_bearp" if gate == "reg_bearp" else "main")]
                                    row.update(S.cell_stats(trs, tg.drift(sgn, "reg_bear" if gate == "reg_bearp" else gate, sess)))
                                rows.append(row)
        print(tf, "done", file=sys.stderr, flush=True)
    if a.pass_ == "dev":
        for fam_sess, m in ((False, M_POOLED_LONG), (True, M_SESSION_LONG)):
            fam = [r for r in rows if r["gate"] in SEG_GATES and r["conf"] in S.CONFIRM_CONFS and r["seg"] == "long"
                   and r.get("n", 0) > 0 and (r["session"] != "ALL") == fam_sess]
            adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=m)
            for r, q in zip(fam, adj):
                r["holm_p"] = float(q)
                r["survivor"] = S.is_survivor(r)
        with open(HERE / "dev_survivors_long.json", "w", newline="\n") as f:
            json.dump([[r["tf"], r["side"], r["conf"], r["entry"], r["session"], r["gate"]] for r in rows if r.get("survivor")], f)
    if a.pass_ == "val":
        for r in rows:
            r["val_pass"] = bool(r.get("n", 0) >= 15 and r["net"] > 0 and r["p"] < 0.05)
    name = {"count": "counts_long.csv", "dev": "dev_cells_long.csv", "val": "val_cells_long.csv"}[a.pass_]
    cols = sorted({k for r in rows for k in r}, key=lambda k: (k not in KEYS, k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    wks = S.week_starts(lo_ms, hi_ms)
    strict = [ctx_s(t)["regime"] for t in wks]
    prox = [ctx_p(t)["regime"] for t in wks]
    line = (rk.regime_mix_line(strict) + f" | strict bear {strict.count('bear')} ; proxy bear (weekly RSI14 <= 40 alone, below SMA200, OURS) "
            f"{prox.count('bear')} of {len(wks)} weeks")
    (HERE / ("regime_mix_long_" + a.pass_ + ".txt")).write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
