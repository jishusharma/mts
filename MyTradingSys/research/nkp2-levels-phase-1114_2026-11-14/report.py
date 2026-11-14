"""Builds RESULT.md from results.json, cells_frozen.json and the summary CSVs. Run after `study.py val`: python report.py"""
import csv, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "results.json").read_text())
fr = res["frozen"]
CTXDIR = Path(r"F:\MTS\data_cache") / "binance" / "nkp2-levels-phase-1114"


def rd(name):
    p = HERE / name
    return list(csv.DictReader(open(p))) if p.exists() and p.stat().st_size else []


def f(x, nd=3, pct=False):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "-"
    if v != v:
        return "-"
    return f"{v * 100:.1f}%" if pct else f"{v:.{nd}f}"


def table(rows, cols, head=None):
    head = head or cols
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


vc = res["val_cells"]
kept = len(vc)
passed = res["passed"]
best = None
for x in vc:
    v = x["val"]
    if v.get("n", 0) and (best is None or v["ci_lo"] > best["val"]["ci_lo"]):
        best = x
if kept == 0:
    verdict = "**VERDICT: FAIL, no DEV cell survived selection for any rule (n >= 150, >= 40 days, lower 90% bound > 0, one cell per layer), so there is nothing to run on VAL. 0 kept cells, 0 passes.**"
elif passed:
    verdict = f"**VERDICT: PASS for {passed} of {kept} DEV-chosen cells on VAL (2024+), fee-net at 12 bp; see the table, one regime only (2024-26).**"
else:
    verdict = f"**VERDICT: FAIL, 0 of {kept} DEV-chosen cells pass VAL (2024+) fee-net at 12 bp; best cell by day-CI low: {best['cell']['rule']} / {best['cell']['phase']} / {best['cell']['layer']} {best['cell']['bucket']}, n {best['val']['n']}, net {f(best['val']['net'])} R, day CI low {f(best['val']['ci_lo'])}.**" if best else f"**VERDICT: FAIL, {kept} kept cells but none traded on VAL.**"

L = [verdict, ""]
mx = res["mix"]
def mixline(k):
    return ", ".join(f"{p} {v[0]}d ({v[1] * 100:.1f}%)" for p, v in mx[k].items() if p != "_days")
L.append(f"Regime mix (days per phase, label from BTC through the prior close). DEV 2019-2023 ({mx['DEV']['_days']} days): {mixline('DEV')}. VAL 2024-2026-11-13 ({mx['VAL']['_days']} days): {mixline('VAL')}.")
sp = res["signals_per_phase"]
L.append("Signals (trades) per phase, registered stop basis, 12 bp sequence:")
rows = []
for r in ("NK2-core", "NK2-deep", "NK3-A", "NK3-B"):
    for sp_k in ("DEV", "VAL"):
        d = sp[f"{r}_{sp_k}"]
        rows.append(dict(rule=r, split=sp_k, **{k: v for k, v in d.items()}))
L.append(table(rows, ["rule", "split", "CAPITULATION", "MARKDOWN", "RELIEF", "ACCUM-RANGE", "MARKUP", "DISTRIBUTION"]))
L.append("")
L.append("## Context")
L.append("Phase table: `F:\\MTS\\data_cache\\mts_brains\\phase_daily.csv` (shared; a sibling worker's builder wrote the file, my own build of the same spec agreed on 2874 of 2874 days from 2019-01-01, so the shared file is used as is), 30 random days re-computed from truncated data in `test_phase_csv_matches_recompute_30_days`. Six phases and thresholds are spec s1 (OURS, not tuned); cycle state SOURCED from the cycle-conditioned PRE_REG. CAPITULATION is below 5% of DEV days (2.9%), so it is reported and never supplies a cell. Context layers C1-C8: spec s2, one layer per cell. Sanity windows (recorded, not retuned): see PRE_REG.md.")
L.append("Rules: NK2-core (P, S1/R1 triggers), NK2-deep (S2, S3 long; R2, R3 short; NEW), NK3-A (breakout retest), NK3-B (fakeout fade). 1h bars, 20 Binance spot coins, taker 12 bp (6 bp per leg on entry and exit notional), spot-equivalent, no funding charge. NK2 uses the close-basis stop (NK 'stop on closing basis', NEW for this study family), NK3 the intraday stop; Step A shows the other basis in `alt net`.")
L.append("")
L.append("## Step A: per-phase table, phase-appropriate vs opposite direction")
L.append("Every phase is its own row; nothing is pooled across phases. `role` marks the phase-appropriate direction (ACCUM-RANGE is both). Net R is mean fee-net R per trade at 12 bp; gross R and cost R before/after the fee; `alt net` is the same set on the other stop basis.")
for split, fn in (("VAL (2024+, descriptive, after the freeze)", "stepA_val.csv"), ("DEV (<=2023, used for selection)", "stepA_dev.csv")):
    L.append(f"\n### {split}")
    rows = rd(fn)
    out = []
    for r in rows:
        if r["n"] in ("0", "") and r["alt_n"] in ("0", ""):
            continue
        out.append(dict(rule=r["rule"], phase=r["phase"], dir=r["dir"], role=r["role"], n=r["n"], days=r["days"], gross=f(r["gross"]), cost=f(r["cost"]), net=f(r["net"]), alt_net=f(r["alt_net"])))
    L.append(table(out, ["rule", "phase", "dir", "role", "n", "days", "gross", "cost", "net", "alt_net"], ["rule", "phase", "dir", "role", "n", "days", "gross R", "cost R", "net R", "alt net R"]))
