"""Export committed audit/study outputs to the standard simulator result files.

Writes sim_desk/results/<test_id>.json (schema: DESIGN.md "Result files"). Read-only on the sources;
DEV window only; no prices are written (percent distances and timestamps only).

Usage: python export_results.py [--out DIR]
"""
import argparse
import csv
import datetime as dt
import json
import os
import subprocess
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.normpath(os.path.join(HERE, ".."))
AUDIT = os.path.join(RESEARCH, "dsa_backtest_audit_2026-10-16")
LEVELS = os.path.join(RESEARCH, "levels_confluence_2026-10-14")
DEFAULT_OUT = os.path.join(HERE, "results")
DEV_TXT = "DEV only, 2022-04-01 to 2024-06-30 (sealed VALIDATION and HOLDOUT windows were not read)"


def commit_of(paths):
    try:
        out = subprocess.run(["git", "-C", RESEARCH, "log", "-1", "--format=%h", "--"] + list(paths),
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def rel(p):
    return os.path.relpath(p, os.path.join(RESEARCH, "..", "..")).replace("\\", "/")


def day(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def W(name, value, label):
    return {"name": name, "value_plain": value, "label": label}


def none_example(text="no example trades exported"):
    return {"kind": "none", "title": "Examples", "caption": text}


def csv_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---------- levels ladder (v1, fixed) ----------
def levels_result(data):
    """data = build_artifact.build_data(...) (filled trades only)."""
    d = data["dev"]
    n = data["n"]
    return {
        "id": "levels_ladder", "kind": "backtest", "parity": None, "family": "Price levels", "title": "Levels ladder (bounce at key levels)",
        "what": [
            W("Idea", "When price first touches a key level in a day (4h swing highs and lows, untested volume peaks, "
              "yesterday's high, low and volume peak, last week's high, round thousands), bet that it bounces.", "OURS"),
            W("Timeframe / market", "BTCUSDT, 5-minute candles for the filter, 1-minute for fills", "OURS"),
            W("Entry filter", "Only if the 14-period RSI on 5-minute candles still reads above 40 for a long, below 60 for a short.", "OURS"),
            W("Entry style", "Do not buy at the touched level: place the whole order at the next level beyond it, against the trade. "
              "If price never gets there the idea is never filled.", "OURS"),
            W("Stop", "0.10 % past the day's extreme so far (pushed past the deeper level if needed).", "OURS"),
            W("Exit", "Take profit at the first level in favour (target 1), or at twice the stop distance, whichever the rule picks.", "OURS"),
            W("Fees", "0.02 % for resting orders, 0.05 % for stops and market exits. No slippage.", "SOURCED"),
            W("How the rule was picked", "Best of 240 variants on DEV (needs at least 200 ideas), so the number is flattering by construction.", "OURS"),
        ],
        "how": "Every idea in DEV is replayed minute by minute with the rule above. Only ideas that actually filled count as trades. "
               "Results are in R (one R = the planned loss of that trade) after fees.",
        "window": DEV_TXT,
        "verdict": {"label": "Does not pay: FAIL", "tone": "bad"},
        "why": [
            "Fees eat the edge. Before fees the rule earns %+.3f R per filled trade; fees cost %.3f R. Net %+.3f R per trade."
            % (d["mean_gross_r"], d["mean_fee_r"], d["mean"]),
            "%d of %d filled trades won (%.1f %%). The best single trade is %+.2f R, the worst %+.2f R, and the deepest losing run is %.1f R." % (data["wins"], n, data["wins"] / n * 100, data["best"], data["worst"], d["maxdd"]),
            "The rule is the best of 240 tries, which flatters it, and it is still below zero.",
            "%d of %d ideas never filled (price never reached the deeper entry). They are not trades and are left out of every number above."
            % (data["unfilled"], data["ideas_selected"]),
            "The 'power' figures in the frozen rule file were computed over all 772 ideas including unfilled ones, so they are not repeated here.",
            "Default: park the idea. Nothing is read on VALIDATION.",
        ],
        "kpis": [
            {"label": "trades filled", "value": str(n)},
            {"label": "ideas never filled", "value": str(data["unfilled"])},
            {"label": "mean net R per trade", "value": "%+.3f" % d["mean"], "tone": "bad"},
            {"label": "win rate (filled)", "value": "%.1f%%" % (data["wins"] / n * 100)},
            {"label": "mean R before fees", "value": "%+.3f" % d["mean_gross_r"]},
            {"label": "mean fee R", "value": "-%.3f" % d["mean_fee_r"]},
            {"label": "worst drawdown", "value": "%.1f R" % d["maxdd"]},
            {"label": "ROI: 1,000 USD start, 1 %% risk per trade, simple sum (OURS), %s to %s" % (data["trades"][0]["d"], data["trades"][-1]["d"]),
             "value": "%d USD" % round(1000 * (1 + 0.01 * data["cum"][-1])), "tone": "bad" if data["cum"][-1] < 0 else "good"},
        ],
        "examples": [
            {"kind": "replay", "title": "Trade replay (filled trades only, in time order)",
             "caption": "Percent distance from the touched level; up is in favour of the trade. No prices.",
             "trades": data["trades"], "cum": data["cum"]},
            {"kind": "table", "title": "Stop choice alone (all ideas, single entry)", "cols": ["Stop", "Ideas", "Mean net R"],
             "rows": [[s["k"], s["n"], "%+.3f" % s["m"]] for s in data["stops"]],
             "caption": "Every stop type loses on average before any filter is added."},
        ],
        "source_files": [rel(os.path.join(LEVELS, "frozen_rule.json")), rel(os.path.join(LEVELS, "ladder_ideas_dev.csv"))],
        "commit": commit_of([LEVELS]),
    }


# ---------- T09 live parity ----------
def t09_result():
    out = os.path.join(AUDIT, "scripts", "T09", "out")
    par = json.load(open(os.path.join(out, "parity_result.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(out, "exit_result.json"), encoding="utf-8"))
    rows, nobt = [], []
    for k, v in sorted(par["per_key"].items()):
        b = v.get("backtest")
        name = k.split("|", 1)[1].replace("|", " ")
        if not b:
            nobt.append([name, v["live_alerts"]])
            continue
        live = b["same"] + b["side_diff"] + b["off_by_one"] + b["live_only"]
        rows.append([name, live, b["n"], b["same"], b["side_diff"], b["off_by_one"], b["live_only"], b["bt_only"]])
    side_sum = sum(r[4] for r in rows)

    fvg = []
    for key in ("fabio|volume_fvg|15m", "fabio|volume_fvg|1h"):
        tf = key.split("|")[2]
        for t in par["per_key"][key]["backtest"]["examples"]["side_diff"]:
            fvg.append({"when": "%s UTC (%s)" % (day(t), tf), "live": "opposite", "backtest": "reference"})
    rsi = []
    ev = OrderedDict()
    for tf in ("5m", "15m", "1h"):
        b = par["per_key"]["rsi|rsi_events|" + tf]["backtest"]
        ev[tf] = b["live_only_by_event"]
        for t, s in b["examples"]["live_only"][:3]:
            rsi.append({"when": "%s UTC (%s)" % (day(t), tf), "live": s, "backtest": None})
    kinds = ["cross", "failure", "rejection", "support"]
    ev_rows = [[tf] + [ev[tf].get(k, 0) for k in kinds] for tf in ev]

    def avg(a, b2, key):
        return round((a[key] + b2[key]) / 2 * 100, 1)

    def stack(label, rule):
        l, s = rule["long"], rule["short"]
        return {"label": label, "parts": [{"name": "stop", "value": avg(l, s, "stop"), "tone": "bad"},
                                           {"name": "target", "value": avg(l, s, "target"), "tone": "good"},
                                           {"name": "time", "value": avg(l, s, "time"), "tone": "mute"}]}
    live_stack = [stack("%s (hold %d min)" % (tf, r["hold_minutes"]), r) for tf, r in ex["live_rule"].items()]
    bt_stack = [stack("%s backtest-style hold (%d min)" % (tf, r["hold_minutes"]), r) for tf, r in ex["backtest_rsi_rule"].items()]
    srcs = [rel(os.path.join(AUDIT, "T09_live_parity.md")), rel(os.path.join(out, "parity_result.json")), rel(os.path.join(out, "exit_result.json"))]
    return {
        "id": "t09_live_parity", "kind": "audit", "parity": None, "family": "Audit: backtest vs live", "title": "Does the live code trade what was backtested?",
        "what": [
            W("Question", "The testnet layers run their own code. Does that code fire the same signals, on the same bars and sides, as the backtest that justified each layer?", "OURS"),
            W("Days replayed", "%d DEV days, seed %d (10 trend, 10 range, 10 high-volatility), 3 h warm-up each, no network." % (len(par["days"]), par["seed"]), "OURS"),
            W("Live exit rule", "Market entry, stop 1 %, target 2 %, close after 8 bars of the signal timeframe.", "SOURCED"),
            W("Exit study", "All DEV 1-minute bars, entry every 5 to 60 minutes, both sides; stop wins ties inside a bar.", "OURS"),
        ],
        "how": "The live layer code is replayed bar by bar on the sampled days and each signal is matched to the backtest's own signal function "
               "(same time and side = same). Separately, the live 1 % / 2 % / 8-bar bracket is simulated on every DEV minute to see how trades end.",
        "window": DEV_TXT + "; 30 sampled days",
        "verdict": {"label": "Backtests do not describe live for 5 layer families", "tone": "bad"},
        "why": [
            "volume_fvg trades the opposite side of the backtested reading: 0 of 24 matched signals have the same side (%d side differences in the table)." % side_sum,
            "The RSI layer trades events (cross, failure, rejection@40) that no backtest covered: 5m 384 of 461 signals, 15m 126 of 147, 1h 25 of 28.",
            "Every layer exits by one fixed 1 % / 2 % / 8-bar bracket that no backtest used. About 94 % time exits follow from that bracket alone (5m), not from bad luck.",
            "Good news: turn_of_candle, session_momentum, cvd_absorption, sr_flip and failed_msb match bit for bit (0 differences in 3,200+ signals).",
        ],
        "kpis": [
            {"label": "days replayed", "value": str(len(par["days"]))},
            {"label": "layers with a backtest to compare", "value": str(len(rows))},
            {"label": "volume_fvg side differences", "value": str(side_sum), "tone": "bad"},
            {"label": "5m time exits (bracket)", "value": "%.0f%%" % live_stack[1]["parts"][2]["value"]},
            {"label": "network attempts", "value": str(par["network_attempts"])},
        ],
        "examples": [
            {"kind": "table", "title": "Per layer: live vs backtest signals",
             "cols": ["Layer", "Live", "Backtest", "Same", "Side differs", "Off by 1 bar", "Live-only", "Backtest-only"], "rows": rows,
             "caption": "Same = same bar and same side. Live-only = live trades it, no backtest ever did. Backtest-only = backtest had it, live never fires."},
            {"kind": "table", "title": "Live layers with no backtest located", "cols": ["Layer", "Live alerts"], "rows": nobt,
             "caption": "Nothing to compare against."},
            {"kind": "sides", "title": "volume_fvg: same bar, opposite sides",
             "caption": "Each row is a bar where both signal. Live goes the opposite way to the backtest (live code: short when the close is above mid; backtest: long). "
                        "Which direction each bar had is not exported, so only 'opposite' is drawn.",
             "rows": fvg},
            {"kind": "sides", "title": "RSI: signals only live trades (3 per timeframe)",
             "caption": "Backtest column empty = no backtest ever produced this event.", "rows": rsi},
            {"kind": "table", "title": "RSI live-only events by type", "cols": ["Timeframe", "cross", "failure", "rejection", "support"], "rows": ev_rows,
             "caption": "Only 'support' at 40 (long) and 'rejection' at 60 (short) were ever backtested."},
            {"kind": "stack", "title": "How live trades end (1 % stop, 2 % target, 8 bars)", "unit": "% of trades",
             "rows": live_stack,
             "caption": "8-bar bracket: the position is closed at market after 8 candles of its own timeframe. A 1 % move rarely happens in 8 one-minute candles, so almost everything ends on the clock."},
            {"kind": "stack", "title": "Same bracket with the RSI backtest's long hold", "unit": "% of trades", "rows": bt_stack,
             "caption": "The backtest held 100 bars; stops and targets decide most trades there."},
        ],
        "source_files": srcs, "commit": commit_of([os.path.join(AUDIT, "T09_live_parity.md"), out]),
    }


# ---------- T06 cost / fill realism ----------
def t06_result():
    be = csv_rows(os.path.join(AUDIT, "scripts", "T06", "breakeven.csv"))
    rows = [[r["study"], r["arm"], r["n"], r["gross_pct"], r["charged_rt_pct"], r["breakeven_rt_cost_bp"]] for r in be]
    pos = sum(1 for r in be if float(r["breakeven_rt_cost_bp"]) > 10)
    return {
        "id": "t06_cost_fill", "kind": "audit", "parity": None, "family": "Audit: costs and fills", "title": "What would we really have paid and got?",
        "what": [
            W("Question", "Are the fees, slippage, funding and fill rules used in the backtests realistic, and does fixing them flip any verdict?", "OURS"),
            W("Scan", "Every fee, slippage and funding constant in backtest/ and research/: 201 hits in 70+ files.", "OURS"),
            W("Funding rerun", "Five recent screens rerun with the real signed 8-hour funding instead of a flat 1 basis point (0.01 %).", "SOURCED"),
            W("Fee reference", "Deribit taker 0.05 %, maker 0 %; Binance taker 0.05 %, maker 0.02 % (fees.py).", "SOURCED"),
        ],
        "how": "Constants are found by regex and tabulated; funding is swapped for the real series and each screen is rerun (the flat run first reproduces the published numbers). "
               "Break-even cost = the round-trip fee at which an arm's average gross result is zero.",
        "window": DEV_TXT,
        "verdict": {"label": "No arm earns even the cheapest realistic fee", "tone": "bad"},
        "why": [
            "The funding data was never found (wrong folder), so every screen charged a flat 1 bp to both longs and shorts instead of the real signed rate. Fixing it flips no verdict (largest move +0.018 percentage points).",
            "57 of the 70 files that set a cost define their own constant instead of importing fees.py, so net numbers are not comparable across studies (the same gross trade nets -0.10 % to -0.20 % depending on the file).",
            "Costs, not funding, decide every verdict: the best measured gross edge is +3.6 bp, all-taker Deribit costs 10 bp round trip.",
        ],
        "kpis": [
            {"label": "cost constants found", "value": "201"},
            {"label": "files with own constant", "value": "57 of 70", "tone": "warn"},
            {"label": "verdicts changed by real funding", "value": "0"},
            {"label": "arms above a 10 bp break-even", "value": str(pos), "tone": "bad" if pos == 0 else "good"},
        ],
        "examples": [
            {"kind": "table", "title": "Break-even cost per arm (bp round trip)",
             "cols": ["Study", "Arm", "Trades", "Gross mean %", "Charged RT %", "Break-even bp"], "rows": rows,
             "caption": "Compare the break-even with 10 bp (all-taker Deribit) or 14 bp (with slippage): every arm is below."},
            none_example(),
        ],
        "source_files": [rel(os.path.join(AUDIT, "T06_cost_fill_realism.md")), rel(os.path.join(AUDIT, "scripts", "T06", "breakeven.csv"))],
        "commit": commit_of([os.path.join(AUDIT, "T06_cost_fill_realism.md"), os.path.join(AUDIT, "scripts", "T06")]),
    }


# ---------- T07 stale verdicts ----------
def t07_result():
    rd = csv_rows(os.path.join(AUDIT, "scripts", "T07", "out", "rerun_diff.csv"))
    agg = OrderedDict()
    for r in rd:
        a = agg.setdefault(r["result"], {"match": 0, "diff": 0, "other": 0})
        s = r["status"]
        a["match" if s == "MATCH" else "diff" if s == "DIFF" else "other"] += 1
    rows = []
    for name, a in agg.items():
        tot = a["match"] + a["diff"] + a["other"]
        rows.append([name, tot, a["match"], a["diff"], "reproduces" if a["diff"] == 0 and a["other"] == 0 else "does NOT reproduce"])
    rows.append(["published_strats", "-", "-", "-", "could not rerun (data folders absent)"])
    good = sum(1 for r in rows if r[4] == "reproduces")
    return {
        "id": "t07_stale_verdicts", "kind": "audit", "parity": None, "family": "Audit: reruns", "title": "Do the published numbers still come out of today's code?",
        "what": [
            W("Question", "For 16 published verdicts: has the code behind each one changed since, and does a rerun on today's code give the same numbers?", "OURS"),
            W("Reruns", "10 results rerun on today's code in a sandbox copy; counts must match exactly, returns within 1e-6.", "OURS"),
            W("Data", "DEV bars only.", "OURS"),
        ],
        "how": "Git history says which code made each verdict and whether it changed. Each result is rerun and every published number is compared with the new one (%d numbers compared)." % len(rd),
        "window": DEV_TXT,
        "verdict": {"label": "No verdict flips; mfe_exit does not reproduce, published_strats could not be rerun", "tone": "warn"},
        "why": [
            "%d results reproduce every number exactly (7 had code changes since publishing, none moved a number). The audit text says 8 of 10; its own comparison file shows 9 matching, so the table below is used." % good,
            "mfe_exit does not reproduce: today's fire files label a different TRAIN window, so the published DEV-only rerun is not repeatable (its 'nothing survives' verdict is untested by it).",
            "published_strats cannot be rerun on this machine because its data folders are absent.",
            "A determinism check (one study run twice) gave identical outputs.",
        ],
        "kpis": [
            {"label": "numbers compared", "value": str(len(rd))},
            {"label": "results reproducing exactly", "value": "%d" % good, "tone": "good"},
            {"label": "not reproducing", "value": "1 (mfe_exit)", "tone": "bad"},
            {"label": "could not rerun", "value": "1", "tone": "warn"},
        ],
        "examples": [
            {"kind": "table", "title": "Rerun results", "cols": ["Result", "Numbers compared", "Match", "Differ", "Status"], "rows": rows,
             "caption": "mfe_exit return values are withheld in the source (they touched a sealed window by accident); only counts are shown."},
            none_example(),
        ],
        "source_files": [rel(os.path.join(AUDIT, "T07_stale_verdicts.md")), rel(os.path.join(AUDIT, "scripts", "T07", "out", "rerun_diff.csv"))],
        "commit": commit_of([os.path.join(AUDIT, "T07_stale_verdicts.md"), os.path.join(AUDIT, "scripts", "T07", "out")]),
    }


# ---------- WaveTrend atlas (parsed from the committed RESULT.md table) ----------
def wavetrend_result():
    p = os.path.join(RESEARCH, "wavetrend_2026-10-17", "RESULT.md")
    txt = open(p, encoding="utf-8").read()
    ver = next(l for l in txt.splitlines() if l.startswith("Verdict:"))
    sec = txt.split("## Primary arms", 1)[1].split(chr(10) + "## ", 1)[0]
    rows = []
    for l in sec.splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) == 5 and c[0].startswith("W"):
            rows.append(c)
    fails = sum(1 for r in rows if r[4] == "FAIL")
    return {
        "id": "wavetrend_atlas", "kind": "backtest", "parity": None, "family": "WaveTrend",
        "title": "WaveTrend behaviour atlas (9 frozen cells)",
        "what": [
            W("Idea", "WaveTrend (LazyBear) oscillator events on BTCUSDT: touches of the +/-53 band, crosses and pivots, each in a context of trend, higher-timeframe zone, volatility or time of day.", "OURS"),
            W("Oscillator settings", "hlc3, EMA 10, EMA 21, SMA 4, 0.015, bands +/-53 and +/-60", "SOURCED"),
            W("Outcome", "Signed return from the open after the event to the close 12 bars later, in the direction the event implies, before fees and funding.", "OURS"),
            W("Cells and tests", "9 cells frozen before the run, Holm correction over 9 (no tuning after the result).", "OURS"),
            W("Costs", "None: this is a gross behaviour table, not a strategy test.", "OURS"),
        ],
        "how": "Count events, then measure the gross 12-bar outcome for each frozen cell and compare with the same events without the context, the indicator alone and a random clock. Nothing is adopted from it.",
        "window": DEV_TXT,
        "verdict": {"label": "INCONCLUSIVE: 0 of 9 cells pass the gross screen", "tone": "warn"},
        "why": ["%d of %d primary arms are marked FAIL; the other cells carry no tuned rule." % (fails, len(rows)),
                "Every mean is within a few hundredths of a percent and mostly inside its standard error, so there is no sign of an edge even before fees.",
                "Verdict as written: " + ver[len("Verdict:"):].replace("**", "").strip()[:260]],
        "kpis": [{"label": "primary arms", "value": str(len(rows))}, {"label": "arms failing", "value": str(fails), "tone": "bad"},
                 {"label": "arms passing", "value": str(len(rows) - fails)}],
        "examples": [{"kind": "table", "title": "Primary arms (gross, % per event)", "cols": ["Arm", "Events", "Mean %", "Std error %", "Verdict"],
                      "rows": [[r[0], r[1], r[2], r[3], r[4]] for r in rows],
                      "caption": "Gross mean of the 12-bar signed return. No example trades exported: this study counts events, it has no trade list."}],
        "source_files": [rel(p)], "commit": commit_of([p]),
    }


def write(out_dir, res):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, res["id"] + ".json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return p


def main(argv=None):
    import sys
    sys.path.insert(0, os.path.join(HERE, "artifact"))
    import build_artifact as ba
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    rule, rows = ba.load(ba.DEFAULT_SRC)
    outs = [levels_result(ba.build_data(rule, rows)), t09_result(), t06_result(), t07_result(), wavetrend_result()]
    return [write(a.out, r) for r in outs]


if __name__ == "__main__":
    print("\n".join(main()))
