"""T07 step 5: key published numbers (brief 1b) -> present near the study's name in LAYERS.md, layer_map.json, research_map.html, STATUS.md?
Writes out/doc_drift.csv. A number absent next to a mention of the study is a drift candidate (read by hand in the report).
Run from the worktree root: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/t07_docdrift.py"""
import csv
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
DOCS = {"LAYERS.md": "MyTradingSys/system/LAYERS.md", "layer_map.json": "MyTradingSys/system/layer_map.json",
        "research_map.html": "MyTradingSys/system/artifacts/research_map.html", "STATUS.md": "MyTradingSys/research/STATUS.md"}
KEYS = [
    ("mal_bb_mid_engulf", r"mal_bb|MAL-BB|mid.{0,12}engulf", [("A1 n", "1179"), ("A2 n", "807"), ("verdict", "FAIL")]),
    ("opr_weekly_low_round_sweep", r"weekly_low_round|weekly-low.{0,20}round|round sweep", [("RL n", "685"), ("AS n", "525"), ("verdict", "FAIL")]),
    ("opr_bb_mtf_center", r"bb_mtf|BB MTF|1h BB mid", [("AU n", "194"), ("AD n", "282")]),
    ("opr_preopen_tops", r"preopen|pre-open", [("H1 n", "105"), ("H2 n", "104")]),
    ("wlow_bounce_bbrsi60", r"wlow_bounce|weekly-low bounce", [("n", "8")]),
    ("gross_effect_screen", r"gross_effect|gross-effect", [("n_T", "40"), ("t", "-1.51")]),
    ("candle_close", r"candle.close", [("arms", "126")]),
    ("levels_sizing", r"levels_sizing|levels sizing", [("campaigns", "117")]),
    ("published_strats", r"published_strats|published strat", [("variants", "62")]),
    ("tom_fabio_q33", r"Q33|guidance", [("cells", "336")]),
]
rows = []
for dn, rel in DOCS.items():
    p = REPO / rel
    if not p.is_file():
        rows.append(["*", dn, "*", "*", 0, "DOC_FILE_MISSING"])
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    for study, rx, nums in KEYS:
        mentions = [m.start() for m in re.finditer(rx, t, re.I)]
        for label, num in nums:
            numrx = re.compile(r"(?<![\d.])" + re.escape(num) + r"(?![\d])")
            near = any(numrx.search(t, max(0, q - 400), q + 600) for q in mentions)
            st = "PRESENT_NEAR_MENTION" if near else ("STUDY_NOT_MENTIONED" if not mentions else "NUMBER_NOT_NEAR_MENTION")
            rows.append([study, dn, label, num, len(mentions), st])
with open(Path(__file__).parent / "out" / "doc_drift.csv", "w", newline="\n", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["study", "doc", "number", "published", "n_mentions", "status"])
    w.writerows(rows)
print(Counter((r[1], r[5]) for r in rows))
for r in rows:
    if r[5] == "NUMBER_NOT_NEAR_MENTION":
        print(r)
