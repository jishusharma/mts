"""Per-analyst extraction status from EXTRACTION_LEDGER.csv (rebuilt by build_ledger.py) + transcript headers.

Usage (repo root): python MyTradingSys/research/analyst_video_status_1112/count_status.py
Analyst = ledger `channel`; when blank, the `# Analyst:` / `# Channel:` / uploader header of the transcript (OURS mapping).
Counts are unique video ids. 'downloaded' = id has a transcript on disk OR appears in the priority lists.
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LEDGER = REPO / "MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv"
TDIR = REPO / "raw_transcripts_canonical"
GROUPS = [("Tom", r"tom|vorwald"), ("Fabio", r"fabio|valentini"), ("Habib (Qriptal)", r"habib|qriptal"),
          ("Malkan", r"malkan"), ("Krown", r"krown")]


def header_analyst(tf):
    if not tf:
        return ""
    p = TDIR / tf
    if not p.exists():
        return ""
    head = p.read_text(encoding="utf-8", errors="replace")[:1500]
    m = re.findall(r"^#\s*(?:Analyst|Channel|Source)[^:]*:\s*(.+)$", head, re.M | re.I)
    return " ".join(m)


def group(name):
    for g, rx in GROUPS:
        if re.search(rx, name, re.I):
            return g
    return "Other / unknown"


def main():
    rows = list(csv.DictReader(open(LEDGER, newline="", encoding="utf-8")))
    by = defaultdict(list)
    for r in rows:
        by[r["video_id"]].append(r)
    stat = defaultdict(lambda: defaultdict(int))
    for vid, rs in by.items():
        name = " ".join(r["channel"] for r in rs if r["channel"]) or header_analyst(next((r["transcript_file"] for r in rs if r["transcript_file"]), ""))
        g = group(name)
        has_t = any(r["transcript_file"] for r in rs)
        ext = [r for r in rs if r["extract_file"]]
        passed = any(r["quotes_verified"] == "PASS" for r in ext)
        failed = any(r["quotes_verified"] in ("FAIL", "NA") for r in ext)
        used = any(r["used_by"] not in ("", "none") for r in ext)
        for k, v in (("ids", 1), ("transcript", has_t), ("extract_pass", passed), ("extract_fail_or_na", failed and not passed),
                     ("transcript_no_extract", has_t and not ext), ("no_transcript", not has_t),
                     ("extracted_unused", bool(ext) and not used)):
            stat[g][k] += int(bool(v))
            stat["ALL"][k] += int(bool(v))
    cols = ["ids", "transcript", "extract_pass", "extract_fail_or_na", "transcript_no_extract", "no_transcript", "extracted_unused"]
    print("| analyst | " + " | ".join(cols) + " |")
    print("|---" * (len(cols) + 1) + "|")
    for g in [x for x, _ in GROUPS] + ["Other / unknown", "ALL"]:
        print(f"| {g} | " + " | ".join(str(stat[g][c]) for c in cols) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
