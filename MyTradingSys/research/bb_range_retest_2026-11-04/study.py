"""bb_range_retest_2026-11-04: Bollinger band retest-LEVEL arm (entry on the return to the band just left), by session. See PRE_REG.md.

Fixes bb_range_to_range_2026-11-04, whose 'retest' entry filled 99.9 % (= the next open). Here the entry needs (1) a re-entry CLOSE back
inside the band within M bars, then (2) a pullback that touches level +- k ATR within N bars. Context only from backtest/research_kit.py
(regime_tag, session_tag, retest_entry, regime_mix_line, cluster stats, holm); no trend tag is written here. Event finding, the bracket,
cell statistics and data loading are reused from the earlier study by path. Passes: --pass count (no returns), dev, val (survivors only).
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

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

_sp = importlib.util.spec_from_file_location("bb_r2r_prev", REPO / "MyTradingSys/research/bb_range_to_range_2026-11-04/study.py")
prev = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(prev)
ms, load_1m, build_context, make_regime_at, week_starts = prev.ms, prev.load_1m, prev.build_context, prev.make_regime_at, prev.week_starts

DAY = 86400000
TF, TF_MS = "15m", 900000
ATR_N = 14                   # OURS (common default)
M_REENTER = 10               # OURS: bars after the signal bar to see a close back inside the band
N_TOUCH = 10                 # OURS: bars after the re-entry bar to touch level +- k ATR (as the earlier retest N)
K_GRID = (0.25, 0.5, 1.0)    # OURS: touch tolerance in ATR(14) at the signal bar
SESS_HIST = 20               # OURS: prior same-name sessions for the "larger range" median
SESS_MIN_HIST = 10           # OURS: fewer than this many prior sessions = never tagged
COST = rk.TAKER_RT_PCT
SESSIONS = ("asia", "london", "ny", "late")
CONFIRM_SESSIONS = ("asia", "london", "ny")
MIN_N, MIN_DAYS = 30, 20


def atr14(ohlc, i, n=ATR_N):
    """Mean true range of bars i-n+1..i (needs bar i-n for the first previous close). NaN when not enough bars."""
    if i - n < 0:
        return float("nan")
    tr = []
    for b in range(i - n + 1, i + 1):
        _, h, l, _c = ohlc[b]
        pc = ohlc[b - 1][3]
        tr.append(max(h - l, abs(h - pc), abs(l - pc)))
    return float(np.mean(tr))


def session_range_tags(bars, tf_ms):
    """Per bar: True when the current session running range (high-low so far incl. this bar, % of this bar close) is STRICTLY above
    the median of the final ranges of the previous SESS_HIST same-name sessions (>= SESS_MIN_HIST of them), else False. Session of a bar =
    research_kit.session_tag of its close time; a session instance = (UTC day of that close, name). As-of: reads bars up to i only."""
    tags, hist = [], {}
    key, name, hi, lo, ref = None, None, 0.0, 0.0, 1.0
    for b in bars:
        tc = b["t"] + tf_ms
        nm = rk.session_tag(tc / 1000)
        k = (int(tc // DAY), nm)
        if k != key:
            if key is not None:
                hist.setdefault(name, []).append((hi - lo) / ref * 100.0)
            key, name, hi, lo = k, nm, b["h"], b["l"]
        else:
            hi, lo = max(hi, b["h"]), min(lo, b["l"])
        ref = b["c"]
        h = hist.get(nm, [])[-SESS_HIST:]
        tags.append(bool(len(h) >= SESS_MIN_HIST and (hi - lo) / ref * 100.0 > float(np.median(h))))
    return tags


def level_arm_fill(ohlc, i, side, level, k_atr, atr, m_reenter=M_REENTER, n_touch=N_TOUCH):
    """Signal bar i beyond the band at `level`. Step 1: first bar r in i+1..i+m_reenter whose CLOSE is back inside (long close > level,
    short close < level); none = no trade. Step 2: research_kit.retest_entry from r with the limit at level + side*k_atr*atr (long: a low at
    or below it; short: a high at or above it) within n_touch bars after r; fills at the limit, or at the open when gapped. Bars <= r are
    never used for the fill. Returns (bar_index, fill_price) or None."""
    if atr != atr:
        return None
    r = None
    for b in range(i + 1, min(i + m_reenter, len(ohlc) - 1) + 1):
        c = ohlc[b][3]
        if (side > 0 and c > level) or (side < 0 and c < level):
            r = b
            break
    if r is None:
        return None
    return rk.retest_entry(ohlc, r, level + side * k_atr * atr, side, n_touch)


def build_trades(events, bars, k, lo_ms, hi_ms):
    """Filled trades with a valid bracket for events whose signal close is in [lo_ms, hi_ms); stores e['fill_<k>'] on every such event."""
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    trs = []
    for e in events:
        if e["t_close"] < lo_ms or e["t_close"] >= hi_ms:
            continue
        i, sgn = e["i"], e["side"]
        fill = level_arm_fill(ohlc, i, sgn, e["level"], k, atr14(ohlc, i))
        e["fill_" + str(k)] = fill
        if fill is None:
            continue
        j, px = fill
        g = prev.bracket_trade(ohlc, j, px, sgn, e["target"])
        if g is None:
            continue
        reach = sgn * (e["target"] - px) / px * 100.0
        trs.append({"day": int(bars[j]["t"] // DAY), "gross": g, "entry_px": px, "side": sgn, "hit": bool(abs(g - reach) < 1e-9),
                    "session": e["session"], "wide": e["wide"], "t": bars[j]["t"], "tag": e["tag"], "regime": e["regime"],
                    "stop_pct": prev.STOP_FRAC * abs(e["target"] - px) / px * 100.0})
    return trs


def reentered(ohlc, e):
    i, sgn = e["i"], e["side"]
    for b in range(i + 1, min(i + M_REENTER, len(ohlc) - 1) + 1):
        c = ohlc[b][3]
        if (sgn > 0 and c > e["level"]) or (sgn < 0 and c < e["level"]):
            return True
    return False


def sel(trs, session, gate, tag, side="both"):
    return [x for x in trs if (session == "ALL" or x["session"] == session) and (gate == "all" or x["regime"] == gate)
            and (tag == "any" or (x["tag"] if tag == "tagged" else not x["tag"]))
            and (side == "both" or x["side"] == (1 if side == "long" else -1))]


def main():
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    surv = []
    if a.pass_ == "val":
        surv = json.loads((HERE / "dev_survivors.json").read_text(encoding="utf-8"))
        if not surv:
            print("no DEV survivors: VALIDATION not read")
            return 0
        if (HERE / "val_cells.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
        lo_ms, hi_ms = ms(splits.VALIDATION_START), ms(splits.VALIDATION_END)
    else:
        lo_ms, hi_ms = ms(splits.DEV_START), ms(splits.DEV_END)
    bars_1m = load_1m(hi_ms)
    assert bars_1m[-1]["t"] < hi_ms
    daily, wk, mo = build_context(bars_1m, registry)
    regime_at = make_regime_at(daily, wk, mo)
    bars = resample(bars_1m, TF, registry)
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    tags = session_range_tags(bars, TF_MS)
    evs = prev.find_events(bars, TF_MS)
    for e in evs:
        e["session"] = rk.session_tag(e["t_close"] / 1000)
        e["tag"] = tags[e["i"]]
        e["regime"] = regime_at(e["t_close"]) or "none"
    inwin = [e for e in evs if lo_ms <= e["t_close"] < hi_ms]
    rows = []
    for k in K_GRID:
        trs = build_trades(evs, bars, k, lo_ms, hi_ms)
        for sess in ("ALL",) + SESSIONS:
            for gate in ("range", "all"):
                for tag in ("tagged", "untagged", "any"):
                    for side in ("both", "long", "short"):
                        if a.pass_ == "val" and not (gate == "range" and tag == "tagged" and side == "both" and [sess, k] in surv):
                            continue
                        s = sel(trs, sess, gate, tag, side)
                        ev_s = [e for e in inwin if (sess == "ALL" or e["session"] == sess) and (gate == "all" or e["regime"] == gate)
                                and (tag == "any" or (e["tag"] if tag == "tagged" else not e["tag"]))
                                and (side == "both" or e["side"] == (1 if side == "long" else -1))]
                        row = {"session": sess, "k": k, "gate": gate, "tag": tag, "side": side, "signals": len(ev_s),
                               "reentered": sum(1 for e in ev_s if reentered(ohlc, e)),
                               "fills": sum(1 for e in ev_s if e.get("fill_" + str(k)) is not None)}
                        row["fill_rate"] = row["fills"] / row["signals"] if row["signals"] else float("nan")
                        if a.pass_ == "count":
                            row.update({"n": len(s), "days": len({x["day"] for x in s}),
                                        "median_stop_pct": float(np.median([x["stop_pct"] for x in s])) if s else float("nan")})
                        else:
                            row.update(prev.cell_stats(s))
                            if gate == "range" and tag == "tagged" and side == "both":
                                for nm, other in (("vs_ungated", sel(trs, sess, "all", "tagged")),
                                                  ("vs_untagged", sel(trs, sess, "range", "untagged"))):
                                    if s and other:
                                        d, dse = rk.cluster_diff([x["gross"] for x in s], [x["day"] for x in s],
                                                                 [x["gross"] for x in other], [x["day"] for x in other])
                                        row.update({nm: d, nm + "_se": dse, nm + "_t": rk.t_stat(d, dse)})
                        rows.append(row)
        print("k", k, "done", file=sys.stderr, flush=True)
    if a.pass_ == "dev":
        fam = [r for r in rows if r["gate"] == "range" and r["tag"] == "tagged" and r["side"] == "both" and r["session"] in CONFIRM_SESSIONS
               and r.get("n", 0) > 0]
        m = len(CONFIRM_SESSIONS) * len(K_GRID)
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=m)
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            vt = r.get("vs_ungated_t", float("nan"))
            r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05 and vt == vt and vt >= 2)
        with open(HERE / "dev_survivors.json", "w", newline="\n") as f:
            json.dump([[r["session"], r["k"]] for r in fam if r.get("survivor")], f)
    name = {"count": "counts.csv", "dev": "dev_cells.csv", "val": "val_cells.csv"}[a.pass_]
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("session", "k", "gate", "tag", "side"), k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    line = rk.regime_mix_line([regime_at(t) for t in week_starts(lo_ms, hi_ms)])
    (HERE / ("regime_mix_%s.txt" % a.pass_)).write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
