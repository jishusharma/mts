"""Export the fractals_2026-10-31 studies (P1b, F1, F2, F3, phase tag) to simulator result files.

Reads only committed outputs of those studies (events_feenet.csv, split_cells.csv, f1/trades_pct.csv,
f2/gate_events.csv, f3/trades_pct.csv, phase_tag/tags.csv, RESULT.md). Nothing is re-run or re-tuned.
The f1/f2 lists are written by fractals_2026-10-31/export_trades.py, the f3 list by f3/run_f3.py.
Percent distances and timestamps only: the repo is public, no prices are written.
Usage: python fractals_export.py [--out DIR]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import export_results as er  # noqa: E402

FR = os.path.join(er.RESEARCH, "fractals_2026-10-31")
FAMILY = "Fractals + BTC phase"
WINDOW = "DEV 2022-01-01 to 2025-06-30 (files after 2025-06 never opened; HOLDOUT untouched)"
RT_PCT = 0.10          # all-taker round trip, 2 x BINANCE_TAKER 0.05 % (fees.py)
S, O = "SOURCED", "OURS"


def rel(*p):
    return er.rel(os.path.join(FR, *p))


def md_rows(path, first_cell, second_cell=None):
    """Rows of the first markdown table whose header starts with first_cell (and second_cell, if given)."""
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, ln in enumerate(lines):
        if not ln.startswith("|"):
            continue
        h = [c.strip() for c in ln.strip().strip("|").split("|")]
        if h[0] == first_cell and (second_cell is None or h[1] == second_cell):
            rows = []
            for r in lines[i:][2:]:
                if not r.startswith("|"):
                    break
                rows.append([c.strip() for c in r.strip().strip("|").split("|")])
            return rows
    raise ValueError("table %r not found in %s" % (first_cell, path))


def replay(trades, unit, title, caption, labels=None):
    e = {"kind": "replay", "title": title, "caption": caption, "unit": unit, "trades": trades,
         "cum": [round(float(x), 3) for x in np.cumsum([t["r"] for t in trades])]}
    if labels:
        e["labels"] = labels
    return e


def table(title, cols, rows, caption=""):
    return {"kind": "table", "title": title, "cols": cols, "rows": rows, "caption": caption}


# ---------- P1b ----------
def p1b_events():
    return pd.read_csv(os.path.join(FR, "p1b_rsi_feenet", "events_feenet.csv"))


def p1b_stats():
    ev = p1b_events()
    by = {tf: (len(d), float(d.r_gross.mean()), float(d.r_net.mean())) for tf, d in ev.groupby("timeframe")}
    return {"n": len(ev), "mean_net": float(ev.r_net.mean()), "mean_gross": float(ev.r_gross.mean()), "by_tf": by}


def p1b_result():
    st = p1b_stats()
    ev = p1b_events()
    cells = pd.read_csv(os.path.join(FR, "p1b_rsi_feenet", "split_cells.csv"))
    trades = []
    for r in ev.itertuples():
        side = 1 if r.side == "long" else -1
        risk = r.r_unit / r.entry * 100
        trades.append({"d": r.date, "s": side, "f": "%s RSI divergence (exit: %s, %d bars)" % (r.timeframe, r.exit_reason, r.bars),
                       "l2": round(-risk, 3), "t1": round(2 * risk, 3), "t2": round(2 * risk, 3), "r": round(float(r.r_net), 3)})
    ex = ev.exit_reason.value_counts(normalize=True) * 100
    crows = [[c.tag, c.cell, int(c.n), "%+.3f" % c.mean_r, "[%+.3f, %+.3f]" % (c.ci_lo, c.ci_hi), c.verdict] for c in cells.itertuples()]
    tfrows = [[tf, n, "%+.3f" % g, "%+.3f" % m] for tf, (n, g, m) in sorted(st["by_tf"].items())]
    return {
        "id": "fractals-p1b-rsi-by-phase", "kind": "backtest", "parity": None, "family": FAMILY, "provenance": "exported",
        "title": "RSI divergence (1h and 4h) with a fixed 1R/2R bracket and taker fees, split by BTC market phase",
        "date": "2026-10-31",
        "what": [
            er.W("Signal", "The 643 RSI-divergence events of the layer lab table (interval 3 to 10 bars, bullish = long, bearish = short); "
                 "3 dropped for no full 24-bar window, %d kept" % st["n"], S),
            er.W("Timeframe / market", "BTCUSDT perpetual, 1h (502 events) and 4h (138 events) bars", S),
            er.W("Entry", "Open of the bar after the signal bar", S),
            er.W("Stop / target", "Stop 1.0 R, target 2.0 R, with R = ATR(14) at entry; both multiples fixed before any outcome was read, not tuned", O),
            er.W("Time exit", "Close of the 24th bar", S),
            er.W("Same-bar touch of stop and target", "Stop is taken (conservative)", O),
            er.W("Fees", "Taker on every leg, 0.05 % per side (Binance USDT-M); no slippage, no funding", S),
            er.W("Phase tags", "Cowen band side, 200-day average side and weekly 10-average phase of the day, from bars closed the day before", O),
            er.W("Cell rule", "n >= 200 decides, 30 to 199 reported only, under 30 too small; block-bootstrap 95 % CI", O),
        ],
        "how": "Every event is replayed bar by bar with the bracket above (frozen in PRE_REG.md before any outcome). Net R = gross R minus the "
               "two taker legs. Then the same events are grouped by the phase tag of their day and each cell is scored with a block-bootstrap CI.",
        "window": "DEV 2022-01 to 2024-06 (bars opening before 2024-07-01; later data never read)",
        "verdict": {"label": "Negative: every phase cell loses after fees, no PASS", "tone": "bad"},
        "why": [
            "Pooled net %+.3f R per trade on %d events (gross %+.3f R): fees alone cost about %.2f R per trade." % (
                st["mean_net"], st["n"], st["mean_gross"], st["mean_gross"] - st["mean_net"]),
            "Exits: stop %.1f %%, target %.1f %%, time %.1f %%." % (ex.get("stop", 0), ex.get("target", 0), ex.get("time", 0)),
            "No cell has a positive CI. The shift test finds no phase tag that separates the cells beyond chance.",
            "4h is the only positive slice (net %+.3f R) but n = %d is under the decide bar of 200." % (st["by_tf"]["4h"][2], st["by_tf"]["4h"][0]),
            "Other brackets are untested and would be a new pre-registration. Edge claimed: none.",
        ],
        "kpis": [
            {"label": "events (DEV)", "value": str(st["n"])},
            {"label": "mean net R per trade", "value": "%+.3f" % st["mean_net"], "tone": "bad"},
            {"label": "mean R before fees", "value": "%+.3f" % st["mean_gross"]},
            {"label": "1h net R (n=%d)" % st["by_tf"]["1h"][0], "value": "%+.3f" % st["by_tf"]["1h"][2], "tone": "bad"},
            {"label": "4h net R (n=%d, too few to decide)" % st["by_tf"]["4h"][0], "value": "%+.3f" % st["by_tf"]["4h"][2]},
            {"label": "phase cells with a positive CI", "value": str(int((cells.ci_lo > 0).sum()))},
        ],
        "examples": [
            replay(trades, "R", "Trade replay (all %d events, time order)" % st["n"],
                   "Distance from entry in %; up is in favour of the trade. No prices.",
                   {"t2": "Target (2 R)", "t1": "Target (2 R)", "zero": "Entry", "l2": "Stop (1 R)"}),
            table("Phase cells (net R per trade)", ["Tag", "Cell", "n", "Net R", "95% CI", "Verdict"], crows,
                  "Cowen band side, 200-day average side, weekly 10-average phase, and a week-parity placebo that must not flag."),
            table("By timeframe", ["Timeframe", "n", "Gross R", "Net R"], tfrows),
        ],
        "source_files": [rel("p1b_rsi_feenet", "RESULT.md"), rel("p1b_rsi_feenet", "PRE_REG.md"), rel("p1b_rsi_feenet", "events_feenet.csv"),
                         rel("p1b_rsi_feenet", "split_cells.csv")],
        "commit": er.commit_of([os.path.join(FR, "p1b_rsi_feenet")]),
    }


# ---------- F1 ----------
def f1_trades():
    return pd.read_csv(os.path.join(FR, "f1", "trades_pct.csv"))


def f1_stats():
    t = f1_trades()
    return {"groups": {k: (len(d), float(d.net_r.mean())) for k, d in t.groupby("group")}}


def risk_pct(row):
    """Stop distance in percent of entry, from net R (stop and target exits only; fee is the 0.10 % round trip)."""
    if row.why == "target":
        return RT_PCT / (1 - row.net_r)
    if row.why == "stop":
        return RT_PCT / (-1 - row.net_r)
    return None


def f1_result():
    t = f1_trades()
    conf = t[t.group != "NONE"].reset_index(drop=True)
    trades = []
    for r in conf.itertuples():
        rp = risk_pct(r)
        e = {"d": r.time[:10], "s": 1 if r.side == "long" else -1, "f": "%s pivot fade (exit: %s)" % (r.group, r.why), "r": round(float(r.net_r), 3)}
        if rp:
            e.update(l2=round(-rp, 3), t1=round(rp, 3), t2=round(rp, 3))
        trades.append(e)
    path = os.path.join(FR, "f1", "RESULT.md")
    tab = md_rows(path, "group", "n real")
    ph = md_rows(path, "group", "tag")
    st = f1_stats()["groups"]
    n_any = st["CONF_4H"][0] + st["CONF_1D"][0]
    m_any = (st["CONF_4H"][0] * st["CONF_4H"][1] + st["CONF_1D"][0] * st["CONF_1D"][1]) / n_any
    ex = conf.why.value_counts()
    return {
        "id": "fractals-f1-swing-confluence", "kind": "backtest", "parity": None, "family": FAMILY, "provenance": "exported",
        "title": "Fade of 1h swing highs and lows, with and without a 4h or daily swing nearby, against random levels",
        "date": "2026-10-31",
        "what": [
            er.W("Idea", "A 1h swing high or low that lines up with a 4h or daily swing is a stronger level, so fading it should do better than a plain 1h swing.", O),
            er.W("Swing", "Williams 5-bar swing on 1h, 4h and daily BTCUSDT bars; a level lives 96 hours", O),
            er.W("Confluence", "A 4h or daily swing (last 5 of that kind) within 0.5 ATR of the 1h level", O),
            er.W("Entry", "Fade at first touch of the level (touch = fill at the level, or the open if gapped; optimistic for a fade)", O),
            er.W("Stop / target / time exit", "Stop 1 ATR beyond the level, target +1 R, exit after 24 hours", O),
            er.W("Control", "Random levels drawn from the same distance distribution, 2 per real event", O),
            er.W("Fees", "Taker on both legs, 0.05 % per side (about 0.17 R per trade at a 1 ATR stop); no slippage", S),
            er.W("Test", "Real minus random, week-block bootstrap 95 % CI; shift null over the labels; a planted +0.3 % edge must be found", O),
        ],
        "how": "Every touch of a live 1h swing level inside DEV is replayed minute by minute on the rule above, and the same is done for random "
               "levels at matched distance. Groups: no confluence, 4h confluence, daily confluence. All parameters frozen in PRE_REG.md before the first run.",
        "window": WINDOW,
        "verdict": {"label": "FAIL: confluence levels lose more than random levels, fee-net", "tone": "bad"},
        "why": [
            "Confluence: n = %d, net %+.3f R per trade; random levels -0.160 R; real minus random -0.106 R (CI -0.143 to -0.070)." % (n_any, m_any),
            "No-confluence swings also lose (%+.3f R) and also trail their random control (-0.137 R)." % st["NONE"][1],
            "Before fees the rule is slightly negative too (stop 3,908 vs target 3,446 of 7,416 trades), so it is not only fees.",
            "n is far above the 551 needed to see 0.10 %, so this is not a thin-data null. Price tends to run through these levels, not respect them.",
            "Other tolerance, stop, target or horizon values are untested. Trading the opposite way is a new trial. No rule added.",
        ],
        "kpis": [
            {"label": "confluence trades (DEV)", "value": str(n_any)},
            {"label": "confluence net R per trade", "value": "%+.3f" % m_any, "tone": "bad"},
            {"label": "no-confluence net R (n=%d)" % st["NONE"][0], "value": "%+.3f" % st["NONE"][1], "tone": "bad"},
            {"label": "confluence minus random levels, R", "value": "-0.106 [-0.143, -0.070]", "tone": "bad"},
            {"label": "exits on confluence trades: stop / target / time", "value": "%d / %d / %d" % (ex.get("stop", 0), ex.get("target", 0), ex.get("time", 0))},
        ],
        "examples": [
            replay(trades, "R", "Trade replay (confluence trades only, time order)",
                   "Distance from entry in %; up is in favour of the trade. Time exits have no ladder. No prices.",
                   {"t2": "Target (1 R)", "t1": "Target (1 R)", "zero": "Entry (the level)", "l2": "Stop (1 ATR)"}),
            table("Real versus random levels", ["Group", "n real", "Net R", "95% CI", "n random", "Random net R", "Real minus random", "95% CI"], tab),
            table("Phase split (descriptive, no verdict)", ["Group", "Tag", "n", "Net R"], ph),
        ],
        "source_files": [rel("f1", "RESULT.md"), rel("f1", "PRE_REG.md"), rel("f1", "output.md"), rel("f1", "trades_pct.csv")],
        "commit": er.commit_of([os.path.join(FR, "f1")]),
    }


# ---------- F2 ----------
GATES = (("F2-1", "RSI-DIV-MTF", "A"), ("F2-2", "RSI-DIV-MTF", "B"), ("F2-3", "FADE", "A"), ("F2-4", "FADE", "B"))


def f2_events():
    return pd.read_csv(os.path.join(FR, "f2", "gate_events.csv"))


def f2_stats():
    g = f2_events()
    out = {}
    for tid, layer, which in GATES:
        d = g[g.layer == layer]
        k = (d.h < 0.45) if which == "A" else (d.h <= 0.55)
        out[tid] = {"layer": layer, "gate": which, "n_kept": int(k.sum()), "n_removed": int((~k).sum()),
                    "kept_mean": float(d.net_r[k].mean()), "removed_mean": float(d.net_r[~k].mean())}
    return out


def f2_result():
    g = f2_events()
    st = f2_stats()
    res = md_rows(os.path.join(FR, "f2", "RESULT.md"), "test")
    tab = [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[11]] for r in res]
    k = g[(g.layer == "FADE") & (g.h < 0.45)].reset_index(drop=True)
    trades = [{"d": r.time[:10], "s": 0, "f": "pivot fade kept by the gate (H %.2f)" % r.h, "r": round(float(r.net_r), 3)} for r in k.itertuples()]
    cells = [[tid, v["layer"], "H < 0.45" if v["gate"] == "A" else "H <= 0.55", v["n_kept"], "%+.3f" % v["kept_mean"],
              v["n_removed"], "%+.3f" % v["removed_mean"]] for tid, v in st.items()]
    return {
        "id": "fractals-f2-hurst-gate", "kind": "backtest", "parity": None, "family": FAMILY, "provenance": "exported",
        "title": "Rolling 1h Hurst (DFA) regime gate on the RSI divergence and the swing-fade trades",
        "date": "2026-10-31",
        "what": [
            er.W("Idea", "Mean-reversion trades should work better when the market has been anti-persistent (low Hurst H) and worse when it trends.", S),
            er.W("Hurst estimate", "DFA-1 on 480 hourly returns, scales 8 to 160, known at the close of its last bar (FORMULAS.md s27)", S),
            er.W("Gate A", "Keep trades only when H < 0.45", S),
            er.W("Gate B", "Drop trending hours: keep H <= 0.55", S),
            er.W("Trades gated", "The 640 RSI divergence events of P1b and the 7,416 F1 pivot-fade trades; outcomes unchanged, fees as in those studies", O),
            er.W("Test", "Lift = mean net R of kept minus removed, week-block bootstrap 95 % CI; shuffled-H, random-gate and circular-shift nulls; two time splits", O),
            er.W("Planted edge", "+0.25 R on kept RSI events must be found by the family-wise null (it was not: kept n too small)", O),
        ],
        "how": "No trade is re-run. Each frozen trade list gets the H value known at its entry time, is split into kept and removed by the gate, "
               "and the difference in mean net R is tested against three nulls. Events in the first 20 days (no H yet) are dropped and counted.",
        "window": WINDOW,
        "verdict": {"label": "Negative: no gate test passes; the low-H gate points the wrong way on the fade", "tone": "bad"},
        "why": [
            "Best lift is +0.123 R [-0.109, +0.358] (RSI, gate B), not different from zero.",
            "On the fade, gate A lifts -0.062 R (CI upper bound -0.0006, borderline wrong way); with 4 tests that is not a finding on its own.",
            "Every kept side stays negative after fees (best -0.20 R), so even a real lift would not make a tradable gate.",
            "The RSI tests are underpowered: the pre-registered +0.25 R plant was not flagged with only 119 kept events. Read them as 'not shown', not 'absent'.",
            "The 0.45 and 0.55 cut-offs are vendor anecdote on a 20-day window; other windows or thresholds are new trials. No gate added.",
        ],
        "kpis": [
            {"label": "tests passed", "value": "0 of 4", "tone": "bad"},
            {"label": "F2-3 fade, gate A: kept n / net R", "value": "%d / %+.3f" % (st["F2-3"]["n_kept"], st["F2-3"]["kept_mean"]), "tone": "bad"},
            {"label": "F2-4 fade, gate B: kept n / net R", "value": "%d / %+.3f" % (st["F2-4"]["n_kept"], st["F2-4"]["kept_mean"]), "tone": "bad"},
            {"label": "F2-1 RSI, gate A: kept n / net R", "value": "%d / %+.3f" % (st["F2-1"]["n_kept"], st["F2-1"]["kept_mean"])},
            {"label": "F2-2 RSI, gate B: kept n / net R", "value": "%d / %+.3f" % (st["F2-2"]["n_kept"], st["F2-2"]["kept_mean"])},
            {"label": "events with an H value: RSI / fade", "value": "%d / %d" % ((g.layer == "RSI-DIV-MTF").sum(), (g.layer == "FADE").sum())},
        ],
        "examples": [
            replay(trades, "R", "Trade replay (F2-3: fade trades kept by gate A, time order)",
                   "Net R per kept trade, running total below. Side is not stored in this list, so no long/short; no prices."),
            table("Gate tests (lift = kept minus removed)", ["Test", "Layer", "Gate", "Events kept", "Events removed", "Kept net R [CI]", "Lift [CI]", "Verdict"], tab),
            table("Kept versus removed, recomputed from the event list", ["Test", "Layer", "Gate", "n kept", "Kept net R", "n removed", "Removed net R"], cells),
        ],
        "source_files": [rel("f2", "RESULT.md"), rel("f2", "PRE_REG.md"), rel("f2", "output.md"), rel("f2", "gate_events.csv")],
        "commit": er.commit_of([os.path.join(FR, "f2")]),
    }


# ---------- F3 ----------
def f3_trades():
    return pd.read_csv(os.path.join(FR, "f3", "trades_pct.csv"))


def f3_stats():
    t = f3_trades()
    return {k: {"n": len(d), "mean_pct": float(d.net_pct.mean()), "hit": float((d.net_pct + RT_PCT > 0).mean())} for k, d in t.groupby("variant")}


def f3_result():
    t = f3_trades()
    st = f3_stats()
    u = t[t.variant == "UNFILT"].reset_index(drop=True)
    trades = [{"d": r.time[:10], "s": 1 if r.side == "long" else -1, "f": "analog forecast, 24 h hold", "r": round(float(r.net_pct), 3)}
              for r in u.itertuples()]
    rows = md_rows(os.path.join(FR, "f3", "RESULT.md"), "variant")
    tab = [[r[0], r[1], r[2], r[3], r[4], r[6], r[7], r[8], r[9]] for r in rows]
    return {
        "id": "fractals-f3-phase-analogs", "kind": "backtest", "parity": None, "family": FAMILY, "provenance": "exported",
        "title": "Nearest-neighbour analog forecast on 1h BTC, with and without matching the market phase",
        "date": "2026-10-31",
        "what": [
            er.W("Idea", "Find the 10 past 48-hour price shapes most like now (z-scored), and trade the next 24 hours the way they went if 70 % or more agree.", O),
            er.W("Query / library", "48 hourly bars; the library expands from about 83 days (2000 windows warm-up); neighbours at least 48 bars apart", O),
            er.W("Neighbours / agreement", "k = 10, agreement at least 70 %", O),
            er.W("Phase variant", "Neighbours must share the Cowen-side and 200-day-side tag of the query day", O),
            er.W("Hold / queries", "24 hours; 1,190 non-overlapping queries, split A and B at 2023-11-13", O),
            er.W("Fees", "Taker both legs, 0.10 % round trip; no slippage", S),
            er.W("Controls", "Random-walk surrogate libraries and block-shuffled outcomes, 300 draws each; Holm over 4 tests; week-block bootstrap 95 % CI", O),
        ],
        "how": "For each non-overlapping query the nearest past shapes vote on direction; when 70 % agree a 24-hour trade is taken and charged the "
               "round trip. The same procedure on random-walk libraries and on shuffled outcomes gives the luck range. Single k, agreement and horizon: no tuning, by design.",
        "window": WINDOW,
        "verdict": {"label": "No edge: both variants inconclusive and below both controls (honest negative, underpowered to prove a loss)", "tone": "warn"},
        "why": [
            "Unfiltered: %d trades, net %+.3f %% per trade, hit rate %.1f %% (a coin flip pays the 0.10 %% round trip)." % (
                st["UNFILT"]["n"], st["UNFILT"]["mean_pct"], 100 * st["UNFILT"]["hit"]),
            "Phase-matched: %d trades, net %+.3f %% per trade. The phase tag halves the usable library and adds nothing (difference -0.061 %%, CI -0.371 to +0.234)." % (
                st["PHASE"]["n"], st["PHASE"]["mean_pct"]),
            "Both are below the random-walk and shuffled controls (p 0.80 to 0.92); Holm-adjusted p is 1.00.",
            "Split A -0.51 versus B +0.07 is the sign of noise: per-trade sd is 2.7 %, so 0.10 % needs about 5,900 trades and this study has 368.",
            "The CI straddles zero, so FAIL is not triggered. No rule, gate or layer added. The replay below shows net percent per trade.",
        ],
        "kpis": [
            {"label": "unfiltered trades / net % per trade", "value": "%d / %+.3f %%" % (st["UNFILT"]["n"], st["UNFILT"]["mean_pct"]), "tone": "bad"},
            {"label": "phase-matched trades / net % per trade", "value": "%d / %+.3f %%" % (st["PHASE"]["n"], st["PHASE"]["mean_pct"]), "tone": "bad"},
            {"label": "hit rate, unfiltered", "value": "%.1f %%" % (100 * st["UNFILT"]["hit"])},
            {"label": "queries answered (unfiltered / phase)", "value": "1190 / 1100"},
            {"label": "trades needed to see 0.10 %", "value": "about 5,900"},
        ],
        "examples": [
            replay(trades, "%", "Trade replay (unfiltered analog trades, time order)",
                   "Net percent per trade after the round trip; running total below. No prices."),
            table("Variants against controls", ["Variant", "Forecasts (A/B)", "Trades", "Hit", "Net % per trade", "Week-boot 95% CI", "RW surrogate mean [CI] (p)", "SHUF mean [CI] (p)", "Mean A / B"], tab),
        ],
        "source_files": [rel("f3", "RESULT.md"), rel("f3", "PRE_REG.md"), rel("f3", "output.md"), rel("f3", "trades_pct.csv")],
        "commit": er.commit_of([os.path.join(FR, "f3")]),
    }


# ---------- F4 ----------
def f4_result():
    t = pd.read_csv(os.path.join(FR, "f4", "events.csv"))
    r = t[(t["set"] == "RULE-cont") & (t.h == 6)].reset_index(drop=True)
    trades = [{"d": x.entry_time[:10], "s": 1 if x.side == "long" else -1, "f": "8h squeeze-break continuation short, 48 h hold", "r": round(float(x.net_r), 3)}
              for x in r.itertuples()]
    rows = md_rows(os.path.join(FR, "f4", "RESULT.md"), "set")
    tab = [[c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[8]] for c in rows]
    return {
        "id": "fractals-f4-8h-state-analogs", "kind": "backtest", "parity": None, "family": FAMILY, "provenance": "exported",
        "title": "8h look-alikes of the operator breakdown setup (BB squeeze-break, volume spike, RSI, StochRSI, CVD proxy)",
        "date": "2026-10-31",
        "what": [
            er.W("Idea", "Find past 8h bars that look like the setup (price shape plus indicator state) and see what a short or a fade did after, fee-net.", O),
            er.W("Rule event", "Bollinger bandwidth in the lowest 30 % of the last 90 bars, 6 or more bars inside the bands, then an 8h close below the lower band on volume z of 2 or more", O),
            er.W("Analog event", "20 nearest past breakdown closes on a 24-bar path and 7 indicator values; the neighbours own results pick the side", O),
            er.W("Trade", "Continuation short (stop at the signal bar high) or fade long (stop at the low), 2R target, 3 / 6 / 9 bars", S),
            er.W("Fees", "Taker both legs, fees.BINANCE_TAKER", S),
            er.W("Controls", "Random bars with matched volatility, random breakdown bars, month-block bootstrap, Holm over 9 tests", O),
        ],
        "how": "Each event is entered at the next open and walked on 1h bars to a stop, a 2R target or the time exit. Only 28 to 36 trades exist per set, far below the 550 to 2,400 needed to see 0.10 R.",
        "window": "Binance spot 2017-08-17 to 2025-06-30 (HOLDOUT 2025-07+ never loaded)",
        "verdict": {"label": "No edge: continuation inconclusive, fade fails, analog negative; too few events to decide", "tone": "warn"},
        "why": [
            "Continuation short: +0.109 / -0.115 / -0.138 R per trade at 3 / 6 / 9 bars, all confidence bands cross zero.",
            "Fade long: about -0.5 R at every horizon; the upper confidence bound is below zero (FAIL).",
            "Analog selection: +0.02 / -0.56 / -0.50 R, fewer than 30 trades at 6 and 9 bars.",
            "The card baseline in R is distorted by tiny-risk random bars; a post-hoc percent control shows only the 3-bar continuation standing out (n 36): a lead for the forward log.",
        ],
        "kpis": [
            {"label": "rule events (7.9 years)", "value": "36"},
            {"label": "continuation 6 bars, net R", "value": "-0.115", "tone": "bad"},
            {"label": "fade 6 bars, net R", "value": "-0.506", "tone": "bad"},
            {"label": "trades needed for 0.10 R", "value": "550 - 2,400"},
        ],
        "examples": [
            replay(trades, "R", "Trade replay (continuation short, 6 bars, time order)", "Fee-net R per trade; running total below. No prices."),
            table("Sets against controls", ["Set", "Bars", "Trades", "Hit", "Net R", "Month-boot 95% CI", "Halves A / B", "Verdict"], tab),
        ],
        "source_files": [rel("f4", "RESULT.md"), rel("f4", "PRE_REG.md"), rel("f4", "output.md"), rel("f4", "events.csv")],
        "commit": er.commit_of([os.path.join(FR, "f4")]),
    }


# ---------- phase tag ----------
def phase_result():
    t = pd.read_csv(os.path.join(FR, "phase_tag", "tags.csv"))
    rows = []
    for col in ("cowen_side", "sma200_side", "sma400_side", "wsma10_phase", "dd_bin", "cycle_year"):
        for cell, n in t[col].value_counts().items():
            rows.append([col, str(int(cell)) if isinstance(cell, float) else str(cell), int(n), "%.1f %%" % (100 * n / len(t))])
    return {
        "id": "fractals-phase-tag", "kind": "audit", "parity": None, "family": FAMILY, "provenance": "exported",
        "title": "BTC market-phase tags (cycle year, drawdown, Cowen band, 200/400-day and weekly averages): days in each cell",
        "date": "2026-10-31",
        "what": [
            er.W("What it is", "A daily tag table used to split other tests by market phase; it is not a trade test and has no R.", O),
            er.W("Causality", "The tag of day t uses only daily bars closed on day t-1 or earlier", O),
            er.W("Halving dates", "2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20 (block timestamps)", S),
            er.W("Cycle year / drawdown bins", "1 + floor(days since halving / 365) capped at 4; drawdown from the running close-ATH: shallow above -20 %, mid -20 to -50 %, deep below -50 %", O),
            er.W("Cowen band, averages", "Cowen band side (FORMULAS.md), 200-day and 400-day average side, weekly 10-average above/below and up/down", S),
            er.W("Data", "BTCUSDT spot daily closes, 2017-08-17 to 2026-09-30", S),
        ],
        "how": "One row per UTC day. The harness checks that a changed bar t leaves the tag of day t alone but changes day t+1, that a planted edge in one cell is found "
               "72 to 100 % of runs at the stated n, and that a no-edge run flags nothing. The P1 split itself was blocked until P1b supplied a frozen event list.",
        "window": "Tag series 2017-08-17 to 2026-09-30 (a descriptive table; the trade studies that use it stay on DEV 2022-01 to 2025-06)",
        "verdict": {"label": "Built and tested (15 tests); descriptive only, never a trigger", "tone": "info"},
        "why": [
            "%d daily rows; every cell describes where price sits, not a forecast." % len(t),
            "Only 2 to 3 cycles exist, so cycle-year cells are descriptive and never a rule.",
            "Used by P1b, F1 and F3 to split results by phase; none of them found a phase in which the tested trade turns positive.",
        ],
        "kpis": [
            {"label": "daily rows", "value": str(len(t))},
            {"label": "tests passing", "value": "15"},
            {"label": "planted edge found", "value": "72 to 100 % of runs"},
        ],
        "examples": [table("Days per tag cell", ["Tag", "Cell", "Days", "Share"], rows, "Blank (nan) rows are the warm-up before each average exists."),
                     er.none_example()],
        "source_files": [rel("phase_tag", "phase_tag.py"), rel("phase_tag", "tags.csv"), rel("SYNTHESIS.md"), rel("p1_split", "RESULT.md")],
        "commit": er.commit_of([os.path.join(FR, "phase_tag")]),
    }


def build_all():
    return [p1b_result(), f1_result(), f2_result(), f3_result(), f4_result(), phase_result()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=er.DEFAULT_OUT)
    a = ap.parse_args(argv)
    return [er.write(a.out, r) for r in build_all()]


if __name__ == "__main__":
    print("\n".join(main()))