L.append("\n### Does the phase-appropriate direction beat the opposite one? (day-clustered difference)")
for split, fn in (("VAL", "stepA_appropriate_vs_opposite_val.csv"), ("DEV", "stepA_appropriate_vs_opposite_dev.csv")):
    rows = rd(fn)
    L.append(f"\n{split}:")
    L.append(table([dict(rule=r["rule"], phase=r["phase"], app_n=r["app_n"], opp_n=r["opp_n"], app=f(r["app_net"]), opp=f(r["opp_net"]), diff=f(r["diff"]), se=f(r["se"]), z=f(r["z"], 2)) for r in rows],
                   ["rule", "phase", "app_n", "opp_n", "app", "opp", "diff", "se", "z"], ["rule", "phase", "appropriate n", "opposite n", "appropriate net R", "opposite net R", "diff", "se", "z"]))
L.append("\n### Pivot level table (NK2; S1/S2/S3 long, R1/R2/R3 short, P both; close-basis stop; trades by trigger level)")
for split, fn in (("VAL", "levels_val.csv"), ("DEV", "levels_dev.csv")):
    rows = [r for r in rd(fn) if r["subset"].startswith("appropriate")]
    L.append(f"\n{split}, phase-appropriate-direction trades only:")
    L.append(table([dict(rule=r["rule"], level=r["level"], n=r["n"], days=r["days"], gross=f(r["gross"]), cost=f(r["cost"]), net=f(r["net"])) for r in rows], ["rule", "level", "n", "days", "gross", "cost", "net"], ["rule", "level", "n", "days", "gross R", "cost R", "net R"]))
L.append("\n## Step B: DEV selection")
el = fr["eligible"]
L.append(table([dict(rule=r, **el[r]) for r in el], ["rule", "cells_scored", "cells_n_days_ok", "positive_dev_mean", "score_gt0"], ["rule", "cells scored", "n>=150 and >=40 days", "of those: DEV mean > 0", "lower 90% bound > 0"]))
if fr["no_data"]:
    L.append("\nNO-DATA layers: " + "; ".join(f"{x['rule']} {x['layer']}" for x in fr["no_data"]))
L.append(f"\nKept cells (frozen in commit `{fr['code_commit'][:10]}`): {kept}.")
L.append("\n## Step C: the DEV-chosen cells on VAL (run once)")
rows = []
for x in vc:
    c, v, m, p = x["cell"], x["val"], x["maker6bp"], x["placebo"]
    rows.append(dict(cell=f"{c['rule']} / {c['phase']} / {c['layer']} {c['bucket']} / {c['direction']}", dev=f"{c['dev_n']} / {f(c['dev_net'])}", n=v.get("n"), days=v.get("days"), win=f(v.get("win"), 1), be=f(v.get("be_win"), 1),
                     gross=f(v.get("gross")), cost=f(v.get("cost")), net=f(v.get("net")), ci=f"{f(v.get('ci_lo'))} .. {f(v.get('ci_hi'))}", ex5=f(v.get("ex5")), plc=f"{f(p.get('placebo_mean'))} / p {f(p.get('placebo_p'))}",
                     q=f(x.get("bh_q")), mk=f"{f(m.get('net'))} (n {m.get('n')}, fill {f(x['maker_fill_ratio'], 2)})", verdict=x.get("verdict")))
