"""wavetrend_c30_retest_2026-11-04: WaveTrend dot re-run with retest entry, RSI confluence and session split. See PRE_REG.md.

Context comes ONLY from backtest/research_kit.py (regime_tag, session_tag, retest_entry, regime_mix_line, cluster stats, holm);
no new trend tag here. WT = research/wavetrend_2026-10-17/wt_parity_ref.py (pinned). Power gate: scripts/dev/prereg_gate.py.
Passes: --pass count (event counts, no returns), --pass dev, --pass val (DEV survivors only, once). Times are UTC milliseconds.
"""
import argparse
import csv
import importlib.util
import json
import sys
from datetime import timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

DAY = 86400000
H = 12                       # exit H bars after the entry bar close (OURS, carried from the atlas primary horizon)
RETEST_N = 6                 # OURS
COST = rk.TAKER_RT_PCT       # 0.14 % round trip, SOURCED research_kit
BAND = 53.0                  # SOURCED Pine band (PARITY_CONTRACT s2); "dot only inside the band" is OURS (C30 pre-reg)
WARMUP = 200                 # SOURCED-in-repo PARITY_CONTRACT s3 (WT used only after 200 bars)
RSI_PERIOD = 14              # SOURCED
RSI_BUY, RSI_SELL = 40.0, 60.0   # OURS level on the signal TF
DIV_WINDOW = (3, 12)         # SOURCED operator relay of Malkan (d-malkan-divergence-window-1104), closes only
DIV_NEAR = 3                 # OURS: a divergence stamped within the last 3 bars up to the dot bar
TFS = ("15m", "30m", "1h")
TF_MS = {"15m": 900000, "30m": 1800000, "1h": 3600000}
SESSIONS = ("asia", "london", "ny", "late")
CONFS = ("none", "rsi", "div")
ENTRIES = ("signal", "retest")
GATES = ("all", "with", "against", "reg_bull", "reg_range", "reg_bear")
SIDES = {"buy": 1, "sell": -1}
CONFIRM_CONFS = ("rsi", "div")
MIN_N, MIN_DAYS = 30, 20     # OURS survivor eligibility
M_POOLED = len(TFS) * len(SIDES) * len(CONFIRM_CONFS) * len(ENTRIES)      # 24
M_SESSION = M_POOLED * len(SESSIONS)                                      # 96
DATA_ROOTS = ("F:/MTS/Dumps/backtest/raw_1m_2019", "F:/MTS/Dumps/backtest/raw_1m_2022", "F:/MTS/Dumps/backtest/raw")
KEYS = ("tf", "side", "conf", "entry", "gate", "session")


def ms(ts):
    return int(ts.tz_localize(timezone.utc).timestamp() * 1000)


def window(pass_):
    """[lo, hi) in ms. dev = DEV; val = VALIDATION. HOLDOUT starts at the val end and is never loaded."""
    if pass_ == "val":
        return ms(splits.VALIDATION_START), ms(splits.VALIDATION_END)
    return ms(splits.DEV_START), ms(splits.DEV_END)


def val_guard(folder, survivors):
    if not survivors:
        return "no_survivors"
    if (Path(folder) / "val_cells.csv").exists():
        return "already_read"
    return "ok"


def is_survivor(r):
    return bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and r["holm_p"] < 0.05
                and r["excess_t"] == r["excess_t"] and r["excess_t"] >= 2)


