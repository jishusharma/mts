"""Append all TOM-CTX-DIV variants to layer_lab/TRIALS.md and export the sim_desk json. Run once after DEV+VALIDATION."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
dev = json.load(open(HERE / "dev.json"))["rows"]
val = json.load(open(HERE / "validation.json"))["rows"]
CMD = "`python MyTradingSys/research/tom_correlation_trick_2026-10-26/run_div.py --split DEV`"


def fmt(s):
    if not s.get("n"):
        return "n 0"
    return f"n {s['n']}, mean net {s['mean'] * 1e4:.1f} bps, cluster SE {s['se'] * 1e4:.1f}, boot lb95 {s['lb95'] * 1e4:.1f}"


rows = []
for k, r in dev.items():
    h, b, L, cut = k.split("|")
    main = f"TOM-CTX-DIV {h} basket {b} {L} {cut} (hold 3d, fee+slip {'4' if h == 'H1' else '10'} bps OURS)"
    split = "DEV 70% (older); VALIDATION " + ("read once, primary only" if k in val else "not read (not primary)") + "; HOLDOUT not read"
    res = f"signal {fmt(r['basket'])}; control(a) {fmt(r['control'])}; divday {fmt(r['divday'])}"
    if k in val:
        res += f"; VALIDATION signal {fmt(val[k]['basket'])}, control(a) {fmt(val[k]['control'])}"
    rows.append(f"| 2026-10-29 | {main} | {CMD} | {split} | {res} |")
tr = ROOT / "layer_lab" / "TRIALS.md"
txt = tr.read_text()
if not txt.endswith("\n"):
    txt += "\n"
tr.write_text(txt + "\n".join(rows) + "\n", newline="\n")

p1, p2 = "H1|B1|L2|cut0.8", "H2|B1|L2|cut0.8"
out = {
    "id": "tom-corr-divergence-backtest", "kind": "backtest", "family": "Tom: correlation divergence (TOM-CTX-DIV)",
    "title": "Tom correlation-divergence filter: H1 DAX vs ES/Nikkei/BTC, H2 BTC vs ES/DXY (daily as-of, fee-net)",
    "provenance": "run", "date": "2026-10-29", "what": [], "how": "run_div.py, frozen by PRE_REG.md before any outcome; DEV 70%, VALIDATION once, HOLDOUT not read.",
    "window": "2017-07-14 to 2026-10-29",
    "verdict": {"label": "NOT-ADD TOM-CTX-DIV: primary variants have negative fee-net expectancy on DEV and VALIDATION; holdout not read.", "tone": "bad"},
    "why": ["All parameters OURS (Tom states none).", "VALIDATION n is 8 (H1) and 16 (H2), below 30: inconclusive on its own; DEV fails first."],
    "kpis": {"H1_DEV": dev[p1]["basket"], "H1_VALIDATION": val[p1]["basket"], "H2_DEV": dev[p2]["basket"], "H2_VALIDATION": val[p2]["basket"],
             "H1_control_a_DEV": dev[p1]["control"], "H2_control_a_DEV": dev[p2]["control"],
             "H1_placebo_DEV": dev[p1]["placebo"], "H2_placebo_DEV": dev[p2]["placebo"]},
    "examples": [], "evidence": ["MyTradingSys/research/tom_correlation_trick_2026-10-26/RESULT.md"], "missing": ["holdout not read (VALIDATION failed)"],
    "source_files": ["MyTradingSys/research/tom_correlation_trick_2026-10-26/run_div.py", "MyTradingSys/research/tom_correlation_trick_2026-10-26/PRE_REG.md"],
    "commit": "see git log",
}
(ROOT / "sim_desk" / "results" / "tom-corr-divergence-backtest.json").write_text(json.dumps(out, indent=1), newline="\n")
print(len(rows), "ledger rows")