if rows:
    L.append(table(rows, ["cell", "dev", "n", "days", "win", "be", "gross", "cost", "net", "ci", "ex5", "plc", "q", "mk", "verdict"],
                   ["cell (rule / phase / layer bucket / dir)", "DEV n / net R", "VAL n", "days", "win %", "break-even win %", "gross R", "fee R", "net R 12bp", "day CI 95%", "ex-best-5 net R", "placebo mean / p", "BH q", "maker 6bp net R", "verdict"]))
    L.append(f"\nDEV cells that passed VAL: {passed} of {kept}. DEV net vs VAL net (shrinkage): " + "; ".join(f"{x['cell']['rule']} {x['cell']['layer']} {f(x['cell']['dev_net'])} -> {f(x['val'].get('net'))}" for x in vc))
    L.append("\nControl rows on VAL (12 bp net R, n):")
    cr = []
    for x in vc:
        c = x["cell"]
        g = lambda k: (f"{f(x[k]['net'])} (n {x[k]['n']})" if x.get(k) and x[k].get("n") else "-")
        cr.append(dict(cell=f"{c['rule']} / {c['phase']} / {c['layer']} {c['bucket']}", cellv=g("val"), opp=g("control_opposite_dir"), other=g("control_other_phases_same_bucket"), unc=g("control_unconditional")))
    L.append(table(cr, ["cell", "cellv", "opp", "other", "unc"], ["cell", "the cell", "opposite direction", "same bucket, other 5 phases", "unconditional rule (same direction)"]))
else:
    L.append("No kept cells, nothing to run on VAL. Unconditional per-phase numbers are in Step A.")
L.append("\n## Useful trades now (descriptive only, no advice)")
td = res["today"]
L.append(f"Phase label for BTC (applied to ETH and all coins) from the latest closed data: {td['applied_label']['phase']} (label day {td['applied_label']['latest_label_day']}). " + (f"Provisional label for the next day using the partial {td['provisional']['partial_day']} bar ({td['provisional']['bars']} of 96 bars): {td['provisional']['provisional_label_for_next_day']}." if td.get("provisional") else ""))
L.append(table([dict(day=r["day_closed"], label=r["label_for_next_day"], close=f(r["close"], 0), sma50=f(r["sma50"], 0), sma200=f(r["sma200"], 0), w200=f(r["w200"], 0), state=r["state"]) for r in td["last_10_closed_days"]], ["day", "label", "close", "sma50", "sma200", "w200", "state"],
              ["closed day", "label for the next day", "BTC close", "SMA50", "SMA200", "W200", "cycle state"]))
for coin, cc in td["context_now"].items():
    L.append(f"\n{coin} latest closed 1h bar {cc['last_1h_open']}: phase {cc['phase']}; " + "; ".join(f"{k} {v}" for k, v in cc["ctx"].items()))
act = td["kept_cells_active_now"]
if act:
    L.append("\nKept cells active at this reading: " + "; ".join(f"{a['coin']}: {a['rule']} / {a['phase']} / {a['layer']} {a['bucket']}" for a in act))
else:
    L.append("\nKept cells active at this reading: none" + (" (no kept cells)." if not vc else "."))
L.append("\n## Data coverage")
meta = sorted(CTXDIR.glob("*.meta.json"))
rows = []
byc = {}
for p in meta:
    j = json.loads(p.read_text())
    k, sym = p.name.split(".")[0].rsplit("_", 1)
    byc.setdefault(sym, {})[k] = j["first_utc"][:10] + (" .. " + j["last_utc"][:10] if k in ("funding", "klines_1h") else " .. " + j["last_utc"][:10])
for s_, d_ in byc.items():
    rows.append(dict(coin=s_, klines=d_.get("klines_1h", "NO-DATA"), funding=d_.get("funding", "NO-DATA"), oi=d_.get("oi", "NO-DATA")))
L.append("First and last available date per coin and series (data.binance.vision). Funding monthly files end at the last full month, so C5 has no bucket for later signals; OI daily files start 2020-09 at the earliest and per listing. Signals before a layer's first date have no bucket for that layer.")
L.append(table(rows, ["coin", "klines", "funding", "oi"], ["coin", "spot 1h klines (C6)", "funding (C5)", "open interest (C4)"]))
tr = HERE / "test_runs.txt"
if tr.exists():
    L.append("\n## Tests\n```\n" + tr.read_text() + "\n```")
extra = HERE / "RESULT_NOTES.md"
if extra.exists():
    L.append("\n" + extra.read_text())
(HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf8")
print("wrote RESULT.md", len("\n".join(L)))
