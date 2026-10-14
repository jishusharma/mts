"""check_numbers.py: every number written in an extract's paraphrase lines must exist in its transcript.

verify_extract_quotes.py only reads the `> "quote"` lines. The `Stated mechanics:` / `Numbers:` paraphrase lines are not
machine-checked, and EXTRACTION_ROUND2_2026-10-01.md measured 7 of 267 such fragments drifting from the source.
A number passes when its digits OR its English word appear in the transcript body (auto-captions mix both).

Usage (repo root):  python -I MyTradingSys/research/krown_ta101_2026-10-13/tools/check_numbers.py [extract.md ...]
Default = every extract in ../extracts. Exit 1 if any number is not found. Prints one line per unmatched number.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORDS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
    "8": "eight", "9": "nine", "10": "ten", "11": "eleven", "12": "twelve", "13": "thirteen", "14": "fourteen",
    "15": "fifteen", "16": "sixteen", "17": "seventeen", "18": "eighteen", "19": "nineteen", "20": "twenty",
    "21": "twenty one", "22": "twenty two", "25": "twenty five", "30": "thirty", "40": "forty", "50": "fifty",
    "55": "fifty five", "60": "sixty", "70": "seventy", "80": "eighty", "90": "ninety", "100": "hundred",
    "200": "two hundred", "500": "five hundred", "1000": "thousand",
}
NUM = re.compile(r"(?<![A-Za-z_-])(\d[\d,]*(?:\.\d+)?)%?")
PARA = re.compile(r"^- (Stated mechanics|Numbers?|Inferred):\s*(.*)$")
VID = re.compile(r"^- Video ID:\s*(\S+)")


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9.%]+", " ", s.lower()).split())


def body(vid):
    p = BASE / "transcripts" / f"{vid}_timed.txt"
    lines = [ln for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if not ln.startswith("#")]
    return norm(" ".join(re.sub(r"^\[\d+:\d{2}(?::\d{2})?\]\s*", "", ln) for ln in lines))


def present(num, text):
    n = num.replace(",", "")
    cands = {n, num}
    if n in WORDS:
        cands.add(WORDS[n])
    if "." not in n and len(n) >= 4:  # 80000 may be said "80 000" / "eighty thousand"
        cands.add(n[:-3] + " " + n[-3:])
        if n.endswith("000") and n[:-3] in WORDS:
            cands.add(WORDS[n[:-3]] + " thousand")
    # an ordinal suffix is part of the same number: "50th", "93rd", "1st", "2nd"
    return any(re.search(r"(?<![0-9a-z])" + re.escape(c) + r"(?:st|nd|rd|th)?(?![0-9a-z])", text) for c in cands)


def check(path):
    vid, text, bad, total = None, None, [], 0
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = VID.match(line)
        if m:
            vid, text = m.group(1), body(m.group(1))
            continue
        m = PARA.match(line)
        if not m or text is None:
            continue
        if "no numbers given" in m.group(2).lower() and not NUM.search(re.sub(r"no numbers? given", "", m.group(2), flags=re.I)):
            continue
        for num in NUM.findall(m.group(2)):
            total += 1
            if not present(num, text):
                bad.append((ln, num, m.group(2)[:90]))
    return vid, total, bad


def main(argv):
    files = [Path(a) for a in argv] or sorted((BASE / "extracts").glob("extract_*.md"))
    rc = 0
    for f in files:
        vid, total, bad = check(f)
        for ln, num, ctx in bad:
            print(f"NUM_NOT_FOUND {f.name}:{ln} number {num} :: {ctx}")
        print(f"{f.name}: {total} numbers checked, {len(bad)} not found")
        rc |= bool(bad)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
