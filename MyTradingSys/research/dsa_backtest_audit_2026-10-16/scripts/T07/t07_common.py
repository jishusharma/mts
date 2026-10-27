"""Shared parser for T07: every published number in a result file -> (key, kind, value). Stdlib only (CI has no pandas).
kind: count (integer cell under an n-like column), num (other number), text (verdict / status word).
JSON files are flattened to their numeric / string leaves.
"""
import json
import re
from pathlib import Path

NUM = re.compile(r"^[-+]?\d+(\.\d+)?([eE][-+]?\d+)?$")
WORDS = {"PASS", "FAIL", "INCONCLUSIVE", "secondary", "ENOUGH", "MARGINAL", "THIN", "KEEP", "DROP"}


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_md(text):
    """Numbers in markdown tables, keyed by section heading | row label | column header | occurrence."""
    out, seen = [], {}
    section, header = "", None
    for line in text.splitlines():
        if line.startswith("#"):
            section = line.lstrip("#").strip()[:60]
            header = None
            continue
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = cells
            continue
        label = cells[0]
        for i, c in enumerate(cells[1:], start=1):
            h = header[i] if i < len(header) else f"col{i}"
            c = c.replace("`", "").replace("*", "")
            if NUM.match(c):
                kind = "count" if (re.fullmatch(r"[-+]?\d+", c) and re.match(r"^(n|n_|bars|events|cells|count)", h.lower())) else "num"
            elif c in WORDS:
                kind = "text"
            else:
                continue
            key = f"{section}|{label}|{h}"
            seen[key] = seen.get(key, 0) + 1
            out.append((f"{key}#{seen[key]}", kind, c))
    m = re.match(r"\s*(VERDICT:\s*)?(PASS|FAIL|INCONCLUSIVE)\b", text)
    if m:
        out.insert(0, ("TOP|verdict#1", "text", m.group(2)))
    return out


def parse_json(text):
    out = []

    def rec(p, v):
        if isinstance(v, dict):
            for k in v:
                rec(f"{p}/{k}", v[k])
        elif isinstance(v, list):
            for i, x in enumerate(v):
                rec(f"{p}[{i}]", x)
        elif isinstance(v, bool) or v is None:
            out.append((p, "text", str(v)))
        elif isinstance(v, (int, float)):
            out.append((p, "count" if isinstance(v, int) else "num", repr(v)))
        elif isinstance(v, str):
            if NUM.match(v):
                out.append((p, "num", v))
            elif v in WORDS:
                out.append((p, "text", v))

    rec("", json.loads(text))
    return out


def parse_file(path):
    t = Path(path).read_text(encoding="utf-8", errors="replace")
    return parse_json(t) if str(path).lower().endswith(".json") else parse_md(t)


# result id -> (study key in t07_rerun, published file(s) relative to MyTradingSys/research, rerun file(s) relative to sandbox study folder)
RESULTS = {
    "gross_effect_screen": ("gross_effect_screen_2026-10-15", [("RESULT.md", "RESULT.md")]),
    "opr_preopen_tops": ("opr_preopen_tops_2026-10-16", [("RESULT.md", "RESULT.md")]),
    "mal_bb_mid_engulf": ("mal_bb_mid_engulf_2026-10-16", [("RESULT.md", "RESULT.md")]),
    "opr_bb_mtf_center": ("opr_bb_mtf_center_2026-10-16", [("RESULT.md", "RESULT.md")]),
    "opr_weekly_low_round_sweep": ("opr_weekly_low_round_sweep_2026-10-16", [("RESULT.md", "RESULT.md")]),
    "wlow_bounce_bbrsi60": ("wlow_bounce_bbrsi60_2026-10-16", [("RESULT.md", "RESULT.md")]),
    "krown_malkan_g3": ("krown_malkan_g3_2026-10-16", [("EVENT_COUNTS.md", "EVENT_COUNTS.md")]),
    "qriptal_scorecard": ("qriptal_2026-10-10", [("SCORECARD.md", "SCORECARD.md")]),
    "orderflow_views": ("orderflow_views_2026-10-14", [("results_dev_rerun_2026-10-17.json", "results_dev_rerun_2026-10-17.json")]),
    "mfe_exit": ("mfe_exit_2026-10-13", [("rerun_dev_2026-10-17/results.json", "results.json")]),
}
