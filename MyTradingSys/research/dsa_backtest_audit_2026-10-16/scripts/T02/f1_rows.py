"""T02-F1 helper (planner 2026-10-19): list the still-unreviewed fwd-index / pivot-right-neighbour allowlist rows of one chunk.

  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py c1 --count          -> prints the number of unreviewed rows (fail-first baseline)
  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py c1 --show 0 6       -> rows 0..5 with the source line and 6 lines of context

The chunk map is T02_F1_chunks.tsv (chunk, rows, file). A row is unreviewed while its 4th column is exactly 'pre-existing, unreviewed'.
Read-only: it never writes the allowlist.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
ALLOW = REPO / "scripts" / "dev" / "lookahead_allowlist.tsv"
CHUNKS = Path(__file__).resolve().parents[2] / "T02_F1_chunks.tsv"
PATTERNS = ("fwd-index", "pivot-right-neighbour")
BASE = "pre-existing, unreviewed"


def norm(s):
    return re.sub(r"\s+", " ", s.strip())


def chunk_files(chunk):
    files = []
    for line in CHUNKS.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        c, _n, f = line.split("\t")
        if c == chunk:
            files.append(f)
    return files


def rows_of(chunk):
    files = set(chunk_files(chunk))
    out = []
    for line in ALLOW.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        a = line.split("\t")
        if len(a) >= 4 and a[0] in files and a[1] in PATTERNS and a[-1].strip() == BASE:
            out.append(a)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chunk")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--show", nargs=2, type=int, metavar=("START", "N"))
    args = ap.parse_args()
    rows = rows_of(args.chunk)
    if args.count or not args.show:
        print("chunk %s: %d unreviewed rows" % (args.chunk, len(rows)))
        return 0
    start, n = args.show
    stop = start + n
    for k, a in enumerate(rows[start:stop], start):
        f, pat, src = a[0], a[1], a[2]
        lines = (REPO / f).read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [i for i, t in enumerate(lines) if norm(t) == norm(src) or norm(src) in norm(t) or norm(t) in norm(src) and len(norm(t)) > 12]
        print("=== row %d  %s  %s  line(s) %s" % (k, f, pat, [h + 1 for h in hits[:3]] or "NOT FOUND"))
        print("src: " + src[:200])
        for h in hits[:1]:
            for i in range(max(0, h - 6), min(len(lines), h + 4)):
                print("%5d%s %s" % (i + 1, ">" if i == h else " ", lines[i][:170]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
