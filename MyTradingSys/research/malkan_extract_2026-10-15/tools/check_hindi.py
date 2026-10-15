"""check_hindi.py: every `- Hindi original: "..."` line in a Malkan extract must occur verbatim in raw_transcripts_canonical/<id>_hi_raw.txt.

verify_extract_quotes.py cannot read Devanagari (it normalises to [a-z0-9%]), so the Hindi quotes get their own gate.
Match = whitespace-collapsed substring, caption line breaks and [..] sound tags ignored. Also requires every `> "..."` quote
block of a Hindi video to be followed by a `- Hindi original:` line (a translation without its original is not allowed).
Non-Hindi extracts (no `- Language: hi`) pass with 0 checked.

Usage (repo root):  python -I MyTradingSys/research/malkan_extract_2026-10-15/tools/check_hindi.py extract.md [...]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HI = re.compile(r'^- Hindi original:\s*"(.+)"\s*$')
QUOTE = re.compile(r'^>\s*"(.+)"\s*$')
VID = re.compile(r"^- Video ID:\s*(\S+)")
LANG = re.compile(r"^- Language:\s*(\w+)")


def norm(s):
    return " ".join(re.sub(r"\[[^\]]*\]", " ", s).split())


def check(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    vid = lang = None
    for l in lines:
        vid = vid or (VID.match(l) and VID.match(l).group(1))
        lang = lang or (LANG.match(l) and LANG.match(l).group(1))
    if lang != "hi":
        print(f"{path.name}: language {lang}, 0 Hindi quotes checked")
        return 0
    src = (ROOT / "raw_transcripts_canonical" / f"{vid}_hi_raw.txt").read_text(encoding="utf-8")
    body = norm(src.split("# ---", 1)[1] if "# ---" in src else src)
    bad = n = 0
    for i, l in enumerate(lines):
        m = HI.match(l.strip())
        if m:
            n += 1
            if norm(m.group(1)) not in body:
                print(f"HINDI_NOT_FOUND {path.name}:{i + 1} {m.group(1)[:60]}")
                bad += 1
        if QUOTE.match(l.strip()):
            tail = lines[i + 1:i + 5]
            if not any(HI.match(t.strip()) for t in tail):
                print(f"NO_HINDI_ORIGINAL {path.name}:{i + 1}")
                bad += 1
    print(f"{path.name}: {n} Hindi quotes checked, {bad} problems")
    return bad


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1251/cp1252 consoles cannot print Devanagari
    rc = 0
    for a in sys.argv[1:]:
        rc |= bool(check(Path(a)))
    sys.exit(rc)
