"""Leak check: no timestamp at or after 2023-07-01 in any file of the pack.
Usage: python leak_check.py <pack_dir>   (exit 1 and a list of hits on failure)

Rules per file type:
  .csv  every cell is tested: a YYYY-MM-DD[ HH:MM] date >= 2023-07-01, or an integer epoch in seconds/ms/us/ns that
        maps to a time >= 2023-07-01, is a hit.
  .md / .py / .txt  any YYYY-MM-DD or YYYY/MM/DD date >= 2023-07-01 is a hit, except a date glued to a file or
        folder name by an underscore (e.g. tom_transfer_2026-10-11/...): that is a path, not a market timestamp.
  .png  cannot be parsed; the file name must carry a date inside the window or none (checked), and the charts are
        rendered only from the CSVs that pass this check.
Any other file type is a hit (unknown content cannot be verified)."""
import csv, os, re, sys
from datetime import datetime, timezone

LIMIT = datetime(2023, 7, 1, tzinfo=timezone.utc)
LIMIT_S = int(LIMIT.timestamp())
DATE = re.compile(r"(?<![0-9])(\d{4})[-/](\d{2})[-/](\d{2})(?![0-9])")
NAME_DATE = re.compile(r"(\d{4})-(\d{2})")


def _date_ge(y, m, d):
    try:
        return datetime(int(y), int(m), int(d), tzinfo=timezone.utc) >= LIMIT
    except ValueError:
        return False


def _epoch_hit(cell):
    if not re.fullmatch(r"\d{9,19}", cell):
        return False
    n = int(cell)
    for div in (1, 1000, 1000000, 1000000000):
        sec = n / div
        if 946684800 <= sec <= 4102444800 and sec >= LIMIT_S:  # 2000..2100
            return True
    return False


def check_csv(path):
    hits = []
    with open(path, newline="") as f:
        for ln, row in enumerate(csv.reader(f), 1):
            for cell in row:
                for m in DATE.finditer(cell):
                    if _date_ge(*m.groups()):
                        hits.append((path, ln, cell))
                if _epoch_hit(cell.strip()):
                    hits.append((path, ln, cell))
    return hits


def check_text(path):
    hits = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, line in enumerate(f, 1):
            for m in DATE.finditer(line):
                if m.start() > 0 and line[m.start() - 1] == "_":
                    continue
                if _date_ge(*m.groups()):
                    hits.append((path, ln, line.strip()[:100]))
    return hits


def check_png(path):
    hits = []
    for m in NAME_DATE.finditer(os.path.basename(path)):
        y, mo = int(m.group(1)), int(m.group(2))
        if (y, mo) >= (2023, 7):
            hits.append((path, 0, "chart name outside the window"))
    return hits


def scan(pack):
    hits = []
    for root, _, files in os.walk(pack):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext == ".csv":
                hits += check_csv(p)
            elif ext in (".md", ".py", ".txt"):
                hits += check_text(p)
            elif ext == ".png":
                hits += check_png(p)
            else:
                hits.append((p, 0, f"unverifiable file type {ext}"))
    return hits


def main(pack):
    hits = scan(pack)
    for h in hits:
        print("LEAK", *h)
    print("leak_check:", "FAIL" if hits else "OK", f"({len(hits)} hits)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
