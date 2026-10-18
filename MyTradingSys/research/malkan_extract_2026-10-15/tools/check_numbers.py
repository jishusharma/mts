"""check_numbers.py (Malkan): every number in an extract's `Stated mechanics:` / `Numbers:` / `Inferred:` lines must exist in its transcript.

Same logic as research/krown_ta101_2026-10-13/tools/check_numbers.py (imported, not copied); only the transcript source differs:
Malkan transcripts live in raw_transcripts_canonical/<id>_raw.txt (no timestamps; header lines start with `#`).

Usage (repo root):  python -I MyTradingSys/research/malkan_extract_2026-10-15/tools/check_numbers.py extract.md [...]
Exit 1 if any number is not found.
"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
KROWN = ROOT / "MyTradingSys" / "research" / "krown_ta101_2026-10-13" / "tools" / "check_numbers.py"

spec = importlib.util.spec_from_file_location("krown_check_numbers", KROWN)
kc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kc)


def body(vid):
    p = ROOT / "raw_transcripts_canonical" / f"{vid}_raw.txt"
    lines = [ln for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if not ln.startswith("#")]
    return kc.norm(" ".join(re.sub(r"^\[\d+:\d{2}(?::\d{2})?\]\s*", "", ln) for ln in lines))


kc.body = body

# Krown's NUM lookbehind drops "-" followed numbers (to skip ids like M-xyz-22) but then matches the tail digit of a range
# ("80-90" -> stray "0"). Here ids are blanked first and ranges are read as two numbers (fix found on A-CQiV_UFB4).
ID = re.compile(r"\b[MS]-[A-Za-z0-9_-]{11}-\d{2}\b")
kc.NUM = re.compile(r"(?<![A-Za-z_\d,.])(\d[\d,]*(?:\.\d+)?)%?")
_findall = kc.NUM.findall


class _Num:
    @staticmethod
    def findall(s):
        return _findall(ID.sub(" ", s))

    @staticmethod
    def search(s):
        return bool(_findall(ID.sub(" ", s)))


kc.NUM = _Num

if __name__ == "__main__":
    files = [Path(a) for a in sys.argv[1:]] or sorted((HERE.parent / "extracts").glob("extract_*.md"))
    rc = 0
    for f in files:
        vid, total, bad = kc.check(f)
        for ln, num, ctx in bad:
            print(f"NUM_NOT_FOUND {f.name}:{ln} number {num} :: {ctx}")
        print(f"{f.name}: {total} numbers checked, {len(bad)} not found")
        rc |= bool(bad)
    sys.exit(rc)
