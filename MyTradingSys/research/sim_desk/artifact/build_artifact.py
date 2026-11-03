"""Build artifact/index.html: the test simulator page, from every sim_desk/results/<id>.json.

One page, many tests: a new test appears by adding one JSON file (schema in sim_desk/DESIGN.md). Nothing is
computed in the page. The levels-ladder numbers (build_data below) are exported to results/ by
export_results.py from the precomputed LC3 ladder DEV results (standard DEV 2022-04-01..2024-06-30 only;
VALIDATION and HOLDOUT are never read). No price levels are written: trades are percent distances.

Usage: python build_artifact.py [--results DIR] [--out FILE]
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.normpath(os.path.join(HERE, "..", "..", "levels_confluence_2026-10-14"))
FROZEN_COL = "S2_K5_X0_2R"
STOP_COLS = ["S0_K1_X1", "S0_K2_X1", "S0_K3_X1", "S0_K4_X1", "S0_K5_X1"]
DEV_START, DEV_END = dt.date(2022, 4, 1), dt.date(2024, 6, 30)


def _num(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if v == v else None


def load(src):
    with open(os.path.join(src, "frozen_rule.json"), encoding="utf-8") as f:
        rule = json.load(f)
    with open(os.path.join(src, "ladder_ideas_dev.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return rule, rows


def build_data(rule, rows):
    """Levels-ladder numbers over FILLED trades only.

    An idea whose deeper entry was never reached has net R exactly 0.0 in the csv: it is not a trade, so it is
    left out of n, mean, win rate and the running total, and counted as `unfilled` instead.
    """
    sel = [r for r in rows if r["E1"] == "True" and _num(r[FROZEN_COL]) is not None]
    sel.sort(key=lambda r: int(r["touch_t"]))
    trades, cum, c = [], [], 0.0
    for r in sel:
        d = dt.date(1970, 1, 1) + dt.timedelta(days=int(r["day"]))
        if not (DEV_START <= d <= DEV_END):
            raise ValueError("row outside the DEV window: %s" % d)
        net = round(float(r[FROZEN_COL]), 3)
        if net == 0.0:
            continue  # never filled
        l1, l2, t1 = (float(r[k]) for k in ("L1", "L2", "T1"))
        t2 = _num(r["T2"])
        if t2 is None:  # ladder rule: T2 = T1 + (T1 - L1) when no second level
            t2 = t1 + (t1 - l1)
        side = int(r["side"])
        pct = lambda p: round((p - l1) / l1 * 100 * side, 3)  # + = in favour
        c += net
        cum.append(round(c, 2))
        trades.append({"d": d.isoformat(), "s": side, "f": r["families"].replace("_", " "),
                       "l2": pct(l2), "t1": pct(t1), "t2": pct(t2), "r": net})
    stops = []
    for col in STOP_COLS:
        v = [float(r[col]) for r in rows if _num(r[col]) is not None]
        stops.append({"k": col.split("_")[1], "n": len(v), "m": round(statistics.mean(v), 3)})
    nets = [t["r"] for t in trades]
    n = len(trades)
    # the frozen file averaged over all selected ideas (incl. unfilled); rescale its gross/fee means to filled trades
    k = len(sel) / n
    dev = dict(rule["dev"])
    dev.update({"n": n, "mean": statistics.mean(nets),
                "mean_gross_r": rule["dev"]["mean_gross_r"] * k, "mean_fee_r": rule["dev"]["mean_fee_r"] * k})
    return {
        "rule": rule["rule"], "dev": dev, "power": rule["power"],
        "verdict": rule["verdict"], "n": n,
        "wins": sum(1 for x in nets if x > 0),
        "best": max(nets), "worst": min(nets),
        "ideas_selected": len(sel), "unfilled": len(sel) - n,
        "trades": trades, "cum": cum, "stops": stops,
        "ideas_total": len(rows),
    }


MIN_N = 30   # under this many filled trades a result is never a pass (desk.MIN_BUCKET uses the same line)
N_LABELS = ("filled trades", "trades filled", "Trades", "trades (first count in the source)", "sample size n (first in the source, may not be trades)")
NET_LABELS = ("average per trade, after fees", "mean net R per trade", "net R after fees (first value in the source)")
_NUM = re.compile(r"[+\-]?\d+(?:\.\d+)?")
CAPTION_RE = re.compile(r"(\d{4}-\d\d-\d\d \d\d:\d\d) UTC\s+[+\-]\d+\.\d+ R (long|short), (.+) \((\d+m)\)\s*$")


def _kpi_num(r, labels):
    for lab in labels:
        for k in r.get("kpis", []):
            if k.get("label") == lab:
                m = _NUM.search(str(k.get("value", "")).replace(",", ""))
                if m:
                    return float(m.group(0))
    return None


def banner_of(r):
    """The one fixed verdict banner (survey C2): state, filled n, net R after fees, try number, fee break-even if exported.
    Only PASS needs n >= MIN_N, a verdict written as good and a net R above zero; n < MIN_N is TOO_FEW whatever the verdict says."""
    v = r.get("verdict")
    label = v.get("label", "") if isinstance(v, dict) else str(v or "")
    tone = v.get("tone") if isinstance(v, dict) else None
    n = _kpi_num(r, N_LABELS)
    n = int(n) if n is not None else None
    net = _kpi_num(r, NET_LABELS)
    try_no = _kpi_num(r, ("try number",))
    try_no = int(try_no) if try_no is not None else None
    be = r.get("fee_breakeven_x")
    if be is None:
        be = _kpi_num(r, ("fee break-even (x the fee)",))
    if n is None:
        state, head = "UNCLEAR", "NO TRADE COUNT"
    elif n < MIN_N:
        state, head = "TOO_FEW", "TOO FEW TRADES"
    elif tone == "bad" or label.upper().startswith("FAIL"):
        state, head = "FAIL", "FAIL"
    elif tone == "good" and net is not None and net > 0:
        state, head = "PASS", "PASS"
    else:
        state, head = "UNCLEAR", "UNCLEAR"
    bt = {"PASS": "good", "FAIL": "bad", "TOO_FEW": "warn", "UNCLEAR": ""}[state]
    text = "%s · verdict as written: %s · n=%s · net R after fees %s · try %s · fee break-even %s" % (
        head, label or "none", "?" if n is None else n, "n/a" if net is None else "%+.3f" % net,
        "n/a" if try_no is None else "#%d" % try_no, "n/a" if be is None else "x%s" % be)
    return {"state": state, "tone": bt, "verdict": label, "n": n, "net_r": net, "try_no": try_no, "breakeven_x": be, "text": text}


def trade_row(item):
    """Trade fields of one desk chart item, read from its own caption (date, side, exit reason); None for event charts."""
    txt = re.findall(r"<text[^>]*>([^<]*)</text>", item.get("svg", ""))
    m = CAPTION_RE.search(txt[-1].strip()) if txt else None
    if not m:
        return None
    return {"when": m.group(1), "side": m.group(2), "net_r": item.get("net_r"), "exit_reason": m.group(3), "span": m.group(4)}


def add_trade_rows(r):
    """Add when / side / exit_reason to every winner/loser chart item (fields only added). Returns the number of rows added."""
    k = 0
    for e in r.get("examples", []):
        if e.get("kind") == "charts":
            for it in e.get("items", []):
                row = trade_row(it)
                if row:
                    it.update({x: row[x] for x in ("when", "side", "exit_reason", "span")})
                    k += 1
    return k


TF_RE = re.compile(r"(?<![A-Za-z0-9.])(?:(?:1|3|5|10|15|30|45)m|60m|(?:1|2|4|6|8|12)h|1d)(?![A-Za-z0-9])", re.I)


def tfs_in(text):
    """Timeframes named in a text, in order, 60m folded into 1h (`15min` is not matched: the result files write 15m)."""
    out = []
    for m in TF_RE.finditer(text or ""):
        t = {"60m": "1h"}.get(m.group(0).lower(), m.group(0).lower())
        if t not in out:
            out.append(t)
    return out


def _uniq(seq):
    out = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


def add_tf(r):
    """Timeframe fields (fields only added). Per example: `tf` from the json (tf_source json) else parsed from its title or caption
    (tf_source inferred); table examples whose rows name two or more timeframes get `row_tf`. Per test: `tfs` (pills: json first,
    then parsed from the examples, the settings text and the title; `tf_source` json when the test file wrote `tf`) and `tf_tabs`
    (the timeframes a tab can switch to: example tfs and row tfs; empty under two)."""
    ex_tfs, row_tfs, inferred = [], [], []
    for e in r.get("examples", []):
        if e.get("kind") == "none":
            continue
        if e.get("tf"):
            e.setdefault("tf_source", "json")
            ex_tfs.append(e["tf"])
        else:
            f = tfs_in(e.get("title", "")) or tfs_in(e.get("caption", ""))
            if f:
                e["tf"], e["tf_source"] = f[0], "inferred"
                inferred.append(f[0])
        if e.get("kind") == "table":
            rt = [(tfs_in(" ".join(str(c) for c in row)) or [""])[0] for row in e.get("rows", [])]
            if len({x for x in rt if x}) >= 2:
                e["row_tf"] = rt
                row_tfs.extend(rt)
    text = " ".join([r.get("title", "")] + ["%s %s" % (w.get("name", ""), w.get("value_plain", "")) for w in r.get("what", [])])
    r["tf_source"] = "json" if r.get("tf") else "inferred"
    r["tfs"] = _uniq(([r["tf"]] if r.get("tf") else []) + ex_tfs + inferred + row_tfs + tfs_in(text))
    tabs = _uniq(ex_tfs + inferred + row_tfs)
    r["tf_tabs"] = tabs if len(tabs) >= 2 else []


RESULTS_DIR = os.path.normpath(os.path.join(HERE, "..", "results"))

STABLE_YEARS = 2   # judged years (>= MIN_N trades each) needed before a run can be called stable


def stability_of(years):
    """Year-by-year flag (survey C4) from desk.breakdown()['year'] rows [{k, n, mean, few}]. A year under MIN_N trades is labelled
    too few and never judged. STABLE = at least 2 judged years and every judged year has a mean net R above zero;
    a judged year at or below zero makes it NOT_STABLE (one good year among bad ones included); fewer than 2 judged years = TOO_FEW;
    no split exported = UNKNOWN."""
    if not years:
        return {"state": "UNKNOWN", "tone": "", "judged": 0, "text": "YEAR SPLIT NOT EXPORTED for this run (re-run it on the desk to add it); not judged"}
    judged = [y for y in years if y["n"] >= MIN_N and not y.get("few")]
    few = [y["k"] for y in years if y not in judged]
    tail = (" (too few trades, not judged: %s)" % ", ".join(few)) if few else ""
    if len(judged) < STABLE_YEARS:
        return {"state": "TOO_FEW", "tone": "warn", "judged": len(judged),
                "text": "TOO FEW TRADES PER YEAR: %d year(s) with %d+ trades, need %d%s" % (len(judged), MIN_N, STABLE_YEARS, tail)}
    bad = [y["k"] for y in judged if y["mean"] <= 0]
    if bad:
        return {"state": "NOT_STABLE", "tone": "bad", "judged": len(judged),
                "text": "NOT STABLE: net R after fees is not above zero in %s of %d judged years%s" % (", ".join(bad), len(judged), tail)}
    return {"state": "STABLE", "tone": "good", "judged": len(judged),
            "text": "STABLE: net R after fees above zero in all %d judged years%s" % (len(judged), tail)}


def check_curve_bands(r, fn="result"):
    """Every curve example must carry the `mc` field (a band dict, or null for a run too short to reshuffle)."""
    for e in r.get("examples", []):
        if e.get("kind") == "curve":
            if "mc" not in e:
                raise ValueError("%s: curve example has no Monte Carlo band field (mc); run export_results.py" % fn)
            if e["mc"] is not None:
                for k in ("lo", "hi", "dd_lo", "dd_hi", "shuffles"):
                    if k not in e["mc"]:
                        raise ValueError("%s: mc band is missing %s" % (fn, k))
                if len(e["mc"]["lo"]) != len(e["r"]) or len(e["mc"]["hi"]) != len(e["r"]):
                    raise ValueError("%s: mc band length differs from the curve" % fn)

REQUIRED = ("id", "family", "title", "what", "how", "window", "verdict", "why", "kpis", "examples", "source_files", "commit")


def collect(results_dir):
    """Every results/*.json (standard schema, DESIGN.md) in file-name order; a malformed file stops the build."""
    out = []
    for fn in sorted(os.listdir(results_dir)):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        with open(os.path.join(results_dir, fn), encoding="utf-8") as f:
            r = json.load(f)
        miss = [k for k in REQUIRED if k not in r]
        if miss:
            raise ValueError("%s is missing %s" % (fn, ", ".join(miss)))
        for w in r["what"]:
            if w.get("label") not in ("SOURCED", "OURS"):
                raise ValueError("%s: parameter %r needs label SOURCED or OURS" % (fn, w.get("name")))
        check_curve_bands(r, fn)
        add_trade_rows(r)
        add_tf(r)
        r.setdefault("banner", banner_of(r))
        r["stability"] = (stability_of(r.get("years")))
        out.append(r)
    hm = heatmaps_of(out)
    for r in out:
        for study, panels in hm.items():
            if panels and r["id"].startswith("desk-%s-" % study):
                r["heatmaps"] = panels
    return out


def parse_settings(study, text):
    """The desk's Settings line -> dict of its parameters (the line is written by desk.py; a line this cannot read gives {})."""
    t = text.split()
    try:
        if study == "tom_vp":   # prior_day RETURN n6 shift OFF stop 1ATR target POC ...
            return {"anchor": t[0], "setup": t[1], "n": t[2][1:], "shift": t[4], "target": t[8]}
        if study == "fabio_v3":   # C m15 push OFF f0.5% rule exit ...   |   B N120 f0.5% target 2R ...
            if t[0] == "C":
                return {"model": "C", "m": t[1][1:], "push": t[3], "f": t[4][1:-1], "exit": " ".join(t[5:7]) if t[5] != "target" else "target " + t[6]}
            return {"model": "B", "N": t[1][1:], "f": t[2][1:-1], "exit": " ".join(t[3:5]) if t[3] != "target" else "target " + t[4]}
    except IndexError:
        pass
    return {}


# Two-parameter grids per study: x and y vary, `fix` holds the rest at the first grid run's value (survey C5). OURS, not the trader's.
HEATMAPS = {
    "tom_vp": [
        {"title": "Anchor x setup (6 closes outside, shift OFF, target POC)", "x": "anchor", "y": "setup",
         "fix": {"n": "6", "shift": "OFF", "target": "POC"}},
        {"title": "Closes outside x setup (prior_day, shift OFF, target POC)", "x": "n", "y": "setup",
         "fix": {"anchor": "prior_day", "shift": "OFF", "target": "POC"}}],
    "fabio_v3": [
        {"title": "Model C: first-window minutes x push (floor 0.5 %, rule exit)", "x": "m", "y": "push",
         "fix": {"model": "C", "f": "0.5", "exit": "rule exit"}},
        {"title": "Model B: balance window x floor % (rule exit)", "x": "N", "y": "f",
         "fix": {"model": "B", "exit": "rule exit"}}],
}


def lone_peak(cells):
    """The one cell worth flagging: of the cells with at least MIN_N trades (3 or more of them), exactly one has a mean net R above zero.
    A positive cell under MIN_N trades is never a peak; two or more positive cells are a plateau, not a lone peak."""
    ok = [c for c in cells if c["n"] >= MIN_N]
    pos = [c for c in ok if c["mean"] is not None and c["mean"] > 0]
    return pos[0] if len(ok) >= 3 and len(pos) == 1 else None


def _sort_key(v):
    try:
        return (0, float(v))
    except ValueError:
        return (1, v)


def heatmaps_of(tests):
    """study id -> list of panels {title, x, y, xs, ys, cells[{id, x, y, n, mean, thin}], peak}; built from the exported desk runs
    (no re-run): n and mean are each run's own banner numbers. thin = under MIN_N trades (greyed on the page)."""
    out = {}
    for study, panels in HEATMAPS.items():
        runs = []
        for t in tests:
            if t["id"].startswith("desk-%s-" % study) and t.get("banner", {}).get("n"):
                st = next((w["value_plain"] for w in t["what"] if w["name"] == "Settings"), "")
                runs.append((t, parse_settings(study, st)))
        res = []
        for pn in panels:
            cells = []
            for t, p in runs:
                if p and all(p.get(k) == v for k, v in pn["fix"].items()) and pn["x"] in p and pn["y"] in p:
                    b = t["banner"]
                    cells.append({"id": t["id"], "x": p[pn["x"]], "y": p[pn["y"]], "n": b["n"], "mean": b["net_r"], "thin": b["n"] < MIN_N})
            if cells:
                xs = sorted({c["x"] for c in cells}, key=_sort_key)
                ys = sorted({c["y"] for c in cells}, key=_sort_key)
                res.append({"title": pn["title"], "x": pn["x"], "y": pn["y"], "xs": xs, "ys": ys, "cells": cells, "peak": lone_peak(cells)})
        out[study] = res
    return out


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Test Simulator</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b2430;--mute:#5b6675;--line:#dde1e8;--good:#157a4b;--bad:#b3261e;--acc:#2456c5;--warn:#9a6700}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10141a;--card:#181e27;--ink:#e6eaf0;--mute:#9aa6b6;--line:#2a3340;--good:#4cc38a;--bad:#ff7b72;--acc:#7aa2ff;--warn:#e3b341}}
:root[data-theme="dark"]{--bg:#10141a;--card:#181e27;--ink:#e6eaf0;--mute:#9aa6b6;--line:#2a3340;--good:#4cc38a;--bad:#ff7b72;--acc:#7aa2ff;--warn:#e3b341}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{padding:12px 16px;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0}
#lst{max-height:calc(100vh - 150px);overflow:auto}
.sub{color:var(--mute);font-size:12px;margin-top:2px}
main{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;padding:12px 16px}
@media(min-width:900px){main{grid-template-columns:280px minmax(0,1fr);align-items:start}nav{position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto}}
nav,article{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
nav h2{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:10px 0 4px}
nav h2:first-child{margin-top:0}
nav button{display:block;width:100%;text-align:left;margin:2px 0;padding:6px 8px;border:1px solid transparent;border-radius:6px;background:none;color:var(--ink);cursor:pointer;font:inherit}
nav button[aria-current=true]{border-color:var(--acc);background:var(--bg)}
nav input[type=search]{width:100%;padding:6px;margin-bottom:6px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit}
nav select{width:100%;padding:5px;margin-bottom:6px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit}
nav button small{display:block;color:var(--mute)}
h2.s{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:18px 0 6px}
h3{font-size:14px;margin:14px 0 4px}
.pill{display:inline-block;font-size:12px;padding:2px 10px;border-radius:99px;border:1px solid var(--mute);color:var(--mute)}
.pill.bad{border-color:var(--bad);color:var(--bad)}.pill.good{border-color:var(--good);color:var(--good)}.pill.warn{border-color:var(--warn);color:var(--warn)}
.tag{font-size:11px;padding:0 6px;border-radius:4px;border:1px solid var(--line);color:var(--mute);white-space:nowrap}
.tag.SOURCED{border-color:var(--good);color:var(--good)}.tag.OURS{border-color:var(--warn);color:var(--warn)}
dl{margin:0}dt{font-weight:600;margin-top:8px}dd{margin:0;color:var(--mute)}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin:8px 0}
.kpi{border:1px solid var(--line);border-radius:8px;padding:6px 8px}.kpi b{display:block;font-size:18px}.kpi span{font-size:11px;color:var(--mute)}
.bad{color:var(--bad)}.good{color:var(--good)}.warn{color:var(--warn)}
svg{width:100%;height:auto;display:block}
.ctl{display:flex;gap:8px;align-items:center;margin:8px 0;flex-wrap:wrap}
.ctl input[type=range]{flex:1;min-width:120px}
button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--acc)}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:4px}
.tw{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:3px 6px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}
.note{font-size:12px;color:var(--mute);margin:4px 0}
.cg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px;margin:8px 0}.cg figure{margin:0;border:1px solid var(--line);border-radius:6px;padding:4px;background:#fff}.cg figcaption{font-size:11px;color:var(--mute);padding:2px 4px}
.ex{border-top:1px solid var(--line);padding-top:4px}
ul{margin:4px 0;padding-left:20px}li{margin:3px 0}
.src{font-size:12px;color:var(--mute);word-break:break-all}
.banner{margin:10px 0;padding:8px 12px;border:2px solid var(--mute);border-radius:8px;font-weight:600;font-size:14px}.banner.good{border-color:var(--good);color:var(--good)}.banner.bad{border-color:var(--bad);color:var(--bad)}.banner.warn{border-color:var(--warn);color:var(--warn)}
.tl{display:grid;grid-template-columns:minmax(0,1fr);gap:10px;margin:8px 0}@media(min-width:900px){.tl{grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);align-items:start}}
#tlist tr[data-i]{cursor:pointer}#tlist tr.sel{background:var(--bg);outline:2px solid var(--acc)}#tpane svg{background:#fff;border:1px solid var(--line);border-radius:6px}
[hidden]{display:none!important}
html,body{height:100%;overflow:hidden}
#app{height:100vh;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:6px 12px;flex:none}
.top h1{font-size:15px}
.tabs{display:flex;gap:4px;flex-wrap:wrap}
.tabs button{padding:3px 12px;border-radius:99px;font-size:13px}
.tabs [aria-selected=true]{border-color:var(--acc);background:var(--acc);color:#fff}
.pane{flex:1;min-height:0;overflow:auto}
main{height:100%;padding:8px 12px;gap:10px}
nav,article{min-height:0;overflow:auto}
@media(min-width:900px){main{align-items:stretch}nav{position:static;max-height:none}}
@media(max-width:899px){main{grid-template-rows:minmax(0,34%) minmax(0,1fr)}}
@media(max-width:700px){.top h1{display:none}.gf>b{width:100%!important}.kpis{grid-template-columns:repeat(auto-fill,minmax(100px,1fr))}}
#lst{max-height:none;overflow:visible}
.pill.tf{border-color:var(--acc);color:var(--acc);font-weight:600;margin-left:4px}
.tft{margin:6px 0}
.gridw{padding:8px 12px}.leg{display:flex;gap:12px;margin-bottom:8px;font-size:13px}
.gf{display:flex;align-items:center;gap:8px;margin:2px 0;flex-wrap:wrap}.gf>b{width:170px;font-size:11px;color:var(--mute);font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.gcs{display:flex;gap:3px;flex-wrap:wrap}
.gc{width:22px;height:22px;padding:0;border-radius:4px;font-size:12px;line-height:20px;text-align:center;border:1px solid var(--line);color:var(--mute)}
.gc.good{background:var(--good);border-color:var(--good);color:#fff}.gc.bad{background:var(--bad);border-color:var(--bad);color:#fff}.gc.warn{background:var(--warn);border-color:var(--warn);color:#fff}
.cm{display:flex;gap:6px;margin:6px 0 2px}.cm input{flex:1;min-width:0;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit}
.cmi{font-size:12px;color:var(--mute);margin:1px 0}.cmi span{color:var(--ink)}
details.dt{margin:8px 0}details>summary{cursor:pointer;color:var(--mute);font-size:12px}
</style></head><body>
<div id="app"><header class="top"><h1>Test simulator</h1><div id="tabs" class="tabs" role="tablist" aria-label="Views"></div><span class="sub" title="Past results on DEV data only; sealed windows unread. Percent distances and timestamps only, no prices.">DEV only &middot; % only</span></header><div id="pane" class="pane"></div></div>
<script>
const TESTS=/*__DATA__*/null;
const CAT=/*__CAT__*/[];
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const f2=x=>(x>=0?"+":"")+x.toFixed(3);
const tone=t=>t==="bad"||t==="good"||t==="warn"?t:"";
const COL={bad:"var(--bad)",good:"var(--good)",mute:"var(--line)",warn:"var(--warn)"};
let tm=null;
const KIND={backtest:"backtest",audit:"audit",thought_experiment:"thought experiment"};
const VC={failed:"failed",unclear:"unclear",passed:"passed",other:"other"};
function opts(v,all,cur){return '<option value="">'+all+"</option>"+v.map(x=>'<option value="'+esc(x[0])+'"'+(x[0]===cur?" selected":"")+">"+esc(x[1])+"</option>").join("");}
function buildNav(){const g=id=>$(id)?$(id).value:"",q=g("q").toLowerCase(),kf=g("kf"),ff=g("ff"),vf=g("vf"),only=$("onlyx")&&$("onlyx").checked;
const rows=CAT.filter(r=>(!only||r.exported)&&(!kf||r.kind===kf)&&(!ff||r.family===ff)&&(!vf||(r.verdict_class||"other")===vf)&&(!q||(r.title+" "+r.family+" "+r.verdict+" "+r.kind).toLowerCase().includes(q)))
.sort((a,b)=>String(b.date||"").localeCompare(String(a.date||""))||a.title.localeCompare(b.title));
const fams=[...new Set(CAT.map(r=>r.family))].sort((a,b)=>a.localeCompare(b));
const list=rows.map(r=>'<button data-id="'+esc(r.exported?r.result_id:r.id)+'">'+(r.status==="FAILED"?'<span class="bad">&#9679;</span> ':"")+esc(r.title)+"<small>"+esc(r.date||"no date")+" · "+esc(KIND[r.kind]||r.kind)+" · "+esc(r.family)+(r.exported?"":" · no result card")+"</small></button>").join("");
$("nav").innerHTML='<input id="q" type="search" placeholder="Search '+CAT.length+' tests" aria-label="Search tests" value="'+esc(q)+'">'+
'<select id="kf" aria-label="Kind">'+opts([["backtest","Backtests"],["audit","Audits"],["thought_experiment","Thought experiments"]],"All kinds",kf)+"</select>"+
'<select id="vf" aria-label="Verdict">'+opts([["failed","Failed"],["unclear","Unclear / not enough data"],["passed","Passed"],["other","Other"]],"Any verdict",vf)+"</select>"+
'<select id="ff" aria-label="Family">'+opts(fams.map(f=>[f,f]),"All families",ff)+"</select>"+
'<label class="note"><input id="onlyx" type="checkbox"'+(only?" checked":"")+'> hand-made charts only ('+CAT.filter(r=>r.exported&&r.provenance!=="source-extracted").length+')</label><div class="note">'+rows.length+' of '+CAT.length+' shown, newest first</div><div id="lst">'+list+"</div>";
["q","kf","vf","ff"].forEach(i=>$(i).oninput=refilter);$("onlyx").onchange=refilter;
$("nav").onclick=e=>{const b=e.target.closest("button");if(b){location.hash=b.dataset.id}};}
function refilter(){const id=document.activeElement&&document.activeElement.id;buildNav();const el=id&&$(id);if(el){el.focus();if(el.id==="q")el.setSelectionRange(el.value.length,el.value.length);}}
function stub(r){return '<h1 style="font-size:20px;margin:0 0 6px">'+esc(r.title)+'</h1><span class="pill '+(r.status==="FAILED"?"bad":"")+'">'+esc(KIND[r.kind]||r.kind)+"</span> <span class=\"pill\">charts not exported yet</span>"+
'<h2 class="s">Verdict as written</h2><p>'+esc(r.verdict)+'</p><h2 class="s">Where it lives</h2><p class="src">'+esc(r.source)+'</p><p class="note">Family: '+esc(r.family)+". The kind ("+esc(r.kind_source||"")+") and the verdict line were read from the file automatically, so check them against the source. No numbers or examples are shown until this test is exported to sim_desk/results/.</p>";}
function table(x){return '<div class="tw"><table><tr>'+x.cols.map(c=>"<th>"+esc(c)+"</th>").join("")+"</tr>"+x.rows.map((r,k)=>"<tr"+(x.row_tf&&x.row_tf[k]?' data-tf="'+esc(x.row_tf[k])+'"':"")+">"+r.map(c=>"<td>"+esc(c)+"</td>").join("")+"</tr>").join("")+"</table></div>";}
function stack(x){const W=600,rh=30;let s='<svg viewBox="0 0 '+W+" "+(x.rows.length*rh+34)+'" role="img" aria-label="'+esc(x.title)+'">';
x.rows.forEach((r,i)=>{const y=i*rh+4;s+='<text x="0" y="'+(y+14)+'" font-size="11" fill="var(--ink)">'+esc(r.label)+"</text>";let cx=190;const sc=(W-196)/100;
r.parts.forEach(p=>{const w=p.value*sc;s+='<rect x="'+cx+'" y="'+y+'" width="'+w.toFixed(1)+'" height="20" fill="'+(COL[p.tone]||"var(--acc)")+'" opacity=".8"/>';if(p.value>=6)s+='<text x="'+(cx+w/2)+'" y="'+(y+14)+'" font-size="10" text-anchor="middle" fill="var(--ink)">'+p.value+"%</text>";cx+=w;});});
const ly=x.rows.length*rh+14;let lx=190;x.rows[0].parts.forEach(p=>{s+='<rect x="'+lx+'" y="'+ly+'" width="10" height="10" fill="'+(COL[p.tone]||"var(--acc)")+'" opacity=".8"/><text x="'+(lx+14)+'" y="'+(ly+9)+'" font-size="11" fill="var(--mute)">'+esc(p.name)+"</text>";lx+=90;});
return s+"</svg>";}
function arrow(cx,side,label,col){if(side==null)return '<text x="'+cx+'" y="46" font-size="11" text-anchor="middle" fill="var(--mute)">'+label+": none</text>";
const up=side==="long"||side==="reference";const y1=up?58:22,y2=up?22:58;
return '<line x1="'+cx+'" x2="'+cx+'" y1="'+y1+'" y2="'+y2+'" stroke="'+col+'" stroke-width="3"/><path d="M'+(cx-6)+","+(y2+(up?8:-8))+" L"+cx+","+y2+" L"+(cx+6)+","+(y2+(up?8:-8))+'" fill="none" stroke="'+col+'" stroke-width="3"/><text x="'+cx+'" y="76" font-size="11" text-anchor="middle" fill="var(--mute)">'+label+(side==="opposite"||side==="reference"?"":": "+side)+"</text>";}
function sides(x){if(!x.rows.length)return '<p class="note">no example trades exported</p>';
return '<div class="kpis">'+x.rows.map(r=>{const opp=r.live==="opposite";
return '<div class="kpi"><svg viewBox="0 0 200 84" role="img" aria-label="'+esc(r.when)+'"><rect x="92" y="30" width="16" height="22" fill="var(--mute)" opacity=".5"/>'+
arrow(50,opp?"opposite":r.live,"live","var(--bad)")+arrow(150,r.backtest,"backtest","var(--acc)")+"</svg><span>"+esc(r.when)+"</span></div>"}).join("")+"</div>";}
function replay(x,id){const U=x.unit||"R",LB=x.labels||{},tr=x.trades,cum=x.cum,n=tr.length,W=600,H=200,P=28,mn=Math.min(0,...cum),mx=Math.max(0,...cum);
const X=i=>P+i*(W-P-8)/(n-1||1),Y=v=>H-P-(v-mn)/(mx-mn||1)*(H-P-10);
let h='<svg viewBox="0 0 600 200" role="img" aria-label="Running total of net R"><line x1="'+P+'" x2="'+(W-8)+'" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="var(--line)"/><polyline fill="none" stroke="var(--acc)" stroke-width="1.5" points="'+cum.map((v,i)=>X(i).toFixed(1)+","+Y(v).toFixed(1)).join(" ")+'"/><circle id="dot" r="4" fill="var(--bad)"/><text x="'+P+'" y="12" font-size="11" fill="var(--mute)">Running total of net '+U+' (high '+mx.toFixed(1)+", low "+mn.toFixed(1)+", end "+cum[n-1].toFixed(1)+")</text></svg>";
h+='<div class="ctl"><button id="prev" aria-label="Previous trade">&lt;</button><button id="play">Play</button><button id="next" aria-label="Next trade">&gt;</button><input id="slider" type="range" min="0" max="'+(n-1)+'" value="0" aria-label="Trade number"><select id="pick" aria-label="Jump to example"></select></div><svg id="ladder" viewBox="0 0 600 190" role="img" aria-label="Planned ladder of the selected trade"></svg><div id="tinfo" class="note"></div>';
return {html:h,init:()=>{const sl=$("slider"),idx=tr.map((t,i)=>i),ex=[];
[...idx].sort((a,b)=>tr[b].r-tr[a].r).slice(0,3).forEach(i=>ex.push(["Big win",i]));
[...idx].sort((a,b)=>tr[a].r-tr[b].r).slice(0,3).forEach(i=>ex.push(["Big loss",i]));
[...idx].sort((a,b)=>Math.abs(tr[a].r)-Math.abs(tr[b].r)).slice(0,2).forEach(i=>ex.push(["Flat",i]));
$("pick").innerHTML='<option value="">Examples</option>'+ex.map(e=>'<option value="'+e[1]+'">'+e[0]+" #"+(e[1]+1)+" ("+f2(tr[e[1]].r)+" "+U+")</option>").join("");
function show(i){i=Math.max(0,Math.min(n-1,+i));sl.value=i;const t=tr[i];$("dot").setAttribute("cx",X(i));$("dot").setAttribute("cy",Y(cum[i]));
const ys=t.l2==null?[0]:[0,t.l2,t.t1,t.t2],lo=Math.min(...ys),hi=Math.max(...ys),sp=(hi-lo)||1,y=v=>170-(v-lo)/sp*150;
const row=(v,l,c)=>'<line x1="150" x2="560" y1="'+y(v)+'" y2="'+y(v)+'" stroke="'+c+'" stroke-dasharray="4 3"/><text x="146" y="'+(y(v)+4)+'" text-anchor="end" font-size="11" fill="var(--ink)">'+l+'</text><text x="564" y="'+(y(v)+4)+'" font-size="11" fill="var(--mute)">'+(v>=0?"+":"")+v.toFixed(2)+"%</text>";
$("ladder").innerHTML=t.l2==null?"":row(t.t2,LB.t2||"Target 2","var(--good)")+row(t.t1,LB.t1||"Target 1","var(--good)")+row(0,LB.zero||"Touched level","var(--acc)")+row(t.l2,LB.l2||"Deeper entry (filled here)","var(--warn)")+'<text x="150" y="186" font-size="11" fill="var(--mute)">Distance from the touched level; up is in favour of the trade</text>';
if(window.cvShow&&$("cvs")&&$("cvs").options.length===n)cvShow(i);$("tinfo").innerHTML="Trade "+(i+1)+" of "+n+": "+esc(t.d)+", "+(t.s>0?"long":"short")+" at "+esc(t.f)+'. Result <b class="'+(t.r<0?"bad":"good")+'">'+f2(t.r)+" "+U+"</b> after fees.";}
sl.oninput=()=>show(sl.value);$("prev").onclick=()=>show(+sl.value-1);$("next").onclick=()=>show(+sl.value+1);
$("pick").onchange=e=>{if(e.target.value!=="")show(e.target.value)};
$("play").onclick=()=>{if(tm){clearInterval(tm);tm=null;$("play").textContent="Play";return}$("play").textContent="Pause";tm=setInterval(()=>{if(+sl.value>=n-1){$("play").onclick();return}show(+sl.value+1)},120)};
show(0);}};}
function tradeChart(x){const tr=x.trades,n=tr.length,M=(x.tf_min||30)*60000;
const h='<details class="note"><summary>?</summary><b>How to read it.</b> The rule is checked on every candle; a trade happens only where it fires. Each picture below is one trade on the '+esc(x.tf||"30m")+' chart: '+
'<span class="good">&#9650; entry</span> (open of the candle after the signal), <span class="bad">&#9660; exit</span>, the shaded box is the time in the trade (green = won, red = lost after fees), the dashed line is the entry price (0 %). '+
'Prices are shown as % from the entry. Lower panes: WaveTrend (blue dot = the buy dot at or under -53), RSI (orange line = the divergence: price made a lower low, RSI a higher low). '+esc(x.stop_note||"")+'</details>'+
'<div class="ctl"><button id="cvp" aria-label="Previous trade">&lt; Prev</button><button id="cvn" aria-label="Next trade">Next &gt;</button><select id="cvs" aria-label="Pick a trade">'+
tr.map((t,i)=>'<option value="'+i+'">#'+(i+1)+" "+esc(t.d)+" UTC: "+f2(t.net)+" %</option>").join("")+'</select><button id="cvr" aria-label="Replay this trade candle by candle">&#9654; Replay this trade</button><button id="cvst" aria-label="One candle forward">Step 1 candle &#9656;</button></div><div id="cvph" style="font-size:15px;min-height:2.6em;margin:4px 0"></div><svg id="cvg" viewBox="0 0 700 430" style="max-width:min(100%,calc((100vh - 140px)*1.49))" role="img" aria-label="Candles of the selected trade"></svg><div id="cvi" class="note"></div>';
const init=()=>{let cur=0,up=null;const stop=()=>{if(window.cvT){clearInterval(window.cvT);window.cvT=null}$("cvr").innerHTML="&#9654; Replay this trade"};const go=i=>{stop();i=Math.max(0,Math.min(n-1,+i));const sl=$("slider");if(sl&&+sl.max===n-1){sl.value=i;sl.oninput()}else cvShow(i)};
$("cvp").onclick=()=>go(+$("cvs").value-1);$("cvn").onclick=()=>go(+$("cvs").value+1);$("cvs").onchange=e=>go(e.target.value);const first=()=>Math.max(0,tr[cur].sig-12),step=()=>{const m=tr[cur].c.length;up=(up==null||up>=m-1)?first():up+1;cvShow(cur,up);if(up>=m-1)stop()};$("cvst").onclick=()=>{stop();step()};$("cvr").onclick=()=>{if(window.cvT){stop();return}up=null;step();$("cvr").innerHTML="&#10074;&#10074; Pause";window.cvT=setInterval(step,450)};
window.cvShow=(i,u)=>{cur=+i;const t=tr[i],c=t.c,m=c.length;if(u==null){u=m-1;up=null}const live=u<m-1||up!=null,L=46,R=600,W=(R-L)/m,X=k=>L+k*W+W/2,win=t.net>=0;$("cvs").value=i;
const lo=Math.min(...c.map(q=>q[2])),hi=Math.max(...c.map(q=>q[1])),sp=(hi-lo)||1,Y=v=>14+(hi-v)/sp*196;
const wv=t.w1.concat(t.w2).filter(v=>v!=null),wl=Math.min(-60,...wv),wh=Math.max(10,...wv),WY=v=>236+(wh-v)/(wh-wl)*84;
const RY=v=>346+(100-v)/100*70;let s="";
const ue=Math.min(u+1,t.ext),pn=u>=t.ext?t.net:c[Math.min(u,m-1)][3];if(u>=t.ent)s+='<rect x="'+(X(t.ent)-W/2)+'" y="14" width="'+((ue-t.ent)*W)+'" height="196" fill="'+(pn>=0?"var(--good)":"var(--bad)")+'" opacity=".12"/>';
if(u>=t.sig)s+='<rect x="'+(X(t.sig)-W/2)+'" y="14" width="'+W+'" height="406" fill="var(--acc)" opacity=".10"/>';if(live)s+='<line x1="'+(X(u)+W/2)+'" x2="'+(X(u)+W/2)+'" y1="14" y2="420" stroke="var(--warn)" stroke-dasharray="2 2"/>';
s+='<line x1="'+L+'" x2="'+R+'" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="var(--mute)" stroke-dasharray="4 3"/><text x="'+(L+2)+'" y="'+(Y(0)-4)+'" font-size="10" fill="var(--mute)">0 % = where we bought</text>';
for(let g=Math.ceil(lo);g<=Math.floor(hi);g++)s+='<text x="'+(R+4)+'" y="'+(Y(g)+4)+'" font-size="10" fill="var(--mute)">'+(g>0?"+":"")+g+"%</text>";
c.forEach((q,k)=>{if(k>u)return;const up=q[3]>=q[0],col=up?"var(--good)":"var(--bad)",x0=X(k);s+='<line x1="'+x0+'" x2="'+x0+'" y1="'+Y(q[1])+'" y2="'+Y(q[2])+'" stroke="'+col+'"/><rect x="'+(x0-W*0.35)+'" y="'+Y(Math.max(q[0],q[3]))+'" width="'+(W*0.7)+'" height="'+Math.max(1,Math.abs(Y(q[0])-Y(q[3])))+'" fill="'+col+'"/>';});
const [p,qd]=t.div;if(u>=t.sig)s+='<line x1="'+X(p)+'" x2="'+X(qd)+'" y1="'+(Y(c[p][2])+6)+'" y2="'+(Y(c[qd][2])+6)+'" stroke="#e8912d" stroke-width="2"/>';
const ey=Y(c[t.ent][0]),xy=Y(c[t.ext][0]);
if(u>=t.ent)s+='<path d="M'+X(t.ent)+","+(ey+4)+" l-7,12 h14 z\" fill=\"var(--good)\"/><text x=\""+X(t.ent)+'" y="'+(ey+30)+'" font-size="11" text-anchor="middle" fill="var(--good)">entry</text>';
if(u>=t.ext)s+='<path d="M'+X(t.ext)+","+(xy-4)+" l-7,-12 h14 z\" fill=\"var(--bad)\"/><text x=\""+X(t.ext)+'" y="'+(xy-20)+'" font-size="11" text-anchor="middle" fill="var(--bad)">exit '+f2(t.net)+"%</text>";
const line=(v,Yf,col)=>'<polyline fill="none" stroke="'+col+'" stroke-width="1.3" points="'+v.map((y,k)=>y==null||k>u?"":X(k).toFixed(1)+","+Yf(y).toFixed(1)).join(" ")+'"/>';
[[0,"0 = exit line"],[-53,"-53 = buy trigger"]].forEach(([v,l])=>{s+='<line x1="'+L+'" x2="'+R+'" y1="'+WY(v)+'" y2="'+WY(v)+'" stroke="var(--line)" stroke-dasharray="3 3"/><text x="'+(R+4)+'" y="'+(WY(v)+4)+'" font-size="10" fill="var(--mute)">'+l+"</text>"});
s+=line(t.w1,WY,"var(--acc)")+line(t.w2,WY,"var(--mute)")+(u>=t.sig?'<circle cx="'+X(t.sig)+'" cy="'+WY(t.w1[t.sig])+'" r="5" fill="var(--acc)"/>':"")+'<text x="'+L+'" y="248" font-size="11" fill="var(--mute)">WaveTrend</text>';
[[40,"40"],[50,"50"]].forEach(([v,l])=>{s+='<line x1="'+L+'" x2="'+R+'" y1="'+RY(v)+'" y2="'+RY(v)+'" stroke="var(--line)" stroke-dasharray="3 3"/><text x="'+(R+4)+'" y="'+(RY(v)+4)+'" font-size="10" fill="var(--mute)">'+l+"</text>"});
s+=line(t.rsi,RY,"var(--ink)")+(u<t.sig?"":'<line x1="'+X(p)+'" x2="'+X(qd)+'" y1="'+RY(t.rsi[p])+'" y2="'+RY(t.rsi[qd])+'" stroke="#e8912d" stroke-width="2"/>')+'<text x="'+L+'" y="358" font-size="11" fill="var(--mute)">RSI 14</text>';
const tl=k=>new Date(t.t0+k*M).toISOString().slice(5,16).replace("T"," ");[0,t.sig,t.ext,m-1].forEach(k=>{s+='<text x="'+X(k)+'" y="428" font-size="10" text-anchor="middle" fill="var(--mute)">'+tl(k)+"</text>"});
const wv1=v=>v==null?"-":v.toFixed(0),T=k=>tl(k)+" UTC";let ph;if(!live)ph='Whole trade shown. Press <b>&#9654; Replay this trade</b> to watch it candle by candle.';else if(u<t.sig)ph='<b>WAITING</b> &middot; '+T(u)+': the rule is checked on this candle and is not true. WaveTrend '+wv1(t.w1[u])+' (needs a buy dot at -53 or lower) and RSI divergence.';else if(u===t.sig)ph='<b style="color:var(--acc)">SIGNAL</b> &middot; '+T(u)+' close: WaveTrend buy dot at '+wv1(t.w1[u])+' with RSI divergence (orange). We buy at the open of the next candle.';else if(u<t.ext-1)ph='<b>IN TRADE</b> &middot; candle '+(u-t.ent+1)+' of max 60 &middot; now <b class="'+(c[u][3]>=0?"good":"bad")+'">'+f2(c[u][3])+' %</b> from entry &middot; WaveTrend '+wv1(t.w1[u])+' (we sell once it closes above 0). No stop loss.';else if(u===t.ext-1)ph='<b style="color:var(--warn)">EXIT SIGNAL</b> &middot; '+T(u)+' close: '+esc(t.why)+'. We sell at the open of the next candle.';else if(u===t.ext)ph='<b class="'+(win?"good":"bad")+'">EXITED</b> &middot; sold at the open of '+T(u)+' &middot; result '+f2(t.net)+' % after fees, held '+t.bars+' candles.';else ph='<b>DONE</b> &middot; trade closed '+f2(t.net)+' % after fees. Prev / Next for another trade.';$("cvph").innerHTML=ph;$("cvg").innerHTML=s;$("cvi").innerHTML="Trade "+(i+1)+" of "+n+": entry "+esc(t.d)+' UTC, held '+t.bars+" candles, exit: "+esc(t.why)+'. Result <b class="'+(win?"good":"bad")+'">'+f2(t.net)+" %</b> after fees.";};
cvShow(0);};return {html:h,init};}
function curveEx(x){const r=x.r,n=r.length,W=600,H=170,mc=x.mc,lo=mc?mc.lo:r,hi=mc?mc.hi:r,pk=[];let m=0,dd=0;r.forEach(v=>{m=Math.max(m,v);pk.push(m);dd=Math.max(dd,m-v)});
const mn=Math.min(0,...r,...lo),mx=Math.max(0,...r,...hi),sp=(mx-mn)||1,X=i=>8+i*(W-16)/(n-1||1),Y=v=>H-8-(v-mn)/sp*(H-16),pt=(a,f)=>a.map((v,i)=>X(i).toFixed(1)+","+Y(f?f(v):v).toFixed(1));
const band=mc?'<polygon class="mcb" fill="var(--acc)" opacity=".15" points="'+pt(hi).concat(pt(lo).reverse()).join(" ")+'"><title>Reshuffled 5-95 % band</title></polygon>':"";
const shade='<polygon class="dd" fill="var(--bad)" opacity=".25" points="'+pt(pk).concat(pt(r).reverse()).join(" ")+'"><title>Drawdown: below the earlier peak</title></polygon>';
const mct=mc?" Blue band: the same trades reshuffled "+mc.shuffles+" times (5th to 95th percent of the running total); worst drawdown of the reshuffles "+mc.dd_lo.toFixed(1)+" to "+mc.dd_hi.toFixed(1)+" R"+(mc.approx?" (approximate: estimated from the sampled curve)":"")+". If the real line sits near the lower edge, luck of the order helped.":" No band: too few trades to reshuffle.";
return '<svg viewBox="0 0 600 '+H+'" role="img" aria-label="Running total of net R with drawdown shading and Monte Carlo band"><line x1="8" x2="592" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="var(--line)"/>'+band+shade+'<polyline fill="none" stroke="var(--acc)" stroke-width="1.5" points="'+pt(r).join(" ")+'"/></svg><p class="note">'+n+" points; ends at "+r[n-1].toFixed(2)+" R = $"+x.usd[n-1].toFixed(0)+" from $"+x.start_usd+" ("+x.risk_pct+" % risked per trade, simple sum). Red shading: drawdown from the earlier peak; deepest "+dd.toFixed(2)+" R."+mct+"</p>";}
function yearStrip(t){const s=t.stability;if(!s)return"";const ys=t.years;
const tb=ys&&ys.length?'<div class="tw"><table><tr><th>Year</th><th>Trades</th><th>Average net R</th><th></th></tr>'+ys.map(y=>"<tr><td>"+esc(y.k)+"</td><td>"+y.n+'</td><td class="'+(y.few?"":(y.mean>0?"good":"bad"))+'">'+f2(y.mean)+"</td><td>"+(y.few?'<span class="tag">too few trades</span>':"")+"</td></tr>").join("")+"</table></div>":"";
return '<h2 class="s">Year by year</h2><div class="banner ys-'+esc(s.state)+" "+tone(s.tone)+'" role="status">'+esc(s.text)+"</div>"+tb+'<p class="note">A split of the same DEV trades by calendar year, not a walk-forward test. A year under 30 trades is shown but not judged.</p>';}
function heatmap(t){const hs=t.heatmaps;if(!hs||!hs.length)return"";let h='<h2 class="s">Neighbour heatmap</h2>';
hs.forEach(m=>{const cw=84,ch=34,L=96,T=24,W=L+m.xs.length*cw+8,H=T+m.ys.length*ch+8;let g="";
m.xs.forEach((x,i)=>{g+='<text x="'+(L+i*cw+cw/2)+'" y="16" text-anchor="middle" font-size="11" fill="var(--mute)">'+esc(x)+"</text>"});
m.ys.forEach((y,j)=>{g+='<text x="'+(L-6)+'" y="'+(T+j*ch+ch/2+4)+'" text-anchor="end" font-size="11" fill="var(--mute)">'+esc(y)+"</text>"});
m.cells.forEach(c=>{const i=m.xs.indexOf(c.x),j=m.ys.indexOf(c.y),a=Math.min(1,Math.abs(c.mean)/0.3),col=c.thin?"var(--mute)":(c.mean>0?"var(--good)":"var(--bad)"),op=c.thin?0.15:0.15+0.7*a,pk=m.peak&&m.peak.id===c.id,cur=c.id===t.id;
g+='<g><title>'+esc(m.x+" "+c.x+", "+m.y+" "+c.y+": n="+c.n+", mean net R "+f2(c.mean)+(c.thin?" (under 30 trades, greyed)":"")+(pk?" (lone peak)":""))+'</title><rect x="'+(L+i*cw+2)+'" y="'+(T+j*ch+2)+'" width="'+(cw-4)+'" height="'+(ch-4)+'" rx="4" fill="'+col+'" fill-opacity="'+op+'" stroke="'+(cur?"var(--acc)":"var(--line)")+'" stroke-width="'+(cur?2.5:1)+'"/><text x="'+(L+i*cw+cw/2)+'" y="'+(T+j*ch+ch/2+4)+'" text-anchor="middle" font-size="11" fill="var(--ink)">'+f2(c.mean)+(pk?" ★":"")+"</text></g>"});
h+="<h3>"+esc(m.title)+'</h3><svg viewBox="0 0 '+W+" "+H+'" style="max-width:'+W+'px;width:100%" role="img" aria-label="'+esc(m.title)+'">'+g+"</svg>"+(m.peak?'<div class="banner warn" role="status">LONE PEAK: only '+esc(m.x+" "+m.peak.x+", "+m.y+" "+m.peak.y)+" is above zero ("+f2(m.peak.mean)+" R, n="+m.peak.n+"); its neighbours are not. A lone peak is more likely luck than an edge.</div>":"")});
return h+'<p class="note">Colour = average net R per trade after fees (green above zero, red below); hover a cell for n. Grey = under 30 trades, not judged. Blue outline = this run. The other settings are held as the title says; only settings already run are shown, empty cells were not run.</p>';}
function banner(b){if(!b)return"";return '<div class="banner b-'+esc(b.state)+" "+tone(b.tone)+'" role="status">'+esc(b.text)+"</div>";}
function chartList(x){const it=x.items,fn=v=>v==null?"-":f2(v)+" R";
const rows=it.map((c,i)=>'<tr data-i="'+i+'" tabindex="0"><td>'+(i+1)+"</td><td>"+esc(c.when)+" UTC</td><td>"+esc(c.side)+"</td><td>"+esc(c.exit_reason)+'</td><td class="'+(c.net_r<0?"bad":"good")+'">'+fn(c.net_r)+"</td></tr>").join("");
const h='<div class="tl"><div class="tw"><table id="tlist"><tr><th>#</th><th>Entry (UTC)</th><th>Side</th><th>Exit reason</th><th>Net R</th></tr>'+rows+'</table></div><div id="tpane"></div></div><p class="note">'+it.length+" example trades (typical winners and losers), not every trade. Click a row to see its chart.</p>";
return {html:h,init:()=>{const sel=i=>{document.querySelectorAll("#tlist tr[data-i]").forEach(r=>r.classList.toggle("sel",+r.dataset.i===i));const c=it[i];$("tpane").innerHTML=c.svg+'<p class="note">'+esc((c.kind==="winner"?"typical winner":"typical loser")+(c.note?": "+c.note:""))+"</p>"};
const tb=$("tlist");tb.onclick=e=>{const r=e.target.closest("tr[data-i]");if(r)sel(+r.dataset.i)};tb.onkeydown=e=>{const r=e.target.closest("tr[data-i]");if(r&&(e.key==="Enter"||e.key===" ")){e.preventDefault();sel(+r.dataset.i)}};sel(0)}};}
const CKEY="simdesk.comments.v1";
function readComments(){try{const a=JSON.parse(localStorage.getItem(CKEY)||"[]");return Array.isArray(a)?a:[]}catch(e){return[]}}
// Comments go to the artifact db (capability `db`, runtime contract 0.2.96: claude.use("db") -> collection/doc/set); null namespace = write skipped; a db or storage error never blocks the page.
let DBP=null;function dbNs(){if(!DBP){try{DBP=(window.claude&&typeof window.claude.use==="function")?Promise.resolve(window.claude.use("db")).catch(()=>null):Promise.resolve(null)}catch(e){DBP=Promise.resolve(null)}}return DBP}
function saveComment(c){try{dbNs().then(db=>{if(!db)return;const id=String(c.ts+"-"+c.test_id+"-"+c.chart_id).replace(/[^A-Za-z0-9_.~:@+-]/g,"_").slice(0,180);return db.collection("comments").doc(id).set(c)}).catch(()=>{})}catch(e){}
try{const a=readComments();a.push(c);localStorage.setItem(CKEY,JSON.stringify(a))}catch(e){}}
/*end-comments-adapter*/
const stamp=ts=>{try{return new Date(ts).toISOString().slice(5,16).replace("T"," ")}catch(e){return""}};
function commentList(tid,cid){return readComments().filter(c=>c.test_id===tid&&c.chart_id===cid).slice(-5).map(c=>'<div class="cmi"><span>'+esc(stamp(c.ts))+"</span> "+esc(c.text)+"</div>").join("")}
function commentBox(tid,cid){return '<form class="cm" data-t="'+esc(tid)+'" data-c="'+esc(cid)+'"><input type="text" maxlength="400" placeholder="&#9998;" aria-label="Comment"><button type="submit">Save</button><button type="button" data-copy="1">copy all</button></form><div class="cml">'+commentList(tid,cid)+"</div>";}
function allCommentsText(){return readComments().map(c=>{const t=TESTS.find(x=>x.id===c.test_id);return stamp(c.ts)+" | "+(t?t.title:c.test_id)+" | "+c.chart_id+" | "+c.text}).join("\n")}
function copyAll(b){const tx=allCommentsText();const done=()=>{const o=b.textContent;b.textContent="✓";setTimeout(()=>{b.textContent=o},900)};
try{navigator.clipboard.writeText(tx).then(done,()=>{});return}catch(e){}
try{const a=document.createElement("textarea");a.value=tx;document.body.appendChild(a);a.select();document.execCommand("copy");a.remove();done()}catch(e){}}
document.addEventListener("submit",e=>{const f=e.target.closest&&e.target.closest("form.cm");if(!f)return;e.preventDefault();const i=f.querySelector("input"),tx=i.value.trim();if(!tx)return;
saveComment({test_id:f.dataset.t,chart_id:f.dataset.c,text:tx,ts:Date.now()});i.value="";if(f.nextElementSibling)f.nextElementSibling.innerHTML=commentList(f.dataset.t,f.dataset.c);});
function tfPill(f,src){return '<span class="pill tf" title="'+(src==="inferred"?"timeframe read from the text":"timeframe from the result file")+'">'+esc(f)+(src==="inferred"?"~":"")+"</span>"}
function tfTabs(t){const a=t.tf_tabs||[];if(a.length<2)return"";return '<div class="tabs tft" role="tablist" aria-label="Timeframe">'+a.map((f,i)=>'<button role="tab" data-tf="'+esc(f)+'" aria-selected="'+(i===0)+'">'+esc(f)+"</button>").join("")+'<button role="tab" data-tf="*" aria-selected="false">&#8734;</button></div>';}
function applyTf(tf){document.querySelectorAll(".tft [role=tab]").forEach(b=>b.setAttribute("aria-selected",b.dataset.tf===tf));
document.querySelectorAll("#view .ex[data-tf],#view tr[data-tf]").forEach(el=>{el.hidden=!(tf==="*"||el.dataset.tf===tf)})}
document.addEventListener("click",e=>{const b=e.target.closest("[data-copy]");if(b){copyAll(b);return}const t=e.target.closest(".tft [role=tab]");if(t)applyTf(t.dataset.tf)});
function example(x,i,t){const inits=[];let real=true;let h='<div class="ex"'+(x.tf&&!x.row_tf?' data-tf="'+esc(x.tf)+'"':"")+"><h3>"+esc(x.title||"Example")+(x.tf?" "+tfPill(x.tf,x.tf_source):"")+"</h3>";
if(x.kind==="table")h+=table(x);else if(x.kind==="stack")h+=stack(x);else if(x.kind==="sides")h+=sides(x);
else if(x.kind==="curve"&&x.r&&x.r.length)h+=curveEx(x);
else if(x.kind==="charts"&&x.items&&x.items.length&&x.items.every(c=>c.when&&c.exit_reason)){const r=chartList(x);h+=r.html;inits.push(r.init);}
else if(x.kind==="charts"&&x.items&&x.items.length)h+='<div class="cg">'+x.items.map(c=>"<figure>"+c.svg+"<figcaption>"+esc((c.label||(c.kind==="winner"?"typical winner":"typical loser"))+(c.note?": "+c.note:""))+"</figcaption></figure>").join("")+"</div>";
else if(x.kind==="replay"){const r=replay(x);h+=r.html;inits.push(r.init);}
else if(x.kind==="trade_chart"&&x.trades&&x.trades.length){const r=tradeChart(x);h+=r.html;inits.push(r.init);}
else{real=false;h+='<p class="note">no example trades exported</p>';}
if(x.caption)h+='<p class="note">'+esc(x.caption)+"</p>";if(real)h+=commentBox(t.id,"ex"+i);return {html:h+"</div>",inits};}
function halt(){if(tm){clearInterval(tm);tm=null}window.cvShow=null;if(window.cvT){clearInterval(window.cvT);window.cvT=null}}
const CHARTK=["trade_chart","charts","replay","curve","stack","sides"];
function testHtml(t,only){const inits=[];const pills=(t.tfs||[]).map(f=>tfPill(f,t.tf_source)).join("");
let h='<h1 style="font-size:18px;margin:0 0 6px">'+esc(t.title)+'</h1><span class="pill '+tone(t.verdict.tone)+'">'+esc(t.verdict.label)+"</span>"+pills+banner(t.banner);
h+='<div class="kpis">'+t.kpis.map(k=>'<div class="kpi"><b class="'+tone(k.tone)+'">'+esc(k.value)+"</b><span>"+esc(k.label)+"</span></div>").join("")+"</div>";
h+=commentBox(t.id,"card")+tfTabs(t);
if(!only){h+=yearStrip(t)+heatmap(t);}
const exs=t.examples.map((x,i)=>[x,i]).filter(([x])=>!only||CHARTK.includes(x.kind));
h+='<h2 class="s">&#9638;</h2>';exs.forEach(([x,i])=>{const e=example(x,i,t);h+=e.html;inits.push(...e.inits)});
if(only)return {h,inits};
h+='<h2 class="s">&#10004;&#10006;</h2><span class="pill '+tone(t.verdict.tone)+'">'+esc(t.verdict.label)+"</span><ul>"+(t.why.length?t.why.map(w=>"<li>"+esc(w)+"</li>").join(""):"<li>The source does not say why.</li>")+"</ul>";
h+='<details class="dt"><summary>&#9432; What was tested</summary><dl>'+t.what.map(w=>"<dt>"+esc(w.name)+' <span class="tag '+esc(w.label)+'" title="'+(w.label==="SOURCED"?"taken from a named source":"our own judgement or tuned on DEV data")+'">'+esc(w.label)+"</span></dt><dd>"+esc(w.value_plain)+"</dd>").join("")+"</dl>"+
'<p class="note"><b>Window:</b> '+esc(t.window||"not stated in the source")+'</p><h2 class="s">How</h2><p>'+esc(t.how)+"</p></details>";
if(t.provenance==="source-extracted"){const ms=Object.entries(t.missing||{});h+='<h2 class="s">Source-extracted</h2><p class="note">Copied from the written note, not re-run. Check each line against the source.</p>'+
(t.evidence&&t.evidence.length?"<ul>"+t.evidence.map(e=>"<li>"+esc(e.field)+": "+esc(e.value)+' <span class="src">from: '+esc(e.quote)+"</span></li>").join("")+"</ul>":"")+
(ms.length?'<p class="note">Not in the source (shown as empty, not guessed): '+ms.map(m=>esc(m[0]+" ("+m[1]+")")).join("; ")+"</p>":"");}
h+='<details class="dt"><summary>&#9432; source</summary><p class="src">'+t.source_files.map(esc).join("<br>")+"<br>commit "+esc(t.commit)+"</p></details>";
return {h,inits};}
function mountTest(t,only){const r=testHtml(t,only);$("view").innerHTML=r.h;r.inits.forEach(f=>f());if((t.tf_tabs||[]).length>1)applyTf(t.tf_tabs[0]);}
function render(id){halt();const t=TESTS.find(x=>x.id===id);
if(!t){const r=CAT.find(x=>x.id===id);if(r){document.querySelectorAll("nav button").forEach(b=>b.setAttribute("aria-current",b.dataset.id===id));$("view").innerHTML=stub(r);return}}
if(!t){render(TESTS[0].id);return}
document.querySelectorAll("nav button").forEach(b=>b.setAttribute("aria-current",b.dataset.id===t.id));mountTest(t,false);}
function glyphOf(r){const t=TESTS.find(x=>x.id===r.result_id);const s=t&&t.banner?t.banner.state:(r.verdict_class==="failed"?"FAIL":r.verdict_class==="passed"?"PASS":r.verdict_class==="unclear"?"UNCLEAR":"OTHER");
return {PASS:["good","&#10004;"],FAIL:["bad","&#10006;"],TOO_FEW:["warn","&#9684;"],UNCLEAR:["","?"],OTHER:["","&middot;"]}[s]||["","&middot;"];}
function gridTab(){const by={},cnt={};CAT.forEach(r=>{const g=glyphOf(r);(by[r.family]=by[r.family]||[]).push([r,g]);const k=g[0]+"|"+g[1];cnt[k]=(cnt[k]||0)+1});
const leg=Object.entries(cnt).sort((a,b)=>b[1]-a[1]).map(([k,n])=>{const [c,g]=k.split("|");return '<span class="'+c+'">'+g+" "+n+"</span>"}).join("");
$("pane").innerHTML='<div class="gridw"><div class="leg">'+leg+"</div>"+Object.keys(by).sort((a,b)=>a.localeCompare(b)).map(f=>'<div class="gf"><b title="'+esc(f)+'">'+esc(f)+'</b><span class="gcs">'+by[f].map(([r,g])=>'<button class="gc '+g[0]+'" data-id="'+esc(r.exported?r.result_id:r.id)+'" title="'+esc(r.title+" | "+r.verdict)+'">'+g[1]+"</button>").join("")+"</span></div>").join("")+"</div>";
$("pane").onclick=e=>{const b=e.target.closest(".gc");if(b)showTab("fam",b.dataset.id)};}
function chartsTab(id){const L=TESTS.filter(t=>t.examples.some(x=>CHARTK.includes(x.kind)&&(x.kind!=="curve"||(x.r&&x.r.length))));
const cur=L.find(t=>t.id===id)||L[0];
$("pane").innerHTML='<main><nav id="cnav" aria-label="Charts">'+L.map(t=>'<button data-id="'+esc(t.id)+'" aria-current="'+(cur&&t.id===cur.id)+'">'+esc(t.title)+"<small>"+(t.tfs||[]).map(esc).join(" ")+"</small></button>").join("")+'</nav><article id="view"></article></main>';
$("cnav").onclick=e=>{const b=e.target.closest("button");if(b){halt();chartsTab(b.dataset.id)}};if(cur){halt();mountTest(cur,true)}}
function commentsTab(){const n=readComments().length;const rows=readComments().slice().reverse().map(c=>{const t=TESTS.find(x=>x.id===c.test_id);return '<div class="cmi"><span>'+esc(stamp(c.ts))+" &middot; "+esc(t?t.title:c.test_id)+" &middot; "+esc(c.chart_id)+"</span> "+esc(c.text)+"</div>"}).join("");
$("pane").innerHTML='<div class="gridw"><div class="leg"><span>&#9998; '+n+'</span><button type="button" data-copy="1">copy all</button></div>'+rows+"</div>";}
let TAB="fam";
const TABS=[["fam","Families","&#9776;"],["grid","Verdict grid","&#9638;"],["charts","Charts","&#9650;"],["cm","Comments","&#9998;"]];
function showTab(t,id){halt();TAB=t;document.querySelectorAll("#tabs [role=tab]").forEach(b=>b.setAttribute("aria-selected",b.dataset.tab===t));$("pane").onclick=null;
if(t==="fam"){$("pane").innerHTML='<main><nav id="nav" aria-label="Tests"></nav><article id="view" aria-live="polite"></article></main>';buildNav();render(id||location.hash.slice(1));}
else if(t==="grid")gridTab();else if(t==="charts")chartsTab(id);else commentsTab();}
$("tabs").innerHTML=TABS.map(([k,l,g])=>'<button role="tab" data-tab="'+k+'" aria-selected="false">'+g+" "+l+"</button>").join("");
$("tabs").onclick=e=>{const b=e.target.closest("[role=tab]");if(b)showTab(b.dataset.tab)};
window.onhashchange=()=>{const id=location.hash.slice(1);if(TAB==="charts")chartsTab(id);else showTab("fam",id)};showTab("fam");
</script></body></html>
'''


def load_catalogue(results_dir):
    p = os.path.join(results_dir, "_catalogue.json")
    if not os.path.isfile(p):
        return {"count": 0, "exported": 0, "rows": []}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def render(tests, catalogue=None):
    def blob(o):
        return json.dumps(o, separators=(",", ":"), ensure_ascii=False).replace("</", "<" + chr(92) + "/")
    cat = (catalogue or {}).get("rows", [])
    ids = {r.get("result_id") for r in cat}
    prov = {t["id"]: t.get("provenance") for t in tests}
    for r in cat:
        r["provenance"] = prov.get(r.get("result_id"))
    for t in tests:  # an exported result missing from the catalogue still gets a row
        if t["id"] not in ids:
            cat.append({"id": t["id"], "family": t["family"], "title": t["title"], "kind": t.get("kind", "backtest"),
                        "verdict": t["verdict"]["label"], "source": t["source_files"][0], "exported": True, "result_id": t["id"],
                        "status": "FAILED" if t["verdict"].get("tone") == "bad" else "SEE_VERDICT"})
    return TEMPLATE.replace("/*__DATA__*/null", blob(tests)).replace("/*__CAT__*/[]", blob(cat))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=RESULTS_DIR)
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    a = ap.parse_args(argv)
    tests = collect(a.results)
    if not tests:
        raise ValueError("no result files in %s" % a.results)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(tests, load_catalogue(a.results)))
    return a.out


if __name__ == "__main__":
    print(main())