def _wt():
    spec = importlib.util.spec_from_file_location("wt_parity_ref", REPO / "MyTradingSys/research/wavetrend_2026-10-17/wt_parity_ref.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_dots(wt1, wt2):
    """[(bar, side)]: buy dot = wt1 crosses above wt2 with wt1 <= -53; sell dot = crosses below with wt1 >= 53 (closed bars)."""
    ev = _wt().cross_events(wt1, wt2, "le")
    out = []
    for i, e in enumerate(ev):
        if e == 1 and wt1[i] <= -BAND:
            out.append((i, 1))
        elif e == -1 and wt1[i] >= BAND:
            out.append((i, -1))
    return out


def dots_for(bars, tf):
    wt1, wt2 = _wt().wavetrend([b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars])
    return [{"i": i, "side": s, "t_close": bars[i]["t"] + TF_MS[tf]} for i, s in find_dots(wt1, wt2) if i >= WARMUP]


def session_of_ms(t_ms):
    return rk.session_tag(int(t_ms) // 1000)


def by_session(events, sess):
    return list(events) if sess == "ALL" else [e for e in events if session_of_ms(e["t_close"]) == sess]


def level_of(bar):
    """Retest level = midpoint of the dot bar (OURS)."""
    return (bar["h"] + bar["l"]) / 2.0


def rsi_ok(rsi, i, side):
    v = rsi[i]
    if v is None:
        return False
    return v <= RSI_BUY if side > 0 else v >= RSI_SELL


def div_ok(idx, i):
    return any(k in idx for k in range(i - DIV_NEAR, i + 1))


def gate_label(ma_side, side):
    if ma_side is None:
        return "none"
    return "with" if (ma_side == "above") == (side > 0) else "against"


def make_ctx_at(daily, weekly_rsi, monthly_rsi):
    """ctx(t_ms) -> research_kit.regime_tag dict. Daily, weekly and monthly bars close at 00:00 UTC, so the tag is constant inside
    a UTC day: evaluated at the day start and cached."""
    cache = {}

    def ctx_at(t):
        d = int(t // DAY)
        if d not in cache:
            cache[d] = rk.regime_tag(d * DAY, daily, weekly_rsi, monthly_rsi)
        return cache[d]
    return ctx_at


def event_in_gate(ctx, side, gate):
    if gate == "all":
        return True
    if gate in ("with", "against"):
        return gate_label(ctx["side"], side) == gate
    return ctx["regime"] == gate[4:]


def trades_for(events, bars, entry, h=H, n=RETEST_N, lo_ms=None, hi_ms=None):
    """Per event {day, gross}: signal = enter at the dot bar close; retest = first pullback to the dot bar midpoint within n bars
    after the dot bar (research_kit.retest_entry). Exit = close h bars after the entry bar. No exit bar / outside window: dropped."""
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    out, nsig = [], 0
    for e in events:
        if (lo_ms is not None and e["t_close"] < lo_ms) or (hi_ms is not None and e["t_close"] >= hi_ms):
            continue
        i, sgn = e["i"], e["side"]
        nsig += 1
        if entry == "signal":
            j, px = i, ohlc[i][3]
        else:
            r = rk.retest_entry(ohlc, i, level_of(bars[i]), sgn, n)
            if r is None:
                continue
            j, px = r
        if j + h >= len(ohlc):
            continue
        out.append({"day": int(bars[j]["t"] // DAY), "gross": sgn * (ohlc[j + h][3] - px) / px * 100.0})
    return out, nsig


def cell_stats(trs, drift):
    g = np.array([x["gross"] for x in trs])
    d = [x["day"] for x in trs]
    if len(g) == 0:
        return {"n": 0, "days": 0}
    net = g - COST
    m, se = rk.cluster_mean_se(net, d)
    t = rk.t_stat(m, se)
    if drift and len(drift[0]):
        ex, ex_se = rk.cluster_diff(g, d, np.array(drift[0]), drift[1])
    else:
        ex, ex_se = float("nan"), float("nan")
    return {"n": len(g), "days": len(set(d)), "gross": float(g.mean()), "net": m, "se": se, "t": t, "p": rk.norm_p_two(t),
            "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se, "hit_net": float((net > 0).mean()),
            "excess": ex, "excess_se": ex_se, "excess_t": rk.t_stat(ex, ex_se)}


class BarTags:
    """Per-bar rows for the drift control: gross H-bar return from every bar close in the window, with its ctx and session."""

    def __init__(self, bars, tf, ctx_at, lo_ms, hi_ms, h=H):
        self.c = np.array([b["c"] for b in bars])
        self.h = h
        self.idx = []
        for i in range(len(bars) - h):
            tc = bars[i]["t"] + TF_MS[tf]
            if tc < lo_ms or tc >= hi_ms:
                continue
            x = ctx_at(tc)
            self.idx.append((i, int(bars[i]["t"] // DAY), x["side"], x["regime"], session_of_ms(tc)))

    def drift(self, side, gate, sess):
        g, day = [], []
        for i, d, ma, reg, s in self.idx:
            if sess != "ALL" and s != sess:
                continue
            if gate in ("with", "against"):
                if gate_label(ma, side) != gate:
                    continue
            elif gate != "all" and reg != gate[4:]:
                continue
            g.append(side * (self.c[i + self.h] - self.c[i]) / self.c[i] * 100.0)
            day.append(d)
        return g, day


def load_1m(end_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    bars = {}
    for r in DATA_ROOTS:
        for b in load_klines(r, end_ms=end_ms):
            bars[b["t"]] = b
    return [bars[k] for k in sorted(bars)]


def rsi_series(bars):
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    r = rsi_core([x["c"] for x in bars], RSI_PERIOD)
    keep = [k for k in range(len(bars) - 1) if r[k] is not None]
    return [bars[k + 1]["t"] for k in keep], [r[k] for k in keep]


def build_context(bars_1m, registry):
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    d = resample(bars_1m, "1d", registry)
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    return daily, rsi_series(resample(bars_1m, "1w", registry)), rsi_series(resample(bars_1m, "1M", registry))


def week_starts(lo_ms, hi_ms):
    d0 = int(lo_ms // DAY)
    d0 += (4 - d0) % 7
    return [d * DAY for d in range(d0, int(hi_ms // DAY), 7)]


def div_index(bars, side):
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence
    closes = [b["c"] for b in bars]
    rsi = rsi_core(closes, RSI_PERIOD)
    kind = "bullish" if side > 0 else "bearish"
    evs = rsi_divergence(closes, rsi, [b["t"] for b in bars], DIV_WINDOW[0], DIV_WINDOW[1], kind, 0.0)
    return {e["i"] for e in evs}, rsi


def main():
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    survivors = []
    if a.pass_ == "val":
        survivors = json.loads((HERE / "dev_survivors.json").read_text(encoding="utf-8"))
        g = val_guard(HERE, survivors)
        if g != "ok":
            print("VALIDATION not read:", g)
            return 0 if g == "no_survivors" else 3
    lo_ms, hi_ms = window(a.pass_)
    bars_1m = load_1m(hi_ms)                      # never a bar at/after the window end (HOLDOUT never loaded)
    assert bars_1m[-1]["t"] < hi_ms
    daily, wk, mo = build_context(bars_1m, registry)
    ctx_at = make_ctx_at(daily, wk, mo)
    rows = []
    for tf in TFS:
        bars = resample(bars_1m, tf, registry)
        dots = dots_for(bars, tf)
        for e in dots:
            e["ctx"] = ctx_at(e["t_close"])
        tags = None if a.pass_ == "count" else BarTags(bars, tf, ctx_at, lo_ms, hi_ms)
        for sname, sgn in SIDES.items():
            idx, rsi = div_index(bars, sgn)
            ev_side = [e for e in dots if e["side"] == sgn]
            for conf in CONFS:
                evs = [e for e in ev_side if conf == "none" or (conf == "rsi" and rsi_ok(rsi, e["i"], sgn))
                       or (conf == "div" and div_ok(idx, e["i"]))]
                for gate in GATES:
                    ge = [e for e in evs if event_in_gate(e["ctx"], sgn, gate)]
                    for sess in ("ALL",) + SESSIONS:
                        se_ = by_session(ge, sess)
                        for entry in ENTRIES:
                            if a.pass_ == "val" and not (gate == "with" and conf != "none" and [tf, sname, conf, entry, sess] in survivors):
                                continue
                            trs, nsig = trades_for(se_, bars, entry, lo_ms=lo_ms, hi_ms=hi_ms)
                            row = dict(zip(KEYS, (tf, sname, conf, entry, gate, sess)))
                            row["signals"] = nsig
                            if a.pass_ == "count":
                                row.update({"n": len(trs), "days": len({x["day"] for x in trs})})
                            else:
                                row.update(cell_stats(trs, tags.drift(sgn, gate, sess)))
                            rows.append(row)
        print(tf, "done", file=sys.stderr, flush=True)
    if a.pass_ == "dev":
        for fam_sess, m in ((False, M_POOLED), (True, M_SESSION)):
            fam = [r for r in rows if r["gate"] == "with" and r["conf"] in CONFIRM_CONFS and r.get("n", 0) > 0
                   and (r["session"] != "ALL") == fam_sess]
            adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=m)
            for r, q in zip(fam, adj):
                r["holm_p"] = float(q)
                r["survivor"] = is_survivor(r)
        with open(HERE / "dev_survivors.json", "w", newline="\n") as f:
            json.dump([[r["tf"], r["side"], r["conf"], r["entry"], r["session"]] for r in rows if r.get("survivor")], f)
    if a.pass_ == "val":
        for r in rows:
            r["val_pass"] = bool(r.get("n", 0) >= 15 and r["net"] > 0 and r["p"] < 0.05)
    name = {"count": "counts.csv", "dev": "dev_cells.csv", "val": "val_cells.csv"}[a.pass_]
    cols = sorted({k for r in rows for k in r}, key=lambda k: (k not in KEYS, k))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    line = rk.regime_mix_line([ctx_at(t)["regime"] for t in week_starts(lo_ms, hi_ms)])
    (HERE / ("regime_mix_" + a.pass_ + ".txt")).write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
